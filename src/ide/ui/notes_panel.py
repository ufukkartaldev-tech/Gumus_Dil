import customtkinter as ctk
import os
import datetime

class NotesPanel(ctk.CTkFrame):
    def __init__(self, parent, config, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.config = config
        self.notes_file = os.path.join(os.getcwd(), "gumus_notlar.txt")
        
        # --- Başlık ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=5, pady=(5, 10))
        
        ctk.CTkLabel(
            self.header, 
            text="📒 GÜMÜŞ NOT", 
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")
        
        # Kaydet Butonu
        self.save_btn = ctk.CTkButton(
            self.header,
            text="💾 Kaydet",
            width=60,
            height=24,
            font=("Segoe UI", 11),
            fg_color=config.THEMES[config.theme]['accent'],
            hover_color=config.THEMES[config.theme]['hover'],
            command=self.save_notes
        )
        self.save_btn.pack(side="right")
        
        # --- Not Alanı ---
        self.textbox = ctk.CTkTextbox(
            self,
            font=("Consolas", 12),
            wrap="word",
            activate_scrollbars=True
        )
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Başlangıçta notları yükle
        self.load_notes()
        
        # Otomatik kaydetme için bind (her tuşa basıldığında değil, odaktan çıkınca)
        self.textbox.bind("<FocusOut>", self.auto_save)
        
    def load_notes(self):
        """Dosyadan notları yükle"""
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.textbox.delete("1.0", "end")
                    self.textbox.insert("1.0", content)
            except Exception as e:
                print(f"Not yükleme hatası: {e}")
        else:
            # İlk açılış mesajı
            welcome_msg = "# GümüşNot'a Hoş Geldin!\n\nBuraya kodlarınla ilgili notlar alabilirsin.\nBu notlar çalıştırılmaz, sadece senin içindir.\n\n- [ ] Yapılacaklar Listesi:\n  - [ ] Döngüleri tekrar et\n  - [ ] Fonksiyonları incele\n"
            self.textbox.insert("1.0", welcome_msg)
            
    def save_notes(self):
        """Notları dosyaya kaydet"""
        try:
            content = self.textbox.get("1.0", "end-1c")
            with open(self.notes_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Görsel geri bildirim (Buton rengi değişsin)
            original_text = self.save_btn.cget("text")
            self.save_btn.configure(text="✅ Kaydedildi")
            self.after(2000, lambda: self.save_btn.configure(text=original_text))
            
        except Exception as e:
            print(f"Not kaydetme hatası: {e}")

    def auto_save(self, event=None):
        """Otomatik kaydet (Sessizce)"""
        try:
            content = self.textbox.get("1.0", "end-1c")
            with open(self.notes_file, "w", encoding="utf-8") as f:
                f.write(content)
        except:
            pass
            
    def apply_theme(self):
        """Tema değişikliğini uygula"""
        theme = self.config.THEMES[self.config.theme]
        
        self.textbox.configure(
            fg_color=theme['editor_bg'],
            text_color=theme['fg'],
            border_color=theme['border'],
            scrollbar_button_color=theme['accent'],
            scrollbar_button_hover_color=theme['hover']
        )
        
        self.save_btn.configure(
            fg_color=theme['accent'],
            hover_color=theme['hover'],
            text_color="white" # Genelde buton yazısı beyaz kalır
        )

