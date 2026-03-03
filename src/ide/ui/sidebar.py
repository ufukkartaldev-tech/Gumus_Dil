# -*- coding: utf-8 -*-
import customtkinter as ctk
import os
from pathlib import Path
from ..config import EXAMPLES_DIR
from .memory_view_v2 import MemoryViewV2 as MemoryView
from .ai_panel import AIPanel
from .notes_panel import NotesPanel
from ..core.debugger import DebuggerManager
from .debug_panels import VariableWatchPanel, CallStackPanel
from .pardus_panel import PardusPanel
from .market_panel import MarketPanel
from .profiler_panel import ProfilerPanel
from .docs_panel import DocsPanel
from .flowchart_panel import FlowchartPanel
from .voxel_editor import VoxelEditor
from .vizyon_panel import VizyonPanel

# Yeni modüler paneller
from .explorer import ExplorerTree
from .search_panel import SearchPanel
from .training_panel import TrainingPanel
from .outline_panel import OutlinePanel
from .transpiler_panel import TranspilerPanel

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
        self.training_panel = TrainingPanel(self.content_container, config, callbacks.get('load_code', lambda c: print(f"GYM: {c}")))
        
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
        try:
            from ..config import COMPILER_PATH
            comp_path = str(COMPILER_PATH)
        except:
            comp_path = str(Path(__file__).resolve().parent.parent.parent.parent / "bin" / "gumus.exe")
        self.debugger = DebuggerManager(compiler_path=comp_path)
        
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
        
        # Tüm panelleri performansı korumak için bir kere tanımlıyoruz (Oluşum Mimarisi)
        self.panels = {
            "explorer": self.explorer_tree,
            "search": self.search_panel,
            "outline": self.outline_panel,
            "training": self.training_panel,
            "memory": self.memory_panel,
            "ai": self.ai_panel,
            "pardus": self.pardus_panel,
            "notes": self.notes_panel,
            "variables": self.var_watch_panel,
            "callstack": self.call_stack_panel,
            "transpiler": self.transpiler_panel,
            "market": self.market_panel,
            "profiler": self.profiler_panel,
            "docs": self.docs_panel,
            "flowchart": self.flowchart_panel,
            "voxel_editor": self.voxel_editor,
            "vizyon": self.vizyon_panel
        }
        
        self.switch_mode("explorer")
        self.set_root(self.current_root)

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
        
        # Önceden yüklenmiş panelleri tek kalemde gizle
        for p in self.panels.values():
            p.pack_forget()

        # İstek yapılan paneli göster
        if mode in self.panels:
            self.panels[mode].pack(fill="both", expand=True)
            
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
            self._refresh_explorer()
        else:
            self.btn_frame.pack_forget()
            
        # Özel Aksiyonlar
        if mode == "memory":
            self.label.configure(text="GÜMÜŞHAFIZA")
        elif mode == "outline":
            if self.callbacks.get('on_refresh_outline'):
                self.callbacks['on_refresh_outline']()
        elif mode == "notes":
            self.notes_panel.load_notes() # Her açıldığında yükle
        elif mode == "profiler":
            self.profiler_panel.start_profiling()
        elif mode == "flowchart":
            # Eğer kod varsa, akış şemasını güncelle
            if self.callbacks.get('get_code'):
                code = self.callbacks['get_code']()
                self.flowchart_panel.update_flowchart(code)
        elif mode == "vizyon":
            # Simüle telemetri
            self.after(500, lambda: self.vizyon_panel.update_metrics(240, 85, 92, -65))
        elif mode == "variables":
            self.var_watch_panel.refresh()
        elif mode == "callstack":
            self.call_stack_panel.refresh()
        elif mode == "transpiler":
            # Eğer kod varsa, çeviriyi tetikle
            if self.callbacks.get('get_code'):
                code = self.callbacks['get_code']()
                if code and code.strip():
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

    def set_root(self, path):
        self.current_root = Path(path)
        self.label.configure(text=self.current_root.name[:15].upper() if self.current_root.name else str(self.current_root))
        self.switch_mode("explorer")
        self.explorer_tree.load_root(self.current_root)

    def reveal_file(self, path):
        if hasattr(self, 'explorer_tree'):
            self.switch_mode("explorer")
            # Sidebari görünür yap (Eğer gizliyse)
            if hasattr(self.master, 'master') and hasattr(self.master.master, 'toggle_sidebar'):
                # Bu kontrol biraz dolaylı
                pass
            
            # MainWindow üzerinden görünürlüğü sağla
            root = self.winfo_toplevel()
            if hasattr(root, 'toggle_sidebar') and not self.winfo_ismapped():
                root.toggle_sidebar()
            elif not self.winfo_ismapped():
                pass
                
            self.explorer_tree.reveal_file(path)

    def update_outline(self, symbols):
        """Dışarıdan gelen sembolleri anahat (outline) panelinde göster"""
        if hasattr(self, 'outline_panel'):
            self.outline_panel.update_outline(symbols)

    def _refresh_explorer(self):
        """Gezgini yenile"""
        self.explorer_tree.refresh()

    def update_variables(self, vars_json):
        """Gelen canlı değişken verilerini panelde güncelle"""
        if hasattr(self, 'var_watch_panel'):
            self.var_watch_panel.update_from_json(vars_json)
