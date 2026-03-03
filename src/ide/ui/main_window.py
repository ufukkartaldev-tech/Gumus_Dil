# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import os
import threading
from pathlib import Path

from ..core.plugin_manager import PluginManager
from ..core.shell import GumusShell
from .main_window_utils import MainWindowActionsMixin, MainWindowUIMixin

class MainWindow(MainWindowActionsMixin, MainWindowUIMixin):
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.last_run_file = None
        self.memory_buffer = []
        self.is_collecting_memory = False
        self.process = None
        
        self.last_ui_update_time = 0
        self.ui_update_interval = 0.05

        # Plugin Yöneticisi
        self.plugin_manager = PluginManager(self)
        
        self.root.title(f"💎 Gümüşdil IDE - {config.mode.upper()}")
        self.root.geometry("1000x800")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.create_menu()
        self.setup_keybindings()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Managerları Başlat
        from .file_manager import CodeFileManager
        from .toast import ToastNotifier
        from .code_runner import CodeRunner
        
        self.file_manager = CodeFileManager(self, config)
        self.notifier = ToastNotifier(self.root, config)
        self.code_runner = CodeRunner(self, config)
        
        self.terminal = None 
        self.gumus_shell = GumusShell(output_callback=lambda msg: self.terminal.write_text(msg) if self.terminal else print(msg))

        self.setup_layout()
        
        if hasattr(self, 'tab_manager'): self.file_manager.tab_manager = self.tab_manager

        self.plugin_manager.load_plugins()
        self.plugin_manager.trigger_hook("on_startup")
        self.file_manager.start_auto_save_loop()

    def create_menu(self):
        from .menu_manager import MenuManager
        self.menu_manager = MenuManager(self)
        self.menu_manager.create_menu()

    def setup_layout(self):
        from .layout_manager import LayoutManager
        from .tab_manager import TabManager 
        from .dialog_manager import DialogManager
        from .context_action import ContextActionHandler
        
        self.layout_manager = LayoutManager(self, self.config)
        self.tab_manager = TabManager(self, self.config)
        self.file_manager.tab_manager = self.tab_manager

        # Aliases
        self.switch_to_tab = self.tab_manager.switch_to_tab
        self.close_tab = self.tab_manager.close_tab
        self.refresh_tabs = self.tab_manager.refresh_tabs
        
        self.dialog_manager = DialogManager(self, self.config)
        self.show_theme_selector = self.dialog_manager.show_theme_selector
        self.toggle_minimap = self.layout_manager.toggle_minimap
        self.toggle_zen_mode = self.layout_manager.toggle_zen_mode
        self.toggle_terminal = self.layout_manager.toggle_terminal
        self.on_activity_click = self.layout_manager.on_activity_click
        self.toggle_sidebar = self.layout_manager.toggle_sidebar
        
        self.show_welcome_screen = self.dialog_manager.show_welcome_screen
        self.apply_theme = self.dialog_manager.apply_theme
        self.show_command_palette = self.dialog_manager.show_command_palette
        self.check_compiler_health = self.dialog_manager.check_compiler_health
        
        self.layout_manager.setup_layout()
        self.context_handler = ContextActionHandler(self)
        self.on_ctx_action = self.context_handler.handle_action

    def setup_keybindings(self):
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file_dialog())
        self.root.bind("<Control-Shift-o>", lambda e: self.open_folder_dialog())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-S>", lambda e: self.save_as_file())
        self.root.bind("<F5>", lambda e: self.run_code())
        self.root.bind("<Control-b>", lambda e: self.toggle_sidebar())
        self.root.bind("<Control-grave>", lambda e: self.toggle_terminal())
        self.root.bind("<Control-p>", lambda e: self.show_command_palette())
        self.root.bind("<Control-w>", lambda e: self.close_tab())

    # --- Proxy Methods to Managers ---
    def new_file(self): self.file_manager.new_file()
    def open_file_dialog(self): self.file_manager.open_file_dialog()
    def open_folder_dialog(self): self.file_manager.open_folder_dialog()
    def save_file(self): self.file_manager.save_file()
    def save_as_file(self): self.file_manager.save_as_file()
    def open_file_from_path(self, path): self.file_manager.open_file_from_path(path)
    
    def get_current_editor(self):
        if hasattr(self, 'active_tab') and self.active_tab in self.editors:
            return self.editors[self.active_tab]
        return None

    def on_closing(self):
        try:
            if self.process: self.process.terminate()
            self.plugin_manager.trigger_hook("on_shutdown")
            self.config.save_settings()
            self.root.destroy()
        except: self.root.destroy()

    @property
    def editors(self): return self.tab_manager.editors if hasattr(self, 'tab_manager') else {}
        
    @property
    def active_tab(self): return self.tab_manager.active_tab if hasattr(self, 'tab_manager') else None
        
    @active_tab.setter
    def active_tab(self, path):
        if hasattr(self, 'tab_manager'): self.tab_manager.active_tab = path
