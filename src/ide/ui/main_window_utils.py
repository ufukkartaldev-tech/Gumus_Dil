# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import os
import threading
from ..core.compiler import CompilerRunner
from ..core.symbols import SymbolExtractor

class MainWindowActionsMixin:
    """MainWindow için çalışma ve çeviri aksiyonları"""
    
    def run_code(self):
        self.code_runner.run_code()
        
    def stop_code(self):
        self.code_runner.stop_code()

    def translate_current_file(self):
        """Aktif Python dosyasını GümüşDil'e çevirir."""
        editor = self.get_current_editor()
        if not editor: return
        
        code = editor._textbox.get("1.0", tk.END)
        from ..core.python_to_gumus import PythonToGumusTranspiler
        translator = PythonToGumusTranspiler()
        
        self.show_toast("🐍 Python -> 💎 Gümüş...", "info")
        gumus_code = translator.transpile(code)
        
        self.new_file()
        new_editor = self.get_current_editor()
        if new_editor:
            new_editor._textbox.insert("1.0", gumus_code)
            self.show_toast("Tercüme tamamlandı! ✨", "success")

    def debug_code(self):
        self.show_toast("🐞 Hata Ayıklama Modu Başlatılıyor...", "info")

    def show_package_manager(self): 
        self.show_toast("📦 Paket Yöneticisi Yakında!", "info")
    
    def show_project_translator(self):
        try:
            from .project_translator_ui import ProjectTranslatorUI
            ui = ProjectTranslatorUI(self, self.config)
            ui.focus()
        except Exception as e:
            self.show_toast(f"Çevirici arayüzü yüklenemedi: {e}", "error")

    def show_factory_sim(self): 
        if hasattr(self, 'mimari_view'): self.mimari_view.show()
        else: self.show_toast("🏭 Fabrika simülasyonu yükleniyor...", "info")
    
    def test_voxel_engine(self):
        self.show_toast("🔌 Voxel Engine Test Modu", "info")

    def show_docs(self): 
        self.show_toast("📚 Dokümantasyon yükleniyor...", "info")
    
    def show_shortcuts(self): 
        self.show_toast("⌨️ Kısayollar Aktif Edildi!", "info")
    
    def show_about(self): 
        messagebox.showinfo("Hakkında", "💎 Gümüşdil IDE\nSürüm 2.0\nUfuk Kartal tarafından geliştirilmiştir.")

    def show_ast_viewer(self):
        """AST Görselleştiriciyi aç"""
        editor = self.get_current_editor()
        if not editor or not editor.file_path or not os.path.exists(editor.file_path):
            self.show_toast("AST için önce dosyayı kaydet yeğenim!", "warning")
            return

        from .ast_viewer import ASTViewer
        self.show_toast("AST Analiz Ediliyor... 🌳", "info")
        ast_json, err, code = CompilerRunner.get_ast_json(editor.file_path)
        
        if code != 0:
            self.show_toast(f"AST Hatası: {err}", "error")
            return
            
        if hasattr(self, 'ast_viewer_window') and self.ast_viewer_window.winfo_exists():
            self.ast_viewer_window.destroy()
        self.ast_viewer_window = ASTViewer(self.root, ast_json, self.config)

    def update_outline(self, event=None):
        editor = self.get_current_editor()
        if not editor: return
        if hasattr(self, 'sidebar') and hasattr(self.sidebar, 'update_outline'):
            text = editor.get("1.0", 'end-1c')
            symbols = SymbolExtractor.extract_from_text(text)
            self.sidebar.update_outline(symbols)

class MainWindowUIMixin:
    """MainWindow için UI yönetimi ve yardımcılar"""
    
    def show_toast(self, message, kind='info'):
        self.notifier.show(message, kind)

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
                editor.delete(f"{line}.0", f"{line}.end")
                editor.insert(f"{line}.0", code)
            else:
                editor.insert(tk.INSERT, code)

    def update_cursor_position(self, event=None):
        import time
        t = time.time()
        if t - self.last_ui_update_time < self.ui_update_interval: return
        self.last_ui_update_time = t
        editor = self.get_current_editor()
        if editor:
            line, col = editor._textbox.index(tk.INSERT).split('.')
            if hasattr(self, 'status_bar'): self.status_bar.set_cursor(line, col)

    def get_active_editor(self):
        """Alias for get_current_editor for MenuManager compatibility"""
        return self.get_current_editor()

    def _update_git_status(self, path):
        if not path: return
        folder = os.path.dirname(path)
        if not os.path.isdir(folder): return
        def check_git():
            try:
                import subprocess
                res = subprocess.run(['git', 'branch', '--show-current'], cwd=folder, capture_output=True, text=True,
                                   creationflags=0x08000000 if os.name == 'nt' else 0)
                if res.returncode == 0:
                    branch = res.stdout.strip()
                    if branch and hasattr(self, 'status_bar'):
                        self.root.after(0, lambda: self.status_bar.update_git_info(branch))
            except: pass
        threading.Thread(target=check_git, daemon=True).start()
