# -*- coding: utf-8 -*-
"""
Terminal Test Script - Yeni özellikleri test et
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.ide.config import Config
import customtkinter as ctk
import tkinter as tk

# Simple terminal test
class TerminalTest:
    def __init__(self):
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("🧪 Terminal Test")
        self.root.geometry("800x600")
        
        config = Config(mode='pro')
        
        # Terminal'i import et ve oluştur
        from src.ide.ui.terminal import Terminal
        self.terminal = Terminal(self.root, config)
        self.terminal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Test callback
        self.terminal.set_input_callback(self.on_input)
        
        # Debug mode toggle butonu
        self.debug_btn = ctk.CTkButton(
            self.root, 
            text="🐛 Debug Modu Aç/Kapat", 
            command=self.toggle_debug
        )
        self.debug_btn.pack(pady=5)
        
        # Başlangıç mesajları
        self.terminal.write_text("💎 Gümüşdil Terminal Testi Başladı!\n")
        self.terminal.write_text("📝 Özellikler:\n")
        self.terminal.write_text("   • Yukarı/Aşağı ok: Komut geçmişi\n")
        self.terminal.write_text("   • Tab: Otomatik tamamlama (yazdır, eğer, döngü...)\n")
        self.terminal.write_text("   • Ctrl+C: Kopyala, Ctrl+V: Yapıştır\n")
        self.terminal.write_text("   • Syntax highlighting: Türkçe anahtar kelimeler renklendirilir\n\n")
        self.terminal.write_text("💡 Denemek için: 'yaz' yazıp TAB'a bas!\n\n")
        
    def on_input(self, text):
        """Terminal input callback"""
        if text.lower() == "temizle":
            self.terminal.clear()
            self.terminal.write_text("🧹 Terminal temizlendi!\n")
        elif text.lower() == "yardım":
            self.show_help()
        elif text.lower().startswith("yazdır"):
            self.terminal.write_text(f"✅ Komut çalıştırıldı: {text}\n")
        else:
            self.terminal.write_text(f"❓ Bilinmeyen komut: {text}\n")
    
    def show_help(self):
        """Yardım menüsü"""
        help_text = """
📚 Gümüşdil Terminal Komutları:
• temizle - Terminali temizler
• yardım - Bu menüyü gösterir
• yazdır(metin) - Metin yazdırır
• eğer(koşul) { ... } - Koşul kontrolü
• döngü(koşul) { ... } - Döngü başlatır

🎹 Kısayollar:
• ↑/↓ - Komut geçmişi
• Tab - Otomatik tamamlama
• Ctrl+C - Kopyala
• Ctrl+V - Yapıştır
"""
        self.terminal.write_text(help_text)
    
    def toggle_debug(self):
        """Debug modunu aç/kapat"""
        # Debug state'i tutmak için basit bir toggle
        if not hasattr(self, 'is_debug'):
            self.is_debug = False
        
        self.is_debug = not self.is_debug
        self.terminal.set_debug_mode(self.is_debug)
        
        mode_text = "🐛 DEBUG Modu AÇIK" if self.is_debug else "⌨️ Normal Mod"
        self.terminal.write_text(f"\n{mode_text}\n")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    test = TerminalTest()
    test.run()

