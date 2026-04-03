# -*- coding: utf-8 -*-
# Pardus Özel Tema - GümüşDil IDE
# Yerli ve Milli

PARDUS_THEME = {
    'name': '🇹🇷 Pardus (Yerli ve Milli)',
    'bg': '#1a1d23',           # Pardus koyu arka plan
    'fg': '#e8e8e8',           # Pardus açık metin
    'editor_bg': '#1e2127',    # Editör arka plan
    'sidebar_bg': '#14171c',   # Kenar çubuğu
    'select_bg': '#2c5aa0',    # Pardus mavi (seçim)
    'accent': '#4a90d9',       # Pardus ana mavi
    'keyword': '#ff6b6b',      # Anahtar kelimeler (kırmızı)
    'string': '#51cf66',       # String (yeşil - Türk bayrağı)
    'number': '#ffd43b',       # Sayılar (altın)
    'comment': '#6c757d',      # Yorumlar (gri)
    'function': '#4a90d9',     # Fonksiyonlar (Pardus mavi)
    'class': '#ff6b6b',        # Sınıflar (kırmızı - Türk bayrağı)
    'terminal_bg': '#14171c',  # Terminal arka plan
    'terminal_fg': '#e8e8e8',  # Terminal metin
    'border': '#2c5aa0',       # Kenarlıklar (Pardus mavi)
    'hover': '#252a33',        # Hover efekti
    
    # Pardus'a özel ekstra renkler
    'turkish_flag_red': '#e30a17',   # Türk bayrağı kırmızısı
    'turkish_flag_white': '#ffffff',  # Türk bayrağı beyazı
    'pardus_blue': '#2c5aa0',        # Pardus kurumsal mavi
    'success': '#51cf66',            # Başarı yeşili
    'warning': '#ffd43b',            # Uyarı sarısı
    'error': '#ff6b6b',              # Hata kırmızısı
}

# Pardus için özel syntax vurguları
PARDUS_SYNTAX_COLORS = {
    # Türkçe anahtar kelimeler özel renk
    'turkish_keywords': '#e30a17',  # Türk bayrağı kırmızısı
    'turkish_types': '#2c5aa0',     # Pardus mavisi
    'turkish_functions': '#51cf66',  # Yeşil
    
    # Özel vurgular
    'highlight_turkish': True,       # Türkçe kelimeleri vurgula
    'show_flag_colors': True,        # Bayrak renkleri kullan
}

# Pardus için özel font ayarları
PARDUS_FONTS = {
    'primary': 'DejaVu Sans Mono',   # Pardus varsayılan
    'fallback': 'Liberation Mono',   # Pardus alternatif
    'size': 12,
    'line_height': 1.5,
}

# Pardus için özel UI ayarları
PARDUS_UI_CONFIG = {
    'show_pardus_logo': True,
    'show_turkish_flag': True,
    'animation_speed': 'normal',  # Pardus performans optimizasyonu
    'use_native_dialogs': True,   # Pardus native dialog'ları
}

