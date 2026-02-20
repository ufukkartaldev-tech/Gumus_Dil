#include "parser.h"
#include <stdexcept>
#include <cstring>
#include "../json_hata.h"

Parser::Parser(const std::vector<Token>& tokens) : tokens(tokens), current(0), hadError(false) {
    // Initialize error counter array
    memset(errorCountPerLine, 0, sizeof(errorCountPerLine));
}

bool Parser::hasError() const {
    return hadError;
}

std::vector<std::shared_ptr<Stmt>> Parser::parse() {
    std::vector<std::shared_ptr<Stmt>> statements;
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
            if (error.line < 10000) {
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
            
            if (currentLine < 10000) {
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

std::shared_ptr<Stmt> Parser::varDeclaration() {
    Token name = consume(TokenType::IDENTIFIER, "Degisken adi bekleniyor.");

    std::shared_ptr<Expr> initializer = nullptr;
    if (match({TokenType::EQUAL})) {
        initializer = expression();
    }

    consumeStatementEnd();
    auto stmt = std::make_shared<VarStmt>(name, initializer);
    stmt->line = name.line;
    return stmt;
}


std::shared_ptr<Stmt> Parser::classDeclaration() {

    Token name = consume(TokenType::IDENTIFIER, "Sinif adi bekleniyor.");
    
    std::shared_ptr<VariableExpr> superclass = nullptr;
    if (match({TokenType::LESS})) {
        consume(TokenType::IDENTIFIER, "Ust sinif adi bekleniyor.");
        superclass = std::make_shared<VariableExpr>(previous());
    }

    consume(TokenType::LBRACE, "Sinif govdesi icin '{' bekleniyor.");

    std::vector<std::shared_ptr<FunctionStmt>> methods;
    while (!check(TokenType::RBRACE) && !isAtEnd()) {
        if (match({TokenType::NEW_LINE})) continue;

        if (match({TokenType::KW_FONKSIYON}) || check(TokenType::KW_KURUCU) || check(TokenType::IDENTIFIER)) {
            // function() handles the rest, including 'kurucu' keyword consumption if needed
            std::shared_ptr<Stmt> methodStmt = function("metot");
            if (auto func = std::dynamic_pointer_cast<FunctionStmt>(methodStmt)) {
                methods.push_back(func);
            }
        } else {
            throw GumusException("parser_error", peek().line, "Sinif icinde sadece metotlar tanimlanabilir.");
        }
    }


    consume(TokenType::RBRACE, "Sinif govdesinden sonra '}' bekleniyor.");
    auto stmt = std::make_shared<ClassStmt>(name, superclass, methods);
    stmt->line = name.line;
    return stmt;
}


std::shared_ptr<Stmt> Parser::moduleDeclaration() {
    Token name = consume(TokenType::IDENTIFIER, "Modul adi bekleniyor.");
    consume(TokenType::LBRACE, "Modul govdesi icin '{' bekleniyor.");

    std::vector<std::shared_ptr<Stmt>> statements;
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
    auto stmt = std::make_shared<ModuleStmt>(name, statements);
    stmt->line = name.line;
    return stmt;
}


std::shared_ptr<Stmt> Parser::function(const std::string& kind) {
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
    std::vector<std::shared_ptr<Stmt>> body = block();
    auto stmt = std::make_shared<FunctionStmt>(name, parameters, body);
    stmt->line = name.line;
    return stmt;
}


std::shared_ptr<Stmt> Parser::statement() {
    if (match({TokenType::KW_EGER})) return ifStatement();
    if (match({TokenType::KW_DONGU})) return whileStatement();
    if (match({TokenType::KW_DON})) return returnStatement();
    if (match({TokenType::KW_YAZDIR})) return printStatement();
    if (match({TokenType::KW_DENEME})) return tryCatchStatement();
    if (match({TokenType::KW_KIR})) {
        Token keyword = previous();
        consumeStatementEnd();
        return std::make_shared<BreakStmt>(keyword);
    }
    if (match({TokenType::KW_DEVAM})) {
        Token keyword = previous();
        consumeStatementEnd();
        return std::make_shared<ContinueStmt>(keyword);
    }
    // REMOVED: if (match({TokenType::LBRACE})) return std::make_shared<BlockStmt>(block());
    // Reason: { can be a dictionary expression, blocks are explicitly parsed in control structures
    
    return expressionStatement();
}

std::shared_ptr<Stmt> Parser::ifStatement() {
    bool parantezli = match({TokenType::LPAREN});
    
    std::shared_ptr<Expr> condition = expression();
    
    if (parantezli) {
        consume(TokenType::RPAREN, "Kosuldan sonra ')' bekleniyor.");
    }
    
    consume(TokenType::LBRACE, "If govdesi icin '{' bekleniyor.");
    std::shared_ptr<Stmt> thenBranch = std::make_shared<BlockStmt>(block());
    
    std::shared_ptr<Stmt> elseBranch = nullptr;
    if (match({TokenType::KW_DEGILSE})) {
        if (match({TokenType::KW_EGER})) {
            elseBranch = ifStatement();
        } else {
            consume(TokenType::LBRACE, "Else govdesi icin '{' bekleniyor.");
            elseBranch = std::make_shared<BlockStmt>(block());
        }
    }
    
    auto stmt = std::make_shared<IfStmt>(condition, thenBranch, elseBranch);
    stmt->line = condition->line; // Use condition's line or track keyword
    return stmt;
}


std::shared_ptr<Stmt> Parser::whileStatement() {
    Token loopKeyword = previous();  // Capture 'dongu' keyword
    bool parantezli = match({TokenType::LPAREN});
    
    // 1. Kismi Parse Et (Init veya Condition)
    // Eger 'var' ile basliyorsa kesinlikle FOR dongusudur.
    if (match({TokenType::KW_VAR})) {
        // FOR DONGUSU (Init var)
        std::shared_ptr<Stmt> initializer = varDeclaration();
        
        std::shared_ptr<Expr> condition = nullptr;
        if (!check(TokenType::SEMICOLON)) {
            condition = expression();
        }
        consume(TokenType::SEMICOLON, "For dongusu kosulundan sonra ';' bekleniyor.");
        
        std::shared_ptr<Expr> increment = nullptr;
        if (!check(TokenType::RPAREN)) {
            increment = expression();
        }
        consume(TokenType::RPAREN, "For dongusu sonrasinda ')' bekleniyor.");
        
        consume(TokenType::LBRACE, "Dongu govdesi icin '{' bekleniyor.");
        std::shared_ptr<Stmt> body = std::make_shared<BlockStmt>(block());
        
        // ForStmt Kullan
        return std::make_shared<ForStmt>(loopKeyword, initializer, condition, increment, body);
    }
    
    // 'var' yoksa, ifade olabilir.
    // Eger ';' varsa FOR, yoksa WHILE (parantez kapandigi varsayimiyla)
    
    // Ancak burada expression() cagirdigimizda ';' yiyor mu? Hayir, expression statement yemez.
    // ExpressionExpression tarafindan yenilen ; expressionStmt icindedir.
    
    // Basit inisiaslizasyon icin expression statement parse edelim ama ';' match etmeden once duralim mi?
    // Zor. 
    // Basit Yontem: Once expression parse et. Sonraki token ';' ise FOR, ')' ise WHILE.
    
    std::shared_ptr<Expr> condOrInit = nullptr;
    if (!check(TokenType::RPAREN) && !check(TokenType::SEMICOLON)) {
        condOrInit = expression();
    }
    
    if (match({TokenType::SEMICOLON})) {
        // FOR DONGUSU (Expression Init)
        std::shared_ptr<Stmt> initializer = nullptr;
        if (condOrInit != nullptr) initializer = std::make_shared<ExpressionStmt>(condOrInit);
        
        std::shared_ptr<Expr> condition = nullptr;
        if (!check(TokenType::SEMICOLON)) {
            condition = expression();
        }
        consume(TokenType::SEMICOLON, "For dongusu kosulundan sonra ';' bekleniyor.");
        
        std::shared_ptr<Expr> increment = nullptr;
        if (!check(TokenType::RPAREN)) {
            increment = expression();
        }
        consume(TokenType::RPAREN, "For dongusu sonrasinda ')' bekleniyor.");
        
        consume(TokenType::LBRACE, "Dongu govdesi icin '{' bekleniyor.");
        std::shared_ptr<Stmt> body = std::make_shared<BlockStmt>(block());
        
        // ForStmt Kullan
        auto stmt = std::make_shared<ForStmt>(loopKeyword, initializer, condition, increment, body);
        stmt->line = loopKeyword.line;
        return stmt;
        
    } else {

        // WHILE DONGUSU
        if (parantezli) {
            consume(TokenType::RPAREN, "Kosuldan sonra ')' bekleniyor.");
        }
        
        consume(TokenType::LBRACE, "While govdesi icin '{' bekleniyor.");
        std::shared_ptr<Stmt> body = std::make_shared<BlockStmt>(block());
        
        if (condOrInit == nullptr) {
            // dongu() -> sonsuz dongu (while(true))
             auto stmt = std::make_shared<WhileStmt>(std::make_shared<LiteralExpr>(Token{TokenType::KW_DOGRU, "dogru", 0, 0}), body);
             stmt->line = loopKeyword.line;
             return stmt;
        }
        
        auto stmt = std::make_shared<WhileStmt>(condOrInit, body);
        stmt->line = loopKeyword.line;
        return stmt;
    }
}


std::shared_ptr<Stmt> Parser::tryCatchStatement() {
    consume(TokenType::LBRACE, "Try blogu icin '{' bekleniyor.");
    std::shared_ptr<Stmt> tryBlock = std::make_shared<BlockStmt>(block());
    
    consume(TokenType::KW_YAKALA, "'dene' sonrasinda 'yakala' bekleniyor.");
    consume(TokenType::LPAREN, "'yakala' sonrasinda '(' bekleniyor.");
    Token errorName = consume(TokenType::IDENTIFIER, "Hata degiskeni adi bekleniyor.");
    consume(TokenType::RPAREN, "Hata degiskeninden sonra ')' bekleniyor.");
    
    consume(TokenType::LBRACE, "Catch blogu icin '{' bekleniyor.");
    std::shared_ptr<Stmt> catchBlock = std::make_shared<BlockStmt>(block());
    auto stmt = std::make_shared<TryCatchStmt>(tryBlock, errorName, catchBlock);
    stmt->line = errorName.line;
    return stmt;
}


std::shared_ptr<Stmt> Parser::returnStatement() {
    Token keyword = previous();
    std::shared_ptr<Expr> value = nullptr;
    
    // Eger sonraki token ';' degilse ve ayni satirda ise, bir ifade donuyor demektir.
    if (!check(TokenType::SEMICOLON) && !check(TokenType::RBRACE) && peek().line == keyword.line) {
        value = expression();
    }
    consumeStatementEnd();
    auto stmt = std::make_shared<ReturnStmt>(keyword, value);
    stmt->line = keyword.line;
    return stmt;
}


std::shared_ptr<Stmt> Parser::printStatement() {
    bool parantezli = match({TokenType::LPAREN});
    std::shared_ptr<Expr> value = expression();
    
    if (parantezli) {
        consume(TokenType::RPAREN, "Ifadeden sonra ')' bekleniyor.");
    }
    
    consumeStatementEnd();
    auto stmt = std::make_shared<PrintStmt>(value);
    stmt->line = value->line;
    return stmt;
}


std::shared_ptr<Stmt> Parser::expressionStatement() {
    std::shared_ptr<Expr> expr = expression();
    consumeStatementEnd();
    auto stmt = std::make_shared<ExpressionStmt>(expr);
    stmt->line = expr->line;
    return stmt;
}



std::vector<std::shared_ptr<Stmt>> Parser::block() {
    std::vector<std::shared_ptr<Stmt>> statements;

    while (!check(TokenType::RBRACE) && !isAtEnd()) {
        // Yeni satirlari atla
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
    // 🚫 NOKTALΙ VΙRGÜL YASAK! Modern sözdizimi - noktalı virgül kullanma!
    if (check(TokenType::SEMICOLON)) {
        throw GumusException("syntax_error", peek().line, 
            "GümüşDil'de noktalı virgül kullanılmaz! Modern sözdizimi kullan.");
    }
    
    // Yeni satır varsa yut
    if (match({TokenType::NEW_LINE})) return;
    
    // Blok sonu, dosya sonu veya başka bir statement başlangıcı varsa sorun yok
    if (check(TokenType::RBRACE)) return;
    if (check(TokenType::END_OF_FILE)) return;
    if (isAtEnd()) return;
    
    // Bir sonraki token başka bir statement başlangıcı mı?
    if (check(TokenType::KW_VAR) || check(TokenType::KW_SINIF) || 
        check(TokenType::KW_FONKSIYON) || check(TokenType::KW_EGER) ||
        check(TokenType::KW_DONGU) || check(TokenType::KW_DON) ||
        check(TokenType::KW_YAZDIR) || check(TokenType::KW_DENEME) ||
        check(TokenType::KW_KIR) || check(TokenType::KW_DEVAM)) {
        return; // Yeni statement başlıyor, sorun yok
    }
    
    // Hiçbiri değilse de sorun yok - esnek sözdizimi
}

// Expression Parsing - Precedence Climbing
std::shared_ptr<Expr> Parser::expression() {
    return assignment();
}

std::shared_ptr<Expr> Parser::assignment() {
    std::shared_ptr<Expr> expr = logicOr();

    if (match({TokenType::EQUAL})) {
        Token equals = previous();
        std::shared_ptr<Expr> value = assignment();

        if (auto var = std::dynamic_pointer_cast<VariableExpr>(expr)) {
            return std::make_shared<AssignExpr>(var->name, value);
        } else if (auto prop = std::dynamic_pointer_cast<PropertyExpr>(expr)) {
             return std::make_shared<SetExpr>(prop->object, prop->name, value);
        } else if (auto get = std::dynamic_pointer_cast<GetExpr>(expr)) {
             return std::make_shared<IndexSetExpr>(get->object, get->bracket, get->index, value);
        }

        throw GumusException("parser_error", equals.line, "Gecersiz atama hedefi.");
    }

    return expr;
}
// ... (skipping unchanged methods)

std::shared_ptr<Expr> Parser::logicOr() {
    std::shared_ptr<Expr> expr = logicAnd();

    while (match({TokenType::LOGIC_OR})) {
        Token op = previous();
        std::shared_ptr<Expr> right = logicAnd();
        expr = std::make_shared<LogicalExpr>(expr, op, right);
    }

    return expr;
}

std::shared_ptr<Expr> Parser::logicAnd() {
    std::shared_ptr<Expr> expr = equality();

    while (match({TokenType::LOGIC_AND})) {
        Token op = previous();
        std::shared_ptr<Expr> right = equality();
        expr = std::make_shared<LogicalExpr>(expr, op, right);
    }

    return expr;
}

std::shared_ptr<Expr> Parser::equality() {
    std::shared_ptr<Expr> expr = comparison();

    while (match({TokenType::BANG_EQUAL, TokenType::EQUAL_EQUAL})) {
        Token op = previous();
        std::shared_ptr<Expr> right = comparison();
        expr = std::make_shared<BinaryExpr>(expr, op, right);
    }

    return expr;
}

std::shared_ptr<Expr> Parser::comparison() {
    std::shared_ptr<Expr> expr = term();

    while (match({TokenType::GREATER, TokenType::GREATER_EQUAL, TokenType::LESS, TokenType::LESS_EQUAL})) {
        Token op = previous();
        std::shared_ptr<Expr> right = term();
        expr = std::make_shared<BinaryExpr>(expr, op, right);
    }

    return expr;
}

std::shared_ptr<Expr> Parser::term() {
    std::shared_ptr<Expr> expr = factor();

    while (match({TokenType::MINUS, TokenType::PLUS})) {
        Token op = previous();
        std::shared_ptr<Expr> right = factor();
        expr = std::make_shared<BinaryExpr>(expr, op, right);
    }

    return expr;
}

std::shared_ptr<Expr> Parser::factor() {
    std::shared_ptr<Expr> expr = unary();

    while (match({TokenType::DIVIDE, TokenType::MULTIPLY, TokenType::MOD})) {
        Token op = previous();
        std::shared_ptr<Expr> right = unary();
        expr = std::make_shared<BinaryExpr>(expr, op, right);
    }

    return expr;
}

std::shared_ptr<Expr> Parser::unary() {
    if (match({TokenType::BANG, TokenType::MINUS})) {
        Token op = previous();
        std::shared_ptr<Expr> right = unary();
        return std::make_shared<UnaryExpr>(op, right);
    }

    // 'yeni' anahtar kelimesini yut ve bir sonraki ifadeyi (CallExpr olmali) dondur
    if (match({TokenType::KW_YENI})) {
        return unary(); 
    }

    return call();
}

std::shared_ptr<Expr> Parser::call() {
    std::shared_ptr<Expr> expr = primary();

    while (true) {
        if (match({TokenType::LPAREN})) {
            expr = finishCall(expr);
        } else if (match({TokenType::DOT})) {
            if (check(TokenType::IDENTIFIER) || (int)peek().type >= (int)TokenType::KW_VAR) {
                Token name = advance();
                expr = std::make_shared<PropertyExpr>(expr, name);
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

std::shared_ptr<Expr> Parser::finishCall(std::shared_ptr<Expr> callee) {
    std::vector<std::shared_ptr<Expr>> arguments;

    if (!check(TokenType::RPAREN)) {
        do {
            if (arguments.size() >= 255) {
                throw GumusException("parser_error", peek().line, "255'ten fazla arguman olamaz.");
            }
            arguments.push_back(expression());
        } while (match({TokenType::COMMA}));
    }

    Token paren = consume(TokenType::RPAREN, "Argumanlardan sonra ')' bekleniyor.");
    return std::make_shared<CallExpr>(callee, paren, arguments);
}

std::shared_ptr<Expr> Parser::finishIndex(std::shared_ptr<Expr> object, Token bracket) {
    std::shared_ptr<Expr> index = expression();
    consume(TokenType::RBRACKET, "Index'ten sonra ']' bekleniyor.");
    return std::make_shared<GetExpr>(object, bracket, index);
}

std::shared_ptr<Expr> Parser::primary() {
    if (match({TokenType::KW_DOGRU})) return std::make_shared<LiteralExpr>(previous());
    if (match({TokenType::KW_YANLIS})) return std::make_shared<LiteralExpr>(previous());
    if (match({TokenType::KW_BOS})) return std::make_shared<LiteralExpr>(previous());
    if (match({TokenType::INTEGER})) return std::make_shared<LiteralExpr>(previous());

    if (match({TokenType::STRING})) return std::make_shared<LiteralExpr>(previous());
    if (match({TokenType::IDENTIFIER})) {
        Token name = previous();
        if (match({TokenType::COLON_COLON})) {
            Token member = consume(TokenType::IDENTIFIER, "Modul uyesi bekleniyor.");
            return std::make_shared<ScopeResolutionExpr>(name, member);
        }
        return std::make_shared<VariableExpr>(name);
    }
    
    if (match({TokenType::KW_ATA})) {
        Token keyword = previous();
        consume(TokenType::DOT, "'ata' dan sonra '.' bekleniyor.");
        if (check(TokenType::IDENTIFIER) || (int)peek().type >= (int)TokenType::KW_VAR) {
            Token method = advance();
            return std::make_shared<SuperExpr>(keyword, method);
        }
        throw GumusException("parser_error", peek().line, "Metot adi bekleniyor.");
    }

    if (match({TokenType::KW_OZ})) {
        return std::make_shared<ThisExpr>(previous());
    }

    if (match({TokenType::LPAREN})) {
        std::shared_ptr<Expr> expr = expression();
        consume(TokenType::RPAREN, "Ifadeden sonra ')' bekleniyor.");
        return expr;
    }

    if (match({TokenType::LBRACKET})) {
        std::vector<std::shared_ptr<Expr>> elements;
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
        return std::make_shared<ListExpr>(elements);
    }

    if (match({TokenType::LBRACE})) {
        std::vector<std::shared_ptr<Expr>> keys;
        std::vector<std::shared_ptr<Expr>> values;
        skipNewLines();
        if (!check(TokenType::RBRACE)) {
            do {
                skipNewLines();
                // Key can be identifier, string, or any expression
                std::shared_ptr<Expr> keyExpr;
                if (check(TokenType::IDENTIFIER)) {
                    // Treat unquoted identifier as string key
                    keyExpr = std::make_shared<LiteralExpr>(advance());
                } else {
                    keyExpr = expression();
                }
                
                skipNewLines();
                consume(TokenType::COLON, "Sozluk anahtarindan sonra ':' bekleniyor.");
                skipNewLines();
                std::shared_ptr<Expr> valueExpr = expression();
                
                keys.push_back(keyExpr);
                values.push_back(valueExpr);

                skipNewLines();
                if (check(TokenType::RBRACE)) break; // Support trailing comma
            } while (match({TokenType::COMMA}));
        }
        skipNewLines();
        consume(TokenType::RBRACE, "Sozluk sonunda '}' bekleniyor.");
        return std::make_shared<MapExpr>(keys, values);
    }

    throw GumusException("parser_error", peek().line, "Ifade bekleniyor.");
}

// Helper Methods
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
