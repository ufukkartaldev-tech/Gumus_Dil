#include "statement_parser.h"
#include "../json_hata.h"

namespace gumus {
namespace compiler {
namespace parser {

Stmt* StatementParser::varDeclaration() {
    Token name = parser->consume(TokenType::IDENTIFIER, "Degisken adi bekleniyor.");

    Expr* initializer = nullptr;
    if (parser->match({TokenType::EQUAL})) {
        initializer = parser->expression();
    }

    consumeStatementEnd();
    auto stmt = parser->arena.alloc<VarStmt>(name, initializer);
    stmt->line = name.line;
    return stmt;
}

Stmt* StatementParser::classDeclaration() {
    Token name = parser->consume(TokenType::IDENTIFIER, "Sinif adi bekleniyor.");
    
    VariableExpr* superclass = nullptr;
    if (parser->match({TokenType::LESS})) {
        parser->consume(TokenType::IDENTIFIER, "Ust sinif adi bekleniyor.");
        superclass = parser->arena.alloc<VariableExpr>(parser->previous());
    }

    parser->consume(TokenType::LBRACE, "Sinif govdesi icin '{' bekleniyor.");

    std::vector<FunctionStmt*> methods;
    while (!parser->check(TokenType::RBRACE) && !parser->isAtEnd()) {
        if (parser->match({TokenType::NEW_LINE})) continue;

        if (parser->match({TokenType::KW_FONKSIYON}) || 
            parser->check(TokenType::KW_KURUCU) || 
            parser->check(TokenType::IDENTIFIER)) {
            
            Stmt* methodStmt = function("metot");
            if (auto func = dynamic_cast<FunctionStmt*>(methodStmt)) {
                methods.push_back(func);
            }
        } else {
            throw GumusException("parser_error", parser->peek().line, 
                               "Sinif icinde sadece metotlar tanimlanabilir.");
        }
    }

    parser->consume(TokenType::RBRACE, "Sinif govdesinden sonra '}' bekleniyor.");
    auto stmt = parser->arena.alloc<ClassStmt>(name, superclass, std::move(methods));
    stmt->line = name.line;
    return stmt;
}

Stmt* StatementParser::moduleDeclaration() {
    Token name = parser->consume(TokenType::IDENTIFIER, "Modul adi bekleniyor.");
    parser->consume(TokenType::LBRACE, "Modul govdesi icin '{' bekleniyor.");

    std::vector<Stmt*> statements;
    while (!parser->check(TokenType::RBRACE) && !parser->isAtEnd()) {
        if (parser->match({TokenType::NEW_LINE})) continue;
        
        try {
            if (parser->match({TokenType::KW_VAR})) {
                statements.push_back(varDeclaration());
            } else if (parser->match({TokenType::KW_SINIF})) {
                statements.push_back(classDeclaration());
            } else if (parser->match({TokenType::KW_FONKSIYON})) {
                statements.push_back(function("function"));
            } else {
                statements.push_back(statement());
            }
        } catch(const GumusException& e) {
            parser->hadError = true;
            JsonHata(e.type, e.what(), e.line);
            parser->advance();
        } catch(const std::exception& e) {
            parser->hadError = true;
            JsonHata("parser_error", e.what(), 0);
            parser->advance();
        }
    }
    
    parser->consume(TokenType::RBRACE, "Modul govdesi sonunda '}' bekleniyor.");
    consumeStatementEnd();
    auto stmt = parser->arena.alloc<ModuleStmt>(name, std::move(statements));
    stmt->line = name.line;
    return stmt;
}

Stmt* StatementParser::function(const std::string& kind) {
    Token name;
    if (parser->check(TokenType::KW_KURUCU)) {
        name = parser->advance();
    } else {
        name = parser->consume(TokenType::IDENTIFIER, kind + " adi bekleniyor.");
    }

    parser->consume(TokenType::LPAREN, kind + " parametreleri icin '(' bekleniyor.");
    
    std::vector<Token> parameters;
    if (!parser->check(TokenType::RPAREN)) {
        do {
            if (parameters.size() >= 255) {
                throw GumusException("parser_error", parser->peek().line, 
                                   "Fonksiyon en fazla 255 parametre alabilir.");
            }
            parameters.push_back(parser->consume(TokenType::IDENTIFIER, "Parametre adi bekleniyor."));
        } while (parser->match({TokenType::COMMA}));
    }
    
    parser->consume(TokenType::RPAREN, "Parametrelerden sonra ')' bekleniyor.");
    parser->consume(TokenType::LBRACE, kind + " govdesi icin '{' bekleniyor.");
    
    std::vector<Stmt*> body = parseBlock();
    
    auto stmt = parser->arena.alloc<FunctionStmt>(name, std::move(parameters), std::move(body));
    stmt->line = name.line;
    return stmt;
}

Stmt* StatementParser::ifStatement() {
    parser->consume(TokenType::LPAREN, "'eger' ifadesinden sonra '(' bekleniyor.");
    Expr* condition = parser->expression();
    parser->consume(TokenType::RPAREN, "Kosuldan sonra ')' bekleniyor.");

    Stmt* thenBranch = statement();
    Stmt* elseBranch = nullptr;
    if (parser->match({TokenType::KW_YOKSA})) {
        elseBranch = statement();
    }

    auto stmt = parser->arena.alloc<IfStmt>(condition, thenBranch, elseBranch);
    stmt->line = parser->previous().line;
    return stmt;
}

Stmt* StatementParser::whileStatement() {
    parser->consume(TokenType::LPAREN, "'dongu' ifadesinden sonra '(' bekleniyor.");
    Expr* condition = parser->expression();
    parser->consume(TokenType::RPAREN, "Kosuldan sonra ')' bekleniyor.");
    Stmt* body = statement();

    auto stmt = parser->arena.alloc<WhileStmt>(condition, body);
    stmt->line = parser->previous().line;
    return stmt;
}

Stmt* StatementParser::forStatement() {
    parser->consume(TokenType::LPAREN, "'icin' dongusunden sonra '(' bekleniyor.");

    Stmt* initializer;
    if (parser->match({TokenType::SEMICOLON})) {
        initializer = nullptr;
    } else if (parser->match({TokenType::KW_VAR})) {
        initializer = varDeclaration();
    } else {
        initializer = expressionStatement();
    }

    Expr* condition = nullptr;
    if (!parser->check(TokenType::SEMICOLON)) {
        condition = parser->expression();
    }
    parser->consume(TokenType::SEMICOLON, "Dongu kosulundan sonra ';' bekleniyor.");

    Expr* increment = nullptr;
    if (!parser->check(TokenType::RPAREN)) {
        increment = parser->expression();
    }
    parser->consume(TokenType::RPAREN, "Dongu parametrelerinden sonra ')' bekleniyor.");

    Stmt* body = statement();

    auto stmt = parser->arena.alloc<ForStmt>(initializer, condition, increment, body);
    stmt->line = parser->previous().line;
    return stmt;
}

Stmt* StatementParser::tryStatement() {
    Stmt* tryBlock = blockStatement();
    
    std::vector<CatchClause*> catchClauses;
    while (parser->match({TokenType::KW_YAKALA})) {
        parser->consume(TokenType::LPAREN, "'yakala' dan sonra '(' bekleniyor.");
        Token exceptionName = parser->consume(TokenType::IDENTIFIER, "Istisna degiskeni adi bekleniyor.");
        parser->consume(TokenType::RPAREN, "Istisna degiskeninden sonra ')' bekleniyor.");
        Stmt* catchBlock = blockStatement();
        
        auto catchClause = parser->arena.alloc<CatchClause>(exceptionName, catchBlock);
        catchClauses.push_back(catchClause);
    }
    
    Stmt* finallyBlock = nullptr;
    if (parser->match({TokenType::KW_SONUNDA})) {
        finallyBlock = blockStatement();
    }
    
    if (catchClauses.empty() && finallyBlock == nullptr) {
        throw GumusException("parser_error", parser->previous().line, 
                           "'dene' blogundan sonra en az bir 'yakala' veya 'sonunda' blogu olmali.");
    }
    
    auto stmt = parser->arena.alloc<TryStmt>(tryBlock, std::move(catchClauses), finallyBlock);
    stmt->line = parser->previous().line;
    return stmt;
}

Stmt* StatementParser::returnStatement() {
    Token keyword = parser->previous();
    Expr* value = nullptr;
    if (!parser->check(TokenType::SEMICOLON) && !parser->check(TokenType::NEW_LINE)) {
        value = parser->expression();
    }

    consumeStatementEnd();
    auto stmt = parser->arena.alloc<ReturnStmt>(keyword, value);
    stmt->line = keyword.line;
    return stmt;
}

Stmt* StatementParser::breakStatement() {
    Token keyword = parser->previous();
    consumeStatementEnd();
    auto stmt = parser->arena.alloc<BreakStmt>(keyword);
    stmt->line = keyword.line;
    return stmt;
}

Stmt* StatementParser::continueStatement() {
    Token keyword = parser->previous();
    consumeStatementEnd();
    auto stmt = parser->arena.alloc<ContinueStmt>(keyword);
    stmt->line = keyword.line;
    return stmt;
}

Stmt* StatementParser::blockStatement() {
    std::vector<Stmt*> statements = parseBlock();
    auto stmt = parser->arena.alloc<BlockStmt>(std::move(statements));
    stmt->line = parser->previous().line;
    return stmt;
}

Stmt* StatementParser::expressionStatement() {
    Expr* expr = parser->expression();
    consumeStatementEnd();
    auto stmt = parser->arena.alloc<ExpressionStmt>(expr);
    stmt->line = parser->previous().line;
    return stmt;
}

Stmt* StatementParser::printStatement() {
    Expr* value = parser->expression();
    consumeStatementEnd();
    auto stmt = parser->arena.alloc<PrintStmt>(value);
    stmt->line = parser->previous().line;
    return stmt;
}

Stmt* StatementParser::statement() {
    if (parser->match({TokenType::KW_EGER})) return ifStatement();
    if (parser->match({TokenType::KW_DONGU})) return whileStatement();
    if (parser->match({TokenType::KW_ICIN})) return forStatement();
    if (parser->match({TokenType::KW_DENE})) return tryStatement();
    if (parser->match({TokenType::KW_DON})) return returnStatement();
    if (parser->match({TokenType::KW_KIR})) return breakStatement();
    if (parser->match({TokenType::KW_DEVAM})) return continueStatement();
    if (parser->match({TokenType::KW_YAZDIR})) return printStatement();
    if (parser->match({TokenType::LBRACE})) return blockStatement();

    return expressionStatement();
}

void StatementParser::consumeStatementEnd() {
    if (!parser->match({TokenType::SEMICOLON, TokenType::NEW_LINE}) && 
        !parser->check(TokenType::RBRACE) && !parser->isAtEnd()) {
        throw GumusException("parser_error", parser->peek().line, 
                           "Ifade sonunda ';' veya yeni satir bekleniyor.");
    }
}

std::vector<Stmt*> StatementParser::parseBlock() {
    std::vector<Stmt*> statements;

    while (!parser->check(TokenType::RBRACE) && !parser->isAtEnd()) {
        if (parser->match({TokenType::NEW_LINE})) continue;
        
        try {
            if (parser->match({TokenType::KW_VAR})) {
                statements.push_back(varDeclaration());
            } else if (parser->match({TokenType::KW_SINIF})) {
                statements.push_back(classDeclaration());
            } else if (parser->match({TokenType::KW_FONKSIYON})) {
                statements.push_back(function("function"));
            } else {
                statements.push_back(statement());
            }
        } catch(const GumusException& e) {
            parser->hadError = true;
            JsonHata(e.type, e.what(), e.line);
            parser->advance();
        } catch(const std::exception& e) {
            parser->hadError = true;
            JsonHata("parser_error", e.what(), 0);
            parser->advance();
        }
    }

    parser->consume(TokenType::RBRACE, "Blok sonunda '}' bekleniyor.");
    return statements;
}

} // namespace parser
} // namespace compiler  
} // namespace gumus