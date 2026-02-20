#include "tokenizer.h"
#include <cctype>
#include "../json_hata.h"

Tokenizer::Tokenizer(const std::string& source) 
    : source(source), position(0), line(1), column(1) {}

std::vector<Token> Tokenizer::tokenize() {
    std::vector<Token> tokens;
    while (!isAtEnd()) {
        skipWhitespace();
        if (isAtEnd()) break;
        
        // Template String Check ($")
        if (peek() == '$' && peek(1) == '"') {
            scanTemplateString(tokens);
            continue;
        }

        tokens.push_back(scanToken());
    }
    tokens.push_back({TokenType::END_OF_FILE, "", line, column});
    return tokens;
}

void Tokenizer::scanTemplateString(std::vector<Token>& tokens) {
    advance(); // $
    advance(); // "
    
    // Baslangic "" stringi (birlestirme operatoru icin guvenli baslangic)
    tokens.push_back({TokenType::STRING, "", line, column});
    
    while (!isAtEnd()) {
        // Araya + koy
        tokens.push_back({TokenType::PLUS, "+", line, column});
        
        std::string buffer = "";
        while (!isAtEnd()) {
            char c = peek();
            if (c == '"' || c == '{') break;
            if (c == '\n') line++;
            buffer += advance();
        }
        
        // String parcasini ekle
        tokens.push_back({TokenType::STRING, buffer, line, column});
        
        if (isAtEnd()) break; // Hata firlatilmali aslinda
        
        char term = peek();
        if (term == '"') {
            advance(); // Kapatan "
            break;
        } else if (term == '{') {
            advance(); // {
            
            // " + metin(
            tokens.push_back({TokenType::PLUS, "+", line, column});
            tokens.push_back({TokenType::IDENTIFIER, "metin", line, column});
            tokens.push_back({TokenType::LPAREN, "(", line, column});
            
            // Ic ifadeyi (expression) parse et - Daha guvenli sekilde
            int balance = 1;
            int startPos = position; // Hata durumunda geri dönmek için
            int startLine = line;
            
            while (balance > 0 && !isAtEnd()) {
                // Skip whitespace
                skipWhitespace();
                
                if (isAtEnd()) {
                    // Dengesiz parantez - hatayı raporla ve döngüden çık
                    break;
                }
                
                char ch = peek();
                
                if (ch == '{') {
                    // Yeni seviye açılıyor
                    tokens.push_back(scanToken());
                    balance++;
                } else if (ch == '}') {
                    // Mevcut seviye kapanıyor
                    balance--;
                    if (balance == 0) {
                        // Bu } karakteri bize ait, tüket
                        advance(); // } karakterini tüket
                        break;
                    } else {
                        // Dengesiz } karakteri
                        tokens.push_back(scanToken());
                    }
                } else {
                    // Normal karakter - token'a çevir
                    tokens.push_back(scanToken());
                }
            }
            
            // Eğer dengesiz parantez varsa, sonraki }'ye kadar atla
            if (balance > 0) {
                // Dengesiz parantez - güvenli çık
                // } karakterine kadar ilerle
                while (!isAtEnd() && peek() != '}') {
                    advance();
                }
                if (!isAtEnd()) advance(); // } karakterini tüket
            }
            
            // )
            tokens.push_back({TokenType::RPAREN, ")", line, column});
        }
    }
}

char Tokenizer::peek(int offset) const {
    if (position + offset >= source.length()) return '\0';
    return source[position + offset];
}

char Tokenizer::advance() {
    if (isAtEnd()) return '\0';
    char current = source[position++];
    column++;
    return current;
}

bool Tokenizer::isAtEnd() const {
    return position >= source.length();
}

void Tokenizer::skipWhitespace() {
    while (!isAtEnd()) {
        char c = peek();
        switch (c) {
            case ' ':
            case '\r':
            case '\t':
                advance();
                break;
            case '/':
                if (peek(1) == '/') {
                    // Yorum satiri: Satir sonuna kadar ilerle
                    while (peek() != '\n' && !isAtEnd()) advance();
                    // Yeni satir karakterini de atla (skipWhitespace dongusu devam edecek)
                } else {
                    return;
                }
                break;
            default:
                return;
        }
    }
}

Token Tokenizer::scanToken() {
    char c = peek();
    int startColumn = column;

    // Numbers
    if (isdigit(c)) {
        return number();
    }

    // Identifiers (starts with alpha, underscore, OR Extended ASCII)
    // 0x80 (128) ve uzeri tum karakterleri kabul et (Genisletilmis, UTF-8 vs)
    if (isalpha(c) || c == '_' || (unsigned char)c >= 0x80) {
        return identifier();
    }
    
    // Strings
    if (c == '"') {
        return string();
    }

    advance(); // Consume the character

    switch (c) {
        case '+': return {TokenType::PLUS, "+", line, startColumn};
        case '-': return {TokenType::MINUS, "-", line, startColumn};
        case '*': return {TokenType::MULTIPLY, "*", line, startColumn};
        case '/': return {TokenType::DIVIDE, "/", line, startColumn};
        case '%': return {TokenType::MOD, "%", line, startColumn};
        case '(': return {TokenType::LPAREN, "(", line, startColumn};
        case ')': return {TokenType::RPAREN, ")", line, startColumn};
        case '{': return {TokenType::LBRACE, "{", line, startColumn};
        case '}': return {TokenType::RBRACE, "}", line, startColumn};
        case '[': return {TokenType::LBRACKET, "[", line, startColumn};
        case ']': return {TokenType::RBRACKET, "]", line, startColumn};
        case ',': return {TokenType::COMMA, ",", line, startColumn};
        case '.': return {TokenType::DOT, ".", line, startColumn};
        
        case ':':
            if (match(':')) return {TokenType::COLON_COLON, "::", line, startColumn};
            return {TokenType::COLON, ":", line, startColumn};

        case ';': return {TokenType::SEMICOLON, ";", line, startColumn};
        
        case '!':
            if (match('=')) return {TokenType::BANG_EQUAL, "!=", line, startColumn};
            return {TokenType::BANG, "!", line, startColumn};
        case '=':
            if (match('=')) return {TokenType::EQUAL_EQUAL, "==", line, startColumn};
            return {TokenType::EQUAL, "=", line, startColumn};
        case '<':
            if (match('=')) return {TokenType::LESS_EQUAL, "<=", line, startColumn};
            return {TokenType::LESS, "<", line, startColumn};
        case '>':
            if (match('=')) return {TokenType::GREATER_EQUAL, ">=", line, startColumn};
            return {TokenType::GREATER, ">", line, startColumn};
        
        case '&':
            if (match('&')) return {TokenType::LOGIC_AND, "&&", line, startColumn};
            throw GumusException("lexer_error", line, "Beklenmeyen karakter: '&' (Kullanim: &&)");
        
        case '|':
            if (match('|')) return {TokenType::LOGIC_OR, "||", line, startColumn};
            throw GumusException("lexer_error", line, "Beklenmeyen karakter: '|' (Kullanim: ||)");
        
        case '\n': // This case should ideally not be reached if skipWhitespace handles newlines
            line++;
            column = 1;
            return {TokenType::NEW_LINE, "\\n", line-1, startColumn};

        default:
            std::string charInfo = std::string(1, c);
            std::string hexCode = std::to_string((int)(unsigned char)c);
            throw GumusException("lexer_error", line, "Bilinmeyen karakter: '" + charInfo + "' (ASCII: " + hexCode + ")");
    }
}

bool Tokenizer::match(char expected) {
    if (isAtEnd()) return false;
    if (source[position] != expected) return false;
    position++;
    column++;
    return true;
}

Token Tokenizer::number() {
    int startColumn = column;
    std::string value;

    while (isdigit(peek())) {
        value += advance();
    }

    // Decimal part
    if (peek() == '.' && isdigit(peek(1))) {
        value += advance(); // Consume '.'
        while (isdigit(peek())) {
            value += advance();
        }
    }

    return {TokenType::INTEGER, value, line, startColumn};

    return {TokenType::INTEGER, value, line, startColumn};
}

Token Tokenizer::string() {
    int startColumn = column;
    std::string value;
    
    advance(); // Consume opening quote

    while (peek() != '"' && !isAtEnd()) {
        char c = peek();
        
        if (c == '\\') {
            advance(); // Consume backslash
            if (isAtEnd()) break;
            
            char next = peek();
            switch (next) {
                case '"': value += '"'; advance(); break;
                case '\\': value += '\\'; advance(); break;
                case 'n': value += '\n'; advance(); break;
                case 't': value += '\t'; advance(); break;
                case 'r': value += '\r'; advance(); break;
                default: 
                    // Bilinmeyen escape sequence, backslash'i oldugu gibi birak
                    value += '\\'; 
                    // Sonraki karakter dongunun normal akisinda islenecek
                    break;
            }
        } else {
            if (c == '\n') line++;
            value += advance();
        }
    }

    if (isAtEnd()) {
        throw GumusException("lexer_error", line, "Sonlandirilmamis Metin (Tirnak isareti eksik)");
    }

    advance(); // Consume closing quote
    return {TokenType::STRING, value, line, startColumn};
}

Token Tokenizer::identifier() {
    int startColumn = column;
    std::string value;

    // UTF-8 ve Genisletilmis ASCII karakterleri kabul et (0x80 ve uzeri)
    while (isalnum(peek()) || peek() == '_' || (unsigned char)peek() >= 0x80) {
        value += advance();
    }

    // ========================================
    // SADECE TÜRKÇE ANAHTAR KELİMELER! 🇹🇷
    // "eger" YAZILIRSA HATA! SADECE "eğer"!
    // ========================================
    
    if (value == "de\xC4\x9F" "i\xC5\x9F" "ken") 
        return {TokenType::KW_VAR, value, line, startColumn};
    if (value == "yazd\xC4\xB1" "r") 
        return {TokenType::KW_YAZDIR, value, line, startColumn};
    if (value == "e\xC4\x9F" "er") 
        return {TokenType::KW_EGER, value, line, startColumn};
    if (value == "de\xC4\x9F" "ilse") 
        return {TokenType::KW_DEGILSE, value, line, startColumn};
    if (value == "d\xC3\xB6" "ng\xC3\xBC") 
        return {TokenType::KW_DONGU, value, line, startColumn};
    if (value == "fonksiyon") 
        return {TokenType::KW_FONKSIYON, value, line, startColumn};
    if (value == "d\xC3\xB6" "n") 
        return {TokenType::KW_DON, value, line, startColumn};
    if (value == "s\xC4\xB1" "n\xC4\xB1" "f") 
        return {TokenType::KW_SINIF, value, line, startColumn};
    if (value == "mod\xC3\xBC" "l") 
        return {TokenType::KW_MODUL, value, line, startColumn};
    if (value == "\xC3\xB6" "z") 
        return {TokenType::KW_OZ, value, line, startColumn};
    if (value == "her") 
        return {TokenType::KW_HER, value, line, startColumn};
    if (value == "kurucu") 
        return {TokenType::KW_KURUCU, value, line, startColumn};
    if (value == "do\xC4\x9F" "ru") 
        return {TokenType::KW_DOGRU, value, line, startColumn};
    if (value == "yanl\xC4\xB1\xC5\x9F") 
        return {TokenType::KW_YANLIS, value, line, startColumn};
    if (value == "deneme") 
        return {TokenType::KW_DENEME, value, line, startColumn};
    if (value == "yakala") 
        return {TokenType::KW_YAKALA, value, line, startColumn};
    if (value == "ve") 
        return {TokenType::LOGIC_AND, value, line, startColumn};
    if (value == "veya") 
        return {TokenType::LOGIC_OR, value, line, startColumn};
    if (value == "k\xC4\xB1" "r" || value == "dur") 
        return {TokenType::KW_KIR, value, line, startColumn};
    if (value == "devam") 
        return {TokenType::KW_DEVAM, value, line, startColumn};
    if (value == "ata") 
        return {TokenType::KW_ATA, value, line, startColumn};
    if (value == "bo\xC5\x9F") 
        return {TokenType::KW_BOS, value, line, startColumn};
    if (value == "yeni") 
        return {TokenType::KW_YENI, value, line, startColumn};



    // ========================================
    // HATA MESAJLARI - İngilizce karakterle yazılırsa!
    // ========================================
    
    if (value == "null" || value == "none") 
        throw GumusException("syntax_error", line, "❌ 'null' veya 'none' değil, 'boş' yazılmalı! (Türkçe karakter kullan)");

    if (value == "var" || value == "let") 
        throw GumusException("syntax_error", line, "❌ 'var' veya 'let' değil, 'değişken' yazılmalı! (Türkçe karakter kullan)");

    if (value == "true") 
        throw GumusException("syntax_error", line, "❌ 'true' değil, 'doğru' yazılmalı! (Türkçe karakter kullan)");
    
    if (value == "false") 
        throw GumusException("syntax_error", line, "❌ 'false' değil, 'yanlış' yazılmalı! (Türkçe karakter kullan)");

    if (value == "if") 
        throw GumusException("syntax_error", line, "❌ 'if' değil, 'eğer' yazılmalı! (Türkçe karakter kullan)");

    if (value == "else") 
        throw GumusException("syntax_error", line, "❌ 'else' değil, 'değilse' yazılmalı! (Türkçe karakter kullan)");

    if (value == "while" || value == "for" || value == "loop") 
        throw GumusException("syntax_error", line, "❌ Döngüler için 'döngü' veya 'her' yazılmalı! (Türkçe karakter kullan)");

    if (value == "function" || value == "func") 
        throw GumusException("syntax_error", line, "❌ 'function' değil, 'fonksiyon' yazılmalı! (Türkçe karakter kullan)");

    if (value == "return") 
        throw GumusException("syntax_error", line, "❌ 'return' değil, 'dön' yazılmalı! (Türkçe karakter kullan)");
    
    if (value == "print") 
        throw GumusException("syntax_error", line, "❌ 'print' değil, 'yazdır' yazılmalı! (Türkçe karakter kullan)");

    if (value == "degisken") 
        throw GumusException("syntax_error", line, "❌ 'degisken' değil, 'değişken' yazılmalı! (Türkçe karakter kullan)");
    if (value == "yazdir") 
        throw GumusException("syntax_error", line, "❌ 'yazdir' değil, 'yazdır' yazılmalı! (Türkçe karakter kullan)");
    if (value == "eger") 
        throw GumusException("syntax_error", line, "❌ 'eger' değil, 'eğer' yazılmalı! (Türkçe karakter kullan)");
    if (value == "degilse") 
        throw GumusException("syntax_error", line, "❌ 'degilse' değil, 'değilse' yazılmalı! (Türkçe karakter kullan)");
    if (value == "dongu") 
        throw GumusException("syntax_error", line, "❌ 'dongu' değil, 'döngü' yazılmalı! (Türkçe karakter kullan)");
    if (value == "don") 
        throw GumusException("syntax_error", line, "❌ 'don' değil, 'dön' yazılmalı! (Türkçe karakter kullan)");
    if (value == "sinif") 
        throw GumusException("syntax_error", line, "❌ 'sinif' değil, 'sınıf' yazılmalı! (Türkçe karakter kullan)");
    if (value == "modul") 
        throw GumusException("syntax_error", line, "❌ 'modul' değil, 'modül' yazılmalı! (Türkçe karakter kullan)");
    if (value == "oz") 
        throw GumusException("syntax_error", line, "❌ 'oz' değil, 'öz' yazılmalı! (Türkçe karakter kullan)");
    if (value == "dogru") 
        throw GumusException("syntax_error", line, "❌ 'dogru' değil, 'doğru' yazılmalı! (Türkçe karakter kullan)");
    if (value == "yanlis") 
        throw GumusException("syntax_error", line, "❌ 'yanlis' değil, 'yanlış' yazılmalı! (Türkçe karakter kullan)");
    if (value == "kir") 
        throw GumusException("syntax_error", line, "❌ 'kir' değil, 'kır' yazılmalı! (Türkçe karakter kullan)");

    return {TokenType::IDENTIFIER, value, line, startColumn};
}

