import sys
import os
import subprocess
from pathlib import Path
import json

# Try to import CompilerRunner
try:
    from src.ide.core.compiler import CompilerRunner
    from src.ide.config import COMPILER_PATH
except ImportError:
    print("Import failed. Make sure to run as module: py -m src.check_ast")
    sys.exit(1)

def main():
    print(f"Compiler Path: {COMPILER_PATH}")
    print(f"Exists: {COMPILER_PATH.exists()}")
    
    # Debug: Check if compiler runs
    try:
        print("Running compiler --help directly...")
        res = subprocess.run(
            [str(COMPILER_PATH), "--help"], 
            capture_output=True, 
            text=True,
            timeout=5
        )
        print(f"Return Code: {res.returncode}")
        print(f"STDOUT: {res.stdout[:200]}...") # First 200 chars
        print(f"STDERR: {res.stderr[:200]}...")
    except Exception as e:
        print(f"Subprocess Error: {e}")

    root_dir = Path(os.getcwd())
    source_file = root_dir / "test_transpiler.tr"
    
    print(f"Checking AST for: {source_file}")
    
    stdout, stderr, code = CompilerRunner.get_ast_json(source_file)
    
    if code != 0:
        print(f"Error Code: {code}")
        print(f"Stderr: {stderr}")
    else:
        print("STDOUT:")
        print(stdout)
        try:
            ast = json.loads(stdout)
            print("Success! JSON parsed.")
            with open("ast_output.json", "w", encoding="utf-8") as f:
                json.dump(ast, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"JSON Parse Error: {e}")

if __name__ == "__main__":
    main()

