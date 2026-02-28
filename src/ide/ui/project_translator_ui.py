import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import os

class ProjectTranslatorUI(ctk.CTkToplevel):
    def __init__(self, main_window, config):
        super().__init__(main_window.root)
        self.main_window = main_window
        self.config = config
        
        self.title("🐍 Proje Çevirici (Python -> GümüşDil) 💎")
        self.geometry("650x500")
        self.resizable(False, False)
        
        # Ekranın ortasına al
        self.update_idletasks()
        try:
            x = self.main_window.root.winfo_x() + (self.main_window.root.winfo_width() // 2) - 325
            y = self.main_window.root.winfo_y() + (self.main_window.root.winfo_height() // 2) - 250
            self.geometry(f"+{x}+{y}")
        except:
            pass
            
        self.transient(self.main_window.root)
        self.grab_set()
        
        self.theme = config.THEMES[config.theme]
        self.configure(fg_color=self.theme['bg'])
        
        self.source_path = ctk.StringVar()
        self.target_path = ctk.StringVar()
        
        self.setup_ui()

    def setup_ui(self):
        # Header (Glassmorphism-vari gradientimsi başlık alanı)
        header_frame = ctk.CTkFrame(self, fg_color=self.theme['sidebar_bg'], corner_radius=0, height=80)
        header_frame.pack(fill="x", side="top")
        
        title_lbl = ctk.CTkLabel(header_frame, text="Yılanı Gümüşe Dönüştür", font=("Segoe UI", 24, "bold"), text_color=self.theme['accent'])
        title_lbl.pack(pady=(15, 0))
        
        subtitle_lbl = ctk.CTkLabel(header_frame, text="Mevcut Python projelerinizi saniyeler içinde GümüşDil'e geçirin.", font=("Segoe UI", 12), text_color=self.theme['comment'])
        subtitle_lbl.pack(pady=(0, 15))
        
        # Body
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # 1. Kaynak Dizin Seçimi
        src_lbl = ctk.CTkLabel(body_frame, text="1. Python Proje Klasörü (Kaynak):", font=("Segoe UI", 14, "bold"), text_color=self.theme['fg'])
        src_lbl.pack(anchor="w", pady=(0, 5))
        
        src_frame = ctk.CTkFrame(body_frame, fg_color="transparent")
        src_frame.pack(fill="x", pady=(0, 20))
        
        self.src_entry = ctk.CTkEntry(src_frame, textvariable=self.source_path, font=("Consolas", 12), fg_color=self.theme['editor_bg'], text_color=self.theme['fg'], border_color=self.theme['border'])
        self.src_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        src_btn = ctk.CTkButton(src_frame, text="📂 Seç", width=80, fg_color=self.theme['keyword'], hover_color=self.theme['hover'], text_color="#fff", font=("Segoe UI", 12, "bold"), command=self.select_source)
        src_btn.pack(side="right")
        
        # 2. Hedef Dizin Seçimi
        tgt_lbl = ctk.CTkLabel(body_frame, text="2. GümüşDil Dönüşüm Klasörü (Hedef):", font=("Segoe UI", 14, "bold"), text_color=self.theme['fg'])
        tgt_lbl.pack(anchor="w", pady=(0, 5))
        
        tgt_frame = ctk.CTkFrame(body_frame, fg_color="transparent")
        tgt_frame.pack(fill="x", pady=(0, 30))
        
        self.tgt_entry = ctk.CTkEntry(tgt_frame, textvariable=self.target_path, font=("Consolas", 12), fg_color=self.theme['editor_bg'], text_color=self.theme['fg'], border_color=self.theme['border'])
        self.tgt_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tgt_btn = ctk.CTkButton(tgt_frame, text="📁 Seç", width=80, fg_color=self.theme['accent'], hover_color=self.theme['hover'], text_color="#fff", font=("Segoe UI", 12, "bold"), command=self.select_target)
        tgt_btn.pack(side="right")
        
        # İlerleme Çubuğu ve Durum
        self.status_lbl = ctk.CTkLabel(body_frame, text="Dönüşüm için bekleniyor...", font=("Segoe UI", 12, "italic"), text_color=self.theme['comment'])
        self.status_lbl.pack(pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(body_frame, fg_color=self.theme['sidebar_bg'], progress_color=self.theme['function'], height=12)
        self.progress_bar.pack(fill="x", pady=(0, 20))
        self.progress_bar.set(0)
        
        # Dönüştür Butonu
        self.convert_btn = ctk.CTkButton(body_frame, text="🚀 ŞİMDİ DÖNÜŞTÜR", font=("Segoe UI", 16, "bold"), height=45, fg_color=self.theme['accent'], text_color="#fff", command=self.start_conversion)
        self.convert_btn.pack(fill="x")

    def select_source(self):
        folder = filedialog.askdirectory(title="Python Proje Klasörünü Seç")
        if folder:
            self.source_path.set(folder)
            if not self.target_path.get():
                # Hedefi varsayılan olarak kaynağın yanına _gumus_dil ekleyerek belirle
                parent_dir = os.path.dirname(folder)
                base_name = os.path.basename(folder)
                self.target_path.set(os.path.join(parent_dir, f"{base_name}_gumus_dil"))

    def select_target(self):
        folder = filedialog.askdirectory(title="GümüşDil Projesinin Kaydedileceği Klasörü Seç")
        if folder:
            self.target_path.set(folder)

    def start_conversion(self):
        source = self.source_path.get().strip()
        target = self.target_path.get().strip()
        
        if not source or not target:
            messagebox.showwarning("Eksik Bilgi", "Lütfen hem kaynak hem de hedef klasörleri seçin!", parent=self)
            return
            
        if not os.path.exists(source):
            messagebox.showerror("Hata", "Seçilen kaynak klasör mevcut değil!", parent=self)
            return

        self.convert_btn.configure(state="disabled", text="⏳ DÖNÜŞTÜRÜLÜYOR...")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        self.status_lbl.configure(text="Dosyalar analiz ediliyor ve çevriliyor...", text_color=self.theme['fg'])
        
        # Arayüzü dondurmamak için Thread içinde çalıştır
        threading.Thread(target=self._run_converter, args=(source, target), daemon=True).start()

    def _run_converter(self, source, target):
        import traceback
        count = 0
        errors = []
        try:
            from ..core.project_converter import GümüşProjectConverter
            converter = GümüşProjectConverter(self.main_window)
            count, errors = converter.convert_project(source, target)
        except Exception as e:
            errors.append(str(e))
            traceback.print_exc()
            
        # UI güncellemelerini ana thread'de yap
        self.after(0, lambda: self._on_conversion_complete(count, errors, target))

    def _on_conversion_complete(self, count, errors, target):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1.0)
        self.convert_btn.configure(state="normal", text="🚀 YENİDEN DÖNÜŞTÜR")
        
        if errors:
            self.status_lbl.configure(text=f"Tamamlandı ({len(errors)} hata). {count} dosya çevrildi.", text_color=self.theme['keyword'])
            msg = f"✅ Dönüşüm tamamlandı, ancak {len(errors)} hata alındı.\n📄 {count} dosya işlendi.\n\nBazı dosyalar çevrilememiş olabilir."
            messagebox.showwarning("Dönüşüm Uyarılarla Bitti", msg, parent=self)
        else:
            self.status_lbl.configure(text=f"Başarıyla tamamlandı! {count} dosya çevrildi.", text_color="#10b981") # Yeşil
            msg = f"✅ Harika! {count} Python dosyası başarıyla GümüşDil'e çevrildi."
            messagebox.showinfo("Dönüşüm Tamamlandı", msg, parent=self)
            
        # İşlem bitince paketleme sorabiliriz
        if count > 0:
            if messagebox.askyesno("Debian Paketi", "Bu projeyi Pardus için bir .deb kurulum paketine dönüştürmek ister misiniz?", parent=self):
                from ..core.project_converter import GümüşProjectConverter
                converter = GümüşProjectConverter(self.main_window)
                converter.package_converted_project(target)
                self.destroy()
