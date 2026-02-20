# -*- coding: utf-8 -*-
"""
Gümüşdil Terminal Unit Testleri
pytest framework ile
"""
import pytest
import sys
import os

# Proje path'ini ekle
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# src modülünü doğrudan ekle
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

try:
    from src.ide.ui.terminal import Terminal
    from src.ide.config import Config
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Project root: {project_root}")
    print(f"Src path: {src_path}")
    print(f"Python path: {sys.path}")
    raise
import tkinter as tk
import customtkinter as ctk

class TestTerminal:
    """Terminal sınıfı için unit testleri"""
    
    @pytest.fixture
    def terminal(self):
        """Test için terminal fixture"""
        # GUI'yi gizle
        root = tk.Tk()
        root.withdraw()
        
        # CustomTkinter ayarları
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        config = Config(mode='pro')
        terminal = Terminal(root, config)
        
        yield terminal
        
        # Cleanup
        root.destroy()
    
    def test_initialization(self, terminal):
        """Terminal başlangıç testi"""
        assert terminal.config is not None
        assert terminal.history == []
        assert terminal.history_index == -1
        assert len(terminal.completions) > 0
        assert "yazdır" in terminal.completions
    
    def test_add_to_history(self, terminal):
        """History ekleme testi"""
        # Tekrar eden komut engellenmeli
        terminal.add_to_history("yazdır('merhaba')")
        terminal.add_to_history("yazdır('merhaba')")  # Aynı komut
        terminal.add_to_history("değişken x = 5")
        
        assert len(terminal.history) == 2
        assert terminal.history[0] == "yazdır('merhaba')"
        assert terminal.history[1] == "değişken x = 5"
        assert terminal.history_index == -1
    
    def test_history_navigation_up(self, terminal):
        """Yukarı ok ile history gezinme"""
        terminal.add_to_history("komut1")
        terminal.add_to_history("komut2")
        
        # İlk yukarı basış (en son komut)
        terminal._on_history_up(None)
        assert terminal.input_entry.get() == "komut2"
        assert terminal.history_index == 0
        
        # İkinci yukarı basış (önceki komut)
        terminal._on_history_up(None)
        assert terminal.input_entry.get() == "komut1"
        assert terminal.history_index == 1
    
    def test_history_navigation_down(self, terminal):
        """Aşağı ok ile history gezinme"""
        terminal.add_to_history("komut1")
        terminal.add_to_history("komut2")
        
        # Yukarı çık (en son komuta)
        terminal._on_history_up(None)
        terminal._on_history_up(None)
        
        # Aşağı in (bir önceki komuta)
        terminal._on_history_down(None)
        assert terminal.input_entry.get() == "komut2"
        assert terminal.history_index == 0
        
        # Tekrar aşağı (en son komuta)
        terminal._on_history_down(None)
        assert terminal.input_entry.get() == "komut1"
        assert terminal.history_index == -1
        
        # Son aşağı - boş olmalı
        terminal._on_history_down(None)
        assert terminal.input_entry.get() == ""
        assert terminal.history_index == -1
    
    def test_auto_complete(self, terminal):
        """Otomatik tamamlama testi"""
        # "yaz" -> "yazdır"
        terminal.input_entry.delete(0, tk.END)
        terminal.input_entry.insert(0, "yaz")
        terminal._on_tab_complete(None)
        assert terminal.input_entry.get() == "yazdır"
        
        # "eğer" tamamlama
        terminal.input_entry.delete(0, tk.END)
        terminal.input_entry.insert(0, "eğer")
        terminal._on_tab_complete(None)
        assert terminal.input_entry.get() == "eğer"
        
        # Boş input'ta tab basarsa hiçbir şey olmamalı
        terminal.input_entry.delete(0, tk.END)
        original = terminal.input_entry.get()
        terminal._on_tab_complete(None)
        assert terminal.input_entry.get() == original
    
    def test_syntax_highlighting(self, terminal):
        """Syntax highlighting testi"""
        # "yazdır" -> mavi
        terminal.input_entry.delete(0, tk.END)
        terminal.input_entry.insert(0, "yazdır")
        terminal._on_input_change()
        color = terminal.input_entry.cget("text_color")
        assert "#569cd6" in color or color == "#569cd6"
        
        # "eğer" -> mor
        terminal.input_entry.delete(0, tk.END)
        terminal.input_entry.insert(0, "eğer")
        terminal._on_input_change()
        color = terminal.input_entry.cget("text_color")
        assert "#c586c0" in color or color == "#c586c0"
        
        # Normal metin -> theme rengi
        terminal.input_entry.delete(0, tk.END)
        terminal.input_entry.insert(0, "normal_metin")
        terminal._on_input_change()
        color = terminal.input_entry.cget("text_color")
        theme_color = terminal.config.THEMES[terminal.config.theme]['terminal_fg']
        assert color == theme_color
    
    def test_debug_mode(self, terminal):
        """Debug modu testi"""
        # Debug modu aç
        terminal.set_debug_mode(True)
        assert "🐛 DEBUG >" in terminal.prompt_label.cget("text")
        
        # Debug modu kapat
        terminal.set_debug_mode(False)
        assert "⌨️ GİRDİ >" in terminal.prompt_label.cget("text")
    
    def test_write_text(self, terminal):
        """Metin yazma testi"""
        # Terminalde metin yaz
        terminal.write_text("test mesajı\n")
        
        # Output area'da kontrol et
        output_content = terminal.output_area.get("1.0", tk.END)
        assert "test mesajı\n" in output_content
    
    def test_write_text_tag(self, terminal):
        """Renkli metin yazma testi"""
        terminal.write_text_tag("yeşil mesaj", "suggestion")
        
        # Tag kontrolü (biraz tricky olabilir)
        output_content = terminal.output_area.get("1.0", tk.END)
        assert "yeşil mesaj" in output_content
    
    def test_clear(self, terminal):
        """Terminal temizleme testi"""
        # Önce bir şeyler yaz
        terminal.write_text("test1\ntest2\ntest3")
        
        # Temizle
        terminal.clear()
        
        # Boş olmalı
        output_content = terminal.output_area.get("1.0", tk.END)
        assert output_content.strip() == ""
    
    def test_history_limit(self, terminal):
        """History limit testi (100 komut)"""
        # 101 komut ekle
        for i in range(101):
            terminal.add_to_history(f"komut_{i}")
        
        # Sadece 100 komut olmalı
        assert len(terminal.history) == 100
        assert "komut_0" not in terminal.history  # İlk komut silinmeli
        assert "komut_100" in terminal.history   # Son komut olmalı
    
    def test_empty_history_navigation(self, terminal):
        """Boş history'de navigasyon testi"""
        # Boş history'de yukarı/aşağı basarsa hata vermemeli
        terminal._on_history_up(None)
        assert terminal.input_entry.get() == ""
        
        terminal._on_history_down(None)
        assert terminal.input_entry.get() == ""
    
    def test_completions_list(self, terminal):
        """Tamamlama listesi kontrolü"""
        expected_completions = [
            "yazdır", "eğer", "değilse", "döngü", "fonksiyon", 
            "değişken", "sınıf", "modül", "dön", "doğru", "yanlış",
            "deneme", "yakala", "ve", "veya", "her", "kurucu", "öz"
        ]
        
        assert len(terminal.completions) == len(expected_completions)
        for completion in expected_completions:
            assert completion in terminal.completions

# Integration testleri
class TestTerminalIntegration:
    """Terminal entegrasyon testleri"""
    
    @pytest.fixture
    def terminal_with_callback(self):
        """Callback ile terminal fixture"""
        root = tk.Tk()
        root.withdraw()
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        config = Config(mode='pro')
        terminal = Terminal(root, config)
        
        # Mock callback
        terminal.input_callback = lambda x: None
        
        yield terminal
        root.destroy()
    
    def test_enter_pressed_with_callback(self, terminal_with_callback, mocker):
        """Enter tuşu ile callback tetikleme"""
        # Mock callback
        mock_callback = mocker.Mock()
        terminal_with_callback.input_callback = mock_callback
        
        # Input ekle ve Enter bas
        terminal_with_callback.input_entry.delete(0, tk.END)
        terminal_with_callback.input_entry.insert(0, "test komutu")
        terminal_with_callback._on_enter_pressed(None)
        
        # Callback çağrılmış olmalı
        mock_callback.assert_called_once_with("test komutu")
        
        # History'ye eklenmiş olmalı
        assert "test komutu" in terminal_with_callback.history
        
        # Input temizlenmiş olmalı
        assert terminal_with_callback.input_entry.get() == ""

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

