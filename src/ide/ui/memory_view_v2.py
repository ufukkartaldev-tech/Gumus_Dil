# -*- coding: utf-8 -*-
"""
GÜMÜŞHAFİZA V2.0 - Modern Bellek Görselleştirici
Tamamen yeniden tasarlandı: Glassmorphism + Neon + Sezgisel UX
"""

import customtkinter as ctk
import tkinter as tk
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable

class MemoryCard(ctk.CTkFrame):
    """
    Tek bir değişkeni temsil eden modern kart
    """
    def __init__(self, parent, var_name: str, var_value: str, var_type: str, 
                 address: str, theme: dict, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.var_name = var_name
        self.var_value = var_value
        self.var_type = var_type
        self.address = address
        self.theme = theme
        self.is_watched = False
        
        # Tip bazlı renk paleti
        type_colors = {
            "int": "#60a5fa",      # Mavi
            "float": "#34d399",    # Yeşil
            "string": "#fbbf24",   # Sarı
            "bool": "#a78bfa",     # Mor
            "list": "#f472b6",     # Pembe
            "map": "#fb923c",      # Turuncu
            "class": "#c084fc",    # Lavanta
            "null": "#6b7280"      # Gri
        }
        
        self.accent_color = type_colors.get(var_type.lower(), "#64748b")
        
        # Ana kart container (Glassmorphism)
        self.configure(
            fg_color=("gray90", "#1a1a1a"),
            corner_radius=12,
            border_width=2,
            border_color=self.accent_color
        )
        
        # Üst başlık (Değişken adı + Tip)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(10, 5))
        
        # Sol: Değişken adı
        name_label = ctk.CTkLabel(
            header,
            text=f"💎 {var_name}",
            font=("Segoe UI", 14, "bold"),
            text_color=self.accent_color,
            anchor="w"
        )
        name_label.pack(side="left")
        
        # Sağ: Tip badge
        type_badge = ctk.CTkLabel(
            header,
            text=var_type.upper(),
            font=("Consolas", 9, "bold"),
            text_color="white",
            fg_color=self.accent_color,
            corner_radius=6,
            padx=8,
            pady=2
        )
        type_badge.pack(side="right")
        
        # Değer gösterimi (Büyük ve belirgin)
        value_display = str(var_value)
        if len(value_display) > 50:
            value_display = value_display[:47] + "..."
            
        value_label = ctk.CTkLabel(
            self,
            text=value_display,
            font=("Consolas", 16, "bold"),
            text_color=("gray10", "gray90"),
            wraplength=280
        )
        value_label.pack(padx=12, pady=(5, 10))
        
        # Alt bilgi çubuğu (Adres + Aksiyonlar)
        footer = ctk.CTkFrame(self, fg_color=("gray85", "#252525"), corner_radius=8)
        footer.pack(fill="x", padx=8, pady=(0, 8))
        
        # Adres chip
        addr_chip = ctk.CTkLabel(
            footer,
            text=f"📍 {address}",
            font=("Consolas", 9),
            text_color=("gray30", "gray60"),
            padx=8,
            pady=4
        )
        addr_chip.pack(side="left", padx=5, pady=5)
        
        # Takip butonu (Yıldız)
        self.watch_btn = ctk.CTkButton(
            footer,
            text="☆",
            width=30,
            height=24,
            font=("Segoe UI", 14),
            fg_color="transparent",
            hover_color=("gray75", "#333333"),
            command=self.toggle_watch
        )
        self.watch_btn.pack(side="right", padx=5, pady=5)
        
        # Hover efekti
        self.bind("<Enter>", self._on_hover_enter)
        self.bind("<Leave>", self._on_hover_leave)
        
    def toggle_watch(self):
        """Takip durumunu değiştir"""
        self.is_watched = not self.is_watched
        if self.is_watched:
            self.watch_btn.configure(text="⭐", fg_color=self.accent_color)
            self.configure(border_width=3)
        else:
            self.watch_btn.configure(text="☆", fg_color="transparent")
            self.configure(border_width=2)
            
    def update_value(self, new_value: str):
        """Değeri güncelle ve animasyon göster"""
        self.var_value = new_value
        # Flash animasyonu
        self._flash_update()
        
    def _flash_update(self):
        """Değer değiştiğinde yanıp sönen efekt"""
        original_border = self.cget("border_color")
        self.configure(border_color="#00ff00", border_width=4)
        self.after(300, lambda: self.configure(border_color=original_border, border_width=2))
        
    def _on_hover_enter(self, event):
        """Mouse üzerine geldiğinde"""
        self.configure(border_width=3)
        
    def _on_hover_leave(self, event):
        """Mouse ayrıldığında"""
        if not self.is_watched:
            self.configure(border_width=2)


class MemoryViewV2(ctk.CTkFrame):
    """
    GümüşHafıza V2.0 - Modern Bellek Görselleştirici
    """
    def __init__(self, parent, config, on_jump: Optional[Callable] = None, 
                 on_ask_ai: Optional[Callable] = None):
        super().__init__(parent, fg_color="transparent")
        
        self.config = config
        self.on_jump = on_jump
        self.on_ask_ai = on_ask_ai
        self.theme = config.THEMES[config.theme]
        
        # Veri yapıları
        self.history: List[dict] = []
        self.current_step = 0
        self.memory_cards: Dict[str, MemoryCard] = {}
        
        self._setup_ui()
        
    def _setup_ui(self):
        """UI bileşenlerini oluştur"""
        
        # ============================================================
        # ÜST PANEL: Kontroller ve Bilgi
        # ============================================================
        top_panel = ctk.CTkFrame(
            self,
            fg_color=self.theme["sidebar_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.theme["border"]
        )
        top_panel.pack(fill="x", padx=10, pady=10)
        
        # Başlık
        title_frame = ctk.CTkFrame(top_panel, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            title_frame,
            text="🧠 GÜMÜŞHAFİZA",
            font=("Segoe UI", 18, "bold"),
            text_color=self.theme["accent"]
        ).pack(side="left")
        
        # Durum badge
        self.status_badge = ctk.CTkLabel(
            title_frame,
            text="⚪ HAZIR",
            font=("Segoe UI", 10, "bold"),
            text_color="white",
            fg_color="#6b7280",
            corner_radius=12,
            padx=12,
            pady=4
        )
        self.status_badge.pack(side="right")
        
        # Kontrol çubuğu
        control_bar = ctk.CTkFrame(top_panel, fg_color="transparent")
        control_bar.pack(fill="x", padx=15, pady=(5, 10))
        
        # Sol: Oynatma kontrolleri
        play_controls = ctk.CTkFrame(control_bar, fg_color=("gray85", "#2a2a2a"), corner_radius=8)
        play_controls.pack(side="left", padx=(0, 10))
        
        # Geri butonu
        ctk.CTkButton(
            play_controls,
            text="⏮",
            width=40,
            height=32,
            font=("Segoe UI", 16),
            fg_color="transparent",
            hover_color=("gray75", "#333333"),
            command=lambda: self.step(-1)
        ).pack(side="left", padx=2, pady=5)
        
        # Oynat/Duraklat
        self.play_btn = ctk.CTkButton(
            play_controls,
            text="▶",
            width=50,
            height=32,
            font=("Segoe UI", 16),
            fg_color=self.theme["accent"],
            hover_color=self.theme["select_bg"],
            command=self.toggle_play
        )
        self.play_btn.pack(side="left", padx=2, pady=5)
        
        # İleri butonu
        ctk.CTkButton(
            play_controls,
            text="⏭",
            width=40,
            height=32,
            font=("Segoe UI", 16),
            fg_color="transparent",
            hover_color=("gray75", "#333333"),
            command=lambda: self.step(1)
        ).pack(side="left", padx=2, pady=5)
        
        # Orta: Zaman çizelgesi (Timeline slider)
        timeline_frame = ctk.CTkFrame(control_bar, fg_color="transparent")
        timeline_frame.pack(side="left", fill="x", expand=True, padx=10)
        
        self.step_label = ctk.CTkLabel(
            timeline_frame,
            text="Adım: 0 / 0",
            font=("Consolas", 11, "bold"),
            text_color=self.theme["comment"]
        )
        self.step_label.pack(anchor="w")
        
        self.timeline_slider = ctk.CTkSlider(
            timeline_frame,
            from_=0,
            to=1,
            width=300,
            height=16,
            button_color=self.theme["accent"],
            button_hover_color=self.theme["select_bg"],
            progress_color=self.theme["accent"],
            command=self._on_slider_change
        )
        self.timeline_slider.set(0)
        self.timeline_slider.pack(fill="x", pady=(2, 0))
        
        # Sağ: Araçlar
        tools_frame = ctk.CTkFrame(control_bar, fg_color=("gray85", "#2a2a2a"), corner_radius=8)
        tools_frame.pack(side="right")
        
        # Snapshot butonu
        ctk.CTkButton(
            tools_frame,
            text="📸",
            width=40,
            height=32,
            font=("Segoe UI", 16),
            fg_color="transparent",
            hover_color=("gray75", "#333333"),
            command=self.take_snapshot
        ).pack(side="left", padx=2, pady=5)
        
        # AI Analiz butonu
        if self.on_ask_ai:
            ctk.CTkButton(
                tools_frame,
                text="🤖",
                width=40,
                height=32,
                font=("Segoe UI", 16),
                fg_color="transparent",
                hover_color=("gray75", "#333333"),
                command=self.ask_ai_analysis
            ).pack(side="left", padx=2, pady=5)
        
        # Temizle butonu
        ctk.CTkButton(
            tools_frame,
            text="🗑️",
            width=40,
            height=32,
            font=("Segoe UI", 16),
            fg_color="transparent",
            hover_color=("gray75", "#333333"),
            command=self.clear_history
        ).pack(side="left", padx=2, pady=5)
        
        # ============================================================
        # ORTA PANEL: İstatistikler (Mini Dashboard)
        # ============================================================
        stats_panel = ctk.CTkFrame(
            self,
            fg_color=self.theme["sidebar_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.theme["border"],
            height=80
        )
        stats_panel.pack(fill="x", padx=10, pady=(0, 10))
        stats_panel.pack_propagate(False)
        
        # Stat kartları
        stat_container = ctk.CTkFrame(stats_panel, fg_color="transparent")
        stat_container.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Değişken sayısı
        self._create_stat_card(
            stat_container,
            "📦",
            "Değişkenler",
            "0",
            "var_count"
        ).pack(side="left", expand=True, fill="both", padx=5)
        
        # Bellek kullanımı
        self._create_stat_card(
            stat_container,
            "💾",
            "Bellek",
            "0 KB",
            "memory_usage"
        ).pack(side="left", expand=True, fill="both", padx=5)
        
        # Scope derinliği
        self._create_stat_card(
            stat_container,
            "🏗️",
            "Scope Derinliği",
            "0",
            "scope_depth"
        ).pack(side="left", expand=True, fill="both", padx=5)
        
        # ============================================================
        # ALT PANEL: Bellek Kartları (Scrollable)
        # ============================================================
        cards_label = ctk.CTkLabel(
            self,
            text="🗂️ Aktif Değişkenler",
            font=("Segoe UI", 14, "bold"),
            text_color=self.theme["fg"],
            anchor="w"
        )
        cards_label.pack(fill="x", padx=20, pady=(0, 5))
        
        self.cards_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=self.theme["editor_bg"],
            corner_radius=12
        )
        self.cards_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Boş durum mesajı
        self.empty_state = ctk.CTkFrame(
            self.cards_scroll,
            fg_color="transparent"
        )
        self.empty_state.pack(expand=True, pady=50)
        
        ctk.CTkLabel(
            self.empty_state,
            text="🎯",
            font=("Segoe UI", 48)
        ).pack()
        
        ctk.CTkLabel(
            self.empty_state,
            text="Henüz veri yok",
            font=("Segoe UI", 16, "bold"),
            text_color=self.theme["comment"]
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            self.empty_state,
            text="Kodunuzu çalıştırın ve bellek değişimlerini izleyin",
            font=("Segoe UI", 12),
            text_color=self.theme["comment"]
        ).pack()
        
    def _create_stat_card(self, parent, icon: str, label: str, value: str, key: str):
        """Mini istatistik kartı oluştur"""
        card = ctk.CTkFrame(
            parent,
            fg_color=("gray80", "#252525"),
            corner_radius=8
        )
        
        ctk.CTkLabel(
            card,
            text=icon,
            font=("Segoe UI", 24)
        ).pack(pady=(8, 0))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Consolas", 16, "bold"),
            text_color=self.theme["accent"]
        )
        value_label.pack()
        
        ctk.CTkLabel(
            card,
            text=label,
            font=("Segoe UI", 9),
            text_color=self.theme["comment"]
        ).pack(pady=(0, 8))
        
        # Referansı sakla (güncelleme için)
        setattr(self, f"stat_{key}", value_label)
        
        return card
        
    def update_memory(self, memory_json: str):
        """Bellek durumunu güncelle (C++ interpreter'dan gelen JSON)"""
        try:
            data = json.loads(memory_json)
            self.history.append(data)
            
            # Timeline'ı güncelle
            total_steps = len(self.history)
            if total_steps > 0:
                self.timeline_slider.configure(to=total_steps - 1)
                
                # Otomatik ilerle (en son adımdaysak)
                if self.current_step == total_steps - 2 or self.current_step == 0:
                    self.current_step = total_steps - 1
                    self.timeline_slider.set(self.current_step)
                    self._display_step(self.current_step)
                    
            # Durum badge'ini güncelle
            self.status_badge.configure(
                text="🟢 ÇALIŞIYOR",
                fg_color="#22c55e"
            )
            
        except Exception as e:
            print(f"❌ Bellek güncelleme hatası: {e}")
            
    def _display_step(self, step_index: int):
        """Belirli bir adımı görselleştir"""
        if step_index < 0 or step_index >= len(self.history):
            return
            
        data = self.history[step_index]
        
        # Adım bilgisini güncelle
        self.step_label.configure(
            text=f"Adım: {step_index + 1} / {len(self.history)}"
        )
        
        # Boş durum mesajını gizle
        self.empty_state.pack_forget()
        
        # Mevcut kartları temizle
        for card in self.memory_cards.values():
            card.destroy()
        self.memory_cards.clear()
        
        # Scope'ları topla (nested)
        variables = self._collect_variables(data)
        
        # Kartları oluştur
        for var_name, var_info in variables.items():
            card = MemoryCard(
                self.cards_scroll,
                var_name=var_name,
                var_value=var_info.get("value", "?"),
                var_type=var_info.get("type", "unknown"),
                address=var_info.get("address", "null"),
                theme=self.theme
            )
            card.pack(fill="x", padx=10, pady=5)
            self.memory_cards[var_name] = card
            
        # İstatistikleri güncelle
        self._update_stats(variables, data)
        
        # Kod satırına git (eğer callback varsa)
        line_no = data.get("line", 0)
        if line_no > 0 and self.on_jump:
            self.on_jump(line_no)
            
    def _collect_variables(self, scope_data: dict) -> dict:
        """Tüm scope'lardan değişkenleri topla"""
        variables = {}
        
        def traverse(scope):
            if not scope:
                return
            # Mevcut scope'taki değişkenler
            for name, info in scope.get("variables", {}).items():
                variables[name] = info
            # Parent scope'a git
            traverse(scope.get("parent"))
            
        traverse(scope_data)
        return variables
        
    def _update_stats(self, variables: dict, data: dict):
        """İstatistik kartlarını güncelle"""
        # Değişken sayısı
        var_count = len(variables)
        self.stat_var_count.configure(text=str(var_count))
        
        # Bellek kullanımı (tahmini)
        memory_kb = var_count * 8  # Basit tahmin
        self.stat_memory_usage.configure(text=f"{memory_kb} KB")
        
        # Scope derinliği
        depth = 0
        scope = data
        while scope:
            depth += 1
            scope = scope.get("parent")
        self.stat_scope_depth.configure(text=str(depth))
        
    def step(self, direction: int):
        """Adım adım ileri/geri git"""
        new_step = self.current_step + direction
        if 0 <= new_step < len(self.history):
            self.current_step = new_step
            self.timeline_slider.set(new_step)
            self._display_step(new_step)
            
    def toggle_play(self):
        """Otomatik oynatmayı başlat/durdur"""
        # TODO: Implement auto-play
        pass
        
    def _on_slider_change(self, value):
        """Timeline slider değiştiğinde"""
        step = int(value)
        if step != self.current_step:
            self.current_step = step
            self._display_step(step)
            
    def take_snapshot(self):
        """Mevcut durumun anlık görüntüsünü kaydet"""
        if self.current_step < 0 or not self.history:
            return
            
        try:
            current_data = self.history[self.current_step]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"memory_snapshot_{timestamp}.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(current_data, f, indent=2, ensure_ascii=False)
                
            print(f"✅ Snapshot kaydedildi: {filename}")
            
        except Exception as e:
            print(f"❌ Snapshot hatası: {e}")
            
    def ask_ai_analysis(self):
        """AI'dan bellek analizi iste"""
        if not self.on_ask_ai or not self.history:
            return
            
        # Mevcut durumu özet olarak hazırla
        variables = self._collect_variables(self.history[self.current_step])
        summary = f"Adım {self.current_step + 1}: {len(variables)} değişken aktif\n"
        summary += "\n".join([f"- {name}: {info.get('value', '?')}" 
                             for name, info in list(variables.items())[:5]])
        
        query = f"Bu bellek durumunu analiz et:\n{summary}"
        self.on_ask_ai(query)
        
    def clear_history(self):
        """Geçmişi temizle"""
        self.history.clear()
        self.current_step = 0
        
        # UI'yi sıfırla
        for card in self.memory_cards.values():
            card.destroy()
        self.memory_cards.clear()
        
        self.empty_state.pack(expand=True, pady=50)
        self.step_label.configure(text="Adım: 0 / 0")
        self.timeline_slider.configure(to=1)
        self.timeline_slider.set(0)
        
        # İstatistikleri sıfırla
        self.stat_var_count.configure(text="0")
        self.stat_memory_usage.configure(text="0 KB")
        self.stat_scope_depth.configure(text="0")
        
        # Durum badge
        self.status_badge.configure(
            text="⚪ HAZIR",
            fg_color="#6b7280"
        )
        
    def reset(self):
        """Tam sıfırlama (clear_history ile aynı)"""
        self.clear_history()

