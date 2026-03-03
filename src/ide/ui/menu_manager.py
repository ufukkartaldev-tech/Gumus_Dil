import tkinter as tk
import functools

class MenuManager:
    """Menü Yönetimi Sınıfı"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.root = main_window.root
        self.menubar = None
        
    def create_menu(self):
        """Ana menüyü oluştur"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        self._create_file_menu()
        self._create_edit_menu()
        self._create_view_menu()
        self._create_run_menu()
        self._create_tools_menu()
        self._create_help_menu()
        
    def _create_file_menu(self):
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Dosya", menu=file_menu)
        
        file_menu.add_command(label="Yeni", accelerator="Ctrl+N", command=self.main_window.new_file)
        file_menu.add_command(label="Aç...", accelerator="Ctrl+O", command=self.main_window.open_file_dialog)
        file_menu.add_command(label="Klasör Aç...", accelerator="Ctrl+Shift+O", command=self.main_window.open_folder_dialog)
        file_menu.add_command(label="Kaydet", accelerator="Ctrl+S", command=self.main_window.save_file)
        file_menu.add_command(label="Farklı Kaydet...", accelerator="Ctrl+Shift+S", command=self.main_window.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", accelerator="Alt+F4", command=self.root.quit)

    def _create_edit_menu(self):
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Düzenle", menu=edit_menu)
        
        edit_menu.add_command(label="Geri Al", accelerator="Ctrl+Z", command=lambda: self.main_window.get_active_editor()._textbox.edit_undo())
        edit_menu.add_command(label="İleri Al", accelerator="Ctrl+Y", command=lambda: self.main_window.get_active_editor()._textbox.edit_redo())
        edit_menu.add_separator()
        edit_menu.add_command(label="Bul...", accelerator="Ctrl+F", command=lambda: self.main_window.get_active_editor().show_find_dialog())
        edit_menu.add_command(label="Değiştir...", accelerator="Ctrl+H", command=lambda: self.main_window.get_active_editor().show_replace_dialog())
        
    def _create_view_menu(self):
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Görünüm", menu=view_menu)
        
        view_menu.add_command(label="📊 AST Görselleştirici", command=self.main_window.show_ast_viewer)
        view_menu.add_command(label="🎨 Tema Değiştir", command=self.main_window.show_theme_selector)
        view_menu.add_separator()
        view_menu.add_command(label="🗺️ GümüşHarita (Minimap)", command=self.main_window.toggle_minimap)
        view_menu.add_command(label="🧘 GümüşOdak (Zen Mode)", accelerator="Ctrl+.", command=self.main_window.toggle_zen_mode)
        view_menu.add_command(label="💻 Terminal", command=self.main_window.toggle_terminal)
    
    def _create_run_menu(self):
        run_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Çalıştır", menu=run_menu)
        
        run_menu.add_command(label="▶ Çalıştır", accelerator="F5", command=self.main_window.run_code)
        run_menu.add_command(label="🐞 Hata Ayıkla", accelerator="F9", command=self.main_window.debug_code)
        run_menu.add_separator()
        run_menu.add_command(label="🛑 Durdur", accelerator="Shift+F5", command=self.main_window.stop_code)

    def _create_tools_menu(self):
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Araçlar", menu=tools_menu)
        
        tools_menu.add_command(label="📦 Paket Yöneticisi (Güm-Pak)", command=self.main_window.show_package_manager)
        tools_menu.add_command(label="🐍 Python Projesini Çevir", command=self.main_window.show_project_translator)
        tools_menu.add_command(label="🏭 Fabrika Simülasyonu", command=self.main_window.show_factory_sim)
        try:
            tools_menu.add_command(label="🔌 Voxel Engine (Test)", command=self.main_window.test_voxel_engine)
        except: pass

    def _create_help_menu(self):
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Yardım", menu=help_menu)
        
        help_menu.add_command(label="GümüşDil Dokümantasyonu", command=self.main_window.show_docs)
        help_menu.add_command(label="Klavye Kısayolları", command=self.main_window.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="Hakkında", command=self.main_window.show_about)

