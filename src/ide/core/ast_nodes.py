# -*- coding: utf-8 -*-

class ASTNode:
    def to_json(self):
        raise NotImplementedError

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    
    def to_json(self):
        return [s.to_json() for s in self.statements]

class VarStmt(ASTNode):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer
        
    def to_json(self):
        children = [self.initializer.to_json()] if self.initializer else []
        return { "type": "VarStmt", "value": self.name.value, "children": children }

class FunctionStmt(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params # List of Token
        self.body = body # BlockStmt
        
    def to_json(self):
        param_names = [p.value for p in self.params]
        body_json = self.body.to_json()
        return {
            "type": "FunctionStmt",
            "value": self.name.value,
            "params": param_names,
            "children": [body_json]
        }

class BlockStmt(ASTNode):
    def __init__(self, statements):
        self.statements = statements
        
    def to_json(self):
        children = [s.to_json() for s in self.statements]
        return { "type": "BlockStmt", "children": children }

class IfStmt(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
        
    def to_json(self):
        children = [self.condition.to_json(), self.then_branch.to_json()]
        if self.else_branch:
            children.append(self.else_branch.to_json())
        return { "type": "IfStmt", "children": children }

class WhileStmt(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
        
    def to_json(self):
        return { "type": "WhileStmt", "children": [self.condition.to_json(), self.body.to_json()] }

class PrintStmt(ASTNode):
    def __init__(self, expressions):
        self.expressions = expressions
        
    def to_json(self):
        return { "type": "PrintStmt", "children": [e.to_json() for e in self.expressions] }

class ReturnStmt(ASTNode):
    def __init__(self, value):
        self.value = value
        
    def to_json(self):
        children = [self.value.to_json()] if self.value else []
        return { "type": "ReturnStmt", "children": children }

class ExprStmt(ASTNode):
    def __init__(self, expression):
        self.expression = expression
        
    def to_json(self):
        return { "type": "ExprStmt", "children": [self.expression.to_json()] }

class BreakStmt(ASTNode):
    def to_json(self): return { "type": "BreakStmt" }

class ContinueStmt(ASTNode):
    def to_json(self): return { "type": "ContinueStmt" }

class IncludeStmt(ASTNode):
    def __init__(self, module):
        self.module = module
    def to_json(self): return { "type": "IncludeStmt", "value": self.module }

class TryStmt(ASTNode):
    def __init__(self, try_block, catch_body):
        self.try_block = try_block
        self.catch_body = catch_body
    def to_json(self):
        return { "type": "TryStmt", "children": [self.try_block.to_json(), self.catch_body.to_json()] }

class UnaryExpr(ASTNode):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right
        
    def to_json(self):
        return { "type": "UnaryExpr", "value": self.operator.value, "children": [self.right.to_json()] }

class BinaryExpr(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
        
    def to_json(self):
        return { "type": "BinaryExpr", "value": self.operator.value, "children": [self.left.to_json(), self.right.to_json()] }

class Literal(ASTNode):
    def __init__(self, value):
        self.value = value
        
    def to_json(self):
        return { "type": "Literal", "value": str(self.value) }

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name
        
    def to_json(self):
        return { "type": "Variable", "value": self.name.value }

class CallExpr(ASTNode):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args
        
    def to_json(self):
        children = [self.callee.to_json()] + [arg.to_json() for arg in self.args]
        return { "type": "CallExpr", "children": children }
