import customtkinter as ctk
import tkinter as tk
import os
from .welcome_screen_v2 import WelcomeScreenV2 as WelcomeScreen
from .command_palette_v2 import CommandPaletteV2 as CommandPalette
from ..core.compiler import CompilerRunner

class DialogManager:
    """Açılır Pencereler ve Dialog Yönetimi"""
    
    def __init__(self, main_window, config):
        self.main_window = main_window
        self.config = config
        self.root = main_window.root

    def show_welcome_screen(self):
        """Karşılama ekranını göster (V2)"""
        WelcomeScreen(
            self.root, 
            self.config,
            on_open_file=self.main_window.open_file_dialog,
            on_new_file=self.main_window.new_file,
            on_open_path=self.main_window.open_file_from_path
        )

    def show_theme_selector(self):
        """Tema seçici dialog göster"""
        theme_window = ctk.CTkToplevel(self.root)
        theme_window.title("🎨 Tema Seçici")
        theme_window.geometry("500x600")
        theme_window.resizable(False, False)
        
        # Pozisyon
        theme_window.update_idletasks()
        try:
            x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 250
            y = self.root.winfo_y() + 100
            theme_window.geometry(f"+{x}+{y}")
        except: pass
        
        # Modal
        theme_window.transient(self.root)
        theme_window.grab_set()
        
        current_theme = self.config.THEMES[self.config.theme]
        
        # Ana frame
        main_frame = ctk.CTkFrame(theme_window, fg_color=current_theme['bg'])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlık ve Liste (Kodun geri kalanı aynı)
        title = ctk.CTkLabel(main_frame, text="🎨 Tema Seçin", font=("Segoe UI", 24, "bold"), text_color=current_theme['accent'])
        title.pack(pady=20)
        
        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color=current_theme['sidebar_bg'], corner_radius=12)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        for theme_key, theme_data in self.config.THEMES.items():
            self._create_theme_item(scroll_frame, theme_key, theme_data, theme_window)

    def _create_theme_item(self, parent, theme_key, theme_data, window):
        theme_frame = ctk.CTkFrame(
            parent,
            fg_color=theme_data['bg'],
            corner_radius=10,
            border_width=3 if theme_key == self.config.theme else 0,
            border_color=theme_data['accent']
        )
        theme_frame.pack(fill="x", padx=10, pady=8)
        
        # Tema bilgileri
        info_frame = ctk.CTkFrame(theme_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=12)
        
        name_label = ctk.CTkLabel(info_frame, text=theme_data.get('name', theme_key), font=("Segoe UI", 16, "bold"), text_color=theme_data['fg'])
        name_label.pack(anchor="w")
        
        # Renk paletleri
        colors_frame = ctk.CTkFrame(info_frame, fg_color="transparent", height=40)
        colors_frame.pack(fill="x", pady=(8, 0))
        
        for color_key in ['keyword', 'string', 'number', 'function', 'class', 'comment']:
            if color_key in theme_data:
                ctk.CTkFrame(colors_frame, fg_color=theme_data[color_key], width=50, height=30, corner_radius=6).pack(side="left", padx=3)
        
        # Seç butonu
        ctk.CTkButton(
            theme_frame,
            text="✓ Seç" if theme_key == self.config.theme else "Seç",
            command=lambda: self.apply_theme(theme_key, window),
            fg_color=theme_data['accent'],
            hover_color=theme_data['select_bg'],
            font=("Segoe UI", 12, "bold"),
            height=35
        ).pack(fill="x", padx=15, pady=(0, 12))

    def apply_theme(self, theme_key, window=None):
        """Temayı uygula - Tüm arayüzü özyinelemeli (recursive) olarak günceller"""
        try:
            self.config.theme = theme_key
            theme = self.config.THEMES[theme_key]
            
            # 1. Ana Pencere Arka Planı
            mw = self.main_window
            # Root ve ana containerlar
            if hasattr(mw, 'root'): mw.root.configure(fg_color=theme['bg'])
            if hasattr(mw, 'toolbar_frame'): mw.toolbar_frame.configure(fg_color=theme['sidebar_bg'])
            if hasattr(mw, 'status_bar'): mw.status_bar.configure(fg_color=theme['fg']) # Status bar kendi rengini yönetiyor ama
            
            # Recursive update fonksiyonu
            def update_widget_theme(widget):
                try:
                    # CustomTkinter Widget'ları
                    if isinstance(widget, ctk.CTkFrame):
                        # Bazı frame'ler özel renklere sahip olabilir, hepsini bozmamak lazım
                        # Ama 'transparent' olmayanları genel bg veya sidebar_bg yapabiliriz
                        # Şimdilik çok agresif değiştirmeyelim, manuel target daha iyi.
                        pass
                        
                    elif isinstance(widget, ctk.CTkLabel):
                        widget.configure(text_color=theme['fg'])
                        
                    elif isinstance(widget, ctk.CTkButton):
                        # Butonlar genellikle özel stillere sahip, dokunmayalım veya accent yapalım
                        # widget.configure(fg_color=theme['accent']) # Bu tehlikeli olabilir
                        pass
                        
                    elif isinstance(widget, ctk.CTkEntry):
                        widget.configure(
                            fg_color=theme['terminal_bg'], 
                            text_color=theme['terminal_fg'],
                            border_color=theme['border']
                        )
                    
                    elif isinstance(widget, ctk.CTkTextbox):
                        # Genel textboxlar (Editor hariç, onlar kendi apply_theme'ini çağırıyor)
                        widget.configure(
                            fg_color=theme['terminal_bg'],
                            text_color=theme['terminal_fg']
                        )
                        
                    # Standart TK Widget'ları
                    elif isinstance(widget, tk.Listbox):
                        widget.configure(
                            bg=theme['sidebar_bg'],
                            fg=theme['fg'],
                            selectbackground=theme['select_bg']
                        )
                        
                    elif isinstance(widget, tk.Canvas):
                        widget.configure(bg=theme['bg'])
                        
                    elif isinstance(widget, tk.Menu):
                        # Menü renkleri platforma göre değişir, Windows'da zor
                        pass

                except Exception as e:
                    pass
                
                # Alt widgetlar için recursive çağrı
                for child in widget.winfo_children():
                    update_widget_theme(child)

            # 2. Tüm ağacı gez (Bu çok agresif olabilir, dikkatli olunmalı)
            # update_widget_theme(mw.root) 
            # YUKARIDAKİ RECURSIVE YÖNTEM YERİNE DELEGASYON DAHA GÜVENLİ

            # Bileşen Bazlı Güncelleme (Delegasyon)
            
            # Editörler
            if hasattr(mw, 'editors'):
                for editor in mw.editors.values():
                    if hasattr(editor, 'apply_theme'): editor.apply_theme()
            
            # Terminal
            if hasattr(mw, 'terminal'): mw.terminal.apply_theme()
            
            # Sidebar
            if hasattr(mw, 'sidebar'): mw.sidebar.apply_theme()
            
            # Status Bar
            if hasattr(mw, 'status_bar'): mw.status_bar.update_theme_display()
            
            # PanedWindow ve Splitterlar
            if hasattr(mw, 'paned_window'): 
                mw.paned_window.configure(bg=theme['bg'])
                
            # Layout Manager üzerinden diğer paneller
            if hasattr(mw, 'layout_manager'):
                 # Activity Bar
                 if hasattr(mw.layout_manager, 'activity_bar'):
                     bar = mw.layout_manager.activity_bar
                     bar.configure(fg_color=theme['sidebar_bg'])
                     for btn in bar.winfo_children():
                         if isinstance(btn, ctk.CTkButton):
                             # Activity butonları
                             btn.configure(fg_color="transparent", text_color=theme['fg'], hover_color=theme['hover'])

                 # Panel Container
                 if hasattr(mw.layout_manager, 'panel_notebook'):
                      # Tabview renklerini güncellemek zor (CustomTkinter kısıtı)
                      pass

            mw.terminal.write_text(f">>> Tema değiştirildi: {theme.get('name', theme_key)} 🎨\n")
            
            if window: window.destroy()
            
        except Exception as e:
            print(f"Tema değiştirme hatası: {e}")
            if window: window.destroy()

    def show_command_palette(self, event=None):
        """Komut Paleti'ni Göster"""
        mw = self.main_window
        commands = [
            {"label": "▶ Çalıştır (Run Code)", "command": mw.run_code},
            {"label": "🛑 Durdur (Stop Code)", "command": mw.stop_code},
            {"label": "💾 Kaydet (Save)", "command": mw.save_file},
            {"label": "📂 Dosya Aç (Open File)", "command": mw.open_file_dialog},
            {"label": "📄 Yeni Dosya (New File)", "command": mw.new_file},
            {"label": "🎨 Tema Değiştir (Change Theme)", "command": self.show_theme_selector},
            {"label": "🔍 Bul/Değiştir", "command": lambda: mw.get_current_editor().show_find_dialog() if mw.get_current_editor() else None},
            {"label": "🧹 Terminali Temizle", "command": lambda: mw.terminal.clear()},
            {"label": "🏋️ Antrenman Modu", "command": lambda: mw.sidebar.switch_mode('training')},
            {"label": "🧠 Hafıza Görünümü", "command": lambda: mw.sidebar.switch_mode('memory')},
            {"label": "❌ Sekmeyi Kapat", "command": lambda: mw.close_tab(mw.active_tab) if mw.active_tab else None},
            {"label": "🗺️ GümüşHarita (Minimap)", "command": mw.toggle_minimap},
            {"label": "🧘 Zen Mode (GümüşOdak)", "command": mw.toggle_zen_mode},
            {"label": "💻 Terminal Göster/Gizle", "command": mw.toggle_terminal},
            {"label": "📊 AST Analizi", "command": mw.show_ast_viewer},
            {"label": "🐆 Pardus Paneli", "command": lambda: mw.sidebar.switch_mode('pardus')},
            {"label": "⚙️ Ayarlar", "command": self.show_theme_selector},
        ]
        CommandPalette(self.root, commands)

    def check_compiler_health(self):
        """Derleyici Sağlık Kontrolü"""
        from ..config import COMPILER_PATH, PROJECT_ROOT
        out = self.main_window.terminal
        
        try:
            out.write_text("\n🔍 Derleyici Sağlık Kontrolü...\n")
            
            # 1. Native Derleyici Kontrolü
            native_ok = False
            if COMPILER_PATH.exists():
                if CompilerRunner.is_compiler_viable():
                    out.write_text(f"✅ Gümüş Native Derleyici: AKTİF ({COMPILER_PATH.name})\n", "success")
                    native_ok = True
                else:
                    out.write_text(f"⚠️ Gümüş Native Derleyici: ÇALIŞMIYOR (DLL Eksik)\n", "warning")
                    out.write_text(f"   (Visual C++ Redistributable paketi gerekebilir)\n")
            else:
                out.write_text(f"⚠️ Gümüş Native Derleyici: BULUNAMADI\n", "warning")

            # 2. Simülatör Kontrolü (Fallback)
            simulator_path = PROJECT_ROOT / "src" / "ide" / "core" / "run_simulator.py"
            if simulator_path.exists():
                out.write_text(f"✅ Gümüş Simülatör (Python Motoru): HAZIR\n", "success")
                if not native_ok:
                    out.write_text(f"💡 Bilgi: Kodlarınız Simülatör kullanılarak çalıştırılacak.\n")
                    out.write_text(f"   Performans native derleyici kadar yüksek olmayabilir ama tüm özellikler çalışır.\n")
            else:
                out.write_text(f"❌ Gümüş Simülatör: BULUNAMADI\n", "error")
                
            if not native_ok and not simulator_path.exists():
                out.write_text("\n🚨 KRİTİK: Hiçbir çalıştırma motoru bulunamadı!\n", "error")
                
        except Exception as e:
            out.write_text(f"❌ Kontrol Hatası: {e}\n", "error")

