# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk

class SilverContextBar(ctk.CTkFrame):
    """Seçili metin üzerinde yüzen hızlı işlem çubuğu."""
    
    def __init__(self, parent, config, callbacks):
        """
        callbacks: {
            'summarize': func(text),
            'run': func(text),
            'explain': func(text)
        }
        """
        theme = config.THEMES[config.theme]
        super().__init__(
            parent, 
            fg_color=theme['sidebar_bg'], 
            corner_radius=4, 
            border_width=1, 
            border_color=theme['border'],
            height=32
        )
        self.callbacks = callbacks
        self.config = config
        
        # Sürükle-bırak için değil, yüzen bar
        self.pack_propagate(False)
        
        # Butonlar
        self._add_btn("🤖", "Özetle", callbacks.get('summarize'))
        self._add_btn("💡", "Açıkla", callbacks.get('explain'))
        self._add_btn("▶️", "Çalıştır", callbacks.get('run'))
        
        # Başlangıçta gizli
        self.place_forget()

    def _add_btn(self, icon, tooltip, command):
        theme = self.config.THEMES[self.config.theme]
        btn = ctk.CTkButton(
            self, 
            text=icon, 
            width=32, 
            height=32, 
            fg_color="transparent", 
            hover_color=theme['hover'],
            corner_radius=16,
            command=lambda: self._execute(command)
        )
        btn.pack(side="left", padx=2, pady=2)
        
    def _execute(self, command):
        if command:
            command()
        self.hide()

    def show(self, x, y):
        self.place(x=x, y=y)
        self.lift()

    def hide(self):
        self.place_forget()

