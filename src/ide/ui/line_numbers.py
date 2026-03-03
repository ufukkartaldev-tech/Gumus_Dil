import tkinter as tk
import tkinter.font

class LineNumberCanvas(tk.Canvas):
    def __init__(self, parent, text_widget, config, **kwargs):
        super().__init__(parent, **kwargs)
        self.text_widget = text_widget
        self.config = config
        self.errors = {}  # {line_number: error_message}
        self.breakpoints = set() # {line_number}
        self.configure(
            width=60,  # Biraz daha geniş (hata işaretleri için)
            highlightthickness=0,
            relief='flat'
        )
        self.apply_theme()
        
        # Binding
        self.bind("<Motion>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.tooltip = None
        
    def apply_theme(self):
        theme = self.config.THEMES[self.config.theme]
        self.configure(bg=theme['sidebar_bg']) 

    def set_errors(self, errors_dict):
        """Hataları ayarla: {line_number: error_message}"""
        self.errors = errors_dict
        self.redraw()
        
    def _on_click(self, event):
        """Tıklama yönetimi: Breakpoint veya Quick Fix"""
        # Tıklanan item'ı bul
        item = self.find_closest(event.x, event.y)
        if item:
            tags = self.gettags(item[0])
            for tag in tags:
                if tag.startswith("error_"):
                    line = int(tag.split("_")[1])
                    self._on_quick_fix(line)
                    return
        
        # Eğer özel bir şey değilse breakpoint toggle et
        self.toggle_breakpoint(event)

    def _on_quick_fix(self, line):
        """Hızlı tamir ikonuna tıklandığında AI paneline gönder"""
        msg = self.errors.get(line, "Bu satırda bir hata var yeğenim.")
        # Editör üzerinden Main Window'a git
        try:
            parent = self.master # Editor
            if hasattr(parent, '_on_quick_fix_request'):
                parent._on_quick_fix_request(line, msg)
        except:
            pass

    def highlight_line(self, line_num):
        """Dışarıdan çağrılan satır vurgulama (Trace için)"""
        # Note: This method seems to use self._textbox which is not defined here.
        # It should probably use self.text_widget or be passed the text widget reference.
        # Looking at editor.py, it was using self._textbox which was defined in CodeEditor.
        # I'll update it to use self.text_widget.
        
        # Önceki vurguyu temizle
        self.text_widget.tag_remove("execution_line", "1.0", tk.END)
        
        # Yeni satırı vurgula
        start = f"{line_num}.0"
        end = f"{line_num}.end+1c"
        self.text_widget.tag_add("execution_line", start, end)
        
        # Görünür yap
        self.text_widget.see(start)
        
        # Minimap'i güncelle (Opsiyonel ama şık durur)
        if hasattr(self.master, 'minimap'):
            self.master.minimap.redraw()

    def toggle_breakpoint(self, event):
        """Breakpoint ekle/kaldır"""
        text_index = self.text_widget.index(f"@0,{event.y}")
        line = int(text_index.split('.')[0])
        
        if line in self.breakpoints:
            self.breakpoints.remove(line)
        else:
            self.breakpoints.add(line)
            
        self.redraw()

    def redraw(self, *args):
        self.delete("all")
        
        # Text widget'in fontunu al
        try:
             text_font = self.text_widget.cget("font")
        except:
             return

        theme = self.config.THEMES[self.config.theme]
        fg_color = theme['comment']
        err_color = "#ff1744"
        bp_color = "#ff4444" 

        i = self.text_widget.index("@0,0")
        
        # İlk satırın bilgilerini al
        if self.text_widget.dlineinfo(i) is None:
             self.after(200, self.redraw)
             return

        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None: break

            y = dline[1]
            linenum = str(i).split(".")[0]
            line_int = int(linenum)
            
            # 1. Breakpoint (Kırmızı Daire)
            if line_int in self.breakpoints:
                self.create_oval(10, y+2, 22, y+14, fill=bp_color, outline="#cc0000", width=1, tags=f"bp_{linenum}")
            
            # 2. Satır Numarası
            self.create_text(45, y, anchor="ne", text=linenum, fill=fg_color, font=text_font, tags=f"line_{linenum}")
            
            # 3. Hata / Quick Fix (💡 Ampul İkonu)
            if line_int in self.errors:
                self.create_text(55, y+8, text="💡", font=("Segoe UI", 10), tags=(f"error_{linenum}", "quickfix"))
                
            i = self.text_widget.index(f"{i}+1line")
    
    def _on_hover(self, event):
        """Mouse hover ile hata mesajını göster"""
        item = self.find_closest(event.x, event.y)
        if not item: return
        
        tags = self.gettags(item[0])
        for tag in tags:
            if tag.startswith("error_"):
                linenum = int(tag.split("_")[1])
                if linenum in self.errors:
                    self._show_tooltip(event.x_root, event.y_root, self.errors[linenum])
                    return
        
        self._hide_tooltip()
    
    def _on_leave(self, event):
        """Mouse ayrıldığında tooltip'i gizle"""
        self._hide_tooltip()
    
    def _show_tooltip(self, x, y, text):
        """Tooltip göster"""
        if self.tooltip:
            self.tooltip.destroy()
        
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x+10}+{y+10}")
        
        theme = self.config.THEMES[self.config.theme]
        label = tk.Label(
            self.tooltip, 
            text=text, 
            background="#ff1744",
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=5,
            relief="solid",
            borderwidth=1
        )
        label.pack()
    
    def _hide_tooltip(self):
        """Tooltip'i gizle"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
