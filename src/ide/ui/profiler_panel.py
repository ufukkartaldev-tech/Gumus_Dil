# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk
import random
import time

class ProfilerPanel(ctk.CTkFrame):
    """Gümüş Analiz - Performans ve Profilleme Paneli"""
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.theme = config.THEMES[config.theme]
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Üst Özet Kartı
        summary_frame = ctk.CTkFrame(self, fg_color=self.theme['sidebar_bg'], corner_radius=12)
        summary_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(summary_frame, text="🚀 PERFORMANS ÖZETİ", font=("Segoe UI", 12, "bold"), text_color=self.theme['accent']).pack(pady=(10, 5))
        
        self.time_lbl = ctk.CTkLabel(summary_frame, text="Son Çalışma Süresi: 0ms", font=("Consolas", 14), text_color=self.theme['fg'])
        self.time_lbl.pack()
        
        self.mem_lbl = ctk.CTkLabel(summary_frame, text="Tepe Bellek Kullanımı: 0KB", font=("Consolas", 11), text_color=self.theme['comment'])
        self.mem_lbl.pack(pady=(0, 10))
        
        # Grafik Alanı (Simüle edilmiş)
        self.chart_canvas = tk.Canvas(self, bg=self.theme['bg'], highlightthickness=1, highlightbackground=self.theme['border'], height=150)
        self.chart_canvas.pack(fill="x", padx=10, pady=5)
        
        self._draw_mock_chart()
        
        # Fonksiyon Analizi (Heatmap tarzı)
        ctk.CTkLabel(self, text="🔥 Darboğaz Analizi (Hot Paths)", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.mock_hot_paths = [
            ("main_loop", "42%", "#ff4444"),
            ("render_frame", "31%", "#ff8844"),
            ("check_collision", "18%", "#ffbb44"),
            ("update_input", "9%", "#44ff88")
        ]
        
        self._load_hot_paths()

    def _draw_mock_chart(self):
        self.chart_canvas.delete("all")
        w, h = 400, 150
        points = []
        for i in range(20):
            points.append((i * 20, h - random.randint(20, 100)))
            
        for i in range(len(points) - 1):
            self.chart_canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill=self.theme['accent'], width=2)
            
        self.chart_canvas.create_text(10, 10, text="CPU Usage %", fill=self.theme['comment'], anchor="nw", font=("Consolas", 8))

    def _load_hot_paths(self):
        for name, perc, color in self.mock_hot_paths:
            row = ctk.CTkFrame(self.scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=name, font=("Consolas", 11)).pack(side="left", padx=5)
            
            # Progress bar as heatmap
            bar_bg = ctk.CTkFrame(row, fg_color=self.theme['sidebar_bg'], height=10, width=100)
            bar_bg.pack(side="right", padx=5)
            bar_bg.pack_propagate(False)
            
            val = int(perc.strip('%'))
            ctk.CTkFrame(bar_bg, fg_color=color, height=10, width=val).pack(side="left")
            
            ctk.CTkLabel(row, text=perc, font=("Consolas", 10, "bold"), text_color=color).pack(side="right")

    def start_profiling(self):
        self.time_lbl.configure(text="⏱️ Analiz ediliyor...")
        # Simülasyon
        self.after(2000, self._finish_profiling)

    def _finish_profiling(self):
        t = random.randint(15, 250)
        m = random.randint(1024, 8192)
        self.time_lbl.configure(text=f"Son Çalışma Süresi: {t}ms")
        self.mem_lbl.configure(text=f"Tepe Bellek Kullanımı: {m}KB")
        self._draw_mock_chart()
