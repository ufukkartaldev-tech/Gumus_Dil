#ifndef GUMUS_PARSER_PARSER_H
#define GUMUS_PARSER_PARSER_H

#include <vector>
#include <memory>
#include <unordered_map>
#include "../lexer/token.h"
#include "ast.h"
#include "arena.h"

class Parser {
public:
    Parser(const std::vector<Token>& tokens, MemoryArena& arena);
    std::vector<Stmt*> parse();
    bool hasError() const;

private:
    std::vector<Token> tokens;
    MemoryArena& arena;
    int current;
    bool hadError;
    std::unordered_map<int, int> errorCountPerLine;

    Stmt* varDeclaration();
    Stmt* classDeclaration();
    Stmt* moduleDeclaration(); // Yeni Modul Destegi
    Stmt* statement();
    Stmt* ifStatement();
    Stmt* whileStatement();
    Stmt* tryCatchStatement();
    Stmt* function(const std::string& kind);

    Stmt* returnStatement();
    Stmt* printStatement();
    Stmt* expressionStatement();
    std::vector<Stmt*> block();

    Expr* expression();
    Expr* assignment();
    Expr* logicOr();
    Expr* logicAnd();
    Expr* equality();

    Expr* comparison();
    Expr* term();
    Expr* factor();
    Expr* unary();
    Expr* call();
    Expr* finishCall(Expr* callee);
    Expr* finishIndex(Expr* object, Token bracket);
    Expr* primary();

    Token peek() const;
    Token previous() const;
    Token advance();
    bool isAtEnd() const;
    bool check(TokenType type) const;
    bool match(const std::vector<TokenType>& types);
    Token consume(TokenType type, const std::string& message);
    void consumeStatementEnd(); // Noktali virgul veya yeni satir kontrolu
    void skipNewLines();
};

#endif // GUMUS_PARSER_PARSER_H
