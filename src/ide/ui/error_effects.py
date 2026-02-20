"""
🎨 GÜMÜŞ ZEKA - Error Visual Effects
Hata görselleştirme ve animasyon sistemi
"""

import tkinter as tk
import customtkinter as ctk
from typing import Optional, Callable
import time


class ErrorHighlightWidget(ctk.CTkFrame):
    """
    Hata vurgulama widget'ı
    
    Özellikler:
    - Kırmızı titreyen çizgi
    - Gümüş dumanı efekti
    - Fade-in/out animasyonları
    """
    
    def __init__(self, parent, config, **kwargs):
        super().__init__(parent, **kwargs)
        self.config = config
        self.theme = config.THEMES[config.theme]
        
        # Animation state
        self.is_animating = False
        self.shake_offset = 0
        self.alpha = 0.0
        
        # Configure
        self.configure(
            fg_color="transparent",
            corner_radius=0
        )
        
    def highlight_error_line(self, line_number: int, editor_widget):
        """
        Hatalı satırı vurgula
        
        Args:
            line_number: Satır numarası
            editor_widget: CodeEditor widget'ı
        """
        # Kırmızı vurgu ekle
        start_index = f"{line_number}.0"
        end_index = f"{line_number}.end+1c"
        
        editor_widget._textbox.tag_remove("error_highlight", "1.0", tk.END)
        editor_widget._textbox.tag_add("error_highlight", start_index, end_index)
        editor_widget._textbox.tag_configure(
            "error_highlight",
            background="#ff1744",
            foreground="#ffffff",
            underline=True
        )
        
        # Satıra scroll
        editor_widget._textbox.see(start_index)
        
        # Titreşim animasyonu başlat
        self._start_shake_animation(editor_widget, line_number)
        
    def _start_shake_animation(self, editor_widget, line_number: int, duration_ms: int = 1000):
        """Titreşim animasyonu"""
        if self.is_animating:
            return
            
        self.is_animating = True
        start_time = time.time()
        
        def shake_step():
            if not self.is_animating:
                return
                
            elapsed = (time.time() - start_time) * 1000
            if elapsed >= duration_ms:
                self.is_animating = False
                return
                
            # Sinüs dalgası ile titreşim
            import math
            frequency = 10  # Hz
            amplitude = 2   # pixels
            offset = int(amplitude * math.sin(2 * math.pi * frequency * elapsed / 1000))
            
            # Tag'i hafifçe kaydır (görsel efekt)
            # Not: Tkinter Text widget'ında pixel kaydırma zor, 
            # bunun yerine background color'u değiştirerek efekt yaratıyoruz
            intensity = int(255 * (1 - elapsed / duration_ms))
            color = f"#{intensity:02x}17{intensity//4:02x}"
            
            editor_widget._textbox.tag_configure(
                "error_highlight",
                background=color
            )
            
            # Sonraki frame
            self.after(16, shake_step)  # ~60 FPS
            
        shake_step()
        
    def clear_highlight(self, editor_widget):
        """Vurguyu temizle"""
        self.is_animating = False
        editor_widget._textbox.tag_remove("error_highlight", "1.0", tk.END)


class SilverSmokeEffect(ctk.CTkFrame):
    """
    Gümüş dumanı efekti
    
    AI panel açılırken gösterilir
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(
            fg_color="#C0C0C0",  # Gümüş rengi
            corner_radius=10
        )
        
        # Başlangıçta görünmez
        self.place_forget()
        
    def show_smoke(self, duration_ms: int = 500, callback: Optional[Callable] = None):
        """
        Duman efektini göster
        
        Args:
            duration_ms: Animasyon süresi
            callback: Animasyon bitince çağrılacak fonksiyon
        """
        # Ekranın ortasına yerleştir
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        width = 300
        height = 200
        x = (parent_width - width) // 2
        y = (parent_height - height) // 2
        
        self.place(x=x, y=y, width=width, height=height)
        
        # Fade-in animasyonu
        self._animate_fade_in(duration_ms, callback)
        
    def _animate_fade_in(self, duration_ms: int, callback: Optional[Callable]):
        """Fade-in animasyonu"""
        steps = 20
        step_duration = duration_ms // steps
        
        def fade_step(step: int):
            if step >= steps:
                # Animasyon bitti
                self.place_forget()
                if callback:
                    callback()
                return
                
            # Alpha değerini artır
            alpha = step / steps
            
            # Renk yoğunluğunu azalt (fade effect)
            gray_value = int(192 + (255 - 192) * (1 - alpha))
            color = f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"
            self.configure(fg_color=color)
            
            # Boyutu büyüt (genişleme efekti)
            scale = 1 + 0.5 * alpha
            new_width = int(300 * scale)
            new_height = int(200 * scale)
            
            parent_width = self.master.winfo_width()
            parent_height = self.master.winfo_height()
            x = (parent_width - new_width) // 2
            y = (parent_height - new_height) // 2
            
            self.place(x=x, y=y, width=new_width, height=new_height)
            
            # Sonraki step
            self.after(step_duration, lambda: fade_step(step + 1))
            
        fade_step(0)


class ErrorAlertBanner(ctk.CTkFrame):
    """
    Hata uyarı banner'ı
    
    Ekranın üstünde kırmızı bir banner gösterir
    """
    
    def __init__(self, parent, config, **kwargs):
        super().__init__(parent, **kwargs)
        self.config = config
        
        self.configure(
            fg_color="#ff1744",
            corner_radius=0,
            height=40
        )
        
        # İkon
        self.icon_label = ctk.CTkLabel(
            self,
            text="🚨",
            font=("Segoe UI Emoji", 24),
            text_color="#ffffff"
        )
        self.icon_label.pack(side="left", padx=10)
        
        # Mesaj
        self.message_label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 14, "bold"),
            text_color="#ffffff"
        )
        self.message_label.pack(side="left", padx=5, fill="x", expand=True)
        
        # Kapat butonu
        self.close_btn = ctk.CTkButton(
            self,
            text="✕",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color="#d50000",
            command=self.hide
        )
        self.close_btn.pack(side="right", padx=10)
        
        # Başlangıçta gizli
        self.pack_forget()
        
    def show(self, message: str, duration_ms: int = 5000):
        """
        Banner'ı göster
        
        Args:
            message: Hata mesajı
            duration_ms: Gösterim süresi (0 = sonsuz)
        """
        self.message_label.configure(text=message)
        self.pack(side="top", fill="x", before=self.master.winfo_children()[0])
        
        # Pulse animasyonu
        self._start_pulse()
        
        # Otomatik gizleme
        if duration_ms > 0:
            self.after(duration_ms, self.hide)
            
    def hide(self):
        """Banner'ı gizle"""
        self.pack_forget()
        
    def _start_pulse(self, count: int = 3):
        """Pulse animasyonu (3 kez yanıp söner)"""
        def pulse_step(step: int):
            if step >= count * 2:
                return
                
            # Renk değiştir
            if step % 2 == 0:
                color = "#ff1744"  # Kırmızı
            else:
                color = "#d50000"  # Koyu kırmızı
                
            self.configure(fg_color=color)
            
            # Sonraki step
            self.after(200, lambda: pulse_step(step + 1))
            
        pulse_step(0)


class RadarPingSound:
    """
    Radar ping sesi efekti
    
    Not: Gerçek ses için winsound veya pygame kullanılabilir
    """
    
    @staticmethod
    def play():
        """Radar ping sesini çal"""
        try:
            import winsound
            # Basit bir beep sesi (800 Hz, 200ms)
            winsound.Beep(800, 200)
        except:
            # Ses çalınamazsa sessizce devam et
            pass

