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
from .voxel_editor import VoxelEditor
from .vizyon_panel import VizyonPanel

from tkinter import ttk, Menu, simpledialog, messagebox
import shutil

class ExplorerTree(ctk.CTkFrame):
    def __init__(self, parent, config, on_file_select):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_file_select = on_file_select
        self.current_root = None
        self.nodes = {} # id -> path
        
        theme = self.config.THEMES[self.config.theme]
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("Sidebar.Treeview",
                        background=theme['sidebar_bg'],
                        foreground=theme['fg'],
                        fieldbackground=theme['sidebar_bg'],
                        borderwidth=0,
                        rowheight=26,
                        font=("Segoe UI", 11))
        style.map("Sidebar.Treeview", 
                  background=[('selected', theme['hover'])],
                  foreground=[('selected', theme['accent'])])
                  
        self.tree = ttk.Treeview(self, style="Sidebar.Treeview", show="tree", selectmode="browse")
        self.scrollbar = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)
        self.tree.bind("<<TreeviewOpen>>", self._on_tree_open)
        
    def load_root(self, path):
        self.current_root = Path(path)
        self.tree.delete(*self.tree.get_children())
        self.nodes.clear()
        self._insert_node("", self.current_root, is_root=True)

    def refresh(self):
        if self.current_root: self.load_root(self.current_root)

    def _insert_node(self, parent_id, path, is_root=False):
        text = path.name if not is_root else path.name.upper()
        if path.is_dir():
            icon = "📂" 
            display_text = f"{icon} {text}"
        else:
            ext = path.suffix.lower()
            icons = {'.tr': '💎', '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨', '.json': '📋', '.md': '📝', '.txt': '📄'}
            icon = icons.get(ext, '📄')
            try:
                size = path.stat().st_size
                size_kb = f"{size/1024:.1f} KB"
            except:
                size_kb = ""
            display_text = f"{icon} {text}   [{size_kb}]"
        node_id = self.tree.insert(parent_id, "end", text=display_text, open=is_root)
        self.nodes[node_id] = path
        
        if path.is_dir():
            self.tree.insert(node_id, "end", text="yükleniyor...")
            if is_root: self._load_children(node_id)
                
    def _on_tree_open(self, event):
        node_id = self.tree.focus()
        if node_id: self._load_children(node_id)
        
    def _load_children(self, node_id):
        path = self.nodes.get(node_id)
        if not path or not path.is_dir(): return
        
        children = self.tree.get_children(node_id)
        if len(children) == 1 and self.tree.item(children[0], "text") == "yükleniyor...":
            self.tree.delete(children[0])
            try:
                items = list(path.iterdir())
                items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
                for item in items:
                    if item.name.startswith('.') or item.name == '__pycache__': continue
                    self._insert_node(node_id, item)
            except: pass

    def _on_double_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if item:
            path = self.nodes.get(item)
            if path and path.is_file() and self.on_file_select:
                self.on_file_select(str(path))

    def _on_right_click(self, event):
        item = self.tree.identify('item', event.x, event.y)
        if item:
            self.tree.selection_set(item)
            self.tree.focus(item)
        target_path = self.nodes.get(item) if item else self.current_root
        if not target_path: return
        
        menu = Menu(self, tearoff=0)
        menu.add_command(label="📄 Yeni Dosya", command=lambda: self._new_file(target_path))
        menu.add_command(label="📁 Yeni Klasör", command=lambda: self._new_folder(target_path))
        menu.add_separator()
        if target_path != self.current_root:
            menu.add_command(label="🖋️ Yeniden Adlandır", command=lambda: self._rename(target_path))
            menu.add_command(label="🗑️ Sil", command=lambda: self._delete(target_path))
            menu.add_separator()
            
        menu.add_command(label="� Burada Terminal Aç", command=lambda: self._open_in_terminal(target_path))
        menu.add_separator()
        menu.add_command(label="�🔄 Yenile", command=self.refresh)
        
        menu.tk_popup(event.x_root, event.y_root)
        
    def _new_file(self, target_path):
        parent_dir = target_path if target_path.is_dir() else target_path.parent
        res = simpledialog.askstring("Yeni Dosya", "Dosya adı (.tr vs.):")
        if res:
            try:
                if not res.endswith('.tr') and '.' not in res: res += '.tr'
                (parent_dir / res).touch()
                self.refresh()
                if self.on_file_select: self.on_file_select(str(parent_dir / res))
            except Exception as e: messagebox.showerror("Hata", str(e))
                
    def _new_folder(self, target_path):
        parent_dir = target_path if target_path.is_dir() else target_path.parent
        res = simpledialog.askstring("Yeni Klasör", "Klasör adı:")
        if res:
            try:
                (parent_dir / res).mkdir()
                self.refresh()
            except Exception as e: messagebox.showerror("Hata", str(e))
                
    def _rename(self, target_path):
        res = simpledialog.askstring("Yeniden Adlandır", "Yeni ad:", initialvalue=target_path.name)
        if res and res != target_path.name:
            try:
                target_path.rename(target_path.parent / res)
                self.refresh()
            except Exception as e: messagebox.showerror("Hata", str(e))
                
    def _delete(self, target_path):
        if messagebox.askyesno("Silme Onayı", f"'{target_path.name}' silinecek. Emin misin?"):
            try:
                if target_path.is_dir(): shutil.rmtree(target_path)
                else: target_path.unlink()
                self.refresh()
            except Exception as e: messagebox.showerror("Hata", str(e))

    def _open_in_terminal(self, target_path):
        import subprocess
        parent_dir = target_path if target_path.is_dir() else target_path.parent
        try:
            if os.name == 'nt':
                subprocess.Popen(['cmd.exe', '/c', 'start', 'cmd.exe', '/K', f'cd /d {parent_dir}'])
            else:
                subprocess.Popen(['x-terminal-emulator', '--working-directory', str(parent_dir)])
        except Exception as e:
            messagebox.showerror("Hata", f"Terminal açılamadı:\n{e}")


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
        
        # Arama sırasında UI donmasını engellemek için Thread kullan
        import threading
        
        def _search_thread():
            root = Path(os.getcwd())
            results = []
            for file_path in root.rglob("*.tr"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if query in line.lower():
                                results.append((file_path, i+1, line.strip()))
                except: continue
            
            # Sonuçları UI thread'inde göster
            self.after(0, lambda: self._show_results(results))
            
        threading.Thread(target=_search_thread, daemon=True).start()

    def _show_results(self, results):
        if not results:
            self._add_result(Path("Bulunamadı"), 0, "Arama kriterine uygun sonuç yok.")
            return
            
        for res in results:
            self._add_result(res[0], res[1], res[2])

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
        self.tasks = []
        self._load_tasks_from_json()
        
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self._load_tasks_ui()
        
    def _load_tasks_from_json(self):
        import json
        tasks_file = Path(os.path.dirname(__file__)).parent / "data" / "tasks.json"
        try:
            if tasks_file.exists():
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            else:
                print("GYM Görevleri bulunamadı:", tasks_file)
        except Exception as e:
            print("GYM Yükleme hatası:", e)
            self.tasks = []
        
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
        
        self.explorer_tree = ExplorerTree(self.content_container, config, callbacks['on_file_select'])
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
        self.voxel_editor = VoxelEditor(
            self.content_container, 
            config,
            on_apply_code=callbacks.get('on_apply_code'),
            get_code=callbacks.get('get_code')
        )
        self.vizyon_panel = VizyonPanel(
            self.content_container, 
            config,
            on_apply_code=callbacks.get('on_apply_code')
        )
        
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
        actions = [("📄+", lambda: self.explorer_tree._new_file(self.current_root)), 
                   ("📁+", lambda: self.explorer_tree._new_folder(self.current_root)), 
                   ("🔄", lambda: self.explorer_tree.refresh())]
        for icon, cmd in actions:
            btn = ctk.CTkButton(self.btn_frame, text=icon, width=24, height=24, fg_color="transparent", 
                               hover_color=self.config.THEMES[self.config.theme]['hover'], font=("Segoe UI", 12), command=cmd)
            btn.pack(side="left", padx=1)

    def switch_mode(self, mode):
        self.mode = mode
        
        # Panelleri Gizle
        self.explorer_tree.pack_forget()
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
        self.voxel_editor.pack_forget()
        self.vizyon_panel.pack_forget()
        
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
            "flowchart": "🌿 GÜMÜŞ AKIŞ",
            "voxel_editor": "🎮 SAHNE EDİTÖRÜ",
            "vizyon": "📡 GÜMÜŞ VİZYON"
        }
        self.label.configure(text=label_map.get(mode, "GEZGİN"))
        
        # Butonlar sadece explorer'da görünür
        if mode == "explorer":
            self.btn_frame.pack(side="right")
        else:
            self.btn_frame.pack_forget()
            
        if mode == "explorer":
            self.explorer_tree.pack(fill="both", expand=True)
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
        elif mode == "voxel_editor":
            self.voxel_editor.pack(fill="both", expand=True)
            for widget in self.btn_frame.winfo_children(): widget.destroy()
        elif mode == "vizyon":
            self.vizyon_panel.pack(fill="both", expand=True)
            # Simüle telemetri
            self.after(500, lambda: self.vizyon_panel.update_metrics(240, 85, 92, -65))
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
        self.explorer_tree.load_root(self.current_root)

    def _refresh_explorer(self):
        """Gezgini yenile"""
        self.explorer_tree.refresh()

    def update_variables(self, vars_json):
        """Gelen canlı değişken verilerini panelde güncelle"""
        if hasattr(self, 'var_watch_panel'):
            # Eğer panel şu an görünür değilse bile veriyi saklayabilir veya güncelleyebilir
            self.var_watch_panel.update_from_json(vars_json)




