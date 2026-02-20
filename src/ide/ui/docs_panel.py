# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk
from ..core.library_bridge import LibraryBridge

class DocsPanel(ctk.CTkFrame):
    """Gümüş-Sözlük (Milli Kütüphane Rehberi)"""
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.theme = config.THEMES[config.theme]
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Üst Arama Çubuğu
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Kütüphane ara (örn: kripto, ai)...",
            height=35,
            border_width=1,
            border_color=self.theme['border']
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        # Bilgi Notu
        ctk.CTkLabel(self, text="📚 GÜMÜŞ-SÖZLÜK", font=("Segoe UI", 14, "bold"), text_color=self.theme['accent']).pack(pady=(5, 10))
        
        # Kaydırılabilir Liste
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self._load_libraries()

    def _load_libraries(self, filter_text=""):
        # Temizle
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        lib_map = LibraryBridge.LIBRARY_MAP
        
        for name, info in lib_map.items():
            if filter_text.lower() and filter_text.lower() not in name.lower():
                continue
                
            card = ctk.CTkFrame(self.scroll_frame, fg_color=self.theme['sidebar_bg'], corner_radius=10, border_width=1, border_color=self.theme['border'])
            card.pack(fill="x", pady=5, padx=5)
            
            # Başlık
            ctk.CTkLabel(card, text=f"💎 {name.upper()}", font=("Segoe UI", 12, "bold"), text_color=self.theme['accent']).pack(anchor="w", padx=15, pady=(10, 5))
            
            # Python Karşılığı
            py_info = info.get("py", {})
            py_text = f"🐍 Python: import {py_info.get('module')} as {py_info.get('alias')}"
            ctk.CTkLabel(card, text=py_text, font=("Consolas", 10), text_color=self.theme['fg']).pack(anchor="w", padx=25)
            
            # C++ Karşılığı
            cpp_info = info.get("cpp", {})
            cpp_text = f"⚙️ C++: #include <{cpp_info.get('include')}>"
            if cpp_info.get('namespace'):
                cpp_text += f" (using {cpp_info.get('namespace')})"
            ctk.CTkLabel(card, text=cpp_text, font=("Consolas", 10), text_color=self.theme['comment']).pack(anchor="w", padx=25, pady=(0, 10))
            
            # Kopyala Butonları (Opsiyonel)
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            ctk.CTkButton(btn_frame, text="Dahil Et", width=80, height=22, font=("Segoe UI", 9),
                         command=lambda n=name: self._copy_to_editor(n)).pack(side="right")

    def _on_search(self, event):
        text = self.search_entry.get()
        self._load_libraries(text)

    def _copy_to_editor(self, name):
        # Editöre "dahil et kütüphane" formatında ekleme simülasyonu
        snippet = f"dahil et {name}\n"
        # Bu fonksiyon main_window üzerinden editöre ulaşmalı, şimdilik toast gibi gösterelim
        print(f"Editöre eklendi: {snippet}")
        # Not: Gerçek ekleme callbacks üzerinden yapılabilir.
