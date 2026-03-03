import customtkinter as ctk
import tkinter as tk

class MemoryCell(ctk.CTkFrame):
    def __init__(self, parent, address, value, v_type, color, theme, data_json=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.address = address
        self.data = data_json
        self.theme = theme # Theme dict
        self.is_dying = False
        self.is_leaking = False
        self.original_color = color
        
        # Hover Bindings
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        # Matriks Estetiği: Adrese Göre Renk Üretimi (Hash to Pastel Color)
        def address_to_color(addr):
            h = hash(addr)
            r = (h & 0xFF0000) >> 16
            g = (h & 0x00FF00) >> 8
            b = h & 0x0000FF
            r = (r + 255) // 2
            g = (g + 255) // 2
            b = (b + 255) // 2
            return f"#{r:02x}{g:02x}{b:02x}"

        addr_color = address_to_color(address)
        
        # Üst Bar (Adres Çipi ve Tür)
        top_bar = ctk.CTkFrame(self, fg_color="transparent", height=20)
        top_bar.pack(fill="x", pady=(0, 2))
        
        # Adres "Çip" Görünümü
        self.chip = ctk.CTkFrame(top_bar, fg_color=self.theme['comment'], corner_radius=5, height=18)
        self.chip.pack(side="left")
        self.addr_label = ctk.CTkLabel(self.chip, text=f" {address} ", font=("Consolas", 9, "bold"), text_color="white")
        self.addr_label.pack(padx=2, pady=0)
        
        # Tür İkonu
        icon_map = {
            "int": "🔢", "float": "🔢", "string": "📝", "list": "🛒", "bool": "☯️",
            "map": "🗺️", "func": "ƒ", "class": "📦", "null": "🚫"
        }
        icon = icon_map.get(v_type.lower(), "📦")
        ctk.CTkLabel(top_bar, text=f"{icon} {v_type.upper()}", font=("Segoe UI", 9, "bold"), text_color=self.theme['comment']).pack(side="right")

        # Ana Kutu (Veri Haznesi)
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
            self._render_class_instance(data_json)
        else:
            val_text = str(value)
            if len(val_text) > 40: val_text = val_text[:37] + "..."
            
            val_lbl = ctk.CTkLabel(self.box, text=val_text, font=("Consolas", 15, "bold"), text_color=theme['fg'])
            val_lbl.pack(padx=15, pady=12)

        # Sağ Tık Menüsü
        self.bind("<Button-3>", self.show_context_menu)
        self.box.bind("<Button-3>", self.show_context_menu)
        
        self.pointers = []

    def _render_class_instance(self, data):
        class_name = data.get("class_name", "Object")
        members = data.get("members", {})
        methods = data.get("methods", [])
        parent_class = data.get("parent_class")
        
        class_header = ctk.CTkFrame(self.box, fg_color=self.theme['keyword'], corner_radius=8)
        class_header.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(class_header, text=f"🏰 {class_name}", 
                    font=("Segoe UI", 12, "bold"),
                    text_color="white").pack(side="left", padx=10, pady=5)
        
        if parent_class:
            ctk.CTkLabel(class_header, text=f"← {parent_class}",
                        font=("Consolas", 9),
                        text_color="#ffd700").pack(side="right", padx=5)
        
        if members:
            member_frame = ctk.CTkFrame(self.box, fg_color="transparent")
            member_frame.pack(fill="x", padx=10, pady=5)
            
            for name, info in members.items():
                is_private = name.startswith("_")
                row = ctk.CTkFrame(member_frame, fg_color=self.theme['hover'], corner_radius=4)
                row.pack(fill="x", pady=1)
                
                icon = "🔒" if is_private else "🟢"
                color = "#ff5252" if is_private else "#00e676"
                
                ctk.CTkLabel(row, text=icon, font=("Segoe UI", 10)).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=name, font=("Consolas", 10, "bold"),
                            text_color=color, anchor="w", width=80).pack(side="left")
                
                val = str(info.get("value", "?"))
                if len(val) > 20: val = val[:17] + "..."
                ctk.CTkLabel(row, text=val, font=("Consolas", 9),
                            text_color=self.theme['string']).pack(side="left", padx=5)
        
        if methods:
            method_frame = ctk.CTkFrame(self.box, fg_color=self.theme['select_bg'], corner_radius=6)
            method_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(method_frame, text="⚙️ Metodlar", 
                        font=("Segoe UI", 9, "bold"),
                        text_color=self.theme['function']).pack(anchor="w", padx=5, pady=2)
            
            for method in methods[:3]:
                m_name = method if isinstance(method, str) else method.get("name", "?")
                is_virtual = isinstance(method, dict) and method.get("virtual", False)
                
                m_label = f"ƒ {m_name}"
                if is_virtual:
                    m_label += " 🎭"
                
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
        popup = ctk.CTkToplevel(self)
        popup.title("🧊 Sanal Tablo (VTable)")
        popup.geometry("350x200")
        popup.attributes('-topmost', True)
        
        ctk.CTkLabel(popup, text="🎭 Polimorfizm Detayları", 
                    font=("Segoe UI", 14, "bold")).pack(pady=10)
        
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
        
        ctk.CTkButton(popup, text="Kapat", width=100,
                     command=popup.destroy).pack(pady=10)

    def show_context_menu(self, event):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="🕵️ Takibe Al / Bırak", command=self.toggle_watch)
        menu.add_command(label="📋 Adresi Kopyala", command=lambda: self.clipboard_append(self.address))
        menu.tk_popup(event.x_root, event.y_root)

    def toggle_watch(self):
        current_bg = self.chip._fg_color
        if current_bg != "#fbc02d":
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
        if self.is_leaking: return
        self.is_leaking = True
        # Note: self.addr_label was not defined in the snippet I saw, but it was used in leak_alarm.
        # I'll check if it's supposed to be somewhere.
        # Looking at birth/death, it seems there's some label.
        # Actually, let's just bypass the label part if it's missing or fix it.
        # I'll add a check.
        if hasattr(self, 'addr_label'):
            self.addr_label.configure(text=f"⚠️ LEAK: {self.address}", text_color="#ff1744")
        self.box.configure(border_color="#ff1744", border_width=3)
        self._pulse_red()

    def _pulse_red(self):
        if not self.is_leaking: return
        current_bg = self.box._fg_color
        new_color = "#b71c1c" if current_bg != "#b71c1c" else self.theme.get('error', '#37474f')
        self.box.configure(fg_color=new_color)
        self.after(500, self._pulse_red)

    def die(self):
        self.is_leaking = False
        self.is_dying = True
        
        for child in self.box.winfo_children():
            child.destroy()
            
        self.box.configure(fg_color="transparent", border_color="#546e7a", border_width=1)
        if hasattr(self, 'addr_label'):
            self.addr_label.configure(text=f"️ FREED", text_color="#546e7a")
        
        ctk.CTkLabel(self.box, text=f"💀 {self.address}\n[Boşluk]", font=("Consolas", 10, "italic"), text_color="#455a64").pack(expand=True)
        self.after(5000, self.destroy)
        
    def flash(self, color=None):
        c = color if color else self.theme['accent']
        self.box.configure(border_color=c, border_width=4)
        self.after(600, lambda: self.box.configure(border_color=self.theme.get('border', '#424242'), border_width=2))

    def update_data(self, new_data):
        self.data = new_data
        new_val = str(new_data.get("value", "?"))
        
        children = self.box.winfo_children()
        if children and isinstance(children[-1], ctk.CTkLabel):
            display_val = new_val
            if len(display_val) > 40: display_val = display_val[:37] + "..."
            children[-1].configure(text=display_val)
            
        try:
            is_watched = (self.chip._fg_color == "#fbc02d")
        except:
            is_watched = False
            
        flash_color = "#ff1744" if is_watched else "#ffc107"
        self.flash(color=flash_color)

    def birth(self):
        self._birth_flash(4)
    
    def _birth_flash(self, count):
        if count <= 0:
            self.box.configure(border_color=self.theme.get('border', '#424242'), border_width=2)
            return
            
        colors = ["#00e676", "#69f0ae", "#b9f6ca", "#00e676"]
        color = colors[count % len(colors)]
        self.box.configure(border_color=color, border_width=5)
        
        self.after(120, lambda: self._birth_flash(count - 1))
