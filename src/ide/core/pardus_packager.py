# -*- coding: utf-8 -*-
# GümüşDil - Pardus Paket Oluşturucu
# TEKNOFEST 2026 - Tek Tıkla .deb Paketi

import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading

class PardusPackageBuilder:
    """
    GümüşDil projelerini Pardus .deb paketine dönüştürür.
    Öğrenciler kendi projelerini paketleyip paylaşabilir!
    """
    
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.build_in_progress = False
        
    def show_package_builder_dialog(self, project_path=None):
        """Paket oluşturucu dialog'unu göster"""
        
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("📦 Pardus Paketi Oluştur - TEKNOFEST 2026")
        dialog.geometry("700x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Ana frame
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = ctk.CTkLabel(
            main_frame,
            text="🇹🇷 Pardus .deb Paketi Oluştur",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Projenizi Pardus kullanıcılarıyla paylaşın!",
            font=("Arial", 12),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Form alanları
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Paket adı
        ctk.CTkLabel(form_frame, text="Paket Adı:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        package_name_entry = ctk.CTkEntry(form_frame, placeholder_text="ornek: benim-oyunum")
        package_name_entry.pack(fill="x", padx=5, pady=(0, 10))
        
        # Versiyon
        ctk.CTkLabel(form_frame, text="Versiyon:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        version_entry = ctk.CTkEntry(form_frame, placeholder_text="1.0.0")
        version_entry.insert(0, "1.0.0")
        version_entry.pack(fill="x", padx=5, pady=(0, 10))
        
        # Açıklama
        ctk.CTkLabel(form_frame, text="Açıklama:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        description_entry = ctk.CTkEntry(form_frame, placeholder_text="Projenizin kısa açıklaması")
        description_entry.pack(fill="x", padx=5, pady=(0, 10))
        
        # Geliştirici
        ctk.CTkLabel(form_frame, text="Geliştirici:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        developer_entry = ctk.CTkEntry(form_frame, placeholder_text="Adınız Soyadınız")
        developer_entry.pack(fill="x", padx=5, pady=(0, 10))
        
        # E-posta
        ctk.CTkLabel(form_frame, text="E-posta:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        email_entry = ctk.CTkEntry(form_frame, placeholder_text="email@example.com")
        email_entry.pack(fill="x", padx=5, pady=(0, 10))
        
        # Proje dizini seçimi
        ctk.CTkLabel(form_frame, text="Proje Dizini:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        dir_frame = ctk.CTkFrame(form_frame)
        dir_frame.pack(fill="x", padx=5, pady=(0, 10))
        
        project_dir_var = ctk.StringVar(value=project_path or "Seçilmedi")
        dir_label = ctk.CTkLabel(dir_frame, textvariable=project_dir_var, anchor="w")
        dir_label.pack(side="left", fill="x", expand=True, padx=5)
        
        def select_directory():
            dir_path = filedialog.askdirectory(title="Proje Dizinini Seçin")
            if dir_path:
                project_dir_var.set(dir_path)
        
        dir_button = ctk.CTkButton(dir_frame, text="Seç", width=80, command=select_directory)
        dir_button.pack(side="right", padx=5)
        
        # İlerleme çubuğu
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", padx=10, pady=10)
        
        progress_label = ctk.CTkLabel(progress_frame, text="Hazır", font=("Arial", 10))
        progress_label.pack(pady=5)
        
        progress_bar = ctk.CTkProgressBar(progress_frame)
        progress_bar.pack(fill="x", padx=10, pady=5)
        progress_bar.set(0)
        
        # Butonlar
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        def build_package():
            """Paketi oluştur"""
            if self.build_in_progress:
                messagebox.showwarning("Uyarı", "Bir paket zaten oluşturuluyor!")
                return
            
            # Validasyon
            pkg_name = package_name_entry.get().strip()
            version = version_entry.get().strip()
            description = description_entry.get().strip()
            developer = developer_entry.get().strip()
            email = email_entry.get().strip()
            proj_dir = project_dir_var.get()
            
            if not pkg_name:
                messagebox.showerror("Hata", "Paket adı gerekli!")
                return
            if not version:
                messagebox.showerror("Hata", "Versiyon gerekli!")
                return
            if proj_dir == "Seçilmedi" or not os.path.exists(proj_dir):
                messagebox.showerror("Hata", "Geçerli bir proje dizini seçin!")
                return
            
            # Thread'de oluştur
            self.build_in_progress = True
            build_button.configure(state="disabled", text="⏳ Oluşturuluyor...")
            
            def build_thread():
                try:
                    progress_label.configure(text="📦 Paket yapısı oluşturuluyor...")
                    progress_bar.set(0.2)
                    
                    result = self._create_deb_package(
                        pkg_name, version, description, developer, email, proj_dir,
                        progress_label, progress_bar
                    )
                    
                    if result:
                        progress_bar.set(1.0)
                        progress_label.configure(text="✅ Paket başarıyla oluşturuldu!")
                        messagebox.showinfo(
                            "Başarılı!",
                            f"Pardus paketi oluşturuldu:\n{result}\n\n"
                            f"Pardus'ta kurmak için:\nsudo dpkg -i {os.path.basename(result)}"
                        )
                    else:
                        progress_label.configure(text="❌ Paket oluşturulamadı!")
                        messagebox.showerror("Hata", "Paket oluşturulurken hata oluştu!")
                    
                except Exception as e:
                    progress_label.configure(text=f"❌ Hata: {str(e)}")
                    messagebox.showerror("Hata", f"Paket oluşturulurken hata:\n{str(e)}")
                
                finally:
                    self.build_in_progress = False
                    build_button.configure(state="normal", text="📦 Paketi Oluştur")
            
            thread = threading.Thread(target=build_thread, daemon=True)
            thread.start()
        
        build_button = ctk.CTkButton(
            button_frame,
            text="📦 Paketi Oluştur",
            command=build_package,
            height=40,
            font=("Arial", 14, "bold"),
            fg_color="#2c5aa0",  # Pardus mavisi
            hover_color="#1a3d6b"
        )
        build_button.pack(side="left", fill="x", expand=True, padx=5)
        
        close_button = ctk.CTkButton(
            button_frame,
            text="Kapat",
            command=dialog.destroy,
            height=40,
            fg_color="gray"
        )
        close_button.pack(side="right", padx=5)
    
    def _create_deb_package(self, pkg_name, version, description, developer, email, 
                           project_dir, progress_label, progress_bar):
        """Gerçek .deb paketi oluştur"""
        
        try:
            # Geçici build dizini
            build_dir = Path(f"/tmp/gumusdil_build_{pkg_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            build_dir.mkdir(parents=True, exist_ok=True)
            
            package_dir = build_dir / f"{pkg_name}_{version}_all"
            package_dir.mkdir(exist_ok=True)
            
            # DEBIAN dizini
            debian_dir = package_dir / "DEBIAN"
            debian_dir.mkdir(exist_ok=True)
            
            progress_label.configure(text="📝 Control dosyası oluşturuluyor...")
            progress_bar.set(0.3)
            
            # Control dosyası
            control_content = f"""Package: {pkg_name}
Version: {version}
Section: education
Priority: optional
Architecture: all
Depends: gumusdil (>= 1.0.0)
Maintainer: {developer} <{email}>
Description: {description}
 GümüşDil ile geliştirilmiş Pardus uygulaması.
 .
 TEKNOFEST 2026 - Yerli ve Milli Yazılım
Homepage: https://gumusdil.org
"""
            
            with open(debian_dir / "control", "w", encoding="utf-8") as f:
                f.write(control_content)
            
            progress_label.configure(text="📂 Proje dosyaları kopyalanıyor...")
            progress_bar.set(0.5)
            
            # Uygulama dizini
            app_dir = package_dir / "usr" / "share" / pkg_name
            app_dir.mkdir(parents=True, exist_ok=True)
            
            # Proje dosyalarını kopyala
            for item in os.listdir(project_dir):
                src = os.path.join(project_dir, item)
                dst = app_dir / item
                
                if os.path.isfile(src) and item.endswith('.tr'):
                    shutil.copy2(src, dst)
                elif os.path.isdir(src) and item not in ['.git', '__pycache__', 'node_modules']:
                    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
            
            progress_label.configure(text="🚀 Başlatıcı script oluşturuluyor...")
            progress_bar.set(0.7)
            
            # Başlatıcı script
            bin_dir = package_dir / "usr" / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            
            launcher_script = f"""#!/bin/bash
# {pkg_name} - GümüşDil Uygulaması
cd /usr/share/{pkg_name}
gumusdil main.tr "$@"
"""
            
            launcher_path = bin_dir / pkg_name
            with open(launcher_path, "w", encoding="utf-8") as f:
                f.write(launcher_script)
            
            os.chmod(launcher_path, 0o755)
            
            progress_label.configure(text="🖥️ Masaüstü dosyası oluşturuluyor...")
            progress_bar.set(0.8)
            
            # Desktop dosyası
            desktop_dir = package_dir / "usr" / "share" / "applications"
            desktop_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={pkg_name.replace('-', ' ').title()}
Comment={description}
Exec={pkg_name}
Icon=applications-games
Terminal=false
Categories=Game;Education;
Keywords=gumusdil;pardus;turkish;
X-Pardus-App=true
"""
            
            with open(desktop_dir / f"{pkg_name}.desktop", "w", encoding="utf-8") as f:
                f.write(desktop_content)
            
            progress_label.configure(text="🔨 .deb paketi derleniyor...")
            progress_bar.set(0.9)
            
            # dpkg-deb ile paketi oluştur
            output_deb = build_dir / f"{pkg_name}_{version}_all.deb"
            
            result = subprocess.run(
                ["dpkg-deb", "--build", str(package_dir), str(output_deb)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and output_deb.exists():
                # Paketi kullanıcının masaüstüne kopyala
                desktop_path = Path.home() / "Desktop" / output_deb.name
                shutil.copy2(output_deb, desktop_path)
                
                # Temizlik
                shutil.rmtree(build_dir, ignore_errors=True)
                
                return str(desktop_path)
            else:
                raise Exception(f"dpkg-deb hatası: {result.stderr}")
        
        except Exception as e:
            raise Exception(f"Paket oluşturma hatası: {str(e)}")

