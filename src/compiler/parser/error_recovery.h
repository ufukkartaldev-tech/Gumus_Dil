#pragma once
#include "parser.h"
#include <unordered_map>

namespace gumus {
namespace compiler {
namespace parser {

/**
 * Error recovery and handling functionality for parser
 * Handles: panic mode recovery, error counting, synchronization
 */
class ErrorRecovery {
private:
    Parser* parser;
    std::unordered_map<int, int> errorCountPerLine;
    
    static const int MAX_ERRORS_PER_LINE = 3;
    
public:
    explicit ErrorRecovery(Parser* p) : parser(p) {}
    
    // Main error handling
    void handleGumusException(const GumusException& error);
    void handleStdException(const std::exception& error);
    
    // Recovery strategies
    void panicModeRecovery();
    void synchronizeToNextStatement();
    void skipToNextDeclaration();
    
    // Error counting and limiting
    bool shouldSkipLine(int line);
    void incrementErrorCount(int line);
    int getErrorCount(int line) const;
    
    // Synchronization points
    bool isAtSynchronizationPoint() const;
    bool isAtDeclarationStart() const;
    bool isAtStatementStart() const;
    
private:
    // Helper methods
    int getCurrentLine() const;
    void reportError(const std::string& type, const std::string& message, int line);
    void reportWarning(const std::string& message, int line);
};

} // namespace parser
} // namespace compiler  
} // namespace gumus