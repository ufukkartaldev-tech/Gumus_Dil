# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk
import random

class VizyonPanel(ctk.CTkFrame):
    """Gümüş Vizyon - İHA Takip ve Kontrol Merkezi"""
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.theme = config.THEMES[config.theme]
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Üst Panel: Telemetri Verileri
        self.telemetry_frame = ctk.CTkFrame(self, height=100, fg_color=self.theme['sidebar_bg'], corner_radius=12, border_width=1, border_color=self.theme['border'])
        self.telemetry_frame.pack(fill="x", padx=10, pady=10)
        self.telemetry_frame.pack_propagate(False)
        
        # Telemetri Başlıkları
        cols = ["🛸 İrtifa", "🚀 Hız", "🔋 Batarya", "📡 Sinyal"]
        self.metrics = {}
        
        for i, col in enumerate(cols):
            f = ctk.CTkFrame(self.telemetry_frame, fg_color="transparent")
            f.pack(side="left", expand=True, fill="both")
            
            ctk.CTkLabel(f, text=col, font=("Segoe UI", 10, "bold"), text_color=self.theme['comment']).pack(pady=(15, 0))
            val_lbl = ctk.CTkLabel(f, text="--", font=("Consolas", 18, "bold"), text_color=self.theme['accent'])
            val_lbl.pack()
            self.metrics[col] = val_lbl
            
        # Ana İçerik Kapasitesi
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
        
        # Sol Taraf: Radar
        self.radar_frame = ctk.CTkFrame(self.content_frame, fg_color=self.theme['bg'], corner_radius=12, border_width=1, border_color=self.theme['border'])
        self.radar_frame.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=(0, 10))
        
        ctk.CTkLabel(self.radar_frame, text="📡 CANLI RADAR", font=("Segoe UI", 11, "bold"), text_color=self.theme['accent']).pack(pady=5)
        
        self.radar_canvas = tk.Canvas(self.radar_frame, bg="#0a1a0a", highlightthickness=0, bd=0)
        self.radar_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        this = self
        self.radar_canvas.bind("<Configure>", lambda e: this._draw_radar_static())
        
        # Sağ Taraf: Kontrol ve Loglar
        self.right_frame = ctk.CTkFrame(self.content_frame, width=200, fg_color="transparent")
        self.right_frame.pack(side="right", fill="both", padx=(5, 10), pady=(0, 10))
        
        # Kontrol Butonları
        self.ctrl_frame = ctk.CTkFrame(self.right_frame, fg_color=self.theme['sidebar_bg'], corner_radius=12, border_width=1, border_color=self.theme['border'])
        self.ctrl_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.ctrl_frame, text="🎮 KONTROL", font=("Segoe UI", 11, "bold")).pack(pady=5)
        
        buttons = [
            ("🛫 Kalkış Yap", self.cmd_takeoff),
            ("🛰️ Devriye At", self.cmd_patrol),
            ("🏠 Eve Dön", self.cmd_rtl),
            ("🛬 İniş Yap", self.cmd_land)
        ]
        
        for text, cmd in buttons:
            btn = ctk.CTkButton(self.ctrl_frame, text=text, height=32, fg_color="transparent", border_width=1, border_color=self.theme['border'], hover_color=self.theme['hover'], command=cmd)
            btn.pack(fill="x", padx=10, pady=3)
            
        # Log Kayıtları
        self.log_frame = ctk.CTkFrame(self.right_frame, fg_color=self.theme['sidebar_bg'], corner_radius=12, border_width=1, border_color=self.theme['border'])
        self.log_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(self.log_frame, text="📜 SİSTEM GÜNLÜĞÜ", font=("Segoe UI", 11, "bold")).pack(pady=5)
        self.log_box = ctk.CTkTextbox(self.log_frame, font=("Consolas", 10), fg_color="transparent", text_color=self.theme['comment'])
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_box.insert("end", "[SİSTEM] Beklemede...\n")
        self.log_box.configure(state="disabled")

    def _draw_radar_static(self):
        self.radar_canvas.delete("all")
        w = self.radar_canvas.winfo_width()
        h = self.radar_canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        # Radar Halkaları
        for r in [40, 80, 120, 160]:
            self.radar_canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#1a3a1a", width=1)
            
        # Eksenler
        self.radar_canvas.create_line(0, cy, w, cy, fill="#1a3a1a")
        self.radar_canvas.create_line(cx, 0, cx, h, fill="#1a3a1a")
        
        # Tarama Çizgisi (Simüle)
        self.radar_canvas.create_line(cx, cy, cx+150, cy-50, fill="#00ff00", width=2, dash=(4, 4))
        
        # Sahte Hedefler
        for _ in range(3):
            tx = cx + random.randint(-150, 150)
            ty = cy + random.randint(-150, 150)
            self.radar_canvas.create_oval(tx-3, ty-3, tx+3, ty+3, fill="#00ff00")

    def add_log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"> {text}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def update_metrics(self, alt, speed, bat, signal):
        self.metrics["🛸 İrtifa"].configure(text=f"{alt} m")
        self.metrics["🚀 Hız"].configure(text=f"{speed} km/s")
        self.metrics["🔋 Batarya"].configure(text=f"%{bat}")
        self.metrics["📡 Sinyal"].configure(text=f"{signal} dBm")

    # Komut Generating Methods
    def cmd_takeoff(self):
        code = "dahil_et robotik\n\nyazdır(\"🌐 İHA Sistemleri Bağlanıyor...\")\nrobotik.kalkış_hazırlığı()\nrobotik.irtifa_set(100)\nyazdır(\"🛫 Kalkış tamamlandı.\")"
        self._apply(code, "Milli İHA havalanıyor!")

    def cmd_patrol(self):
        code = "döngü (sayac < 4) {\n    robotik.ilerle(50)\n    robotik.sağa_dön(90)\n    yazdır(\"📡 Devriye noktası tarandı.\")\n}"
        self._apply(code, "Devriye görevi başlatıldı.")

    def cmd_rtl(self):
        code = "robotik.eve_dön()\nyazdır(\"🏠 Merkeze dönüş başladı.\")"
        self._apply(code, "Geri dönüş rotası çizildi.")

    def cmd_land(self):
        code = "robotik.iniş_modu()\nrobotik.motor_kapat()\nyazdır(\"🛬 Güvenli iniş yapıldı.\")"
        self._apply(code, "İniş prosedürü devrede.")

    def _apply(self, code, log):
        self.add_log(log)
        if hasattr(self.master, 'callbacks') and 'on_apply_code' in self.master.callbacks:
            self.master.callbacks['on_apply_code'](code)
