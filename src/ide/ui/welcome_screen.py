# -*- coding: utf-8 -*-
"""
Gümüşdil IDE - Modern Hoş Geldin Ekranı
"""
import customtkinter as ctk
import tkinter as tk
from pathlib import Path
import json

class WelcomeScreen(ctk.CTkToplevel):
    def __init__(self, parent, config, callbacks):
        super().__init__(parent)
        
        self.config = config
        self.callbacks = callbacks
        
        # Pencere ayarları
        self.title("💎 Gümüşdil IDE'ye Hoş Geldiniz")
        self.geometry("900x600")
        self.resizable(False, False)
        
        # Pencereyi merkeze al
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 900) // 2
        y = (screen_height - 600) // 2
        self.geometry(f"900x600+{x}+{y}")
        
        # MODAL - Ana pencereyi engelle
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        
        # Her zaman üstte
        self.attributes('-topmost', True)
        self.after(100, lambda: self.attributes('-topmost', False))
        
        # Tema uygula
        theme = config.THEMES[config.theme]
        
        # Ana container
        self.main_frame = ctk.CTkFrame(self, fg_color=theme['bg'], corner_radius=0)
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.create_content(theme)
        
        # Animasyon
        if config.animations_enabled:
            self.animate_entrance()
        
        # ESC ile kapat
        self.bind("<Escape>", lambda e: self.destroy())

        
    def create_content(self, theme):
        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color=theme['sidebar_bg'], corner_radius=0, height=120)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Close Button (Top Right)
        close_btn = ctk.CTkButton(
            header_frame,
            text="×",
            width=40,
            height=40,
            fg_color="transparent",
            hover_color=theme['hover'],
            text_color=theme['fg'],
            font=("Arial", 20),
            command=self.destroy
        )
        close_btn.pack(side="right", anchor="n", padx=10, pady=10)
        
        # Logo ve başlık
        title_label = ctk.CTkLabel(
            header_frame,
            text="💎 Gümüşdil IDE",
            font=("Segoe UI", 36, "bold"),
            text_color=theme['accent']
        )
        title_label.place(relx=0.5, rely=0.4, anchor="center")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Türkçe Programlama Dilinin Modern Geliştirme Ortamı",
            font=("Segoe UI", 13),
            text_color=theme['comment']
        )
        subtitle_label.place(relx=0.5, rely=0.7, anchor="center")
        
        # Content area
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Grid layout
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Sol panel - Hızlı Başlangıç
        left_panel = self.create_quick_start_panel(content_frame, theme)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Sağ panel - Örnekler ve Kaynaklar
        right_panel = self.create_resources_panel(content_frame, theme)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Footer
        footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=50)
        footer_frame.pack(fill="x", padx=40, pady=(0, 20))
        

        
        show_again_var = ctk.BooleanVar(value=True)
        show_again_check = ctk.CTkCheckBox(
            footer_frame,
            text="Başlangıçta göster",
            variable=show_again_var,
            font=("Segoe UI", 11),
            text_color=theme['comment']
        )
        show_again_check.pack(side="right", padx=10)
        
    def create_quick_start_panel(self, parent, theme):
        panel = ctk.CTkFrame(parent, fg_color=theme['sidebar_bg'], corner_radius=12)
        
        # Başlık
        title = ctk.CTkLabel(
            panel,
            text="⚡ Hızlı Başlangıç",
            font=("Segoe UI", 18, "bold"),
            text_color=theme['fg']
        )
        title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Butonlar
        actions = [
            ("📄 Yeni Dosya", "Boş bir Gümüşdil dosyası oluştur", self.callbacks.get('new_file')),
            ("📂 Dosya Aç", "Mevcut bir dosyayı aç", self.callbacks.get('open_file')),
            ("📁 Klasör Aç", "Bir proje klasörü aç", self.callbacks.get('open_folder')),
        ]
        
        for icon_text, desc, callback in actions:
            btn_frame = ctk.CTkFrame(panel, fg_color="transparent")
            btn_frame.pack(fill="x", padx=20, pady=5)
            
            btn = ctk.CTkButton(
                btn_frame,
                text=icon_text,
                command=lambda c=callback: self.execute_and_close(c),
                fg_color=theme['bg'],
                hover_color=theme['hover'],
                text_color=theme['fg'],
                font=("Segoe UI", 13, "bold"),
                height=45,
                anchor="w",
                corner_radius=8
            )
            btn.pack(fill="x")
            
            desc_label = ctk.CTkLabel(
                btn_frame,
                text=desc,
                font=("Segoe UI", 10),
                text_color=theme['comment']
            )
            desc_label.pack(anchor="w", padx=10, pady=(2, 5))
        
        # Son dosyalar
        recent_label = ctk.CTkLabel(
            panel,
            text="📌 Son Dosyalar",
            font=("Segoe UI", 14, "bold"),
            text_color=theme['fg']
        )
        recent_label.pack(pady=(20, 10), padx=20, anchor="w")
        
        recent_files = self.get_recent_files()
        if recent_files:
            for file_path in recent_files[:3]:
                file_btn = ctk.CTkButton(
                    panel,
                    text=f"  {Path(file_path).name}",
                    command=lambda p=file_path: self.open_recent(p),
                    fg_color="transparent",
                    hover_color=theme['hover'],
                    text_color=theme['comment'],
                    font=("Segoe UI", 11),
                    height=30,
                    anchor="w"
                )
                file_btn.pack(fill="x", padx=20, pady=2)
        else:
            no_recent = ctk.CTkLabel(
                panel,
                text="Henüz dosya açılmamış",
                font=("Segoe UI", 10),
                text_color=theme['comment']
            )
            no_recent.pack(padx=20, anchor="w")
        
        return panel
    
    def create_resources_panel(self, parent, theme):
        panel = ctk.CTkFrame(parent, fg_color=theme['sidebar_bg'], corner_radius=12)
        
        # Başlık
        title = ctk.CTkLabel(
            panel,
            text="📚 Örnekler ve Kaynaklar",
            font=("Segoe UI", 18, "bold"),
            text_color=theme['fg']
        )
        title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Örnek projeler
        examples = [
            ("🎯 Temel Sözdizimi", "Değişkenler, döngüler ve fonksiyonlar"),
            ("🎨 Nesne Yönelimli", "Sınıflar ve kalıtım örnekleri"),
            ("📊 Veri İşleme", "Listeler ve dosya işlemleri"),
            ("🌐 Ağ İşlemleri", "HTTP istekleri ve API kullanımı"),
        ]
        
        for icon_text, desc in examples:
            example_frame = ctk.CTkFrame(panel, fg_color=theme['bg'], corner_radius=8)
            example_frame.pack(fill="x", padx=20, pady=5)
            
            example_btn = ctk.CTkButton(
                example_frame,
                text=icon_text,
                command=lambda t=icon_text: self.open_example(t),
                fg_color="transparent",
                hover_color=theme['hover'],
                text_color=theme['accent'],
                font=("Segoe UI", 12, "bold"),
                height=35,
                anchor="w"
            )
            example_btn.pack(fill="x", padx=10, pady=(8, 2))
            
            desc_label = ctk.CTkLabel(
                example_frame,
                text=desc,
                font=("Segoe UI", 10),
                text_color=theme['comment']
            )
            desc_label.pack(anchor="w", padx=10, pady=(0, 8))
        
        # Dokümantasyon
        docs_frame = ctk.CTkFrame(panel, fg_color="transparent")
        docs_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        docs_label = ctk.CTkLabel(
            docs_frame,
            text="📖 Dokümantasyon",
            font=("Segoe UI", 14, "bold"),
            text_color=theme['fg']
        )
        docs_label.pack(anchor="w", pady=(0, 10))
        
        doc_links = [
            "📘 Dil Referansı",
            "🎓 Öğretici",
            "💡 Örnekler",
        ]
        
        for link_text in doc_links:
            link_btn = ctk.CTkButton(
                docs_frame,
                text=link_text,
                fg_color="transparent",
                hover_color=theme['hover'],
                text_color=theme['comment'],
                font=("Segoe UI", 11),
                height=25,
                anchor="w"
            )
            link_btn.pack(fill="x", pady=2)
        
        return panel
    
    def get_recent_files(self):
        """Son açılan dosyaları getir"""
        recent_file = Path.home() / ".gumusdil" / "recent.json"
        if recent_file.exists():
            try:
                with open(recent_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('files', [])
            except:
                pass
        return []
    
    def execute_and_close(self, callback):
        """Callback çalıştır ve pencereyi kapat"""
        self.destroy()
        if callback:
            callback()
    
    def open_recent(self, file_path):
        """Son dosyayı aç"""
        self.destroy()
        if self.callbacks.get('open_file_path'):
            self.callbacks['open_file_path'](file_path)
    
    def open_example(self, example_name):
        """Örnek dosyayı aç"""
        from ..config import PROJECT_ROOT
        
        # Örnek ismine göre dosya eşleştirmesi
        example_files = {
            "🎯 Temel Sözdizimi": "examples/01_selam.tr",
            "🎨 Nesne Yönelimli": "examples/11_hesap_makinesi.tr",  # OOP örneği
            "📊 Veri İşleme": "examples/08_metin_ters.tr",  # String işleme
            "🌐 Ağ İşlemleri": "test_ag_seri.tr",
        }
        
        file_path = example_files.get(example_name)
        
        if file_path:
            full_path = PROJECT_ROOT / file_path
            if full_path.exists():
                self.destroy()
                if self.callbacks.get('open_file_path'):
                    self.callbacks['open_file_path'](str(full_path))
            else:
                # Dosya yoksa examples klasöründen uygun bir dosya bul
                self._open_fallback_example(example_name)
        else:
            self.destroy()
    
    def _open_fallback_example(self, example_name):
        """Yedek örnek dosya aç"""
        from ..config import PROJECT_ROOT
        
        examples_dir = PROJECT_ROOT / "examples"
        if not examples_dir.exists():
            self.destroy()
            return
        
        # Kategori ismine göre uygun dosya seç
        fallback_map = {
            "🎯 Temel Sözdizimi": ["01_selam.tr", "02_vki.tr", "03_tek_cift.tr"],
            "🎨 Nesne Yönelimli": ["11_hesap_makinesi.tr", "07_ogrenci_not.tr"],
            "📊 Veri İşleme": ["08_metin_ters.tr", "09_sesli_harf.tr", "06_carpim_tablosu.tr"],
            "🌐 Ağ İşlemleri": ["10_sezar_sifre.tr", "04_asal_sayilar.tr"],
        }
        
        fallback_files = fallback_map.get(example_name, [])
        
        for filename in fallback_files:
            file_path = examples_dir / filename
            if file_path.exists():
                self.destroy()
                if self.callbacks.get('open_file_path'):
                    self.callbacks['open_file_path'](str(file_path))
                return
        
        # Hiçbiri yoksa ilk .tr dosyasını aç
        example_files_list = list(examples_dir.glob("*.tr"))
        if example_files_list:
            self.destroy()
            if self.callbacks.get('open_file_path'):
                self.callbacks['open_file_path'](str(example_files_list[0]))
        else:
            self.destroy()

    
    def animate_entrance(self):
        """Giriş animasyonu"""
        self.attributes('-alpha', 0.0)
        self.alpha = 0.0
        self.fade_in()
    
    def fade_in(self):
        """Fade in efekti"""
        self.alpha += 0.1
        if self.alpha < 1.0:
            self.attributes('-alpha', self.alpha)
            self.after(20, self.fade_in)
        else:
            self.attributes('-alpha', 1.0)

