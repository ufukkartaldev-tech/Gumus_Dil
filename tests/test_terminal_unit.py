# -*- coding: utf-8 -*-
"""
Gümüşdil Terminal Unit Testleri - GUI'siz versiyon
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

# Mock GUI sınıfları
class MockTk:
    END = "end"
    
    def __init__(self):
        pass
    
    def withdraw(self):
        pass
    
    def destroy(self):
        pass

class MockCTk:
    class CTkFrame:
        def __init__(self, parent=None, **kwargs):
            pass
        
        def pack(self, **kwargs):
            pass
        
        def bind(self, event, callback):
            pass
        
        def configure(self, **kwargs):
            pass
    
    class CTkTextbox:
        def __init__(self, parent=None, **kwargs):
            # Mock underlying tkinter widget
            self._textbox = self
        
        def configure(self, **kwargs):
            pass
        
        def get(self, start, end):
            return ""
        
        def delete(self, start, end):
            pass
        
        def see(self, index):
            pass
        
        def tag_config(self, tag, **kwargs):
            pass
        
        def insert(self, index, text):
            pass
        
        def pack(self, **kwargs):
            pass
        
        def bind(self, event, callback):
            pass
    
    class CTkEntry:
        def __init__(self, parent=None, **kwargs):
            pass
        
        def delete(self, start, end):
            pass
        
        def insert(self, index, text):
            pass
        
        def get(self):
            return ""
        
        def cget(self, option):
            return ""
        
        def configure(self, **kwargs):
            pass
        
        def bind(self, event, callback):
            pass
        
        def pack(self, **kwargs):
            pass
    
    class CTkLabel:
        def __init__(self, parent=None, **kwargs):
            self.text = ""
        
        def cget(self, option):
            return self.text
        
        def configure(self, **kwargs):
            if "text" in kwargs:
                self.text = kwargs["text"]
        
        def pack(self, **kwargs):
            pass
    
    @staticmethod
    def set_appearance_mode(mode):
        pass
    
    @staticmethod
    def set_default_color_theme(theme):
        pass

# Mock modüller
sys.modules['tkinter'] = MockTk()
sys.modules['customtkinter'] = MockCTk()

try:
    from src.ide.ui.terminal import Terminal
    from src.ide.config import Config
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Project root: {project_root}")
    print(f"Src path: {src_path}")
    print(f"Python path: {sys.path}")
    raise

class MockInputEntry:
    def __init__(self):
        self.text = ""
    
    def delete(self, start, end):
        self.text = ""
    
    def insert(self, position, text):
        self.text = text
    
    def get(self):
        return self.text
    
    def cget(self, option):
        if option == "text_color":
            return "#569cd6"  # Default mavi
        return ""
    
    def configure(self, **kwargs):
        pass

class MockOutputArea:
    def __init__(self):
        self.content = ""
    
    def get(self, start, end):
        return self.content
    
    def configure(self, **kwargs):
        pass

class MockLabel:
    def __init__(self):
        self.text = ""
    
    def cget(self, option):
        return self.text
    
    def configure(self, **kwargs):
        if "text" in kwargs:
            self.text = kwargs["text"]

class TestTerminalUnit:
    """Terminal unit testleri - GUI olmadan"""
    
    @pytest.fixture
    def terminal(self):
        """Test için terminal fixture (GUI mock)"""
        config = Config(mode='pro')
        terminal = Terminal(None, config)  # Parent yok
        
        # Mock GUI components
        terminal.input_entry = MockInputEntry()
        terminal.output_area = MockOutputArea()
        terminal.prompt_label = MockLabel()
        
        # Test için history'i sıfırla
        terminal.history = []
        terminal.history_index = -1
        
        yield terminal
    
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
        
        # Tekrar aşağı (input temizlenmeli)
        terminal._on_history_down(None)
        assert terminal.input_entry.get() == ""
        assert terminal.history_index == -1
        
        # Son aşağı - yine boş olmalı
        terminal._on_history_down(None)
        assert terminal.input_entry.get() == ""
        assert terminal.history_index == -1
    
    def test_auto_complete(self, terminal):
        """Otomatik tamamlama testi"""
        # "yaz" -> "yazdır"
        terminal.input_entry.delete(0, "end")
        terminal.input_entry.insert(0, "yaz")
        terminal._on_tab_complete(None)
        assert terminal.input_entry.get() == "yazdır"
        
        # "eğer" tamamlama
        terminal.input_entry.delete(0, "end")
        terminal.input_entry.insert(0, "eğer")
        terminal._on_tab_complete(None)
        assert terminal.input_entry.get() == "eğer"
        
        # Boş input'ta tab basarsa hiçbir şey olmamalı
        terminal.input_entry.delete(0, "end")
        original = terminal.input_entry.get()
        terminal._on_tab_complete(None)
        assert terminal.input_entry.get() == original
    
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
    
    def test_debug_mode(self, terminal):
        """Debug modu testi"""
        # Debug modu aç
        terminal.set_debug_mode(True)
        assert "🐛 DEBUG >" in terminal.prompt_label.cget("text")
        
        # Debug modu kapat
        terminal.set_debug_mode(False)
        assert "⌨️ GİRDİ >" in terminal.prompt_label.cget("text")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

