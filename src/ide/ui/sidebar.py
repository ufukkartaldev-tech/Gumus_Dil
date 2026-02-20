# -*- coding: utf-8 -*-
import customtkinter as ctk
import os
from pathlib import Path
from ..config import EXAMPLES_DIR
from .memory_view_v2 import MemoryViewV2 as MemoryView
from .ai_panel import AIPanel
from .notes_panel import NotesPanel
from ..core.debugger import DebuggerManager
from .debug_panels import VariableWatchPanel, CallStackPanel, DebugControlBar
from .pardus_panel import PardusPanel
from .market_panel import MarketPanel
from .profiler_panel import ProfilerPanel
from .docs_panel import DocsPanel
from .flowchart_panel import FlowchartPanel

class TreeNode(ctk.CTkFrame):
    def __init__(self, parent, path, is_file, level, on_file_click, config):
        super().__init__(parent, fg_color="transparent")
        self.path = path
        self.is_file = is_file
        self.level = level
        self.on_file_click = on_file_click
        self.config = config
        self.is_expanded = False
        self.loaded = False
        
        theme = self.config.THEMES[self.config.theme] if self.config else {}

        # Header (Satır)
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x")
        
        # İçerik Girintisi (Padding)
        indent = level * 20
        
        # İkon ve Metin
        text = path.name
        
        # Colors
        text_color = theme.get('fg', "gray90")
        hover_color = theme.get('hover', "gray25")
        
        if self.is_file:
            # Gelişmiş Dosya İkonları
            ext = path.suffix.lower()
            icons = {
                '.tr': '💎', '.py': '🐍', '.js': '📜', '.html': '🌐', 
                '.css': '🎨', '.json': '📋', '.md': '📝', '.txt': '📄',
                '.png': '🖼️', '.jpg': '🖼️', '.svg': '🖼️'
            }
            icon = icons.get(ext, '📄')
            
            cmd = self._on_click_file
            self.btn = ctk.CTkButton(self.header, text=f"{icon} {text}", 
                                   anchor="w", fg_color="transparent", 
                                   text_color=text_color,
                                   hover_color=hover_color, height=28,
                                   font=("Segoe UI", 12),
                                   command=cmd)
            # Sağ Tık Menüsü
            self.btn.bind("<Button-3>", self._show_context_menu)
            
        else:
            icon = "▶" if not self.is_expanded else "▼" 
            folder_icon = "📁"
            cmd = self._on_toggle_folder
            
            self.btn = ctk.CTkButton(self.header, text=f"{icon} {folder_icon} {text}", 
                                   anchor="w", fg_color="transparent",
                                   text_color=text_color, 
                                   hover_color=hover_color, height=28,
                                   font=("Segoe UI", 12, "bold"),
                                   command=cmd)
            # Klasör Sağ Tık (İleride eklenebilir)
            
        self.btn.pack(fill="x", padx=(indent, 0), side="left", expand=True)

        if not self.is_file:
            self.children_container = ctk.CTkFrame(self, fg_color="transparent")
            
    def _show_context_menu(self, event):
        """Sağ tık menüsü"""
        import tkinter as tk
        from tkinter import simpledialog, messagebox
        import shutil
        
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Yeniden Adlandır", command=self._rename_item)
        menu.add_command(label="Sil", command=self._delete_item)
        menu.add_separator()
        menu.add_command(label="Yolu Kopyala", command=lambda: self.master.clipboard_clear() or self.master.clipboard_append(str(self.path)))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _rename_item(self):
        from tkinter import simpledialog, messagebox
        new_name = simpledialog.askstring("Yeniden Adlandır", f"Yeni ismi giriniz ({self.path.name}):", initialvalue=self.path.name)
        if new_name and new_name != self.path.name:
            try:
                new_path = self.path.parent / new_name
                self.path.rename(new_path)
                # Basit yenileme: Parent'ı reload et
                # Sidebar üzerinden reload trigger edilebilir ama şimdilik path'i güncelle
                self.path = new_path
                self.btn.configure(text=f"{'💎' if self.is_file else '📁'} {new_name}")
            except Exception as e:
                messagebox.showerror("Hata", f"Yeniden adlandırılamadı: {e}")

    def _delete_item(self):
        from tkinter import messagebox
        import shutil
        confirm = messagebox.askyesno("Silme Onayı", f"'{self.path.name}' öğesini silmek istediğinizden emin misiniz?")
        if confirm:
            try:
                if self.path.is_dir():
                    shutil.rmtree(self.path)
                else:
                    self.path.unlink()
                self.destroy() # UI'dan kaldır
            except Exception as e:
                messagebox.showerror("Hata", f"Silinemedi: {e}")

    def _on_click_file(self):
        if self.on_file_click:
            self.on_file_click(str(self.path))

    def _on_toggle_folder(self):
        if self.is_expanded:
            self._collapse()
        else:
            self._expand()

    def _expand(self):
        self.is_expanded = True
        self.btn.configure(text=f"▼ 📂 {self.path.name}")
        self.children_container.pack(fill="x", expand=True)
        if not self.loaded:
            self._load_children()
            self.loaded = True

    def _collapse(self):
        self.is_expanded = False
        self.btn.configure(text=f"▶ 📁 {self.path.name}")
        self.children_container.pack_forget()

    def _load_children(self):
        try:
            items = list(self.path.iterdir())
            items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for item in items:
                if item.name.startswith('.') or item.name == '__pycache__': continue
                if item.is_file() and item.suffix not in ['.tr', '.py']: continue
                    
                node = TreeNode(self.children_container, item, item.is_file(), self.level + 1, self.on_file_click, self.config)
                node.pack(fill="x")
                
        except Exception as e:
            print(f"Klasör yükleme hatası: {e}")
            err = ctk.CTkLabel(self.children_container, text=f"Hata: {e}", text_color="red")
            err.pack(padx=20)


class SearchPanel(ctk.CTkFrame):
    def __init__(self, parent, config, on_file_click):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_file_click = on_file_click
        
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Tüm dosyalarda ara...", height=35)
        self.search_entry.pack(fill="x", padx=10, pady=10)
        self.search_entry.bind("<Return>", lambda e: self.perform_search())
        
        self.results_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True)

    def perform_search(self):
        query = self.search_entry.get().lower()
        if not query: return
        for widget in self.results_frame.winfo_children(): widget.destroy()
        root = Path(os.getcwd())
        for file_path in root.rglob("*.tr"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if query in line.lower():
                            self._add_result(file_path, i+1, line.strip())
            except: continue

    def _add_result(self, path, line_no, content):
        theme = self.config.THEMES[self.config.theme]
        btn = ctk.CTkButton(self.results_frame, text=f"{path.name}:{line_no}\n{content[:40]}...",
                           anchor="w", fg_color="transparent", hover_color=theme['hover'],
                           text_color=theme['fg'], height=45, font=("Segoe UI", 10),
                           command=lambda: self.on_file_click(str(path)))
        btn.pack(fill="x", padx=5, pady=2)

class TrainingPanel(ctk.CTkFrame):
    def __init__(self, parent, config, on_load_task):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_load_task = on_load_task # callback(task_code, instructions)
        
        # Görev Veritabanı
        self.tasks = [
            {
                "id": 1, 
                "title": "Görev 1: Merhaba Dünya", 
                "desc": "Yazılım dünyasının kapısını arala! Ekrana 'Merhaba Dünya' yazdıran kodu yaz.",
                "code": '// Ekrana "Merhaba Dünya" yazdır\n\n',
                "check": "Merhaba Dünya"
            },
            {
                "id": 2, 
                "title": "Görev 2: Değişkenler", 
                "desc": "Bir değişken tanımla ve onu yazdır. Mesela 'isim' değişkenine adını yaz.",
                "code": '// Değişken tanımla ve yazdır\ndeğişken isim = "..."\n\n',
                "check": ""
            },
            {
                "id": 3, 
                "title": "Görev 3: Basit Matematik", 
                "desc": "İki sayıyı toplayıp ekrana yazdıran bir kod yaz.",
                "code": 'değişken a = 5\ndeğişken b = 10\n// Toplamı yazdır\n',
                "check": "15"
            }
        ]
        
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self._load_tasks_ui()
        
    def _load_tasks_ui(self):
        theme = self.config.THEMES[self.config.theme]
        
        title = ctk.CTkLabel(self.scroll, text="🏋️ GÜMÜŞ GYM", font=("Segoe UI", 14, "bold"), text_color=theme['accent'])
        title.pack(pady=(10, 20))
        
        for task in self.tasks:
            card = ctk.CTkFrame(self.scroll, fg_color=theme['sidebar_bg'], corner_radius=10, border_width=1, border_color=theme['border'])
            card.pack(fill="x", pady=5, padx=5)
            
            # Başlık
            ctk.CTkLabel(card, text=task['title'], font=("Segoe UI", 12, "bold"), text_color=theme['fg']).pack(anchor="w", padx=10, pady=(10, 0))
            
            # Açıklama
            desc = ctk.CTkLabel(card, text=task['desc'], font=("Segoe UI", 10), text_color=theme['comment'], wraplength=200, justify="left")
            desc.pack(anchor="w", padx=10, pady=(2, 10))
            
            # Başla Butonu
            btn = ctk.CTkButton(card, text="Başla", height=24, width=60, fg_color=theme['accent'], hover_color=theme['select_bg'],
                              command=lambda t=task: self.start_task(t))
            btn.pack(anchor="e", padx=10, pady=(0, 10))
            
    def start_task(self, task):
        # Kullanıcının editörüne kodu yükle
        self.on_load_task(task['code'])
        # Yönlendirme mesajı (Opsiyonel)
        print(f"Görev Başladı: {task['title']}")

class OutlinePanel(ctk.CTkFrame):
    def __init__(self, parent, config, on_jump):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_jump = on_jump
        self.tree_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.tree_frame.pack(fill="both", expand=True)

    def update_outline(self, symbols):
        for widget in self.tree_frame.winfo_children(): widget.destroy()
        theme = self.config.THEMES[self.config.theme]
        for s in symbols:
            color = theme['function'] if s['type'] == 'function' else theme['class'] if s['type'] == 'class' else theme['variable']
            btn = ctk.CTkButton(self.tree_frame, text=f"{s['icon']} {s['name']}", anchor="w",
                               fg_color="transparent", hover_color=theme['hover'], text_color=color,
                               height=28, font=("Segoe UI", 11), command=lambda line=s['line']: self.on_jump(line))
            btn.pack(fill="x", padx=5, pady=1)

class TranspilerPanel(ctk.CTkFrame):
    def __init__(self, parent, config, on_language_change=None):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_language_change = on_language_change
        
        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", pady=5, padx=5)
        
        # Hedef Dil Seçici
        self.lang_var = ctk.StringVar(value="Python")
        self.lang_menu = ctk.CTkOptionMenu(
            self.header, 
            values=["Python", "C++"], 
            variable=self.lang_var,
            width=80,
            height=24,
            command=self._on_lang_change
        )
        self.lang_menu.pack(side="left", padx=(0, 10))
        
        self.info_lbl = ctk.CTkLabel(self.header, text="Çıktısı", font=("Segoe UI", 12, "bold"))
        self.info_lbl.pack(side="left")
        
        self.copy_btn = ctk.CTkButton(self.header, text="Kopyala", width=60, height=24, command=self.copy_code)
        self.copy_btn.pack(side="right")
        
        # Code Area
        self.code_view = ctk.CTkTextbox(self, font=("Consolas", 12), wrap="none")
        self.code_view.pack(fill="both", expand=True, padx=5, pady=5)
        
    def _on_lang_change(self, choice):
        if self.on_language_change:
            self.on_language_change(choice)

    def set_code(self, code):
        self.code_view.configure(state="normal")
        self.code_view.delete("1.0", "end")
        self.code_view.insert("1.0", code)
        self.code_view.configure(state="disabled")
        
    def copy_code(self):
        code = self.code_view.get("1.0", "end-1c")
        self.master.clipboard_clear()
        self.master.clipboard_append(code)
        # Toast?
        print(f"{self.lang_var.get()} kodu kopyalandı.")

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, config, callbacks):
        super().__init__(parent, corner_radius=0)
        self.config = config
        self.callbacks = callbacks # {'on_file_select', 'on_jump'}
        self.current_root = EXAMPLES_DIR
        self.mode = "explorer"
        
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", pady=(10, 5), padx=10)
        
        self.label = ctk.CTkLabel(self.top_frame, text="GEZGİN", font=('Segoe UI', 11, 'bold'), text_color=self.config.THEMES[self.config.theme]['comment'])
        self.label.pack(side="left")

        self.btn_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.btn_frame.pack(side="right")
        self._setup_explorer_buttons()

        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True)
        
        self.explorer_panel = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        self.search_panel = SearchPanel(self.content_container, config, callbacks['on_file_select'])
        self.outline_panel = OutlinePanel(self.content_container, config, callbacks['on_jump'])
        self.training_panel = TrainingPanel(self.content_container, config, callbacks.get('load_code', lambda c: print(c)))
        
        # Transpiler Panel
        self.transpiler_panel = TranspilerPanel(
            self.content_container, 
            config,
            on_language_change=lambda _: self.switch_mode("transpiler")
        )
        
        # AI Paneli önce başlat (MemoryView buna erişebilecek)
        self.ai_panel = AIPanel(
            self.content_container, 
            config, 
            on_apply_code=callbacks.get('on_apply_code'),
            on_get_code=callbacks.get('get_code')
        )
        
        self.notes_panel = NotesPanel(self.content_container, config)
        
        # Debugger Manager
        self.debugger = DebuggerManager(compiler_path="bin/gumus.exe")
        
        # Pardus Paneli
        self.pardus_panel = PardusPanel(self.content_container, config)
        
        # Market ve Profiler Panelleri
        self.market_panel = MarketPanel(self.content_container, config)
        self.profiler_panel = ProfilerPanel(self.content_container, config)
        self.docs_panel = DocsPanel(self.content_container, config)
        self.flowchart_panel = FlowchartPanel(self.content_container, config)
        
        # MemoryView'e AI Köprüsü
        def bridge_to_ai(context_text):
            self.switch_mode("ai")
            if hasattr(self.ai_panel, 'receive_external_query'):
                self.ai_panel.receive_external_query(context_text)
                
        self.memory_panel = MemoryView(self.content_container, config, 
                                     on_jump=callbacks['on_jump'], 
                                     on_ask_ai=bridge_to_ai)
        
        # Debug Panels
        self.var_watch_panel = VariableWatchPanel(self.content_container, self.debugger, config)
        self.call_stack_panel = CallStackPanel(
            self.content_container, 
            self.debugger, 
            config,
            on_frame_click=lambda frame: callbacks.get('on_jump', lambda x: None)(frame.line_number)
        )
        
        self.switch_mode("explorer")


    def _setup_explorer_buttons(self):
        for widget in self.btn_frame.winfo_children(): widget.destroy()
        actions = [("📄+", self._on_new_file), ("📁+", self._on_new_folder), ("🔄", lambda: self.set_root(self.current_root))]
        for icon, cmd in actions:
            btn = ctk.CTkButton(self.btn_frame, text=icon, width=24, height=24, fg_color="transparent", 
                               hover_color=self.config.THEMES[self.config.theme]['hover'], font=("Segoe UI", 12), command=cmd)
            btn.pack(side="left", padx=1)

    def switch_mode(self, mode):
        self.mode = mode
        
        # Panelleri Gizle
        self.explorer_panel.pack_forget()
        self.search_panel.pack_forget()
        self.outline_panel.pack_forget()
        self.memory_panel.pack_forget()
        self.training_panel.pack_forget()
        self.ai_panel.pack_forget()
        self.pardus_panel.pack_forget()
        self.notes_panel.pack_forget()
        self.var_watch_panel.pack_forget()
        self.call_stack_panel.pack_forget()
        self.transpiler_panel.pack_forget()
        self.market_panel.pack_forget()
        self.profiler_panel.pack_forget()
        self.docs_panel.pack_forget()
        self.flowchart_panel.pack_forget()
        
        # İlgili Paneli Göster
        label_map = {
            "explorer": "GEZGİN",
            "search": "ARA", 
            "outline": "ANAHAT",
            "memory": "HAFIZA",
            "training": "GÜMÜŞ GYM",
            "ai": "GÜMÜŞ ZEKA",
            "pardus": "🐆 PARDUS",
            "notes": "NOT DEFTERİ",
            "variables": "🔍 VARIABLES",
            "callstack": "📚 CALL STACK",
            "transpiler": "🐍 PYTHON ÇEVİRİ",
            "market": "🛒 GÜMÜŞ PAZAR",
            "profiler": "📊 GÜMÜŞ ANALİZ",
            "docs": "📚 GÜMÜŞ SÖZLÜK",
            "flowchart": "🌿 GÜMÜŞ AKIŞ"
        }
        self.label.configure(text=label_map.get(mode, "GEZGİN"))
        
        # Butonlar sadece explorer'da görünür
        if mode == "explorer":
            self.btn_frame.pack(side="right")
        else:
            self.btn_frame.pack_forget()
            
        if mode == "explorer":
            self.explorer_panel.pack(fill="both", expand=True)
            self._refresh_explorer()
        elif mode == "search":
            self.search_panel.pack(fill="both", expand=True)
        elif mode == "outline":
            self.outline_panel.pack(fill="both", expand=True)
        elif mode == "training":
            self.training_panel.pack(fill="both", expand=True)
            for widget in self.btn_frame.winfo_children(): widget.destroy()
        elif mode == "memory":
            self.label.configure(text="GÜMÜŞHAFIZA")
            self.memory_panel.pack(fill="both", expand=True)
            for widget in self.btn_frame.winfo_children(): widget.destroy()
        elif mode == "ai":
            self.ai_panel.pack(fill="both", expand=True)
            for widget in self.btn_frame.winfo_children(): widget.destroy()
        elif mode == "pardus":
            self.pardus_panel.pack(fill="both", expand=True)
            for widget in self.btn_frame.winfo_children(): widget.destroy()
        elif mode == "notes":
            self.notes_panel.pack(fill="both", expand=True)
            self.notes_panel.load_notes() # Her açıldığında yükle
            for widget in self.btn_frame.winfo_children(): widget.destroy()
        elif mode == "market":
            self.market_panel.pack(fill="both", expand=True)
            for widget in self.btn_frame.winfo_children(): widget.destroy()
        elif mode == "profiler":
            self.profiler_panel.pack(fill="both", expand=True)
            self.profiler_panel.start_profiling()
            for widget in self.btn_frame.winfo_children(): widget.destroy()
        elif mode == "docs":
            self.docs_panel.pack(fill="both", expand=True)
            for widget in self.btn_frame.winfo_children(): widget.destroy()
        elif mode == "flowchart":
            self.flowchart_panel.pack(fill="both", expand=True)
            # Eğer kod varsa, akış şemasını güncelle
            if self.callbacks.get('get_code'):
                code = self.callbacks['get_code']()
                self.flowchart_panel.update_flowchart(code)
            for widget in self.btn_frame.winfo_children(): widget.destroy()
        elif mode == "variables":
            self.var_watch_panel.pack(fill="both", expand=True)
            self.var_watch_panel.refresh()
            for widget in self.btn_frame.winfo_children(): widget.destroy()
        elif mode == "callstack":
            self.call_stack_panel.pack(fill="both", expand=True)
            self.call_stack_panel.refresh()
            for widget in self.btn_frame.winfo_children(): widget.destroy()
        elif mode == "transpiler":
            self.transpiler_panel.pack(fill="both", expand=True)
            # Eğer kod varsa, çeviriyi tetikle
            if self.callbacks.get('get_code'):
                code = self.callbacks['get_code']()
                if code:
                    target_lang = self.transpiler_panel.lang_var.get()
                    try:
                        if target_lang == "Python":
                            from ..core.transpiler import GumusToPythonTranspiler
                            t = GumusToPythonTranspiler()
                        else:
                            from ..core.gumus_to_cpp import GumusToCppTranspiler
                            t = GumusToCppTranspiler()
                            
                        translated_code = t.transpile(code)
                        self.transpiler_panel.set_code(translated_code)
                    except Exception as e:
                        self.transpiler_panel.set_code(f"# Error: {e}")
            for widget in self.btn_frame.winfo_children(): widget.destroy()

    def set_root(self, path):
        self.current_root = Path(path)
        self.label.configure(text=self.current_root.name[:15].upper())
        
        for widget in self.explorer_panel.winfo_children():
            widget.destroy()
            
        self._load_root_contents()


    def _load_root_contents(self):
        try:
            items = list(self.current_root.iterdir())
            items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for item in items:
                if item.name.startswith('.') or item.name == '__pycache__': continue
                if item.is_file() and item.suffix not in ['.tr', '.py']: continue
                
                # Level 0 nodes
                node = TreeNode(self.explorer_panel, item, item.is_file(), 0, self.callbacks['on_file_select'], self.config)
                node.pack(fill="x")

        except Exception as e:
            print(f"Root yükleme hatası: {e}")
    def _on_new_file(self):
        """Yeni bir .tr dosyası oluştur"""
        dialog = ctk.CTkInputDialog(text="Dosya Adı (.tr):", title="Yeni Dosya")
        filename = dialog.get_input()
        
        if filename:
            if not filename.endswith(".tr"):
                filename += ".tr"
            
            new_path = self.current_root / filename
            try:
                if new_path.exists():
                    from tkinter import messagebox
                    messagebox.showwarning("Uyarı", "Bu isimde bir dosya zaten var!")
                    return
                
                # Dosyayı oluştur
                new_path.touch()
                self.set_root(self.current_root) # Listeyi yenile
                
                # Yeni dosyayı aç
                if self.callbacks['on_file_select']:
                    self.callbacks['on_file_select'](str(new_path))

                    
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Hata", f"Dosya oluşturulamadı: {e}")

    def _on_new_folder(self):
        """Yeni bir klasör oluştur"""
        dialog = ctk.CTkInputDialog(text="Klasör Adı:", title="Yeni Klasör")
        folder_name = dialog.get_input()
        
        if folder_name:
            new_path = self.current_root / folder_name
            try:
                new_path.mkdir(exist_ok=True)
                self.set_root(self.current_root) # Listeyi yenile
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Hata", f"Klasör oluşturulamadı: {e}")

    def _refresh_explorer(self):
        """Gezgini yenile"""
        self.set_root(self.current_root)

    def update_variables(self, vars_json):
        """Gelen canlı değişken verilerini panelde güncelle"""
        if hasattr(self, 'var_watch_panel'):
            # Eğer panel şu an görünür değilse bile veriyi saklayabilir veya güncelleyebilir
            self.var_watch_panel.update_from_json(vars_json)




