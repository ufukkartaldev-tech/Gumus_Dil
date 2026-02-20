import os
import sys
import importlib.util
import inspect

class PluginManager:
    def __init__(self, ide_interface):
        self.ide = ide_interface
        self.plugins = []
        
        # Kancalar (Hooks) - Tetik mekanizmimarirı
        self.hooks = {
            "on_code_change": [], # Kod her değiştiğinde
            "on_error": [],       # Hata tespit edildiğinde
            "on_ui_setup": [],    # UI ilk kurulurken (Menü ekleme vb.)
            "on_save": [],        # Kaydetme anında
            "on_startup": [],     # IDE tamamen açıldığında
            "on_editor_init": []  # Yeni bir editör açıldığında
        }
        
    def load_plugins(self, plugin_dir="plugins"):
        """Belirtilen klasördeki .py dosyalarını eklenti olarak yükler"""
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
            
        print(f"[Gumus-Modul] Eklentiler taraniyor: {plugin_dir}")
        # Import yolunu ekle ki eklentiler kendi içlerindeki modülleri bulabilsin (gerekirse)
        if os.getcwd() not in sys.path:
            sys.path.append(os.getcwd())

        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                self._load_single_plugin(os.path.join(plugin_dir, filename))
                
    def _load_single_plugin(self, file_path):
        try:
            name = os.path.basename(file_path).replace(".py", "")
            spec = importlib.util.spec_from_file_location(name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # gumus_kayit(manager) fonksiyonunu ara
            # Eklenti kendini bu fonksiyonla sisteme tanıtır.
            if hasattr(module, "gumus_kayit"):
                print(f"[Gumus-Modul] Yukleniyor: {name}")
                # Eklentiye 'self' (PluginManager) gönderilir, böylece register_hook yapabilir.
                # Ayrıca ide_interface erişimi de sağlar (self.ide üzerinden).
                module.gumus_kayit(self)
                
                self.plugins.append({
                    "name": name,
                    "module": module
                })
            else:
                print(f"[UYARI] [Gumus-Modul] {name} gecerli bir eklenti degil ('gumus_kayit' fonksiyonu eksik).")
                
        except Exception as e:
            print(f"[HATA] [Gumus-Modul] Eklenti yukleme hatasi ({file_path}): {e}")

    def register_hook(self, hook_name, callback):
        """Eklentilerin olaylara kanca atmasını sağlar"""
        if hook_name in self.hooks:
            self.hooks[hook_name].append(callback)
            # print(f"[Gumus-Modul] Kanca kaydedildi: {hook_name}")
        else:
            print(f"[UYARI] [Gumus-Modul] Gecersiz kanca: {hook_name}")

    def trigger_hook(self, hook_name, *args, **kwargs):
        """IDE'nin olayları tetiklemesi için"""
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    # Callback'leri güvenli şekilde çağır
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"[HATA] [Gumus-Modul] Hook hatasi ({hook_name}): {e}")


