# -*- coding: utf-8 -*-
"""
GÜMÜŞDİL IDE - Breadcrumbs (Gezinti Çubuğu)
Kodun neresinde olduğunuzu gösteren zarif şerit.
"""
import customtkinter as ctk

class Breadcrumbs(ctk.CTkFrame):
    def __init__(self, parent, config, on_navigate=None, **kwargs):
        super().__init__(parent, height=26, corner_radius=0, **kwargs)
        self.config = config
        self.on_navigate = on_navigate # Callback: (type, value)
        self.pack_propagate(False)
        self.path_items = []
        
        # Tema
        self.theme = config.THEMES[config.theme]
        self.configure(fg_color=self.theme['editor_bg']) # veya sidebar_bg
        
        # İçerik Frame (Yatay Layout)
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="left", fill="y", padx=5)
        
    def update_path(self, items):
        """
        items: List of dicts -> [{'text': 'src', 'type': 'folder', 'path': '/...'}, ...]
        """
        # Performans: Eğer metinler aynıysa yeniden çizme
        current_texts = [item.get('text', '') for item in items]
        if self.path_items == current_texts: return
        self.path_items = current_texts
        
        # Temizle
        for widget in self.content.winfo_children():
            widget.destroy()
            
        # Yeniden oluştur
        for i, item in enumerate(items):
            text = item.get('text', '')
            itype = item.get('type', 'generic')
            
            # Ayırıcı
            if i > 0:
                ctk.CTkLabel(
                    self.content, 
                    text=" › ", 
                    font=("Consolas", 10), 
                    text_color=self.theme['comment']
                ).pack(side="left")
            
            # İkon
            icon = ""
            if itype == 'folder': icon = "📂 "
            elif itype == 'file': icon = "📄 "
            elif itype == 'class': icon = "📦 "
            elif itype == 'function': icon = "ƒ "
            
            # Buton
            btn = ctk.CTkButton(
                self.content,
                text=f"{icon}{text}",
                font=("Segoe UI", 11),
                fg_color="transparent",
                hover_color=self.theme['hover'],
                text_color=self.theme['fg'] if i < len(items)-1 else self.theme['accent'], # Sonuncusu parlak
                height=22,
                width=20,
                corner_radius=4,
                command=lambda it=item: self._on_click(it)
            )
            btn.pack(side="left", padx=0)
            
    def _on_click(self, item):
        """Tıklama olayı"""
        if self.on_navigate:
            self.on_navigate(item)
            
    def set_theme(self, theme):
        self.theme = theme
        self.configure(fg_color=theme['editor_bg'])
        # İçeriği yenilemek gerekir ama şimdilik kalsın

