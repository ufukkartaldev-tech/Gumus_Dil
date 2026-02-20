# -*- coding: utf-8 -*-
"""
GümüşDil IDE - Event Controller
MainWindow'dan event handling mantığını ayırır (Separation of Concerns)
"""

class EventController:
    """
    IDE event'lerini yöneten controller sınıfı.
    MainWindow'un kod kalabalığını azaltmak için oluşturuldu.
    """
    
    def __init__(self, main_window):
        self.main = main_window
        
    def on_file_open(self, path):
        """Dosya açma event'i"""
        self.main.open_file_from_path(path)
        
    def on_file_save(self):
        """Dosya kaydetme event'i"""
        self.main.save_file()
        
    def on_code_run(self):
        """Kod çalıştırma event'i"""
        self.main.run_code()
        
    def on_code_stop(self):
        """Kod durdurma event'i"""
        self.main.stop_code()
        
    def on_theme_change(self, theme_name):
        """Tema değiştirme event'i"""
        self.main.config.theme = theme_name
        self.main.config.save_settings()
        # UI'ı yenile (gelecekte implement edilecek)
        
    def on_tab_switch(self, path):
        """Sekme değiştirme event'i"""
        self.main.switch_to_tab(path)
        
    def on_search_request(self, query):
        """Arama event'i"""
        # Command Palette veya Find/Replace
        pass

# Kullanım (MainWindow içinde):
# self.event_controller = EventController(self)
# self.event_controller.on_file_open(path)

