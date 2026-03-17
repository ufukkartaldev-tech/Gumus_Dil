#ifndef SECURE_SUBPROCESS_H
#define SECURE_SUBPROCESS_H

#include "input_validator.h"
#include <string>
#include <vector>
#include <memory>
#include <chrono>

// 🛡️ Secure Subprocess Execution Framework

class SecureSubprocess {
public:
    enum class ExecutionResult {
        SUCCESS,
        TIMEOUT,
        ACCESS_DENIED,
        INVALID_COMMAND,
        EXECUTION_ERROR,
        SECURITY_VIOLATION
    };
    
    struct ProcessResult {
        ExecutionResult result;
        std::string stdout_output;
        std::string stderr_output;
        int exit_code = -1;
        std::chrono::milliseconds execution_time{0};
        std::string error_message;
    };
    
    struct ExecutionConfig {
        std::chrono::milliseconds timeout{30000}; // 30 seconds default
        std::string working_directory;
        std::unordered_map<std::string, std::string> environment;
        bool capture_output = true;
        bool merge_stderr = false;
        size_t max_output_size = 1024 * 1024; // 1MB default
        bool allow_network = false;
        bool allow_file_access = false;
        std::vector<std::string> allowed_paths;
        std::vector<std::string> blocked_paths;
    };
    
private:
    SecurityContext securityContext;
    InputValidator validator;
    ExecutionConfig config;
    
    // Command whitelist
    std::vector<std::string> allowedCommands;
    std::vector<std::string> blockedCommands;
    bool useCommandWhitelist = true;
    
    // Dangerous command patterns
    std::vector<std::string> dangerousPatterns = {
        "rm -rf", "del /s", "format", "fdisk", "mkfs",
        "dd if=", "wget", "curl", "nc ", "netcat",
        "telnet", "ssh", "sudo", "su ", "chmod 777",
        "chown", "passwd", "useradd", "userdel",
        "iptables", "firewall", "regedit", "reg add"
    };
    
public:
    SecureSubprocess(SecurityContext::TrustLevel trustLevel = SecurityContext::TrustLevel::LOW);
    
    // Main execution methods
    ProcessResult execute(const std::string& command);
    ProcessResult execute(const std::string& command, const std::vector<std::string>& args);
    ProcessResult executeShell(const std::string& shellCommand);
    
    // Safe execution wrappers
    ProcessResult executeSafe(const std::string& command, const std::vector<std::string>& args);
    ProcessResult executeWithSandbox(const std::string& command, const std::vector<std::string>& args);
    
    // Configuration
    void setConfig(const ExecutionConfig& cfg) { config = cfg; }
    void setTimeout(std::chrono::milliseconds timeout) { config.timeout = timeout; }
    void setWorkingDirectory(const std::string& dir) { config.working_directory = dir; }
    void setMaxOutputSize(size_t size) { config.max_output_size = size; }
    
    // Security configuration
    void addAllowedCommand(const std::string& command);
    void addBlockedCommand(const std::string& command);
    void enableCommandWhitelist(bool enable) { useCommandWhitelist = enable; }
    void addAllowedPath(const std::string& path);
    void addBlockedPath(const std::string& path);
    
    // Validation
    bool isCommandAllowed(const std::string& command);
    bool isPathAllowed(const std::string& path);
    bool containsDangerousPatterns(const std::string& command);
    
private:
    // Internal validation
    bool validateCommand(const std::string& command);
    bool validateArguments(const std::vector<std::string>& args);
    bool validateEnvironment(const std::unordered_map<std::string, std::string>& env);
    
    // Execution helpers
    ProcessResult executeInternal(const std::string& command, const std::vector<std::string>& args);
    std::string sanitizeCommand(const std::string& command);
    std::vector<std::string> sanitizeArguments(const std::vector<std::string>& args);
    
    // Security enforcement
    void applySandbox();
    void limitResources();
    void setupSecureEnvironment();
    
    // Error handling
    ProcessResult createErrorResult(ExecutionResult result, const std::string& error);
    void logSecurityViolation(const std::string& command, const std::string& reason);
};

// 🔒 Command Builder for Safe Execution
class SafeCommandBuilder {
private:
    std::string baseCommand;
    std::vector<std::string> arguments;
    std::unordered_map<std::string, std::string> environment;
    std::string workingDir;
    InputValidator validator;
    
public:
    SafeCommandBuilder(const std::string& command);
    
    // Argument building
    SafeCommandBuilder& addArgument(const std::string& arg);
    SafeCommandBuilder& addFlag(const std::string& flag);
    SafeCommandBuilder& addOption(const std::string& option, const std::string& value);
    SafeCommandBuilder& addFile(const std::string& filepath);
    
    // Environment
    SafeCommandBuilder& setEnvironment(const std::string& key, const std::string& value);
    SafeCommandBuilder& setWorkingDirectory(const std::string& dir);
    
    // Validation and building
    bool validate();
    std::string build();
    std::vector<std::string> buildArgs();
    
    // Security helpers
    SafeCommandBuilder& escapeArguments();
    SafeCommandBuilder& validatePaths();
    
private:
    std::string escapeArgument(const std::string& arg);
    bool isValidPath(const std::string& path);
};

// 🛡️ Subprocess Sandbox (Platform-specific)
class SubprocessSandbox {
public:
    struct SandboxConfig {
        bool restrict_network = true;
        bool restrict_filesystem = true;
        std::vector<std::string> allowed_directories;
        std::chrono::milliseconds cpu_limit{10000}; // 10 seconds
        size_t memory_limit = 128 * 1024 * 1024; // 128MB
        bool allow_fork = false;
        bool allow_exec = false;
    };
    
private:
    SandboxConfig config;
    bool active = false;
    
public:
    SubprocessSandbox(const SandboxConfig& cfg = SandboxConfig{});
    
    // Sandbox control
    bool enable();
    void disable();
    bool isActive() const { return active; }
    
    // Configuration
    void setConfig(const SandboxConfig& cfg) { config = cfg; }
    void addAllowedDirectory(const std::string& dir);
    void setCPULimit(std::chrono::milliseconds limit) { config.cpu_limit = limit; }
    void setMemoryLimit(size_t limit) { config.memory_limit = limit; }
    
private:
    // Platform-specific implementations
    bool enableLinuxSandbox();
    bool enableWindowsSandbox();
    bool enableMacOSSandbox();
    
    void setupSeccomp(); // Linux
    void setupAppContainer(); // Windows
    void setupSandboxProfile(); // macOS
};

// 🚨 Process Monitor for Security
class ProcessMonitor {
public:
    struct ProcessInfo {
        int pid;
        std::string command;
        std::chrono::steady_clock::time_point start_time;
        std::chrono::milliseconds cpu_time{0};
        size_t memory_usage = 0;
        int file_descriptors = 0;
        bool is_suspicious = false;
    };
    
private:
    std::vector<ProcessInfo> monitoredProcesses;
    bool monitoring = false;
    std::chrono::milliseconds check_interval{1000}; // 1 second
    
public:
    ProcessMonitor();
    
    // Monitoring control
    void startMonitoring();
    void stopMonitoring();
    bool isMonitoring() const { return monitoring; }
    
    // Process management
    void addProcess(int pid, const std::string& command);
    void removeProcess(int pid);
    ProcessInfo getProcessInfo(int pid);
    std::vector<ProcessInfo> getAllProcesses();
    
    // Security checks
    bool isProcessSuspicious(int pid);
    void killSuspiciousProcesses();
    void setResourceLimits(int pid, size_t memory_limit, std::chrono::milliseconds cpu_limit);
    
    // Configuration
    void setCheckInterval(std::chrono::milliseconds interval) { check_interval = interval; }
    
private:
    void monitorLoop();
    void updateProcessInfo(ProcessInfo& info);
    bool checkResourceUsage(const ProcessInfo& info);
    bool checkSuspiciousActivity(const ProcessInfo& info);
};

#endif // SECURE_SUBPROCESS_H