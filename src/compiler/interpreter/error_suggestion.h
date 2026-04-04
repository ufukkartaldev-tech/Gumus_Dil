#pragma once
#include "interpreter.h"
#include <string>

namespace gumus {
namespace compiler {
namespace interpreter {

/**
 * Error suggestion and Levenshtein distance functionality
 * Handles: undefined variable suggestions, function name corrections
 */
class ErrorSuggestion {
private:
    const Interpreter* interpreter;
    
public:
    explicit ErrorSuggestion(const Interpreter* interp) : interpreter(interp) {}
    
    // Main suggestion methods
    std::string suggestVariable(const std::string& name) const;
    std::string suggestFunction(const std::string& name) const;
    std::string suggestMethod(const std::string& className, const std::string& methodName) const;
    
    // Levenshtein distance calculation
    static int calculateDistance(const std::string& a, const std::string& b);
    
private:
    // Helper methods
    bool isAcceptableSuggestion(const std::string& name, const std::string& candidate, int distance) const;
    std::string findBestMatch(const std::string& name, const std::vector<std::string>& candidates) const;
    
    // Constants
    static const int MAX_SUGGESTION_DISTANCE = 2;
    static const int MIN_NAME_LENGTH = 3;
    static const double MAX_DISTANCE_RATIO = 0.34;
};

} // namespace interpreter
} // namespace compiler  
} // namespace gumus