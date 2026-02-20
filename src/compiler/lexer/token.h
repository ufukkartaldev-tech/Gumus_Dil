#ifndef GUMUS_LEXER_TOKEN_H
#define GUMUS_LEXER_TOKEN_H

#include <string>
#include <iostream>

enum class TokenType {
    INTEGER,
    PLUS,
    MINUS,
    MULTIPLY,
    DIVIDE,
    MOD,
    
    IDENTIFIER,
    EQUAL,      // =
    SEMICOLON,  // ;
    KW_YAZDIR,  // yazdir (keyword)
    KW_VAR,     // degisken

    KW_EGER,    // eger
    KW_DEGILSE, // degilse
    KW_DONGU,   // dongu
    KW_DOGRU,   // dogru
    KW_YANLIS,  // yanlis
    KW_DENEME,  // deneme (try)
    KW_YAKALA,  // yakala (catch)

    KW_FONKSIYON, // fonksiyon
    KW_DON,       // don (return)
    KW_KURUCU,    // kurucu (constructor)
    KW_HER,       // her (foreach)
    KW_KIR,       // kir (break)
    KW_DEVAM,     // devam (continue)
    KW_ATA,       // ata (super)
    KW_YENI,      // yeni (new)
    
    COLON,        // :
    COMMA,        // ,
    
    STRING,       // "metin"
    LBRACKET,     // [
    RBRACKET,     // ]

    LBRACE,     // {
    RBRACE,     // }

    KW_SINIF,   // sinif
    KW_OZ,      // öz (this)
    KW_MODUL,   // modul (module)
    DOT,        // .
    COLON_COLON, // :: (Scope Resolution)
    
    EQUAL_EQUAL,   // ==
    BANG_EQUAL,    // !=
    LESS,          // <
    LESS_EQUAL,    // <=
    GREATER,       // >
    GREATER_EQUAL, // >=

    BANG,          // !
    
    LOGIC_AND,     // ve
    LOGIC_OR,      // veya

    LPAREN, // (
    RPAREN, // )

    KW_BOS,   // bos (null)

    NEW_LINE, // \n (Satir sonu)
    END_OF_FILE,
    UNKNOWN
};



struct Token {
    TokenType type;
    std::string value;
    int line;
    int column;

    std::string toString() const {
        switch (type) {
            case TokenType::INTEGER: return "INTEGER(" + value + ")";
            case TokenType::PLUS: return "PLUS";
            case TokenType::MINUS: return "MINUS";
            case TokenType::MULTIPLY: return "MULTIPLY";
            case TokenType::DIVIDE: return "DIVIDE";
            case TokenType::LPAREN: return "LPAREN";
            case TokenType::RPAREN: return "RPAREN";
            case TokenType::IDENTIFIER: return "IDENTIFIER(" + value + ")";
            case TokenType::EQUAL: return "EQUAL";
            case TokenType::SEMICOLON: return "SEMICOLON";
            case TokenType::KW_YAZDIR: return "KW_YAZDIR";
            case TokenType::KW_VAR: return "KW_VAR";
            
            case TokenType::KW_EGER: return "KW_EGER";
            case TokenType::KW_DEGILSE: return "KW_DEGILSE";
            case TokenType::KW_DONGU: return "KW_DONGU";
            case TokenType::KW_DOGRU: return "KW_DOGRU";
            case TokenType::KW_YANLIS: return "KW_YANLIS";
            case TokenType::KW_DENEME: return "KW_DENEME";
            case TokenType::KW_YAKALA: return "KW_YAKALA";

            case TokenType::KW_FONKSIYON: return "KW_FONKSIYON";
            case TokenType::KW_DON: return "KW_DON";
            case TokenType::KW_KIR: return "KW_KIR";
            case TokenType::KW_DEVAM: return "KW_DEVAM";
            case TokenType::KW_ATA: return "KW_ATA";
            case TokenType::KW_YENI: return "KW_YENI";
            case TokenType::COMMA: return "COMMA";
            case TokenType::STRING: return "STRING(" + value + ")";
            case TokenType::LBRACKET: return "LBRACKET";
            case TokenType::RBRACKET: return "RBRACKET";
            case TokenType::LBRACE: return "LBRACE";
            case TokenType::RBRACE: return "RBRACE";
            case TokenType::KW_SINIF: return "KW_SINIF";
            case TokenType::KW_OZ: return "KW_OZ";
            case TokenType::KW_MODUL: return "KW_MODUL";
            case TokenType::DOT: return "DOT";
            case TokenType::COLON_COLON: return "COLON_COLON";
            case TokenType::EQUAL_EQUAL: return "EQUAL_EQUAL";
            case TokenType::BANG_EQUAL: return "BANG_EQUAL";
            case TokenType::LESS: return "LESS";
            case TokenType::LESS_EQUAL: return "LESS_EQUAL";
            case TokenType::GREATER: return "GREATER";
            case TokenType::GREATER_EQUAL: return "GREATER_EQUAL";

            case TokenType::BANG: return "BANG";
            case TokenType::LOGIC_AND: return "LOGIC_AND";
            case TokenType::LOGIC_OR: return "LOGIC_OR";
            case TokenType::KW_BOS: return "KW_BOS";
            case TokenType::NEW_LINE: return "NEW_LINE";



            case TokenType::END_OF_FILE: return "EOF";
            case TokenType::UNKNOWN: return "UNKNOWN(" + value + ")";
            default: return "UNKNOWN";
        }
    }
};

#endif // GUMUS_LEXER_TOKEN_H
