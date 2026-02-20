# -*- coding: utf-8 -*-
"""
GümüşIDE Debug Panels
Variable Watch Panel & Call Stack Panel
"""

import customtkinter as ctk
import tkinter as tk
from typing import List, Dict, Any, Optional, Callable
from ..core.debugger import DebuggerManager, Variable, StackFrame


class VariableWatchPanel(ctk.CTkFrame):
    """
    Değişken Takip Paneli
    
    Özellikler:
    - Tüm değişkenleri listele
    - Değer değişikliklerini vurgula
    - Manuel değişken ekle/çıkar
    - Değişken değerlerini düzenle
    """
    
    def __init__(self, parent, debugger: DebuggerManager, config, **kwargs):
        super().__init__(parent, corner_radius=8, **kwargs)
        self.debugger = debugger
        self.config = config
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            header,
            text="🔍 Variable Watch",
            font=("Segoe UI", 14, "bold"),
            text_color="#00e676"
        ).pack(side="left")
        
        # Yenile butonu
        ctk.CTkButton(
            header,
            text="↻",
            width=30,
            height=30,
            font=("Segoe UI", 16),
            fg_color="transparent",
            hover_color="#2a2a2a",
            command=self.refresh
        ).pack(side="right", padx=2)
        
        # Değişken ekle butonu
        ctk.CTkButton(
            header,
            text="+",
            width=30,
            height=30,
            font=("Segoe UI", 16, "bold"),
            fg_color="#1e88e5",
            hover_color="#1565c0",
            command=self._add_watch_dialog
        ).pack(side="right", padx=2)
        
        # Filtre: Local / Global / Watched
        self.filter_var = tk.StringVar(value="all")
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        for label, value in [("All", "all"), ("Local", "local"), ("Global", "global"), ("⭐ Watched", "watched")]:
            ctk.CTkRadioButton(
                filter_frame,
                text=label,
                variable=self.filter_var,
                value=value,
                font=("Segoe UI", 10),
                command=self.refresh
            ).pack(side="left", padx=5)
        
        # Scrollable Variable List
        self.var_list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#1a1a1a",
            corner_radius=8
        )
        self.var_list_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        self.var_widgets: Dict[str, ctk.CTkFrame] = {}
        
    def refresh(self):
        """Değişken listesini yenile"""
        # Eski widget'ları temizle
        for widget in self.var_widgets.values():
            widget.destroy()
        self.var_widgets.clear()
        
        # Filtre uygula
        filter_mode = self.filter_var.get()
        
        if filter_mode == "watched":
            variables = self.debugger.get_watched_variables()
        else:
            variables = self.debugger.get_all_variables()
            if filter_mode != "all":
                variables = [v for v in variables if v.scope == filter_mode]
        
        # Değişkenleri göster
        for var in variables:
            self._create_variable_widget(var)

    def update_from_json(self, vars_json):
        """GümüşGöz: Canlı JSON verisinden tabloyu 'Smart Update' ile güncelle"""
        import json
        try:
            vars_data = json.loads(vars_json)
            
            # 🚀 Optimizasyon: Sadece değişenleri güncelle veya yeni ekle
            current_names = set(vars_data.keys())
            existing_names = set(self.var_widgets.keys())

            # Silinmesi gerekenler (Ekranda var ama veride yok)
            for name in existing_names - current_names:
                self.var_widgets[name].destroy()
                del self.var_widgets[name]

            for name, value in vars_data.items():
                type_name = type(value).__name__
                var = Variable(name=name, value=value, type_name=type_name, scope="global")

                if name in self.var_widgets:
                    # Mevcut widget'ı bul ve sadece değerini güncelle
                    self._update_existing_widget(name, var)
                else:
                    # Yeni widget oluştur
                    self._create_variable_widget(var)
                    
        except Exception as e:
            print(f"GümüşGöz Optimizasyon Hatası: {e}")

    def _update_existing_widget(self, name, var):
        """Widget'ı silmeden değerini ve stilini güncelle (Performans!)"""
        frame = self.var_widgets[name]
        # Entry widget'ına ulaş (Widget yapısına göre index değişebilir)
        # Widget yapımız: frame -> [left_frame, right_frame] -> [entry]
        try:
            # Right frame içindeki entry'yi bulalım
            for child in frame.winfo_children():
                if isinstance(child, ctk.CTkFrame): # right_frame veya left_frame
                    for inner in child.winfo_children():
                        if isinstance(inner, ctk.CTkEntry):
                            # Değer farklıysa güncelle
                            current_val = inner.get()
                            new_val = str(var.value)
                            if current_val != new_val:
                                inner.delete(0, tk.END)
                                inner.insert(0, new_val)
                                # Animasyon: Değiştiğini belli et
                                frame.configure(border_color="#ffd700", border_width=2)
                                self.after(500, lambda f=frame: f.configure(border_width=0))
                            break
        except:
            pass
            
    def _create_variable_widget(self, var: Variable):
        """Tek bir değişken için widget oluştur"""
        # Ana container
        var_frame = ctk.CTkFrame(
            self.var_list_frame,
            fg_color="#2a2a2a" if not var.changed else "#3d3d00",  # Değiştiyse sarı ton
            corner_radius=6,
            border_width=2,
            border_color="#ffd700" if var.changed else "transparent"
        )
        var_frame.pack(fill="x", pady=3, padx=5)
        
        # Sol: İsim ve Tip
        left_frame = ctk.CTkFrame(var_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)
        
        # İsim (scope badge ile)
        name_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        name_frame.pack(anchor="w")
        
        scope_color = "#4caf50" if var.scope == "local" else "#2196f3"
        scope_badge = ctk.CTkLabel(
            name_frame,
            text=var.scope[0].upper(),  # "L" veya "G"
            font=("Consolas", 9, "bold"),
            text_color="white",
            fg_color=scope_color,
            corner_radius=3,
            width=20,
            height=20
        )
        scope_badge.pack(side="left", padx=(0, 5))
        
        name_label = ctk.CTkLabel(
            name_frame,
            text=var.name,
            font=("Consolas", 12, "bold"),
            text_color="#00e676" if var.name in self.debugger.watched_vars else "#ffffff"
        )
        name_label.pack(side="left")
        
        # Tip
        type_label = ctk.CTkLabel(
            left_frame,
            text=f"({var.type_name})",
            font=("Consolas", 9, "italic"),
            text_color="#888888"
        )
        type_label.pack(anchor="w")
        
        # Sağ: Değer ve Kontroller
        right_frame = ctk.CTkFrame(var_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=10, pady=8)
        
        # Değer (düzenlenebilir)
        value_str = str(var.value)
        if len(value_str) > 30:
            value_str = value_str[:27] + "..."
            
        value_entry = ctk.CTkEntry(
            right_frame,
            width=150,
            height=28,
            font=("Consolas", 11),
            fg_color="#1a1a1a",
            border_color="#555555"
        )
        value_entry.insert(0, value_str)
        value_entry.pack(side="left", padx=5)
        
        # Değer değiştirme butonu
        def update_value():
            new_value = value_entry.get()
            # Tip dönüşümü (basit)
            try:
                if var.type_name == "int":
                    new_value = int(new_value)
                elif var.type_name == "float":
                    new_value = float(new_value)
                elif var.type_name == "bool":
                    new_value = new_value.lower() in ("true", "1", "yes")
                self.debugger.update_variable(var.name, new_value)
                self.refresh()
            except ValueError:
                pass  # Hatalı değer, görmezden gel
                
        ctk.CTkButton(
            right_frame,
            text="✓",
            width=30,
            height=28,
            font=("Segoe UI", 14),
            fg_color="#4caf50",
            hover_color="#388e3c",
            command=update_value
        ).pack(side="left", padx=2)
        
        # Watch toggle butonu
        is_watched = var.name in self.debugger.watched_vars
        watch_btn = ctk.CTkButton(
            right_frame,
            text="⭐" if is_watched else "☆",
            width=30,
            height=28,
            font=("Segoe UI", 14),
            fg_color="#ff9800" if is_watched else "transparent",
            hover_color="#f57c00" if is_watched else "#2a2a2a",
            command=lambda: self._toggle_watch(var.name)
        )
        watch_btn.pack(side="left", padx=2)
        
        self.var_widgets[var.name] = var_frame
        
        # Değişiklik animasyonu
        if var.changed:
            self._flash_variable(var_frame)
            
    def _flash_variable(self, frame: ctk.CTkFrame):
        """Değişken değiştiğinde flash animasyonu"""
        def reset_color():
            frame.configure(fg_color="#2a2a2a", border_color="transparent")
            
        frame.after(1000, reset_color)
        
    def _toggle_watch(self, var_name: str):
        """Değişkeni watch listesine ekle/çıkar"""
        if var_name in self.debugger.watched_vars:
            self.debugger.remove_watch(var_name)
        else:
            self.debugger.add_watch(var_name)
        self.refresh()
        
    def _add_watch_dialog(self):
        """Manuel olarak değişken ekle"""
        dialog = ctk.CTkInputDialog(
            text="Takip edilecek değişken adı:",
            title="Add Watch"
        )
        var_name = dialog.get_input()
        if var_name:
            self.debugger.add_watch(var_name)
            self.refresh()


class CallStackPanel(ctk.CTkFrame):
    """
    Çağrı Yığını Paneli
    
    Özellikler:
    - Fonksiyon çağrı zincirini göster
    - Her frame'deki değişkenleri göster
    - Tıklanabilir stack frames
    """
    
    def __init__(self, parent, debugger: DebuggerManager, config, on_frame_click: Optional[Callable[[StackFrame], None]] = None, **kwargs):
        super().__init__(parent, corner_radius=8, **kwargs)
        self.debugger = debugger
        self.config = config
        self.on_frame_click = on_frame_click
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            header,
            text="📚 Call Stack",
            font=("Segoe UI", 14, "bold"),
            text_color="#ff9800"
        ).pack(side="left")
        
        # Stack depth badge
        self.depth_badge = ctk.CTkLabel(
            header,
            text="0",
            font=("Consolas", 10, "bold"),
            text_color="white",
            fg_color="#ff5722",
            corner_radius=10,
            width=30,
            height=20
        )
        self.depth_badge.pack(side="right")
        
        # Scrollable Stack List
        self.stack_list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#1a1a1a",
            corner_radius=8
        )
        self.stack_list_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        self.stack_widgets: List[ctk.CTkFrame] = []
        
    def refresh(self):
        """Stack listesini yenile"""
        # Eski widget'ları temizle
        for widget in self.stack_widgets:
            widget.destroy()
        self.stack_widgets.clear()
        
        # Stack frame'leri getir
        stack = self.debugger.get_call_stack()
        self.depth_badge.configure(text=str(len(stack)))
        
        # En üstteki frame en üstte göster (reverse order)
        for i, frame in enumerate(reversed(stack)):
            self._create_stack_frame_widget(frame, len(stack) - i - 1)
            
    def _create_stack_frame_widget(self, frame: StackFrame, depth: int):
        """Tek bir stack frame için widget oluştur"""
        # Ana container (tıklanabilir)
        frame_widget = ctk.CTkFrame(
            self.stack_list_frame,
            fg_color="#2a2a2a" if depth > 0 else "#1e3a5f",  # En üstteki mavi
            corner_radius=6,
            border_width=2,
            border_color="#2196f3" if depth == 0 else "transparent"
        )
        frame_widget.pack(fill="x", pady=3, padx=5)
        
        # Tıklama eventi
        def on_click(event):
            if self.on_frame_click:
                self.on_frame_click(frame)
                
        frame_widget.bind("<Button-1>", on_click)
        
        # İçerik
        content_frame = ctk.CTkFrame(frame_widget, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=8)
        content_frame.bind("<Button-1>", on_click)
        
        # Depth indicator
        depth_label = ctk.CTkLabel(
            content_frame,
            text=f"#{depth}",
            font=("Consolas", 10, "bold"),
            text_color="#888888",
            width=30
        )
        depth_label.pack(side="left", padx=(0, 10))
        depth_label.bind("<Button-1>", on_click)
        
        # Fonksiyon bilgisi
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        info_frame.bind("<Button-1>", on_click)
        
        # Fonksiyon adı
        func_label = ctk.CTkLabel(
            info_frame,
            text=f"🔹 {frame.function_name}()",
            font=("Consolas", 12, "bold"),
            text_color="#00e676" if depth == 0 else "#ffffff",
            anchor="w"
        )
        func_label.pack(anchor="w")
        func_label.bind("<Button-1>", on_click)
        
        # Dosya ve satır
        location_label = ctk.CTkLabel(
            info_frame,
            text=f"📄 Line {frame.line_number}",
            font=("Consolas", 9, "italic"),
            text_color="#888888",
            anchor="w"
        )
        location_label.pack(anchor="w")
        location_label.bind("<Button-1>", on_click)
        
        # Local variables (küçük önizleme)
        if frame.local_vars:
            vars_preview = ", ".join([f"{k}={v}" for k, v in list(frame.local_vars.items())[:3]])
            if len(frame.local_vars) > 3:
                vars_preview += "..."
                
            vars_label = ctk.CTkLabel(
                info_frame,
                text=f"💾 {vars_preview}",
                font=("Consolas", 8),
                text_color="#64b5f6",
                anchor="w"
            )
            vars_label.pack(anchor="w", pady=(2, 0))
            vars_label.bind("<Button-1>", on_click)
        
        self.stack_widgets.append(frame_widget)


class DebugControlBar(ctk.CTkFrame):
    """
    Debug Kontrol Çubuğu
    
    Özellikler:
    - Play/Pause/Stop
    - Step Over/Into/Out
    - Hız kontrolü
    """
    
    def __init__(self, parent, debugger: DebuggerManager, config, **kwargs):
        super().__init__(parent, corner_radius=8, fg_color="#1a1a1a", **kwargs)
        self.debugger = debugger
        self.config = config
        
        # Sol: Execution Controls
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.pack(side="left", padx=10, pady=5)
        
        # Play/Pause
        self.play_btn = ctk.CTkButton(
            left_frame,
            text="▶",
            width=40,
            height=40,
            font=("Segoe UI", 18),
            fg_color="#4caf50",
            hover_color="#388e3c",
            command=self._toggle_play_pause
        )
        self.play_btn.pack(side="left", padx=2)
        
        # Stop
        ctk.CTkButton(
            left_frame,
            text="⏹",
            width=40,
            height=40,
            font=("Segoe UI", 18),
            fg_color="#f44336",
            hover_color="#d32f2f",
            command=self.debugger.stop
        ).pack(side="left", padx=2)
        
        # Separator
        ctk.CTkFrame(left_frame, width=2, height=30, fg_color="#444444").pack(side="left", padx=10)
        
        # Step Over (F10)
        ctk.CTkButton(
            left_frame,
            text="⤵",
            width=40,
            height=40,
            font=("Segoe UI", 18),
            fg_color="#2196f3",
            hover_color="#1976d2",
            command=self.debugger.step_over
        ).pack(side="left", padx=2)
        
        # Step Into (F11)
        ctk.CTkButton(
            left_frame,
            text="⤓",
            width=40,
            height=40,
            font=("Segoe UI", 18),
            fg_color="#2196f3",
            hover_color="#1976d2",
            command=self.debugger.step_into
        ).pack(side="left", padx=2)
        
        # Step Out (Shift+F11)
        ctk.CTkButton(
            left_frame,
            text="⤒",
            width=40,
            height=40,
            font=("Segoe UI", 18),
            fg_color="#2196f3",
            hover_color="#1976d2",
            command=self.debugger.step_out
        ).pack(side="left", padx=2)
        
        # Orta: Durum Göstergesi
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(side="left", fill="both", expand=True, padx=20)
        
        self.status_label = ctk.CTkLabel(
            center_frame,
            text="⚪ IDLE",
            font=("Segoe UI", 12, "bold"),
            text_color="#888888"
        )
        self.status_label.pack(expand=True)
        
        # Sağ: Hız Kontrolü (Gelişmiş UX)
        right_frame = ctk.CTkFrame(self, fg_color="#252525", corner_radius=6, border_width=1, border_color="#333333")
        right_frame.pack(side="right", padx=10, pady=5)
        
        # Kaplumbağa (Yavaş)
        ctk.CTkLabel(
            right_frame,
            text="🐢",
            font=("Segoe UI", 12),
        ).pack(side="left", padx=(8, 2))
        
        # Ana Slider
        self.speed_slider = ctk.CTkSlider(
            right_frame,
            from_=0.5,
            to=2.0,
            number_of_steps=15, # Daha hassas kontrol
            width=120,
            height=16,
            button_color="#00e676",
            button_hover_color="#00c853",
            progress_color="#00c853",
            command=self._on_speed_change
        )
        self.speed_slider.set(1.0)
        self.speed_slider.pack(side="left", padx=5)
        
        # Tavşan (Hızlı)
        ctk.CTkLabel(
            right_frame,
            text="🚀",
            font=("Segoe UI", 12),
        ).pack(side="left", padx=(2, 8))
        
        # Durum Etiketi (Hız Değeri)
        self.speed_label = ctk.CTkLabel(
            right_frame,
            text="1.0x",
            font=("Consolas", 11, "bold"),
            text_color="#00e676",
            width=45
        )
        self.speed_label.pack(side="right", padx=(0, 5))
        
        # Alt başlık (Açıklama) - İsteğe bağlı
        # self.speed_desc = ctk.CTkLabel(self, text="Simülasyon Aktif Hızı", font=("Segoe UI", 9), text_color="#666666")
        # self.speed_desc.place(relx=0.9, rely=0.8, anchor="e")
        
        # Debugger callback'leri
        self.debugger.on_state_change = self._on_state_change
        
    def _toggle_play_pause(self):
        """Play/Pause toggle"""
        if self.debugger.state.value in ["idle", "paused", "finished"]:
            self.debugger.continue_execution()
        else:
            self.debugger.pause()
            
    def _on_speed_change(self, value):
        """Hız değiştiğinde"""
        speed = round(value, 1)
        self.debugger.set_speed(speed)
        self.speed_label.configure(text=f"{speed}x")
        
    def _on_state_change(self, state):
        """Debugger durumu değiştiğinde UI'yi güncelle"""
        state_icons = {
            "idle": ("⚪", "#888888", "IDLE"),
            "running": ("🟢", "#4caf50", "RUNNING"),
            "paused": ("🟡", "#ff9800", "PAUSED"),
            "stepping": ("🔵", "#2196f3", "STEPPING"),
            "finished": ("⚫", "#666666", "FINISHED")
        }
        
        icon, color, text = state_icons.get(state.value, ("⚪", "#888888", "UNKNOWN"))
        self.status_label.configure(text=f"{icon} {text}", text_color=color)
        
        # Play/Pause buton güncellemesi
        if state.value in ["running", "stepping"]:
            self.play_btn.configure(text="⏸", fg_color="#ff9800")
        else:
            self.play_btn.configure(text="▶", fg_color="#4caf50")

