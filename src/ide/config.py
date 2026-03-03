# -*- coding: utf-8 -*-
import sys
import os
import json
from pathlib import Path
from .ui.themes import THEMES

# Proje Yolları
IDE_DIR = Path(__file__).resolve().parent # src/ide

# KURULUM KONTROLÜ
PARDUS_INSTALL_PATH = Path("/usr/share/gumusdil")
IS_INSTALLED = (sys.platform != 'win32') and PARDUS_INSTALL_PATH.exists()

if IS_INSTALLED:
    PROJECT_ROOT = PARDUS_INSTALL_PATH
else:
    PROJECT_ROOT = IDE_DIR.parent.parent 

# PLATFORM KONTROLÜ
if sys.platform == 'win32':
    COMPILER_PATH = PROJECT_ROOT / "bin" / "gumus.exe"
else:
    COMPILER_PATH = PROJECT_ROOT / "bin" / "gumus"

EXAMPLES_DIR = PROJECT_ROOT / "ornekler"
LIB_DIR = PROJECT_ROOT / "lib"
TEMP_DIR = PROJECT_ROOT / "temp"

# KULLANICI VERİ DİZİNİ
if sys.platform == 'win32':
    USER_DATA_DIR = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / "AppData" / "Local"))) / "GumusDil"
else:
    USER_DATA_DIR = Path.home() / ".config" / "gumusdil"

DATA_DIR = USER_DATA_DIR / "data"
LOG_DIR = USER_DATA_DIR / "logs"

for d in [USER_DATA_DIR, DATA_DIR, LOG_DIR]:
    if not d.exists():
        try: d.mkdir(parents=True, exist_ok=True)
        except: pass

class Config:
    """IDE Konfigürasyonu"""
    THEMES = THEMES
    
    def __init__(self, mode='pro'):
        self.mode = mode
        if sys.platform == 'win32': self.theme = 'glass_premium'
        else: self.theme = 'pardus_dark'
        
        self.show_sidebar = True
        self.show_ast = False
        self.simple_ui = True
        self.show_welcome = True
        self.animations_enabled = True
        self.recent_files = []
        
        self.load_settings()
        self.load_custom_themes()

    def load_settings(self):
        self.user_settings = {"ai_modu": "dayi", "kisayollar": {}, "son_dosyalar": []}
        try:
            settings_path = DATA_DIR / "ayarlar.json"
            if settings_path.exists():
                with open(settings_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f); self.user_settings.update(loaded)
            self.recent_files = self.user_settings.get("son_dosyalar", [])
        except: self.recent_files = []

    def save_settings(self):
        try:
            if not DATA_DIR.exists(): DATA_DIR.mkdir(parents=True)
            self.user_settings["son_dosyalar"] = self.recent_files
            with open(DATA_DIR / "ayarlar.json", "w", encoding="utf-8") as f:
                json.dump(self.user_settings, f, indent=4, ensure_ascii=False)
        except: pass

    def add_recent_file(self, path):
        if not path: return
        path_str = str(path)
        if path_str in self.recent_files: self.recent_files.remove(path_str)
        self.recent_files.insert(0, path_str)
        if len(self.recent_files) > 10: self.recent_files = self.recent_files[:10]
        self.save_settings()

    def load_custom_themes(self):
        try:
            themes_path = DATA_DIR / "temimarir.json"
            if themes_path.exists():
                with open(themes_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "aktif_tema" in data:
                        if data["aktif_tema"] in data.get("temimarir", {}) or data["aktif_tema"] in self.THEMES:
                            self.theme = data["aktif_tema"]
                    if "temimarir" in data:
                        for name, style in data["temimarir"].items():
                            base_theme = self.THEMES['premium'].copy()
                            base_theme.update(style)
                            base_theme['name'] = f"🔧 {name.capitalize()} (Özel)"
                            Config.THEMES[name] = base_theme
        except: pass

default_config = Config(mode='ogrenci')
