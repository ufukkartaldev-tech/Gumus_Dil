from pygments import lex
from pygments.lexer import RegexLexer, bygroups
from pygments.token import *

import tkinter as tk

class GumusLexer(RegexLexer):
    name = 'Gumus'
    aliases = ['gumus', 'tr']
    filenames = ['*.tr']

    tokens = {
        'root': [
            (r'\s+', Text),
            (r'//.*?$', Comment.Single), # Support // comments
            (r'#.*?$', Comment.Single),
            (r'"(\\\\|\\"|[^"])*"', String),
            (r'\'(\\\\|\\\'|[^\\\'])*\'', String),
            # Keywords (Both accented and unaccented)
            (r'\b(fonksiyon|eğer|eger|değilse|degilse|yoksa|döngü|dongu|dön|don|kır|kir|devam|sınıf|sinif|miras|öz|oz|temel|dahil_et|değişken|degisken|modül|modul|dene|deneme|yakala|ve|veya|ben|kurucu|kır|devam)\b', Keyword),
            (r'\b(doğru|dogru|yanlış|yanlis|yok)\b', Keyword.Constant),
            # Builtins
            (r'\b(yazdır|yazdir|girdi|uzunluk|sayı|sayi|metin|zaman|karekök|karekok|tip|ekle|sil|sırala|sirala|rastgele|ters_cevir|icerir|buyuk|kucuk|parcala|bul|kirp|yer_degistir|dosya_oku|dosya_yaz|dosya_ekle|dosya_varmi|bekle|sistem)\b', Name.Builtin),
            # Function calls
            (r'([a-zA-Z_üğışçöÜĞİŞÇÖ][a-zA-Z0-9_üğışçöÜĞİŞÇÖ]*)(\s*)(\()', bygroups(Name.Function, Text, Punctuation)),
            # Class definitions
            (r'\b(sınıf|sinif)(\s+)([a-zA-Z_üğışçöÜĞİŞÇÖ][a-zA-Z0-9_üğışçöÜĞİŞÇÖ]*)', bygroups(Keyword, Text, Name.Class)),

            # Operators
            (r'(\+|\-|\*|\/|%|=|<|>|!|&|\|)', Operator),
            # Numbers
            (r'\d+', Number),
            # Names
            (r'[a-zA-Z_üğışçöÜĞİŞÇÖ][a-zA-Z0-9_üğışçöÜĞİŞÇÖ]*', Name),
            (r'[(){}\[\],;]', Punctuation),
        ]

    }

class SyntaxHighlighter:
    def __init__(self, text_widget, config):
        self.text_widget = text_widget
        self.config = config
        self.lexer = GumusLexer()
        
        self.setup_tags()

    def setup_tags(self):
        theme = self.config.THEMES[self.config.theme]
        # Regex tokens to Theme keys mapping
        self.tag_colors = {
            Token.Keyword: theme['keyword'],
            Token.Keyword.Constant: theme['number'],
            Token.String: theme['string'],
            Token.Number: theme['number'],
            Token.Comment.Single: theme['comment'],
            Token.Operator: theme['accent'],
            Token.Name: theme['fg'],
            Token.Name.Builtin: theme['function'],
            Token.Name.Function: theme['function'],
            Token.Name.Class: theme['class'],
            Token.Punctuation: theme['fg'],
            Token.Text: theme['fg']
        }

        
        for token, color in self.tag_colors.items():
            self.text_widget.tag_config(str(token), foreground=color)

    def highlight(self, event=None):
        if not self.text_widget: return
        
        # Tüm içeriği al
        code = self.text_widget.get("1.0", "end-1c")
        
        # Mevcut tagleri temizle (Sadece syntax taglerini)
        for token in self.tag_colors.keys():
            self.text_widget.tag_remove(str(token), "1.0", "end")

        # Lexer ile analiz et
        self.text_widget.mark_set("range_start", "1.0")
        for token, content in lex(code, self.lexer):
            self.text_widget.mark_set("range_end", f"range_start + {len(content)}c")
            self.text_widget.tag_add(str(token), "range_start", "range_end")
            self.text_widget.mark_set("range_start", "range_end")

