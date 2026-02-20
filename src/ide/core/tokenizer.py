# -*- coding: utf-8 -*-
import re

class TokenType:
    # Keywords
    FUNCTION = 'FONKSIYON'
    IF = 'EGER'
    ELSE = 'DEGILSE'
    WHILE = 'DONGU'
    RETURN = 'DON'
    VAR = 'DEGISKEN'
    CLASS = 'SINIF'
    THIS = 'OZ'
    SUPER = 'ATA'
    BREAK = 'KIR'
    CONTINUE = 'DEVAM'
    PRINT = 'YAZDIR'
    INCLUDE = 'DAHIL_ET'
    NEW = 'YENI'
    TRY = 'DENE'
    CATCH = 'YAKALA'
    FOR = 'DONGU_FOR'
    
    # Literals
    IDENTIFIER = 'ISIM'
    STRING = 'METIN'
    NUMBER = 'SAYI'
    TRUE = 'DOGRU'
    FALSE = 'YANLIS'
    NULL = 'YOK'
    
    # Operators
    PLUS = 'ARTI'
    MINUS = 'EKSI'
    STAR = 'CARPI'
    SLASH = 'BOLU'
    PERCENT = 'MOD'
    EQ = 'ESITTIR'
    EQEQ = 'ESIT_MI'
    BANG = 'UNLEM'
    BANGEQ = 'ESIT_DEGIL'
    GT = 'BUYUK'
    GTEQ = 'BUYUK_ESIT'
    LT = 'KUCUK'
    LTEQ = 'KUCUK_ESIT'
    AND = 'VE'
    OR = 'VEYA'
    
    # Delimiters
    LPAREN = 'SOL_PAR'
    RPAREN = 'SAG_PAR'
    LBRACE = 'SOL_SUS'
    RBRACE = 'SAG_SUS'
    LBRACKET = 'SOL_KOS'
    RBRACKET = 'SAG_KOS'
    COMMA = 'VIRGUL'
    DOT = 'NOKTA'
    SEMICOLON = 'NOKTALI_VIRGUL'
    OF = 'OF'  # for 'of' loops if we supported them, Gümüş uses standard loops
    
    EOF = 'SON'

class Token:
    def __init__(self, type, value, line=0):
        self.type = type
        self.value = value
        self.line = line
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line})"

class GumusTokenizer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        
        self.keywords = {
            'fonksiyon': TokenType.FUNCTION,
            'eğer': TokenType.IF, 'eger': TokenType.IF,
            'değilse': TokenType.ELSE, 'degilse': TokenType.ELSE, 'yoksa': TokenType.ELSE,
            'döngü': TokenType.WHILE, 'dongu': TokenType.WHILE, 
            'dön': TokenType.RETURN, 'don': TokenType.RETURN,
            'kır': TokenType.BREAK, 'kir': TokenType.BREAK,
            'devam': TokenType.CONTINUE,
            'değişken': TokenType.VAR, 'degisken': TokenType.VAR,
            'sınıf': TokenType.CLASS, 'sinif': TokenType.CLASS,
            'öz': TokenType.THIS, 'oz': TokenType.THIS, 'ben': TokenType.THIS,
            'ata': TokenType.SUPER, 'temel': TokenType.SUPER,
            'yazdır': TokenType.PRINT, 'yazdir': TokenType.PRINT,
            'doğru': TokenType.TRUE, 'dogru': TokenType.TRUE,
            'yanlış': TokenType.FALSE, 'yanlis': TokenType.FALSE,
            'yok': TokenType.NULL,
            'dahil_et': TokenType.INCLUDE, 'dahil et': TokenType.INCLUDE,
            'boş geç': TokenType.NULL, 'bos gec': TokenType.NULL,
            'devam': TokenType.CONTINUE, 'devam et': TokenType.CONTINUE,
            'çık': TokenType.EOF, 'cik': TokenType.EOF,
            'dene': TokenType.TRY,
            'yakala': TokenType.CATCH,
            'yeni': TokenType.NEW,
            've': TokenType.AND,
            'veya': TokenType.OR
        }

    def tokenize(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        
        self.tokens.append(Token(TokenType.EOF, "", self.line))
        return self.tokens

    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def peek(self):
        if self.is_at_end(): return '\0'
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source): return '\0'
        return self.source[self.current + 1]

    def match(self, expected):
        if self.is_at_end(): return False
        if self.source[self.current] != expected: return False
        self.current += 1
        return True

    def scan_token(self):
        c = self.advance()
        
        if c in ' \r\t':
            pass
        elif c == '\n':
            self.line += 1
        elif c == '(': self.add_token(TokenType.LPAREN)
        elif c == ')': self.add_token(TokenType.RPAREN)
        elif c == '{': self.add_token(TokenType.LBRACE)
        elif c == '}': self.add_token(TokenType.RBRACE)
        elif c == '[': self.add_token(TokenType.LBRACKET)
        elif c == ']': self.add_token(TokenType.RBRACKET)
        elif c == ',': self.add_token(TokenType.COMMA)
        elif c == '.': self.add_token(TokenType.DOT)
        elif c == ';': self.add_token(TokenType.SEMICOLON)
        elif c == '+': self.add_token(TokenType.PLUS)
        elif c == '-': self.add_token(TokenType.MINUS) # TODO: -> arrow?
        elif c == '*': self.add_token(TokenType.STAR)
        elif c == '%': self.add_token(TokenType.PERCENT)
        elif c == '!': self.add_token(TokenType.BANGEQ if self.match('=') else TokenType.BANG)
        elif c == '=': self.add_token(TokenType.EQEQ if self.match('=') else TokenType.EQ)
        elif c == '<': self.add_token(TokenType.LTEQ if self.match('=') else TokenType.LT)
        elif c == '>': self.add_token(TokenType.GTEQ if self.match('=') else TokenType.GT)
        elif c == '/':
            if self.match('/'):
                # Comment
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif c == '"':
            self.string()
        elif self.is_digit(c):
            self.number()
        elif self.is_alpha(c):
            self.identifier()
        else:
            # print(f"Unexpected char: {c} at line {self.line}")
            pass

    def add_token(self, type, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, literal if literal is not None else text, self.line))

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n': self.line += 1
            self.advance()
        
        if self.is_at_end():
            # Unterminated string
            return
            
        self.advance() # Closing "
        value = self.source[self.start+1 : self.current-1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()
        
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()
        
        val = float(self.source[self.start:self.current])
        # If integer, keep as int logic if needed, but python handlefloat fine
        if val.is_integer():
            val = int(val)
        self.add_token(TokenType.NUMBER, val)

    def identifier(self):
        while self.is_alpha_numeric(self.peek()):
            self.advance()
            
        text = self.source[self.start:self.current]
        
        # Check for multi-word keywords
        if text == "dahil" and self.peek() == " " and self.peek_next() != " ":
            # Try to match "dahil et"
            saved_current = self.current
            self.advance() # space
            word2_start = self.current
            while self.is_alpha_numeric(self.peek()):
                self.advance()
            word2 = self.source[word2_start:self.current]
            if word2 == "et":
                text = "dahil et"
            else:
                self.current = saved_current # backtrack

        elif text == "boş" and self.peek() == " " and self.peek_next() != " ":
            saved_current = self.current
            self.advance()
            word2_start = self.current
            while self.is_alpha_numeric(self.peek()):
                self.advance()
            word2 = self.source[word2_start:self.current]
            if word2 == "geç" or word2 == "gec":
                text = "boş geç"
            else:
                self.current = saved_current

        elif text == "devam" and self.peek() == " " and self.peek_next() != " ":
            saved_current = self.current
            self.advance()
            word2_start = self.current
            while self.is_alpha_numeric(self.peek()):
                self.advance()
            word2 = self.source[word2_start:self.current]
            if word2 == "et":
                text = "devam et"
            else:
                self.current = saved_current

        type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(type)

    def is_digit(self, c):
        return '0' <= c <= '9'

    def is_alpha(self, c):
        return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or c == '_' or c in 'üğışçöÜĞİŞÇÖ'

    def is_alpha_numeric(self, c):
        return self.is_alpha(c) or self.is_digit(c)

class TokenizerRunner:
    @staticmethod
    def get_tokens(source):
        t = GumusTokenizer(source)
        return t.tokenize()

