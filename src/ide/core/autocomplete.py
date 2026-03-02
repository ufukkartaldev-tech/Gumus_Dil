# -*- coding: utf-8 -*-
import os

class AutoCompleter:
    """GümüşDil Otomatik Tamamlama ve Snippet Mantığı"""
    
    def __init__(self):
        self.keywords = [
            "yazdır", "eğer", "değilse", "döngü", "fonksiyon", "değişken", "sınıf", "dön", 
            "doğru", "yanlış", "yok", "dahil_et", "dene", "yakala", "ve", "veya", "öz", "miras",
            "dosya_oku", "dosya_yaz", "dosya_ekle", "dosya_varmi", "bekle", "temizle", 
            "uzunluk", "metin", "sayı", "girdi", "zaman", "tip", "sistem"
        ]
        self.snippets = {
            "eğer": " () {\n    \n}",
            "değilse": " {\n    \n}",
            "yoksa": " eğer () {\n    \n}",
            "döngü": " () {\n    \n}",
            "fonksiyon": " isim() {\n    \n    dön \n}",
            "sınıf": " İsim {\n    kurucu() {\n        \n    }\n}",
            "dene": " {\n    \n} yakala(hata) {\n    yazdır(hata)\n}",
            "yazdır": "(\"\")",
            "değişken": " isim = ",
            "dahil_et": "(\".tr\")"
        }
        
    def get_snippet(self, word):
        """Kelime için snippet döndür (yoksa None)"""
        return self.snippets.get(word)

    def should_indent(self, line_text):
        """Satırın girintilenmesi gerekip gerekmediğini kontrol et"""
        stripped = line_text.strip()
        return stripped.endswith(("{", "(", ":", "[")) or \
               stripped.startswith(("eğer", "değilse", "yoksa", "döngü", "fonksiyon", "sınıf", "dene", "yakala"))

    def get_completions(self, text_before_cursor):
        """
        İmleç öncesindeki metne göre önerileri döndürür.
        Dönüş: [(word, meta_dict), ...]
        """
        # Basit bir mantık: son kelimeyi al
        import re
        match = re.search(r'([a-zA-Z_ığüşöçİĞÜŞÖÇ]+)$', text_before_cursor)
        if not match:
            return []
            
        prefix = match.group(1)
        suggestions = []
        
        # Snippet'ları ekle
        for key in self.snippets:
            if key.startswith(prefix):
                suggestions.append((key, {"type": "snippet", "doc": "Kod Bloğu"}))
                
        # Anahtar kelimeleri ekle (Henüz snippet'i yoksa)
        for key in self.keywords:
            if key.startswith(prefix) and key not in self.snippets:
                suggestions.append((key, {"type": "keyword", "doc": "Yerleşik Anahtar Kelime"}))
        
        return suggestions

