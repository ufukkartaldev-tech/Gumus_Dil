#include "error_recovery.h"
#include <algorithm>
#include <iostream>
#include <thread>

namespace GumusStability {

// Global instances
std::unique_ptr<ErrorRecoveryManager> g_error_recovery = std::make_unique<ErrorRecoveryManager>();
std::unique_ptr<DegradationManager> g_degradation_manager = std::make_unique<DegradationManager>();

// ErrorRecoveryManager implementation
ErrorRecoveryManager::ErrorRecoveryManager() {
    // Register default recovery handlers
    registerRecoveryHandler("compiler", RecoveryStrategy::RETRY, 
        [](const ErrorContext& ctx) -> bool {
            std::cerr << "[RECOVERY] Attempting compiler retry for: " << ctx.operation << std::endl;
            return true; // Allow retry
        });
    
    registerRecoveryHandler("interpreter", RecoveryStrategy::FALLBACK,
        [](const ErrorContext& ctx) -> bool {
            std::cerr << "[RECOVERY] Using interpreter fallback for: " << ctx.operation << std::endl;
            return true; // Use fallback
        });
    
    registerRecoveryHandler("ide", RecoveryStrategy::GRACEFUL_SHUTDOWN,
        [](const ErrorContext& ctx) -> bool {
            if (ctx.severity >= ErrorSeverity::CRITICAL) {
                std::cerr << "[RECOVERY] IDE graceful shutdown initiated" << std::endl;
                return true;
            }
            return false;
        });
}

void ErrorRecoveryManager::reportError(const ErrorContext& context) {
    // Add to error history
    error_history.push_back(context);
    
    // Update component health
    auto& health = component_health[context.component];
    health.error_count++;
    health.last_error = context.timestamp;
    
    if (context.severity >= ErrorSeverity::ERROR) {
        health.is_healthy = false;
    }
    
    // Log error
    std::cerr << "[ERROR] " << context.component << "::" << context.operation 
              << " - " << context.details << " (Code: " << context.error_code << ")" << std::endl;
    
    // Attempt recovery
    if (context.severity >= ErrorSeverity::ERROR) {
        attemptRecovery(context);
    }
    
    // Cleanup old errors
    cleanupOldErrors();
}

void ErrorRecoveryManager::registerRecoveryHandler(const std::string& component, 
                                                  RecoveryStrategy strategy, 
                                                  RecoveryHandler handler) {
    recovery_handlers[component].emplace_back(strategy, handler);
}

bool ErrorRecoveryManager::attemptRecovery(const ErrorContext& context) {
    auto it = recovery_handlers.find(context.component);
    if (it == recovery_handlers.end()) {
        return false; // No recovery handlers for this component
    }
    
    for (const auto& [strategy, handler] : it->second) {
        if (executeRecoveryStrategy(context, strategy, handler)) {
            std::cerr << "[RECOVERY] Successfully recovered from error in " 
                      << context.component << std::endl;
            
            // Mark component as healthy again
            auto& health = component_health[context.component];
            health.is_healthy = true;
            health.last_success = std::chrono::steady_clock::now();
            
            return true;
        }
    }
    
    return false;
}

bool ErrorRecoveryManager::executeRecoveryStrategy(const ErrorContext& context, 
                                                  RecoveryStrategy strategy, 
                                                  RecoveryHandler handler) {
    switch (strategy) {
        case RecoveryStrategy::IGNORE:
            return true;
            
        case RecoveryStrategy::RETRY:
            for (int attempt = 0; attempt < max_retry_attempts; ++attempt) {
                if (attempt > 0) {
                    std::this_thread::sleep_for(retry_delay);
                }
                
                if (handler(context)) {
                    return true;
                }
            }
            return false;
            
        case RecoveryStrategy::FALLBACK:
            return handler(context);
            
        case RecoveryStrategy::GRACEFUL_SHUTDOWN:
            return handler(context);
            
        case RecoveryStrategy::FORCE_RESTART:
            return handler(context);
    }
    
    return false;
}

void ErrorRecoveryManager::setMaxRetryAttempts(int max_attempts) {
    max_retry_attempts = std::max(1, max_attempts);
}

void ErrorRecoveryManager::setRetryDelay(std::chrono::milliseconds delay) {
    retry_delay = delay;
}

size_t ErrorRecoveryManager::getErrorCount(const std::string& component) const {
    if (component.empty()) {
        return error_history.size();
    }
    
    return std::count_if(error_history.begin(), error_history.end(),
        [&component](const ErrorContext& ctx) {
            return ctx.component == component;
        });
}

std::vector<ErrorContext> ErrorRecoveryManager::getRecentErrors(size_t count) const {
    if (error_history.size() <= count) {
        return error_history;
    }
    
    return std::vector<ErrorContext>(error_history.end() - count, error_history.end());
}

double ErrorRecoveryManager::getErrorRate(const std::string& component) const {
    auto now = std::chrono::steady_clock::now();
    auto one_minute_ago = now - std::chrono::minutes(1);
    
    size_t recent_errors = 0;
    for (const auto& error : error_history) {
        if (error.timestamp >= one_minute_ago && 
            (component.empty() || error.component == component)) {
            recent_errors++;
        }
    }
    
    return static_cast<double>(recent_errors) / 60.0; // Errors per second
}

bool ErrorRecoveryManager::isComponentHealthy(const std::string& component) const {
    auto it = component_health.find(component);
    if (it == component_health.end()) {
        return true; // Unknown components are assumed healthy
    }
    
    return it->second.is_healthy;
}

void ErrorRecoveryManager::markComponentUnhealthy(const std::string& component) {
    component_health[component].is_healthy = false;
}

void ErrorRecoveryManager::markComponentHealthy(const std::string& component) {
    auto& health = component_health[component];
    health.is_healthy = true;
    health.last_success = std::chrono::steady_clock::now();
}

void ErrorRecoveryManager::cleanupOldErrors() {
    if (error_history.size() > max_error_history) {
        error_history.erase(error_history.begin(), 
                           error_history.begin() + (error_history.size() - max_error_history));
    }
}

// CircuitBreaker implementation
CircuitBreaker::CircuitBreaker(size_t failure_threshold, std::chrono::milliseconds timeout)
    : failure_threshold(failure_threshold), timeout(timeout) {}

bool CircuitBreaker::canExecute() const {
    switch (current_state) {
        case State::CLOSED:
            return true;
            
        case State::OPEN: {
            auto now = std::chrono::steady_clock::now();
            if (now - last_failure_time >= timeout) {
                const_cast<CircuitBreaker*>(this)->transitionToHalfOpen();
                return true;
            }
            return false;
        }
        
        case State::HALF_OPEN:
            return true;
    }
    
    return false;
}

void CircuitBreaker::recordSuccess() {
    failure_count = 0;
    if (current_state == State::HALF_OPEN) {
        transitionToClosed();
    }
}

void CircuitBreaker::recordFailure() {
    failure_count++;
    last_failure_time = std::chrono::steady_clock::now();
    
    if (current_state == State::HALF_OPEN) {
        transitionToOpen();
    } else if (current_state == State::CLOSED && failure_count >= failure_threshold) {
        transitionToOpen();
    }
}

CircuitBreaker::State CircuitBreaker::getState() const {
    return current_state;
}

void CircuitBreaker::transitionToOpen() {
    current_state = State::OPEN;
    std::cerr << "[CIRCUIT_BREAKER] Transitioned to OPEN state" << std::endl;
}

void CircuitBreaker::transitionToClosed() {
    current_state = State::CLOSED;
    failure_count = 0;
    std::cerr << "[CIRCUIT_BREAKER] Transitioned to CLOSED state" << std::endl;
}

void CircuitBreaker::transitionToHalfOpen() {
    current_state = State::HALF_OPEN;
    std::cerr << "[CIRCUIT_BREAKER] Transitioned to HALF_OPEN state" << std::endl;
}

// DegradationManager implementation
DegradationManager::DegradationManager() {
    // Initialize default feature flags
    feature_flags["memory_visualization"] = true;
    feature_flags["advanced_debugging"] = true;
    feature_flags["profiling"] = true;
    feature_flags["syntax_highlighting"] = true;
    feature_flags["auto_completion"] = true;
    
    // Initialize default resource limits
    resource_limits["memory_mb"] = 512.0;
    resource_limits["cpu_percent"] = 80.0;
    resource_limits["disk_mb"] = 1024.0;
}

void DegradationManager::setServiceLevel(ServiceLevel level) {
    current_level = level;
    applyServiceLevelConstraints();
    
    std::cerr << "[DEGRADATION] Service level set to " << static_cast<int>(level) << "%" << std::endl;
}

DegradationManager::ServiceLevel DegradationManager::getCurrentServiceLevel() const {
    return current_level;
}

bool DegradationManager::isFeatureEnabled(const std::string& feature) const {
    auto it = feature_flags.find(feature);
    return it != feature_flags.end() && it->second;
}

void DegradationManager::disableFeature(const std::string& feature) {
    feature_flags[feature] = false;
    std::cerr << "[DEGRADATION] Disabled feature: " << feature << std::endl;
}

void DegradationManager::enableFeature(const std::string& feature) {
    feature_flags[feature] = true;
    std::cerr << "[DEGRADATION] Enabled feature: " << feature << std::endl;
}

void DegradationManager::setResourceLimit(const std::string& resource, double limit) {
    resource_limits[resource] = limit;
}

double DegradationManager::getResourceLimit(const std::string& resource) const {
    auto it = resource_limits.find(resource);
    return it != resource_limits.end() ? it->second : 0.0;
}

void DegradationManager::applyServiceLevelConstraints() {
    switch (current_level) {
        case ServiceLevel::FULL_SERVICE:
            // All features enabled
            for (auto& [feature, enabled] : feature_flags) {
                enabled = true;
            }
            break;
            
        case ServiceLevel::REDUCED_SERVICE:
            // Disable non-essential features
            disableFeature("advanced_debugging");
            disableFeature("profiling");
            break;
            
        case ServiceLevel::MINIMAL_SERVICE:
            // Only core features
            disableFeature("memory_visualization");
            disableFeature("advanced_debugging");
            disableFeature("profiling");
            break;
            
        case ServiceLevel::EMERGENCY_SERVICE:
            // Bare minimum
            disableFeature("memory_visualization");
            disableFeature("advanced_debugging");
            disableFeature("profiling");
            disableFeature("auto_completion");
            break;
            
        case ServiceLevel::NO_SERVICE:
            // Disable everything
            for (auto& [feature, enabled] : feature_flags) {
                enabled = false;
            }
            break;
    }
}

} // namespace GumusStability