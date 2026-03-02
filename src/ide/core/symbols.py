# -*- coding: utf-8 -*-
import re

class SymbolExtractor:
    """Gümüşdil kodundan fonksiyon, sınıf ve değişkenleri ayıklar"""
    
    # Regex kalıpları (Strict Turkish)
    CLASS_PATTERN = re.compile(r'\b(sınıf)\s+([a-zA-Z_ığüşöçİĞÜŞÖÇ][a-zA-Z0-9_ığüşöçİĞÜŞÖÇ]*)')
    # Fonksiyon Kontrolü (Parametreleri de yakalar)
    FUNC_PATTERN = re.compile(r'\b(fonksiyon)\s+([a-zA-Z_ığüşöçİĞÜŞÖÇ][a-zA-Z0-9_ığüşöçİĞÜŞÖÇ]*)\s*\((.*?)\)')
    VAR_PATTERN = re.compile(r'\b(değişken)\s+([a-zA-Z_ığüşöçİĞÜŞÖÇ][a-zA-Z0-9_ığüşöçİĞÜŞÖÇ]*)')

    @staticmethod
    def extract_from_text(text):
        """Metin içindeki tüm sembolleri satır numaralarıyla birlikte döner"""
        symbols = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_no = i + 1
            
            # Sınıf Kontrolü
            match = SymbolExtractor.CLASS_PATTERN.search(line)
            if match:
                symbols.append({
                    'name': match.group(2),
                    'type': 'class',
                    'line': line_no,
                    'icon': '🏛️'
                })
                continue
                
            # Fonksiyon Kontrolü
            match = SymbolExtractor.FUNC_PATTERN.search(line)
            if match:
                symbols.append({
                    'name': match.group(2),
                    'type': 'function',
                    'line': line_no,
                    'params': match.group(3).strip(), # Parametreleri al
                    'icon': 'ƒ'
                })
                continue
                
            # Değişken Kontrolü
            match = SymbolExtractor.VAR_PATTERN.search(line)
            if match:
                symbols.append({
                    'name': match.group(2),
                    'type': 'variable',
                    'line': line_no,
                    'icon': '💎'
                })
                
        return symbols

