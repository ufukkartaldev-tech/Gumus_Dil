# -*- coding: utf-8 -*-
from .tokenizer import TokenType, Token
from .ast_nodes import *

class GumusParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        
    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return Program(statements)
        
    def declaration(self):
        try:
            if self.match(TokenType.VAR): return self.var_declaration()
            if self.match(TokenType.FUNCTION): return self.function_declaration()
            if self.match(TokenType.INCLUDE): return self.include_declaration()
            return self.statement()
        except Exception as e:
            self.synchronize()
            return None

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Değişken ismi bekleniyor.")
        initializer = None
        if self.match(TokenType.EQ):
            initializer = self.expression()
        return VarStmt(name, initializer)

    def include_declaration(self):
        module = self.consume(TokenType.IDENTIFIER, "Modül ismi bekleniyor.")
        return IncludeStmt(module.value)

    def function_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Fonksiyon ismi bekleniyor.")
        self.consume(TokenType.LPAREN, "Fonksiyon parametreleri için ( bekleniyor.")
        params = []
        if not self.check(TokenType.RPAREN):
            while True:
                params.append(self.consume(TokenType.IDENTIFIER, "Parametre ismi bekleniyor."))
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RPAREN, "Fonksiyon parametreleri sonrası ) bekleniyor.")
        self.consume(TokenType.LBRACE, "Fonksiyon gövdesi için { bekleniyor.")
        body = self.block()
        return FunctionStmt(name, params, body)

    def statement(self):
        if self.match(TokenType.IF): return self.if_statement()
        if self.match(TokenType.WHILE): return self.while_statement()
        if self.match(TokenType.TRY): return self.try_statement()
        if self.match(TokenType.BREAK): return BreakStmt()
        if self.match(TokenType.CONTINUE): return ContinueStmt()
        if self.match(TokenType.LBRACE): return BlockStmt(self.block().statements)
        if self.match(TokenType.PRINT): return self.print_statement()
        if self.match(TokenType.RETURN): return self.return_statement()
        return self.expression_statement()

    def if_statement(self):
        self.consume(TokenType.LPAREN, "Eğer koşulu için ( bekleniyor.")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Eğer koşulu sonrası ) bekleniyor.")
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return IfStmt(condition, then_branch, else_branch)

    def while_statement(self):
        self.consume(TokenType.LPAREN, "Döngü koşulu için ( bekleniyor.")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Döngü koşulu sonrası ) bekleniyor.")
        body = self.statement()
        return WhileStmt(condition, body)

    def try_statement(self):
        try_body = self.statement()
        self.consume(TokenType.CATCH, "Dene bloğu sonrası yakala bekleniyor.")
        catch_body = self.statement()
        return TryStmt(try_body, catch_body)

    def block(self):
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(TokenType.RBRACE, "Blok bitimi için } bekleniyor.")
        return BlockStmt(statements)

    def print_statement(self):
        self.consume(TokenType.LPAREN, "Yazdır için parantez aç.")
        expressions = []
        if not self.check(TokenType.RPAREN):
            while True:
                expressions.append(self.expression())
                if not self.match(TokenType.COMMA): break
        self.consume(TokenType.RPAREN, "Yazdır sonrası parantez kapat.")
        return PrintStmt(expressions)

    def return_statement(self):
        value = None
        if not self.check(TokenType.SEMICOLON) and not self.check(TokenType.RBRACE):
             value = self.expression()
        return ReturnStmt(value)

    def expression_statement(self):
        expr = self.expression()
        return ExprStmt(expr)

    def expression(self):
        return self.equality()

    def equality(self):
        expr = self.comparison()
        while self.match(TokenType.BANGEQ, TokenType.EQEQ):
            operator = self.previous(); right = self.comparison()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(TokenType.GT, TokenType.GTEQ, TokenType.LT, TokenType.LTEQ):
            operator = self.previous(); right = self.term()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous(); right = self.factor()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous(); right = self.unary()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous(); right = self.unary()
            return UnaryExpr(operator, right)
        return self.call()

    def call(self):
        expr = self.primary()
        while True:
            if self.match(TokenType.LPAREN): expr = self.finish_call(expr)
            else: break
        return expr

    def finish_call(self, callee):
        args = []
        if not self.check(TokenType.RPAREN):
            while True:
                args.append(self.expression())
                if not self.match(TokenType.COMMA): break
        self.consume(TokenType.RPAREN, "Fonksiyon çağrısı sonrası ) bekleniyor.")
        return CallExpr(callee, args)

    def primary(self):
        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.NULL): return Literal(None)
        if self.match(TokenType.NUMBER, TokenType.STRING): return Literal(self.previous().value)
        if self.match(TokenType.IDENTIFIER): return Variable(self.previous())
        if self.match(TokenType.LPAREN):
            expr = self.expression(); self.consume(TokenType.RPAREN, "Grup sonrası ) bekleniyor."); return expr
        raise Exception(f"Beklenmeyen token: {self.peek()}")

    def match(self, *types):
        for type in types:
            if self.check(type): self.advance(); return True
        return False
        
    def check(self, type):
        if self.is_at_end(): return False
        return self.peek().type == type
        
    def advance(self):
        if not self.is_at_end(): self.current += 1
        return self.previous()
        
    def is_at_end(self): return self.peek().type == TokenType.EOF
    def peek(self): return self.tokens[self.current]
    def previous(self): return self.tokens[self.current - 1]
    def consume(self, type, message):
        if self.check(type): return self.advance()
        raise Exception(f"{message} Bulunan: {self.peek()}")
        
    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON: return
            if self.peek().type in [TokenType.FUNCTION, TokenType.VAR, TokenType.IF,TokenType.WHILE, TokenType.PRINT, TokenType.RETURN]:
                return
            self.advance()
