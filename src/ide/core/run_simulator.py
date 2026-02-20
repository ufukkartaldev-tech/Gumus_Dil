# -*- coding: utf-8 -*-
import sys
import os

# Windows'ta UTF-8 çıktı desteği (Emoji ve Türkçe karakterler için)
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Path Resolution (Production & Development Compatible)
# Geliştirme: src/ide/core dizinindeyiz
# Pardus Paketi: /usr/share/gumusdil/src/ide/core dizinindeyiz
current_dir = os.path.dirname(os.path.abspath(__file__))

# Proje kökünü bul (3 üst dizin: core -> ide -> src -> PROJECT_ROOT)
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))

# Pardus kurulumu kontrolü
pardus_install_path = "/usr/share/gumusdil"
if os.path.exists(pardus_install_path) and sys.platform != 'win32':
    project_root = pardus_install_path

sys.path.insert(0, project_root)

from src.ide.core.simulator import GumusSimulator

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Dosya belirtilmedi.")
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Hata: Dosya bulunamadi: {file_path}")
        sys.exit(1)
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
            
        # Simülatörü başlat
        print(f"🚀 GÜMÜŞ SİMÜLATÖR (Python Motoru) Devrede: {os.path.basename(file_path)}")
        sim = GumusSimulator()
        
        # Simülatör print fonksiyonu stdout'a yazar, IDE bunu yakalar.
        sim.run(code)
        
    except Exception as e:
        err_msg = str(e)
        if isinstance(e, UnicodeEncodeError) or "codec can't encode" in err_msg:
            err_msg = "Karakter kodlama hatası: Daktilo bu karakteri mühürleyemedi (UTF-8 sorunu). Lütfen UTF-8 desteklemeyen karakterleri temizle yeğenim."
        elif "no such file or directory" in err_msg.lower():
            err_msg = "Dosya bulunamadı: Belirttiğin adreste böyle bir evrak yok yeğenim."
            
        print(f"Kritik Simülatör Hatası: {err_msg}")
        sys.exit(1)

