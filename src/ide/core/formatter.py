# -*- coding: utf-8 -*-
import re

class GumusFormatter:
    """GümüşDil Kod Formatlayıcı: Standartlara uygun düzenleme yapar."""
    
    @staticmethod
    def format(code):
        if not code: return ""
        
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                formatted_lines.append("")
                continue
            
            # 1. Kapanış parantezi varsa girintiyi azalt
            if trimmed.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # 2. Girintiyi uygula
            indent = "    " * indent_level
            
            # 3. Operatörler arasına boşluk koy (x=5+2 -> x = 5 + 2)
            # String ve yorumları korumak için: Satırda tırnak varsa içeriğe dokunma.
            line_content = trimmed
            
            if not trimmed.startswith('//') and '"' not in trimmed and "'" not in trimmed:
                # =, +, -, *, /, ==, !=, >=, <=
                operators = ['==', '!=', '>=', '<=', '=', '+', '-', '*', '/']
                for op in operators:
                    if op in ['==', '!=', '>=', '<=']:
                         line_content = line_content.replace(op, f" {op} ")
                    else:
                         if op == '=' and ('==' in line_content or '!=' in line_content or '>=' in line_content or '<=' in line_content):
                             continue
                         line_content = line_content.replace(op, f" {op} ")

                # Temizlik
                line_content = re.sub(r'\s+', ' ', line_content)
                line_content = line_content.replace('( ', '(').replace(' )', ')')
                line_content = line_content.replace(',', ', ')
                line_content = re.sub(r'\s+', ' ', line_content)
            
            formatted_lines.append(indent + line_content.strip())
            
            # 4. Açılış parantezi varsa bir sonraki satır için girintiyi artır
            if trimmed.endswith('{'):
                indent_level += 1
                
        return '\n'.join(formatted_lines)

