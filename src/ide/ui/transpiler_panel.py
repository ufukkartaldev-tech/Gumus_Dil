# -*- coding: utf-8 -*-
import customtkinter as ctk

class TranspilerPanel(ctk.CTkFrame):
    def __init__(self, parent, config, on_language_change=None):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_language_change = on_language_change
        
        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", pady=5, padx=5)
        
        # Hedef Dil Seçici
        self.lang_var = ctk.StringVar(value="Python")
        self.lang_menu = ctk.CTkOptionMenu(
            self.header, 
            values=["Python", "C++"], 
            variable=self.lang_var,
            width=80,
            height=24,
            command=self._on_lang_change
        )
        self.lang_menu.pack(side="left", padx=(0, 10))
        
        self.info_lbl = ctk.CTkLabel(self.header, text="Çıktısı", font=("Segoe UI", 12, "bold"))
        self.info_lbl.pack(side="left")
        
        self.copy_btn = ctk.CTkButton(self.header, text="Kopyala", width=60, height=24, command=self.copy_code)
        self.copy_btn.pack(side="right")
        
        # Code Area
        self.code_view = ctk.CTkTextbox(self, font=("Consolas", 12), wrap="none")
        self.code_view.pack(fill="both", expand=True, padx=5, pady=5)
        
    def _on_lang_change(self, choice):
        if self.on_language_change:
            self.on_language_change(choice)

    def set_code(self, code):
        self.code_view.configure(state="normal")
        self.code_view.delete("1.0", "end")
        self.code_view.insert("1.0", code)
        self.code_view.configure(state="disabled")
        
    def copy_code(self):
        code = self.code_view.get("1.0", "end-1c")
        self.master.clipboard_clear()
        self.master.clipboard_append(code)
        # Toast?
        print(f"{self.lang_var.get()} kodu kopyalandı.")
