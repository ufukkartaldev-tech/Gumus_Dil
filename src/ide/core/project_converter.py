# -*- coding: utf-8 -*-
import os
from pathlib import Path
from .python_to_gumus import PythonToGumusTranspiler

class GümüşProjectConverter:
    """Python projesini toplu halde GümüşDil'e çevirir."""

    def __init__(self, main_window=None):
        self.main_window = main_window
        self.transpiler = PythonToGumusTranspiler()

    def convert_project(self, source_dir, target_dir):
        """Tüm klasörü tarar ve .py dosyalarını .tr'ye çevirir."""
        source_path = Path(source_dir)
        target_path = Path(target_dir)

        if not target_path.exists():
            target_path.mkdir(parents=True)

        files_converted = 0
        errors = []

        for root, dirs, files in os.walk(source_path):
            # Hedef klasör yapısını oluştur
            relative_path = Path(root).relative_to(source_path)
            dest_folder = target_path / relative_path
            
            if not dest_folder.exists():
                dest_folder.mkdir(parents=True)

            for file in files:
                if file.endswith(".py"):
                    src_file = Path(root) / file
                    dest_file = dest_folder / (src_file.stem + ".tr")
                    
                    try:
                        with open(src_file, 'r', encoding='utf-8') as f:
                            py_code = f.read()
                        
                        gumus_code = self.transpiler.transpile(py_code)
                        
                        # Dosya başlığı ekle
                        header = f"// 💎 Python'dan GümüşDil'e Otomatik Çevrildi\n"
                        header += f"// 📄 Kaynak: {file}\n\n"
                        
                        with open(dest_file, 'w', encoding='utf-8') as f:
                            f.write(header + gumus_code)
                        
                        files_converted += 1
                    except Exception as e:
                        errors.append(f"{file}: {str(e)}")

        return files_converted, errors

    def package_converted_project(self, converted_dir):
        """Çevrilmiş projeyi Pardus paketi haline getirir."""
        if not self.main_window:
            return False, "Main Window referansı yok."
        
        try:
            from .pardus_packager import PardusPackageBuilder
            packager = PardusPackageBuilder(self.main_window.root, self.main_window.config)
            packager.show_package_builder_dialog(converted_dir)
            return True, "Paketleme diyaloğu açıldı."
        except Exception as e:
            return False, str(e)

