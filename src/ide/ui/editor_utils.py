# -*- coding: utf-8 -*-
import tkinter as tk
import customtkinter as ctk
import re
import difflib
import threading
import os
from pathlib import Path

try:
    import winsound
except ImportError:
    winsound = None

class EditorAutocompleteMixin:
    """Editör için kod tamamlama ve snippet mantığı"""
    
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

    def show_suggestion_box(self, prefix):
        # 1. Sabit Anahtar Kelimeler
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
        
        from ..core.symbols import SymbolExtractor
        text = self.get("1.0", 'end-1c')
        extracted_symbols = SymbolExtractor.extract_from_text(text)
        
        all_candidates = {} 
        for word, meta in keywords_meta.items():
            all_candidates[word] = meta
        for sym in extracted_symbols:
            all_candidates[sym['name']] = {"type": sym['type'], "doc": f"Tanım: {sym['type'].capitalize()}\nSatır: {sym['line']}"}

        suggestions = []
        if prefix:
            starts = [w for w in all_candidates.keys() if w.startswith(prefix) and w != prefix]
            for w in sorted(starts):
                suggestions.append((w, all_candidates[w]))
            if len(suggestions) < 5:
                closes = difflib.get_close_matches(prefix, all_candidates.keys(), n=5, cutoff=0.6)
                for w in closes:
                    if w not in starts and w != prefix:
                        suggestions.append((w, all_candidates[w]))

        if not suggestions:
             self.hide_suggestion_box()
             return

        theme = self.config.THEMES[self.config.theme]
        if not hasattr(self, 'suggestion_box'):
            self.suggestion_frame = ctk.CTkFrame(self, fg_color=theme['sidebar_bg'], corner_radius=6, border_width=1, border_color=theme['border'])
            self.suggestion_box = tk.Listbox(
                self.suggestion_frame, font=('Segoe UI', 11), height=6, width=30,
                selectmode=tk.SINGLE, bg=theme['sidebar_bg'], fg=theme['fg'],
                selectbackground=theme['accent'], highlightthickness=0, borderwidth=0, relief="flat"
            )
            self.suggestion_box.pack(side="left", fill="both", expand=True, padx=2, pady=2)
            self.suggestion_box.bind("<Return>", self._apply_suggestion)
            self.suggestion_box.bind("<Tab>", self._apply_suggestion)
            self.suggestion_box.bind("<Double-Button-1>", self._apply_suggestion)
            self.suggestion_box.bind("<<ListboxSelect>>", self._on_suggestion_select)

        self.suggestion_box.delete(0, tk.END)
        self._suggestion_data = [] # Store meta
        for word, meta in suggestions:
            self.suggestion_box.insert(tk.END, word)
            self._suggestion_data.append((word, meta))
        
        self.suggestion_box.selection_set(0)
        
        bbox = self._textbox.bbox(tk.INSERT)
        if bbox:
            x, y, w, h = bbox
            self.suggestion_frame.place(x=x + 50, y=y + 30)
            self.suggestion_frame.lift()
            self._on_suggestion_select()

    def hide_suggestion_box(self):
        if hasattr(self, 'suggestion_frame'):
            self.suggestion_frame.place_forget()
        if hasattr(self, 'doc_frame'):
            self.doc_frame.place_forget()

    def _apply_suggestion(self, event=None):
        selection = self.suggestion_box.curselection()
        if selection:
            word, meta = self._suggestion_data[selection[0]]
            # Mevcut kelimeyi sil ve yenisini ekle
            current_index = self._textbox.index(tk.INSERT)
            line_start = f"{current_index.split('.')[0]}.0"
            line_text = self._textbox.get(line_start, current_index)
            wb = re.search(r'([a-zA-Z_ığüşöçİĞÜŞÖÇ]+)$', line_text)
            if wb:
                start_index = f"{current_index.split('.')[0]}.{wb.start(1)}"
                self._textbox.delete(start_index, current_index)
                self._textbox.insert(start_index, word)
            
            # Fonksiyon ise parantez ekle
            if meta['type'] == 'func':
                self._textbox.insert(tk.INSERT, "()")
                self._textbox.mark_set(tk.INSERT, f"{self._textbox.index(tk.INSERT)}-1c")
            
            self.hide_suggestion_box()
            self._trigger_highlight()
        return "break"

    def _on_suggestion_select(self, event=None):
        selection = self.suggestion_box.curselection()
        if selection:
            word, meta = self._suggestion_data[selection[0]]
            # Dokümantasyon göster
            theme = self.config.THEMES[self.config.theme]
            if not hasattr(self, 'doc_frame'):
                self.doc_frame = ctk.CTkFrame(self, fg_color=theme['sidebar_bg'], corner_radius=6, border_width=1, border_color=theme['border'])
                self.doc_label = ctk.CTkLabel(self.doc_frame, text="", font=("Segoe UI", 10), justify="left", wraplength=200)
                self.doc_label.pack(padx=10, pady=10)
            
            self.doc_label.configure(text=meta.get('doc', 'Dokümantasyon yok.'))
            fx = self.suggestion_frame.winfo_x()
            fy = self.suggestion_frame.winfo_y()
            fw = self.suggestion_frame.winfo_width()
            self.doc_frame.place(x=fx + fw + 5, y=fy)
            self.doc_frame.lift()

class EditorLinterMixin:
    """Editör için canlı hata denetimi (Linter)"""
    
    def _run_linter(self):
        text = self.get("1.0", 'end-1c')
        errors = []
        forbidden_map = {
            "var": "değişken", "let": "değişken", "degisken": "değişken",
            "if": "eğer", "eger": "eğer", "else": "değilse", "degilse": "değilse",
            "true": "doğru", "dogru": "doğru", "false": "yanlış", "yanlis": "yanlış",
            "while": "döngü", "loop": "döngü", "dongu": "döngü", "for": "her", 
            "function": "fonksiyon", "func": "fonksiyon", "def": "fonksiyon",
            "return": "dön", "don": "dön", "print": "yazdır", "yazdir": "yazdır",
            "class": "sınıf", "sinif": "sınıf", "new": "yeni", "this": "öz", "oz": "öz",
            "null": "boş", "none": "boş", "bos": "boş", "break": "kır", "kir": "kır",
            "continue": "devam", "try": "deneme", "catch": "yakala", "modul": "modül",
            "or": "veya", "and": "ve"
        }
        
        stack = []
        pairs = {')':'(', '}':'{', ']':'['}
        lines = text.split('\n')
        in_string = False 
        string_char = None
        
        for i, line in enumerate(lines):
            line_no = i + 1
            stripped = line.strip()
            if stripped.startswith("//"): continue
            
            col_idx = 0
            while col_idx < len(line):
                char = line[col_idx]
                if char in ('"', "'"):
                    if not in_string: in_string = True; string_char = char
                    elif char == string_char: in_string = False; string_char = None
                
                if not in_string:
                    if char in "({[": stack.append((char, line_no))
                    elif char in ")}]":
                        if not stack: errors.append({"line": line_no, "message": f"Beklenmeyen kapatma: '{char}'"})
                        else:
                            top, open_line = stack.pop()
                            if pairs[char] != top:
                                 errors.append({"line": line_no, "message": f"Uyuşmazlık: '{top}' (Satır {open_line}) beklenirken '{char}' geldi."})
                col_idx += 1
            
            clean_line = re.sub(r'("[^"]*"|\'[^\']*\')', '', stripped) 
            words = re.findall(r'\b\w+\b', clean_line)
            seen_errors = set()
            for w in words:
                if w in forbidden_map and w not in seen_errors:
                    errors.append({"line": line_no, "message": f"🔍 Bak hele! '{w}' yasak! '{forbidden_map[w]}' kullanmalısın."})
                    seen_errors.add(w)

        if stack:
            top, line_no = stack[-1]
            errors.append({"line": line_no, "message": f"Kapatılmamış blok: '{top}'"})

        self.set_errors(errors)

class EditorActionsMixin:
    """Editör aksiyonları (yorum satırı, taşıma, formatlama)"""

    def toggle_comment(self, event=None):
        try:
            sel_ranges = self._textbox.tag_ranges(tk.SEL)
            if sel_ranges:
                start_line = int(self._textbox.index(tk.SEL_FIRST).split('.')[0])
                end_line = int(self._textbox.index(tk.SEL_LAST).split('.')[0])
                if self._textbox.index(tk.SEL_LAST).endswith(".0"): end_line -= 1
                for line in range(start_line, end_line + 1):
                    self._toggle_comment_line(line)
            else:
                curr_line = int(self._textbox.index(tk.INSERT).split('.')[0])
                self._toggle_comment_line(curr_line)
        except: pass
        self._trigger_highlight()
        return "break"

    def _toggle_comment_line(self, line_no):
        line_start = f"{line_no}.0"
        content = self._textbox.get(line_start, f"{line_no}.end")
        if content.strip().startswith("//"):
            match = re.search(r'\/\/\s?', content)
            if match:
                self._textbox.delete(f"{line_no}.{match.start()}", f"{line_no}.{match.end()}")
        else:
            indent_match = re.search(r'^\s*', content)
            pos = indent_match.end() if indent_match else 0
            self._textbox.insert(f"{line_no}.{pos}", "// ")

    def move_line_up(self, event=None):
        line_no = int(self._textbox.index(tk.INSERT).split('.')[0])
        if line_no > 1:
            line_text = self._textbox.get(f"{line_no}.0", f"{line_no}.end+1c")
            self._textbox.delete(f"{line_no}.0", f"{line_no}.end+1c")
            self._textbox.insert(f"{line_no-1}.0", line_text)
            self._textbox.mark_set(tk.INSERT, f"{line_no-1}.0")
            self._trigger_highlight(full=True)
        return "break"

    def move_line_down(self, event=None):
        line_no = int(self._textbox.index(tk.INSERT).split('.')[0])
        last_line = int(self._textbox.index("end-1c").split('.')[0])
        if line_no < last_line:
            line_text = self._textbox.get(f"{line_no}.0", f"{line_no}.end+1c")
            self._textbox.delete(f"{line_no}.0", f"{line_no}.end+1c")
            self._textbox.insert(f"{line_no+1}.0", line_text)
            self._textbox.mark_set(tk.INSERT, f"{line_no+1}.0")
            self._trigger_highlight(full=True)
        return "break"

    def delete_current_line(self, event=None):
        line_no = self._textbox.index(tk.INSERT).split('.')[0]
        self._textbox.delete(f"{line_no}.0", f"{line_no}.end+1c")
        self._on_change()
        return "break"

    def rename_symbol(self, event=None):
        # Basitçe dosya genelinde replace
        current_word = self._textbox.get("insert wordstart", "insert wordend")
        if not current_word: return
        from tkinter import simpledialog
        new_word = simpledialog.askstring("Yeniden Adlandır", f"'{current_word}' için yeni ad:", initialvalue=current_word)
        if new_word and new_word != current_word:
            content = self._textbox.get("1.0", tk.END)
            new_content = re.sub(rf'\b{current_word}\b', new_word, content)
            self._textbox.delete("1.0", tk.END)
            self._textbox.insert("1.0", new_content)
            self._trigger_highlight(full=True)

    def format_code(self):
        from ..core.formatter import GumusFormatter
        def play_mechanical_sound():
            try:
                if not winsound: return
                import random, time
                for _ in range(random.randint(4, 7)):
                    winsound.Beep(random.randint(800, 1500), random.randint(20, 50))
                    time.sleep(random.uniform(0.02, 0.08))
            except: pass
        threading.Thread(target=play_mechanical_sound, daemon=True).start()
        content = self.get("1.0", 'end-1c')
        self._textbox.delete("1.0", tk.END)
        self._textbox.insert("1.0", GumusFormatter.format(content))
        self.show_toast("Kod formatlandı! ✨", "success")
