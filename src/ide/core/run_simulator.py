#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gümüşdil Simülatör - Enhanced Error Handling
Derleyici mevcut olmadığında Python tabanlı simülasyon
"""

import sys
import os
import json
import traceback
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class GumusSimulator:
    """Enhanced Gümüşdil simulator with better error handling"""
    
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.output_buffer = []
        self.error_buffer = []
        self.trace_mode = False
        self.memory_dump_mode = False
        
    def simulate_file(self, file_path):
        """Simulate execution of a Gümüşdil file"""
        try:
            if not os.path.exists(file_path):
                self.error_buffer.append(f"Dosya bulunamadı: {file_path}")
                return 1
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return self.simulate_code(content)
            
        except Exception as e:
            self.error_buffer.append(f"Dosya okuma hatası: {e}")
            return 1
    
    def simulate_code(self, code):
        """Simulate execution of Gümüşdil code"""
        try:
            lines = code.strip().split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                    
                if self.trace_mode:
                    print(f"__TRACE__:{line_num}")
                    
                try:
                    self.execute_line(line, line_num)
                except Exception as e:
                    self.error_buffer.append(f"Satır {line_num}: {e}")
                    return 1
                    
                if self.memory_dump_mode:
                    self.dump_memory(line_num)
            
            # Output results
            for output in self.output_buffer:
                print(output)
                
            # Output errors to stderr
            for error in self.error_buffer:
                print(error, file=sys.stderr)
                
            return 0 if not self.error_buffer else 1
            
        except Exception as e:
            print(f"Simülasyon hatası: {e}", file=sys.stderr)
            if "--debug" in sys.argv:
                traceback.print_exc()
            return 1
    
    def execute_line(self, line, line_num):
        """Execute a single line of code"""
        # Simple pattern matching for basic Gümüşdil constructs
        
        # Skip empty lines and comments
        if not line or line.startswith('//'):
            return
            
        # Variable declaration: değişken x = 5
        if line.startswith('değişken '):
            self.handle_variable_declaration(line)
            
        # Print statement: yazdır("Hello") or yazdır(variable)
        elif 'yazdır(' in line and ')' in line:
            self.handle_print_statement(line)
            
        # Function declaration: fonksiyon test() { ... }
        elif line.startswith('fonksiyon '):
            self.handle_function_declaration(line)
            
        # If statement: eğer (condition) { ... }
        elif line.startswith('eğer '):
            self.handle_if_statement(line)
            
        # Loop: döngü (condition) { ... }
        elif line.startswith('döngü '):
            self.handle_loop_statement(line)
            
        # Assignment: x = 10
        elif '=' in line and not line.startswith('değişken'):
            self.handle_assignment(line)
            
        # Function call
        elif '(' in line and ')' in line:
            self.handle_function_call(line)
            
        # Include/import statements
        elif 'dahil_et(' in line:
            self.handle_include_statement(line)
            
        # Return statement
        elif line.startswith('dön '):
            self.handle_return_statement(line)
            
        # Break/continue
        elif line.strip() in ['kır', 'devam']:
            self.output_buffer.append(f"// {line.strip()} statement")
            
        # Try-catch blocks
        elif line.startswith('dene ') or line.startswith('yakala '):
            self.handle_try_catch_statement(line)
            
        # Class definitions
        elif line.startswith('sınıf '):
            self.handle_class_statement(line)
            
        # Braces and block markers
        elif line.strip() in ['{', '}']:
            pass  # Ignore braces for now
            
        else:
            # Unknown statement - simulate as comment
            self.output_buffer.append(f"// Simulated: {line}")
    
    def handle_include_statement(self, line):
        """Handle include/import statements"""
        # Extract filename from dahil_et("filename")
        if 'dahil_et(' in line:
            start = line.find('"') + 1
            end = line.rfind('"')
            if start > 0 and end > start:
                filename = line[start:end]
                self.output_buffer.append(f"// Included: {filename}")
    
    def handle_return_statement(self, line):
        """Handle return statements"""
        # Extract return value
        return_value = line.replace('dön ', '').strip()
        if return_value:
            result = self.evaluate_expression(return_value)
            self.output_buffer.append(f"// Return: {result}")
    
    def handle_try_catch_statement(self, line):
        """Handle try-catch statements"""
        self.output_buffer.append(f"// Try-catch: {line}")
    
    def handle_class_statement(self, line):
        """Handle class definitions"""
        class_name = line.replace('sınıf ', '').split(' ')[0].strip()
        self.functions[class_name] = f"class_{class_name}"
        self.output_buffer.append(f"// Class defined: {class_name}")
    
    def handle_variable_declaration(self, line):
        """Handle variable declarations"""
        # Parse: değişken x = 5
        parts = line.replace('değişken ', '').split(' = ')
        if len(parts) == 2:
            var_name = parts[0].strip()
            var_value = self.evaluate_expression(parts[1].strip())
            self.variables[var_name] = var_value
        else:
            # Declaration without initialization
            var_name = line.replace('değişken ', '').strip()
            self.variables[var_name] = None
    
    def handle_print_statement(self, line):
        """Handle print statements"""
        # Find yazdır( and matching )
        start_idx = line.find('yazdır(')
        if start_idx == -1:
            return
            
        # Find the matching closing parenthesis
        paren_count = 0
        content_start = start_idx + 7  # Length of 'yazdır('
        content_end = -1
        
        for i in range(content_start, len(line)):
            if line[i] == '(':
                paren_count += 1
            elif line[i] == ')':
                if paren_count == 0:
                    content_end = i
                    break
                paren_count -= 1
        
        if content_end == -1:
            content_end = len(line) - 1
            
        content = line[content_start:content_end]
        
        # Evaluate the expression
        result = self.evaluate_expression(content)
        self.output_buffer.append(str(result))
    
    def handle_function_declaration(self, line):
        """Handle function declarations"""
        # Simple function storage
        func_name = line.split('(')[0].replace('fonksiyon ', '').strip()
        self.functions[func_name] = line
    
    def handle_if_statement(self, line):
        """Handle if statements"""
        # Simplified if handling
        self.output_buffer.append(f"// If statement: {line}")
    
    def handle_loop_statement(self, line):
        """Handle loop statements"""
        # Simplified loop handling
        self.output_buffer.append(f"// Loop statement: {line}")
    
    def handle_assignment(self, line):
        """Handle variable assignments"""
        parts = line.split(' = ')
        if len(parts) == 2:
            var_name = parts[0].strip()
            var_value = self.evaluate_expression(parts[1].strip())
            self.variables[var_name] = var_value
    
    def handle_function_call(self, line):
        """Handle function calls"""
        # Simplified function call handling
        self.output_buffer.append(f"// Function call: {line}")
    
    def evaluate_expression(self, expr):
        """Evaluate a simple expression"""
        expr = expr.strip()
        
        # Handle empty expressions
        if not expr:
            return ""
        
        # String literal
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]  # Remove quotes
        
        # Single quotes
        if expr.startswith("'") and expr.endswith("'"):
            return expr[1:-1]  # Remove quotes
        
        # Number literal
        try:
            if '.' in expr:
                return float(expr)
            else:
                return int(expr)
        except ValueError:
            pass
        
        # Boolean literals
        if expr in ['doğru', 'true']:
            return True
        elif expr in ['yanlış', 'false']:
            return False
        elif expr in ['boş', 'null', 'nil']:
            return None
        
        # Variable reference
        if expr in self.variables:
            return self.variables[expr]
        
        # String concatenation with +
        if '+' in expr and '"' in expr:
            parts = []
            current_part = ""
            in_string = False
            
            i = 0
            while i < len(expr):
                char = expr[i]
                if char == '"':
                    in_string = not in_string
                    current_part += char
                elif char == '+' and not in_string:
                    if current_part.strip():
                        parts.append(current_part.strip())
                    current_part = ""
                else:
                    current_part += char
                i += 1
            
            if current_part.strip():
                parts.append(current_part.strip())
            
            result = ""
            for part in parts:
                part_value = self.evaluate_expression(part)
                result += str(part_value)
            return result
        
        # Simple arithmetic
        if '+' in expr:
            parts = expr.split('+')
            if len(parts) == 2:
                try:
                    left = self.evaluate_expression(parts[0].strip())
                    right = self.evaluate_expression(parts[1].strip())
                    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                        return left + right
                    else:
                        return str(left) + str(right)
                except:
                    pass
        
        # Function calls
        if '(' in expr and ')' in expr:
            func_name = expr.split('(')[0].strip()
            if func_name in self.functions:
                return f"// Function call result: {func_name}"
            else:
                return f"// Unknown function: {func_name}"
        
        # Array/list access
        if '[' in expr and ']' in expr:
            return f"// Array access: {expr}"
        
        # Default: return as string or try to resolve as variable
        if expr.isidentifier():
            return self.variables.get(expr, f"// Undefined: {expr}")
        
        return expr
    
    def dump_memory(self, line_num):
        """Dump memory state for visualization"""
        memory_data = {
            "line": line_num,
            "variables": self.variables.copy(),
            "functions": list(self.functions.keys())
        }
        
        print("__MEMORY_JSON_START__")
        print(json.dumps(memory_data, ensure_ascii=False, indent=2))
        print("__MEMORY_JSON_END__")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Kullanım: python run_simulator.py <dosya.tr> [--trace] [--debug]", file=sys.stderr)
        return 1
    
    file_path = sys.argv[1]
    
    # Create simulator
    simulator = GumusSimulator()
    
    # Check for flags
    if "--trace" in sys.argv:
        simulator.trace_mode = True
        simulator.memory_dump_mode = True
    
    if "--debug" in sys.argv:
        print(f"[SIMULATOR] Debug mode enabled", file=sys.stderr)
        print(f"[SIMULATOR] Simulating file: {file_path}", file=sys.stderr)
    
    # Run simulation
    try:
        exit_code = simulator.simulate_file(file_path)
        
        if "--debug" in sys.argv:
            print(f"[SIMULATOR] Simulation completed with exit code: {exit_code}", file=sys.stderr)
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n[SIMULATOR] Simulation interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"[SIMULATOR] Fatal error: {e}", file=sys.stderr)
        if "--debug" in sys.argv:
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())