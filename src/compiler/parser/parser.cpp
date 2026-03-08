#include "parser.h"
#include <stdexcept>
#include "../json_hata.h"

Parser::Parser(const std::vector<Token>& tokens, MemoryArena& arena) : tokens(tokens), arena(arena), current(0), hadError(false) {
    // errorCountPerLine is automatically initialized as an empty map
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
                statements.push_back(varDeclaration());
            } else if (match({TokenType::KW_SINIF})) {
                statements.push_back(classDeclaration());
            } else if (match({TokenType::KW_FONKSIYON})) {
                statements.push_back(function("function"));
            } else if (match({TokenType::KW_MODUL})) { // Modul Tanimlama
                statements.push_back(moduleDeclaration());
            } else {
                statements.push_back(statement());
            }

        } catch (const GumusException& error) {
            hadError = true;
            advance(); // Consume the invalid token to prevent infinite loop
            
            // 🛡️ Adım 1: Error Counter Implementation
            if (error.line >= 0) {
                errorCountPerLine[error.line]++;
                
                // Eğer aynı satırda 3'ten fazla hata varsa, o satırı skip et
                if (errorCountPerLine[error.line] > 3) {
                    JsonHata(error.type, error.what(), error.line);
                    JsonHata("parser_warning", "Çok fazla hata - satır atlanıyor", error.line);
                    
                    // Skip to next statement
                    while (!isAtEnd()) {
                        if (previous().type == TokenType::SEMICOLON || previous().type == TokenType::NEW_LINE) break;
                        if (check(TokenType::KW_VAR) || check(TokenType::KW_SINIF) || 
                            check(TokenType::KW_FONKSIYON) || check(TokenType::KW_EGER) ||
                            check(TokenType::KW_DONGU) || check(TokenType::KW_DON) ||
                            check(TokenType::KW_YAZDIR)) break;
                        advance();
                    }
                    continue; // Continue with next statement
                }
            }
            
            JsonHata(error.type, error.what(), error.line);
            // Panic mode recovery: Bir sonraki statement basina kadar ilerle
            while (!isAtEnd()) {
                if (previous().type == TokenType::SEMICOLON || previous().type == TokenType::NEW_LINE) break;
                if (check(TokenType::KW_VAR) || check(TokenType::KW_SINIF) || 
                    check(TokenType::KW_FONKSIYON) || check(TokenType::KW_EGER) ||
                    check(TokenType::KW_DONGU) || check(TokenType::KW_DON) ||
                    check(TokenType::KW_YAZDIR)) break;
                advance();
            }
        } catch (const std::exception& error) {
            hadError = true;
            advance(); // Consume the invalid token
            
            // 🛡️ Adım 1: Error Counter for std exceptions
            int currentLine = 0;
            if (!tokens.empty() && current > 0 && current <= (int)tokens.size()) {
                currentLine = tokens[current-1].line;
            }
            
            if (currentLine >= 0) {
                errorCountPerLine[currentLine]++;
                
                // Eğer aynı satırda 3'ten fazla hata varsa, o satırı skip et
                if (errorCountPerLine[currentLine] > 3) {
                    JsonHata("parser_error", error.what(), currentLine);
                    JsonHata("parser_warning", "Çok fazla hata - satır atlanıyor", currentLine);
                    
                    // Skip to next statement
                    while (!isAtEnd()) {
                        if (previous().type == TokenType::SEMICOLON || previous().type == TokenType::NEW_LINE) break;
                        if (check(TokenType::KW_VAR) || check(TokenType::KW_SINIF) || 
                            check(TokenType::KW_FONKSIYON) || check(TokenType::KW_EGER) ||
                            check(TokenType::KW_DONGU) || check(TokenType::KW_DON) ||
                            check(TokenType::KW_YAZDIR)) break;
                        advance();
                    }
                    continue; // Continue with next statement
                }
            }
            
            JsonHata("parser_error", error.what(), currentLine);
            while (!isAtEnd()) {
                if (previous().type == TokenType::SEMICOLON || previous().type == TokenType::NEW_LINE) break;
                if (check(TokenType::KW_VAR) || check(TokenType::KW_SINIF) || 
                    check(TokenType::KW_FONKSIYON) || check(TokenType::KW_EGER) ||
                    check(TokenType::KW_DONGU) || check(TokenType::KW_DON) ||
                    check(TokenType::KW_YAZDIR)) break;
                advance();
            }
        }
    }
    return statements;
}

Stmt* Parser::varDeclaration() {
    Token name = consume(TokenType::IDENTIFIER, "Degisken adi bekleniyor.");

    Expr* initializer = nullptr;
    if (match({TokenType::EQUAL})) {
        initializer = expression();
    }

    consumeStatementEnd();
    auto stmt = arena.alloc<VarStmt>(name, initializer);
    stmt->line = name.line;
    return stmt;
}


Stmt* Parser::classDeclaration() {

    Token name = consume(TokenType::IDENTIFIER, "Sinif adi bekleniyor.");
    
    VariableExpr* superclass = nullptr;
    if (match({TokenType::LESS})) {
        consume(TokenType::IDENTIFIER, "Ust sinif adi bekleniyor.");
        superclass = arena.alloc<VariableExpr>(previous());
    }

    consume(TokenType::LBRACE, "Sinif govdesi icin '{' bekleniyor.");

    std::vector<FunctionStmt*> methods;
    while (!check(TokenType::RBRACE) && !isAtEnd()) {
        if (match({TokenType::NEW_LINE})) continue;

        if (match({TokenType::KW_FONKSIYON}) || check(TokenType::KW_KURUCU) || check(TokenType::IDENTIFIER)) {
            // function() handles the rest, including 'kurucu' keyword consumption if needed
            Stmt* methodStmt = function("metot");
            if (auto func = dynamic_cast<FunctionStmt*>(methodStmt)) {
                methods.push_back(func);
            }
        } else {
            throw GumusException("parser_error", peek().line, "Sinif icinde sadece metotlar tanimlanabilir.");
        }
    }


    consume(TokenType::RBRACE, "Sinif govdesinden sonra '}' bekleniyor.");
    auto stmt = arena.alloc<ClassStmt>(name, superclass, std::move(methods));
    stmt->line = name.line;
    return stmt;
}


Stmt* Parser::moduleDeclaration() {
    Token name = consume(TokenType::IDENTIFIER, "Modul adi bekleniyor.");
    consume(TokenType::LBRACE, "Modul govdesi icin '{' bekleniyor.");

    std::vector<Stmt*> statements;
    while (!check(TokenType::RBRACE) && !isAtEnd()) {
        if (match({TokenType::NEW_LINE})) continue;
        
        try {
            if (match({TokenType::KW_VAR})) statements.push_back(varDeclaration());
            else if (match({TokenType::KW_SINIF})) statements.push_back(classDeclaration());
            else if (match({TokenType::KW_FONKSIYON})) statements.push_back(function("function"));
            else statements.push_back(statement());
        } catch(const GumusException& e) {
            hadError = true;
            JsonHata(e.type, e.what(), e.line);
            advance();
        } catch(const std::exception& e) {
            hadError = true;
            JsonHata("parser_error", e.what(), 0);
            advance();
        }
    }
    consume(TokenType::RBRACE, "Modul govdesi sonunda '}' bekleniyor.");
    consumeStatementEnd();
    auto stmt = arena.alloc<ModuleStmt>(name, std::move(statements));
    stmt->line = name.line;
    return stmt;
}


Stmt* Parser::function(const std::string& kind) {
    Token name;
    if (check(TokenType::KW_KURUCU)) {
        name = advance();
    } else {
        name = consume(TokenType::IDENTIFIER, kind + " adi bekleniyor.");
    }
    consume(TokenType::LPAREN, kind + " adindan sonra '(' bekleniyor.");
    std::vector<Token> parameters;
    if (!check(TokenType::RPAREN)) {
        do {
            if (parameters.size() >= 255) {
                throw GumusException("parser_error", peek().line, "255'ten fazla parametre olamaz.");
            }
            parameters.push_back(consume(TokenType::IDENTIFIER, "Parametre adi bekleniyor."));
        } while (match({TokenType::COMMA}));
    }
    consume(TokenType::RPAREN, "Parametrelerden sonra ')' bekleniyor.");
    consume(TokenType::LBRACE, kind + " govdesi icin '{' bekleniyor.");
    std::vector<Stmt*> body = block();
    auto stmt = arena.alloc<FunctionStmt>(name, std::move(parameters), std::move(body));
    stmt->line = name.line;
    return stmt;
}


Stmt* Parser::statement() {
    if (match({TokenType::KW_EGER})) return ifStatement();
    if (match({TokenType::KW_DONGU})) return whileStatement();
    if (match({TokenType::KW_DON})) return returnStatement();
    if (match({TokenType::KW_YAZDIR})) return printStatement();
    if (match({TokenType::KW_DENEME})) return tryCatchStatement();
    if (match({TokenType::KW_KIR})) {
        Token keyword = previous();
        consumeStatementEnd();
        return arena.alloc<BreakStmt>(keyword);
    }
    if (match({TokenType::KW_DEVAM})) {
        Token keyword = previous();
        consumeStatementEnd();
        return arena.alloc<ContinueStmt>(keyword);
    }
    
    return expressionStatement();
}

Stmt* Parser::ifStatement() {
    bool parantezli = match({TokenType::LPAREN});
    
    Expr* condition = expression();
    
    if (parantezli) {
        consume(TokenType::RPAREN, "Kosuldan sonra ')' bekleniyor.");
    }
    
    consume(TokenType::LBRACE, "If govdesi icin '{' bekleniyor.");
    Stmt* thenBranch = arena.alloc<BlockStmt>(block());
    
    Stmt* elseBranch = nullptr;
    if (match({TokenType::KW_DEGILSE})) {
        if (match({TokenType::KW_EGER})) {
            elseBranch = ifStatement();
        } else {
            consume(TokenType::LBRACE, "Else govdesi icin '{' bekleniyor.");
            elseBranch = arena.alloc<BlockStmt>(block());
        }
    }
    
    auto stmt = arena.alloc<IfStmt>(condition, thenBranch, elseBranch);
    stmt->line = condition->line; 
    return stmt;
}


Stmt* Parser::whileStatement() {
    Token loopKeyword = previous();  // Capture 'dongu' keyword
    bool parantezli = match({TokenType::LPAREN});
    
    if (match({TokenType::KW_VAR})) {
        // FOR DONGUSU (Init var)
        Stmt* initializer = varDeclaration();
        
        Expr* condition = nullptr;
        if (!check(TokenType::SEMICOLON)) {
            condition = expression();
        }
        consume(TokenType::SEMICOLON, "For dongusu kosulundan sonra ';' bekleniyor.");
        
        Expr* increment = nullptr;
        if (!check(TokenType::RPAREN)) {
            increment = expression();
        }
        consume(TokenType::RPAREN, "For dongusu sonrasinda ')' bekleniyor.");
        
        consume(TokenType::LBRACE, "Dongu govdesi icin '{' bekleniyor.");
        Stmt* body = arena.alloc<BlockStmt>(block());
        
        // ForStmt Kullan
        return arena.alloc<ForStmt>(loopKeyword, initializer, condition, increment, body);
    }
    
    Expr* condOrInit = nullptr;
    if (!check(TokenType::RPAREN) && !check(TokenType::SEMICOLON)) {
        condOrInit = expression();
    }
    
    if (match({TokenType::SEMICOLON})) {
        // FOR DONGUSU (Expression Init)
        Stmt* initializer = nullptr;
        if (condOrInit != nullptr) initializer = arena.alloc<ExpressionStmt>(condOrInit);
        
        Expr* condition = nullptr;
        if (!check(TokenType::SEMICOLON)) {
            condition = expression();
        }
        consume(TokenType::SEMICOLON, "For dongusu kosulundan sonra ';' bekleniyor.");
        
        Expr* increment = nullptr;
        if (!check(TokenType::RPAREN)) {
            increment = expression();
        }
        consume(TokenType::RPAREN, "For dongusu sonrasinda ')' bekleniyor.");
        
        consume(TokenType::LBRACE, "Dongu govdesi icin '{' bekleniyor.");
        Stmt* body = arena.alloc<BlockStmt>(block());
        
        // ForStmt Kullan
        auto stmt = arena.alloc<ForStmt>(loopKeyword, initializer, condition, increment, body);
        stmt->line = loopKeyword.line;
        return stmt;
        
    } else {

        // WHILE DONGUSU
        if (parantezli) {
            consume(TokenType::RPAREN, "Kosuldan sonra ')' bekleniyor.");
        }
        
        consume(TokenType::LBRACE, "While govdesi icin '{' bekleniyor.");
        Stmt* body = arena.alloc<BlockStmt>(block());
        
        if (condOrInit == nullptr) {
            // dongu() -> sonsuz dongu (while(true))
             auto stmt = arena.alloc<WhileStmt>(arena.alloc<LiteralExpr>(Token{TokenType::KW_DOGRU, "dogru", 0, 0}), body);
             stmt->line = loopKeyword.line;
             return stmt;
        }
        
        auto stmt = arena.alloc<WhileStmt>(condOrInit, body);
        stmt->line = loopKeyword.line;
        return stmt;
    }
}


Stmt* Parser::tryCatchStatement() {
    consume(TokenType::LBRACE, "Try blogu icin '{' bekleniyor.");
    Stmt* tryBlock = arena.alloc<BlockStmt>(block());
    
    consume(TokenType::KW_YAKALA, "'dene' sonrasinda 'yakala' bekleniyor.");
    consume(TokenType::LPAREN, "'yakala' sonrasinda '(' bekleniyor.");
    Token errorName = consume(TokenType::IDENTIFIER, "Hata degiskeni adi bekleniyor.");
    consume(TokenType::RPAREN, "Hata degiskeninden sonra ')' bekleniyor.");
    
    consume(TokenType::LBRACE, "Catch blogu icin '{' bekleniyor.");
    Stmt* catchBlock = arena.alloc<BlockStmt>(block());
    auto stmt = arena.alloc<TryCatchStmt>(tryBlock, errorName, catchBlock);
    stmt->line = errorName.line;
    return stmt;
}


Stmt* Parser::returnStatement() {
    Token keyword = previous();
    Expr* value = nullptr;
    
    // Eger sonraki token ';' degilse ve ayni satirda ise, bir ifade donuyor demektir.
    if (!check(TokenType::SEMICOLON) && !check(TokenType::RBRACE) && peek().line == keyword.line) {
        value = expression();
    }
    consumeStatementEnd();
    auto stmt = arena.alloc<ReturnStmt>(keyword, value);
    stmt->line = keyword.line;
    return stmt;
}


Stmt* Parser::printStatement() {
    bool parantezli = match({TokenType::LPAREN});
    Expr* value = expression();
    
    if (parantezli) {
        consume(TokenType::RPAREN, "Ifadeden sonra ')' bekleniyor.");
    }
    
    consumeStatementEnd();
    auto stmt = arena.alloc<PrintStmt>(value);
    stmt->line = stmt->expression->line;
    return stmt;
}


Stmt* Parser::expressionStatement() {
    Expr* expr = expression();
    consumeStatementEnd();
    auto stmt = arena.alloc<ExpressionStmt>(expr);
    stmt->line = stmt->expression->line;
    return stmt;
}



std::vector<Stmt*> Parser::block() {
    std::vector<Stmt*> statements;

    while (!check(TokenType::RBRACE) && !isAtEnd()) {
        if (match({TokenType::NEW_LINE})) continue;
        
        if (match({TokenType::KW_VAR})) {
            statements.push_back(varDeclaration());
        } else {
            statements.push_back(statement());
        }
    }

    consume(TokenType::RBRACE, "Blok sonrasinda '}' bekleniyor.");
    return statements;
}

void Parser::consumeStatementEnd() {
    if (check(TokenType::SEMICOLON)) {
        throw GumusException("syntax_error", peek().line, 
            "GümüşDil'de noktalı virgül kullanılmaz! Modern sözdizimi kullan.");
    }
    if (match({TokenType::NEW_LINE})) return;
    if (check(TokenType::RBRACE)) return;
    if (check(TokenType::END_OF_FILE)) return;
    if (isAtEnd()) return;
    if (check(TokenType::KW_VAR) || check(TokenType::KW_SINIF) || 
        check(TokenType::KW_FONKSIYON) || check(TokenType::KW_EGER) ||
        check(TokenType::KW_DONGU) || check(TokenType::KW_DON) ||
        check(TokenType::KW_YAZDIR) || check(TokenType::KW_DENEME) ||
        check(TokenType::KW_KIR) || check(TokenType::KW_DEVAM)) {
        return;
    }
}

Expr* Parser::expression() {
    return assignment();
}

Expr* Parser::assignment() {
    Expr* expr = logicOr();

    if (match({TokenType::EQUAL})) {
        Token equals = previous();
        Expr* value = assignment();

        if (auto var = dynamic_cast<VariableExpr*>(expr)) {
            return arena.alloc<AssignExpr>(var->name, value);
        } else if (auto prop = dynamic_cast<PropertyExpr*>(expr)) {
             return arena.alloc<SetExpr>(prop->object, prop->name, value);
        } else if (auto get = dynamic_cast<GetExpr*>(expr)) {
             return arena.alloc<IndexSetExpr>(get->object, get->bracket, get->index, value);
        }

        throw GumusException("parser_error", equals.line, "Gecersiz atama hedefi.");
    }

    return expr;
}

Expr* Parser::logicOr() {
    Expr* expr = logicAnd();

    while (match({TokenType::LOGIC_OR})) {
        Token op = previous();
        Expr* right = logicAnd();
        expr = arena.alloc<LogicalExpr>(expr, op, right);
    }

    return expr;
}

Expr* Parser::logicAnd() {
    Expr* expr = equality();

    while (match({TokenType::LOGIC_AND})) {
        Token op = previous();
        Expr* right = equality();
        expr = arena.alloc<LogicalExpr>(expr, op, right);
    }

    return expr;
}

Expr* Parser::equality() {
    Expr* expr = comparison();

    while (match({TokenType::BANG_EQUAL, TokenType::EQUAL_EQUAL})) {
        Token op = previous();
        Expr* right = comparison();
        expr = arena.alloc<BinaryExpr>(expr, op, right);
    }

    return expr;
}

Expr* Parser::comparison() {
    Expr* expr = term();

    while (match({TokenType::GREATER, TokenType::GREATER_EQUAL, TokenType::LESS, TokenType::LESS_EQUAL})) {
        Token op = previous();
        Expr* right = term();
        expr = arena.alloc<BinaryExpr>(expr, op, right);
    }

    return expr;
}

Expr* Parser::term() {
    Expr* expr = factor();

    while (match({TokenType::MINUS, TokenType::PLUS})) {
        Token op = previous();
        Expr* right = factor();
        expr = arena.alloc<BinaryExpr>(expr, op, right);
    }

    return expr;
}

Expr* Parser::factor() {
    Expr* expr = unary();

    while (match({TokenType::DIVIDE, TokenType::MULTIPLY, TokenType::MOD})) {
        Token op = previous();
        Expr* right = unary();
        expr = arena.alloc<BinaryExpr>(expr, op, right);
    }

    return expr;
}

Expr* Parser::unary() {
    if (match({TokenType::BANG, TokenType::MINUS})) {
        Token op = previous();
        Expr* right = unary();
        return arena.alloc<UnaryExpr>(op, right);
    }

    if (match({TokenType::KW_YENI})) {
        return unary(); 
    }

    return call();
}

Expr* Parser::call() {
    Expr* expr = primary();

    while (true) {
        if (match({TokenType::LPAREN})) {
            expr = finishCall(expr);
        } else if (match({TokenType::DOT})) {
            if (check(TokenType::IDENTIFIER) || (int)peek().type >= (int)TokenType::KW_VAR) {
                Token name = advance();
                expr = arena.alloc<PropertyExpr>(expr, name);
            } else {
                throw GumusException("parser_error", peek().line, "Property adi bekleniyor.");
            }
        } else if (match({TokenType::LBRACKET})) {
            Token bracket = previous();
            expr = finishIndex(expr, bracket);
        } else {
            break;
        }
    }

    return expr;
}

Expr* Parser::finishCall(Expr* callee) {
    std::vector<Expr*> arguments;

    if (!check(TokenType::RPAREN)) {
        do {
            if (arguments.size() >= 255) {
                throw GumusException("parser_error", peek().line, "255'ten fazla arguman olamaz.");
            }
            arguments.push_back(expression());
        } while (match({TokenType::COMMA}));
    }

    Token paren = consume(TokenType::RPAREN, "Argumanlardan sonra ')' bekleniyor.");
    return arena.alloc<CallExpr>(callee, paren, std::move(arguments));
}

Expr* Parser::finishIndex(Expr* object, Token bracket) {
    Expr* index = expression();
    consume(TokenType::RBRACKET, "Index'ten sonra ']' bekleniyor.");
    return arena.alloc<GetExpr>(object, bracket, index);
}

Expr* Parser::primary() {
    if (match({TokenType::KW_DOGRU})) return arena.alloc<LiteralExpr>(previous());
    if (match({TokenType::KW_YANLIS})) return arena.alloc<LiteralExpr>(previous());
    if (match({TokenType::KW_BOS})) return arena.alloc<LiteralExpr>(previous());
    if (match({TokenType::INTEGER})) return arena.alloc<LiteralExpr>(previous());
    if (match({TokenType::STRING})) return arena.alloc<LiteralExpr>(previous());

    if (match({TokenType::IDENTIFIER})) {
        Token name = previous();
        if (match({TokenType::COLON_COLON})) {
            Token member = consume(TokenType::IDENTIFIER, "Modul uyesi bekleniyor.");
            return arena.alloc<ScopeResolutionExpr>(name, member);
        }
        return arena.alloc<VariableExpr>(name);
    }
    
    if (match({TokenType::KW_ATA})) {
        Token keyword = previous();
        consume(TokenType::DOT, "'ata' dan sonra '.' bekleniyor.");
        if (check(TokenType::IDENTIFIER) || (int)peek().type >= (int)TokenType::KW_VAR) {
            Token method = advance();
            return arena.alloc<SuperExpr>(keyword, method);
        }
        throw GumusException("parser_error", peek().line, "Metot adi bekleniyor.");
    }

    if (match({TokenType::KW_OZ})) {
        return arena.alloc<ThisExpr>(previous());
    }

    if (match({TokenType::LPAREN})) {
        Expr* expr = expression();
        consume(TokenType::RPAREN, "Ifadeden sonra ')' bekleniyor.");
        return expr;
    }

    if (match({TokenType::LBRACKET})) {
        std::vector<Expr*> elements;
        skipNewLines();
        if (!check(TokenType::RBRACKET)) {
            do {
                skipNewLines();
                elements.push_back(expression());
                skipNewLines();
                if (check(TokenType::RBRACKET)) break; // Support trailing comma
            } while (match({TokenType::COMMA}));
        }
        skipNewLines();
        consume(TokenType::RBRACKET, "Liste sonunda ']' bekleniyor.");
        return arena.alloc<ListExpr>(std::move(elements));
    }

    if (match({TokenType::LBRACE})) {
        std::vector<Expr*> keys;
        std::vector<Expr*> values;
        skipNewLines();
        if (!check(TokenType::RBRACE)) {
            do {
                skipNewLines();
                Expr* keyExpr;
                if (check(TokenType::IDENTIFIER)) {
                    keyExpr = arena.alloc<LiteralExpr>(advance());
                } else {
                    keyExpr = expression();
                }
                
                skipNewLines();
                consume(TokenType::COLON, "Sozluk anahtarindan sonra ':' bekleniyor.");
                skipNewLines();
                Expr* valueExpr = expression();
                
                keys.push_back(keyExpr);
                values.push_back(valueExpr);

                skipNewLines();
                if (check(TokenType::RBRACE)) break; // Support trailing comma
            } while (match({TokenType::COMMA}));
        }
        skipNewLines();
        consume(TokenType::RBRACE, "Sozluk sonunda '}' bekleniyor.");
        return arena.alloc<MapExpr>(std::move(keys), std::move(values));
    }

    throw GumusException("parser_error", peek().line, "Ifade bekleniyor.");
}

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
    return peek().type == TokenType::END_OF_FILE;
}

bool Parser::check(TokenType type) const {
    if (isAtEnd()) return false;
    return peek().type == type;
}

void Parser::skipNewLines() {
    while (match({TokenType::NEW_LINE}));
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
