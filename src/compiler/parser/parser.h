#pragma once

#include <vector>
#include <memory>
#include <unordered_map>
#include "../lexer/token.h"
#include "ast.h"
#include "arena.h"

namespace gumus {
namespace compiler {
namespace parser {

// Forward declarations for modular components
class StatementParser;
class ExpressionParser;
class ErrorRecovery;

/**
 * Main Parser class - now modular and focused on coordination
 * Delegates specific parsing tasks to specialized components
 */
class Parser {
public:
    Parser(const std::vector<Token>& tokens, MemoryArena& arena);
    std::vector<Stmt*> parse();
    bool hasError() const;

    // Public interface for modular components
    std::vector<Token> tokens;
    MemoryArena& arena;
    int current;
    bool hadError;

    // Token navigation methods (public for modules)
    Token peek() const;
    Token previous() const;
    Token advance();
    bool isAtEnd() const;
    bool check(TokenType type) const;
    bool checkNext(TokenType type) const;
    bool match(const std::vector<TokenType>& types);
    Token consume(TokenType type, const std::string& message);

    // Expression parsing (delegated to ExpressionParser)
    Expr* expression();

private:
    // Modular components
    std::unique_ptr<StatementParser> statementParser;
    std::unique_ptr<ExpressionParser> expressionParser;
    std::unique_ptr<ErrorRecovery> errorRecovery;

    // Helper methods
    void skipNewLines();
    
    friend class StatementParser;
    friend class ExpressionParser;
    friend class ErrorRecovery;
};

} // namespace parser
} // namespace compiler  
} // namespace gumus
