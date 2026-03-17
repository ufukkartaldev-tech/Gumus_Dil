#include "secure_subprocess.h"
#include <iostream>
#include <algorithm>
#include <thread>

SecureSubprocess::SecureSubprocess(SecurityContext::TrustLevel trustLevel) 
    : securityContext(trustLevel) {
    
    // Initialize default safe commands
    allowedCommands = {
        "echo", "cat", "ls", "dir", "pwd", "cd", "mkdir", "rmdir",
        "cp", "copy", "mv", "move", "find", "grep", "head", "tail",
        "wc", "sort", "uniq", "cut", "awk", "sed", "python", "python3",
        "node", "npm", "yarn", "git", "make", "cmake", "gcc", "g++",
        "clang", "clang++", "javac", "java", "rustc", "cargo"
    };
}

SecureSubprocess::ProcessResult SecureSubprocess::execute(const std::string& command) {
    std::vector<std::string> args;
    return execute(command, args);
}

SecureSubprocess::ProcessResult SecureSubprocess::execute(const std::string& command, 
                                                         const std::vector<std::string>& args) {
    auto start = std::chrono::steady_clock::now();
    
    // Validate command
    if (!validateCommand(command)) {
        return createErrorResult(ExecutionResult::INVALID_COMMAND, 
                               "Command validation failed: " + command);
    }
    
    // Validate arguments
    if (!validateArguments(args)) {
        return createErrorResult(ExecutionResult::INVALID_COMMAND, 
                               "Argument validation failed");
    }
    
    // Check security permissions
    if (!securityContext.canExecuteCommand(command)) {
        return createErrorResult(ExecutionResult::ACCESS_DENIED, 
                               "Command execution not allowed: " + command);
    }
    
    // Execute the command
    ProcessResult result = executeInternal(command, args);
    
    auto end = std::chrono::steady_clock::now();
    result.execution_time = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    return result;
}

SecureSubprocess::ProcessResult SecureSubprocess::executeShell(const std::string& shellCommand) {
    // Parse shell command into command and arguments
    std::string command;
    std::vector<std::string> args;
    
    std::istringstream iss(shellCommand);
    std::string token;
    bool first = true;
    
    while (iss >> token) {
        if (first) {
            command = token;
            first = false;
        } else {
            args.push_back(token);
        }
    }
    
    return execute(command, args);
}

SecureSubprocess::ProcessResult SecureSubprocess::executeSafe(const std::string& command, 
                                                             const std::vector<std::string>& args) {
    // Additional safety checks
    if (containsDangerousPatterns(command)) {
        return createErrorResult(ExecutionResult::SECURITY_VIOLATION, 
                               "Dangerous pattern detected in command");
    }
    
    for (const auto& arg : args) {
        if (containsDangerousPatterns(arg)) {
            return createErrorResult(ExecutionResult::SECURITY_VIOLATION, 
                                   "Dangerous pattern detected in arguments");
        }
    }
    
    return execute(command, args);
}

SecureSubprocess::ProcessResult SecureSubprocess::executeWithSandbox(const std::string& command, 
                                                                    const std::vector<std::string>& args) {
    // For now, just execute normally - sandbox implementation would be platform-specific
    std::cout << "[SANDBOX] Executing in sandbox: " << command << std::endl;
    return executeSafe(command, args);
}

void SecureSubprocess::addAllowedCommand(const std::string& command) {
    allowedCommands.push_back(command);
}

void SecureSubprocess::addBlockedCommand(const std::string& command) {
    blockedCommands.push_back(command);
}

void SecureSubprocess::addAllowedPath(const std::string& path) {
    config.allowed_paths.push_back(path);
}

void SecureSubprocess::addBlockedPath(const std::string& path) {
    config.blocked_paths.push_back(path);
}

bool SecureSubprocess::isCommandAllowed(const std::string& command) {
    // Check blocked commands first
    for (const auto& blocked : blockedCommands) {
        if (command == blocked) {
            return false;
        }
    }
    
    // If whitelist is enabled, command must be in allowed list
    if (useCommandWhitelist) {
        return std::find(allowedCommands.begin(), allowedCommands.end(), command) != allowedCommands.end();
    }
    
    return true;
}

bool SecureSubprocess::isPathAllowed(const std::string& path) {
    // Check blocked paths
    for (const auto& blocked : config.blocked_paths) {
        if (path.find(blocked) == 0) {
            return false;
        }
    }
    
    // Check allowed paths (if specified)
    if (!config.allowed_paths.empty()) {
        for (const auto& allowed : config.allowed_paths) {
            if (path.find(allowed) == 0) {
                return true;
            }
        }
        return false;
    }
    
    return true;
}

bool SecureSubprocess::containsDangerousPatterns(const std::string& command) {
    std::string lowerCommand = command;
    std::transform(lowerCommand.begin(), lowerCommand.end(), lowerCommand.begin(), ::tolower);
    
    for (const auto& pattern : dangerousPatterns) {
        if (lowerCommand.find(pattern) != std::string::npos) {
            return true;
        }
    }
    
    return false;
}

bool SecureSubprocess::validateCommand(const std::string& command) {
    if (command.empty()) {
        return false;
    }
    
    // Validate command string
    auto validation = validator.validateString(command);
    if (validation != InputValidator::ValidationResult::VALID) {
        return false;
    }
    
    // Check if command is allowed
    if (!isCommandAllowed(command)) {
        return false;
    }
    
    // Check for dangerous patterns
    if (containsDangerousPatterns(command)) {
        return false;
    }
    
    return true;
}

bool SecureSubprocess::validateArguments(const std::vector<std::string>& args) {
    for (const auto& arg : args) {
        auto validation = validator.validateString(arg);
        if (validation != InputValidator::ValidationResult::VALID) {
            return false;
        }
        
        if (containsDangerousPatterns(arg)) {
            return false;
        }
    }
    
    return true;
}

bool SecureSubprocess::validateEnvironment(const std::unordered_map<std::string, std::string>& env) {
    for (const auto& pair : env) {
        auto keyValidation = validator.validateString(pair.first);
        auto valueValidation = validator.validateString(pair.second);
        
        if (keyValidation != InputValidator::ValidationResult::VALID ||
            valueValidation != InputValidator::ValidationResult::VALID) {
            return false;
        }
    }
    
    return true;
}

SecureSubprocess::ProcessResult SecureSubprocess::executeInternal(const std::string& command, 
                                                                 const std::vector<std::string>& args) {
    // This is a simplified implementation
    // In a real implementation, this would use platform-specific APIs
    
    ProcessResult result;
    result.result = ExecutionResult::SUCCESS;
    result.stdout_output = "Command executed successfully (simulated)";
    result.stderr_output = "";
    result.exit_code = 0;
    
    std::cout << "[SECURE EXEC] " << command;
    for (const auto& arg : args) {
        std::cout << " " << arg;
    }
    std::cout << std::endl;
    
    return result;
}

std::string SecureSubprocess::sanitizeCommand(const std::string& command) {
    return validator.sanitizeString(command);
}

std::vector<std::string> SecureSubprocess::sanitizeArguments(const std::vector<std::string>& args) {
    std::vector<std::string> sanitized;
    for (const auto& arg : args) {
        sanitized.push_back(validator.sanitizeString(arg));
    }
    return sanitized;
}

void SecureSubprocess::applySandbox() {
    // Platform-specific sandbox implementation would go here
    std::cout << "[SANDBOX] Sandbox applied (simulated)" << std::endl;
}

void SecureSubprocess::limitResources() {
    // Resource limiting implementation would go here
    std::cout << "[RESOURCE] Resource limits applied (simulated)" << std::endl;
}

void SecureSubprocess::setupSecureEnvironment() {
    // Secure environment setup would go here
    std::cout << "[ENV] Secure environment setup (simulated)" << std::endl;
}

SecureSubprocess::ProcessResult SecureSubprocess::createErrorResult(ExecutionResult result, 
                                                                   const std::string& error) {
    ProcessResult processResult;
    processResult.result = result;
    processResult.error_message = error;
    processResult.exit_code = -1;
    return processResult;
}

void SecureSubprocess::logSecurityViolation(const std::string& command, const std::string& reason) {
    std::cerr << "[SECURITY VIOLATION] Command blocked: " << reason << std::endl;
    std::cerr << "[COMMAND] " << command << std::endl;
}

// SafeCommandBuilder implementation
SafeCommandBuilder::SafeCommandBuilder(const std::string& command) : baseCommand(command) {}

SafeCommandBuilder& SafeCommandBuilder::addArgument(const std::string& arg) {
    arguments.push_back(arg);
    return *this;
}

SafeCommandBuilder& SafeCommandBuilder::addFlag(const std::string& flag) {
    arguments.push_back(flag);
    return *this;
}

SafeCommandBuilder& SafeCommandBuilder::addOption(const std::string& option, const std::string& value) {
    arguments.push_back(option);
    arguments.push_back(value);
    return *this;
}

SafeCommandBuilder& SafeCommandBuilder::addFile(const std::string& filepath) {
    if (isValidPath(filepath)) {
        arguments.push_back(filepath);
    }
    return *this;
}

SafeCommandBuilder& SafeCommandBuilder::setEnvironment(const std::string& key, const std::string& value) {
    environment[key] = value;
    return *this;
}

SafeCommandBuilder& SafeCommandBuilder::setWorkingDirectory(const std::string& dir) {
    workingDir = dir;
    return *this;
}

bool SafeCommandBuilder::validate() {
    // Validate base command
    auto validation = validator.validateString(baseCommand);
    if (validation != InputValidator::ValidationResult::VALID) {
        return false;
    }
    
    // Validate arguments
    for (const auto& arg : arguments) {
        auto argValidation = validator.validateString(arg);
        if (argValidation != InputValidator::ValidationResult::VALID) {
            return false;
        }
    }
    
    // Validate working directory
    if (!workingDir.empty() && !isValidPath(workingDir)) {
        return false;
    }
    
    return true;
}

std::string SafeCommandBuilder::build() {
    std::string command = baseCommand;
    for (const auto& arg : arguments) {
        command += " " + escapeArgument(arg);
    }
    return command;
}

std::vector<std::string> SafeCommandBuilder::buildArgs() {
    return arguments;
}

SafeCommandBuilder& SafeCommandBuilder::escapeArguments() {
    for (auto& arg : arguments) {
        arg = escapeArgument(arg);
    }
    return *this;
}

SafeCommandBuilder& SafeCommandBuilder::validatePaths() {
    // Remove invalid paths
    arguments.erase(
        std::remove_if(arguments.begin(), arguments.end(),
                      [this](const std::string& arg) { return !isValidPath(arg); }),
        arguments.end());
    return *this;
}

std::string SafeCommandBuilder::escapeArgument(const std::string& arg) {
    std::string escaped;
    escaped.reserve(arg.length() * 2);
    
    for (char c : arg) {
        if (c == ' ' || c == '"' || c == '\'' || c == '\\') {
            escaped += '\\';
        }
        escaped += c;
    }
    
    return escaped;
}

bool SafeCommandBuilder::isValidPath(const std::string& path) {
    auto validation = validator.validateFilePath(path);
    return validation == InputValidator::ValidationResult::VALID;
}

// SubprocessSandbox implementation
SubprocessSandbox::SubprocessSandbox(const SandboxConfig& cfg) : config(cfg) {}

bool SubprocessSandbox::enable() {
    if (active) {
        return true;
    }
    
    // Platform-specific sandbox enabling
#ifdef __linux__
    return enableLinuxSandbox();
#elif _WIN32
    return enableWindowsSandbox();
#elif __APPLE__
    return enableMacOSSandbox();
#else
    std::cout << "[SANDBOX] Sandbox not supported on this platform" << std::endl;
    return false;
#endif
}

void SubprocessSandbox::disable() {
    active = false;
    std::cout << "[SANDBOX] Sandbox disabled" << std::endl;
}

void SubprocessSandbox::addAllowedDirectory(const std::string& dir) {
    config.allowed_directories.push_back(dir);
}

bool SubprocessSandbox::enableLinuxSandbox() {
    // Linux seccomp implementation would go here
    std::cout << "[SANDBOX] Linux sandbox enabled (simulated)" << std::endl;
    active = true;
    return true;
}

bool SubprocessSandbox::enableWindowsSandbox() {
    // Windows App Container implementation would go here
    std::cout << "[SANDBOX] Windows sandbox enabled (simulated)" << std::endl;
    active = true;
    return true;
}

bool SubprocessSandbox::enableMacOSSandbox() {
    // macOS sandbox profile implementation would go here
    std::cout << "[SANDBOX] macOS sandbox enabled (simulated)" << std::endl;
    active = true;
    return true;
}

void SubprocessSandbox::setupSeccomp() {
    // Linux seccomp setup
    std::cout << "[SANDBOX] Seccomp setup (simulated)" << std::endl;
}

void SubprocessSandbox::setupAppContainer() {
    // Windows App Container setup
    std::cout << "[SANDBOX] App Container setup (simulated)" << std::endl;
}

void SubprocessSandbox::setupSandboxProfile() {
    // macOS sandbox profile setup
    std::cout << "[SANDBOX] Sandbox profile setup (simulated)" << std::endl;
}

// ProcessMonitor implementation
ProcessMonitor::ProcessMonitor() {}

void ProcessMonitor::startMonitoring() {
    monitoring = true;
    std::cout << "[MONITOR] Process monitoring started" << std::endl;
    
    // Start monitoring thread
    std::thread([this]() {
        monitorLoop();
    }).detach();
}

void ProcessMonitor::stopMonitoring() {
    monitoring = false;
    std::cout << "[MONITOR] Process monitoring stopped" << std::endl;
}

void ProcessMonitor::addProcess(int pid, const std::string& command) {
    ProcessInfo info;
    info.pid = pid;
    info.command = command;
    info.start_time = std::chrono::steady_clock::now();
    
    monitoredProcesses.push_back(info);
    std::cout << "[MONITOR] Added process: " << pid << " (" << command << ")" << std::endl;
}

void ProcessMonitor::removeProcess(int pid) {
    monitoredProcesses.erase(
        std::remove_if(monitoredProcesses.begin(), monitoredProcesses.end(),
                      [pid](const ProcessInfo& info) { return info.pid == pid; }),
        monitoredProcesses.end());
    
    std::cout << "[MONITOR] Removed process: " << pid << std::endl;
}

ProcessMonitor::ProcessInfo ProcessMonitor::getProcessInfo(int pid) {
    for (const auto& info : monitoredProcesses) {
        if (info.pid == pid) {
            return info;
        }
    }
    
    return ProcessInfo{}; // Return empty info if not found
}

std::vector<ProcessMonitor::ProcessInfo> ProcessMonitor::getAllProcesses() {
    return monitoredProcesses;
}

bool ProcessMonitor::isProcessSuspicious(int pid) {
    for (const auto& info : monitoredProcesses) {
        if (info.pid == pid) {
            return info.is_suspicious;
        }
    }
    return false;
}

void ProcessMonitor::killSuspiciousProcesses() {
    for (const auto& info : monitoredProcesses) {
        if (info.is_suspicious) {
            std::cout << "[MONITOR] Killing suspicious process: " << info.pid << std::endl;
            // Platform-specific process killing would go here
        }
    }
}

void ProcessMonitor::setResourceLimits(int pid, size_t memory_limit, std::chrono::milliseconds cpu_limit) {
    std::cout << "[MONITOR] Setting resource limits for process " << pid 
              << ": memory=" << memory_limit << ", cpu=" << cpu_limit.count() << "ms" << std::endl;
    // Platform-specific resource limiting would go here
}

void ProcessMonitor::monitorLoop() {
    while (monitoring) {
        for (auto& info : monitoredProcesses) {
            updateProcessInfo(info);
            
            if (checkResourceUsage(info) || checkSuspiciousActivity(info)) {
                info.is_suspicious = true;
            }
        }
        
        std::this_thread::sleep_for(check_interval);
    }
}

void ProcessMonitor::updateProcessInfo(ProcessInfo& info) {
    // Update process information (platform-specific)
    // This would query the OS for current process stats
}

bool ProcessMonitor::checkResourceUsage(const ProcessInfo& info) {
    // Check if process is using too many resources
    return false; // Simplified for now
}

bool ProcessMonitor::checkSuspiciousActivity(const ProcessInfo& info) {
    // Check for suspicious process behavior
    return false; // Simplified for now
}