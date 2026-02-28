import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from .editor import CodeEditor

class CodeFileManager:
    """Dosya Yönetim İşlemleri"""
    
    def __init__(self, main_window, config):
        self.main_window = main_window
        self.config = config
        
    def new_file(self):
        """Yeni bir sekme aç"""
        # Benzersiz bir anahtar oluştur (Adsız-1, Adsız-2 vb.)
        temp_id_counter = 0
        while f"untitled_{temp_id_counter}" in self.main_window.editors:
            temp_id_counter += 1
        temp_id = f"untitled_{temp_id_counter}"
        
        # Breadcrumb navigasyon callback'i ile oluştur
        editor = CodeEditor(self.main_window.editor_content_area, self.config, on_navigate=self.main_window.handle_breadcrumb_click)
        self.main_window.editors[temp_id] = editor
        if hasattr(self.main_window, 'tab_manager'):
            self.main_window.tab_manager.editors[temp_id] = editor
        self.main_window.switch_to_tab(temp_id)
        
        # Trigger plugin hook
        self.main_window.plugin_manager.trigger_hook("on_editor_init", editor)
        
    def open_file_dialog(self):
        path = filedialog.askopenfilename(filetypes=[("Gümüşdil Dosyaları", "*.tr")])
        if path:
            self.open_file_from_path(path)
            
    def open_folder_dialog(self):
        path = filedialog.askdirectory()
        if path:
            if hasattr(self.main_window, 'sidebar'):
                self.main_window.sidebar.set_root(path)
                self.main_window.terminal.write_text(f">>> Klasör açıldı: {path}\n")
    
    def open_file_from_path(self, path):
        """Dosyayı aç (Eğer zaten açıksa o sekmeye geç)"""
        path = str(Path(path).resolve())
        
        if path in self.main_window.editors:
            self.main_window.switch_to_tab(path)
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            editor = CodeEditor(self.main_window.editor_content_area, self.config, on_navigate=self.main_window.handle_breadcrumb_click)
            editor.insert('1.0', content)
            editor.has_content = True # Placeholder'ı engelle
            
            # Dosya yolunu bildir
            if hasattr(editor, 'set_file_path'):
                editor.set_file_path(path)
            
            self.main_window.editors[path] = editor
            if hasattr(self.main_window, 'tab_manager'):
                self.main_window.tab_manager.editors[path] = editor
            self.main_window.switch_to_tab(path)
            
            # Son kullanılanlara ekle
            self.config.add_recent_file(path)
            
            # Trigger plugin hook
            self.main_window.plugin_manager.trigger_hook("on_editor_init", editor)
            
            # Gümüş-Git Simülasyonunu Güncelle
            self.main_window._update_git_status(path)
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya açılamadı:\n{e}")
            
    def save_file(self):
        if not self.main_window.active_tab: return False
        
        path = self.main_window.active_tab
        # Eğer henüz kaydedilmemiş (untitled) ise dialog aç
        if "untitled" in path:
            path = filedialog.asksaveasfilename(defaultextension=".tr", 
                                               filetypes=[("Gümüşdil Dosyaları", "*.tr")])
            if not path: return False
            
            # Eski editörü yeni yola taşı
            editor = self.main_window.editors.pop(self.main_window.active_tab)
            self.main_window.editors[path] = editor
            if hasattr(self.main_window, 'tab_manager'):
                self.main_window.tab_manager.editors.pop(self.main_window.active_tab, None)
                self.main_window.tab_manager.editors[path] = editor
            self.main_window.active_tab = path
            
        try:
            content = self.main_window.editors[path].get('1.0', tk.END)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Editöre yolu bildir (Breadcrumbs için)
            if hasattr(self.main_window.editors[path], 'set_file_path'):
                self.main_window.editors[path].set_file_path(path)
            
            self.main_window.terminal.write_text(f">>> Dosya Kaydedildi: {os.path.basename(path)}\n")
            self.main_window.refresh_tabs()
            self.main_window.update_title()
            return True
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydetme hatası:\n{e}")
            return False
            
    def save_as_file(self):
        """Farklı Kaydet"""
        if not self.main_window.active_tab: return
        
        default_name = os.path.basename(self.main_window.active_tab)
        path = filedialog.asksaveasfilename(defaultextension=".tr", 
                                           initialfile=default_name,
                                           filetypes=[("Gümüşdil Dosyaları", "*.tr")])
        if not path: return

        try:
            # Yeni dosya olarak kaydet ama sekme ID'sini güncelleme (Save Copy As gibi mi yoksa Rename gibi mi?)
            # Standart davranış: Sekmeyi yeni dosyaya dönüştür
            content = self.main_window.editors[self.main_window.active_tab].get('1.0', tk.END)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Eski editörü yeni yola taşı
            editor = self.main_window.editors.pop(self.main_window.active_tab)
            self.main_window.editors[path] = editor
            if hasattr(self.main_window, 'tab_manager'):
                self.main_window.tab_manager.editors.pop(self.main_window.active_tab, None)
                self.main_window.tab_manager.editors[path] = editor
            self.main_window.active_tab = path
            
            if hasattr(editor, 'set_file_path'):
                editor.set_file_path(path)
                
            self.main_window.terminal.write_text(f">>> Dosya Farklı Kaydedildi: {path}\n")
            self.main_window.refresh_tabs()
            self.main_window.update_title()
            self.config.add_recent_file(path)
            
        except Exception as e:
             messagebox.showerror("Hata", f"Farklı kaydetme hatası:\n{e}")

