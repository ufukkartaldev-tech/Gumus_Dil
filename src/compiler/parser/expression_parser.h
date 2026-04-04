#pragma once
#include "parser.h"

namespace gumus {
namespace compiler {
namespace parser {

/**
 * Expression parsing functionality separated from main parser
 * Handles: binary expressions, unary expressions, call expressions,
 * property access, literals, grouping
 */
class ExpressionParser {
private:
    Parser* parser;
    
public:
    explicit ExpressionParser(Parser* p) : parser(p) {}
    
    // Main expression entry point
    Expr* expression();
    
    // Precedence levels (from lowest to highest)
    Expr* assignment();
    Expr* logicalOr();
    Expr* logicalAnd();
    Expr* equality();
    Expr* comparison();
    Expr* term();
    Expr* factor();
    Expr* unary();
    Expr* call();
    Expr* primary();
    
    // Call and property access helpers
    Expr* finishCall(Expr* callee);
    Expr* finishProperty(Expr* object);
    
    // Array and object literals
    Expr* arrayLiteral();
    Expr* objectLiteral();
    
    // Lambda expressions
    Expr* lambdaExpression();
    
private:
    // Helper methods
    bool isAssignmentTarget(Expr* expr);
    TokenType getAssignmentOperator();
};

} // namespace parser
} // namespace compiler  
} // namespace gumus