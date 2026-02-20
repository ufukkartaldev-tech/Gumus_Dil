#ifndef GUMUS_PARSER_PARSER_H
#define GUMUS_PARSER_PARSER_H

#include <vector>
#include <memory>
#include "../lexer/token.h"
#include "ast.h"

class Parser {
public:
    Parser(const std::vector<Token>& tokens);
    std::vector<std::shared_ptr<Stmt>> parse();
    bool hasError() const;

private:
    std::vector<Token> tokens;
    int current;
    bool hadError;
    int errorCountPerLine[1000];

    std::shared_ptr<Stmt> varDeclaration();
    std::shared_ptr<Stmt> classDeclaration();
    std::shared_ptr<Stmt> moduleDeclaration(); // Yeni Modul Destegi
    std::shared_ptr<Stmt> statement();
    std::shared_ptr<Stmt> ifStatement();
    std::shared_ptr<Stmt> whileStatement();
    std::shared_ptr<Stmt> tryCatchStatement();
    std::shared_ptr<Stmt> function(const std::string& kind);

    std::shared_ptr<Stmt> returnStatement();
    std::shared_ptr<Stmt> printStatement();
    std::shared_ptr<Stmt> expressionStatement();
    std::vector<std::shared_ptr<Stmt>> block();

    std::shared_ptr<Expr> expression();
    std::shared_ptr<Expr> assignment();
    std::shared_ptr<Expr> logicOr();
    std::shared_ptr<Expr> logicAnd();
    std::shared_ptr<Expr> equality();

    std::shared_ptr<Expr> comparison();
    std::shared_ptr<Expr> term();
    std::shared_ptr<Expr> factor();
    std::shared_ptr<Expr> unary();
    std::shared_ptr<Expr> call();
    std::shared_ptr<Expr> finishCall(std::shared_ptr<Expr> callee);
    std::shared_ptr<Expr> finishIndex(std::shared_ptr<Expr> object, Token bracket);
    std::shared_ptr<Expr> primary();

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
