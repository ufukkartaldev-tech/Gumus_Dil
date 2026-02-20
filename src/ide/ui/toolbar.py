import customtkinter as ctk
import tkinter as tk

class ToolBar(ctk.CTkFrame):
    """Ana Araç Çubuğu (Toolbar)"""
    
    def __init__(self, parent, main_window, config, **kwargs):
        super().__init__(parent, height=50, corner_radius=0, border_width=1, **kwargs)
        self.main_window = main_window
        self.config = config
        
        self.apply_theme()
        self.pack_propagate(False) # Yüksekliği koru
        
        self.setup_buttons()
        
    def apply_theme(self):
        theme = self.config.THEMES[self.config.theme]
        self.configure(fg_color=theme['sidebar_bg'], border_color=theme['border'])
        
    def setup_buttons(self):
        theme = self.config.THEMES[self.config.theme]
        
        # --- Sol Taraftaki Butonlar ---
        
        # Çalıştır Butonu
        self.run_btn = ctk.CTkButton(
            self, 
            text="▶ ÇALIŞTIR (F5)", 
            command=self.main_window.run_code,
            fg_color="#2ea043", # GitHub Green
            hover_color="#3fb950",
            font=("Segoe UI", 12, "bold"),
            width=140,
            height=32,
            corner_radius=4
        )
        self.run_btn.pack(side="left", padx=(15, 5), pady=8)

        # Durdur Butonu
        self.stop_btn = ctk.CTkButton(
            self, 
            text="🛑 DURDUR (Shift+F5)", 
            command=self.main_window.stop_code,
            fg_color="#da3633", # GitHub Red
            hover_color="#f85149",
            font=("Segoe UI", 12, "bold"),
            width=160,
            height=32,
            state="disabled",
            corner_radius=4
        )
        self.stop_btn.pack(side="left", padx=5, pady=8)

        # Ayırıcı
        ctk.CTkLabel(self, text="|", text_color=theme['border']).pack(side="left", padx=10)

        # Temizle Butonu
        self.clear_btn = ctk.CTkButton(
            self, 
            text="🧹 Temizle", 
            command=lambda: self.main_window.terminal.clear() if hasattr(self.main_window, 'terminal') else None,
            fg_color="transparent",
            hover_color=theme['hover'],
            text_color=theme['fg'],
            width=80,
            height=32,
            corner_radius=4
        )
        self.clear_btn.pack(side="left", padx=5, pady=8)

        # Kaydet Butonu
        self.save_btn = ctk.CTkButton(
            self, 
            text="💾 Kaydet", 
            command=self.main_window.save_file,
            fg_color="transparent",
            hover_color=theme['hover'],
            text_color=theme['fg'],
            width=80,
            height=32,
            corner_radius=4
        )
        self.save_btn.pack(side="left", padx=5, pady=8)

        # Düzenle (Format) Butonu
        self.format_btn = ctk.CTkButton(
            self, 
            text="✨ Düzenle", 
            command=self.main_window.format_code,
            fg_color="transparent",
            hover_color=theme['hover'],
            text_color=theme['fg'],
            width=80,
            height=32,
            corner_radius=4
        )
        self.format_btn.pack(side="left", padx=5, pady=8)
        
        # Ayırıcı
        ctk.CTkLabel(self, text="|", text_color=theme['border']).pack(side="left", padx=10)
        
        # Debug Control Placeholder (Sağ taraf)
        self.debug_placeholder = ctk.CTkFrame(self, fg_color="transparent")
        self.debug_placeholder.pack(side="right", padx=10, pady=8)
        
    def set_run_state(self, is_running):
        """Butonların durumunu güncelle"""
        if is_running:
            self.run_btn.configure(state="disabled", fg_color="#1a7f37")
            self.stop_btn.configure(state="normal")
        else:
            self.run_btn.configure(state="normal", fg_color="#2ea043")
            self.stop_btn.configure(state="disabled")

