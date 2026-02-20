import sys
import os
from pathlib import Path

# Add src to sys.path to resolve imports correctly
current_dir = Path(__file__).parent.parent 
sys.path.insert(0, str(current_dir))

try:
    from src.ide.core.transpiler import GumusToPythonTranspiler
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def main():
    root_dir = Path(os.getcwd())
    source_file = root_dir / "test_transpiler.tr"
    
    print(f"Transpiling: {source_file}")
    
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            code = f.read()
            
        transpiler = GumusToPythonTranspiler()
        python_code = transpiler.transpile(code)
        
        print("-" * 40)
        print("PYTHON ÇIKTISI:")
        print("-" * 40)
        print(python_code)
        print("-" * 40)
        
        # Save output
        with open("test_transpiler.py", "w", encoding="utf-8") as f:
            f.write(python_code)
        print("Saved to test_transpiler.py")
        
    except Exception as e:
        print(f"Transpilation Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

