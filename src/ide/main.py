# -*- coding: utf-8 -*-
"""
GÜMÜŞDİL IDE - Giriş Noktası
Parçalanmış, modüler yapı.
"""
import sys
import os
import locale
import customtkinter as ctk

# Path Resolution (Production & Development Compatible)
# Geliştirme: src/ide/main.py
# Pardus: /usr/share/gumusdil/src/ide/main.py
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

# Pardus kurulumu kontrolü
if os.path.exists("/usr/share/gumusdil") and sys.platform != 'win32':
    project_root = "/usr/share/gumusdil"

sys.path.insert(0, project_root)

from src.ide.config import Config
from src.ide.ui.main_window import MainWindow

def main():
    # UTF-8 Desteği (Windows için)
    if sys.platform == 'win32':
        try:
            # Console encoding'i UTF-8 yap
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
            # Windows console code page'i UTF-8 yap
            os.system('chcp 65001 > nul')
        except:
            pass
    
    # Türkçe Locale Ayarı
    try:
        # Sadece karakter ve sıralama ayarlarını değiştir, sayısal ayarları (nokta/virgül) bozma
        # Tkinter/CustomTkinter Tcl tarafında nokta beklerken Python virgül verirse patlar.
        locale.setlocale(locale.LC_CTYPE, 'tr_TR.UTF-8')
        locale.setlocale(locale.LC_COLLATE, 'tr_TR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_CTYPE, 'Turkish_Turkey.1254')
            locale.setlocale(locale.LC_COLLATE, 'Turkish_Turkey.1254')
        except:
            pass

    
    # Komut satırı argümanı kontrolü
    mode = 'pro'
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    
    # Argüman yoksa mod seçimi sor (Basit)
    if len(sys.argv) == 1:
        # İleride buraya şık bir launcher eklenebilir
        pass 

    config = Config(mode)
    app = MainWindow(root, config)
    root.mainloop()

if __name__ == "__main__":
    main()

