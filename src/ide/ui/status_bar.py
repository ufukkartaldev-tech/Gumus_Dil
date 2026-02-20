# -*- coding: utf-8 -*-
"""
Gümüşdil IDE - Gelişmiş Durum Çubuğu
"""
import customtkinter as ctk
import tkinter as tk
from datetime import datetime

class StatusBar(ctk.CTkFrame):
    def __init__(self, parent, config, **kwargs):
        super().__init__(parent, corner_radius=0, height=28, **kwargs)
        self.config = config
        self.pack_propagate(False)
        
        theme = config.THEMES[config.theme]
        self.configure(fg_color=theme['sidebar_bg'], border_width=1, border_color=theme['border'])
        
        # Sol taraf - Dosya bilgisi
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.pack(side="left", fill="y", padx=10)
        
        self.file_label = ctk.CTkLabel(
            self.left_frame,
            text="📄 Adsız",
            font=("Segoe UI", 10),
            text_color=theme['fg']
        )
        self.file_label.pack(side="left", padx=5)
        
        # Orta - Satır/Sütun bilgisi
        self.middle_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.middle_frame.pack(side="left", fill="y", padx=20)
        
        self.position_label = ctk.CTkLabel(
            self.middle_frame,
            text="Satır 1, Sütun 1",
            font=("Segoe UI", 10),
            text_color=theme['comment']
        )
        self.position_label.pack(side="left")
        
        # Sağ taraf - Durum bilgileri
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.pack(side="right", fill="y", padx=10)
        
        # 📊 GümüşRadar (CPU/MEM/LINE)
        self.radar_label = ctk.CTkLabel(
            self.right_frame,
            text="CPU: 0% | MEM: 0MB | LN: 1",
            font=("Consolas", 10, "bold"),
            text_color=theme['accent']
        )
        self.radar_label.pack(side="right", padx=15)

        # 🌿 Git Branch Simulation
        self.git_label = ctk.CTkLabel(
            self.right_frame,
            text="🌿 ana-dal (master)",
            font=("Segoe UI", 9, "italic"),
            text_color=theme['comment']
        )
        self.git_label.pack(side="right", padx=10)

        # Encoding
        self.encoding_label = ctk.CTkLabel(
            self.right_frame,
            text="UTF-8",
            font=("Segoe UI", 9),
            text_color=theme['comment']
        )
        self.encoding_label.pack(side="right", padx=10)
        
        # Dil
        self.lang_label = ctk.CTkLabel(
            self.right_frame,
            text="💎 Gümüşdil",
            font=("Segoe UI", 9, "bold"),
            text_color=theme['accent']
        )
        self.lang_label.pack(side="right", padx=10)

        # Tema seçici butonu (Görsel olarak entegre)
        self.theme_btn = ctk.CTkButton(
            self.right_frame,
            text=f"🎨 {theme.get('name', 'Tema')}",
            width=140,
            height=22,
            font=("Segoe UI", 9),
            fg_color="transparent",
            hover_color=theme['hover'],
            text_color=theme['comment'],
            corner_radius=4
        )
        self.theme_btn.pack(side="right", padx=5)
    
    def update_file(self, filename):
        """Dosya adını güncelle"""
        icon = "📄" if filename else "📝"
        name = filename if filename else "Adsız"
        self.file_label.configure(text=f"{icon} {name}")
    
    def update_position(self, line, column):
        """Satır ve sütun bilgisini güncelle"""
        self.position_label.configure(text=f"Satır {line}, Sütun {column}")
    
    def update_status(self, message, duration=3000):
        """Geçici durum mesajı göster"""
        original_text = self.position_label.cget("text")
        self.position_label.configure(text=message)
        self.after(duration, lambda: self.position_label.configure(text=original_text))
    
    def set_theme_callback(self, callback):
        """Tema değiştirme callback'i ayarla"""
        self.theme_btn.configure(command=callback)
    
    def update_theme_display(self):
        """Tema adını güncelle"""
        theme = self.config.THEMES[self.config.theme]
        self.theme_btn.configure(text=f"🎨 {theme.get('name', 'Tema')}")
        
        # Renkleri güncelle
        self.configure(fg_color=theme['sidebar_bg'], border_color=theme['border'])
        self.file_label.configure(text_color=theme['fg'])
        self.position_label.configure(text_color=theme['comment'])
        self.encoding_label.configure(text_color=theme['comment'])
        self.lang_label.configure(text_color=theme['comment'])
        self.theme_btn.configure(
            hover_color=theme['hover'],
            text_color=theme['comment']
        )
        
    def update_git_info(self, branch_name):
        """Git branch bilgisini güncelle"""
        if branch_name:
            self.git_label.configure(text=f"🌿 {branch_name}")
        else:
            self.git_label.configure(text="")

