import customtkinter as ctk
import re
import tkinter as tk
import time
from ..core.error_translator import ErrorTranslator

class Terminal(ctk.CTkFrame):
    def __init__(self, parent, config, **kwargs):
        super().__init__(parent, **kwargs)
        self.config = config
        self.input_callback = None
        
        # Hata Gruplama (Error Aggregation)
        self.last_error_signature = None
        self.error_count = 0
        self.error_lines = []
        
        # 🆕 Komut Geçmişi
        self.history = []
        self.history_index = -1
        
        # 🆕 Otomatik Tamamlama
        self.completions = [
            "yazdır", "eğer", "değilse", "döngü", "fonksiyon", 
            "değişken", "sınıf", "modül", "dön", "doğru", "yanlış",
            "deneme", "yakala", "ve", "veya", "her", "kurucu", "öz"
        ]
        
        # 1. Output (Log) Area
        self.output_area = ctk.CTkTextbox(self, activate_scrollbars=True)
        self.output_area.pack(side="top", fill="both", expand=True, padx=2, pady=(2, 0))
        self.output_area.configure(
            state='disabled',
            font=('Consolas', 12),
            wrap='word'
        )
        
        # Terminale tıklayınca input'a focusla
        self.output_area.bind("<Button-1>", lambda e: self.input_entry.focus_set())
        
        # 🆕 Kopyala kısayolu için output binding
        self.output_area.bind("<Control-c>", self._copy_output)
        
        # 2. Input Area - Debug için kırmızı border
        self.input_frame = ctk.CTkFrame(self, height=40, fg_color="transparent")
        self.input_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        
        self.prompt_label = ctk.CTkLabel(self.input_frame, text=" ⌨️ GİRDİ > ", font=('Consolas', 11, 'bold'))
        self.prompt_label.pack(side="left")
        
        self.input_entry = ctk.CTkEntry(
            self.input_frame, 
            font=('Consolas', 12),
            placeholder_text="Klavye girişi için buraya yazıp ENTER'a basın...",
            height=32,
            corner_radius=16,
            border_width=1
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.input_entry.bind("<Return>", self._on_enter_pressed)
        
        # 🆕 History kısayolları
        self.input_entry.bind("<Up>", self._on_history_up)
        self.input_entry.bind("<Down>", self._on_history_down)
        
        # 🆕 Auto-complete
        self.input_entry.bind("<Tab>", self._on_tab_complete)
        
        # 🆕 Yapıştır kısayolu
        self.input_entry.bind("<Control-v>", self._paste_input)
        
        # 🆕 Input değişikliği için syntax highlighting
        self.input_entry.bind("<KeyRelease>", self._on_input_change)
        
        # Tag config
        self._textbox = self.output_area._textbox # Access underlying TK widget
        theme = self.config.THEMES[self.config.theme]
        
        self._textbox.tag_config('suggestion', foreground='#22c55e')
        self._textbox.tag_config('user_input', foreground=theme['accent']) 
        self._textbox.tag_config('error_summary', foreground=theme['comment'], font=('Consolas', 11, 'italic'))
        
        # Hata ve Uyarı Renkleri
        self._textbox.tag_config('error', foreground='#ff4d4d', font=('Consolas', 12, 'bold')) # Kırmızı
        self._textbox.tag_config('warning', foreground=theme['accent'], font=('Consolas', 12, 'bold')) # Tema Akranı
        self._textbox.tag_config('keyword', foreground=theme['keyword'])
        self._textbox.tag_config('function', foreground=theme['function'])
        
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        self.apply_theme()

    def set_input_callback(self, callback):
        self.input_callback = callback

    def _on_enter_pressed(self, event):
        text = self.input_entry.get()
        self.input_entry.delete(0, tk.END)
        
        # 🆕 Komutu geçmişe ekle
        self.add_to_history(text)
        
        # Ekrana bas (echo)
        self.write_text(f"> {text}\n")
        
        # Callback çalıştır (Process'e gönder)
        if self.input_callback:
            self.input_callback(text)

    def apply_theme(self):
        theme = self.config.THEMES[self.config.theme]
        
        self.configure(fg_color=theme['bg'])
        self.input_frame.configure(fg_color=theme['bg'])
        
        self.output_area.configure(
            fg_color=theme['terminal_bg'],
            text_color=theme['terminal_fg']
        )
        
        self.input_entry.configure(
            fg_color=theme['terminal_bg'],
            text_color=theme['terminal_fg'],
            border_color=theme['accent']
        )
        
        self.prompt_label.configure(text_color=theme['accent'])
    
    def _strip_ansi(self, text):
        return self.ansi_escape.sub('', text)

    def write_text(self, text, tags=None):
        """Terminale metin yaz (Hata çevirisi ve renklendirme ile)"""
        clean_text = self._strip_ansi(text)
        
        # Hata Çevirisi
        translated_text = clean_text
        
        if tags is None:
            try:
                # Çeviriyi dene
                translated_text = ErrorTranslator.translate(clean_text)
                
                # Renklendirme etiketini belirle
                if "🔴" in translated_text:
                    tags = "error"
                elif "⚠️" in translated_text:
                    tags = "warning"
            except Exception as e:
                print(f"[ErrorTranslator] Çeviri hatası: {e}")
                translated_text = clean_text  # Fallback
        
        try:
             self.output_area.configure(state='normal')
             
             if tags:
                 # Tag desteği için underlying widget kullan
                 self._textbox.insert("end", translated_text, tags)
             else:
                 self.output_area.insert("end", translated_text)
             
             self.output_area.see("end")
             self.output_area.configure(state='disabled')
        except Exception as e:
             print(f"[Terminal] Yazma hatası: {e}")

    def write_smart_error(self, error_json):
        """Aynı hatadan peş peşe gelirse gruplar ve GümüşTamir butonu ekler"""
        try:
            import json
            data = json.loads(error_json)
            
            # Tüm hata tiplerini grupla
            if isinstance(data, dict) and data.get("type") in ["syntax_error", "runtime_error", "lexer_error", "parser_error"]:
                signature = data.get("message", "")
                line_no = data.get("line", 0)
                
                if signature == self.last_error_signature:
                    self.error_count += 1
                    self.error_lines.append(str(line_no))
                    
                    self.output_area.configure(state='normal')
                    start_index = self.output_area.index("end-2l linestart")
                    self.output_area.delete(start_index, "end-1c")
                    
                    summary_msg = f" ... (Bu hata {self.error_count} kez tekrarlandı. Satırlar: {', '.join(self.error_lines[:5])}{'...' if len(self.error_lines)>5 else ''})\n"
                    self.output_area.insert("end", summary_msg, "error_summary")
                    self.output_area.configure(state='disabled')
                    return
                else:
                    self.last_error_signature = signature
                    self.error_count = 1
                    self.error_lines = [str(line_no)]
                    
                    # 🔧 GümüşTamir Entegrasyonu
                    msg = f"🔴 HATA [Satır {line_no}]: {signature}  "
                    self.write_text_tag(msg, "error")
                    
                    # Tıklanabilir Tamir Bağlantısı
                    fix_id = f"fix_{line_no}_{int(time.time())}" if 'time' in globals() else f"fix_{line_no}"
                    import time
                    self._textbox.tag_config("tamir", foreground="#00e676", underline=1, font=('Consolas', 10, 'bold'))
                    self._textbox.tag_bind("tamir", "<Enter>", lambda e: self._textbox.config(cursor="hand2"))
                    self._textbox.tag_bind("tamir", "<Leave>", lambda e: self._textbox.config(cursor="xterm"))
                    
                    self.output_area.configure(state='normal')
                    self._textbox.insert("end", " 🔨 GümüşTamir'i Başlat\n", "tamir")
                    self._textbox.tag_bind("tamir", "<Button-1>", lambda e, d=data: self._on_fix_request(d))
                    self.output_area.configure(state='disabled')
                    self.output_area.see("end")
                    return

            self.write_text(error_json + "\n")
            self.last_error_signature = None
            
        except:
            self.write_text(error_json + "\n")
            self.last_error_signature = None

    def _on_fix_request(self, error_data):
        """Kullanıcı tamir butonuna bastığında MainWindow'a sinyal gönder"""
        if hasattr(self, 'master') and hasattr(self.master, '_on_fix_request'):
            self.master._on_fix_request(error_data)
        elif hasattr(self, 'fix_callback') and self.fix_callback:
            self.fix_callback(error_data)

    def write_text_tag(self, text, tag):
        clean_text = self._strip_ansi(text)
        self.output_area.configure(state='normal')
        self.output_area._textbox.insert("end", clean_text, tag)
        self.output_area.see("end")
        self.output_area.configure(state='disabled')
        
    def clear(self):
        self.output_area.configure(state='normal')
        self.output_area.delete('0.0', "end")
        self.output_area.configure(state='disabled')

    def see(self, index):
        self.output_area.see(index)
    
    # 🆕 Komut Geçmişi Fonksiyonları
    def _on_history_up(self, event):
        """Yukarı ok ile geçmişte git"""
        if not self.history:
            return "break"
            
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.history[-(self.history_index + 1)])
        return "break"  # Event'i durdur
    
    def _on_history_down(self, event):
        """Aşağı ok ile geçmişte geri git"""
        if not self.history:
            return "break"
            
        if self.history_index > 0:
            self.history_index -= 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.history[-(self.history_index + 1)])
        elif self.history_index == 0:
            self.history_index = -1
            self.input_entry.delete(0, tk.END)
        return "break"
    
    # 🆕 Otomatik Tamamlama
    def _on_tab_complete(self, event):
        """Tab ile otomatik tamamlama"""
        current_text = self.input_entry.get().strip()
        if not current_text:
            return "break"
            
        # En uygun eşleşmeyi bul
        for completion in self.completions:
            if completion.startswith(current_text):
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, completion)
                return "break"
        return "break"
    
    # 🆕 Input Syntax Highlighting
    def _on_input_change(self, event=None):
        """Input'daki metne göre renklendirme"""
        text = self.input_entry.get().strip()
        theme = self.config.THEMES[self.config.theme]
        
        # Keyword-Color Table
        syntax = {
            "yazdır": theme.get('function', "#569cd6"),
            "eğer": theme.get('keyword', "#c586c0"),
            "değilse": theme.get('keyword', "#c586c0"),
            "döngü": theme.get('keyword', "#dcdcaa"),
            "fonksiyon": theme.get('function', "#4ec9b0"),
            "değişken": theme.get('accent', "#9cdcfe"),
            "dön": theme.get('keyword', "#c586c0"),
            "sınıf": theme.get('class', "#ffab40")
        }
        
        colored = False
        for kw, color in syntax.items():
            if text.startswith(kw):
                self.input_entry.configure(text_color=color)
                colored = True
                break
        
        if not colored:
            self.input_entry.configure(text_color=theme['terminal_fg'])
    
    # 🆕 Kopyala/Yapıştır
    def _copy_output(self, event):
        """Terminal çıktısından kopyala"""
        try:
            # CustomTkinter'da seçim kontrolü
            try:
                selected = self.output_area.get("sel.first", "sel.last")
                if selected.strip():
                    self.clipboard_clear()
                    self.clipboard_append(selected)
                    return "break"
            except:
                pass
        except:
            pass
    
    def _paste_input(self, event):
        """Input'a yapıştır"""
        try:
            clipboard_text = self.clipboard_get()
            if clipboard_text:
                # Yeni satırları temizle
                clean_text = clipboard_text.replace('\n', ' ').replace('\r', '')
                self.input_entry.insert(tk.END, clean_text)
                return "break"
        except:
            pass
    
    # 🆕 Debug Modu
    def set_debug_mode(self, is_debug):
        """Debug moduna göre terminal stilini değiştir"""
        if is_debug:
            self.input_frame.configure(fg_color="#2d1b69")  # Koyu mor
            self.prompt_label.configure(text=" 🐛 DEBUG > ")
        else:
            self.input_frame.configure(fg_color="transparent")
            self.prompt_label.configure(text=" ⌨️ GİRDİ > ")
    
    # 🆕 History'ye komut ekle
    def add_to_history(self, command):
        """Komutu geçmişe ekle (tekrar edenleri engelle)"""
        command = command.strip()
        if command and (not self.history or self.history[-1] != command):
            self.history.append(command)
            # History'i 100 ile sınırla
            if len(self.history) > 100:
                self.history.pop(0)
        self.history_index = -1  # Index'i sıfırla

