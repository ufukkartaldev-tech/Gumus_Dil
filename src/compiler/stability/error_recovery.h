#pragma once

#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <chrono>
#include <unordered_map>

namespace GumusStability {

enum class ErrorSeverity {
    INFO = 0,
    WARNING = 1,
    ERROR = 2,
    CRITICAL = 3,
    FATAL = 4
};

enum class RecoveryStrategy {
    IGNORE,
    RETRY,
    FALLBACK,
    GRACEFUL_SHUTDOWN,
    FORCE_RESTART
};

struct ErrorContext {
    std::string component;
    std::string operation;
    std::string details;
    ErrorSeverity severity;
    std::chrono::steady_clock::time_point timestamp;
    int error_code;
    std::string stack_trace;
    std::unordered_map<std::string, std::string> metadata;
};

class ErrorRecoveryManager {
public:
    using RecoveryHandler = std::function<bool(const ErrorContext&)>;
    
    ErrorRecoveryManager();
    ~ErrorRecoveryManager() = default;
    
    // Error reporting and handling
    void reportError(const ErrorContext& context);
    void registerRecoveryHandler(const std::string& component, RecoveryStrategy strategy, RecoveryHandler handler);
    
    // Recovery operations
    bool attemptRecovery(const ErrorContext& context);
    void setMaxRetryAttempts(int max_attempts);
    void setRetryDelay(std::chrono::milliseconds delay);
    
    // Statistics and monitoring
    size_t getErrorCount(const std::string& component = "") const;
    std::vector<ErrorContext> getRecentErrors(size_t count = 10) const;
    double getErrorRate(const std::string& component = "") const;
    
    // Health checking
    bool isComponentHealthy(const std::string& component) const;
    void markComponentUnhealthy(const std::string& component);
    void markComponentHealthy(const std::string& component);
    
private:
    struct ComponentHealth {
        bool is_healthy = true;
        size_t error_count = 0;
        std::chrono::steady_clock::time_point last_error;
        std::chrono::steady_clock::time_point last_success;
    };
    
    std::vector<ErrorContext> error_history;
    std::unordered_map<std::string, std::vector<std::pair<RecoveryStrategy, RecoveryHandler>>> recovery_handlers;
    std::unordered_map<std::string, ComponentHealth> component_health;
    
    int max_retry_attempts = 3;
    std::chrono::milliseconds retry_delay{1000};
    size_t max_error_history = 1000;
    
    bool executeRecoveryStrategy(const ErrorContext& context, RecoveryStrategy strategy, RecoveryHandler handler);
    void cleanupOldErrors();
};

// Circuit breaker pattern for preventing cascade failures
class CircuitBreaker {
public:
    enum class State {
        CLOSED,    // Normal operation
        OPEN,      // Failing, reject calls
        HALF_OPEN  // Testing if service recovered
    };
    
    CircuitBreaker(size_t failure_threshold = 5, 
                   std::chrono::milliseconds timeout = std::chrono::milliseconds(60000));
    
    bool canExecute() const;
    void recordSuccess();
    void recordFailure();
    State getState() const;
    
private:
    State current_state = State::CLOSED;
    size_t failure_count = 0;
    size_t failure_threshold;
    std::chrono::milliseconds timeout;
    std::chrono::steady_clock::time_point last_failure_time;
    
    void transitionToOpen();
    void transitionToClosed();
    void transitionToHalfOpen();
};

// Graceful degradation manager
class DegradationManager {
public:
    enum class ServiceLevel {
        FULL_SERVICE = 100,
        REDUCED_SERVICE = 75,
        MINIMAL_SERVICE = 50,
        EMERGENCY_SERVICE = 25,
        NO_SERVICE = 0
    };
    
    DegradationManager();
    
    void setServiceLevel(ServiceLevel level);
    ServiceLevel getCurrentServiceLevel() const;
    
    bool isFeatureEnabled(const std::string& feature) const;
    void disableFeature(const std::string& feature);
    void enableFeature(const std::string& feature);
    
    // Resource management
    void setResourceLimit(const std::string& resource, double limit);
    double getResourceLimit(const std::string& resource) const;
    
private:
    ServiceLevel current_level = ServiceLevel::FULL_SERVICE;
    std::unordered_map<std::string, bool> feature_flags;
    std::unordered_map<std::string, double> resource_limits;
    
    void applyServiceLevelConstraints();
};

// Global error recovery instance
extern std::unique_ptr<ErrorRecoveryManager> g_error_recovery;
extern std::unique_ptr<DegradationManager> g_degradation_manager;

// Convenience macros for error reporting
#define REPORT_ERROR(component, operation, details, severity, code) \
    do { \
        if (GumusStability::g_error_recovery) { \
            GumusStability::ErrorContext ctx; \
            ctx.component = component; \
            ctx.operation = operation; \
            ctx.details = details; \
            ctx.severity = severity; \
            ctx.error_code = code; \
            ctx.timestamp = std::chrono::steady_clock::now(); \
            GumusStability::g_error_recovery->reportError(ctx); \
        } \
    } while(0)

#define REPORT_CRITICAL_ERROR(component, operation, details, code) \
    REPORT_ERROR(component, operation, details, GumusStability::ErrorSeverity::CRITICAL, code)

#define REPORT_WARNING(component, operation, details) \
    REPORT_ERROR(component, operation, details, GumusStability::ErrorSeverity::WARNING, 0)

} // namespace GumusStability