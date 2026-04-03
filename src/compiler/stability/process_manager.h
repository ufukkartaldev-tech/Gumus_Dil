#pragma once

#include <string>
#include <vector>
#include <memory>
#include <chrono>
#include <functional>
#include <unordered_map>
#include <atomic>
#include <thread>
#include <mutex>

namespace GumusStability {

enum class ProcessState {
    CREATED,
    STARTING,
    RUNNING,
    STOPPING,
    STOPPED,
    FAILED,
    TIMEOUT
};

struct ProcessInfo {
    int pid = -1;
    std::string command;
    std::vector<std::string> arguments;
    ProcessState state = ProcessState::CREATED;
    std::chrono::steady_clock::time_point start_time;
    std::chrono::steady_clock::time_point end_time;
    int exit_code = -1;
    std::string stdout_data;
    std::string stderr_data;
    size_t memory_usage_mb = 0;
    double cpu_usage_percent = 0.0;
};

class ProcessManager {
public:
    using ProcessCallback = std::function<void(const ProcessInfo&)>;
    
    ProcessManager();
    ~ProcessManager();
    
    // Process lifecycle management
    int startProcess(const std::string& command, const std::vector<std::string>& args = {});
    bool stopProcess(int pid, bool force = false);
    bool killProcess(int pid);
    
    // Process monitoring
    ProcessInfo getProcessInfo(int pid) const;
    std::vector<ProcessInfo> getAllProcesses() const;
    bool isProcessRunning(int pid) const;
    
    // Resource monitoring
    void setResourceLimits(size_t max_memory_mb, double max_cpu_percent);
    void enableResourceMonitoring(bool enable);
    
    // Callbacks
    void setProcessStartCallback(ProcessCallback callback);
    void setProcessEndCallback(ProcessCallback callback);
    void setProcessErrorCallback(ProcessCallback callback);
    
    // Timeout management
    void setDefaultTimeout(std::chrono::milliseconds timeout);
    void setProcessTimeout(int pid, std::chrono::milliseconds timeout);
    
    // Health checking
    bool isHealthy() const;
    size_t getActiveProcessCount() const;
    
private:
    struct ManagedProcess {
        ProcessInfo info;
        std::chrono::milliseconds timeout{30000}; // 30 seconds default
        std::thread monitor_thread;
        std::atomic<bool> should_stop{false};
    };
    
    mutable std::mutex processes_mutex;
    std::unordered_map<int, std::unique_ptr<ManagedProcess>> processes;
    
    // Resource limits
    size_t max_memory_mb = 1024; // 1GB default
    double max_cpu_percent = 90.0;
    bool resource_monitoring_enabled = true;
    
    // Callbacks
    ProcessCallback on_process_start;
    ProcessCallback on_process_end;
    ProcessCallback on_process_error;
    
    // Default timeout
    std::chrono::milliseconds default_timeout{30000};
    
    // Monitoring thread
    std::thread resource_monitor_thread;
    std::atomic<bool> monitoring_active{true};
    
    // Internal methods
    void monitorProcess(int pid);
    void monitorResources();
    void updateProcessStats(ManagedProcess& process);
    bool checkResourceLimits(const ManagedProcess& process);
    void handleProcessTimeout(int pid);
    void handleResourceViolation(int pid, const std::string& reason);
    void cleanupProcess(int pid);
    
    // Platform-specific implementations
    int createProcess(const std::string& command, const std::vector<std::string>& args);
    bool terminateProcess(int pid, bool force);
    ProcessInfo queryProcessInfo(int pid);
};

// Singleton process manager
class GlobalProcessManager {
public:
    static ProcessManager& getInstance();
    
private:
    static std::unique_ptr<ProcessManager> instance;
    static std::once_flag init_flag;
};

// Process wrapper for safe execution
class SafeProcess {
public:
    SafeProcess(const std::string& command, const std::vector<std::string>& args = {});
    ~SafeProcess();
    
    // Execution control
    bool start();
    bool stop(bool force = false);
    bool wait(std::chrono::milliseconds timeout = std::chrono::milliseconds::zero());
    
    // State queries
    bool isRunning() const;
    ProcessState getState() const;
    int getExitCode() const;
    
    // Output access
    std::string getStdout() const;
    std::string getStderr() const;
    
    // Resource monitoring
    size_t getMemoryUsage() const;
    double getCpuUsage() const;
    
    // Configuration
    void setTimeout(std::chrono::milliseconds timeout);
    void setResourceLimits(size_t max_memory_mb, double max_cpu_percent);
    
private:
    std::string command;
    std::vector<std::string> arguments;
    int pid = -1;
    ProcessManager* manager;
    std::chrono::milliseconds timeout{30000};
    size_t max_memory_mb = 512;
    double max_cpu_percent = 80.0;
};

// Process pool for managing multiple processes
class ProcessPool {
public:
    ProcessPool(size_t max_processes = 10);
    ~ProcessPool();
    
    // Pool management
    int submitProcess(const std::string& command, const std::vector<std::string>& args = {});
    bool cancelProcess(int pid);
    void waitForAll();
    void terminateAll();
    
    // Pool status
    size_t getActiveCount() const;
    size_t getQueuedCount() const;
    bool isFull() const;
    
    // Configuration
    void setMaxProcesses(size_t max_processes);
    void setDefaultTimeout(std::chrono::milliseconds timeout);
    
private:
    struct QueuedProcess {
        std::string command;
        std::vector<std::string> arguments;
        std::chrono::steady_clock::time_point submit_time;
    };
    
    mutable std::mutex pool_mutex;
    std::vector<std::unique_ptr<SafeProcess>> active_processes;
    std::vector<QueuedProcess> process_queue;
    
    size_t max_processes;
    std::chrono::milliseconds default_timeout{30000};
    
    std::thread scheduler_thread;
    std::atomic<bool> scheduler_active{true};
    
    void schedulerLoop();
    void startQueuedProcesses();
    void cleanupFinishedProcesses();
};

} // namespace GumusStability