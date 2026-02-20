# -*- coding: utf-8 -*-
"""
GÜMÜŞDİL IDE - Modern Karşılama Ekranı (V2.0)
Glassmorphism + Neon Animasyonlar
"""
import customtkinter as ctk
import tkinter as tk
import math
import random
from pathlib import Path
from ..config import EXAMPLES_DIR

class AnimatedBackground(tk.Canvas):
    """
    Arka planda yavaşça hareket eden parçacıklar ve gradyanlar
    """
    def __init__(self, parent, width, height, theme, **kwargs):
        super().__init__(parent, width=width, height=height, bg=theme['bg'], highlightthickness=0, **kwargs)
        self.particles = []
        self.theme = theme
        self.width = width
        self.height = height
        
        # Parçacık oluştur
        for _ in range(20):
            self.particles.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'r': random.randint(2, 6),
                'dx': random.uniform(-0.5, 0.5),
                'dy': random.uniform(-0.5, 0.5),
                'color': random.choice([theme['accent'], theme['keyword'], theme['function']])
            })
            
        self.animate()
        
    def animate(self):
        self.delete("all")
        
        # Arkaplan Deseni (Grid)
        grid_size = 40
        for x in range(0, self.width, grid_size):
            self.create_line(x, 0, x, self.height, fill="#252525", width=1)
        for y in range(0, self.height, grid_size):
            self.create_line(0, y, self.width, y, fill="#252525", width=1)
            
        # Parçacıkları çiz ve hareket ettir
        for p in self.particles:
            self.create_oval(
                p['x'] - p['r'], p['y'] - p['r'],
                p['x'] + p['r'], p['y'] + p['r'],
                fill=p['color'], outline=""
            )
            
            # Hareket
            p['x'] += p['dx']
            p['y'] += p['dy']
            
            # Sınırlardan sekme
            if p['x'] < 0 or p['x'] > self.width: p['dx'] *= -1
            if p['y'] < 0 or p['y'] > self.height: p['dy'] *= -1
            
            # Bağlantı çizgileri (Constellation effect)
            for other in self.particles:
                dist = math.hypot(p['x'] - other['x'], p['y'] - other['y'])
                if dist < 100:
                    alpha = int((1 - dist/100) * 100) # Yaklaştıkça belirginleş
                    # Tkinter alpha desteklemez, renk tonuyla oynayabiliriz ama şimdilik solid
                    self.create_line(p['x'], p['y'], other['x'], other['y'], fill="#333333", width=1)
                    
        self.after(50, self.animate)

class ProjectCard(ctk.CTkFrame):
    """
    Hover efektli proje başlatma kartı
    """
    def __init__(self, parent, icon, title, desc, command, theme, color="accent"):
        super().__init__(parent, fg_color=("gray85", "#2a2a2a"), corner_radius=12, border_width=1, border_color=theme['border'])
        self.command = command
        self.theme = theme
        self.base_color = theme[color]
        
        # İçerik
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(padx=20, pady=20, expand=True, fill="both")
        
        # İkon
        self.lbl_icon = ctk.CTkLabel(content, text=icon, font=("Segoe UI", 32))
        self.lbl_icon.pack(pady=(0, 10))
        
        # Başlık
        self.lbl_title = ctk.CTkLabel(content, text=title, font=("Segoe UI", 16, "bold"), text_color=theme['fg'])
        self.lbl_title.pack()
        
        # Açıklama
        self.lbl_desc = ctk.CTkLabel(content, text=desc, font=("Segoe UI", 11), text_color=theme['comment'], wraplength=140)
        self.lbl_desc.pack(pady=(5, 0))
        
        # Tıklanabilirlik
        self.bind("<Button-1>", self._on_click)
        content.bind("<Button-1>", self._on_click)
        for child in content.winfo_children():
            child.bind("<Button-1>", self._on_click)
            
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_click(self, event):
        if self.command: self.command()
        
    def _on_enter(self, event):
        self.configure(border_color=self.base_color, border_width=2)
        self.lbl_title.configure(text_color=self.base_color)
        
    def _on_leave(self, event):
        self.configure(border_color=self.theme['border'], border_width=1)
        self.lbl_title.configure(text_color=self.theme['fg'])


class WelcomeScreenV2(ctk.CTkToplevel):
    def __init__(self, parent, config, on_open_file, on_new_file, on_open_path=None):
        super().__init__(parent)
        self.config = config
        self.parent = parent
        self.on_open_file = on_open_file
        self.on_new_file = on_new_file
        self.on_open_path = on_open_path
        theme = config.THEMES[config.theme]
        
        # Pencere Ayarları
        self.title("GümüşDil - Hoş Geldiniz")
        self.geometry("900x600")
        self.resizable(False, False)
        
        # Ekranın ortasında aç
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 900) // 2
        y = (screen_height - 600) // 2
        self.geometry(f"+{x}+{y}")
        
        # Arka Plan (Animasyonlu)
        self.bg_frame = ctk.CTkFrame(self, corner_radius=0)
        self.bg_frame.pack(fill="both", expand=True)
        
        # Canvas'ı bir wrapper frame içine al
        canvas_wrapper = ctk.CTkFrame(self.bg_frame, fg_color="transparent")
        canvas_wrapper.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.canvas = AnimatedBackground(canvas_wrapper, width=900, height=600, theme=theme)
        self.canvas.pack(fill="both", expand=True)
        
        # Ana İçerik Kutusu (Glassmorphism)
        # Ortada yüzen bir panel
        container = ctk.CTkFrame(
            self.bg_frame, 
            fg_color=("#ffffff", "#1e1e1e"), # Hex formatına çevrildi
            corner_radius=20,
            border_width=1,
            border_color=theme['border']
        )
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.85)
        
        # --- Sol Panel: Logo ve Karşılama ---
        left_panel = ctk.CTkFrame(container, fg_color="transparent")
        left_panel.pack(side="left", fill="both", expand=True, padx=40, pady=40)
        
        # Logo
        ctk.CTkLabel(left_panel, text="💎", font=("Segoe UI", 64)).pack(anchor="w")
        ctk.CTkLabel(left_panel, text="GümüşDil", font=("Segoe UI", 36, "bold"), text_color=theme['accent']).pack(anchor="w")
        ctk.CTkLabel(left_panel, text="Kodlamak hiç bu kadar bizden olmamıştı.", font=("Segoe UI", 14, "italic"), text_color=theme['comment']).pack(anchor="w", pady=(0, 20))
        
        # Günün İpucu
        tips = [
            "💡 İpucu: Hata aldığınızda Gümüş Zeka size çözüm önerebilir.",
            "💡 İpucu: 'Ctrl+Shift+P' ile komut paletini açmayı denediniz mi? (Yakında!)",
            "💡 İpucu: Değişkenlerinizi GümüşHafıza ile canlı izleyebilirsiniz.",
            "💡 İpucu: 'eğer' ve 'döngü' bloklarını Türkçe kullanmanın keyfini çıkarın.",
            "💡 İpucu: Voxel Dünyası ile 3D oyunlar yapabilirsiniz!"
        ]
        tip = random.choice(tips)
        
        tip_frame = ctk.CTkFrame(left_panel, fg_color=("gray90", "#252525"), corner_radius=10)
        tip_frame.pack(fill="x", pady=20, anchor="s")
        ctk.CTkLabel(tip_frame, text=tip, font=("Segoe UI", 11), text_color=theme['fg'], wraplength=250, justify="left").pack(padx=15, pady=10)
        
        # Sürüm ve Durum Bilgisi
        stats_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        stats_frame.pack(side="bottom", fill="x", anchor="w")
        
        ctk.CTkLabel(stats_frame, text="🚀 GÜMÜŞ METRİKLER", font=("Segoe UI", 10, "bold"), text_color=theme['accent']).pack(anchor="w")
        ctk.CTkLabel(stats_frame, text="• GümüşZeka Tamirleri: %d" % random.randint(120, 500), font=("Segoe UI", 9), text_color=theme['comment']).pack(anchor="w")
        ctk.CTkLabel(stats_frame, text="• Toplam Kod Satırı: %dK+" % random.randint(10, 50), font=("Segoe UI", 9), text_color=theme['comment']).pack(anchor="w")
        ctk.CTkLabel(stats_frame, text="• Pardus Uyumluluk: %100", font=("Segoe UI", 9), text_color=theme['comment']).pack(anchor="w")
        
        ctk.CTkLabel(stats_frame, text="\nv1.1.0-Leopar", font=("Consolas", 10), text_color=theme['comment']).pack(anchor="w")

        # --- Sağ Panel: Hızlı Başlangıç ---
        right_panel = ctk.CTkFrame(container, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True, padx=20, pady=40)
        
        ctk.CTkLabel(right_panel, text="Başlangıç", font=("Segoe UI", 18, "bold"), text_color=theme['fg']).pack(anchor="w", pady=(0, 15))
        
        # Kartlar Grid
        grid = ctk.CTkFrame(right_panel, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure((0, 1), weight=1)
        
        # Yeni Dosya
        ProjectCard(grid, "📄", "Yeni Dosya", "Boş bir GümüşDil sayfası aç.", 
                   lambda: self._action(on_new_file), theme, color="accent").grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Dosya Aç
        ProjectCard(grid, "📂", "Dosya Aç", "Bilgisayarındaki bir projeyi yükle.", 
                   lambda: self._action(self._open_file_dialog), theme, color="keyword").grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Gümüş Market
        ProjectCard(grid, "🛒", "Gümüş Pazar", "Kütüphane ve eklentilere göz at.", 
                   lambda: self._action(lambda: self._jump_to_sidebar("market")), theme, color="function").grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Gümüş Analiz
        ProjectCard(grid, "📊", "Gümüş Analiz", "Performans ve darboğaz analizi yap.", 
                   lambda: self._action(lambda: self._jump_to_sidebar("profiler")), theme, color="class").grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Son Dosyalar (Mockup)
        # İleride gerçek geçmiş (history) eklenebilir
        recent_frame = ctk.CTkFrame(right_panel, fg_color=("gray90", "#252525"), corner_radius=10)
        recent_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(recent_frame, text="Son Kullanılanlar", font=("Segoe UI", 12, "bold"), text_color=theme['comment']).pack(anchor="w", padx=15, pady=(10, 5))
        
        recents = self.config.recent_files[:5] # En son 5 dosya
        if not recents:
             ctk.CTkLabel(recent_frame, text="Henüz dosya açılmadı.", font=("Segoe UI", 11), text_color=theme['comment']).pack(padx=15, pady=5)
        
        for f_path in recents:
            f_name = Path(f_path).name
            btn = ctk.CTkButton(recent_frame, text=f"• {f_name}", anchor="w", fg_color="transparent", hover_color=("gray80", "#333333"),
                               height=24, font=("Consolas", 11), text_color=theme['fg'],
                               command=lambda p=f_path: self._action(lambda: self.on_open_path(p) if self.on_open_path else None))
            btn.pack(fill="x", padx=5, pady=1)
            
        # Alt boşluk
        ctk.CTkFrame(recent_frame, height=5, fg_color="transparent").pack()

    def _action(self, func):
        self.destroy() # Pencereyi kapat
        if func: func()

    def _open_file_dialog(self):
        # Ana penceredeki open_file_dialog'u tetikle
        self.on_open_file()
        
    def _open_examples(self):
        # Örnekler klasörü
        from tkinter import filedialog
        path = filedialog.askopenfilename(initialdir=EXAMPLES_DIR, filetypes=[("GümüşDil", "*.tr")])
        if path and self.on_open_path:
            self.on_open_path(path)

    def _jump_to_sidebar(self, mode):
        """Main Window üzerinden sidebar modunu değiştir"""
        if hasattr(self.parent, 'on_activity_click'):
            self.parent.on_activity_click(mode)

