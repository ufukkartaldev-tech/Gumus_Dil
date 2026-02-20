# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk
import random

class MarketItem(ctk.CTkFrame):
    """Market'teki her bir kütüphane veya eklenti kartı"""
    def __init__(self, parent, name, desc, author, stars, version, theme, on_install):
        super().__init__(parent, fg_color=theme['bg'], corner_radius=12, border_width=1, border_color=theme['border'])
        
        self.on_install = on_install
        self.name = name
        
        # İçerik
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(padx=15, pady=15, fill="both")
        
        # Başlık ve Versiyon
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x")
        
        ctk.CTkLabel(header, text=name, font=("Segoe UI", 14, "bold"), text_color=theme['accent']).pack(side="left")
        ctk.CTkLabel(header, text=f"v{version}", font=("Consolas", 10), text_color=theme['comment']).pack(side="right")
        
        # Açıklama
        ctk.CTkLabel(content, text=desc, font=("Segoe UI", 11), text_color=theme['fg'], wraplength=200, justify="left").pack(anchor="w", pady=(5, 10))
        
        # Alt Bilgi (Yazar ve Yıldız)
        footer = ctk.CTkFrame(content, fg_color="transparent")
        footer.pack(fill="x")
        
        ctk.CTkLabel(footer, text=f"👤 {author}", font=("Segoe UI", 10), text_color=theme['comment']).pack(side="left")
        ctk.CTkLabel(footer, text=f"⭐ {stars}", font=("Segoe UI", 10), text_color="#FFD700").pack(side="right")
        
        # Yükle Butonu
        self.install_btn = ctk.CTkButton(
            content, 
            text="Yükle", 
            height=28,
            fg_color=theme['accent'],
            hover_color=theme.get('hover', "#00aaff"),
            command=self._install_click
        )
        self.install_btn.pack(fill="x", pady=(10, 0))

    def _install_click(self):
        self.install_btn.configure(text="Yükleniyor...", state="disabled")
        # Simüle edilmiş yükleme gecikmesi
        self.after(1500, self._finish_install)

    def _finish_install(self):
        self.install_btn.configure(text="✅ Yüklendi", fg_color="gray50")
        if self.on_install:
            self.on_install(self.name)

class MarketPanel(ctk.CTkFrame):
    """Gümüş Pazar - Kütüphane ve Eklenti Mağazası"""
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
            placeholder_text="Kütüphane veya eklenti ara...",
            height=35,
            border_width=1,
            border_color=self.theme['border']
        )
        self.search_entry.pack(fill="x")
        
        # Kategoriler
        cat_frame = ctk.CTkFrame(self, fg_color="transparent")
        cat_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        categories = ["Hepsi", "Sistem", "Grafik", "AI", "Oyun"]
        for cat in categories:
            btn = ctk.CTkButton(
                cat_frame, 
                text=cat, 
                width=60, 
                height=22, 
                font=("Segoe UI", 10),
                fg_color=self.theme['sidebar_bg'] if cat != "Hepsi" else self.theme['accent'],
                text_color=self.theme['fg']
            )
            btn.pack(side="left", padx=2)
            
        # Kaydırılabilir Market Alanı
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            label_text="🔥 Öne Çıkanlar"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Örnek Market Ürünleri
        self.items_data = [
            ("Gümüş-Veri", "Yüksek performanslı veri işleme ve analiz kütüphanesi.", "GümüşEkip", 1250, "1.2.0"),
            ("Anadolu-Görsel", "Gelişmiş 2D/3D grafik motoru entegrasyonu.", "PardusGeliştirici", 840, "0.9.5"),
            ("Zeka-Kökü", "Yapay sinir ağları ve derin öğrenme araçları.", "Metaforik", 2100, "2.1.0"),
            ("Siber-Kalkan", "Şifreleme ve ağ güvenliği protokolleri.", "AselsanGönüllü", 560, "1.0.1"),
            ("Hızlı-Matematik", "GPU destekli matris ve lineer cebir işlemleri.", "TübitakGenç", 420, "1.1.0")
        ]
        
        self._load_items()

    def _load_items(self):
        for name, desc, author, stars, version in self.items_data:
            item = MarketItem(
                self.scroll_frame, 
                name, desc, author, stars, version, 
                self.theme, 
                self._on_item_installed
            )
            item.pack(fill="x", pady=5)

    def _on_item_installed(self, name):
        print(f"Market'ten yüklendi: {name}")
        # İleride library_bridge.py içine dinamik kayıt eklenebilir
