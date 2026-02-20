# -*- coding: utf-8 -*-
import sys
from pathlib import Path

# Proje Yolları
IDE_DIR = Path(__file__).resolve().parent # src/ide

# KURULUM KONTROLÜ (Production vs Development)
# Pardus'ta paket kurulduğunda dosyalar /usr/share/gumusdil altındadır
PARDUS_INSTALL_PATH = Path("/usr/share/gumusdil")
IS_INSTALLED = (sys.platform != 'win32') and PARDUS_INSTALL_PATH.exists()

if IS_INSTALLED:
    PROJECT_ROOT = PARDUS_INSTALL_PATH
else:
    PROJECT_ROOT = IDE_DIR.parent.parent # Geliştirme modu: src/ide -> src -> programlama_dili

# PLATFORM KONTROLÜ (Windows / Pardus)
if sys.platform == 'win32':
    COMPILER_PATH = PROJECT_ROOT / "bin" / "gumus.exe"
else:
    COMPILER_PATH = PROJECT_ROOT / "bin" / "gumus" # Linux/Pardus için uzantısız

EXAMPLES_DIR = PROJECT_ROOT / "ornekler" # Paket içinde 'ornekler' olarak adlandırıldı
LIB_DIR = PROJECT_ROOT / "lib"
TEMP_DIR = PROJECT_ROOT / "temp"

# KULLANICI VERİ DİZİNİ (OS Standartlarına Uygun)
import os
if sys.platform == 'win32':
    # Windows: %LOCALAPPDATA%/GumusDil
    USER_DATA_DIR = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / "AppData" / "Local"))) / "GumusDil"
else:
    # Pardus/Linux: ~/.config/gumusdil (XDG Standartı)
    USER_DATA_DIR = Path.home() / ".config" / "gumusdil"

DATA_DIR = USER_DATA_DIR / "data"
LOG_DIR = USER_DATA_DIR / "logs"

# Dizinleri oluştur
for d in [USER_DATA_DIR, DATA_DIR, LOG_DIR]:
    if not d.exists():
        try: d.mkdir(parents=True, exist_ok=True)
        except: pass

class Config:
    """IDE Konfigürasyonu"""
    THEMES = {
        'dark': {
            'name': '🌙 Gece Mavisi',
            'bg': '#0d1117',
            'fg': '#c9d1d9',
            'editor_bg': '#0d1117',
            'sidebar_bg': '#010409',
            'select_bg': '#163356', # Better selection visibility
            'accent': '#58a6ff',
            'keyword': '#ff7b72',
            'string': '#a5d6ff',
            'number': '#79c0ff',
            'comment': '#8b949e',
            'function': '#d2a8ff',
            'class': '#ffa657',
            'terminal_bg': '#0d1117',
            'terminal_fg': '#c9d1d9',
            'border': '#30363d',
            'hover': '#21262d'
        },
        'monokai': {
            'name': '🎨 Monokai Pro',
            'bg': '#2d2a2e',
            'fg': '#fcfcfa',
            'editor_bg': '#2d2a2e',
            'sidebar_bg': '#221f22',
            'select_bg': '#403e41',
            'accent': '#ffd866',
            'keyword': '#ff6188',
            'string': '#ffd866',
            'number': '#ab9df2',
            'comment': '#727072',
            'function': '#a9dc76',
            'class': '#78dce8',
            'terminal_bg': '#2d2a2e',
            'terminal_fg': '#fcfcfa',
            'border': '#403e41',
            'hover': '#3e3b3f'
        },
        'dracula': {
            'name': '🧛 Dracula',
            'bg': '#282a36',
            'fg': '#f8f8f2',
            'editor_bg': '#282a36',
            'sidebar_bg': '#21222c',
            'select_bg': '#44475a',
            'accent': '#bd93f9',
            'keyword': '#ff79c6',
            'string': '#f1fa8c',
            'number': '#bd93f9',
            'comment': '#6272a4',
            'function': '#50fa7b',
            'class': '#8be9fd',
            'terminal_bg': '#282a36',
            'terminal_fg': '#f8f8f2',
            'border': '#44475a',
            'hover': '#343746'
        },
        'nord': {
            'name': '❄️ Nord',
            'bg': '#2e3440',
            'fg': '#d8dee9',
            'editor_bg': '#2e3440',
            'sidebar_bg': '#242933', # Darker sidebar
            'select_bg': '#434c5e',
            'accent': '#88c0d0',
            'keyword': '#81a1c1',
            'string': '#a3be8c',
            'number': '#b48ead',
            'comment': '#4c566a',
            'function': '#88c0d0',
            'class': '#8fbcbb',
            'terminal_bg': '#2e3440',
            'terminal_fg': '#d8dee9',
            'border': '#3b4252',
            'hover': '#3b4252'
        },
        'light': {
            'name': '☀️ Aydınlık',
            'bg': '#ffffff',
            'fg': '#24292f',
            'editor_bg': '#ffffff',
            'sidebar_bg': '#f6f8fa',
            'select_bg': '#dae6fc', # Softer blue
            'accent': '#0969da',
            'keyword': '#d73a49',
            'string': '#032f62',
            'number': '#005cc5',
            'comment': '#6a737d',
            'function': '#6f42c1',
            'class': '#e36209',
            'terminal_bg': '#f6f8fa',
            'terminal_fg': '#24292f',
            'border': '#d0d7de',
            'hover': '#f3f4f6'
        },
        'obsidian': {
            'name': '🌋 Obsidian',
            'bg': '#292b2e',
            'fg': '#e0e2e4',
            'editor_bg': '#292b2e',
            'sidebar_bg': '#212325',
            'select_bg': '#3f4b61',
            'accent': '#668799',
            'keyword': '#93c763',
            'string': '#ec7600',
            'number': '#ffcd22',
            'comment': '#66747b',
            'function': '#678cb1',
            'class': '#a082bd',
            'terminal_bg': '#292b2e',
            'terminal_fg': '#e0e2e4',
            'border': '#3e4246',
            'hover': '#2f3235'
        },
        'anadolu_leopari': {
            'name': '🐆 Anadolu Leoparı (Pardus)',
            'bg': '#0a0a0b',           # Derin Siyah (Asalet)
            'fg': '#e0e0e0',           # Gümüşü Gri
            'editor_bg': '#0f0f11',    # Gece Siyahı
            'sidebar_bg': '#070708',   # En Koyu Odak
            'select_bg': '#1b2a4a',    # Pardus Mavisi (Seçim)
            'accent': '#ffb000',       # Kehribar (Leopar Gözü)
            'keyword': '#38bdf8',      # Safir Mavi (Lisanın Gücü)
            'string': '#ffc107',       # Altın Sarısı
            'number': '#f59e0b',       # Bronz
            'comment': '#4b5563',      # Kaya Grisi
            'function': '#60a5fa',     # Gökyüzü Mavisi
            'class': '#fbbf24',        # Anadolu Güneşi
            'terminal_bg': '#000000', 
            'terminal_fg': '#38bdf8',
            'border': '#1e293b',
            'hover': '#1b294a'
        },
        'premium': {
            'name': '💎 Elmas (Premium)',
            'bg': '#0f172a',  # Slate 900
            'fg': '#e2e8f0',  # Slate 200
            'editor_bg': '#0f172a',
            'sidebar_bg': '#020617',  # Slate 950 (Darker for Contrast)
            'select_bg': '#1e293b',  # Slate 800
            'accent': '#38bdf8',  # Sky 400
            'keyword': '#c084fc',  # Violet 400 (Vibrant)
            'string': '#4ade80',  # Green 400
            'number': '#f472b6',  # Pink 400
            'comment': '#475569',  # Slate 600
            'function': '#60a5fa',  # Blue 400
            'class': '#fbbf24',  # Amber 400
            'terminal_bg': '#020617', 
            'terminal_fg': '#94a3b8', # Slate 400 (Subtle)
            'border': '#1e293b',
            'hover': '#1e293b'
        },
        'cyberpunk': {
            'name': '👾 Cyberpunk',
            'bg': '#0b001a', # Deep Purple/Black
            'fg': '#00ff9f', # Neon Green
            'editor_bg': '#0b001a',
            'sidebar_bg': '#1a0029',
            'select_bg': '#ff00aa', # Neon Pink Selection
            'accent': '#00f3ff', # Cyan
            'keyword': '#ff0055', # Neon Red/Pink
            'string': '#fee840', # Neon Yellow
            'number': '#00f3ff', # Cyan
            'comment': '#623d85', # Muted Purple
            'function': '#bd00ff', # Electric Purple
            'class': '#ff9100', # Neon Orange
            'terminal_bg': '#05000d',
            'terminal_fg': '#00ff9f',
            'border': '#bd00ff',
            'hover': '#290042'
        },
        'oceanic': {
            'name': '🌊 Okyanus',
            'bg': '#001e26', # Deep Teal
            'fg': '#d3ebe9',
            'editor_bg': '#001e26',
            'sidebar_bg': '#00141a',
            'select_bg': '#004052',
            'accent': '#00dcb4', # Bright Teal
            'keyword': '#ff5d7d', # Coral
            'string': '#00dcb4', # Cyan/Teal
            'number': '#c678dd', # Purple
            'comment': '#466870',
            'function': '#2196f3', # Blue
            'class': '#ffc107', # Amber
            'terminal_bg': '#00141a',
            'terminal_fg': '#d3ebe9',
            'border': '#003642',
            'hover': '#003642'
        },
        'zen_master': {
            'name': '🧘 Zen Ustası (Aydınlık)',
            'bg': '#e3e5e8', # Sıcak Açık Gri
            'fg': '#3b4252', 
            'editor_bg': '#fcfcfc', 
            'sidebar_bg': '#d8dee9', 
            'select_bg': '#d8dee9', 
            'accent': '#5e81ac', 
            'keyword': '#bf616a', 
            'string': '#a3be8c', 
            'number': '#d08770', 
            'comment': '#8fbcbb', 
            'function': '#88c0d0', 
            'class': '#ebcb8b', 
            'terminal_bg': '#2e3440', 
            'terminal_fg': '#eceff4',
            'border': '#c0c5ce', 
            'hover': '#eceff4'
        },
        'zen_dark': {
            'name': '🧘 Zen (Gece Modu)',
            'bg': '#232730', # Çok koyu gri/mavi (Yumuşak)
            'fg': '#d8dee9', # Kırık beyaz
            'editor_bg': '#1e2227', # Odak noktası daha koyu
            'sidebar_bg': '#191c21', # Sidebar geri planda
            'select_bg': '#2e3440', 
            'accent': '#8ca0ff', # Soluk Mavi
            'keyword': '#ff9bce', # Soluk Pembe
            'string': '#96e072', # Soluk Yeşil
            'number': '#ffb86c', # Soluk Turuncu
            'comment': '#5c6370', # Gri (Göz almaz)
            'function': '#61afef', # Mavi
            'class': '#e5c07b', # Altın
            'terminal_bg': '#1e2227', 
            'terminal_fg': '#abb2bf',
            'border': '#2c323c', 
            'hover': '#2c323c'
        },
        'pardus_dark': {
            'name': '🐆 Pardus Derin Gece',
            'bg': '#171a21',
            'fg': '#e2e8f0',
            'editor_bg': '#171a21',
            'sidebar_bg': '#101217',
            'select_bg': '#0088cc',
            'accent': '#00aaff',
            'keyword': '#ffd23f',
            'string': '#5fe0b1',
            'number': '#ff7063',
            'comment': '#64748b',
            'function': '#38bdf8',
            'class': '#fbbf24',
            'terminal_bg': '#0b0d11',
            'terminal_fg': '#e2e8f0',
            'border': '#1e293b',
            'hover': '#1e293b'
        },
        'pardus_etap': {
            'name': '🖥️ Pardus ETAP (Etkileşimli Tahta)',
            'bg': '#f8fafc',
            'fg': '#0f172a',
            'editor_bg': '#ffffff',
            'sidebar_bg': '#f1f5f9',
            'select_bg': '#38bdf8',
            'accent': '#0088cc',
            'keyword': '#e11d48',
            'string': '#16a34a',
            'number': '#ea580c',
            'comment': '#64748b',
            'function': '#2563eb',
            'class': '#9333ea',
            'terminal_bg': '#1e293b',
            'terminal_fg': '#f8fafc',
            'border': '#cbd5e1',
            'hover': '#e2e8f0'
        },
        'glass_premium': {
            'name': '✨ Kristal Gümüş (Premium)',
            'bg': '#0a0b10',           # Derin Uzay Siyahı
            'fg': '#ffffff',           # Saf Beyaz
            'editor_bg': '#0f111a',    # Modern Soft Dark
            'sidebar_bg': '#05060b',   # Ultra Dark Sidebar
            'select_bg': '#263345',    # Soft Steel Blue
            'accent': '#00f2fe',       # Cyan Glow
            'keyword': '#ff007c',      # Electric Pink
            'string': '#39ff14',       # Neon Green
            'number': '#7d12ff',       # Deep Purple
            'comment': '#666666',      # Muted Gray
            'function': '#448aff',     # Royal Blue
            'class': '#ffab40',        # Vivid Orange
            'terminal_bg': '#05060b', 
            'terminal_fg': '#00f2fe',
            'border': '#1a1d2d',
            'hover': '#141726'
        }
    }
    
    def __init__(self, mode='pro'):
        self.mode = mode
        
        # Varsayılan Tema Seçimi
        if sys.platform == 'win32':
            self.theme = 'zen_master'
        else:
            self.theme = 'pardus_dark' # Pardus/Linux için yerel tema
        
        # Mod ayarları
        self.show_sidebar = (mode == 'pro')
        self.show_ast = (mode == 'pro')
        self.simple_ui = (mode == 'ogrenci')
        self.show_welcome = True  # İlk açılışta hoş geldin ekranını göster (Pardus farkındalığı için)
        self.animations_enabled = True  # Animasyonlar
        self.recent_files = [] # Son kullanılan dosyalar
        
        # --- Dinamik Ayarlar ve Temimarir ---
        self.load_settings()
        self.load_custom_themes()

    def load_settings(self):
        """Ayarlar.json'dan kullanıcı tercihlerini yükle"""
        # İlk başta varsayılanları koy
        self.user_settings = {
            "ai_modu": "dayi",
            "kisayollar": {},
            "son_dosyalar": []
        }
        try:
            settings_path = DATA_DIR / "ayarlar.json"
            if settings_path.exists():
                with open(settings_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        self.user_settings.update(loaded)
            
            # Son dosyaları senkronize et
            self.recent_files = self.user_settings.get("son_dosyalar", [])
        except Exception as e:
            print(f"Ayar yükleme hatası: {e}")
            self.recent_files = []

    def save_settings(self):
        """Ayarları disk'e kaydet"""
        try:
            if not DATA_DIR.exists(): DATA_DIR.mkdir(parents=True)
            settings_path = DATA_DIR / "ayarlar.json"
            
            # Senkronizasyon
            self.user_settings["son_dosyalar"] = self.recent_files
            
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(self.user_settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ayar kaydetme hatası: {e}")

    def add_recent_file(self, path):
        """Son kullanılanlara ekle"""
        if not path: return
        path_str = str(path)
        
        if path_str in self.recent_files:
            self.recent_files.remove(path_str)
        
        self.recent_files.insert(0, path_str)
        
        # Limit (örn: 10 dosya)
        if len(self.recent_files) > 10:
            self.recent_files = self.recent_files[:10]
            
        self.save_settings()

    def load_custom_themes(self):
        """Temimarir.json'dan özel temimarirı yükle"""
        try:
            themes_path = DATA_DIR / "temimarir.json"
            if themes_path.exists():
                with open(themes_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    # Varsa aktif temayı güncelle
                    if "aktif_tema" in data:
                        # Eğer geçerli bir tema ise
                        if data["aktif_tema"] in data.get("temimarir", {}) or data["aktif_tema"] in self.THEMES:
                            self.theme = data["aktif_tema"]
                    
                    # Yeni temimarirı ekle
                    if "temimarir" in data:
                        for name, style in data["temimarir"].items():
                            # Eksik alanları varsayılanla doldur (Fallback)
                            base_theme = self.THEMES['premium'].copy() # En zenginden miras al
                            base_theme.update(style)
                            base_theme['name'] = f"🔧 {name.capitalize()} (Özel)"
                            Config.THEMES[name] = base_theme
                            
        except Exception as e:
            print(f"Tema yükleme hatası: {e}")

# Global Nesne
import json
# DATA_DIR yukarıda dinamik olarak tanımlandı

# ==================== SINGLETON PATTERN ====================
# Tüm IDE bileşenleri aynı Config nesnesini kullanır
# Bu sayede ayarlar merkezi bir yerden yönetilir
default_config = Config(mode='pro')

# Kullanım:
# from ..config import default_config
# theme = default_config.THEMES[default_config.theme]


