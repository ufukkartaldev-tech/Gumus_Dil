import tkinter as tk
import os
import customtkinter as ctk
from .toolbar import ToolBar
from .status_bar import StatusBar
from .sidebar import Sidebar
from .debug_panels import DebugControlBar
from .terminal import Terminal
from .canvas_panel import CanvasPanel
from .game_view import GameView
from .mimari_visualization import FactorySimulation
from .gpio_panel import GPIOPanel

class LayoutManager:
    """Arayüz Yerleşim ve Bileşen Yönetimi"""
    
    def __init__(self, main_window, config):
        self.main_window = main_window
        self.config = config
        self.root = main_window.root
        
        # State
        self.minimap_hidden = False
        self.zen_mode = False
        self.activity_buttons = {}

    def setup_layout(self):
        """Ana pencere yerleşimini oluştur"""
        theme = self.config.THEMES[self.config.theme]
        
        # 1. Ana Konteyner
        self.main_window.main_container = ctk.CTkFrame(self.root, fg_color=theme['bg'], corner_radius=0)
        self.main_window.main_container.pack(fill=tk.BOTH, expand=True)

        # 2. Araç Çubuğu (Toolbar)
        self.main_window.toolbar = ToolBar(self.main_window.main_container, self.main_window, self.config)
        self.main_window.toolbar.pack(side="top", fill="x")
        
        # Alias'lar (Geriye uyumluluk)
        self.main_window.toolbar_frame = self.main_window.toolbar
        self.main_window.run_btn = self.main_window.toolbar.run_btn
        self.main_window.stop_btn = self.main_window.toolbar.stop_btn
        self.main_window.debug_control_placeholder = self.main_window.toolbar.debug_placeholder

        # 3. Durum Çubuğu (Status Bar)
        self.main_window.status_bar = StatusBar(self.main_window.main_container, self.config)
        self.main_window.status_bar.pack(side="bottom", fill="x")
        self.main_window.status_bar.set_theme_callback(self.main_window.show_theme_selector)

        # 4. Workspace (Activity Bar + Sidebar + Editor + Panels)
        self.main_window.workspace_container = ctk.CTkFrame(self.main_window.main_container, fg_color="transparent", corner_radius=0)
        self.main_window.workspace_container.pack(fill="both", expand=True)

        # 5. Activity Bar (Sol Şerit)
        self.setup_activity_bar(theme)

        # 6. Ana Bölücü (Splitter: Sidebar | Editor/RightPane)
        self.main_window.paned_window = tk.PanedWindow(
            self.main_window.workspace_container, 
            orient=tk.HORIZONTAL, 
            bg=theme['bg'], 
            sashwidth=4, 
            sashrelief='flat'
        )
        self.main_window.paned_window.pack(side="left", fill=tk.BOTH, expand=True)
        
        # 7. Sidebar
        self.setup_sidebar()

        # 8. Sağ Taraf (Splitter: Editor | BottomPanel)
        self.main_window.right_pane = tk.PanedWindow(
            self.main_window.paned_window, 
            orient=tk.VERTICAL, 
            bg=theme['bg'], 
            sashwidth=4, 
            sashrelief='flat'
        )
        self.main_window.paned_window.add(self.main_window.right_pane, stretch="always")
        
        # 9. Editör Alanı
        self.setup_editor_area(theme)
        
        # 10. Alt Paneller (Terminal, vb.)
        self.setup_bottom_panels(theme)
        
        # Initial State
        if hasattr(self.main_window, 'new_file'):
            self.main_window.new_file()
            
        # Derleyici Kontrolü (Gecikmeli)
        self.root.after(1000, self.main_window.check_compiler_health)

    def setup_activity_bar(self, theme):
        self.main_window.activity_bar = ctk.CTkFrame(
            self.main_window.workspace_container, 
            width=55, 
            fg_color=theme['sidebar_bg'], 
            corner_radius=0,
            border_width=1,
            border_color=theme['border']
        )
        self.main_window.activity_bar.pack(side="left", fill="y")
        self.main_window.activity_bar.pack_propagate(False)

        # Butonları ekle
        self._add_activity_icon("📂", "Gezgin", "explorer", active=True)
        self._add_activity_icon("🔍", "Ara", "search")
        self._add_activity_icon("📜", "Outline", "outline")
        self._add_activity_icon("💎", "Hafıza", "memory")
        self._add_activity_icon("🏋️", "Gümüş GYM", "training")
        self._add_activity_icon("🔬", "Variables", "variables")
        self._add_activity_icon("📚", "Call Stack", "callstack")
        self._add_activity_icon("🤖", "Gümüş Zeka", "ai")
        self._add_activity_icon("🐍", "Python Çevirici", "transpiler")
        self._add_activity_icon("🛒", "Gümüş Pazar", "market")
        self._add_activity_icon("📊", "Gümüş Analiz", "profiler")
        self._add_activity_icon("📚", "Gümüş Sözlük", "docs")
        self._add_activity_icon("🌿", "Gümüş Akış", "flowchart")
        self._add_activity_icon("🐆", "Pardus", "pardus")
        self._add_activity_icon("📓", "Notlar", "notes")
        self._add_activity_icon("⚙️", "Ayarlar", "settings", side="bottom")

    def _add_activity_icon(self, icon, tooltip, mode, side="top", active=False):
        theme = self.config.THEMES[self.config.theme]
        btn = ctk.CTkButton(
            self.main_window.activity_bar,
            text=icon,
            width=55,
            height=50,
            fg_color=theme['accent'] if active else "transparent",
            hover_color=theme['hover'],
            font=("Segoe UI", 20),
            corner_radius=0,
            text_color="white" if active else theme['comment'],
            command=lambda m=mode: self.on_activity_click(m)
        )
        btn.pack(side=side, pady=0)
        self.activity_buttons[mode] = btn
        
        # Main Window'a da referans ekle (eskisi gibi erişebilsinler diye)
        if not hasattr(self.main_window, 'activity_buttons'):
            self.main_window.activity_buttons = {}
        self.main_window.activity_buttons[mode] = btn

    def on_activity_click(self, mode):
        if mode == "settings":
            self.main_window.show_theme_selector()
            return

        if hasattr(self.main_window, 'sidebar'):
            self.main_window.sidebar.switch_mode(mode)
            
            # İkon vurgula
            theme = self.config.THEMES[self.config.theme]
            for m, btn in self.activity_buttons.items():
                if m != "settings":
                    btn.configure(fg_color=theme['accent'] if m == mode else "transparent")
            
            if mode == "outline":
                self.main_window.update_outline()

    def setup_sidebar(self):
        if self.config.show_sidebar:
            callbacks = {
                'on_file_select': self.main_window.open_file_from_path,
                'on_jump': self.main_window.jump_to_line,
                'on_apply_code': self.main_window.apply_code_snippet,
                'get_code': lambda: self.main_window.get_current_editor().get('1.0', tk.END) if self.main_window.get_current_editor() else ""
            }
            self.main_window.sidebar = Sidebar(self.main_window.paned_window, self.config, callbacks)
            self.main_window.paned_window.add(self.main_window.sidebar, minsize=250)
            
            # Debug Control Bar
            self.main_window.debug_control_bar = DebugControlBar(
                self.main_window.debug_control_placeholder,
                self.main_window.sidebar.debugger,
                self.config
            )
            self.main_window.debug_control_bar.pack(fill="both", expand=True)
            
            # Callbacks
            self.main_window.sidebar.debugger.on_line_change = self.main_window._on_debug_line_change
            self.main_window.sidebar.debugger.on_variable_change = self.main_window._on_debug_variable_change

    def setup_editor_area(self, theme):
        # Container
        self.main_window.editor_main_frame = ctk.CTkFrame(self.main_window.right_pane, fg_color="transparent", corner_radius=0)
        self.main_window.right_pane.add(self.main_window.editor_main_frame, stretch="always")

        # Tab Bar
        self.main_window.tab_bar = ctk.CTkFrame(self.main_window.editor_main_frame, height=35, fg_color=theme['sidebar_bg'], corner_radius=0)
        self.main_window.tab_bar.pack(side="top", fill="x")
        self.main_window.tab_bar.pack_propagate(False)

        # Breadcrumbs
        self.main_window.breadcrumbs_frame = ctk.CTkFrame(self.main_window.editor_main_frame, height=28, fg_color=theme['bg'], corner_radius=0)
        self.main_window.breadcrumbs_frame.pack(side="top", fill="x")
        self.main_window.breadcrumbs_frame.pack_propagate(False)

        # Editor Content
        self.main_window.editor_content_area = ctk.CTkFrame(self.main_window.editor_main_frame, fg_color="transparent", corner_radius=0)
        self.main_window.editor_content_area.pack(fill="both", expand=True)

    def setup_bottom_panels(self, theme):
        self.main_window.bottom_tabs = ctk.CTkTabview(
            self.main_window.right_pane, 
            fg_color=theme['bg'],
            corner_radius=0,
            border_width=0,
            anchor="nw",
            height=200
        )
        self.main_window.right_pane.add(self.main_window.bottom_tabs, minsize=150)
        
        # Terminal
        tab_term = self.main_window.bottom_tabs.add("Terminal")
        self.main_window.terminal = Terminal(tab_term, self.config)
        self.main_window.terminal.pack(fill="both", expand=True)
        
        # Diğer Paneller
        panels = [
            ("Tuval (Görsel)", CanvasPanel, 'canvas_panel'),
            ("Oyun (Voxel)", GameView, 'game_view'),
            ("mimari (Fabrika)", FactorySimulation, 'mimari_view'),
            ("Donanım (GPIO)", GPIOPanel, 'gpio_panel')
        ]
        
        for title, cls, attr in panels:
            tab = self.main_window.bottom_tabs.add(title)
            instance = cls(tab, self.config)
            instance.pack(fill="both", expand=True)
            setattr(self.main_window, attr, instance)
            
        # Tab Styling
        self.main_window.bottom_tabs._segmented_button.configure(
            font=("Segoe UI", 12, "bold"),
            selected_color=theme['accent'],
            selected_hover_color=theme['select_bg'],
            unselected_color=theme['sidebar_bg'],
            unselected_hover_color=theme['hover'],
            corner_radius=6,
            height=28
        )
        self.main_window.bottom_tabs._segmented_button.grid(pady=2, padx=5, sticky="w")

    # --- Toggle Methods ---
    
    def toggle_terminal(self):
        try:
            if self.main_window.bottom_tabs.winfo_ismapped():
                self.main_window.right_pane.forget(self.main_window.bottom_tabs)
            else:
                self.main_window.right_pane.add(self.main_window.bottom_tabs, height=250)
        except: pass

    def toggle_zen_mode(self):
        self.zen_mode = not self.zen_mode
        mw = self.main_window
        
        if self.zen_mode:
            mw.activity_bar.pack_forget()
            if mw.config.show_sidebar and hasattr(mw, 'sidebar'):
                mw.sidebar.pack_forget() # PanedWindow'dan nasıl çıkar?
                try: mw.paned_window.forget(mw.sidebar)
                except: pass
            
            mw.toolbar.pack_forget()
            mw.status_bar.pack_forget()
            try: mw.right_pane.forget(mw.bottom_tabs)
            except: pass
            
            mw.show_toast("🧘 Zen Modu Açık", "info")
        else:
            mw.toolbar.pack(side="top", fill="x", before=mw.workspace_container)
            mw.activity_bar.pack(side="left", fill="y", before=mw.paned_window)
            
            if mw.config.show_sidebar and hasattr(mw, 'sidebar'):
                 try: mw.paned_window.add(mw.sidebar, before=mw.right_pane, minsize=250)
                 except: pass # Zaten ekli olabilir
            
            mw.status_bar.pack(side="bottom", fill="x")
            try: mw.right_pane.add(mw.bottom_tabs, height=250)
            except: pass
            
            mw.show_toast("Zen Modu Kapalı", "info")

    def toggle_sidebar(self):
        mw = self.main_window
        if not hasattr(mw, 'sidebar'): return
        
        try:
            if mw.sidebar.winfo_ismapped():
                mw.paned_window.forget(mw.sidebar)
            else:
                mw.paned_window.add(mw.sidebar, before=mw.right_pane, minsize=250)
        except: pass

    def toggle_minimap(self):
        self.minimap_hidden = not self.minimap_hidden
        
        for editor in self.main_window.editors.values():
            if hasattr(editor, 'minimap'):
                if self.minimap_hidden:
                    editor.minimap.grid_forget()
                else:
                    editor.minimap.grid(row=1, column=2, sticky="ns", padx=(0, 8), pady=(4, 8))
        
        status = "Kapalı" if self.minimap_hidden else "Açık"
        self.main_window.show_toast(f"🗺️ GümüşHarita {status}", "info")


