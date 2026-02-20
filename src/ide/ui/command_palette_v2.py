# -*- coding: utf-8 -*-
"""
GÜMÜŞDİL IDE - Komut Paleti V2.0
Fuzzy Search + Klavye Kontrolü + Modern UI
"""
import customtkinter as ctk
import tkinter as tk
import difflib
from datetime import datetime

class CommandPaletteV2(ctk.CTkToplevel):
    _recent_commands = [] # Class-level history
    
    def __init__(self, parent, config, commands):
        super().__init__(parent)
        self.config = config
        self.commands = commands # Dict: {"Komut Adı": fonksiyon}
        self.theme = config.THEMES[config.theme]
        
        # Pencere Ayarları
        self.title("Komut Paleti")
        self.geometry("600x400")
        self.overrideredirect(True) # Çerçevesiz
        self.attributes('-alpha', 0.98)
        self.configure(fg_color=self.theme['bg'])
        
        # Merkezde ve Hafif Yukarıda Aç
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        
        x = parent_x + (parent_w - 600) // 2
        y = parent_y + (parent_h - 400) // 4 # Biraz daha yukarıda
        self.geometry(f"+{int(x)}+{int(y)}")
        
        # Modal benzeri davranış (Focus çalma)
        self.transient(parent)
        self.grab_set()
        
        # Ana Çerçeve (Shadow/Border Effect)
        self.main_frame = ctk.CTkFrame(
            self, 
            corner_radius=12, 
            border_width=2, 
            border_color=self.theme['accent'],
            fg_color=self.theme['sidebar_bg']
        )
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # --- Arama Çubuğu ---
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search_change)
        
        self.search_box = ctk.CTkEntry(
            self.main_frame,
            textvariable=self.search_var,
            placeholder_text="Komut ara... (Ctrl+P)",
            height=45,
            font=("Segoe UI", 16),
            border_width=0,
            fg_color="transparent",
            text_color=self.theme['fg']
        )
        self.search_box.pack(fill="x", padx=15, pady=(15, 5))
        self.search_box.focus_set()
        
        # Ayırıcı Çizgi
        self.separator = ctk.CTkFrame(self.main_frame, height=2, fg_color=self.theme['border'])
        self.separator.pack(fill="x")
        
        # --- Sonuç Listesi (Custom Listbox) ---
        self.results_scroll = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent",
            corner_radius=0
        )
        self.results_scroll.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Klavye Navigasyonu için State
        self.selected_index = 0
        self.visible_items = [] # [(label, func, widget), ...]
        
        # Klavye Bindings
        self.bind("<Escape>", self.close)
        self.bind("<FocusOut>", self.close)
        self.search_box.bind("<Down>", self._nav_down)
        self.search_box.bind("<Up>", self._nav_up)
        # self.search_box.bind("<Tab>", self._nav_down) # Tab ile de gezilebilir
        self.search_box.bind("<Return>", self._execute_selected)
        
        # İlk listeleme
        self._update_list()

    def _on_search_change(self, *args):
        self.selected_index = 0 # Aramada başa dön
        self._update_list()
        
    def _update_list(self):
        """Listeyi filtrele ve yeniden oluştur"""
        query = self.search_var.get().lower()
        
        # Temizle
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        self.visible_items = []
        
        # Adayları Hazırla
        candidates = []
        
        # 1. Son Kullanılanlar (Öncelikli)
        if not query:
            for cmd_name in reversed(CommandPaletteV2._recent_commands):
                if cmd_name in self.commands:
                    candidates.append((f"🕒 {cmd_name}", self.commands[cmd_name], True)) # True = is_recent
        
        # 2. Tüm Komutlar
        all_cmds = list(self.commands.keys())
        
        if query:
            # Fuzzy Search
            matches = difflib.get_close_matches(query, [c.lower() for c in all_cmds], n=10, cutoff=0.3)
            # Match sırasına göre orijinal isimleri bul
            for m in matches:
                # Orijinal case'i bul (biraz yavaş olabilir ama liste küçük)
                for real_name in all_cmds:
                    if real_name.lower() == m:
                        # Zaten eklenmediyse ekle
                        if not any(c[0] == real_name for c in candidates):
                            candidates.append((real_name, self.commands[real_name], False))
                        break
        else:
            # Hepsini listele (Recent dışındakiler)
            for name in sorted(all_cmds):
                # Recent olarak eklenmediyse
                if not any(c[0] == f"🕒 {name}" for c in candidates):
                    candidates.append((name, self.commands[name], False))
                    
        # UI Oluştur
        for i, (label, func, is_recent) in enumerate(candidates):
            if i >= 15: break # Max 15 öğe göster
            
            # Seçili öğe rengi
            is_selected = (i == self.selected_index)
            bg_color = self.theme['select_bg'] if is_selected else "transparent"
            text_color = self.theme['accent'] if is_selected else self.theme['fg']
            
            # Container
            item_frame = ctk.CTkFrame(self.results_scroll, fg_color=bg_color, corner_radius=6, height=35)
            item_frame.pack(fill="x", pady=1, padx=5)
            item_frame.pack_propagate(False) # Yükseklik sabit kalsın
            
            # İkon ve Metin
            # label içindeki emoji'yi ayırabiliriz veya direkt basarız
            ctk.CTkLabel(
                item_frame, 
                text=label, 
                anchor="w", 
                font=("Segoe UI", 12),
                text_color=text_color
            ).pack(side="left", padx=10, fill="x", expand=True)
            
            # Kısayol İpucu (Sağda)
            # (Dictionary'de kısayol bilgisi yok ama eklenebilir)
            if is_recent:
                ctk.CTkLabel(item_frame, text="Son", font=("Segoe UI", 9), text_color="gray").pack(side="right", padx=10)
            elif i < 9:
                # Alt+1, Alt+2 gibi ipuçları eklenebilir (görsel)
                # ctk.CTkLabel(item_frame, text=f"Alt+{i+1}", font=("Segoe UI", 9), text_color="gray").pack(side="right", padx=10)
                pass

            # Tıklama ile çalıştır
            item_frame.bind("<Button-1>", lambda e, f=func, l=label: self._execute(f, l))
            for child in item_frame.winfo_children():
                child.bind("<Button-1>", lambda e, f=func, l=label: self._execute(f, l))
                
            # Hover Efekti (Mouse over)
            def on_enter(e, frame=item_frame, idx=i):
                self.selected_index = idx
                self._highlight_row(frame)
                
            item_frame.bind("<Enter>", on_enter)
            
            # Listeye kaydet
            self.visible_items.append({"widget": item_frame, "func": func, "label": label})
            
    def _highlight_row(self, target_widget):
        """Sadece hedef widget'ı vurgula, diğerlerini temizle"""
        for item in self.visible_items:
            w = item["widget"]
            if w == target_widget:
                w.configure(fg_color=self.theme['select_bg'])
                # İçindeki label'ı da boya
                for child in w.winfo_children():
                    if isinstance(child, ctk.CTkLabel) and "Son" not in child.cget("text"):
                         child.configure(text_color=self.theme['accent'])
            else:
                w.configure(fg_color="transparent")
                for child in w.winfo_children():
                    if isinstance(child, ctk.CTkLabel) and "Son" not in child.cget("text"):
                         child.configure(text_color=self.theme['fg'])

    def _nav_down(self, event):
        if self.visible_items:
            self.selected_index = (self.selected_index + 1) % len(self.visible_items)
            self._update_highlight_by_index()
        return "break" # Textbox'a gitmesin

    def _nav_up(self, event):
        if self.visible_items:
            self.selected_index = (self.selected_index - 1) % len(self.visible_items)
            self._update_highlight_by_index()
        return "break"

    def _update_highlight_by_index(self):
        """Seçili indexe göre UI güncelle"""
        if 0 <= self.selected_index < len(self.visible_items):
            target = self.visible_items[self.selected_index]["widget"]
            self._highlight_row(target)
            # Scroll to view (Basitçe)
            # ctkScrollableFrame scroll_to metodunu desteklemiyor olabilir, 
            # ama widget focus alırsa otomatik kayabilir.
            # target.focus_set() # Bu aramayı bozar.
            
    def _execute_selected(self, event=None):
        if 0 <= self.selected_index < len(self.visible_items):
            item = self.visible_items[self.selected_index]
            self._execute(item["func"], item["label"].replace("🕒 ", ""))

    def _execute(self, func, label_name):
        # Geçmişe ekle
        if label_name in self.commands: # "🕒 " ön ekini temizlemek lazım
             label_clean = label_name.replace("🕒 ", "")
             if label_clean in CommandPaletteV2._recent_commands:
                 CommandPaletteV2._recent_commands.remove(label_clean)
             CommandPaletteV2._recent_commands.append(label_clean)
             # Son 5 komutu tut
             if len(CommandPaletteV2._recent_commands) > 5:
                 CommandPaletteV2._recent_commands.pop(0)
                 
        self.destroy() # Önce kapat
        self.after(100, func) # Sonra çalıştır (UI takılmasın)

    def close(self, event=None):
        self.destroy()

