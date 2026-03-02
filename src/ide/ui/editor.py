import customtkinter as ctk
import tkinter as tk
import re
import os
from ..core.highlighter import SyntaxHighlighter
from .context_bar import SilverContextBar
from .breadcrumbs import Breadcrumbs
from ..core.formatter import GumusFormatter

class Minimap(tk.Canvas):
    def __init__(self, parent, text_widget, config, **kwargs):
        super().__init__(parent, **kwargs)
        self.text_widget = text_widget
        self.config = config
        self.configure(width=100, highlightthickness=0, relief='flat')
        self.apply_theme()
        
        # İnteraktif Minimap
        self.bind("<Button-1>", self.jump_to_click)
        self.bind("<B1-Motion>", self.jump_to_click)
        self.line_height = 3 # Varsayılan
        
    def apply_theme(self):
        theme = self.config.THEMES[self.config.theme]
        self.configure(bg=theme['sidebar_bg'])
        
    def redraw(self, *args):
        self.delete("all")
        content = self.text_widget.get("1.0", "end-1c")
        lines = content.split("\n")
        
        # Orijinal metin satır sayısı
        total_lines = len(lines)
        if total_lines == 0: return

        # Her satır 3 piksel temsil edilsin (daha net görünüm)
        line_height = 3
        
        theme = self.config.THEMES[self.config.theme]
        # Renk tonunu çeşitlendir (yorumlar silik, kodlar parlak)
        base_color = theme.get('comment', '#555')
        accent_color = theme.get('function', '#888')
        
        for i, line in enumerate(lines):
             if not line.strip(): continue
             
             # Satırın başındaki boşluğu al (girinti)
             indent = len(line) - len(line.lstrip())
             y = i * line_height + 5
             
             # Satır uzunluğu
             line_len = min(len(line.strip()), 50) 
             
             # Basit renk mantığı: eğer 'def' veya 'class' ise parlak yap
             is_def = line.strip().startswith(('fonksiyon', 'sınıf', 'temel'))
             color = accent_color if is_def else base_color
             
             self.create_line(
                 5 + (indent * 2), y, 
                 5 + (indent * 2) + (line_len * 2), y, 
                 fill=color, 
                 width=2 # Daha kalın
             )
             
        # Viewport göstergesi (kullanıcının şu an gördüğü alan)
        try:
             first_visible = self.text_widget.index("@0,0")
             last_visible = self.text_widget.index(f"@0,{self.text_widget.winfo_height()}")
             
             start_line = int(first_visible.split('.')[0])
             end_line = int(last_visible.split('.')[0])
             
             viewport_y1 = (start_line - 1) * line_height + 5
             viewport_y2 = (end_line - 1) * line_height + 5
             
             # Yarı saydam bir efekt verilemez (Canvas sınırlı), ama outline çizilebilir
             self.create_rectangle(
                 2, viewport_y1, 
                 98, viewport_y2, 
                 outline=theme['accent'],
                 width=1.5,
                 tags="viewport"
             )
             # Viewport background (hafif dolgu - opsiyonel, stipple kullanarak)
             # self.create_rectangle(2, viewport_y1, 98, viewport_y2, fill=theme['accent'], stipple='gray12', outline="")
             
        except:
             pass

    def jump_to_click(self, event):
        """Minimap'e tıklandığında oraya git"""
        y = event.y
        # Satır numarasını tahmin et
        target_line = int((y - 5) / self.line_height) + 1
        if target_line < 1: target_line = 1
        
        # Oraya kaydır
        try:
             self.text_widget.see(f"{target_line}.0")
             self.text_widget.mark_set("insert", f"{target_line}.0")
        except:
             pass

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
        # Önceki vurguyu temizle
        self._textbox.tag_remove("execution_line", "1.0", tk.END)
        
        # Yeni satırı vurgula
        start = f"{line_num}.0"
        end = f"{line_num}.end+1c"
        self._textbox.tag_add("execution_line", start, end)
        
        # Görünür yap
        self._textbox.see(start)
        
        # Minimap'i güncelle (Opsiyonel ama şık durur)
        if hasattr(self, 'minimap'):
            self.minimap.redraw()

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
        # Eğer None dönerse, widget henüz layout yapılmamış olabilir.
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
                # Daha belirgin ve tıklanabilir bir ikon
                self.create_text(55, y+8, text="💡", font=("Segoe UI", 10), tags=(f"error_{linenum}", "quickfix"))
                
            i = self.text_widget.index(f"{i}+1line")
    
    def _on_hover(self, event):
        """Mouse hover ile hata mesajını göster"""
        # Hangi satırın üzerindeyiz?
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

class CodeEditor(ctk.CTkFrame):
    def __init__(self, parent, config, on_navigate=None, **kwargs):
        super().__init__(parent, corner_radius=8, **kwargs)
        self.config = config
        self.has_content = False
        self.file_path = None
        self.on_navigate = on_navigate
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1) # Row 1: Editor content
        self.grid_rowconfigure(0, weight=0) # Row 0: Breadcrumbs
        
        # 0. Breadcrumbs (Navigasyon)
        self.breadcrumbs = Breadcrumbs(self, config, on_navigate=self.on_navigate)
        self.breadcrumbs.grid(row=0, column=0, columnspan=3, sticky="ew", padx=8, pady=(4, 0))
        
        # 1. Textbox (CTkTextbox) - Premium tasarım
        self.textbox = ctk.CTkTextbox(
            self, 
            activate_scrollbars=True, 
            corner_radius=8,
            border_width=2
        )
        self.textbox.grid(row=1, column=1, sticky="nsew", padx=(0, 8), pady=(4, 8))
        self.textbox.configure(state="normal")
        
        self.completer = None
        try:
             from ..core.autocomplete import AutoCompleter
             self.completer = AutoCompleter()
        except ImportError:
             pass
        
        # Internal TK Text widget erişimi
        self._textbox = self.textbox._textbox
        
        # Font ve Yapılandırma - Daha büyük ve okunabilir
        font_size = 14 if config.simple_ui else 13
        font_name = 'JetBrains Mono' if self._is_font_available('JetBrains Mono') else 'Consolas'
        self.textbox.configure(
            wrap="none", 
            font=(font_name, font_size),
            padx=15,  # İç padding
            pady=15
        )
        
        self._textbox.configure(
            undo=True, 
            autoseparators=True, 
            maxundo=50,
            insertwidth=3,  # Cursor kalınlığı
            spacing1=2,  # Satır üstü boşluk
            spacing3=2   # Satır altı boşluk
        )
        
        # 2. Satır Numaraları (Canvas) - Premium stil
        self.linenumbers = LineNumberCanvas(self, self._textbox, config)
        self.linenumbers.grid(row=1, column=0, sticky="ns", padx=(8, 0), pady=(4, 8))
        
        # 3. Minimap (Yeni)
        self.minimap = Minimap(self, self._textbox, config)
        self.minimap.grid(row=1, column=2, sticky="ns", padx=(0, 8), pady=(4, 8))
        
        # 3. Syntax Highlighting
        self.highlighter = SyntaxHighlighter(self._textbox, config)
        
        # 4. Placeholder Text
        self.placeholder_text = "// 💎 Gümüşdil kodunuzu buraya yazın...\n\n// Örnek:\n// değişken x = 10\n// yazdır(\"Merhaba Dünya!\")"
        self.show_placeholder()
        
        # Event Binding (Sync)
        self._textbox.bind("<<Change>>", self._on_change)
        self._textbox.bind("<Configure>", self._on_change_ui)
        self._textbox.bind("<KeyRelease>", self._on_key_release)
        self._textbox.bind("<MouseWheel>", self._on_change_ui)
        self._textbox.bind("<Button-1>", self._on_click_editor, add="+") # Focus fix
        # self._textbox.bind("<Button-1>", self._on_change_ui) # Eski binding
        self._textbox.bind("<Button-4>", self._on_change_ui) 
        self._textbox.bind("<Button-5>", self._on_change_ui)
        self._textbox.bind("<ButtonRelease-1>", self._match_brackets)
        self._textbox.bind("<Return>", self._on_return)
        self._textbox.bind("<Tab>", self._on_tab_press)
        self._textbox.bind("<Button-3>", self._show_context_menu)
        self._textbox.bind("<<Paste>>", self._on_paste)
        
        # Shortcuts
        self._textbox.bind("<Control-f>", self.show_find_dialog)
        self._textbox.bind("<Control-F>", self.show_find_dialog)
        self._textbox.bind("<Control-slash>", self.toggle_comment) # Ctrl + /
        self._textbox.bind("<Alt-Up>", self.move_line_up)
        self._textbox.bind("<Alt-Down>", self.move_line_down)
        self._textbox.bind("<Control-Shift-K>", self.delete_current_line)
        self._textbox.bind("<Control-Shift-k>", self.delete_current_line)
        self._textbox.bind("<F2>", self.rename_symbol)
        self._textbox.bind("<KeyPress>", self._on_key_press)
        self._textbox.bind("<Control-Alt-l>", lambda e: self.format_code())
        self._textbox.bind("<Control-Alt-L>", lambda e: self.format_code())
        self.bind_snippets()
        
        # Placeholder events
        self._textbox.bind("<FocusIn>", self._on_focus_in)
        self._textbox.bind("<FocusOut>", self._on_focus_out)

        self._orig_yview = self._textbox.yview
        self._textbox.yview = self._custom_yview
        
        self.apply_theme()
        
        # 5. Bağlam Çubuğu (Context Bar) - Floating UX
        self.context_bar = SilverContextBar(
            self, 
            config, 
            callbacks={
                'summarize': self._on_ctx_summarize,
                'explain': self._on_ctx_explain,
                'run': self._on_ctx_run
            }
        )
        
        # Selection Bindings
        self._textbox.bind("<<Selection>>", self._on_selection_change)
        self._textbox.bind("<Button-1>", self._on_click_clear_ctx, add="+")
        
        # Tag Configurations
        theme = self.config.THEMES[self.config.theme]
        self._textbox.tag_configure("current_line", background=theme.get('current_line_bg', '#2a2a2a'))
        self._textbox.tag_configure("error_underline", underline=True, foreground="#ff1744")
        self._textbox.tag_configure("execution_line", background="#3d3d00", foreground="#ffffff")  # Sarı ton
        
        # Highlight timer
        self._highlight_timer = None
        
        # Hata Takibi
        self.current_errors = {}  # {line_number: error_message}

    # --- Proxy Methods ---
    def insert(self, index, text, tags=None):
        self._textbox.insert(index, text, tags)
        self._on_change()

    def get(self, start, end):
        return self._textbox.get(start, end)

    def delete(self, start, end):
        self._textbox.delete(start, end)
        self._on_change()

    # --- Floating Context Bar Helpers ---
    def _on_selection_change(self, event=None):
        """Metin seçildiğinde bağlam çubuğunu göster"""
        try:
            sel_text = self._textbox.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if len(sel_text) > 2:
                # Pozisyon hesapla (Seçimin bittiği yerin biraz üstü)
                bbox = self._textbox.bbox(tk.SEL_LAST)
                if bbox:
                    x, y, w, h = bbox
                    self.context_bar.show(x + 50, y - 35)
            else:
                self.context_bar.hide()
        except tk.TclError:
            self.context_bar.hide()

    def _on_click_clear_ctx(self, event=None):
        """Boş bir yere tıklandığında barı gizle"""
        # Gecikmeli yap ki seçim temizlenmeden önce bar kapanmasın (event flow)
        self.after(100, self.context_bar.hide)

    def _on_ctx_summarize(self):
        """Seçili kodu özetle"""
        try:
            text = self._textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            if hasattr(self.master.master.master, 'on_ctx_action'): # CTkFrame stack: Editor -> ContentArea -> MainWindow
                self.master.master.master.on_ctx_action("summarize", text)
            elif hasattr(self.master.master, 'on_ctx_action'):
                self.master.master.on_ctx_action("summarize", text)
            # Fallback for deep nesting
            elif hasattr(self.master, 'on_ctx_action'):
                self.master.on_ctx_action("summarize", text)
        except:
            pass

    def _on_ctx_explain(self):
        try:
            text = self._textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            # Find MainWindow in parents
            parent = self.master
            while parent:
                if hasattr(parent, 'on_ctx_action'):
                    parent.on_ctx_action("explain", text)
                    break
                parent = parent.master
        except:
            pass

    def _on_run_ctx_action(self, action): # Generic caller
        try:
            text = self._textbox.get(tk.SEL_FIRST, tk.SEL_LAST)
            parent = self.master
            while parent:
                if hasattr(parent, 'on_ctx_action'):
                    parent.on_ctx_action(action, text)
                    break
                parent = parent.master
        except:
            pass

    def _on_ctx_run(self):
        self._on_run_ctx_action("run")

    def _on_quick_fix_request(self, line, error_msg):
        """Hızlı tamir ikonuna tıklandığında MainWindow'a bildir"""
        code_on_line = self._textbox.get(f"{line}.0", f"{line}.end").strip()
        parent = self.master
        while parent:
            if hasattr(parent, 'on_ctx_action'):
                parent.on_ctx_action("quick_fix", {
                    "line": line,
                    "error": error_msg,
                    "code": code_on_line
                })
                break
            parent = parent.master

    def set_errors(self, errors_list):
        """
        Hataları editörde göster
        errors_list: [{"line": 10, "message": "Hata mesajı"}, ...]
        """
        # Eski hataları temizle
        self._textbox.tag_remove("error_underline", "1.0", tk.END)
        self.current_errors = {}
        
        # Yeni hataları işle
        for error in errors_list:
            line_num = error.get("line", 0)
            message = error.get("message", "Bilinmeyen hata")
            
            if line_num > 0:
                self.current_errors[line_num] = message
                
                # Satırın altını kırmızı çiz
                start_index = f"{line_num}.0"
                end_index = f"{line_num}.end"
                self._textbox.tag_add("error_underline", start_index, end_index)
        
        # Satır numaralarına hataları bildir
        self.linenumbers.set_errors(self.current_errors)
    
    def clear_errors(self):
        """Tüm hataları temizle"""
        self._textbox.tag_remove("error_underline", "1.0", tk.END)
        self.current_errors = {}
        self.linenumbers.set_errors({})
    
    def highlight_execution_line(self, line_number):
        """
        Debug sırasında mevcut çalıştırılan satırı vurgula
        line_number: Vurgulanacak satır numarası
        """
        # Önceki vurguyu temizle
        self._textbox.tag_remove("execution_line", "1.0", tk.END)
        
        # Yeni satırı vurgula (sarı arka plan)
        if line_number > 0:
            start_index = f"{line_number}.0"
            end_index = f"{line_number}.end+1c"
            self._textbox.tag_add("execution_line", start_index, end_index)
            
            # Satıra scroll et
            self._textbox.see(start_index)
            
    def clear_execution_highlight(self):
        """Debug execution vurgusunu temizle"""
        self._textbox.tag_remove("execution_line", "1.0", tk.END)

    def _is_font_available(self, font_name):
        return font_name in tk.font.families()

    def _custom_yview(self, *args):
        res = self._orig_yview(*args)
        self.linenumbers.redraw()
        if hasattr(self, 'minimap'): self.minimap.redraw()
        return res

    def _on_change_ui(self, event=None):
        self.linenumbers.redraw()
        if hasattr(self, 'minimap'): self.minimap.redraw()

    def _on_change(self, event=None):
        """Called on text modification via proxy usually, but TKinter native <<Change>> is tricky.
           We rely on KeyRelease for editing. <<Change>> is for other edits."""
        self.linenumbers.redraw()
        if hasattr(self, 'minimap'): self.minimap.redraw()
        self._highlight_current_line()
        self._trigger_highlight()

    def _on_key_release(self, event=None):
        self.linenumbers.redraw()
        if hasattr(self, 'minimap'): self.minimap.redraw()
        self._highlight_current_line()
        self._trigger_highlight()
        self._match_brackets()

    def _on_key_press(self, event):
        """Klavye tuş vuruşlarını yakala (Öneri kutusu kontrolü için)"""
        print(f"Key pressed: {getattr(event, 'keysym', 'UNKNOWN')}")
        # Eğer öneri kutusu açıksa yön tuşlarıyla gez
        if hasattr(self, 'suggestion_frame') and self.suggestion_frame.winfo_ismapped():
            if event.keysym == "Down":
                current = self.suggestion_box.curselection()
                if current:
                    next_idx = (current[0] + 1) % self.suggestion_box.size()
                    self.suggestion_box.selection_clear(0, tk.END)
                    self.suggestion_box.selection_set(next_idx)
                    self.suggestion_box.see(next_idx)
                    self._on_suggestion_select()
                return "break"
            elif event.keysym == "Up":
                current = self.suggestion_box.curselection()
                if current:
                    prev_idx = (current[0] - 1) % self.suggestion_box.size()
                    self.suggestion_box.selection_clear(0, tk.END)
                    self.suggestion_box.selection_set(prev_idx)
                    self.suggestion_box.see(prev_idx)
                    self._on_suggestion_select()
                return "break"
            elif event.keysym == "Escape":
                self.hide_suggestion_box()
                return "break"
            elif event.keysym == "Return" or event.keysym == "Tab":
                if self.suggestion_box.curselection():
                    self._apply_suggestion()
                    return "break"
        
        # Undo history için separator ekle (Her kelime bitiminde veya enter'da)
        if event.char in (' ', '\n', '.', '(', ')'):
            self._textbox.edit_separator()
        
        # Otomatik Türkçe Karakter Düzeltme (Hafif İpucu)
        # Örn: eger -> eğer (Sadece kelime bitiminde boşluk bırakınca veya enterlayınca tetiklenebilir ama karmaşık)
        # Şimdilik linter bunu yapıyor.
        
        # NOTE: Tab ve Return islenmesi _on_tab_press ve _on_return icinde yapiliyor
        # Yine de fallback olarak burada kalabilir veya temizlenebilir.
        
        # İmza yardımı kontrolü (Parantez açıldığında)
        if event.char == "(":
            # Gecikmeli tetikle ki parantez yazılsın
            self.after(10, self._trigger_signature_help)
        
    def _show_context_menu(self, event):
        """Sağ tık menüsü"""
        menu = tk.Menu(self, tearoff=0)
        
        # Standart İşlemler
        menu.add_command(label="Kes", command=lambda: self._textbox.event_generate("<<Cut>>"))
        menu.add_command(label="Kopyala", command=lambda: self._textbox.event_generate("<<Copy>>"))
        menu.add_command(label="Yapıştır", command=lambda: self._textbox.event_generate("<<Paste>>"))
        menu.add_separator()
        
        # Gelişmiş İşlemler
        menu.add_command(label="Tümünü Seç", command=lambda: self._textbox.tag_add("sel", "1.0", "end"))
        
        # Python Dosyası ise Çeviri Seçeneği Ekle
        if self.file_path and self.file_path.endswith(".py"):
            menu.add_separator()
            menu.add_command(label="🐍 GümüşDil'e Çevir", command=self._translate_file_action)
            
        menu.add_separator()
        menu.add_command(label="🔍 Bul...", command=self.show_find_dialog)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _translate_file_action(self):
        """MainWindow üzerinden çeviriyi tetikle"""
        parent = self.master
        while parent:
            if hasattr(parent, 'translate_current_file'):
                parent.translate_current_file()
                break
            parent = parent.master

    def _on_paste(self, event=None):
        """Yapıştırma işleminden sonra tam vurgulama yap"""
        self.after(10, lambda: self._trigger_highlight(full=True))
        self._textbox.edit_separator()

    def _highlight_current_line(self):
        """Aktif satırı vurgula"""
        self._textbox.tag_remove("current_line", "1.0", tk.END)
        # self._textbox.tag_add("current_line", "insert linestart", "insert lineend+1c")
        
        # ASTViewer Vurgusu İçin Main Window'u Bilgilendir
        try:
            line_str = self._textbox.index("insert").split('.')[0]
            line = int(line_str)
            # Find MainWindow in parents
            parent = self.master
            while parent:
                if hasattr(parent, 'on_line_click'):
                    parent.on_line_click(line)
                    break
                parent = parent.master
        except:
            pass
        
    def _trigger_highlight(self, delay=100, full=False):
        """
        Gecikmeli vurgulama. 
        full=False: Sadece aktif satırı vurgular (Hızlı)
        full=True: Tüm dosyayı vurgular (Yavaş ama tam tutarlılık için)
        """
        if self._highlight_timer:
            self.after_cancel(self._highlight_timer)
            
        def job():
            if full:
                self.highlighter.highlight()
            else:
                curr_line = self._textbox.index("insert").split('.')[0]
                self.highlighter.highlight_line(curr_line)
                
            self._run_linter() # Canlı Hata Denetimi
            self.update_breadcrumbs()
            
            # Autocompletion logic moved to independent trigger or kept here
            self._check_autocompletion()
            
        self._highlight_timer = self.after(delay, job)

    def _check_autocompletion(self):
        """İmleç altındaki kelimeye göre öneri kutusunu yönetir"""
        try:
             current_index = self._textbox.index(tk.INSERT)
             line_start = f"{current_index.split('.')[0]}.0"
             line_text = self._textbox.get(line_start, current_index)
             
             # Sadece kelime yazılırken (alfanümerik + türkçe karakterler)
             wb = re.search(r'([a-zA-Z_ığüşöçİĞÜŞÖÇ]+)$', line_text)
             if wb:
                 word = wb.group(1)
                 if len(word) >= 2:
                     self.show_suggestion_box(word)
                 else:
                     self.hide_suggestion_box()
             else:
                 self.hide_suggestion_box()
        except:
             pass
        
        # Trigger autosuggestion if typing word chars
        # ... (Suggestion logic) ...
    # --- Autocomplete & Suggestions ---
    # Redundant methods removed, combined version exists below.

    # --- Autocomplete & Suggestions ---
    # Unified version exists below (_apply_suggestion).

    def _on_suggestion_select(self, event=None):
        pass

    def format_code(self):
        """Kodu Gümüşhane standartlarına göre formatla"""
        # 🔊 Mekanik Daktilo Sesi Efekti
        def play_mechanical_sound():
            try:
                import winsound
                import random
                import time
                for _ in range(random.randint(4, 7)):
                    # Farklı frekanslarda kısa biplerle "tıkırtı" efekti
                    freq = random.randint(800, 1500)
                    dur = random.randint(20, 50)
                    winsound.Beep(freq, dur)
                    time.sleep(random.uniform(0.02, 0.08))
            except:
                pass
        
        import threading
        threading.Thread(target=play_mechanical_sound, daemon=True).start()

        content = self.get("1.0", 'end-1c')
        formatted = GumusFormatter.format(content)
        
        # Undo history korumak için replace et
        self._textbox.delete("1.0", tk.END)
        self._textbox.insert("1.0", formatted)
        self.show_toast("Kod Gümüşhane standartlarına göre düzenlendi! ✨", "success")

    def show_toast(self, message, kind='info'):
        # MainWindow'a ulaşmaya çalış
        parent = self.master
        while parent:
            if hasattr(parent, 'show_toast'):
                parent.show_toast(message, kind)
                break
            parent = parent.master

    def _run_linter(self):
        """GümüşDil Canlı Hata Denetimi (Linter)"""
        text = self.get("1.0", 'end-1c')
        errors = []
        
        # Yasaklı Kelimeler (İngilizce/ASCII -> Türkçe Doğrusu)
        forbidden_map = {
            "var": "değişken", "let": "değişken", "degisken": "değişken",
            "if": "eğer", "eger": "eğer",
            "else": "değilse", "degilse": "değilse",
            "true": "doğru", "dogru": "doğru",
            "false": "yanlış", "yanlis": "yanlış",
            "while": "döngü", "loop": "döngü", "dongu": "döngü",
            "for": "her", 
            "function": "fonksiyon", "func": "fonksiyon", "def": "fonksiyon",
            "return": "dön", "don": "dön",
            "print": "yazdır", "yazdir": "yazdır",
            "class": "sınıf", "sinif": "sınıf",
            "new": "yeni",
            "this": "öz", "oz": "öz",
            "null": "boş", "none": "boş", "bos": "boş", 
            "break": "kır", "kir": "kır",
            "continue": "devam",
            "try": "deneme",
            "catch": "yakala",
            "modul": "modül",
            "veya": "veya" # 'or' -> veya eklenebilir ama 'veya' zaten doğru.
        }
        # İngilizce mantıksal operatörler
        forbidden_map["or"] = "veya"
        forbidden_map["and"] = "ve"
        
        # 1. Parantez ve Blok Kontrolü (Stack Based)
        stack = []
        pairs = {')':'(', '}':'{', ']':'['}
        lines = text.split('\n')
        
        in_string = False 
        string_char = None
        
        for i, line in enumerate(lines):
            line_no = i + 1
            stripped = line.strip()
            
            # Yorum satırı mı?
            if stripped.startswith("//"): continue
            
            # Karakter Analizi (Parantez Dengesi)
            col_idx = 0
            while col_idx < len(line):
                char = line[col_idx]
                
                # String Kontrolü
                if char in ('"', "'"):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                        string_char = None
                
                # Parantez (String dışındaysa)
                if not in_string:
                    if char in "({[":
                        stack.append((char, line_no))
                    elif char in ")}]":
                        if not stack:
                            errors.append({"line": line_no, "message": f"Beklenmeyen kapatma: '{char}'"})
                        else:
                            top, open_line = stack.pop()
                            if pairs[char] != top:
                                 errors.append({"line": line_no, "message": f"Uyuşmazlık: '{top}' (Satır {open_line}) beklenirken '{char}' geldi."})
                
                col_idx += 1
            
            # Yasaklı Kelime Kontrolü
            # Stringleri ve yorumları temizle (Basitçe)
            clean_line = re.sub(r'("[^"]*"|\'[^\']*\')', '', stripped) 
            words = re.findall(r'\b\w+\b', clean_line)
            
            seen_errors = set() # Aynı satırda aynı hatayı tekrar etme
            for w in words:
                if w in forbidden_map and w not in seen_errors:
                    correct = forbidden_map[w]
                    errors.append({"line": line_no, "message": f"🔍 Bak hele! '{w}' yasak! '{correct}' kullanmalısın yeğenim."})
                    seen_errors.add(w)

        # 2. Değişken Tanımı Kontrolü (Basit)
        for i, line in enumerate(lines):
             if 'değişken' in line and '=' not in line:
                  errors.append({"line": i+1, "message": "⚠️ Değişken tanımlarken değer atamayı mı unuttun yiğidim? (Örn: değişken x = 5)"})

        # Kapatılmamış parantezler
        if stack:
            top, line_no = stack[-1]
            errors.append({"line": line_no, "message": f"Kapatılmamış blok/parantez: '{top}'"})

        self.set_errors(errors)

    def set_file_path(self, path):
        """Dosya yolunu sakla ve breadcrumbs güncelle"""
        self.file_path = path
        self.update_breadcrumbs()

    def update_breadcrumbs(self):
        """İmleç konumuna göre Breadcrumbs'ı güncelle"""
        try:
            items = []
            
            # 1. Dosya Yolu
            if self.file_path:
                filename = os.path.basename(self.file_path)
                folder = os.path.dirname(self.file_path)
                
                # Proje klasörünü bulmaya çalış (Basitçe)
                # Tam yol yerine son klasörü göster
                if folder:
                    folder_name = os.path.basename(folder)
                    items.append({'text': folder_name, 'type': 'folder', 'path': folder})
                
                items.append({'text': filename, 'type': 'file', 'path': self.file_path})
            else:
                items.append({'text': 'Adsız', 'type': 'file'})
            
            # 2. Kod İçi Yapı (Scope)
            linenum = int(self._textbox.index("insert").split(".")[0])
            content = self._textbox.get("1.0", f"{linenum}.end")
            lines = content.split("\n")
            
            scope_stack = []
            
            for l in lines:
                s_line = l.strip()
                if not s_line or s_line.startswith("//"): continue
                
                match = re.search(r'^\s*(sınıf|fonksiyon|kurucu)\s+([a-zA-Z_ığüşöçİĞÜŞÖÇ]\w*)?', l)
                if match:
                    indent = len(l) - len(l.lstrip())
                    keyword = match.group(1) 
                    name = match.group(2) or ("(isimsiz)" if keyword == "kurucu" else "")
                    
                    if keyword == "kurucu" and not name: name = "kurucu"
                    
                    while scope_stack and scope_stack[-1]['indent'] >= indent:
                        scope_stack.pop()
                        
                    scope_stack.append({'name': name, 'indent': indent, 'type': 'class' if keyword == 'sınıf' else 'function'})
            
            for s in scope_stack:
                items.append({'text': s['name'], 'type': s['type']})
                
            if hasattr(self, 'breadcrumbs'):
                self.breadcrumbs.update_path(items)
                  
        except Exception:
            pass

    def show_suggestion_box(self, prefix):
        from ..core.symbols import SymbolExtractor
        
        # 1. Sabit Anahtar Kelimeler (GümüşZeka Metadatalı)
        keywords_meta = {
            "fonksiyon": {"type": "kwd", "doc": "Yeni bir fonksiyon tanımlar."},
            "eğer": {"type": "kwd", "doc": "Koşullu ifade bloğu başlatır."},
            "değilse": {"type": "kwd", "doc": "Koşul sağlanmazsa çalışacak blok."},
            "döngü": {"type": "kwd", "doc": "Bir döngü bloğu başlatır."},
            "dön": {"type": "kwd", "doc": "Fonksiyondan değer döndürür."},
            "kır": {"type": "kwd", "doc": "Döngüyü sonlandırır."},
            "devam": {"type": "kwd", "doc": "Döngünün bir sonraki adımına geçer."},
            "sınıf": {"type": "kwd", "doc": "Yeni bir nesne sınıfı tanımlar."},
            "miras": {"type": "kwd", "doc": "Bir sınıftan kalıtım alır."},
            "öz": {"type": "kwd", "doc": "Sınıfın o anki örneğini (instance) belirtir."},
            "temel": {"type": "kwd", "doc": "Üst sınıfın (superclass) metotlarına erişim sağlar."},
            "yazdır": {"type": "func", "doc": "Konsola veya terminale çıktı yazar.\n\nKullanım: yazdır(text)"},
            "girdi": {"type": "func", "doc": "Kullanıcıdan veri alır."},
            "dahil_et": {"type": "kwd", "doc": "Başka bir dosyayı koda dahil eder."},
            "değişken": {"type": "kwd", "doc": "Yeni bir değişken tanımlar."},
            "modül": {"type": "kwd", "doc": "Modül tanımlar."},
            "doğru": {"type": "bool", "doc": "Mantıksal True değeri."},
            "yanlış": {"type": "bool", "doc": "Mantıksal False değeri."},
            "yok": {"type": "null", "doc": "Değersiz (Null) ifade."},
            "dene": {"type": "kwd", "doc": "Hata yakalama bloğu başlatır."},
            "yakala": {"type": "kwd", "doc": "Yakalanan hatayı işler."},
            "uzunluk": {"type": "func", "doc": "Listenin veya metnin uzunluğunu döner."},
            "sayı": {"type": "func", "doc": "Değeri sayıya çevirir."},
            "metin": {"type": "func", "doc": "Değeri metne çevirir."},
            "zaman": {"type": "func", "doc": "Sistem zamanını döner."},
        }
        
        import difflib
        
        # Nokta (.) kontrolü - Üye tamamlama
        is_member_completion = False
        member_prefix = ""
        parent_obj = ""
        
        try:
            current_index = self._textbox.index(tk.INSERT)
            line_start = f"{current_index.split('.')[0]}.0"
            full_line_text = self._textbox.get(line_start, current_index)
            
            dot_match = re.search(r'([a-zA-Z_ığüşöçİĞÜŞÖÇ][a-zA-Z0-9_ığüşöçİĞÜŞÖÇ]*)\.([a-zA-Z0-9_ığüşöçİĞÜŞÖÇ]*)$', full_line_text)
            if dot_match:
                is_member_completion = True
                parent_obj = dot_match.group(1)
                member_prefix = dot_match.group(2)
                prefix = member_prefix
        except:
            pass

        # 2. Dinamik Semboller (Açık dosyadan)
        text = self.get("1.0", 'end-1c')
        extracted_symbols = SymbolExtractor.extract_from_text(text)
        
        all_candidates = {} # name -> meta
        
        if is_member_completion:
            # Sadece ilgili sınıfın veya nesnenin üyelerini bul (basitçe her şeyi gösterelim ama filtreli)
            # Daha gelişmiş bir analiz için parent_obj tipini bulmak gerekir.
            # Şimdilik dosyadaki tüm fonksiyonları ve değişkenleri 'üye' olarak görelim.
            for sym in extracted_symbols:
                all_candidates[sym['name']] = {"type": sym['type'], "doc": f"Üye: {sym['name']}\nTanım: Satır {sym['line']}"}
        else:
            # Hem anahtar kelimeleri hem de sembolleri ekle
            for word, meta in keywords_meta.items():
                all_candidates[word] = meta
            for sym in extracted_symbols:
                all_candidates[sym['name']] = {"type": sym['type'], "doc": f"Tanım: {sym['type'].capitalize()}\nSatır: {sym['line']}"}

        # Fuzzy matching ve Filtreleme
        suggestions = []
        if prefix:
            # 1. Tam eşleşenler veya başlayanlar (Öncelikli)
            starts = [w for w in all_candidates.keys() if w.startswith(prefix) and w != prefix]
            for w in sorted(starts):
                suggestions.append((w, all_candidates[w]))
            
            # 2. Benzer olanlar (Fuzzy) - Eğer liste çok kısa ise
            if len(suggestions) < 5:
                closes = difflib.get_close_matches(prefix, all_candidates.keys(), n=5, cutoff=0.6)
                for w in closes:
                    if w not in starts and w != prefix:
                        suggestions.append((w, all_candidates[w]))
        else:
            # Prefix yoksa (noktadan hemen sonra)
            for w in sorted(all_candidates.keys()):
                suggestions.append((w, all_candidates[w]))

        if not suggestions:
             self.hide_suggestion_box()
             return

        theme = self.config.THEMES[self.config.theme]
        if not hasattr(self, 'suggestion_box'):
            # Frame içinde Listbox ve Label (Doc)
            self.suggestion_frame = ctk.CTkFrame(self, fg_color=theme['sidebar_bg'], corner_radius=6, border_width=1, border_color=theme['border'])
            
            self.suggestion_box = tk.Listbox(
                self.suggestion_frame, 
                font=('Segoe UI', 11), 
                height=6,
                width=30,
                selectmode=tk.SINGLE,
                bg=theme['sidebar_bg'],
                fg=theme['fg'],
                selectbackground=theme['accent'],
                highlightthickness=0,
                borderwidth=0,
                relief="flat"
            )
            self.suggestion_box.pack(side="left", fill="both", expand=True, padx=2, pady=2)
            
            # Event Bindings
            self.suggestion_box.bind("<Return>", self._apply_suggestion)
            self.suggestion_box.bind("<Tab>", self._apply_suggestion)
            self.suggestion_box.bind("<Double-Button-1>", self._apply_suggestion)
            self.suggestion_box.bind("<<ListboxSelect>>", self._on_suggestion_select)
            
            # Documentation Popup (Yan tarafta çıkacak)
            self.doc_popup = None
            
        # Pozisyon Hesapla
        try:
             bbox = self._textbox.bbox(tk.INSERT)
             if bbox:
                 x, y, w, h = bbox
                 self.suggestion_frame.place(x=x + 50, y=y + 25)
                 self.suggestion_frame.lift()
        except:
             pass
        
        # Listeyi doldur
        self.current_suggestions = suggestions # Referans tut
        self.suggestion_box.delete(0, tk.END)
        
        icon_map = {"kwd": "🔑", "func": "ƒ", "class": "📦", "variable": "💎", "bool": "☯", "null": "∅"}
        
        for word, meta in suggestions:
            icon = icon_map.get(meta['type'], "🔹")
            self.suggestion_box.insert(tk.END, f"{icon} {word}")
            
        self.suggestion_box.selection_set(0)
        self._on_suggestion_select(None) # İlk elemanın dokümantasyonunu göster


    def _on_tab_press(self, event):
        """Tab tuşu basıldığında: Öneri varsa tamamla, yoksa snippet ekle, yoksa girinti yap"""
        if hasattr(self, 'suggestion_frame') and self.suggestion_frame.winfo_ismapped():
            self._apply_suggestion()
            return "break"
        
        # Öneri yoksa snippet kontrolü yap (tabanlı oto-tamamlama)
        if self.insert_snippet():
            return "break"
            
        # Varsayılan davranış (4 boşluk girinti önerilir)
        # self._textbox.insert(tk.INSERT, "    ")
        # return "break"
        return None # Tkinter varsayılan Tab davranışına izin ver

    def _on_return(self, event):
        """Enter tuşu basıldığında: Öneri varsa tamamla, yoksa yeni satır (Auto-indent)"""
        if hasattr(self, 'suggestion_frame') and self.suggestion_frame.winfo_ismapped():
            self._apply_suggestion()
            return "break"
        
        # Akıllı girinti mantığı buraya eklenebilir
        return None

    def _trigger_signature_help(self):
        """Fonksiyon parametre yardımını göster"""
        try:
            current_index = self._textbox.index(tk.INSERT)
            line_start = f"{current_index.split('.')[0]}.0"
            line_text = self._textbox.get(line_start, current_index)
            
            # Parantezden önceki kelime
            match = re.search(r'([a-zA-Z_ığüşöçİĞÜŞÖÇ][a-zA-Z0-9_ığüşöçİĞÜŞÖÇ]*)\s*\($', line_text)
            if not match: return
            
            func_name = match.group(1)
            
            # Sembollerden bul
            from ..core.symbols import SymbolExtractor
            text = self.get("1.0", tk.END)
            symbols = SymbolExtractor.extract_from_text(text)
            
            target_func = next((s for s in symbols if s['type'] == 'function' and s['name'] == func_name), None)
            
            if target_func and 'params' in target_func:
                params = target_func['params']
                self._show_signature_popup(func_name, params)
        except:
            pass

    def _show_signature_popup(self, name, params):
        """Küçük bir imza kutucuğu göster"""
        theme = self.config.THEMES[self.config.theme]
        
        if hasattr(self, 'sig_popup') and self.sig_popup:
            self.sig_popup.destroy()
            
        self.sig_popup = tk.Toplevel(self)
        self.sig_popup.wm_overrideredirect(True)
        self.sig_popup.configure(bg=theme['sidebar_bg'])
        
        # Minimalist Frame
        frame = ctk.CTkFrame(self.sig_popup, fg_color=theme['sidebar_bg'], border_width=1, border_color=theme['accent'], corner_radius=4)
        frame.pack()
        
        label = ctk.CTkLabel(
            frame, 
            text=f"ƒ {name}({params})", 
            text_color=theme['fg'],
            font=("Segoe UI", 10),
            padx=10, 
            pady=5
        )
        label.pack()
        
        # Pozisyon
        bbox = self._textbox.bbox(tk.INSERT)
        if bbox:
            x, y, w, h = bbox
            rootx = self._textbox.winfo_rootx()
            rooty = self._textbox.winfo_rooty()
            self.sig_popup.geometry(f"+{rootx + x}+{rooty + y - 30}")
            
        # 5 saniye sonra veya başka tuşa basınca kapansın
        self.after(5000, lambda: self.sig_popup.destroy() if hasattr(self, 'sig_popup') and self.sig_popup else None)

    def hide_suggestion_box(self):
        if hasattr(self, 'suggestion_frame'):
            self.suggestion_frame.place_forget()
        if hasattr(self, 'doc_popup') and self.doc_popup:
            self.doc_popup.destroy()
            self.doc_popup = None

    def bind_snippets(self):
        """Tab ile kod tamamlama şablonları (Artık _on_tab_press içinde birleşik)"""
        pass

    def _check_snippet(self, event):
        pass
             
    def insert_snippet(self, event=None):
        """Tab tuşu ile snippet ekleme"""
        if self.suggestion_box and self.suggestion_box.winfo_ismapped():
            # Eğer öneri kutusu açıksa, seçimi uygula
            return self._apply_suggestion()
             
        try:
            # İmleçten önceki kelimeyi al
            current_index = self._textbox.index(tk.INSERT)
            line_start = f"{current_index.split('.')[0]}.0"
            line_text = self._textbox.get(line_start, current_index)
            
            import re
            wb = re.search(r'([a-zA-Z_ığüşöçİĞÜŞÖÇ]+)$', line_text)
            if not wb: return
            
            keyword = wb.group(1)
            
            if self.completer:
                template = self.completer.get_snippet(keyword)
                if template:
                    # Sadece template'i ekle
                    self._textbox.insert(tk.INSERT, template)
                    
                    # İmleci parantez içine al (basitçe 2 geri git, eğer parantez varsa)
                    if "..." in template:
                        pass
                    
                    return "break" # Tab tuşunun default davranışını engelle
                
        except Exception as e:
            print(f"Snippet hatası: {e}")
            pass

    def show_find_dialog(self, event=None):
        """Modern Bul/Değiştir Paneli (Ctrl+F)"""
        self._toggle_find_bar(replace_mode=False)
        return "break" # Default davranışı engelle

    def show_replace_dialog(self, event=None):
        """Modern Değiştir Paneli (Ctrl+H)"""
        self._toggle_find_bar(replace_mode=True)
        return "break"

    def _toggle_find_bar(self, replace_mode=False):
        if hasattr(self, 'find_bar') and self.find_bar.winfo_ismapped():
            # Zaten açıksa ve mod değiştiyse modu güncelle, değilse kapat
            if replace_mode != self.find_bar.replace_mode:
                self._update_find_bar_mode(replace_mode)
            else:
                self.hide_find_bar()
        else:
            self._create_find_bar(replace_mode)
            
    def hide_find_bar(self):
        if hasattr(self, 'find_bar'):
            self.find_bar.place_forget()
            self._textbox.tag_remove("search_highlight", "1.0", tk.END)
            self._textbox.focus_set()

    def _create_find_bar(self, replace_mode):
        theme = self.config.THEMES[self.config.theme]
        
        if not hasattr(self, 'find_bar'):
            self.find_bar = ctk.CTkFrame(self, fg_color=theme['sidebar_bg'], corner_radius=5, border_width=1, border_color=theme['border'])
            self.find_bar.replace_mode = replace_mode
            
            # Üst satır: Bul
            row1 = ctk.CTkFrame(self.find_bar, fg_color="transparent")
            row1.pack(fill="x", padx=5, pady=5)
            
            self.find_entry = ctk.CTkEntry(row1, placeholder_text="Bul...", width=150, height=28, font=("Segoe UI", 12))
            self.find_entry.pack(side="left", padx=(0, 5))
            self.find_entry.bind("<Return>", self.find_next)
            self.find_entry.bind("<KeyRelease>", self._live_search)
            
            ctk.CTkButton(row1, text="↓", width=24, height=24, command=self.find_next).pack(side="left", padx=1)
            ctk.CTkButton(row1, text="↑", width=24, height=24, command=self.find_prev).pack(side="left", padx=1)
            ctk.CTkButton(row1, text="×", width=24, height=24, fg_color="transparent", hover_color="#c62828", command=self.hide_find_bar).pack(side="left", padx=(5, 0))
            
            # Alt satır: Değiştir (Opsiyonel)
            self.replace_row = ctk.CTkFrame(self.find_bar, fg_color="transparent")
            
            self.replace_entry = ctk.CTkEntry(self.replace_row, placeholder_text="Değiştir...", width=150, height=28, font=("Segoe UI", 12))
            self.replace_entry.pack(side="left", padx=(0, 5))
            
            ctk.CTkButton(self.replace_row, text="Değiştir", width=60, height=24, font=("Segoe UI", 11), command=self.replace_one).pack(side="left", padx=1)
            ctk.CTkButton(self.replace_row, text="Tümü", width=50, height=24, font=("Segoe UI", 11), command=self.replace_all).pack(side="left", padx=1)
        
        # Modu ayarla
        self._update_find_bar_mode(replace_mode)
        
        # Göster (Sağ üst köşe)
        self.find_bar.place(relx=1.0, rely=0.0, anchor="ne", x=-25, y=5)
        self.find_bar.lift()
        self.find_entry.focus_set()

    def _update_find_bar_mode(self, replace_mode):
        self.find_bar.replace_mode = replace_mode
        if replace_mode:
            self.replace_row.pack(fill="x", padx=5, pady=(0, 5))
        else:
            self.replace_row.pack_forget()

    def _live_search(self, event=None):
        query = self.find_entry.get()
        self._textbox.tag_remove("search_highlight", "1.0", tk.END)
        if not query: return
        
        count = 0
        start_pos = "1.0"
        while True:
            pos = self._textbox.search(query, start_pos, stopindex=tk.END)
            if not pos: break
            
            end_pos = f"{pos}+{len(query)}c"
            self._textbox.tag_add("search_highlight", pos, end_pos)
            start_pos = end_pos
            count += 1
            if count > 1000: break # Performans koruması

    def find_next(self, event=None):
        query = self.find_entry.get()
        if not query: return
        
        start_pos = self._textbox.index(tk.INSERT) + "+1c"
        pos = self._textbox.search(query, start_pos, stopindex=tk.END)
        if not pos:
             pos = self._textbox.search(query, "1.0", stopindex=tk.END)
        
        if pos:
            self._highlight_match(pos, len(query))

    def find_prev(self, event=None):
        query = self.find_entry.get()
        if not query: return
        
        start_pos = self._textbox.index(tk.INSERT)
        pos = self._textbox.search(query, start_pos, stopindex="1.0", backwards=True)
        if not pos:
             pos = self._textbox.search(query, tk.END, stopindex="1.0", backwards=True)
             
        if pos:
            self._highlight_match(pos, len(query))

    def _highlight_match(self, pos, length):
        end_pos = f"{pos}+{length}c"
        self._textbox.tag_remove("sel", "1.0", tk.END)
        self._textbox.tag_add("sel", pos, end_pos)
        self._textbox.mark_set(tk.INSERT, end_pos)
        self._textbox.see(pos)

    def replace_one(self):
        query = self.find_entry.get()
        replacement = self.replace_entry.get()
        if not query: return
        
        # Seçim varsa ve eşleşiyorsa değiştir
        try:
            sel_start = self._textbox.index("sel.first")
            sel_end = self._textbox.index("sel.last")
            if self._textbox.get(sel_start, sel_end) == query:
                self._textbox.delete(sel_start, sel_end)
                self._textbox.insert(sel_start, replacement)
                self.find_next()
            else:
                self.find_next()
        except:
            self.find_next()

    def replace_all(self):
        query = self.find_entry.get()
        replacement = self.replace_entry.get()
        if not query: return
        
        text = self._textbox.get("1.0", 'end-1c')
        new_text = text.replace(query, replacement)
        
        self._textbox.delete("1.0", tk.END)
        self._textbox.insert("1.0", new_text)
        self._live_search()

    def toggle_comment(self, event=None):
        """Satırı yorum satırı yap/kaldır (//)"""
        try:
            # Seçim var mı?
            try:
                sel_start = self._textbox.index("sel.first")
                sel_end = self._textbox.index("sel.last")
                # Çoklu satır (Selection based - basitleştirilmiş: her satıra uygula)
                start_line = int(sel_start.split('.')[0])
                end_line = int(sel_end.split('.')[0])
                
                # Eğer son satırın başındaysa (seçim oraya kadar gelmişse) ve içerik yoksa dahil etme
                if sel_end.split('.')[1] == '0' and end_line > start_line:
                    end_line -= 1
                
                for line_no in range(start_line, end_line + 1):
                    self._toggle_comment_line(line_no)
                    
            except tk.TclError:
                # Seçim yok, aktif satır
                current_index = self._textbox.index(tk.INSERT)
                line_no = int(current_index.split('.')[0])
                self._toggle_comment_line(line_no)
            
            self._trigger_highlight()
            return "break"
        except Exception as e:
            pass

    def _toggle_comment_line(self, line_no):
        start_idx = f"{line_no}.0"
        end_idx = f"{line_no}.end"
        line_text = self._textbox.get(start_idx, end_idx)
        
        # Eğer satır zaten yorum ise kaldır
        if line_text.lstrip().startswith("//"):
            # Yorumu kaldır (Sadece ilk //'yi)
            import re
            new_text = re.sub(r"^(\s*)// ?(.*)", r"\1\2", line_text)
            self._textbox.delete(start_idx, end_idx)
            self._textbox.insert(start_idx, new_text)
        else:
            # Yorum ekle
            self._textbox.insert(start_idx, "// ")

    def move_line_up(self, event=None):
        """Satırı yukarı taşı"""
        try:
            current_index = self._textbox.index(tk.INSERT)
            line_no = int(current_index.split('.')[0])
            
            if line_no <= 1: return "break"
            
            current_text = self._textbox.get(f"{line_no}.0", f"{line_no + 1}.0")
            prev_text = self._textbox.get(f"{line_no - 1}.0", f"{line_no}.0")
            
            # Yer değiştir (Satırın tamamını silip yerleştiriyoruz, \n dahil)
            self._textbox.delete(f"{line_no - 1}.0", f"{line_no + 1}.0")
            self._textbox.insert(f"{line_no - 1}.0", current_text + prev_text) # Bu logic biraz tricky, basitçe takas etsek daha iyi.
            
            # Daha stabil yöntem:
            # 1. Mevcut satırı kes
            # 2. Üst satırın üstüne yapıştır
            # Ama newline karakterleri sorun çıkarabilir.
            
            # Basitçe:
            # text = get(line)
            # delete(line)
            # insert(line-1, text)
            # cursor'ı takip ettir
            
            # Hatalı logic yukarıda, basit yöntemle tekrar deneyelim:
            self._textbox.delete(f"{line_no}.0", f"{line_no+1}.0") # Mevcutu sil
            self._textbox.insert(f"{line_no-1}.0", current_text) # Bir üste ekle
            
            # Cursor takibi
            self._textbox.mark_set(tk.INSERT, f"{line_no - 1}.0")
            self._textbox.see(tk.INSERT)
            
            self._trigger_highlight()
            return "break"
        except:
             pass

    def move_line_down(self, event=None):
        """Satırı aşağı taşı"""
        try:
            current_index = self._textbox.index(tk.INSERT)
            line_no = int(current_index.split('.')[0])
            
            # Son satır kontrolü (biraz zor ama try/except halleder)
            next_line_idx = f"{line_no + 1}.0"
            if not self._textbox.get(next_line_idx, f"{next_line_idx}+1c"): return "break"
            
            current_text = self._textbox.get(f"{line_no}.0", f"{line_no + 1}.0")
            
            self._textbox.delete(f"{line_no}.0", f"{line_no + 1}.0")
            self._textbox.insert(f"{line_no + 1}.0", current_text)
            
            # Cursor takibi
            self._textbox.mark_set(tk.INSERT, f"{line_no + 1}.0")
            self._textbox.see(tk.INSERT)
            
            self._trigger_highlight()
            return "break"
        except:
             pass

    def rename_symbol(self, event=None):
        """İmleçteki kelimeyi dosya genelinde yeniden adlandır (F2)"""
        try:
            # İmleçteki kelimeyi bul
            current_index = self._textbox.index(tk.INSERT)
            line_start = f"{current_index.split('.')[0]}.0"
            line_text = self._textbox.get(line_start, current_index.split('.')[0] + ".end")
            column = int(current_index.split('.')[1])
            
            # Regex ile kelime sınırlarını bul
            import re
            words = list(re.finditer(r'\b[a-zA-Z_ığüşöçİĞÜŞÖÇ][a-zA-Z0-9_ığüşöçİĞÜŞÖÇ]*\b', line_text))
            
            target_word = ""
            for m in words:
                if m.start() <= column <= m.end():
                    target_word = m.group()
                    break
            
            if not target_word: return
            
            # Yeni isim iste
            dialog = ctk.CTkInputDialog(text=f"'{target_word}' için yeni isim:", title="Yeniden Adlandır")
            # Dialog penceresini ortala (biraz hacky ama işe yarar)
            # dialog geometry setlemek zor, o yüzden varsayılan kalır.
            
            new_name = dialog.get_input()
            if not new_name or new_name == target_word: return
            
            # Tüm dosyadaki eşleşmeleri değiştir
            # Not: Bu basit bir replace işlemidir, scope analizi yapmaz.
            # Gerçek refactoring için parser gerekir ama şimdilik "Find & Replace All" mantığı yeterli.
            
            content = self._textbox.get("1.0", 'end-1c')
            
            # Regex ile tam kelime eşleşmesi (whole word search)
            pattern = re.compile(r'\b' + re.escape(target_word) + r'\b')
            new_content = pattern.sub(new_name, content)
            
            # İçeriği güncelle (Scroll koruyarak)
            self._textbox.delete("1.0", tk.END)
            self._textbox.insert("1.0", new_content)
            
            # Cursor'ı geri yükle (yaklaşık)
            self._textbox.mark_set(tk.INSERT, current_index)
            self._textbox.see(tk.INSERT)
            
            # Highlight ve Bildirim
            self._trigger_highlight()
            # Durum çubuğuna mesaj gönderilebilir (MainWindow üzerinden)
            
        except Exception as e:
            # print(f"Rename Error: {e}")
            pass

    def delete_current_line(self, event=None):
        """Satırı sil (Ctrl+Shift+K)"""
        try:
            current_index = self._textbox.index(tk.INSERT)
            line_no = int(current_index.split('.')[0])
            self._textbox.delete(f"{line_no}.0", f"{line_no + 1}.0")
            self._trigger_highlight()
            return "break"
        except:
            pass

    def _apply_suggestion(self, event=None):
        if not hasattr(self, 'suggestion_box'): return
        
        selection = self.suggestion_box.curselection()
        if not selection: return
        
        # Seçilen metni al (İkonu temizle)
        raw_text = self.suggestion_box.get(selection[0])
        # Örnek: "🔹 fonksiyon" -> "fonksiyon"
        word = raw_text.split(" ", 1)[1] if " " in raw_text else raw_text
        
        self.hide_suggestion_box()
        
        # Mevcut yarım kelimeyi silip tamamını yaz
        try:
             current_index = self._textbox.index(tk.INSERT)
             line_start = f"{current_index.split('.')[0]}.0"
             line_text = self._textbox.get(line_start, current_index)
             import re
             # Noktalı veya noktasız kelimeyi yakala
             wb = re.search(r'([a-zA-Z_ığüşöçİĞÜŞÖÇ]+)(\.?)([a-zA-Z_ığüşöçİĞÜŞÖÇ]*)$', line_text)
             if wb:
                 full_word_match = wb.group(0)
                 start_char = wb.start(0)
                 
                 line_no = current_index.split('.')[0]
                 start_idx = f"{line_no}.{start_char}"
                 
                 # Eski (yarım) kısmı sil
                 self._textbox.delete(start_idx, tk.INSERT)
                 # Tam kelimeyi yaz
                 if wb.group(2) == ".": # Nesne.üye durumu
                     self._textbox.insert(start_idx, f"{wb.group(1)}.{word}")
                 else:
                     self._textbox.insert(start_idx, word)
                 
                 # 🚀 SNIPPET UYGULA (AutoCompleter ile)
                 if self.completer:
                     snippet = self.completer.get_snippet(word)
                     if snippet:
                         self._textbox.insert(tk.INSERT, snippet)
                         # İmleci akıllı pozisyona taşı
                         if "(" in snippet and ")" in snippet:
                             # Parantez içine git
                             self._textbox.mark_set("insert", f"insert -{len(snippet)-2}c")
                         elif "{" in snippet:
                             # Blok içine git
                             self._textbox.mark_set("insert", "insert -3c")
                             self._textbox.mark_set("insert", "insert -3c")
        except Exception as e:
             print(f"Snippet uygulama hatası: {e}")
        
        return "break"

    def _on_suggestion_select(self, event=None):
        if not hasattr(self, 'suggestion_box') or not self.suggestion_box.curselection():
            if hasattr(self, 'doc_popup') and self.doc_popup:
                self.doc_popup.destroy()
                self.doc_popup = None
            return

        try:
            index = self.suggestion_box.curselection()[0]
            if index >= len(self.current_suggestions): return
            
            word, meta = self.current_suggestions[index]
            doc_text = meta.get('doc', '')
            
            if not doc_text:
                if hasattr(self, 'doc_popup') and self.doc_popup:
                    self.doc_popup.destroy()
                    self.doc_popup = None
                return
                
            theme = self.config.THEMES[self.config.theme]
            
            # Popup oluştur/güncelle (Sade ve Şık)
            if not self.doc_popup:
                self.doc_popup = tk.Toplevel(self)
                self.doc_popup.wm_overrideredirect(True)
                self.doc_popup.configure(bg=theme['sidebar_bg'])
                
                # Standard Frame
                self.doc_inner = ctk.CTkFrame(
                    self.doc_popup, 
                    fg_color=theme['sidebar_bg'], 
                    border_width=1, 
                    border_color=theme['border'],
                    corner_radius=4
                )
                self.doc_inner.pack(fill="both", expand=True)
                
                self.doc_label = ctk.CTkLabel(
                    self.doc_inner,
                    text="",
                    justify="left",
                    text_color=theme['fg'],
                    font=('Segoe UI', 11),
                    padx=12,
                    pady=8,
                    wraplength=250
                )
                self.doc_label.pack()
            
            self.doc_label.configure(text=doc_text)
            
            # Konumlandır (Listenin sağına)
            self.doc_popup.update_idletasks()
            frame_x = self.suggestion_frame.winfo_rootx()
            frame_y = self.suggestion_frame.winfo_rooty()
            frame_w = self.suggestion_frame.winfo_width()
            
            # Ekran sınırlarını kontrol et
            screen_w = self.doc_popup.winfo_screenwidth()
            if frame_x + frame_w + 260 > screen_w:
                # Sola çıkar
                self.doc_popup.geometry(f"+{frame_x - 265}+{frame_y}")
            else:
                self.doc_popup.geometry(f"+{frame_x + frame_w + 5}+{frame_y}")
            
            self.doc_popup.lift()
            # Şeffaflık kaldırıldı, daha net görünüm
            
        except Exception as e:
            pass

    def apply_theme(self):
        theme = self.config.THEMES[self.config.theme]
        
        # Frame border rengi
        self.configure(fg_color=theme['sidebar_bg'])
        
        # Textbox renkleri
        self.textbox.configure(
            fg_color=theme['editor_bg'], 
            text_color=theme['fg'],
            border_color=theme.get('border', theme['accent'])
        )
        self.linenumbers.apply_theme()
        if hasattr(self, 'minimap'): self.minimap.apply_theme()
        
        try:
            self._textbox.configure(
                 background=theme['editor_bg'],
                 foreground=theme['fg'],
                 insertbackground=theme['accent'],  # Cursor rengi
                 selectbackground=theme['select_bg'],
                 selectforeground=theme['fg']
            )
        except:
            pass
            
        # Re-setup tags for theme change
        if hasattr(self, 'highlighter'):
            self.highlighter.setup_tags()
            self.highlighter.highlight()
        
        # Placeholder tag
        self._textbox.tag_config("placeholder", foreground=theme.get('comment', '#6a9955'), font=('Consolas', 13, 'italic'))
        
        # Hata alt çizgi stili (Kırmızı dalgalı çizgi simülasyonu - TKinter'da alt çizgi ile yapılır)
        self._textbox.tag_config("error_underline", underline=True, underlinefg="#ff1744")
        
        # Aktif satır vurgusu
        highlight_bg = theme.get('hover', '#2c313a')
        # Eğer hover rengi çok koyuysa biraz açabiliriz ama şimdilik theme['hover'] kullanalım
        self._textbox.tag_config("current_line", background=highlight_bg)
        self._textbox.tag_lower("current_line") # Yazının arkasında kalsın
        
        # Vizualizasyon satır vurgusu (Altın Sarısı / Amber)
        exec_bg = "#4d4010" if 'dark' in self.config.theme or 'premium' in self.config.theme else "#fff6cc"
        if theme.get('name') == '👾 Cyberpunk': exec_bg = "#3d002e" # Cyberpunk için özel
        
        self._textbox.tag_config("execution_line", background=exec_bg)
        self._textbox.tag_lower("execution_line")
        
        # Parantez Eşleştirme Stili
        match_bg = "#3e4451" if 'dark' in self.config.theme else "#c4c4c4"
        self._textbox.tag_config("bracket_match", background=theme['comment'], foreground=theme['bg']) 
        
        # Arama Vurgusu
        self._textbox.tag_config("search_highlight", background="#515c6a", foreground="white") # VS Code benzeri
    
    def show_placeholder(self):
        """Placeholder text göster"""
        if not self.has_content:
            self._textbox.insert('1.0', self.placeholder_text, "placeholder")
            self.has_content = False
    
    def hide_placeholder(self):
        """Placeholder text gizle"""
        # Eğer içerik yoksa sil (Placeholder varsa)
        if not self.has_content:
             # Placeholder tag varsa veya metin placeholder ile eşleşiyorsa
             current_text = self._textbox.get("1.0", "end-1c")
             if current_text == self.placeholder_text:
                 self._textbox.delete('1.0', tk.END)
    
    def _on_focus_in(self, event=None):
        """Focus alındığında placeholder'ı gizle"""
        self.hide_placeholder()
        # Ensure caret is visible
        self._textbox.configure(insertbackground=self.config.THEMES[self.config.theme]['accent'])

    def _on_focus_out(self, event=None):
        """Focus kaybedildiğinde boşsa placeholder göster"""
        content = self.get("1.0", "end-1c").strip()
        if not content:
            self.has_content = False
            self.show_placeholder()
        else:
            self.has_content = True

    def _on_click_editor(self, event):
        """Editöre tıklandığında kesin odaklan"""
        self._textbox.focus_set()
        self.hide_placeholder()
        # Normal click işlemleri devam etsin
        return None


    def _match_brackets(self, event=None):
        """Parantez Eşleştirme"""
        self._textbox.tag_remove("bracket_match", "1.0", tk.END)
        
        try:
            # İmleç pozisyonu
            insert_idx = self._textbox.index(tk.INSERT)
            
            # İmlecin solundaki ve sağındaki karakterlere bak
            # current: imlecin sağındaki, prev: imlecin solundaki
            current_char = self._textbox.get(insert_idx, f"{insert_idx}+1c")
            prev_char = self._textbox.get(f"{insert_idx}-1c", insert_idx)
            
            check_char = None
            check_index = None
            
            # Öncelik: imleç parantezin sağındaysa (kapanıştan hemen sonra veya açılıştan hemen hatra)
            if prev_char in "(){}[]":
                check_char = prev_char
                check_index = f"{insert_idx}-1c"
            elif current_char in "(){}[]":
                check_char = current_char
                check_index = insert_idx
                
            if not check_char: return
            
            # Eşleşme haritası
            pairs = {')':'(', '}':'{', ']':'[', '(':')', '{':'}', '[':']'}
            is_close = check_char in ")}]"
            target = pairs[check_char]
            
            # Arama yönü
            match_index = None
            start_index = check_index
            
            # Tkinter search kullanımı
            # Not: İç içe parantezleri saymak lazım, basit search yetmez.
            # Ancak basitlik için şimdilik sadece string olmayan ilk eşleşmeye bakalım.
            # Daha robust bir yöntem için metni taramak gerekir.
            
            text_content = self._textbox.get("1.0", tk.END)
            # Bu işlem büyük dosyalarda yavaş olabilir, optimize edilebilir.
            # Şimdilik basitçe yakındaki 5000 karakteri tarayalım.
            
            # Basit Yöntem:
            count = 1
            direction = -1 if is_close else 1
            step = "1c"
            
            limit = 2000 # Karakter limiti
            search_idx = self._textbox.index(f"{start_index}{'+' if direction==1 else '-'}{step}")
            
            while limit > 0:
                char = self._textbox.get(search_idx, f"{search_idx}+1c")
                if not char: break # EOF/BOF
                
                if char == check_char:
                    count += 1
                elif char == target:
                    count -= 1
                    
                if count == 0:
                    match_index = search_idx
                    break
                    
                limit -= 1
                # Move index
                if direction == 1:
                     search_idx = self._textbox.index(f"{search_idx}+1c")
                else:
                     search_idx = self._textbox.index(f"{search_idx}-1c")
            
            if match_index:
                self._textbox.tag_add("bracket_match", check_index, f"{check_index}+1c")
                self._textbox.tag_add("bracket_match", match_index, f"{match_index}+1c")
                
        except Exception as e:
            pass
            
    def _on_return(self, event=None):
        """Akıllı Girintileme (Smart Indent)"""
        try:
            # Mevcut satırı al
            current_index = self._textbox.index(tk.INSERT)
            line_start = f"{current_index.split('.')[0]}.0"
            line_text = self._textbox.get(line_start, current_index)
            
            # Mevcut girintiyi bul
            import re
            match = re.match(r"^(\s*)", line_text)
            current_indent = match.group(1) if match else ""
            
            # Eğer satır '{', '(', '[' ile bitiyorsa veya blok başlatıcı kelimeler varsa
            should_indent = False
            if self.completer:
                should_indent = self.completer.should_indent(line_text)
            else:
                 # Fallback (AutoCompleter yüklenemezse)
                 stripped = line_text.strip()
                 should_indent = stripped.endswith(("{", "(", ":", "[")) or \
                                 stripped.startswith(("eğer", "değilse", "yoksa", "döngü", "fonksiyon", "sınıf", "dene", "yakala"))
                            
            new_indent = current_indent
            if should_indent:
                new_indent += "    " # 4 boşluk (veya \t)
            
            # Yeni satır + girinti ekle
            self._textbox.insert(tk.INSERT, "\n" + new_indent)
            self._textbox.see(tk.INSERT)
            
            # Line numbers update
            self.linenumbers.redraw()
            if hasattr(self, 'minimap'): self.minimap.redraw()
            
            return "break" # Default enter davranışını engelle
        except Exception as e:
            # print(f"Indent Error: {e}")
            pass

    # Proxy Metotları (MainWindow için)
    def see(self, index):
        self._textbox.see(index)
        self.linenumbers.redraw()
        if hasattr(self, 'minimap'): self.minimap.redraw()
    
    def tag_add(self, tagName, index1, *args):
        self._textbox.tag_add(tagName, index1, *args)
        
    def tag_remove(self, tagName, index1, index2=None):
        self._textbox.tag_remove(tagName, index1, index2)
        
    def tag_config(self, tagName, **kwargs):
        self._textbox.tag_config(tagName, **kwargs)
        
    def get(self, index1, index2=None):
        return self._textbox.get(index1, index2)
        
    def delete(self, index1, index2=None):
        self._textbox.delete(index1, index2)
        self.linenumbers.redraw()
        if hasattr(self, 'minimap'): self.minimap.redraw()
        self._trigger_highlight()
        
    def insert(self, index, text, *args):
        self._textbox.insert(index, text, *args)
        self.linenumbers.redraw()
        if hasattr(self, 'minimap'): self.minimap.redraw()
        self._trigger_highlight()
        
    def bind(self, sequence=None, command=None, add=None):
        if add:
            self._textbox.bind(sequence, command, add)
        else:
            self._textbox.bind(sequence, command)

    def change_font_size(self, delta):
        """Font boyutunu değiştir (Ctrl +/-)"""
        try:
            # Mevcut fontu al (CTkFont veya tuple olabilir)
            current_font = self._textbox.cget("font")
            
            # Font özelliklerini ayrıştır
            name = "Consolas"
            size = 13
            weight = "normal"
            
            if isinstance(current_font, (tuple, list)):
                # Tkinter tuple formatı: ('Family', size, 'weight')
                if len(current_font) >= 1: name = current_font[0]
                if len(current_font) >= 2: size = int(current_font[1])
                if len(current_font) >= 3: weight = current_font[2]
            elif hasattr(current_font, 'cget'):
                # CTkFont object
                name = current_font.cget("family")
                size = current_font.cget("size")
                weight = current_font.cget("weight")
            
            # Yeni boyutu hesapla
            new_size = size + delta
            if new_size < 8: new_size = 8
            if new_size > 36: new_size = 36
            
            # Fontu güncelle
            new_font = (name, new_size) # Tuple olarak set edelim, daha güvenli
            self._textbox.configure(font=new_font)
            
            # Line numbers da etkilenebilir ama onlar sabit kalsa da olur şimdilik
            # self.linenumbers.configure(font=(name, new_size)) # Opsiyonel
            self.linenumbers.redraw() # En azından satır yükseklikleri değişeceği için redraw lazım
            
        except Exception as e:
            # print(f"Font change error: {e}")
            pass
