#ifndef GUMUS_PARSER_PARSER_H
#define GUMUS_PARSER_PARSER_H

#include <vector>
#include <memory>
#include <unordered_map>
#include "../lexer/token.h"
#include "ast.h"

class Parser {
public:
    Parser(const std::vector<Token>& tokens);
    std::vector<std::unique_ptr<Stmt>> parse();
    bool hasError() const;

private:
    std::vector<Token> tokens;
    int current;
    bool hadError;
    std::unordered_map<int, int> errorCountPerLine;

    std::unique_ptr<Stmt> varDeclaration();
    std::unique_ptr<Stmt> classDeclaration();
    std::unique_ptr<Stmt> moduleDeclaration(); // Yeni Modul Destegi
    std::unique_ptr<Stmt> statement();
    std::unique_ptr<Stmt> ifStatement();
    std::unique_ptr<Stmt> whileStatement();
    std::unique_ptr<Stmt> tryCatchStatement();
    std::unique_ptr<Stmt> function(const std::string& kind);

    std::unique_ptr<Stmt> returnStatement();
    std::unique_ptr<Stmt> printStatement();
    std::unique_ptr<Stmt> expressionStatement();
    std::vector<std::unique_ptr<Stmt>> block();

    std::unique_ptr<Expr> expression();
    std::unique_ptr<Expr> assignment();
    std::unique_ptr<Expr> logicOr();
    std::unique_ptr<Expr> logicAnd();
    std::unique_ptr<Expr> equality();

    std::unique_ptr<Expr> comparison();
    std::unique_ptr<Expr> term();
    std::unique_ptr<Expr> factor();
    std::unique_ptr<Expr> unary();
    std::unique_ptr<Expr> call();
    std::unique_ptr<Expr> finishCall(std::unique_ptr<Expr> callee);
    std::unique_ptr<Expr> finishIndex(std::unique_ptr<Expr> object, Token bracket);
    std::unique_ptr<Expr> primary();

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
