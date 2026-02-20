
from src.ide.core.python_to_gumus import PythonToGumusTranspiler
import sys

def test():
    code = "a = 1\nprint(a)"
    t = PythonToGumusTranspiler()
    res = t.transpile(code)
    print("RESULT:")
    print(res)

if __name__ == "__main__":
    test()

