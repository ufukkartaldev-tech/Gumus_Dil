# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
import threading
import json
from pathlib import Path
from .editor import CodeEditor
from .terminal import Terminal
from .canvas_panel import CanvasPanel
from .game_view import GameView
from .sidebar import Sidebar
from .ast_viewer import ASTViewer
from .mimari_visualization import FactorySimulation
from .welcome_screen_v2 import WelcomeScreenV2 as WelcomeScreen
from .status_bar import StatusBar
from .gpio_panel import GPIOPanel
from .command_palette_v2 import CommandPaletteV2 as CommandPalette
from .debug_panels import DebugControlBar
from ..core.compiler import CompilerRunner
from ..core.ast_viewer import AstVisualizer
from ..core.symbols import SymbolExtractor
from ..core.plugin_manager import PluginManager # Gümüş-Modül
from ..core.shell import GumusShell
from ..config import TEMP_DIR


class MainWindow:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.editors = {} # {path: editor_widget}
        self.active_tab = None # current path
        self.last_run_file = None
        self.memory_buffer = []
        self.is_collecting_memory = False
        self.process = None # Aktif derleyici process'i (Zombi önleme için)
        
        # 🚀 Optimizasyon: UI Throttle (Sıklık kısıtlama)
        import time
        self.last_ui_update_time = 0
        self.last_vars_update_time = 0
        self.ui_update_interval = 0.05 # 50ms (Saniyede max 20 güncelleme)

        # Plugin Yöneticisi (En başta başlat ki hooklar hazır olsun)
        self.plugin_manager = PluginManager(self)
        
        self.root.title(f"💎 Gümüşdil IDE - {config.mode.upper()}")
        self.root.geometry("1400x900" if config.mode == 'pro' else "1000x800")
        
        # Grid configure for root to expand
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # İkon ayarla (opsiyonel)
        try:
            # Windows için .ico dosyası kullanılabilir
            pass
        except:
            pass
        
        # self.setup_layout() # Moved to later
        self.create_menu()
        self.setup_keybindings()
        
        # Auto-Save
        # self.editor.bind('<KeyRelease>', self.auto_save) # This will be handled by the active editor
        self.load_autosave()
        
        # Hoş geldin ekranı göster
        if config.show_welcome:
            self.show_welcome_screen()

        # Kapanış protokolü (Zombi process önleme)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


        # Dosya Yöneticisi Başlat
        from .file_manager import CodeFileManager
        self.file_manager = CodeFileManager(self, config)

        # Bildirim Yöneticisi Başlat
        from .toast import ToastNotifier
        self.notifier = ToastNotifier(self.root, config)

        # Kod Yöneticisi Başlat
        from .code_runner import CodeRunner
        self.code_runner = CodeRunner(self, config)

        # GümüşShell Başlat
        # Terminal henuz hazir degil, setup_layout ile olusacak
        self.terminal = None 
        self.gumus_shell = GumusShell(output_callback=lambda msg: self.terminal.write_text(msg) if self.terminal else print(msg))
        # self.gumus_shell.terminal_clear_callback = self.terminal.clear # erteleyelim
        # self.terminal.prompt_label.configure(text=" GÜMÜŞ > ") # erteleyelim

        # Arayüzü Kur (Managers hazır olduktan sonra)
        self.setup_layout()
        
        # Tab Yöneticisini File Manager'a bağla (Circular dependency çözümü)
        if hasattr(self, 'tab_manager'):
            self.file_manager.tab_manager = self.tab_manager

        # Eklentileri Yükle ve Başlat (UI Hazır Olduktan Sonra)
        # Fix: 'MainWindow' object has no attribute 'toolbar_frame' hatası için buraya taşındı
        self.plugin_manager.load_plugins()
        self.plugin_manager.trigger_hook("on_startup")
        self.plugin_manager.trigger_hook("on_ui_setup", self)

    def run_code(self):
        self.code_runner.run_code()
        
    def stop_code(self):
        self.code_runner.stop_code()
        
    def _send_input_to_process(self, text):
        if self.code_runner.process:
            self.code_runner._send_input_to_process(text)
        else:
            # Program çalışmıyorsa Kabuk (REPL) olarak davran
            prompt = self.gumus_shell.execute_line(text)
            if prompt:
                self.terminal.prompt_label.configure(text=f" {prompt} ")

    def show_toast(self, message, kind='info'):
        """Bildirim Merkezi: Kullanıcıya geçici mesaj göster"""
        self.notifier.show(message, kind)
        
    def _dummy_fade_toast(self):
        # Eski referansları temizlemek için (silinebilir)
        pass

    def create_menu(self):
        """Üst menü çubuğunu oluştur"""
        # Placeholder methods for menu creation
        self.show_theme_selector = lambda: None
        self.show_ast_viewer = self.show_ast_viewer
        self.toggle_minimap = lambda: None
        self.toggle_zen_mode = lambda: None
        self.toggle_terminal = lambda: None
        self.show_package_manager = lambda: self.show_toast("📦 Paket Yöneticisi Yakında!", "info")
        self.show_project_translator = lambda: None
        self.show_factory_sim = lambda: None
        self.test_voxel_engine = lambda: None
        self.show_docs = lambda: self.show_toast("📚 Dokümantasyon yükleniyor...", "info")
        self.show_shortcuts = lambda: self.show_toast("⌨️ Kısayollar Aktif Edildi!", "info")
        self.show_about = lambda: messagebox.showinfo("Hakkında", "💎 Gümüşdil IDE\nSürüm 2.0\nUfuk Kartal tarafından geliştirilmiştir.")
        
        self.show_welcome_screen = lambda: None
        from .menu_manager import MenuManager
        self.menu_manager = MenuManager(self)
        self.menu_manager.create_menu()

    def setup_layout(self):
        # ... (Önceki kodlar)
        # Layout Yöneticisini Başlat
        from .layout_manager import LayoutManager
        self.layout_manager = LayoutManager(self, self.config)
        
        # Tab Yöneticisini Başlat
        from .tab_manager import TabManager 
        self.tab_manager = TabManager(self, self.config)
        self.file_manager.tab_manager = self.tab_manager

        # Tab Aliases - LayoutManager setup öncesi gerekli!
        self.switch_to_tab = self.tab_manager.switch_to_tab
        self.close_tab = self.tab_manager.close_tab
        self.refresh_tabs = self.tab_manager.refresh_tabs
        
        # Dialog Yöneticisini Başlat
        from .dialog_manager import DialogManager
        self.dialog_manager = DialogManager(self, self.config)
        self.show_theme_selector = self.dialog_manager.show_theme_selector
        self.show_ast_viewer = self.show_ast_viewer 
        self.toggle_minimap = self.layout_manager.toggle_minimap
        self.toggle_zen_mode = self.layout_manager.toggle_zen_mode
        self.toggle_terminal = self.layout_manager.toggle_terminal
        self.on_activity_click = self.layout_manager.on_activity_click
        self.toggle_sidebar = self.layout_manager.toggle_sidebar
        
        # Dialog Aliases
        self.show_welcome_screen = self.dialog_manager.show_welcome_screen
        self.apply_theme = self.dialog_manager.apply_theme
        self.show_command_palette = self.dialog_manager.show_command_palette
        self.check_compiler_health = self.dialog_manager.check_compiler_health
        
        # Layout Setup (Bu adımda new_file -> switch_to_tab çağrılıyor)
        self.layout_manager.setup_layout()
        
        self.show_welcome_screen = self.dialog_manager.show_welcome_screen
        self.show_theme_selector = self.dialog_manager.show_theme_selector
        self.apply_theme = self.dialog_manager.apply_theme
        self.show_command_palette = self.dialog_manager.show_command_palette
        self.check_compiler_health = self.dialog_manager.check_compiler_health

        # Context Action Handler
        from .context_action import ContextActionHandler
        self.context_handler = ContextActionHandler(self)
        self.on_ctx_action = self.context_handler.handle_action
        self._on_fix_request = self.context_handler.handle_fix_request

    def setup_keybindings(self):
        """Kısayol Tuşlarını Tanımla"""
        # Dosya İşlemleri
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-N>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file_dialog())
        self.root.bind("<Control-O>", lambda e: self.open_file_dialog())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-S>", lambda e: self.save_as_file())
        
        # Çalıştırma
        self.root.bind("<F5>", lambda e: self.run_code())
        self.root.bind("<F9>", lambda e: self.debug_code())
        
        # Görünüm
        self.root.bind("<Control-b>", lambda e: self.toggle_sidebar())
        self.root.bind("<Control-B>", lambda e: self.toggle_sidebar())
        self.root.bind("<Control-grave>", lambda e: self.toggle_terminal())
        self.root.bind("<Control-j>", lambda e: self.toggle_terminal())
        self.root.bind("<Control-J>", lambda e: self.toggle_terminal())
        self.root.bind("<Control-period>", lambda e: self.toggle_zen_mode())
        
        # Palette & Sekme
        self.root.bind("<Control-p>", lambda e: self.show_command_palette())
        self.root.bind("<Control-P>", lambda e: self.show_command_palette())
        self.root.bind("<Control-w>", lambda e: self.close_tab(self.active_tab))
        self.root.bind("<Control-W>", lambda e: self.close_tab(self.active_tab))

    def new_file(self): self.file_manager.new_file()
    def open_file_dialog(self): self.file_manager.open_file_dialog()
    def save_file(self): self.file_manager.save_file()
    def save_as_file(self): self.file_manager.save_as_file()
    def open_file_from_path(self, path): self.file_manager.open_file_from_path(path)
    def format_code(self):
        editor = self.get_current_editor()
        if editor:
            editor.format_code()
    
    def debug_code(self):
        self.show_toast("🐞 Hata Ayıklama Modu Başlatılıyor...", "info")
        # Gelecekte buraya debugger logic gelecek
        
    def jump_to_line(self, line):
        editor = self.get_current_editor()
        if editor:
            editor._textbox.see(f"{line}.0")
            editor._textbox.mark_set("insert", f"{line}.0")
            editor._highlight_current_line()
            
    def apply_code_snippet(self, code, line=None):
        editor = self.get_current_editor()
        if editor:
            if line:
                # Satıra odaklı tamir
                editor.delete(f"{line}.0", f"{line}.end")
                editor.insert(f"{line}.0", code)
                self.show_toast(f"📍 Satır {line} mühürlendi!", "success")
            else:
                editor.insert(tk.INSERT, code)
            
    def update_title(self):
        title = "💎 Gümüşdil IDE"
        if self.active_tab:
            title += f" - {os.path.basename(self.active_tab)}"
        self.root.title(title)
        
    def update_outline(self, event=None):
        if hasattr(self, 'sidebar') and hasattr(self.sidebar, 'update_outline'):
            self.sidebar.update_outline()
            
    def load_autosave(self): pass
    
    def handle_breadcrumb_click(self, path):
        self.open_file_from_path(path)
        
    def update_cursor_position(self, event=None):
        editor = self.get_current_editor()
        if editor:
            pos = editor._textbox.index(tk.INSERT)
            line, col = pos.split('.')
            if hasattr(self, 'status_bar'):
                self.status_bar.set_cursor(line, col)
            
    def show_package_manager(self): self.show_toast("📦 Paket Yöneticisi Yakında!", "info")
    
    def show_project_translator(self):
        """Python projesini toplu halde GümüşDil'e çevirir."""
        from tkinter import filedialog
        source = filedialog.askdirectory(title="Python Proje Klasörünü Seç")
        if not source: return
        
        target = filedialog.askdirectory(title="GümüşDil Projesinin Kaydedileceği Klasörü Seç")
        if not target: return
        
        self.show_toast("🚀 Proje Dönüştürülüyor...", "info")
        
        from ..core.project_converter import GümüşProjectConverter
        converter = GümüşProjectConverter(self)
        count, errors = converter.convert_project(source, target)
        
        msg = f"✅ Dönüştürme Tamamlandı!\n📄 {count} dosya çevrildi."
        if errors:
            msg += f"\n🚨 {len(errors)} hata oluştu."
        
        messagebox.showinfo("Proje Çevirici", msg)
        
        # Pardus Paketleme sorabiliriz
        if count > 0:
            if messagebox.askyesno("Paketleme", "Bu projeyi hemen Pardus (.deb) paketi haline getirelim mi?"):
                converter.package_converted_project(target)

    def translate_current_file(self):
        """Aktif Python dosyasını GümüşDil'e çevirir."""
        editor = self.get_current_editor()
        if not editor: return
        
        code = editor._textbox.get("1.0", tk.END)
        from ..core.python_to_gumus import PythonToGumusTranspiler
        translator = PythonToGumusTranspiler()
        
        self.show_toast("🐍 Python -> 💎 Gümüş...", "info")
        gumus_code = translator.transpile(code)
        
        # Yeni bir sekmede açalım
        self.new_file()
        new_editor = self.get_current_editor()
        if new_editor:
            new_editor._textbox.insert("1.0", gumus_code)
            self.show_toast("Tercüme başarıyla tamamlandı! ✨", "success")

    def show_factory_sim(self): 
        if hasattr(self, 'mimari_view'): self.mimari_view.show()
    def show_docs(self): self.show_toast("📚 Dokümantasyon yükleniyor...", "info")
    def show_shortcuts(self): self.show_toast("⌨️ Kısayollar Aktif Edildi!", "info")
    def show_about(self): messagebox.showinfo("Hakkında", "💎 Gümüşdil IDE\nSürüm 2.0\nUfuk Kartal tarafından geliştirilmiştir.")

    def get_current_editor(self):
        """Aktif editör nesnesini döndürür"""
        if hasattr(self, 'active_tab') and self.active_tab in self.editors:
            return self.editors[self.active_tab]
        return None

    def show_ast_viewer(self):
        """AST Görselleştiriciyi aç (Dinamik Ağaç)"""
        editor = self.get_current_editor()
        if not editor: return
        
        # Dosya yolu yoksa (Adsız dosya), önce uyar
        if not editor.file_path or not os.path.exists(editor.file_path):
            self.show_toast("AST için önce dosyayı kaydet yeğenim!", "warning")
            return

        # Derleyiciden JSON al
        self.show_toast("AST Analiz Ediliyor... 🌳", "info")
        ast_json, err, code = CompilerRunner.get_ast_json(editor.file_path)
        
        if code != 0:
            self.show_toast(f"AST Hatası: {err}", "error")
            return
            
        # Pencereyi göster
        if hasattr(self, 'ast_viewer_window') and self.ast_viewer_window.winfo_exists():
            self.ast_viewer_window.destroy() # Yenilemek için kapatıp aç
            
        self.ast_viewer_window = ASTViewer(self.root, ast_json, self.config)

    def on_line_click(self, line):
        """Editörden gelen satır tıklama olayı"""
        if hasattr(self, 'ast_viewer_window') and self.ast_viewer_window.winfo_exists():
            self.ast_viewer_window.highlight_line(line)


    # --- Debugger Callbacks ---
    def _on_debug_line_change(self, line):
        """Debugger aktif satırı değiştirdiğinde"""
        self.jump_to_line(line)
        
    def _on_debug_variable_change(self, vars_json):
        """Debugger değişkenleri güncellediğinde"""
        # Şimdilik pass, debug_panels handle ediyor
        pass

    def _update_git_status(self, path):
        """Dosya için git durumunu güncelle (Basit Entegrasyon)"""
        try:
            if not path: return
            
            # Dosyanın olduğu klasör
            folder = os.path.dirname(path)
            if not os.path.isdir(folder): return
            
            def check_git():
                try:
                    import subprocess
                    # Git branch adını al
                    # not: windows'ta 'git' komutu path'te olmalı
                    result = subprocess.run(
                        ['git', 'branch', '--show-current'], 
                        cwd=folder, 
                        capture_output=True, 
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    
                    if result.returncode == 0:
                        branch = result.stdout.strip()
                        if branch and hasattr(self, 'status_bar'):
                            self.root.after(0, lambda: self.status_bar.update_git_info(branch))
                    else:
                        # Git reposu değilse
                        if hasattr(self, 'status_bar'):
                             self.root.after(0, lambda: self.status_bar.update_git_info(None))
                except Exception:
                    pass

            # Thread içinde çalıştır ki UI donmasın
            threading.Thread(target=check_git, daemon=True).start()
            
        except Exception:
            pass

    def on_closing(self):
        """IDE kapanırken temizlik işlemleri (Zombi process önleme)"""
        try:
            # 1. Aktif process'i temizle
            if self.process:
                try:
                    self.process.terminate()  # Önce nazikçe sor
                    self.process.wait(timeout=1)  # 1 saniye bekle
                except:
                    try:
                        self.process.kill()  # Dinlemezse zorla kapat
                    except:
                        pass
                self.process = None
            
            # 2. Plugin cleanup hook'ları
            self.plugin_manager.trigger_hook("on_shutdown")
            
            # 3. Ayarları kaydet
            self.config.save_settings()
            
            # 4. Pencereyi kapat
            self.root.destroy()
            
        except Exception as e:
            print(f"Kapanış hatası: {e}")
            self.root.destroy()  # Yine de kapat

if __name__ == "__main__":
    from ..config import Config
    
    # CustomTkinter ayarları
    ctk.set_appearance_mode("Dark") 
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    config = Config(mode='pro') 
    app = MainWindow(root, config)
    root.mainloop()


