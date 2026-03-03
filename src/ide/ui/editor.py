# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk
import re
import os
import threading

from ..core.highlighter import SyntaxHighlighter
from .context_bar import SilverContextBar
from .breadcrumbs import Breadcrumbs
from ..core.formatter import GumusFormatter
from ..core.symbols import SymbolExtractor

from .minimap import Minimap
from .line_numbers import LineNumberCanvas
from .find_replace import FindReplacePanel
from .editor_utils import EditorAutocompleteMixin, EditorLinterMixin, EditorActionsMixin

class CodeEditor(ctk.CTkFrame, EditorAutocompleteMixin, EditorLinterMixin, EditorActionsMixin):
    def __init__(self, parent, config, on_navigate=None, **kwargs):
        super().__init__(parent, corner_radius=8, **kwargs)
        self.config = config
        self.has_content = False
        self.file_path = None
        self.on_navigate = on_navigate
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        
        # 0. Breadcrumbs
        self.breadcrumbs = Breadcrumbs(self, config, on_navigate=self.on_navigate)
        self.breadcrumbs.grid(row=0, column=0, columnspan=3, sticky="ew", padx=8, pady=(4, 0))
        
        # 1. Textbox
        self.textbox = ctk.CTkTextbox(self, activate_scrollbars=True, corner_radius=8, border_width=2)
        self.textbox.grid(row=1, column=1, sticky="nsew", padx=(0, 8), pady=(4, 8))
        self._textbox = self.textbox._textbox
        
        # Font ve Yapılandırma
        font_size = 14 if config.simple_ui else 13
        font_name = 'JetBrains Mono' if self._is_font_available('JetBrains Mono') else 'Consolas'
        self.textbox.configure(wrap="none", font=(font_name, font_size), padx=15, pady=15)
        self._textbox.configure(undo=True, autoseparators=True, maxundo=50, insertwidth=3, spacing1=2, spacing3=2)
        
        # 2. Satır Numaraları
        self.linenumbers = LineNumberCanvas(self, self._textbox, config)
        self.linenumbers.grid(row=1, column=0, sticky="ns", padx=(8, 0), pady=(4, 8))
        
        # 3. Minimap
        self.minimap = Minimap(self, self._textbox, config)
        self.minimap.grid(row=1, column=2, sticky="ns", padx=(0, 8), pady=(4, 8))
        
        # 4. Highlighter
        self.highlighter = SyntaxHighlighter(self._textbox, config)
        
        # 5. Placeholder
        self.placeholder_text = "// 💎 Gümüşdil kodunuzu buraya yazın...\n\n// Örnek:\n// değişken x = 10\n// yazdır(\"Merhaba Dünya!\")"
        self.show_placeholder()
        
        # Event Binding
        self._textbox.bind("<<Change>>", self._on_change)
        self._textbox.bind("<Configure>", self._on_change_ui)
        self._textbox.bind("<KeyRelease>", self._on_key_release)
        self._textbox.bind("<MouseWheel>", self._on_change_ui)
        self._textbox.bind("<Button-1>", self._on_click_editor, add="+")
        self._textbox.bind("<ButtonRelease-1>", self._match_brackets)
        self._textbox.bind("<Return>", self._on_return)
        self._textbox.bind("<Tab>", self._on_tab_press)
        self._textbox.bind("<Button-3>", self._show_context_menu)
        self._textbox.bind("<<Paste>>", self._on_paste)
        
        # Shortcuts
        self._textbox.bind("<Control-f>", self.show_find_dialog)
        self._textbox.bind("<Control-slash>", self.toggle_comment) 
        self._textbox.bind("<Alt-Up>", self.move_line_up)
        self._textbox.bind("<Alt-Down>", self.move_line_down)
        self._textbox.bind("<Control-Shift-K>", self.delete_current_line)
        self._textbox.bind("<F2>", self.rename_symbol)
        self._textbox.bind("<KeyPress>", self._on_key_press)
        self._textbox.bind("<Control-Alt-l>", lambda e: self.format_code())
        
        # Placeholder events
        self._textbox.bind("<FocusIn>", self._on_focus_in)
        self._textbox.bind("<FocusOut>", self._on_focus_out)

        self._orig_yview = self._textbox.yview
        self._textbox.yview = self._custom_yview
        
        # 6. Context Bar
        self.context_bar = SilverContextBar(self, config, callbacks={
            'summarize': self._on_ctx_summarize,
            'explain': self._on_ctx_explain,
            'run': self._on_ctx_run
        })
        self._textbox.bind("<<Selection>>", self._on_selection_change)
        self._textbox.bind("<Button-1>", self._on_click_clear_ctx, add="+")
        
        theme = self.config.THEMES[self.config.theme]
        self._textbox.tag_configure("current_line", background=theme.get('current_line_bg', '#2a2a2a'))
        self._textbox.tag_configure("error_underline", underline=True, foreground="#ff1744")
        self._textbox.tag_configure("execution_line", background="#3d3d00", foreground="#ffffff")
        
        self.apply_theme()
        self._highlight_timer = None
        self.current_errors = {}

    # --- Core Proxy Methods ---
    def insert(self, index, text, tags=None):
        self._textbox.insert(index, text, tags)
        self._on_change()

    def get(self, start, end):
        return self._textbox.get(start, end)

    def delete(self, start, end):
        self._textbox.delete(start, end)
        self._on_change()

    def _is_font_available(self, font_name):
        return font_name in tk.font.families()

    def _custom_yview(self, *args):
        res = self._orig_yview(*args)
        self.linenumbers.redraw()
        if hasattr(self, 'minimap'): self.minimap.redraw()
        return res

    def _on_change_ui(self, event=None):
        self.linenumbers.redraw()
        if hasattr(self, 'minimap'): self.minimap.redraw()

    def _on_change(self, event=None):
        self.linenumbers.redraw()
        if hasattr(self, 'minimap'): self.minimap.redraw()
        self._highlight_current_line()
        self._trigger_highlight()

    def _on_key_release(self, event=None):
        self.linenumbers.redraw()
        if hasattr(self, 'minimap'): self.minimap.redraw()
        self._highlight_current_line()
        self._trigger_highlight()
        self._match_brackets()

    def _on_key_press(self, event):
        if hasattr(self, 'suggestion_frame') and self.suggestion_frame.winfo_ismapped():
            if event.keysym == "Down":
                curr = self.suggestion_box.curselection(); next_i = (curr[0]+1)%self.suggestion_box.size() if curr else 0
                self.suggestion_box.selection_clear(0, tk.END); self.suggestion_box.selection_set(next_i); self.suggestion_box.see(next_i); self._on_suggestion_select(); return "break"
            elif event.keysym == "Up":
                curr = self.suggestion_box.curselection(); prev_i = (curr[0]-1)%self.suggestion_box.size() if curr else 0
                self.suggestion_box.selection_clear(0, tk.END); self.suggestion_box.selection_set(prev_i); self.suggestion_box.see(prev_i); self._on_suggestion_select(); return "break"
            elif event.keysym == "Escape": self.hide_suggestion_box(); return "break"
            elif event.keysym in ("Return", "Tab"): self._apply_suggestion(); return "break"
        
        if event.char in (' ', '\n', '.', '(', ')'): self._textbox.edit_separator()
        if event.char == "(": self.after(10, self._trigger_signature_help)

    def _trigger_highlight(self, delay=100, full=False):
        if self._highlight_timer: self.after_cancel(self._highlight_timer)
        def job():
            if full: self.highlighter.highlight()
            else: self.highlighter.highlight_line(self._textbox.index("insert").split('.')[0])
            self._run_linter()
            self.update_breadcrumbs()
            self._check_autocompletion()
        self._highlight_timer = self.after(delay, job)

    def _highlight_current_line(self):
        self._textbox.tag_remove("current_line", "1.0", tk.END)
        try:
            line = int(self._textbox.index("insert").split('.')[0])
            p = self.master
            while p:
                if hasattr(p, 'on_line_click'): p.on_line_click(line); break
                p = p.master
        except: pass

    # --- UI Helpers ---
    def show_toast(self, message, kind='info'):
        p = self.master
        while p:
            if hasattr(p, 'show_toast'): p.show_toast(message, kind); break
            p = p.master

    def show_placeholder(self):
        if not self._textbox.get("1.0", "end-1c").strip():
            self._textbox.insert("1.0", self.placeholder_text, "placeholder")
            self._textbox.tag_config("placeholder", foreground="gray")

    def hide_placeholder(self):
        if self._textbox.tag_ranges("placeholder"):
            self._textbox.delete("1.0", tk.END)

    def _on_focus_in(self, event=None): self.hide_placeholder()
    def _on_focus_out(self, event=None): self.show_placeholder()
    def _on_click_editor(self, event): self._textbox.focus_set()

    def set_file_path(self, path):
        self.file_path = path; self.update_breadcrumbs()

    def update_breadcrumbs(self):
        try:
            items = []
            if self.file_path:
                items.append({'text': os.path.basename(os.path.dirname(self.file_path)), 'type': 'folder'})
                items.append({'text': os.path.basename(self.file_path), 'type': 'file'})
            else: items.append({'text': 'Adsız', 'type': 'file'})
            
            # Scope detection (simplified)
            curr = int(self._textbox.index("insert").split('.')[0])
            text = self._textbox.get("1.0", f"{curr}.end")
            match = re.search(r'(sınıf|fonksiyon)\s+([a-zA-Z_ığüşöçİĞÜŞÖÇ]\w*)', text.split('\n')[-1])
            if match: items.append({'text': match.group(2), 'type': 'function'})
            
            if hasattr(self, 'breadcrumbs'): self.breadcrumbs.update_path(items)
        except: pass

    # --- Errors & Debug ---
    def set_errors(self, errors):
        self._textbox.tag_remove("error_underline", "1.0", tk.END); self.current_errors = {}
        for e in errors:
            line = e.get("line", 0); self.current_errors[line] = e.get("message", "")
            if line > 0: self._textbox.tag_add("error_underline", f"{line}.0", f"{line}.end")
        self.linenumbers.set_errors(self.current_errors)

    def highlight_execution_line(self, line):
        self._textbox.tag_remove("execution_line", "1.0", tk.END)
        if line > 0:
            self._textbox.tag_add("execution_line", f"{line}.0", f"{line}.end+1c")
            self._textbox.see(f"{line}.0")

    # --- Menu & Dialogs ---
    def _show_context_menu(self, event):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Kes", command=lambda: self._textbox.event_generate("<<Cut>>"))
        menu.add_command(label="Kopyala", command=lambda: self._textbox.event_generate("<<Copy>>"))
        menu.add_command(label="Yapıştır", command=lambda: self._textbox.event_generate("<<Paste>>"))
        menu.tk_popup(event.x_root, event.y_root)

    def show_find_dialog(self, event=None):
        if not hasattr(self, 'find_bar'):
            self.find_bar = FindReplacePanel(self, self.config, self._textbox)
            self.find_bar.grid(row=2, column=1, sticky="ew", padx=8, pady=4)
        self.find_bar.show()

    def show_replace_dialog(self, event=None):
        self.show_find_dialog(); self.find_bar.show_replace()

    def _match_brackets(self, event=None):
        self._textbox.tag_remove("bracket_match", "1.0", tk.END)
        idx = self._textbox.index(tk.INSERT)
        char = self._textbox.get(f"{idx}-1c")
        # Logic here... (simplified for brevity, can be refined)
        pass

    def _on_tab_press(self, event):
        # Auto-complete or indent
        if hasattr(self, 'suggestion_frame') and self.suggestion_frame.winfo_ismapped():
             return self._apply_suggestion()
        self._textbox.insert(tk.INSERT, "    ")
        return "break"

    def _on_return(self, event):
        # Smart indent
        curr = int(self._textbox.index(tk.INSERT).split('.')[0])
        prev_line = self._textbox.get(f"{curr}.0", f"{curr}.end")
        indent = len(prev_line) - len(prev_line.lstrip())
        self._textbox.insert(tk.INSERT, "\n" + (" " * indent))
        if prev_line.strip().endswith(":"): self._textbox.insert(tk.INSERT, "    ")
        return "break"

    def _on_paste(self, event=None):
        self.after(10, lambda: self._trigger_highlight(full=True))

    def _on_selection_change(self, event=None):
        try:
            sel = self._textbox.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if len(sel) > 2:
                bbox = self._textbox.bbox(tk.SEL_LAST)
                if bbox: self.context_bar.show(bbox[0]+50, bbox[1]-35)
            else: self.context_bar.hide()
        except: self.context_bar.hide()

    def _on_click_clear_ctx(self, event=None): self.after(100, self.context_bar.hide)

    def _on_ctx_summarize(self): self._ctx_call("summarize")
    def _on_ctx_explain(self): self._ctx_call("explain")
    def _on_ctx_run(self): self._ctx_call("run")

    def _ctx_call(self, action):
        try:
            text = self._textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            p = self.master
            while p:
                if hasattr(p, 'on_ctx_action'): p.on_ctx_action(action, text); break
                p = p.master
        except: pass

    def apply_theme(self):
        theme = self.config.THEMES[self.config.theme]
        self.textbox.configure(fg_color=theme['editor_bg'], text_color=theme['fg'], border_color=theme['border'])
        self._textbox.configure(insertbackground=theme['accent'], selectbackground=theme['select_bg'])
        self.linenumbers.redraw()

    def _trigger_signature_help(self):
        # Logic for function signature help
        pass
