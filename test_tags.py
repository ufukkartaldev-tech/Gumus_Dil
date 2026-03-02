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

def check_tags():
    print(editor._textbox.tag_names())
    for tag in editor._textbox.tag_names():
        print(f"Tag {tag}: {editor._textbox.tag_cget(tag, 'background')} {editor._textbox.tag_cget(tag, 'foreground')}")
    app.destroy()

app.after(1000, check_tags)
app.mainloop()
