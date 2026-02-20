import customtkinter as ctk
import json
import tkinter as tk
import random
from datetime import datetime

class MemoryCell(ctk.CTkFrame):
    def __init__(self, parent, address, value, v_type, color, theme, data_json=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.address = address
        self.data = data_json
        self.theme = theme # Theme dict
        self.is_dying = False
        self.is_leaking = False
        
        # Hover Bindings
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        # Matriks Estetiği: Adrese Göre Renk Üretimi (Hash to Pastel Color)
        def address_to_color(addr):
            # Basit hash
            h = hash(addr)
            r = (h & 0xFF0000) >> 16
            g = (h & 0x00FF00) >> 8
            b = h & 0x0000FF
            # Renkleri yumuşat (Pastel)
            r = (r + 255) // 2
            g = (g + 255) // 2
            b = (b + 255) // 2
            return f"#{r:02x}{g:02x}{b:02x}"

        addr_color = address_to_color(address)
        
        # Üst Bar (Adres Çipi ve Tür)
        top_bar = ctk.CTkFrame(self, fg_color="transparent", height=20)
        top_bar.pack(fill="x", pady=(0, 2))
        
        # Adres "Çip" Görünümü
        chip = ctk.CTkFrame(top_bar, fg_color=self.theme['comment'], corner_radius=5, height=18)
        chip.pack(side="left")
        ctk.CTkLabel(chip, text=f" {address} ", font=("Consolas", 9, "bold"), text_color="white").pack(padx=2, pady=0)
        
        # Tür İkonu
        icon_map = {
            "int": "🔢", "float": "🔢", "string": "📝", "list": "🛒", "bool": "☯️",
            "map": "🗺️", "func": "ƒ", "class": "📦", "null": "🚫"
        }
        icon = icon_map.get(v_type.lower(), "📦")
        ctk.CTkLabel(top_bar, text=f"{icon} {v_type.upper()}", font=("Segoe UI", 9, "bold"), text_color=self.theme['comment']).pack(side="right")

        # Ana Kutu (Veri Haznesi)
        # Eğer 'color' parametresi geldiyse onu kullan, yoksa temadan hesapla
        # Ama burada 'color' genelde rastgele geliyor, biz adres rengini border yapalım.
        
        self.box = ctk.CTkFrame(self, fg_color=color, corner_radius=10, border_width=2, border_color=addr_color)
        self.box.pack(fill="both", expand=True)
        
        # Propagate click/hover events to children
        for child in self.box.winfo_children():
            child.bind("<Enter>", self._on_enter)
            child.bind("<Leave>", self._on_leave)

        if data_json and data_json.get("type") == 3: # LIST
            self._render_list(data_json.get("elements", []))
        elif data_json and data_json.get("type") == 21: # MAP
            self._render_map(data_json.get("items", {}))
        elif data_json and (data_json.get("type") == "class" or data_json.get("members")):
            # 🏰 OOP: Nesne (Class Instance)
            self._render_class_instance(data_json)
        else:
            val_text = str(value)
            if len(val_text) > 40: val_text = val_text[:37] + "..."
            
            # Değer Göstergesi (Büyük ve Net)
            val_lbl = ctk.CTkLabel(self.box, text=val_text, font=("Consolas", 15, "bold"), text_color=theme['fg'])
            val_lbl.pack(padx=15, pady=12)

        # Sağ Tık Menüsü (Dedektif Modu)
        self.bind("<Button-3>", self.show_context_menu)
        self.box.bind("<Button-3>", self.show_context_menu)
        
        # Chip referansı
        self.chip = chip
        
        # İşaretçiler (Ok çizimi için kaynak noktalar)
        # Format: [(hedef_adres, widget_objesi), ...]
        self.pointers = []

    def _render_class_instance(self, data):
        """OOP: Sınıf nesnesini görselleştir"""
        class_name = data.get("class_name", "Object")
        members = data.get("members", {})
        methods = data.get("methods", [])
        parent_class = data.get("parent_class")
        
        # Sınıf Başlığı
        class_header = ctk.CTkFrame(self.box, fg_color=self.theme['keyword'], corner_radius=8)
        class_header.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(class_header, text=f"🏰 {class_name}", 
                    font=("Segoe UI", 12, "bold"),
                    text_color="white").pack(side="left", padx=10, pady=5)
        
        # Miras Badge
        if parent_class:
            ctk.CTkLabel(class_header, text=f"← {parent_class}",
                        font=("Consolas", 9),
                        text_color="#ffd700").pack(side="right", padx=5)
        
        # Üyeler (Members)
        if members:
            member_frame = ctk.CTkFrame(self.box, fg_color="transparent")
            member_frame.pack(fill="x", padx=10, pady=5)
            
            for name, info in members.items():
                is_private = name.startswith("_")
                row = ctk.CTkFrame(member_frame, fg_color=self.theme['hover'], corner_radius=4)
                row.pack(fill="x", pady=1)
                
                # Görünürlük ikonu
                icon = "🔒" if is_private else "🟢"
                color = "#ff5252" if is_private else "#00e676"
                
                ctk.CTkLabel(row, text=icon, font=("Segoe UI", 10)).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=name, font=("Consolas", 10, "bold"),
                            text_color=color, anchor="w", width=80).pack(side="left")
                
                # Değer
                val = str(info.get("value", "?"))
                if len(val) > 20: val = val[:17] + "..."
                ctk.CTkLabel(row, text=val, font=("Consolas", 9),
                            text_color=self.theme['string']).pack(side="left", padx=5)
        
        # Metodlar (Methods)
        if methods:
            method_frame = ctk.CTkFrame(self.box, fg_color=self.theme['select_bg'], corner_radius=6)
            method_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(method_frame, text="⚙️ Metodlar", 
                        font=("Segoe UI", 9, "bold"),
                        text_color=self.theme['function']).pack(anchor="w", padx=5, pady=2)
            
            for method in methods[:3]:  # İlk 3 metod
                m_name = method if isinstance(method, str) else method.get("name", "?")
                is_virtual = isinstance(method, dict) and method.get("virtual", False)
                
                m_label = f"ƒ {m_name}"
                if is_virtual:
                    m_label += " 🎭"  # Polimorfizm işareti
                
                # Virtual metodlar tıklanabilir
                if is_virtual:
                    m_btn = ctk.CTkButton(method_frame, text=m_label,
                                         font=("Consolas", 9),
                                         fg_color="transparent",
                                         hover_color=self.theme['select_bg'],
                                         text_color=self.theme['function'],
                                         anchor="w",
                                         command=lambda m=method: self._show_vtable_popup(m))
                    m_btn.pack(anchor="w", padx=10, fill="x")
                else:
                    ctk.CTkLabel(method_frame, text=m_label,
                                font=("Consolas", 9),
                                text_color=self.theme['function']).pack(anchor="w", padx=10)
    
    def _show_vtable_popup(self, method_info):
        """🧊 VTable bilgilerini göster"""
        popup = ctk.CTkToplevel(self)
        popup.title("🧊 Sanal Tablo (VTable)")
        popup.geometry("350x200")
        popup.attributes('-topmost', True)
        
        # Başlık
        ctk.CTkLabel(popup, text="🎭 Polimorfizm Detayları", 
                    font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        # Bilgiler
        info_frame = ctk.CTkFrame(popup, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        m_name = method_info.get("name", "?")
        vtable_addr = method_info.get("vtable_addr", "0x" + hex(id(method_info))[2:].upper())
        override_from = method_info.get("override_from", "Base")
        
        ctk.CTkLabel(info_frame, text=f"Metod: {m_name}", 
                    font=("Consolas", 11, "bold"),
                    anchor="w").pack(fill="x", pady=5)
        
        ctk.CTkLabel(info_frame, text=f"VTable Adresi: {vtable_addr}",
                    font=("Consolas", 10),
                    text_color="#00e676",
                    anchor="w").pack(fill="x", pady=5)
        
        ctk.CTkLabel(info_frame, text=f"Override: {override_from}",
                    font=("Consolas", 10),
                    text_color="#ffd700",
                    anchor="w").pack(fill="x", pady=5)
        
        ctk.CTkLabel(info_frame, 
                    text="Bu metod runtime'da dinamik olarak çözümlenir.\nBu sayede farklı nesneler aynı arayüzü kullanabilir!",
                    font=("Segoe UI", 9),
                    text_color="gray",
                    wraplength=300).pack(fill="x", pady=10)
        
        # Kapat butonu
        ctk.CTkButton(popup, text="Kapat", width=100,
                     command=popup.destroy).pack(pady=10)

    def show_context_menu(self, event):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="🕵️ Takibe Al / Bırak", command=self.toggle_watch)
        menu.add_command(label="📋 Adresi Kopyala", command=lambda: self.clipboard_append(self.address))
        menu.tk_popup(event.x_root, event.y_root)

    def toggle_watch(self):
        current_bg = self.chip._fg_color
        if current_bg != "#fbc02d": # Sarı
            self.chip.configure(fg_color="#fbc02d")
        else:
            self.chip.configure(fg_color=self.theme['comment'])

    def _render_list(self, elements):
        v_frame = ctk.CTkFrame(self.box, fg_color="transparent")
        v_frame.pack(fill="x", padx=10, pady=5)
        for i, el in enumerate(elements):
            v = ctk.CTkFrame(v_frame, fg_color=self.theme['select_bg'], width=45, height=35, corner_radius=6, border_width=1, border_color=self.theme['border'])
            v.pack(side="left", padx=1)
            v.pack_propagate(False)
            ctk.CTkLabel(v, text=str(i), font=("Segoe UI", 8), text_color=self.theme['comment']).place(relx=0.1, rely=0.1)
            
            val = el.get("value", "")
            target_addr = el.get("address", "null")
            
            if target_addr != "null": 
                # İşaretçi Butonu
                btn = ctk.CTkButton(v, text="💠", width=20, height=20, fg_color="transparent", hover_color=self.theme['accent'])
                btn.place(relx=0.5, rely=0.5, anchor="center")
                self.pointers.append((target_addr, btn))
            else:
                ctk.CTkLabel(v, text=val, font=("Consolas", 10, "bold"), text_color=self.theme['fg']).place(relx=0.5, rely=0.5, anchor="center")

    def _render_map(self, items):
        for k, v in items.items():
            row = ctk.CTkFrame(self.box, fg_color="rgba(0,0,0,0.3)", corner_radius=6)
            row.pack(fill="x", padx=10, pady=1)
            ctk.CTkLabel(row, text=f"{k}:", width=60, anchor="w", font=("Consolas", 9, "bold"), text_color=self.theme['string']).pack(side="left", padx=5)
            
            val = v.get("value", "")
            target_addr = v.get("address", "null")
            
            if target_addr != "null":
                # İşaretçi Butonu (Text + Ikon)
                btn = ctk.CTkButton(row, text=f"💠 {target_addr[-4:]}", width=80, height=18, 
                                    fg_color=self.theme['select_bg'], font=("Consolas", 9))
                btn.pack(side="left")
                self.pointers.append((target_addr, btn))
            else:
                ctk.CTkLabel(row, text=val, font=("Consolas", 9, "bold"), text_color=self.theme['fg']).pack(side="left")

    def _on_enter(self, event):
        self.box.configure(border_width=3)
        
    def _on_leave(self, event):
        self.box.configure(border_width=2)

    def leak_alarm(self):
        """Hafıza Kaçağı Alarmı"""
        if self.is_leaking: return
        self.is_leaking = True
        self.addr_label.configure(text=f"⚠️ LEAK: {self.address}", text_color="#ff1744")
        self.box.configure(border_color="#ff1744", border_width=3)
        self._pulse_red()

    def _pulse_red(self):
        if not self.is_leaking: return
        current_bg = self.box._fg_color
        # Yanıp sönme efekti
        new_color = "#b71c1c" if current_bg != "#b71c1c" else self.theme.get('error', '#37474f')
        self.box.configure(fg_color=new_color)
        self.after(500, self._pulse_red)

    def die(self):
        self.is_leaking = False
        self.is_dying = True
        
        # İçeriği temizle (Vagonu boşalt)
        for child in self.box.winfo_children():
            child.destroy()
            
        # Fragmentasyon Görseli (Kırık Hafıza Bloğu)
        self.box.configure(fg_color="transparent", border_color="#546e7a", border_width=1)
        self.addr_label.configure(text=f"�️ FREED", text_color="#546e7a")
        
        # Kırık Taş Efekti
        ctk.CTkLabel(self.box, text=f"💀 {self.address}\n[Boşluk]", font=("Consolas", 10, "italic"), text_color="#455a64").pack(expand=True)
        
        # Hemen yok etme, fragmentasyonu göster (5 saniye bekle)
        self.after(5000, self.destroy)
        
    def flash(self, color=None):
        c = color if color else self.theme['accent']
        self.box.configure(border_color=c, border_width=4)
        self.after(600, lambda: self.box.configure(border_color=self.theme['border'], border_width=2))

    def update_data(self, new_data):
        """Hücre verisini güncelle ve parlayarak bildir"""
        self.data = new_data
        new_val = str(new_data.get("value", "?"))
        
        # Basit değer güncellemesi (Karmaşık yapılar için full re-render gerekebilir ama şimdilik text)
        children = self.box.winfo_children()
        # Genelde son label değerdir, ama daha güvenlisi box içindeki label'ı bulmaktır.
        # Basitlik için son label diyelim
        if children and isinstance(children[-1], ctk.CTkLabel):
            display_val = new_val
            if len(display_val) > 40: display_val = display_val[:37] + "..."
            children[-1].configure(text=display_val)
            
        # Takipteyse Kırmızı, değilse Sarı çak
        # chip rengini kontrol et
        try:
            is_watched = (self.chip._fg_color == "#fbc02d")
        except:
            is_watched = False
            
        flash_color = "#ff1744" if is_watched else "#ffc107" # Red vs Amber
        self.flash(color=flash_color)

    def birth(self):
        """✨ Constructor Animasyonu (Yeşil Parlama)"""
        self._birth_flash(4)
    
    def _birth_flash(self, count):
        """Doğum parlaması"""
        if count <= 0:
            self.box.configure(border_color=self.theme.get('border', '#424242'), border_width=2)
            return
            
        # Yeşil parlama
        colors = ["#00e676", "#69f0ae", "#b9f6ca", "#00e676"]
        color = colors[count % len(colors)]
        self.box.configure(border_color=color, border_width=5)
        
        self.after(120, lambda: self._birth_flash(count - 1))


class MemoryView(ctk.CTkFrame):
    def __init__(self, parent, config, on_jump=None, on_ask_ai=None):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_jump = on_jump
        self.on_ask_ai = on_ask_ai
        self.history = []
        self.current_index = -1
        self.cells = {} # current active cells
        self.is_playing = False
        self.play_job = None
        
        # Tema Kısayolu
        self.current_theme = self.config.THEMES[self.config.theme]

        # 🕰️ ZAMAN MAKİNESİ
        self.top_strip = ctk.CTkFrame(self, fg_color="transparent")
        self.top_strip.pack(fill="x", padx=10, pady=5)
        
        self.timer_panel = ctk.CTkFrame(self.top_strip, fg_color=self.current_theme['sidebar_bg'], corner_radius=12)
        self.timer_panel.pack(fill="x", expand=True)
        
        ctk.CTkLabel(self.timer_panel, text="🕰️ REF-COUNT ZAMAN MAKİNESİ", font=("Segoe UI", 12, "bold"), 
                     text_color=self.current_theme['accent']).pack(pady=(5, 0))
        
        ctrl_frame = ctk.CTkFrame(self.timer_panel, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=10)
        
        # Geri Butonu
        self.btn_back = ctk.CTkButton(ctrl_frame, text="◀", width=30, height=26, 
                                      fg_color=self.current_theme['select_bg'], 
                                      command=lambda: self._move_step(-1))
        self.btn_back.pack(side="left", padx=2, pady=5)
        
        # Oynat Butonu
        self.btn_play = ctk.CTkButton(ctrl_frame, text="▶ Oynat", width=70, height=26, 
                                      fg_color="#2e7d32", command=self.toggle_play)
        self.btn_play.pack(side="left", padx=2, pady=5)
        
        self.slider = ctk.CTkSlider(ctrl_frame, from_=0, to=1, command=self._on_slider_change, progress_color=self.current_theme['accent'])
        self.slider.pack(side="left", fill="x", expand=True, padx=5)
        self.slider.set(0)
        
        # İleri Butonu
        self.btn_next = ctk.CTkButton(ctrl_frame, text="▶", width=30, height=26, 
                                      fg_color=self.current_theme['select_bg'], 
                                      command=lambda: self._move_step(1))
        self.btn_next.pack(side="left", padx=2, pady=5)
        
        # 📂 Yükle Butonu
        self.btn_load = ctk.CTkButton(ctrl_frame, text="📂", width=30, height=26,
                                      fg_color="#f57f17", # Amber Dark
                                      hover_color="#xhdb0a",
                                      command=self.load_snapshot)
        self.btn_load.pack(side="right", padx=2)

        # 📸 Snapshot Butonu
        self.btn_snap = ctk.CTkButton(ctrl_frame, text="📷", width=30, height=26,
                                      fg_color="#00838f", # Cyan Dark
                                      hover_color="#00acc1",
                                      command=self.take_snapshot)
        self.btn_snap.pack(side="right", padx=2)
        
        # 🧠 Analiz Butonu
        if self.on_ask_ai:
            self.btn_ai = ctk.CTkButton(ctrl_frame, text="🧠", width=30, height=26,
                                        fg_color="#7b1fa2", # Purple
                                        hover_color="#8e24aa",
                                        command=self.run_diagnostics)
            self.btn_ai.pack(side="right", padx=2)

        # 📊 SİSTEM GÖSTERGELERİ ve PERFORMANS GRAFİĞİ
        self.metric_frame = ctk.CTkFrame(self, fg_color=self.current_theme['sidebar_bg'], height=50, corner_radius=0)
        self.metric_frame.pack(side="bottom", fill="x")
        
        # Sol taraf: Barlar
        self.stats_left = ctk.CTkFrame(self.metric_frame, fg_color="transparent")
        self.stats_left.pack(side="left", fill="y", padx=5)
        
        self.cpu_bar = ctk.CTkProgressBar(self.stats_left, width=80, height=6, progress_color=self.current_theme['keyword'])
        self.cpu_bar.set(0.2)
        self.cpu_bar.pack(side="top", pady=(8, 2))
        
        self.mem_bar = ctk.CTkProgressBar(self.stats_left, width=80, height=6, progress_color=self.current_theme['accent'])
        self.mem_bar.set(0.4)
        self.mem_bar.pack(side="top", pady=2)
        
        # Orta: Sayaç
        self.obj_count_label = ctk.CTkLabel(self.metric_frame, text="📦 0", font=("Consolas", 12, "bold"))
        self.obj_count_label.pack(side="left", padx=10)

        # Sağ: Big-O Sparkline (Canlı Grafik)
        self.perf_history = [] # [nesne_sayisi, ...]
        self.perf_canvas = tk.Canvas(self.metric_frame, height=40, width=120, 
                                     bg=self.current_theme['sidebar_bg'], highlightthickness=0)
        self.perf_canvas.pack(side="right", padx=5, pady=5)
        
        # Çizgi etiketi
        ctk.CTkLabel(self.metric_frame, text="📈 O(n)", font=("Segoe UI", 9, "bold"), 
                     text_color="gray").pack(side="right", padx=2)
        
        # 🌳 Layout Mode Toggle (Liste vs Ağaç)
        self.layout_mode = "linear"  # "linear" veya "tree"
        layout_frame = ctk.CTkFrame(self.metric_frame, fg_color="transparent")
        layout_frame.pack(side="right", padx=10)
        
        self.btn_layout = ctk.CTkButton(layout_frame, text="🌳 Ağaç Modu", width=100, height=24,
                                       fg_color=self.current_theme['select_bg'],
                                       command=self.toggle_layout)
        self.btn_layout.pack()
        
        # Nesne Sayacı (eski tanımı kaldırıldı, yukarıda zaten var)
        # self.obj_count_label = ctk.CTkLabel(self.metric_frame, text="📦 Nesne: 0", font=("Consolas", 10, "bold"))
        # self.obj_count_label.pack(side="right", padx=15)
        
        self.mem_bar = ctk.CTkProgressBar(self.stats_left, width=80, height=6, progress_color=self.current_theme['accent'])
        self.mem_bar.set(0.4)
        self.mem_bar.pack(side="left", padx=(20, 5), pady=10)
        ctk.CTkLabel(self.metric_frame, text="BELLEK %", font=("Segoe UI", 9), text_color=self.current_theme['fg']).pack(side="left")

        self.step_label = ctk.CTkLabel(self.metric_frame, text="Adım: 0/0", font=("Consolas", 10), text_color=self.current_theme['comment'])
        self.step_label.pack(side="right", padx=20)

        # Ana Tabview
        self.tabview = ctk.CTkTabview(self, segmented_button_selected_color=self.current_theme['accent'])
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tab_stack = self.tabview.add("🧱 ÇAĞRI KULESİ")
        self.tab_heap = self.tabview.add("🏠 HAFIZA ODALARI")
        
        self.stack_scroll = ctk.CTkScrollableFrame(self.tab_stack, fg_color=self.current_theme['editor_bg'])
        self.stack_scroll.pack(fill="both", expand=True)
        
        self.heap_container = ctk.CTkFrame(self.tab_heap, fg_color=self.current_theme['editor_bg'])
        self.heap_container.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.heap_container, bg=self.current_theme['editor_bg'], highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.scrollbar = ctk.CTkScrollbar(self.heap_container, orientation="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.heap_frame = tk.Frame(self.canvas, bg=self.current_theme['editor_bg'])
        self.canvas_window = self.canvas.create_window((0,0), window=self.heap_frame, anchor="nw")
        
        self.heap_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

    def _move_step(self, delta):
        n = self.current_index + delta
        if 0 <= n < len(self.history):
            self.slider.set(n)
            self._on_slider_change(n)

    def toggle_play(self):
        self.is_playing = not self.is_playing
        self.btn_play.configure(text="⏸ Duraklat" if self.is_playing else "▶ Oynat", 
                              fg_color="#c62828" if self.is_playing else "#2e7d32")
        if self.is_playing: self._play_step()

    def _play_step(self):
        if not self.is_playing: return
        if self.current_index < len(self.history) - 1:
            self._move_step(1)
            self.after(800, self._play_step)
        else:
            self.toggle_play()

    def _on_slider_change(self, val):
        self.current_index = int(val)
        self._display_current()

    def update_memory(self, memory_json):
        try:
            data = json.loads(memory_json)
            
            # Eğer bu ilk frame ise (parent yoksa veya history boşsa)
            # data.get("parent") == None kontrolü güvenilir değil çünkü ilk scope'un parent'ı null'dır zaten.
            # Ancak yeni bir çalıştırma olduğunu anlamak için daha iyi bir yol lazım.
            # Şimdilik basitçe: eğer veride "step": 0 gibi bir bilgi varsa resetleyebiliriz.
            # Veya main_window, çalıştırmadan önce reset çağırabilir.
            
            self.history.append(data)
            
            total_steps = len(self.history)
            if total_steps > 0:
                self.slider.configure(to=total_steps - 1)
                
                # Eğer kullanıcı geriye gitmediyse (en sondayda), otomatik ilerlet
                if self.current_index == total_steps - 2 or self.current_index == -1:
                     self.current_index = total_steps - 1
                     self.slider.set(self.current_index)
                     self._display_current()
        except Exception as e:
            print(f"Memory Update Error: {e}")

    def reset(self):
        """View'ı ve geçmişi temizle"""
        self.history = []
        self.current_index = -1
        self.cells = {}
        self.slider.configure(to=1)
        self.slider.set(0)
        self.step_label.configure(text="Adım: 0/0")
        
        # UI Temizle
        for widget in self.stack_scroll.winfo_children():
            widget.destroy()
        
        for widget in self.heap_frame.winfo_children():
            widget.destroy()
            
        self.canvas.configure(scrollregion=(0,0,0,0))

    def _display_current(self):
        if self.current_index < 0: return
        data = self.history[self.current_index]
        prev = self.history[self.current_index-1] if self.current_index > 0 else None
        
        self.step_label.configure(text=f"Adım: {self.current_index + 1} / {len(self.history)}")
        self.step_label.configure(text=f"Adım: {self.current_index + 1} / {len(self.history)}")
        self._display_stack(data, prev)
        self._display_heap(data, prev)
        self.after(100, self._draw_arrows)
        
        # 🚀 CANLI KOD AKIŞI: Editörde satıra git
        line_no = data.get("line", 0)
        if line_no > 0 and self.on_jump:
            self.on_jump(line_no, highlight=True) # highlight=True parametresi ekliyoruz
        
        self.cpu_bar.set(0.1 + random.random() * 0.4)
        self.mem_bar.set(0.2 + (len(self.history) / 1000.0))

    def _display_stack(self, data, prev):
        for w in self.stack_scroll.winfo_children(): w.destroy()
        
        self.stack_pointers = [] # Reset pointer list
        
        scopes = []
        c = data
        while c:
            scopes.append(c)
            c = c.get("parent")
        
        for i, s in enumerate(reversed(scopes)):
            scope_name = "🌍 GLOBAL" if i == 0 else f"🛠️ KAT {i}"
            depth_indent = 10 + (i * 20)
            
            # Simple alternating colors based on theme
            bg_color = self.current_theme['sidebar_bg'] if i % 2 == 0 else self.current_theme['bg']
            
            f = ctk.CTkFrame(self.stack_scroll, fg_color=bg_color, corner_radius=10, 
                             border_width=2, border_color=self.current_theme['border'])
            f.pack(fill="x", pady=(2, 8), padx=(depth_indent, 10), side="bottom") 
            
            header = ctk.CTkLabel(f, text=scope_name, font=("Segoe UI", 10, "bold"), 
                                  text_color=self.current_theme['accent'] if i == len(scopes)-1 else self.current_theme['comment'])
            header.pack(pady=2, anchor="w", padx=10)
            
            var_frame = ctk.CTkFrame(f, fg_color="transparent")
            var_frame.pack(fill="x", padx=5, pady=5)
            
            if not s.get("variables"):
                ctk.CTkLabel(var_frame, text="(Boş)", font=("Segoe UI", 9, "italic"), text_color="gray").pack()
            
            for n, v in s.get("variables", {}).items():
                row = ctk.CTkFrame(var_frame, fg_color=self.current_theme['hover'], corner_radius=6)
                row.pack(fill="x", pady=1)
                
                lbl_name = ctk.CTkLabel(row, text=n, width=80, anchor="w", font=("Consolas", 11, "bold"), 
                                        text_color=self.current_theme['variable'] if 'variable' in self.current_theme else self.current_theme['fg'])
                lbl_name.pack(side="left", padx=10)
                
                addr = v.get("address", "null")
                if addr != "null":
                    btn = ctk.CTkButton(row, text=f"💠 {addr[-6:]}", width=90, height=18,
                                       fg_color=self.current_theme['select_bg'], 
                                       command=lambda a=addr: self.jump_jump(a)) 
                    btn.bind("<Enter>", lambda e, a=addr: self._focus_connections(a))
                    btn.bind("<Leave>", lambda e: self._reset_focus())
                    btn.pack(side="right", padx=5)
                    self.stack_pointers.append((addr, btn))
                else:
                    ctk.CTkLabel(row, text=f"= {v['value']}", font=("Consolas", 11), 
                                 text_color=self.current_theme['string']).pack(side="right", padx=10)

    def _focus_connections(self, target_addr):
        # Lazer Odak: Diğerlerini karart, sadece bu değişkene bağlı olanları yak
        self.canvas.itemconfig("ptr_arrow", state="hidden")
        self.canvas.itemconfig(f"arrow_to_{target_addr}", state="normal", width=4, fill=self.current_theme['accent'])
        self.canvas.itemconfig(f"arrow_from_{target_addr}", state="normal", width=4, fill=self.current_theme['keyword'])

    def _reset_focus(self):
        # Varsayılan: Hepsi gizli (Temiz ekran)
        self.canvas.itemconfig("ptr_arrow", state="hidden")

    def _display_heap(self, data, prev):
        # 1. Stack'ten Objelere Erişim (Roots)
        objects = {} # addr -> variable_data
        
        def collect(scope):
            if not scope: return
            for n, v in scope.get("variables", {}).items():
                if v.get("address", "null") != "null":
                    addr = v["address"]
                    objects[addr] = v 
            collect(scope.get("parent"))
        collect(data)
        
        # 2. UI Senkronizasyonu
        
        # a) Yeni veya Güncellenenler
        for addr, v in objects.items():
            if addr not in self.cells:
                # Yeni Hücre
                # Renk seçimi (Döngüsel)
                palette = [
                    self.current_theme.get('keyword', '#c084fc'),
                    self.current_theme.get('function', '#60a5fa'), 
                    self.current_theme.get('string', '#4ade80'),
                    self.current_theme.get('number', '#f472b6'),
                    self.current_theme.get('class', '#fbbf24')
                ]
                color = palette[len(self.cells) % len(palette)]
                
                cell = MemoryCell(self.heap_frame, addr, v.get("value", "?"), v.get("type", "Nesne"), 
                                color, self.current_theme, data_json=v)
                cell.pack(pady=5, padx=10, fill="x")
                self.cells[addr] = cell
                
                # ✨ Constructor Animasyonu
                if hasattr(cell, 'birth'):
                    cell.birth()
                
                # 🧬 Miras ilişkisini kaydet (ok çizimi için)
                if v.get("parent_class"):
                    if not hasattr(self, 'inheritance_links'):
                        self.inheritance_links = []
                    # Parent class adresini bul (basitleştirilmiş - gerçekte parent'ın adresini bilmemiz lazım)
                    # Şimdilik sadece kaydedelim
                    self.inheritance_links.append((addr, v.get("parent_class")))
                    
            else:
                # Varolan hücre: Değer kontrolü (Diff & Watch)
                cell = self.cells[addr]
                old_val = str(cell.data.get("value", "?"))
                new_val = str(v.get("value", "?"))
                
                # Eğer değer değişmişse (veya karmaşık obje güncellendiyse)
                if old_val != new_val:
                    cell.update_data(v)
                elif cell.is_dying:
                    # Dirilme mucizesi (GC'den kurtulduysa) - Nadir durum
                    cell.is_dying = False
                    cell.box.configure(fg_color=cell.original_color)
        
        # b) Silinenler (GC)
        active_addrs = list(self.cells.keys())
        for addr in active_addrs:
             if addr not in objects:
                 cell = self.cells[addr]
                 if not cell.is_dying:
                     cell.die()
                     del self.cells[addr]

        self.after(100, self._draw_arrows)
        self.update_stats()

    def _draw_arrows(self):
        self.canvas.delete("ptr_arrow")
        
        # 1. Stack -> Heap Okları
        if hasattr(self, 'stack_pointers'):
            for addr, btn in self.stack_pointers:
                if addr in self.cells:
                    target_cell = self.cells[addr]
                    self._draw_single_arrow(btn, target_cell)
                else:
                    self._draw_broken_arrow(btn, addr)
        
        # 2. Heap -> Heap Okları
        for addr, cell in self.cells.items():
            if hasattr(cell, 'pointers'):
                 for target_addr, btn in cell.pointers:
                     if target_addr in self.cells:
                         target_cell = self.cells[target_addr]
                         self._draw_single_arrow(btn, target_cell)
                     else:
                        self._draw_broken_arrow(btn, target_addr)
    
    def jump_jump(self, addr):
        # Placeholder for jump logic
        print(f"Jumping to {addr}")
        
    def take_snapshot(self):
        """Hafıza Anlık Görüntüsü (Snapshot)"""
        if not self.history or self.current_index < 0:
            return
            
        try:
            current_data = self.history[self.current_index]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"memory_snapshot_{timestamp}.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(current_data, f, indent=4, ensure_ascii=False)
                
            # Efekt: Buton yeşil yansın
            orig_color = self.btn_snap._fg_color
            self.btn_snap.configure(fg_color="#00c853") # Bright Green
            self.after(500, lambda: self.btn_snap.configure(fg_color=orig_color))
            
            # TODO: Toast mesajı göster
            print(f"Snapshot kaydedildi: {filename}")
        except Exception as e:
            print(f"Snapshot hatası: {e}")

    def update_stats(self):
        """İstatistikleri Güncelle"""
        count = len(self.cells)
        if hasattr(self, 'obj_count_label'):
            self.obj_count_label.configure(text=f"📦 Nesne: {count}")
            
        # Big-O Verisi
        if hasattr(self, 'perf_history'):
            self.perf_history.append(count)
            if len(self.perf_history) > 50:
                self.perf_history.pop(0)
            self._update_sparkline()


    def _draw_single_arrow(self, start_cell, end_cell):
        try:
            x1 = start_cell.winfo_x() + start_cell.winfo_width()
            y1 = start_cell.winfo_y() + 20
            x2 = end_cell.winfo_x()
            y2 = end_cell.winfo_y() + 20
            
            cx1 = x1 + 50
            cy1 = y1
            cx2 = x2 - 50
            cy2 = y2
            
            tag_name = f"ptr_arrow"
            spec_tag_to = f"arrow_to_{end_cell.address}"
            spec_tag_from = f"arrow_from_{start_cell.address}"
            
            # Varsayılan: GİZLİ (Oklar sadece hover anında görülecek)
            self.canvas.create_line(x1, y1,cx1, cy1, cx2, cy2, x2, y2, 
                                   arrow=tk.LAST, fill=self.current_theme['comment'], width=3, smooth=True, 
                                   state='hidden',
                                   tags=(tag_name, spec_tag_to, spec_tag_from))
        except: pass

    def load_snapshot(self):
        """Hafıza Dosyası Yükle (De-Serialization)"""
        try:
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="Hafıza Kaydını Yükle",
                filetypes=(("JSON Dosyaları", "*.json"), ("Tüm Dosyalar", "*.*"))
            )
            
            if not file_path:
                return
                
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.reset()
            
            if isinstance(data, list):
                 self.history = data
            else:
                 self.history = [data]
                 
            self.current_index = len(self.history) - 1
            self.slider.configure(to=max(1, len(self.history) - 1))
            self.slider.set(self.current_index)
            
            # _display_current metodunu bulamazsak manuel çağırırız
            if hasattr(self, '_display_current'):
                self._display_current()
            else:
                d = self.history[self.current_index]
                self._display_stack(d, None)
                self._display_heap(d, None)
                
            self.step_label.configure(text=f"Yüklendi: {len(self.history)} adım")
            
            # Efekt: Turuncu yak
            orig_color = self.btn_load._fg_color
            self.btn_load.configure(fg_color="#ffab00") 
            self.after(500, lambda: self.btn_load.configure(fg_color=orig_color))
            
        except Exception as e:
            print(f"Yükleme hatası: {e}")

    def run_diagnostics(self):
        """Mühendis AI: Bellek Analizi ve Raporlama"""
        if not self.history or self.current_index < 0:
            return

        current_data = self.history[self.current_index]
        if not current_data: return
        
        # 1. Stack Analizi (Derinlik)
        depth = 0
        node = current_data
        while node:
            depth += 1
            node = node.get("parent")
            
        # 2. Heap Analizi
        obj_count = len(self.cells)
        largest_obj_size = 0
        largest_obj_addr = "N/A"
        
        for addr, cell in self.cells.items():
            if hasattr(cell, 'data') and cell.data:
                d = cell.data
                size = 0
                if d.get("type") == 3: # LIST
                    size = len(d.get("elements", []))
                elif d.get("type") == 21: # MAP
                    size = len(d.get("items", {}))
                
                if size > largest_obj_size:
                    largest_obj_size = size
                    largest_obj_addr = addr

        # 3. Rapor Oluşturma
        report = []
        report.append(f"🔍 **Gümüş Mühendis Raporu**")
        report.append(f"- **Stack Derinliği**: {depth} katman")
        report.append(f"- **Canlı Nesne Sayısı**: {obj_count} adet")
        if largest_obj_size > 0:
            report.append(f"- **En Büyük Veri Yapısı**: {largest_obj_size} eleman ({largest_obj_addr})")
        
        risk_level = "DÜŞÜK 🟢"
        if depth > 40 or obj_count > 500 or largest_obj_size > 100:
            risk_level = "YÜKSEK 🔴"
        elif depth > 20 or obj_count > 100 or largest_obj_size > 50:
             risk_level = "ORTA 🟠"
             
        report.append(f"- **Genel Risk Seviyesi**: {risk_level}")
        report.append("\nUsta, bu duruma göre bir yorum yapar mısın? Kodda mantık hatası veya bellek sızıntısı var mı?")
        
        full_query = "\n".join(report)
        
        # AI'ya Gönder
        if self.on_ask_ai:
            self.on_ask_ai(full_query)
            
            # Efekt
            if hasattr(self, 'btn_ai'):
                orig_color = self.btn_ai._fg_color
                self.btn_ai.configure(fg_color="#ab47bc") 
                self.after(500, lambda: self.btn_ai.configure(fg_color=orig_color))

    def toggle_layout(self):
        """Layout modunu değiştir (Liste ↔ Ağaç)"""
        if self.layout_mode == "linear":
            self.layout_mode = "tree"
            self.btn_layout.configure(text="📋 Liste Modu")
        else:
            self.layout_mode = "linear"
            self.btn_layout.configure(text="🌳 Ağaç Modu")
        
        # Mevcut görünümü yenile
        if self.history and self.current_index >= 0:
            data = self.history[self.current_index]
            self._display_heap(data, None)

    def _calculate_complexity(self):
        """Big-O karmaşıklığını tahmin et (sparkline eğimine göre)"""
        if len(self.perf_history) < 10:
            return "O(?)", "#808080"
        
        data = self.perf_history[-10:]  # Son 10 adım
        
        # Basit eğim analizi
        # Eğer veri 2 katına çıktıysa ama adım sayısı aynıysa -> O(n²) veya üzeri
        first_half_avg = sum(data[:5]) / 5
        second_half_avg = sum(data[5:]) / 5
        
        if first_half_avg == 0:
            return "O(1)", "#00e676"
        
        growth_rate = second_half_avg / first_half_avg
        
        if growth_rate < 1.1:
            return "O(1)", "#00e676"  # Sabit
        elif growth_rate < 1.5:
            return "O(log n)", "#76ff03"  # Logaritmik
        elif growth_rate < 2.5:
            return "O(n)", "#ffeb3b"  # Lineer
        else:
            return "O(n²)", "#ff1744"  # Karesel veya daha kötü

    def _update_sparkline(self):
        if not hasattr(self, 'perf_canvas') or len(self.perf_history) < 2:
            return
            
        self.perf_canvas.delete("all")
        
        w = int(self.perf_canvas.cget("width"))
        h = int(self.perf_canvas.cget("height"))
        data = self.perf_history
        max_val = max(data) if max(data) > 0 else 1
        min_val = min(data)
        
        # Scaling
        step_x = w / (len(data) - 1) if len(data) > 1 else w
        
        points = []
        for i, val in enumerate(data):
            x = i * step_x
            norm_y = val / max_val
            y = h - (norm_y * (h - 5)) - 2
            points.append(x)
            points.append(y)
            
        if len(points) >= 4:
            # Big-O Analizi
            complexity, color = self._calculate_complexity()
            
            self.perf_canvas.create_line(points, fill=color, width=2, smooth=True)
            
            # Etiket güncelle
            if hasattr(self, 'metric_frame'):
                # Metric frame içindeki O(n) etiketini bul ve güncelle
                for child in self.metric_frame.winfo_children():
                    if isinstance(child, ctk.CTkLabel) and "O(" in child.cget("text"):
                        child.configure(text=f"📈 {complexity}", text_color=color)
                        break
            
            # Kötü performans uyarısı
            if complexity == "O(n²)" and self.on_ask_ai and len(data) > 20:
                # Sadece bir kere uyar (son uyarıdan 50 adım geçmişse)
                if not hasattr(self, '_last_complexity_warning'):
                    self._last_complexity_warning = 0
                    
                if len(self.perf_history) - self._last_complexity_warning > 50:
                    self._last_complexity_warning = len(self.perf_history)
                    self.on_ask_ai(f"⚠️ PERFORMANS UYARISI: Algoritma {complexity} karmaşıklıkta çalışıyor! "
                                  f"Nesne sayısı {data[0]}'den {data[-1]}'e çıktı. "
                                  f"Bu Gümüşhane'nin sarp yolları gibi hantal! Optimizasyon öner.")

    def _draw_broken_arrow(self, start_widget, target_addr):
        try:
            x1 = start_widget.winfo_x() + start_widget.winfo_width()
            y1 = start_widget.winfo_y() + 10 # Button center
            
            # Rastgele bir yere doğru kırık çizgi
            x2 = x1 + 40
            y2 = y1 + 10
            
            self.canvas.create_line(x1, y1, x2, y2,
                                   arrow=tk.LAST, fill="#ff1744", width=2, dash=(4, 2),
                                   tags=("ptr_arrow", "broken"))
        except: pass

    def handle_crash(self, error_msg):
        """Kaza Kırım Raporu: Otomatik Snapshot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"CRASH_DUMP_{timestamp}.json"
            
            data = {
                "error": error_msg,
                "memory_state": self.history[self.current_index] if self.history and self.current_index >= 0 else {},
                "timestamp": timestamp
            }
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
            print(f"🚨 KAZA KIRIM RAPORU OLUŞTURULDU: {filename}")
            
            # AI'ya bildir
            if self.on_ask_ai:
                self.on_ask_ai(f"🚨 ACİL DURUM: Program çöktü! Hata: {error_msg}. Kaza raporunu ({filename}) incele ve sorunu bul.")
                
        except Exception as e:
            print(f"Crash handler hatası: {e}")

