# -*- coding: utf-8 -*-
from .tokenizer import TokenizerRunner, TokenType
from .parser import GumusParser, Program, VarStmt, FunctionStmt, BlockStmt, IfStmt, WhileStmt, PrintStmt, ReturnStmt, ExprStmt, BinaryExpr, UnaryExpr, Literal, Variable, CallExpr, IncludeStmt, BreakStmt, ContinueStmt, TryStmt
from .library_bridge import LibraryBridge

class GumusToCppTranspiler:
    """GümüşDil kodunu C++'a çevirir."""
    
    def __init__(self):
        self.indent_level = 0
        self.output_lines = []
        self.includes = {"iostream", "string"}
        
        # Native Mapping (GümüşDil -> C++)
        self.builtins = {
            "yazdır": "std::cout <<",
            "uzunluk": ".size()",
            "metin": "std::to_string",
            "sayı": "std::stoi",
            "dosya_oku": "/* logic handled in visit_CallExpr */",
            "dosya_yaz": "/* logic handled in visit_CallExpr */",
            "ekle": ".push_back",
            "rastgele_sayı": "rand_between", 
            "rastgele_ondalık": "/* logic handled in visit_CallExpr */",
            "bekle": "this_thread::sleep_for",
            "temizle": "system",
        }

    def transpile(self, source_code):
        self.output_lines = []
        self.indent_level = 0
        self.includes = {"iostream", "string"}
        
        try:
            # 1. Tokenize
            tokens = TokenizerRunner.get_tokens(source_code)
            
            # 2. Parse
            parser = GumusParser(tokens)
            ast = parser.parse()
            
            if not ast or not hasattr(ast, 'statements') or not ast.statements:
                return "// Boş program veya parse hatası."
                
            # 3. Visit AST (Collect and Generate)
            temp_lines = []
            self.current_output = temp_lines
            
            for stmt in ast.statements:
                self.visit_stmt(stmt)
            
            # 4. Final Assembler
            header = []
            for inc in sorted(list(self.includes)):
                header.append(f"#include <{inc}>")
            
            header.append("using namespace std;")
            header.append("")
            
            # main fonksiyonu içine alalım eğer dosya bazlıysa
            # Ancak GümüşDil genelde script gibi çalıştığı için her şeyi main içine koymak güvenli bir yaklaşımdır.
            final_code = []
            final_code.extend(header)
            final_code.append("int main() {")
            
            for line in self.output_lines:
                final_code.append("    " + line)
                
            final_code.append("    return 0;")
            final_code.append("}")
            
            return "\n".join(final_code)
            
        except Exception as e:
            import traceback
            return f"// HATA: C++ Transpilation başarısız oldu.\n// Sebep: {str(e)}\n\n/*\n{traceback.format_exc()}\n*/"

    def emit(self, text):
        indent = "    " * self.indent_level
        self.output_lines.append(f"{indent}{text}")

    # --- Statement Visitors ---

    def visit_stmt(self, node):
        if isinstance(node, VarStmt): self.visit_VarStmt(node)
        elif isinstance(node, FunctionStmt): self.visit_FunctionStmt(node)
        elif isinstance(node, BlockStmt): self.visit_BlockStmt(node)
        elif isinstance(node, IfStmt): self.visit_IfStmt(node)
        elif isinstance(node, WhileStmt): self.visit_WhileStmt(node)
        elif isinstance(node, PrintStmt): self.visit_PrintStmt(node)
        elif isinstance(node, ReturnStmt): self.visit_ReturnStmt(node)
        elif isinstance(node, IncludeStmt): self.visit_IncludeStmt(node)
        elif isinstance(node, BreakStmt): self.visit_BreakStmt(node)
        elif isinstance(node, ContinueStmt): self.visit_ContinueStmt(node)
        elif isinstance(node, TryStmt): self.visit_TryStmt(node)
        elif isinstance(node, ExprStmt): self.visit_ExprStmt(node)
        else:
            self.emit(f"// Unknown Statement: {type(node).__name__}")

    def visit_VarStmt(self, node):
        name = node.name.value
        init = "nullptr"
        if node.initializer:
            init = self.visit_expr(node.initializer)
        # C++'da auto ile tip çıkarımı yapabiliriz
        self.emit(f"auto {name} = {init};")

    def visit_FunctionStmt(self, node):
        # C++'da fonksiyonlar main dışında olmalı ancak bu basit transpiler main içine script gibi yazar.
        # Daha karmaşık bir yapı için fonksiyonları ayırmak gerekir.
        name = node.name.value
        params = ", ".join([f"auto {p.value}" for p in node.params])
        
        # C++ fonksiyon tanımı (Lambda formatında main içine gömebiliriz)
        self.emit(f"auto {name} = []({params}) {{")
        self.indent_level += 1
        self.visit_BlockStmt(node.body)
        self.indent_level -= 1
        self.emit("};")

    def visit_BlockStmt(self, node):
        for stmt in node.statements:
            self.visit_stmt(stmt)

    def visit_IfStmt(self, node):
        cond = self.visit_expr(node.condition)
        self.emit(f"if ({cond}) {{")
        self.indent_level += 1
        self.visit_stmt(node.then_branch)
        self.indent_level -= 1
        self.emit("}")
        
        if node.else_branch:
            self.emit("else {")
            self.indent_level += 1
            self.visit_stmt(node.else_branch)
            self.indent_level -= 1
            self.emit("}")

    def visit_WhileStmt(self, node):
        cond = self.visit_expr(node.condition)
        self.emit(f"while ({cond}) {{")
        self.indent_level += 1
        self.visit_stmt(node.body)
        self.indent_level -= 1
        self.emit("}")

    def visit_PrintStmt(self, node):
        val = self.visit_expr(node.expression)
        # std::endl ile yeni satır
        self.emit(f"std::cout << {val} << std::endl;")

    def visit_ReturnStmt(self, node):
        if node.value:
            val = self.visit_expr(node.value)
            self.emit(f"return {val};")
        else:
            self.emit("return;")

    def visit_ExprStmt(self, node):
        val = self.visit_expr(node.expression)
        self.emit(f"{val};")

    def visit_IncludeStmt(self, node):
        module = LibraryBridge.get_cpp_include(node.module)
        if "." not in module:
            self.includes.add(module)
        else:
            self.emit(f'#include "{module}"')

    def visit_BreakStmt(self, node):
        self.emit("break;")

    def visit_ContinueStmt(self, node):
        self.emit("continue;")

    def visit_TryStmt(self, node):
        self.emit("try {")
        self.indent_level += 1
        self.visit_stmt(node.try_block)
        self.indent_level -= 1
        self.emit("} catch (...) {")
        self.indent_level += 1
        self.visit_stmt(node.catch_body)
        self.indent_level -= 1
        self.emit("}")

    # --- Expression Visitors ---

    def visit_expr(self, node):
        if isinstance(node, BinaryExpr): return self.visit_BinaryExpr(node)
        elif isinstance(node, UnaryExpr): return self.visit_UnaryExpr(node)
        elif isinstance(node, Literal): return self.visit_Literal(node)
        elif isinstance(node, Variable): return self.visit_Variable(node)
        elif isinstance(node, CallExpr): return self.visit_CallExpr(node)
        else:
            return f"/* Unknown Expr: {type(node).__name__} */"

    def visit_BinaryExpr(self, node):
        left = self.visit_expr(node.left)
        right = self.visit_expr(node.right)
        op = node.operator.value
        
        op_map = {
            "ve": "&&", "veya": "||",
        }
        final_op = op_map.get(op, op)
        return f"({left} {final_op} {right})"

    def visit_UnaryExpr(self, node):
        op = node.operator.value
        right = self.visit_expr(node.right)
        if op == "değil": return f"!({right})"
        return f"{op}{right}"

    def visit_Literal(self, node):
        val = node.value
        if val is True: return "true"
        if val is False: return "false"
        if val is None: return "nullptr"
        if isinstance(val, str): return f'"{val}"'
        return str(val)

    def visit_Variable(self, node):
        return node.name.value

    def visit_CallExpr(self, node):
        callee_name = self.visit_expr(node.callee)
        args_str = [self.visit_expr(arg) for arg in node.args]
        
        if callee_name == "uzunluk" and len(args_str) == 1:
            return f"{args_str[0]}.size()"
        
        if callee_name == "dosya_yaz":
            self.includes.add("fstream")
            return f"std::ofstream({args_str[0]}) << {args_str[1]}"

        if callee_name == "bekle":
            self.includes.add("thread")
            self.includes.add("chrono")
            return f"std::this_thread::sleep_for(std::chrono::milliseconds({args_str[0]}))"

        # Gümüş-Vizyon (Graphics) support
        if callee_name == "daire_çiz":
            return f'std::cout << "__CANVAS__:daire " << {args_str[0]} << " " << {args_str[1]} << " " << {args_str[2]} << " " << {args_str[3]} << std::endl'
        if callee_name == "dikdörtgen_çiz":
            return f'std::cout << "__CANVAS__:dikdortgen " << {args_str[0]} << " " << {args_str[1]} << " " << {args_str[2]} << " " << {args_str[3]} << " " << {args_str[4]} << std::endl'
        if callee_name == "çizgi_çiz":
            return f'std::cout << "__CANVAS__:cizgi " << {args_str[0]} << " " << {args_str[1]} << " " << {args_str[2]} << " " << {args_str[3]} << " " << {args_str[4]} << " " << {args_str[5]} << std::endl'
        if callee_name == "tuval_temizle":
            return 'std::cout << "__CANVAS__:temizle" << std::endl'

        if callee_name == "rastgele_ondalık" and len(args_str) == 2:
            a, b = args_str[0], args_str[1]
            # C++ Robust float random: min + (max-min) * (rand/RAND_MAX)
            return f"(std::min({a}, {b}) + (float)rand()/((float)RAND_MAX/(std::max({a}, {b}) - std::min({a}, {b}))))"
            
        if callee_name == "rastgele_sayı" and len(args_str) == 2:
            a, b = args_str[0], args_str[1]
            # Robust integer random: min + rand % (max - min + 1)
            return f"(std::min({a}, {b}) + rand() % ((int)std::max({a}, {b}) - (int)std::min({a}, {b}) + 1))"

        if callee_name in self.builtins:
            callee_name = self.builtins[callee_name]
            
        return f"{callee_name}({', '.join(args_str)})"

