import customtkinter as ctk
import tkinter as tk

class ThemeSelectorV2(ctk.CTkToplevel):
    def __init__(self, main_window, config):
        super().__init__(main_window.root)
        self.main_window = main_window
        self.config = config
        self.theme = config.THEMES[config.theme]
        
        self.title("🎨 GümüşDil Tema Galerisi")
        self.geometry("700x550")
        self.resizable(False, False)
        self.attributes('-alpha', 0.98) # Hafif Glassmorphism Efekti
        
        # Ekranın tam ortasına hizala
        self.update_idletasks()
        try:
            x = self.main_window.root.winfo_x() + (self.main_window.root.winfo_width() // 2) - 350
            y = self.main_window.root.winfo_y() + (self.main_window.root.winfo_height() // 2) - 275
            self.geometry(f"+{x}+{y}")
        except:
            pass
            
        self.transient(self.main_window.root)
        self.grab_set()
        
        self.configure(fg_color=self.theme['bg'])
        self.setup_ui()

    def setup_ui(self):
        # Üst Başlık Şeridi (Header)
        header_frame = ctk.CTkFrame(self, fg_color=self.theme['sidebar_bg'], corner_radius=0, height=80)
        header_frame.pack(fill="x", side="top")
        
        title_lbl = ctk.CTkLabel(header_frame, text="🎨 Tema Galerisi", font=("Segoe UI", 24, "bold"), text_color=self.theme['accent'])
        title_lbl.pack(pady=(15, 0))
        
        subtitle_lbl = ctk.CTkLabel(header_frame, text="GümüşDil daktilonuzun ruhunu ve renklerini yansıtın.", font=("Segoe UI", 12), text_color=self.theme['comment'])
        subtitle_lbl.pack(pady=(0, 15))
        
        # Temaların Listeleneceği Izgara/Kaydırma Alanı
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Grid Yapısında (2 sütunlu) listelemek için scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(body_frame, fg_color="transparent", corner_radius=0)
        self.scroll_frame.pack(fill="both", expand=True)
        
        # Sütun ayarları
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(1, weight=1)
        
        row, col = 0, 0
        for theme_key, theme_data in self.config.THEMES.items():
            self._create_theme_card(self.scroll_frame, theme_key, theme_data, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

    def _create_theme_card(self, parent, theme_key, theme_data, row, col):
        is_selected = (theme_key == self.config.theme)
        
        # Şık Kart (Card) Tasarımı
        card = ctk.CTkFrame(
            parent,
            fg_color=theme_data.get('editor_bg', '#1e1e1e'),
            corner_radius=12,
            border_width=2 if is_selected else 1,
            border_color=theme_data.get('accent', '#ffffff') if is_selected else self.theme['border']
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Tıklanabilir hover efekti
        def on_enter(e, c=card, sel=is_selected, h_color=theme_data.get('accent')):
            if not sel: c.configure(border_width=1, border_color=h_color)
            
        def on_leave(e, c=card, sel=is_selected):
            if not sel: c.configure(border_width=1, border_color=self.theme['border'])
            
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        card.bind("<Button-1>", lambda e: self.apply_then_close(theme_key))
        
        # Tema İsmi
        name_lbl = ctk.CTkLabel(card, text=theme_data.get('name', theme_key), font=("Segoe UI", 16, "bold"), text_color=theme_data.get('fg', '#ffffff'))
        name_lbl.pack(pady=(15, 5))
        name_lbl.bind("<Button-1>", lambda e: self.apply_then_close(theme_key))
        
        # Mini Renk Paleti (Önizleme)
        palette_frame = ctk.CTkFrame(card, fg_color="transparent")
        palette_frame.pack(pady=10)
        palette_frame.bind("<Button-1>", lambda e: self.apply_then_close(theme_key))
        
        preview_colors = [
            theme_data.get('keyword', '#569cd6'),
            theme_data.get('string', '#ce9178'),
            theme_data.get('function', '#dcdcaa'),
            theme_data.get('comment', '#6a9955')
        ]
        
        for c_hex in preview_colors:
            color_dot = ctk.CTkFrame(palette_frame, width=16, height=16, corner_radius=8, fg_color=c_hex)
            color_dot.pack(side="left", padx=4)
            color_dot.bind("<Button-1>", lambda e: self.apply_then_close(theme_key))
            
        # Seç Butonu veya Etiketi
        if is_selected:
            status_lbl = ctk.CTkLabel(card, text="✓ Aktif Tema", font=("Segoe UI", 12, "bold"), text_color=theme_data.get('accent', '#ffffff'))
            status_lbl.pack(pady=(5, 15))
            status_lbl.bind("<Button-1>", lambda e: self.apply_then_close(theme_key))
        else:
            select_btn = ctk.CTkButton(
                card, 
                text="Uygula", 
                width=100, 
                height=28,
                fg_color=self.theme['sidebar_bg'],
                hover_color=theme_data.get('accent', '#ffffff'),
                border_width=1,
                border_color=self.theme['border'],
                command=lambda: self.apply_then_close(theme_key)
            )
            select_btn.pack(pady=(5, 15))

    def apply_then_close(self, theme_key):
        # DialogManager içindeki asıl tema değiştiriciyi tetikle
        import sys
        
        # Parent yapısı üzerinden DialogManager'ın apply_theme fonksiyonuna ulaşmamız lazım
        # main_window içinde theme değişimini genelde DialogManager yapar
        if hasattr(self.main_window, 'dialog_manager'):
             self.main_window.dialog_manager.apply_theme(theme_key, None)
             
        self.destroy()
