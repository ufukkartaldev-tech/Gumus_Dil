import sys
import os
from pathlib import Path
import json

# Add src to python path to allow imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "src"))

try:
    from ide.core.compiler import CompilerRunner
    from config import COMPILER_PATH
    
    print(f"Compiler Path: {COMPILER_PATH}")
    print(f"Compiler exists: {COMPILER_PATH.exists()}")
    
    source_file = current_dir / "test_transpiler.tr"
    print(f"Source file: {source_file}")
    
    stdout, stderr, code = CompilerRunner.get_ast_json(source_file)
    
    print(f"Exit Code: {code}")
    if stderr:
        print(f"Stderr: {stderr}")
        
    if stdout:
        print("-" * 20)
        print("AST Output:")
        print(stdout)
        print("-" * 20)
        
        # Try to parse valid JSON if possible
        try:
            ast_data = json.loads(stdout)
            print("Successfully parsed JSON.")
            # Save nicely formatted JSON for inspection
            with open("test_ast.json", "w", encoding="utf-8") as f:
                json.dump(ast_data, f, indent=4, ensure_ascii=False)
            print("Saved nicely formatted AST to test_ast.json")
        except json.JSONDecodeError:
            print("Output was not valid JSON.")
            
except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()

