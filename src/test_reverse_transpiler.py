# -*- coding: utf-8 -*-
import sys
import os
from pathlib import Path

# Add src to sys.path
current_dir = Path(__file__).parent.parent 
sys.path.insert(0, str(current_dir))

try:
    from src.ide.core.python_to_gumus import PythonToGumusTranspiler
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def test_translation():
    python_code = """
def topla(a, b):
    return a + b

sayi = 10
if sayi > 5:
    print("Sayı büyük")
else:
    print("Sayı küçük")
"""
    print("PYTHON KODU:")
    print(python_code)
    
    translator = PythonToGumusTranspiler()
    gumus_code = translator.transpile(python_code)
    
    print("-" * 40)
    print("GÜMÜŞDİL TERCÜMESİ:")
    print("-" * 40)
    print(gumus_code)
    print("-" * 40)

if __name__ == "__main__":
    test_translation()

