# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk
from .game_view import GameView

class VoxelEditor(ctk.CTkFrame):
    """3D Sahne Editörü - Sürükle Bırak Voxel İnşası"""
    def __init__(self, parent, config):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.theme = config.THEMES[config.theme]
        
        self.selected_type = 1 # Varsayılan: Çimen
        self.editor_mode = "add" # add, delete
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Sol Araç Çubuğu (Toolbox)
        self.toolbox = ctk.CTkFrame(self, width=120, fg_color=self.theme['sidebar_bg'], corner_radius=12, border_width=1, border_color=self.theme['border'])
        self.toolbox.pack(side="left", fill="y", padx=(10, 5), pady=10)
        self.toolbox.pack_propagate(False)
        
        ctk.CTkLabel(self.toolbox, text="🧱 BLOKLAR", font=("Segoe UI", 12, "bold"), text_color=self.theme['accent']).pack(pady=10)
        
        # Blok Tipleri
        self.blocks = [
            (1, "🌿 Çimen", "#66bb6a"),
            (2, "🪨 Taş", "#90a4ae"),
            (3, "💧 Su", "#42a5f5"),
            (4, "🪵 Odun", "#ffa726"),
            (5, "🧱 Tuğla", "#ef5350")
        ]
        
        self.block_buttons = {}
        for b_id, b_name, b_color in self.blocks:
            btn = ctk.CTkButton(
                self.toolbox, 
                text=b_name, 
                width=100, 
                height=32,
                fg_color="transparent",
                border_width=1,
                border_color=b_color,
                text_color=self.theme['fg'],
                hover_color=self.theme['hover'],
                command=lambda bid=b_id: self.select_block(bid)
            )
            btn.pack(pady=3, padx=10)
            self.block_buttons[b_id] = btn
            
        self.select_block(1) # Başlangıç seçimi
        
        ctk.CTkLabel(self.toolbox, text="🛠️ ARAÇLAR", font=("Segoe UI", 12, "bold"), text_color=self.theme['accent']).pack(pady=(20, 10))
        
        self.add_mode_btn = ctk.CTkButton(self.toolbox, text="➕ Ekle", width=100, height=32, fg_color=self.theme['accent'], command=lambda: self.set_mode("add"))
        self.add_mode_btn.pack(pady=3)
        
        self.del_mode_btn = ctk.CTkButton(self.toolbox, text="🧹 Sil", width=100, height=32, fg_color="transparent", border_width=1, command=lambda: self.set_mode("delete"))
        self.del_mode_btn.pack(pady=3)

        self.export_btn = ctk.CTkButton(self.toolbox, text="💎 Koda Aktar", width=100, height=32, fg_color="#9c27b0", command=self.export_to_code)
        self.export_btn.pack(side="bottom", pady=20)

        # Ana Sahne (GameView)
        self.scene_container = ctk.CTkFrame(self, fg_color=self.theme['bg'], corner_radius=12, border_width=1, border_color=self.theme['border'])
        self.scene_container.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        self.game_view = GameView(self.scene_container, self.config)
        self.game_view.pack(fill="both", expand=True)
        
        # Grid üzerine tıklama olayını yakalayalım
        self.game_view.canvas.bind("<Button-3>", self.on_canvas_right_click) # Sağ tık -> İnşa/Yıkım
        
        self.game_view.info_label.configure(text="🎮 Editör: Sağ tıkla inşa et, sürükleyerek gez!")

    def select_block(self, b_id):
        self.selected_type = b_id
        for bid, btn in self.block_buttons.items():
            if bid == b_id:
                btn.configure(fg_color=self.theme['select_bg'])
            else:
                btn.configure(fg_color="transparent")

    def set_mode(self, mode):
        self.editor_mode = mode
        if mode == "add":
            self.add_mode_btn.configure(fg_color=self.theme['accent'])
            self.del_mode_btn.configure(fg_color="transparent")
        else:
            self.add_mode_btn.configure(fg_color="transparent")
            self.del_mode_btn.configure(fg_color=self.theme['accent'])

    def on_canvas_right_click(self, event):
        """Tıklanan koordinatı izometrik dünyaya çevir (Basitleştirilmiş Ters Projeksiyon)"""
        # Hassas ters projeksiyon matematiksel olarak karmaşıktır, 
        # burada kaba bir grid tahmini yapıyoruz.
        
        w = self.game_view.canvas.winfo_width() / 2
        h = self.game_view.canvas.winfo_height() / 2
        
        # Offsetleri çıkar
        rel_x = event.x - (w + self.game_view.offset_x)
        rel_y = event.y - (h + self.game_view.offset_y)
        
        # Izometrik grid tahmini (basitleştirilmiş)
        # sx = (x - z) * mw
        # sy = (x + z) * mh
        # x-z = rel_x / mw
        # x+z = rel_y / mh
        
        mw = self.game_view.block_width
        mh = self.game_view.block_height
        
        xz_diff = rel_x / mw
        xz_sum = rel_y / mh
        
        vx = int((xz_sum + xz_diff) / 2)
        vz = int((xz_sum - xz_diff) / 2)
        vy = 0 # Şimdilik sadece zemine inşa
        
        # Blok ekle/sil
        import json
        if self.editor_mode == "add":
            cmd = {"islem": "ekle", "x": vx, "y": vy, "z": vz, "tip": self.selected_type}
        else:
            cmd = {"islem": "sil", "x": vx, "y": vy, "z": vz}
            
        self.game_view.process_command(json.dumps(cmd))

    def export_to_code(self):
        """Sahnedeki voxel verilerini GümüşDil koduna çevirir"""
        if not self.game_view.voxels:
            return
            
        code = "dahil_et grafik_3d\n\ngrafik_3d.temizle()\n\n"
        for (x, y, z), tip in self.game_view.voxels.items():
            code += f"grafik_3d.blok_ekle(x={x}, y={y}, z={z}, tip={tip})\n"
            
        code += "\ngrafik_3d.sahneyi_göster()"
        
        # Ana pencereye bu kodu gönder
        if hasattr(self.master, 'callbacks') and 'on_apply_code' in self.master.callbacks:
            self.master.callbacks['on_apply_code'](code)
            self.game_view.info_label.configure(text="✅ Dünya GümüşDil koduna aktarıldı!")
