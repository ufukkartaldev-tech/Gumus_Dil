#include "parser.h"
#include "statement_parser.h"
#include "expression_parser.h"
#include "error_recovery.h"
#include <stdexcept>

namespace gumus {
namespace compiler {
namespace parser {

Parser::Parser(const std::vector<Token>& tokens, MemoryArena& arena) 
    : tokens(tokens), arena(arena), current(0), hadError(false) {
    
    // Initialize modular components
    statementParser = std::make_unique<StatementParser>(this);
    expressionParser = std::make_unique<ExpressionParser>(this);
    errorRecovery = std::make_unique<ErrorRecovery>(this);
}

bool Parser::hasError() const {
    return hadError;
}

std::vector<Stmt*> Parser::parse() {
    std::vector<Stmt*> statements;
    
    while (!isAtEnd()) {
        try {
            while (match({TokenType::NEW_LINE}));
            if (isAtEnd()) break;

            if (match({TokenType::KW_VAR})) {
                statements.push_back(statementParser->varDeclaration());
            } else if (match({TokenType::KW_SINIF})) {
                statements.push_back(statementParser->classDeclaration());
            } else if (match({TokenType::KW_FONKSIYON})) {
                statements.push_back(statementParser->function("function"));
            } else if (match({TokenType::KW_MODUL})) {
                statements.push_back(statementParser->moduleDeclaration());
            } else if (match({TokenType::KW_DAHIL_ET})) {
                statements.push_back(statementParser->importStatement());
            } else {
                statements.push_back(statementParser->statement());
            }


        } catch (const GumusException& error) {
            errorRecovery->handleGumusException(error);
        } catch (const std::exception& error) {
            errorRecovery->handleStdException(error);
        }
    }
    
    return statements;
}

Expr* Parser::expression() {
    return expressionParser->expression();
}

// Token navigation methods
Token Parser::peek() const {
    if (current >= tokens.size()) {
        return tokens.back(); // EOF token
    }
    return tokens[current];
}

Token Parser::previous() const {
    return tokens[current - 1];
}

Token Parser::advance() {
    if (!isAtEnd()) current++;
    return previous();
}

bool Parser::isAtEnd() const {
    return peek().type == TokenType::EOF_TOKEN || peek().type == TokenType::END_OF_FILE;
}

bool Parser::check(TokenType type) const {
    if (isAtEnd()) return false;
    return peek().type == type;
}

bool Parser::checkNext(TokenType type) const {
    if (current + 1 >= (int)tokens.size()) return false;
    return tokens[current + 1].type == type;
}

bool Parser::match(const std::vector<TokenType>& types) {
    for (TokenType type : types) {
        if (check(type)) {
            advance();
            return true;
        }
    }
    return false;
}

Token Parser::consume(TokenType type, const std::string& message) {
    if (check(type)) return advance();
    
    throw GumusException("parser_error", peek().line, message);
}

void Parser::skipNewLines() {
    while (match({TokenType::NEW_LINE}));
}

} // namespace parser
} // namespace compiler  
} // namespace gumus