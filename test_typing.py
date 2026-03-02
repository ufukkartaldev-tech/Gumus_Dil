import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tkinter as tk
import customtkinter as ctk

from src.ide.config import Config as GumusConfig
from src.ide.ui.editor import CodeEditor

app = ctk.CTk()
app.geometry("800x600")

config = GumusConfig()
editor = CodeEditor(app, config)
editor.pack(fill="both", expand=True)

def simulate_typing():
    # Set focus
    # Simulate user typing A
    editor._textbox.focus_set()
    editor._textbox.event_generate("<KeyPress-a>")
    editor._textbox.event_generate("<KeyRelease-a>")
    app.update()
    txt = editor.get("1.0", "end")
    print("Content after typing: " + repr(txt))
    
    # Try with another key
    editor._textbox.event_generate("<KeyPress-b>")
    editor._textbox.event_generate("<KeyRelease-b>")
    app.update()
    txt = editor.get("1.0", "end")
    print("Content after typing b: " + repr(txt))
    
    app.destroy()

app.after(1000, simulate_typing)
app.mainloop()
