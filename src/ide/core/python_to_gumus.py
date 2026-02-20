# -*- coding: utf-8 -*-
import ast

class PythonToGumusTranspiler:
    """Python kodunu GümüşDil'e çevirir."""

    def __init__(self):
        self.indent_level = 0
        self.output = []

    def transpile(self, python_code):
        self.output = []
        self.indent_level = 0
        try:
            tree = ast.parse(python_code)
            for stmt in tree.body:
                res = self.visit(stmt)
                if res:
                    self.emit(res)
            return "\n".join(self.output)
        except Exception as e:
            return f"// HATA: Python kodu GümüşDil'e çevrilemedi.\n// {str(e)}"

    def emit(self, text):
        indent = "    " * self.indent_level
        # Handle multiline results from visit
        lines = text.split('\n')
        for line in lines:
            if line.strip() == "" and len(lines) > 1: continue # Skip empty lines in block
            self.output.append(f"{( '    ' * self.indent_level) if line.strip() else ''}{line}")

    def visit(self, node):
        if isinstance(node, ast.Assign):
            target = self.visit(node.targets[0])
            value = self.visit(node.value)
            # Eğer değişken daha önce tanımlanmadıysa 'değişken' kelimesi eklemek GümüşDil için iyidir
            # Ama basitleştirmek için hep ekleyebiliriz veya akıllıca davranabiliriz.
            # GümüşDil'de 'değişken x = 5' formatı esastır.
            return f"değişken {target} = {value}"
        
        elif isinstance(node, ast.AnnAssign):
             target = self.visit(node.target)
             value = self.visit(node.value) if node.value else "yok"
             return f"değişken {target} = {value}"

        elif isinstance(node, ast.Name):
            return node.id
        
        elif isinstance(node, ast.Constant):
            val = node.value
            if val is True: return "doğru"
            if val is False: return "yanlış"
            if val is None: return "yok"
            if isinstance(val, str): return f'"{val}"'
            return str(val)

        elif isinstance(node, ast.BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            op = self.visit_op(node.op)
            return f"{left} {op} {right}"

        elif isinstance(node, ast.UnaryOp):
            op = self.visit_op(node.op)
            operand = self.visit(node.operand)
            if op == "değil": return f"değil {operand}"
            return f"{op}{operand}"

        elif isinstance(node, ast.Compare):
            left = self.visit(node.left)
            ops = [self.visit_op(op) for op in node.ops]
            comparators = [self.visit(c) for c in node.comparators]
            # Basitlik için sadece ilk karşılaştırmayı alalım
            return f"({left} {ops[0]} {comparators[0]})"

        elif isinstance(node, ast.Call):
            func_name = self.visit(node.func)
            # Built-in Mapping
            builtin_map = {
                "print": "yazdır",
                "len": "uzunluk",
                "str": "metin",
                "int": "sayı",
                "input": "girdi",
                "exit": "çık",
                "range": "aralık",
                "math.sqrt": "karekök"
            }
            func_name = builtin_map.get(func_name, func_name)
            args = ", ".join(self.visit(arg) for arg in node.args)
            return f"{func_name}({args})"

        elif isinstance(node, ast.FunctionDef):
            params = ", ".join(arg.arg for arg in node.args.args)
            old_indent = self.indent_level
            inner_statements = []
            
            # GümüşDil'de bloklar { } ile ayrılır. 
            # emit yerine string dönüp birleştirirsek daha kolay olur.
            res = f"fonksiyon {node.name}({params}) {{\n"
            self.indent_level += 1
            for stmt in node.body:
                stmt_res = self.visit(stmt)
                if stmt_res:
                    res += ("    " * self.indent_level) + stmt_res + "\n"
            self.indent_level -= 1
            res += ("    " * self.indent_level) + "}"
            return res

        elif isinstance(node, ast.Return):
            val = self.visit(node.value) if node.value else ""
            return f"dön {val}"

        elif isinstance(node, ast.If):
            cond = self.visit(node.test)
            res = f"eğer ({cond}) {{\n"
            self.indent_level += 1
            for stmt in node.body:
                res += ("    " * self.indent_level) + self.visit(stmt) + "\n"
            self.indent_level -= 1
            res += ("    " * self.indent_level) + "}"
            
            if node.orelse:
                if isinstance(node.orelse[0], ast.If):
                    # else if (değilse eğer)
                    res += " değilse " + self.visit(node.orelse[0])
                else:
                    res += " değilse {\n"
                    self.indent_level += 1
                    for stmt in node.orelse:
                        res += ("    " * self.indent_level) + self.visit(stmt) + "\n"
                    self.indent_level -= 1
                    res += ("    " * self.indent_level) + "}"
            return res

        elif isinstance(node, ast.While):
            cond = self.visit(node.test)
            res = f"döngü ({cond}) {{\n"
            self.indent_level += 1
            for stmt in node.body:
                res += ("    " * self.indent_level) + self.visit(stmt) + "\n"
            self.indent_level -= 1
            res += ("    " * self.indent_level) + "}"
            return res

        elif isinstance(node, ast.For):
            # for i in range(5) -> döngü değişken i = aralık(5)
            target = self.visit(node.target)
            iter_val = self.visit(node.iter)
            res = f"döngü (değişken {target} = {iter_val}) {{\n"
            self.indent_level += 1
            for stmt in node.body:
                 res += ("    " * self.indent_level) + self.visit(stmt) + "\n"
            self.indent_level -= 1
            res += ("    " * self.indent_level) + "}"
            return res

        elif isinstance(node, ast.Expr):
            return self.visit(node.value)

        elif isinstance(node, ast.Try):
            res = "dene {\n"
            self.indent_level += 1
            for stmt in node.body:
                 res += ("    " * self.indent_level) + self.visit(stmt) + "\n"
            self.indent_level -= 1
            res += ("    " * self.indent_level) + "} yakala {\n"
            self.indent_level += 1
            for handler in node.handlers:
                 for stmt in handler.body:
                      res += ("    " * self.indent_level) + self.visit(stmt) + "\n"
            self.indent_level -= 1
            res += ("    " * self.indent_level) + "}"
            return res

        elif isinstance(node, ast.Pass):
            return "boş geç"

        elif isinstance(node, ast.Break):
            return "kır"

        elif isinstance(node, ast.Continue):
            return "devam et"

        elif isinstance(node, ast.Attribute):
             value = self.visit(node.value)
             return f"{value}.{node.attr}"

        elif isinstance(node, ast.Import):
            # import math -> dahil et math
            names = [alias.name for alias in node.names]
            return f"dahil et {', '.join(names)}"

        elif isinstance(node, ast.ImportFrom):
            # from math import sqrt -> dahil et math
            return f"dahil et {node.module}"

        return f"// Python yapısı henüz Gümüş'e tercüme edilemedi: {type(node).__name__}"

    def visit_op(self, op):
        mapping = {
            ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
            ast.Eq: "==", ast.NotEq: "!=", ast.Gt: ">", ast.Lt: "<",
            ast.GtE: ">=", ast.LtE: "<=", ast.And: "ve", ast.Or: "veya",
            ast.Not: "değil"
        }
        return mapping.get(type(op), "?")

