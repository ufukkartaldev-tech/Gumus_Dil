#include "process_manager.h"
#include "error_recovery.h"
#include <iostream>
#include <algorithm>
#include <thread>
#include <chrono>

#ifdef _WIN32
#include <windows.h>
#include <psapi.h>
#include <tlhelp32.h>
#else
#include <sys/wait.h>
#include <sys/resource.h>
#include <signal.h>
#include <unistd.h>
#endif

namespace GumusStability {

// ProcessManager implementation
ProcessManager::ProcessManager() {
    // Start resource monitoring thread
    resource_monitor_thread = std::thread(&ProcessManager::monitorResources, this);
}

ProcessManager::~ProcessManager() {
    monitoring_active = false;
    
    // Stop all processes
    std::lock_guard<std::mutex> lock(processes_mutex);
    for (auto& [pid, process] : processes) {
        process->should_stop = true;
        stopProcess(pid, true);
    }
    
    // Wait for monitoring thread to finish
    if (resource_monitor_thread.joinable()) {
        resource_monitor_thread.join();
    }
}

int ProcessManager::startProcess(const std::string& command, const std::vector<std::string>& args) {
    try {
        int pid = createProcess(command, args);
        if (pid <= 0) {
            REPORT_ERROR("ProcessManager", "startProcess", 
                        "Failed to create process: " + command, ErrorSeverity::ERROR, -1);
            return -1;
        }
        
        // Create managed process
        auto managed = std::make_unique<ManagedProcess>();
        managed->info.pid = pid;
        managed->info.command = command;
        managed->info.arguments = args;
        managed->info.state = ProcessState::STARTING;
        managed->info.start_time = std::chrono::steady_clock::now();
        managed->timeout = default_timeout;
        
        // Start monitoring thread
        managed->monitor_thread = std::thread(&ProcessManager::monitorProcess, this, pid);
        
        {
            std::lock_guard<std::mutex> lock(processes_mutex);
            processes[pid] = std::move(managed);
        }
        
        // Notify callback
        if (on_process_start) {
            on_process_start(getProcessInfo(pid));
        }
        
        std::cout << "[PROCESS] Started process " << pid << ": " << command << std::endl;
        return pid;
        
    } catch (const std::exception& e) {
        REPORT_CRITICAL_ERROR("ProcessManager", "startProcess", 
                             "Exception starting process: " + std::string(e.what()), -1);
        return -1;
    }
}

bool ProcessManager::stopProcess(int pid, bool force) {
    std::lock_guard<std::mutex> lock(processes_mutex);
    auto it = processes.find(pid);
    if (it == processes.end()) {
        return false;
    }
    
    auto& process = it->second;
    process->should_stop = true;
    process->info.state = ProcessState::STOPPING;
    
    bool success = terminateProcess(pid, force);
    
    if (success) {
        process->info.state = ProcessState::STOPPED;
        process->info.end_time = std::chrono::steady_clock::now();
        
        if (on_process_end) {
            on_process_end(process->info);
        }
        
        std::cout << "[PROCESS] Stopped process " << pid << std::endl;
    } else {
        process->info.state = ProcessState::FAILED;
        
        if (on_process_error) {
            on_process_error(process->info);
        }
        
        REPORT_ERROR("ProcessManager", "stopProcess", 
                    "Failed to stop process " + std::to_string(pid), 
                    ErrorSeverity::WARNING, -1);
    }
    
    return success;
}

bool ProcessManager::killProcess(int pid) {
    return stopProcess(pid, true);
}

ProcessInfo ProcessManager::getProcessInfo(int pid) const {
    std::lock_guard<std::mutex> lock(processes_mutex);
    auto it = processes.find(pid);
    if (it != processes.end()) {
        return it->second->info;
    }
    
    // Return empty info for unknown processes
    ProcessInfo info;
    info.pid = pid;
    info.state = ProcessState::STOPPED;
    return info;
}

std::vector<ProcessInfo> ProcessManager::getAllProcesses() const {
    std::lock_guard<std::mutex> lock(processes_mutex);
    std::vector<ProcessInfo> result;
    
    for (const auto& [pid, process] : processes) {
        result.push_back(process->info);
    }
    
    return result;
}

bool ProcessManager::isProcessRunning(int pid) const {
    std::lock_guard<std::mutex> lock(processes_mutex);
    auto it = processes.find(pid);
    if (it != processes.end()) {
        return it->second->info.state == ProcessState::RUNNING;
    }
    return false;
}

void ProcessManager::setResourceLimits(size_t max_memory_mb, double max_cpu_percent) {
    this->max_memory_mb = max_memory_mb;
    this->max_cpu_percent = max_cpu_percent;
}

void ProcessManager::enableResourceMonitoring(bool enable) {
    resource_monitoring_enabled = enable;
}

void ProcessManager::setProcessStartCallback(ProcessCallback callback) {
    on_process_start = callback;
}

void ProcessManager::setProcessEndCallback(ProcessCallback callback) {
    on_process_end = callback;
}

void ProcessManager::setProcessErrorCallback(ProcessCallback callback) {
    on_process_error = callback;
}

void ProcessManager::setDefaultTimeout(std::chrono::milliseconds timeout) {
    default_timeout = timeout;
}

void ProcessManager::setProcessTimeout(int pid, std::chrono::milliseconds timeout) {
    std::lock_guard<std::mutex> lock(processes_mutex);
    auto it = processes.find(pid);
    if (it != processes.end()) {
        it->second->timeout = timeout;
    }
}

bool ProcessManager::isHealthy() const {
    std::lock_guard<std::mutex> lock(processes_mutex);
    
    // Check if any processes are in failed state
    for (const auto& [pid, process] : processes) {
        if (process->info.state == ProcessState::FAILED) {
            return false;
        }
    }
    
    return true;
}

size_t ProcessManager::getActiveProcessCount() const {
    std::lock_guard<std::mutex> lock(processes_mutex);
    
    size_t count = 0;
    for (const auto& [pid, process] : processes) {
        if (process->info.state == ProcessState::RUNNING || 
            process->info.state == ProcessState::STARTING) {
            count++;
        }
    }
    
    return count;
}

void ProcessManager::monitorProcess(int pid) {
    while (monitoring_active) {
        {
            std::lock_guard<std::mutex> lock(processes_mutex);
            auto it = processes.find(pid);
            if (it == processes.end() || it->second->should_stop) {
                break;
            }
            
            auto& process = *it->second;
            
            // Update process statistics
            updateProcessStats(process);
            
            // Check timeout
            auto now = std::chrono::steady_clock::now();
            if (now - process.info.start_time > process.timeout) {
                handleProcessTimeout(pid);
                break;
            }
            
            // Check resource limits
            if (resource_monitoring_enabled && !checkResourceLimits(process)) {
                handleResourceViolation(pid, "Resource limit exceeded");
                break;
            }
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(1000)); // Check every second
    }
    
    cleanupProcess(pid);
}

void ProcessManager::monitorResources() {
    while (monitoring_active) {
        std::this_thread::sleep_for(std::chrono::seconds(5)); // Check every 5 seconds
        
        if (!resource_monitoring_enabled) {
            continue;
        }
        
        std::lock_guard<std::mutex> lock(processes_mutex);
        for (auto& [pid, process] : processes) {
            if (process->info.state == ProcessState::RUNNING) {
                updateProcessStats(*process);
            }
        }
    }
}

void ProcessManager::updateProcessStats(ManagedProcess& process) {
    ProcessInfo updated = queryProcessInfo(process.info.pid);
    process.info.memory_usage_mb = updated.memory_usage_mb;
    process.info.cpu_usage_percent = updated.cpu_usage_percent;
    process.info.state = updated.state;
    process.info.exit_code = updated.exit_code;
}

bool ProcessManager::checkResourceLimits(const ManagedProcess& process) {
    if (process.info.memory_usage_mb > max_memory_mb) {
        return false;
    }
    
    if (process.info.cpu_usage_percent > max_cpu_percent) {
        return false;
    }
    
    return true;
}

void ProcessManager::handleProcessTimeout(int pid) {
    std::cout << "[PROCESS] Process " << pid << " timed out, terminating..." << std::endl;
    
    {
        std::lock_guard<std::mutex> lock(processes_mutex);
        auto it = processes.find(pid);
        if (it != processes.end()) {
            it->second->info.state = ProcessState::TIMEOUT;
        }
    }
    
    stopProcess(pid, true);
    
    REPORT_WARNING("ProcessManager", "handleProcessTimeout", 
                  "Process " + std::to_string(pid) + " exceeded timeout");
}

void ProcessManager::handleResourceViolation(int pid, const std::string& reason) {
    std::cout << "[PROCESS] Process " << pid << " violated resource limits: " << reason << std::endl;
    
    stopProcess(pid, true);
    
    REPORT_WARNING("ProcessManager", "handleResourceViolation", 
                  "Process " + std::to_string(pid) + " - " + reason);
}

void ProcessManager::cleanupProcess(int pid) {
    std::lock_guard<std::mutex> lock(processes_mutex);
    auto it = processes.find(pid);
    if (it != processes.end()) {
        if (it->second->monitor_thread.joinable()) {
            it->second->monitor_thread.join();
        }
        processes.erase(it);
    }
}

// Platform-specific implementations
#ifdef _WIN32

int ProcessManager::createProcess(const std::string& command, const std::vector<std::string>& args) {
    std::string cmdline = command;
    for (const auto& arg : args) {
        cmdline += " \"" + arg + "\"";
    }
    
    STARTUPINFOA si = {};
    si.cb = sizeof(si);
    PROCESS_INFORMATION pi = {};
    
    if (!CreateProcessA(nullptr, const_cast<char*>(cmdline.c_str()), 
                       nullptr, nullptr, FALSE, 0, nullptr, nullptr, &si, &pi)) {
        return -1;
    }
    
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    
    return static_cast<int>(pi.dwProcessId);
}

bool ProcessManager::terminateProcess(int pid, bool force) {
    HANDLE hProcess = OpenProcess(PROCESS_TERMINATE, FALSE, static_cast<DWORD>(pid));
    if (!hProcess) {
        return false;
    }
    
    BOOL result = TerminateProcess(hProcess, 1);
    CloseHandle(hProcess);
    
    return result != FALSE;
}

ProcessInfo ProcessManager::queryProcessInfo(int pid) {
    ProcessInfo info;
    info.pid = pid;
    info.state = ProcessState::STOPPED;
    
    HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, static_cast<DWORD>(pid));
    if (!hProcess) {
        return info;
    }
    
    // Check if process is still running
    DWORD exitCode;
    if (GetExitCodeProcess(hProcess, &exitCode)) {
        if (exitCode == STILL_ACTIVE) {
            info.state = ProcessState::RUNNING;
        } else {
            info.state = ProcessState::STOPPED;
            info.exit_code = static_cast<int>(exitCode);
        }
    }
    
    // Get memory usage
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(hProcess, &pmc, sizeof(pmc))) {
        info.memory_usage_mb = pmc.WorkingSetSize / (1024 * 1024);
    }
    
    CloseHandle(hProcess);
    return info;
}

#else // Unix/Linux

int ProcessManager::createProcess(const std::string& command, const std::vector<std::string>& args) {
    pid_t pid = fork();
    if (pid == 0) {
        // Child process
        std::vector<char*> argv;
        argv.push_back(const_cast<char*>(command.c_str()));
        for (const auto& arg : args) {
            argv.push_back(const_cast<char*>(arg.c_str()));
        }
        argv.push_back(nullptr);
        
        execvp(command.c_str(), argv.data());
        _exit(1); // If execvp fails
    } else if (pid > 0) {
        // Parent process
        return static_cast<int>(pid);
    } else {
        // Fork failed
        return -1;
    }
}

bool ProcessManager::terminateProcess(int pid, bool force) {
    int signal = force ? SIGKILL : SIGTERM;
    return kill(static_cast<pid_t>(pid), signal) == 0;
}

ProcessInfo ProcessManager::queryProcessInfo(int pid) {
    ProcessInfo info;
    info.pid = pid;
    info.state = ProcessState::STOPPED;
    
    // Check if process exists
    if (kill(static_cast<pid_t>(pid), 0) == 0) {
        info.state = ProcessState::RUNNING;
    } else {
        // Process doesn't exist or we can't signal it
        return info;
    }
    
    // Try to get memory usage from /proc/pid/status
    std::string status_file = "/proc/" + std::to_string(pid) + "/status";
    std::ifstream file(status_file);
    if (file.is_open()) {
        std::string line;
        while (std::getline(file, line)) {
            if (line.find("VmRSS:") == 0) {
                size_t kb = 0;
                if (sscanf(line.c_str(), "VmRSS: %zu kB", &kb) == 1) {
                    info.memory_usage_mb = kb / 1024;
                }
                break;
            }
        }
    }
    
    return info;
}

#endif

// GlobalProcessManager implementation
std::unique_ptr<ProcessManager> GlobalProcessManager::instance;
std::once_flag GlobalProcessManager::init_flag;

ProcessManager& GlobalProcessManager::getInstance() {
    std::call_once(init_flag, []() {
        instance = std::make_unique<ProcessManager>();
    });
    return *instance;
}

// SafeProcess implementation
SafeProcess::SafeProcess(const std::string& command, const std::vector<std::string>& args)
    : command(command), arguments(args), manager(&GlobalProcessManager::getInstance()) {}

SafeProcess::~SafeProcess() {
    if (isRunning()) {
        stop(true);
    }
}

bool SafeProcess::start() {
    if (pid != -1) {
        return false; // Already started
    }
    
    pid = manager->startProcess(command, arguments);
    if (pid > 0) {
        manager->setProcessTimeout(pid, timeout);
        return true;
    }
    
    return false;
}

bool SafeProcess::stop(bool force) {
    if (pid == -1) {
        return false;
    }
    
    bool result = manager->stopProcess(pid, force);
    if (result) {
        pid = -1;
    }
    
    return result;
}

bool SafeProcess::wait(std::chrono::milliseconds timeout) {
    if (pid == -1) {
        return true; // Not running
    }
    
    auto start = std::chrono::steady_clock::now();
    while (isRunning()) {
        if (timeout != std::chrono::milliseconds::zero()) {
            auto elapsed = std::chrono::steady_clock::now() - start;
            if (elapsed >= timeout) {
                return false; // Timeout
            }
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    return true;
}

bool SafeProcess::isRunning() const {
    return pid != -1 && manager->isProcessRunning(pid);
}

ProcessState SafeProcess::getState() const {
    if (pid == -1) {
        return ProcessState::STOPPED;
    }
    
    return manager->getProcessInfo(pid).state;
}

int SafeProcess::getExitCode() const {
    if (pid == -1) {
        return -1;
    }
    
    return manager->getProcessInfo(pid).exit_code;
}

std::string SafeProcess::getStdout() const {
    if (pid == -1) {
        return "";
    }
    
    return manager->getProcessInfo(pid).stdout_data;
}

std::string SafeProcess::getStderr() const {
    if (pid == -1) {
        return "";
    }
    
    return manager->getProcessInfo(pid).stderr_data;
}

size_t SafeProcess::getMemoryUsage() const {
    if (pid == -1) {
        return 0;
    }
    
    return manager->getProcessInfo(pid).memory_usage_mb;
}

double SafeProcess::getCpuUsage() const {
    if (pid == -1) {
        return 0.0;
    }
    
    return manager->getProcessInfo(pid).cpu_usage_percent;
}

void SafeProcess::setTimeout(std::chrono::milliseconds timeout) {
    this->timeout = timeout;
    if (pid != -1) {
        manager->setProcessTimeout(pid, timeout);
    }
}

void SafeProcess::setResourceLimits(size_t max_memory_mb, double max_cpu_percent) {
    this->max_memory_mb = max_memory_mb;
    this->max_cpu_percent = max_cpu_percent;
}

// ProcessPool implementation
ProcessPool::ProcessPool(size_t max_processes) 
    : max_processes(max_processes) {
    scheduler_thread = std::thread(&ProcessPool::schedulerLoop, this);
}

ProcessPool::~ProcessPool() {
    scheduler_active = false;
    terminateAll();
    
    if (scheduler_thread.joinable()) {
        scheduler_thread.join();
    }
}

int ProcessPool::submitProcess(const std::string& command, const std::vector<std::string>& args) {
    std::lock_guard<std::mutex> lock(pool_mutex);
    
    if (active_processes.size() < max_processes) {
        // Start immediately
        auto process = std::make_unique<SafeProcess>(command, args);
        process->setTimeout(default_timeout);
        
        if (process->start()) {
            int pid = process->getProcessInfo().pid;
            active_processes.push_back(std::move(process));
            return pid;
        }
        
        return -1;
    } else {
        // Queue for later
        QueuedProcess queued;
        queued.command = command;
        queued.arguments = args;
        queued.submit_time = std::chrono::steady_clock::now();
        
        process_queue.push_back(queued);
        return 0; // Queued
    }
}

bool ProcessPool::cancelProcess(int pid) {
    std::lock_guard<std::mutex> lock(pool_mutex);
    
    auto it = std::find_if(active_processes.begin(), active_processes.end(),
        [pid](const std::unique_ptr<SafeProcess>& process) {
            return process->getProcessInfo().pid == pid;
        });
    
    if (it != active_processes.end()) {
        (*it)->stop(true);
        active_processes.erase(it);
        return true;
    }
    
    return false;
}

void ProcessPool::waitForAll() {
    while (getActiveCount() > 0 || getQueuedCount() > 0) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

void ProcessPool::terminateAll() {
    std::lock_guard<std::mutex> lock(pool_mutex);
    
    for (auto& process : active_processes) {
        process->stop(true);
    }
    
    active_processes.clear();
    process_queue.clear();
}

size_t ProcessPool::getActiveCount() const {
    std::lock_guard<std::mutex> lock(pool_mutex);
    return active_processes.size();
}

size_t ProcessPool::getQueuedCount() const {
    std::lock_guard<std::mutex> lock(pool_mutex);
    return process_queue.size();
}

bool ProcessPool::isFull() const {
    std::lock_guard<std::mutex> lock(pool_mutex);
    return active_processes.size() >= max_processes;
}

void ProcessPool::setMaxProcesses(size_t max_processes) {
    this->max_processes = max_processes;
}

void ProcessPool::setDefaultTimeout(std::chrono::milliseconds timeout) {
    default_timeout = timeout;
}

void ProcessPool::schedulerLoop() {
    while (scheduler_active) {
        {
            std::lock_guard<std::mutex> lock(pool_mutex);
            cleanupFinishedProcesses();
            startQueuedProcesses();
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }
}

void ProcessPool::startQueuedProcesses() {
    while (!process_queue.empty() && active_processes.size() < max_processes) {
        auto queued = process_queue.front();
        process_queue.erase(process_queue.begin());
        
        auto process = std::make_unique<SafeProcess>(queued.command, queued.arguments);
        process->setTimeout(default_timeout);
        
        if (process->start()) {
            active_processes.push_back(std::move(process));
        }
    }
}

void ProcessPool::cleanupFinishedProcesses() {
    active_processes.erase(
        std::remove_if(active_processes.begin(), active_processes.end(),
            [](const std::unique_ptr<SafeProcess>& process) {
                return !process->isRunning();
            }),
        active_processes.end());
}

} // namespace GumusStability