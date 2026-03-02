import tkinter as tk
import customtkinter as ctk
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# config.py has a relative path which might fail if not in the right dir, but we are in gumus_dil.
try:
    from src.ide.config import Config as GumusConfig
    from src.ide.ui.editor import CodeEditor
except Exception as e:
    print(f"Import error: {e}")
    exit(1)

app = ctk.CTk()
app.geometry("800x600")

config = GumusConfig()
# Bypass the theme loading issues or just use default
editor = CodeEditor(app, config)
editor.pack(fill="both", expand=True)

# Test insert
try:
    editor.insert("end", "print('hello')\n")
    print("Insertion worked")
except Exception as e:
    print(f"Error: {e}")

def after_timer():
    print(f"Content: {editor.get('1.0', 'end')}")
    editor.insert("end", "Timer done\n")
    print("Timer executed")
    app.update()

app.after(1000, after_timer)
app.after(2000, app.destroy)

try:
    app.mainloop()
except Exception as e:
    print(f"Mainloop error: {e}")
