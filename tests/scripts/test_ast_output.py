
import subprocess
import os
import sys

def test_ast():
    compiler = r"c:\Users\90538\Desktop\Ufuk Kartal\programlama_dili\bin\gumus.exe"
    test_file = r"c:\Users\90538\Desktop\Ufuk Kartal\programlama_dili\simple_test.tr"
    
    if not os.path.exists(compiler):
        print("Compiler not found")
        return

    res = subprocess.run([compiler, "--dump-ast", test_file], capture_output=True, text=True, encoding='utf-8')
    print("STDOUT:")
    print(res.stdout)
    print("STDERR:")
    print(res.stderr)

if __name__ == "__main__":
    test_ast()

