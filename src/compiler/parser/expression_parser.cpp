#include "expression_parser.h"
#include "../json_hata.h"

namespace gumus {
namespace compiler {
namespace parser {

Expr* ExpressionParser::expression() {
    return assignment();
}

Expr* ExpressionParser::assignment() {
    Expr* expr = logicalOr();

    if (parser->match({TokenType::EQUAL, TokenType::PLUS_EQUAL, TokenType::MINUS_EQUAL, 
                      TokenType::STAR_EQUAL, TokenType::SLASH_EQUAL})) {
        Token equals = parser->previous();
        Expr* value = assignment();

        if (auto var = dynamic_cast<VariableExpr*>(expr)) {
            Token name = var->name;
            auto assignExpr = parser->arena.alloc<AssignExpr>(name, value);
            assignExpr->line = equals.line;
            assignExpr->operator_ = equals;
            return assignExpr;
        } else if (auto get = dynamic_cast<GetExpr*>(expr)) {
            auto setExpr = parser->arena.alloc<SetExpr>(get->object, get->name, value);
            setExpr->line = equals.line;
            setExpr->operator_ = equals;
            return setExpr;
        }

        throw GumusException("parser_error", equals.line, "Gecersiz atama hedefi.");
    }

    return expr;
}

Expr* ExpressionParser::logicalOr() {
    Expr* expr = logicalAnd();

    while (parser->match({TokenType::KW_VEYA})) {
        Token operator_ = parser->previous();
        Expr* right = logicalAnd();
        expr = parser->arena.alloc<LogicalExpr>(expr, operator_, right);
        expr->line = operator_.line;
    }

    return expr;
}

Expr* ExpressionParser::logicalAnd() {
    Expr* expr = equality();

    while (parser->match({TokenType::KW_VE})) {
        Token operator_ = parser->previous();
        Expr* right = equality();
        expr = parser->arena.alloc<LogicalExpr>(expr, operator_, right);
        expr->line = operator_.line;
    }

    return expr;
}

Expr* ExpressionParser::equality() {
    Expr* expr = comparison();

    while (parser->match({TokenType::BANG_EQUAL, TokenType::EQUAL_EQUAL})) {
        Token operator_ = parser->previous();
        Expr* right = comparison();
        expr = parser->arena.alloc<BinaryExpr>(expr, operator_, right);
        expr->line = operator_.line;
    }

    return expr;
}

Expr* ExpressionParser::comparison() {
    Expr* expr = term();

    while (parser->match({TokenType::GREATER, TokenType::GREATER_EQUAL, 
                         TokenType::LESS, TokenType::LESS_EQUAL})) {
        Token operator_ = parser->previous();
        Expr* right = term();
        expr = parser->arena.alloc<BinaryExpr>(expr, operator_, right);
        expr->line = operator_.line;
    }

    return expr;
}

Expr* ExpressionParser::term() {
    Expr* expr = factor();

    while (parser->match({TokenType::MINUS, TokenType::PLUS})) {
        Token operator_ = parser->previous();
        Expr* right = factor();
        expr = parser->arena.alloc<BinaryExpr>(expr, operator_, right);
        expr->line = operator_.line;
    }

    return expr;
}

Expr* ExpressionParser::factor() {
    Expr* expr = unary();

    while (parser->match({TokenType::SLASH, TokenType::STAR, TokenType::PERCENT})) {
        Token operator_ = parser->previous();
        Expr* right = unary();
        expr = parser->arena.alloc<BinaryExpr>(expr, operator_, right);
        expr->line = operator_.line;
    }

    return expr;
}

Expr* ExpressionParser::unary() {
    if (parser->match({TokenType::BANG, TokenType::MINUS, TokenType::PLUS})) {
        Token operator_ = parser->previous();
        Expr* right = unary();
        auto expr = parser->arena.alloc<UnaryExpr>(operator_, right);
        expr->line = operator_.line;
        return expr;
    }

    return call();
}

Expr* ExpressionParser::call() {
    Expr* expr = primary();

    while (true) {
        if (parser->match({TokenType::LPAREN})) {
            expr = finishCall(expr);
        } else if (parser->match({TokenType::DOT})) {
            expr = finishProperty(expr);
        } else if (parser->match({TokenType::LBRACKET})) {
            Expr* index = expression();
            parser->consume(TokenType::RBRACKET, "Dizin erisiminden sonra ']' bekleniyor.");
            auto getExpr = parser->arena.alloc<IndexExpr>(expr, index);
            getExpr->line = parser->previous().line;
            expr = getExpr;
        } else {
            break;
        }
    }

    return expr;
}

Expr* ExpressionParser::primary() {
    if (parser->match({TokenType::KW_DOGRU})) {
        auto expr = parser->arena.alloc<LiteralExpr>(true);
        expr->line = parser->previous().line;
        return expr;
    }

    if (parser->match({TokenType::KW_YANLIS})) {
        auto expr = parser->arena.alloc<LiteralExpr>(false);
        expr->line = parser->previous().line;
        return expr;
    }

    if (parser->match({TokenType::KW_BOS})) {
        auto expr = parser->arena.alloc<LiteralExpr>(nullptr);
        expr->line = parser->previous().line;
        return expr;
    }

    if (parser->match({TokenType::NUMBER})) {
        auto expr = parser->arena.alloc<LiteralExpr>(parser->previous().literal);
        expr->line = parser->previous().line;
        return expr;
    }

    if (parser->match({TokenType::STRING})) {
        auto expr = parser->arena.alloc<LiteralExpr>(parser->previous().literal);
        expr->line = parser->previous().line;
        return expr;
    }

    if (parser->match({TokenType::KW_BU})) {
        auto expr = parser->arena.alloc<ThisExpr>(parser->previous());
        expr->line = parser->previous().line;
        return expr;
    }

    if (parser->match({TokenType::KW_UST})) {
        Token keyword = parser->previous();
        parser->consume(TokenType::DOT, "'ust' anahtar kelimesinden sonra '.' bekleniyor.");
        Token method = parser->consume(TokenType::IDENTIFIER, "Ust sinif metot adi bekleniyor.");
        auto expr = parser->arena.alloc<SuperExpr>(keyword, method);
        expr->line = keyword.line;
        return expr;
    }

    if (parser->match({TokenType::IDENTIFIER})) {
        auto expr = parser->arena.alloc<VariableExpr>(parser->previous());
        expr->line = parser->previous().line;
        return expr;
    }

    if (parser->match({TokenType::LPAREN})) {
        Expr* expr = expression();
        parser->consume(TokenType::RPAREN, "Ifadeden sonra ')' bekleniyor.");
        auto groupExpr = parser->arena.alloc<GroupingExpr>(expr);
        groupExpr->line = parser->previous().line;
        return groupExpr;
    }

    if (parser->match({TokenType::LBRACKET})) {
        return arrayLiteral();
    }

    if (parser->match({TokenType::LBRACE})) {
        return objectLiteral();
    }

    if (parser->check(TokenType::KW_LAMBDA) || 
        (parser->check(TokenType::LPAREN) && parser->checkNext(TokenType::IDENTIFIER))) {
        return lambdaExpression();
    }

    throw GumusException("parser_error", parser->peek().line, "Ifade bekleniyor.");
}

Expr* ExpressionParser::finishCall(Expr* callee) {
    std::vector<Expr*> arguments;
    if (!parser->check(TokenType::RPAREN)) {
        do {
            if (arguments.size() >= 255) {
                throw GumusException("parser_error", parser->peek().line, 
                                   "Fonksiyon en fazla 255 arguman alabilir.");
            }
            arguments.push_back(expression());
        } while (parser->match({TokenType::COMMA}));
    }

    Token paren = parser->consume(TokenType::RPAREN, "Argumanlardan sonra ')' bekleniyor.");
    auto expr = parser->arena.alloc<CallExpr>(callee, paren, std::move(arguments));
    expr->line = paren.line;
    return expr;
}

Expr* ExpressionParser::finishProperty(Expr* object) {
    Token name = parser->consume(TokenType::IDENTIFIER, "Ozellik adi bekleniyor.");
    auto expr = parser->arena.alloc<GetExpr>(object, name);
    expr->line = name.line;
    return expr;
}

Expr* ExpressionParser::arrayLiteral() {
    std::vector<Expr*> elements;
    
    if (!parser->check(TokenType::RBRACKET)) {
        do {
            elements.push_back(expression());
        } while (parser->match({TokenType::COMMA}));
    }
    
    parser->consume(TokenType::RBRACKET, "Dizi literalinden sonra ']' bekleniyor.");
    auto expr = parser->arena.alloc<ArrayExpr>(std::move(elements));
    expr->line = parser->previous().line;
    return expr;
}

Expr* ExpressionParser::objectLiteral() {
    std::vector<std::pair<Token, Expr*>> properties;
    
    if (!parser->check(TokenType::RBRACE)) {
        do {
            Token key;
            if (parser->match({TokenType::IDENTIFIER})) {
                key = parser->previous();
            } else if (parser->match({TokenType::STRING})) {
                key = parser->previous();
            } else {
                throw GumusException("parser_error", parser->peek().line, 
                                   "Nesne ozellik adi bekleniyor.");
            }
            
            parser->consume(TokenType::COLON, "Ozellik adından sonra ':' bekleniyor.");
            Expr* value = expression();
            properties.emplace_back(key, value);
        } while (parser->match({TokenType::COMMA}));
    }
    
    parser->consume(TokenType::RBRACE, "Nesne literalinden sonra '}' bekleniyor.");
    auto expr = parser->arena.alloc<ObjectExpr>(std::move(properties));
    expr->line = parser->previous().line;
    return expr;
}

Expr* ExpressionParser::lambdaExpression() {
    std::vector<Token> parameters;
    
    if (parser->match({TokenType::KW_LAMBDA})) {
        // lambda x, y => x + y
        if (!parser->check(TokenType::ARROW)) {
            do {
                parameters.push_back(parser->consume(TokenType::IDENTIFIER, "Lambda parametre adi bekleniyor."));
            } while (parser->match({TokenType::COMMA}));
        }
        parser->consume(TokenType::ARROW, "Lambda parametrelerinden sonra '=>' bekleniyor.");
    } else {
        // (x, y) => x + y
        parser->consume(TokenType::LPAREN, "Lambda parametreleri icin '(' bekleniyor.");
        if (!parser->check(TokenType::RPAREN)) {
            do {
                parameters.push_back(parser->consume(TokenType::IDENTIFIER, "Lambda parametre adi bekleniyor."));
            } while (parser->match({TokenType::COMMA}));
        }
        parser->consume(TokenType::RPAREN, "Lambda parametrelerinden sonra ')' bekleniyor.");
        parser->consume(TokenType::ARROW, "Lambda parametrelerinden sonra '=>' bekleniyor.");
    }
    
    Expr* body = expression();
    auto expr = parser->arena.alloc<LambdaExpr>(std::move(parameters), body);
    expr->line = parser->previous().line;
    return expr;
}

bool ExpressionParser::isAssignmentTarget(Expr* expr) {
    return dynamic_cast<VariableExpr*>(expr) != nullptr || 
           dynamic_cast<GetExpr*>(expr) != nullptr ||
           dynamic_cast<IndexExpr*>(expr) != nullptr;
}

TokenType ExpressionParser::getAssignmentOperator() {
    if (parser->check(TokenType::EQUAL)) return TokenType::EQUAL;
    if (parser->check(TokenType::PLUS_EQUAL)) return TokenType::PLUS_EQUAL;
    if (parser->check(TokenType::MINUS_EQUAL)) return TokenType::MINUS_EQUAL;
    if (parser->check(TokenType::STAR_EQUAL)) return TokenType::STAR_EQUAL;
    if (parser->check(TokenType::SLASH_EQUAL)) return TokenType::SLASH_EQUAL;
    return TokenType::EOF_TOKEN;
}

} // namespace parser
} // namespace compiler  
} // namespace gumus