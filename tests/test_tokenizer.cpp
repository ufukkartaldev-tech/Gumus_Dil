#include <gtest/gtest.h>
#include "../src/compiler/lexer/tokenizer.h"
#include <vector>

class TokenizerTest : public ::testing::Test {
protected:
    void SetUp() override {}
    void TearDown() override {}
    
    std::vector<Token> tokenize(const std::string& source) {
        Tokenizer tokenizer(source);
        return tokenizer.tokenize();
    }
};

// 🇹🇷 Türkçe Anahtar Kelimeler Testi
TEST_F(TokenizerTest, TurkishKeywords) {
    auto tokens = tokenize("yazdır eğer değişken döngü fonksiyon");
    
    ASSERT_EQ(tokens.size(), 6); // 5 keywords + EOF
    
    EXPECT_EQ(tokens[0].type, TokenType::KW_YAZDIR);
    EXPECT_EQ(tokens[0].value, "yazdır");
    EXPECT_EQ(tokens[0].line, 1);
    
    EXPECT_EQ(tokens[1].type, TokenType::KW_EGER);
    EXPECT_EQ(tokens[1].value, "eğer");
    
    EXPECT_EQ(tokens[2].type, TokenType::KW_VAR);
    EXPECT_EQ(tokens[2].value, "değişken");
    
    EXPECT_EQ(tokens[3].type, TokenType::KW_DONGU);
    EXPECT_EQ(tokens[3].value, "döngü");
    
    EXPECT_EQ(tokens[4].type, TokenType::KW_FONKSIYON);
    EXPECT_EQ(tokens[4].value, "fonksiyon");
    
    EXPECT_EQ(tokens[5].type, TokenType::END_OF_FILE);
}

// 🎯 String ve Sayı Testleri
TEST_F(TokenizerTest, StringAndNumbers) {
    auto tokens = tokenize("yazdır(\"Merhaba Dünya\") sayi = 42");
    
    ASSERT_EQ(tokens.size(), 7);
    
    EXPECT_EQ(tokens[0].type, TokenType::KW_YAZDIR);
    EXPECT_EQ(tokens[1].type, TokenType::LPAREN);
    EXPECT_EQ(tokens[2].type, TokenType::STRING);
    EXPECT_EQ(tokens[2].value, "Merhaba Dünya");
    EXPECT_EQ(tokens[3].type, TokenType::RPAREN);
    EXPECT_EQ(tokens[4].type, TokenType::IDENTIFIER);
    EXPECT_EQ(tokens[4].value, "sayi");
    EXPECT_EQ(tokens[5].type, TokenType::EQUAL);
    EXPECT_EQ(tokens[6].type, TokenType::INTEGER);
    EXPECT_EQ(tokens[6].value, "42");
}

// 🌍 UTF-8 Karakter Testi
TEST_F(TokenizerTest, UTF8Characters) {
    auto tokens = tokenize("değişken mesaj = \"ğüşıöçĞÜŞİÖÇ\"");
    
    ASSERT_EQ(tokens.size(), 5);
    
    EXPECT_EQ(tokens[0].type, TokenType::KW_VAR);
    EXPECT_EQ(tokens[0].value, "değişken");
    
    EXPECT_EQ(tokens[1].type, TokenType::IDENTIFIER);
    EXPECT_EQ(tokens[1].value, "mesaj");
    
    EXPECT_EQ(tokens[3].type, TokenType::STRING);
    EXPECT_EQ(tokens[3].value, "ğüşıöçĞÜŞİÖÇ");
}

// ❌ Hata Durumları Testi
TEST_F(TokenizerTest, InvalidCharacter) {
    EXPECT_THROW(
        tokenize("yazdır('single quotes')"),
        GumusException
    );
}

TEST_F(TokenizerTest, UnclosedString) {
    EXPECT_THROW(
        tokenize("yazdır(\"unclosed string)"),
        GumusException
    );
}

// 🔢 Operatör Testi
TEST_F(TokenizerTest, Operators) {
    auto tokens = tokenize("a + b * c / d == e != f <= g >= h");
    
    // Token değerlerini kontrol et
    std::vector<TokenType> expected_types = {
        TokenType::IDENTIFIER, TokenType::PLUS, TokenType::IDENTIFIER,
        TokenType::MULTIPLY, TokenType::IDENTIFIER, TokenType::DIVIDE,
        TokenType::IDENTIFIER, TokenType::EQUAL_EQUAL, TokenType::IDENTIFIER,
        TokenType::BANG_EQUAL, TokenType::IDENTIFIER, TokenType::LESS_EQUAL,
        TokenType::IDENTIFIER, TokenType::GREATER_EQUAL, TokenType::IDENTIFIER,
        TokenType::END_OF_FILE
    };
    
    ASSERT_EQ(tokens.size(), expected_types.size());
    
    for (size_t i = 0; i < expected_types.size(); i++) {
        EXPECT_EQ(tokens[i].type, expected_types[i]) 
            << "Token at position " << i << " has wrong type";
    }
}

// 📝 Template String Testi
TEST_F(TokenizerTest, TemplateStrings) {
    auto tokens = tokenize("yazdır($\"Merhaba {isim}!\")");
    
    ASSERT_GE(tokens.size(), 6);
    
    EXPECT_EQ(tokens[0].type, TokenType::KW_YAZDIR);
    EXPECT_EQ(tokens[1].type, TokenType::LPAREN);
    
    // Template string parçaları
    EXPECT_EQ(tokens[2].type, TokenType::STRING);
    EXPECT_EQ(tokens[2].value, ""); // Başlangıç boş string
    
    EXPECT_EQ(tokens[3].type, TokenType::PLUS);
    EXPECT_EQ(tokens[4].type, TokenType::STRING);
    EXPECT_EQ(tokens[4].value, "Merhaba ");
    
    // Değişken ve devamı
    EXPECT_EQ(tokens[5].type, TokenType::PLUS);
}

// 🎯 Line ve Column Tracking Testi
TEST_F(TokenizerTest, LineAndColumnTracking) {
    auto tokens = tokenize("yazdır(\"satır 1\")\nyazdır(\"satır 2\")");
    
    // İlk satır
    EXPECT_EQ(tokens[0].line, 1);
    EXPECT_EQ(tokens[0].column, 1);
    
    // İkinci satır (NEW_LINE token'ı)
    EXPECT_EQ(tokens[4].line, 1);
    EXPECT_EQ(tokens[5].line, 2);
    EXPECT_EQ(tokens[5].column, 1);
}

// 🔍 Escape Sequences Testi
TEST_F(TokenizerTest, EscapeSequences) {
    auto tokens = tokenize("yazdır(\"Merhaba\\nDünya\\t!\")");
    
    ASSERT_EQ(tokens.size(), 4);
    
    EXPECT_EQ(tokens[2].type, TokenType::STRING);
    EXPECT_EQ(tokens[2].value, "Merhaba\nDünya\t!");
}

// 🚫 Edge Case Testleri
TEST_F(TokenizerTest, EmptySource) {
    auto tokens = tokenize("");
    
    ASSERT_EQ(tokens.size(), 1);
    EXPECT_EQ(tokens[0].type, TokenType::END_OF_FILE);
}

TEST_F(TokenizerTest, WhitespaceOnly) {
    auto tokens = tokenize("   \n\t  \n  ");
    
    ASSERT_EQ(tokens.size(), 1);
    EXPECT_EQ(tokens[0].type, TokenType::END_OF_FILE);
}

TEST_F(TokenizerTest, IdentifiersWithNumbers) {
    auto tokens = tokenize("degisken123 _private __magic");
    
    ASSERT_EQ(tokens.size(), 4);
    
    EXPECT_EQ(tokens[0].type, TokenType::IDENTIFIER);
    EXPECT_EQ(tokens[0].value, "degisken123");
    
    EXPECT_EQ(tokens[1].type, TokenType::IDENTIFIER);
    EXPECT_EQ(tokens[1].value, "_private");
    
    EXPECT_EQ(tokens[2].type, TokenType::IDENTIFIER);
    EXPECT_EQ(tokens[2].value, "__magic");
}

// 🧪 Main Test Runner
int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
