import tkinter as tk
import os
import customtkinter as ctk

class TabManager:
    """Sekme (Tab) Yönetimi"""
    
    def __init__(self, main_window, config):
        self.main_window = main_window
        self.config = config
        self.active_tab = None
        self.editors = {} # {path: editor_widget}
        self.tab_close_btns = {} 
        self.dirty_tabs = set()

    def setup_tabs(self):
        """Sekmeleri başlat"""
        # İlk boş dosyayı aç
        self.new_file()

    def new_file(self):
        """Yeni boş dosya/sekme oluştur"""
        self.main_window.file_manager.new_file()

    def add_tab(self, path, name):
        """Sekme çubuğuna yeni bir sekme ekle"""
        if not hasattr(self.main_window, 'tab_bar'): return None
        
        theme = self.config.THEMES[self.config.theme]
        
        is_active = (path == self.active_tab)
        bg_color = theme['editor_bg'] if is_active else "transparent"
        text_color = theme['accent'] if is_active else theme['comment']
        font_weight = "bold" if is_active else "normal"
        
        # Sekme container
        tab_frame = ctk.CTkFrame(self.main_window.tab_bar, fg_color="transparent", corner_radius=0)
        tab_frame.pack(side="left", padx=1, pady=0, fill="y")

        # Sekme İçeriği
        btn_frame = ctk.CTkFrame(tab_frame, fg_color=bg_color, corner_radius=0)
        btn_frame.pack(side="top", fill="both", expand=True)

        # Alt Çizgi (Aktif sekme vurgusu)
        if is_active:
             bottom_line = ctk.CTkFrame(tab_frame, height=2, fg_color=theme['accent'], corner_radius=0)
             bottom_line.pack(side="bottom", fill="x")

        # Gelişmiş Dosya İkonları
        ext = os.path.splitext(path)[1].lower() if path else ""
        icons = {
            '.tr': '💎', '.py': '🐍', '.js': '📜', '.html': '🌐', 
            '.css': '🎨', '.json': '📋', '.md': '📝', '.txt': '📄',
        }
        icon = icons.get(ext, '📄')

        # Sekme Butonu
        btn = ctk.CTkButton(
            btn_frame,
            text=f"{icon} {name}",
            width=130,
            height=33,
            fg_color="transparent",
            hover_color=theme['hover'],
            text_color=text_color,
            font=("Segoe UI", 11, font_weight),
            corner_radius=0,
            command=lambda p=path: self.switch_to_tab(p)
        )
        btn.pack(side="left", padx=0, pady=0)

        # Kapat Butonu
        close_btn = ctk.CTkButton(
            btn_frame,
            text="×",
            width=25,
            height=33,
            fg_color="transparent",
            hover_color="#da3633",
            text_color=text_color,
            font=("Segoe UI", 14),
            corner_radius=0,
            command=lambda p=path: self.close_tab(p)
        )
        close_btn.pack(side="right", padx=0, pady=0)
        
        self.tab_close_btns[path] = close_btn
        if path in self.dirty_tabs:
            close_btn.configure(text="●", text_color=theme['accent'], hover_color=theme['border'])
            
        # Orta Tık (Scroll Click) Kapatma Desteği
        for w in [btn_frame, btn]:
            w.bind("<Button-2>", lambda e, p=path: self.close_tab(p))
            
        return tab_frame

    def refresh_tabs(self):
        """Sekme çubuğunu yeniden çiz"""
        if hasattr(self.main_window, 'tab_bar'):
             self.tab_close_btns.clear()
             for widget in self.main_window.tab_bar.winfo_children():
                widget.destroy()
        
             for path in self.editors.keys():
                name = os.path.basename(path) if "untitled" not in path else path.replace("untitled_", "Adsız-")
                self.add_tab(path, name)

    def switch_to_tab(self, path):
        """Belirli bir sekmeye geçiş yap"""
        if self.active_tab == path: return
        
        # Eski editörü gizle
        if self.active_tab in self.editors:
            self.editors[self.active_tab].pack_forget()
        
        # Yeni editörü göster
        self.active_tab = path
        if path in self.editors:
            self.editors[path].pack(fill="both", expand=True)
            self.editors[path].focus_set()
            self._bind_editor_events(path)
        
        self.refresh_tabs()
        self.main_window.update_title()
        self.main_window.update_outline()


    def close_tab(self, path):
        """Sekmeyi kapat"""
        if path not in self.editors: return
        
        # Emniyet Kilidi (Dayı Tavsiyesi)
        if path in self.dirty_tabs:
            from tkinter import messagebox
            filename = os.path.basename(path) if "untitled" not in path else path.replace("untitled_", "Adsız-")
            ans = messagebox.askyesnocancel("Kaydedilmemiş Değişiklik", f"'{filename}' dosyasında kaydedilmeyen değişiklikler var.\nKaydedip de mi kapatalım, yeğenim?")
            
            if ans is None:
                return # İptal (Kapatma işlemini durdur)
            elif ans is True:
                self.main_window.switch_to_tab(path)
                if not self.main_window.file_manager.save_file():
                    return # Kaydetme işlemi başarısız veya iptal edildiyse yine kapatma
        
        editor = self.editors.pop(path)
        editor.destroy()
        
        if path in self.dirty_tabs: self.dirty_tabs.remove(path)
        if path in self.tab_close_btns: del self.tab_close_btns[path]
        
        if self.active_tab == path:
            self.active_tab = list(self.editors.keys())[-1] if self.editors else None
            if self.active_tab:
                self.editors[self.active_tab].pack(fill="both", expand=True)
        
        if not self.editors:
            self.new_file()
        else:
            self.refresh_tabs()
            self.main_window.update_title()

    def _bind_editor_events(self, path):
        """Editör olaylarını ana pencereye bağla"""
        editor = self.editors[path]
        mw = self.main_window
        
        # Bu bağlamimarir gereksiz tekrar yapmamalı, ama şimdilik güvenli olması için bırakıyoruz
        # İdealde CodeEditor sınıfı kendi event'lerini fırlatmalı (Virtual Event)
        if hasattr(editor, '_textbox'):
            editor._textbox.bind('<KeyRelease>', lambda e: mw._on_editor_modified(e) if hasattr(mw, '_on_editor_modified') else None, add="+")
            editor._textbox.bind('<KeyRelease>', lambda e: mw.update_cursor_position(e) if hasattr(mw, 'update_cursor_position') else None, add="+")
            editor._textbox.bind('<KeyRelease>', lambda e: mw.update_outline(e) if hasattr(mw, 'update_outline') else None, add="+")
            editor._textbox.bind('<ButtonRelease-1>', lambda e: mw.update_cursor_position(e) if hasattr(mw, 'update_cursor_position') else None, add="+")

    def register_editor(self, path, editor_widget):
        """Yeni bir editör kaydet"""
        self.editors[path] = editor_widget
        self.active_tab = path

    def set_dirty(self, path, is_dirty):
        """Sekmenin kirli (değiştirilmiş ve kaydedilmemiş) durumunu ayarla"""
        theme = self.config.THEMES[self.config.theme]
        if is_dirty:
            self.dirty_tabs.add(path)
            if path in self.tab_close_btns:
                self.tab_close_btns[path].configure(text="●", text_color=theme['accent'], hover_color=theme['border'])
        else:
            if path in self.dirty_tabs:
                self.dirty_tabs.remove(path)
            if path in self.tab_close_btns:
                text_color = theme['accent'] if path == self.active_tab else theme['comment']
                self.tab_close_btns[path].configure(text="×", text_color=text_color, hover_color="#da3633")


