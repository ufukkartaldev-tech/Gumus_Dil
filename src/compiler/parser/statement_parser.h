#pragma once
#include "parser.h"

namespace gumus {
namespace compiler {
namespace parser {

/**
 * Statement parsing functionality separated from main parser
 * Handles: var declarations, class declarations, function declarations, 
 * control flow statements (if, while, for, try-catch)
 */
class StatementParser {
private:
    Parser* parser;
    
public:
    explicit StatementParser(Parser* p) : parser(p) {}
    
    // Declaration statements
    Stmt* varDeclaration();
    Stmt* classDeclaration();
    Stmt* moduleDeclaration();
    Stmt* function(const std::string& kind);
    
    // Control flow statements
    Stmt* ifStatement();
    Stmt* whileStatement();
    Stmt* forStatement();
    Stmt* tryStatement();
    Stmt* returnStatement();
    Stmt* breakStatement();
    Stmt* continueStatement();
    
    // Block and expression statements
    Stmt* blockStatement();
    Stmt* expressionStatement();
    Stmt* printStatement();
    
    // Main statement dispatcher
    Stmt* statement();
    
private:
    // Helper methods
    void consumeStatementEnd();
    std::vector<Stmt*> parseBlock();
};

} // namespace parser
} // namespace compiler  
} // namespace gumus