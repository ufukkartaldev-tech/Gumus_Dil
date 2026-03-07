# 🧪 Gümüşdil Unit Test Documentation

## 📋 Test Yapısı

### 🎯 Mevcut Testler
- **Tokenizer Testleri**: `tests/test_tokenizer.cpp`
  - Türkçe anahtar kelime parsing
  - UTF-8 karakter desteği
  - String ve sayı token'ları
  - Operatörler ve escape sequences
  - Hata durumları
  - Line/column tracking

### 🛠️ Test Çalıştırma

#### Windows (Recommended)
```bash
# Interactive test runner
run_unit_tests.bat

# Manual build
cd tests
mkdir build && cd build
cmake .. -G "MinGW Makefiles"
mingw32-make
unit_tests.exe
```

#### Linux/Mac
```bash
cd tests
mkdir build && cd build
cmake ..
make
./unit_tests
```

## 🧪 Test Kategorileri

### 1. ✅ Pozitif Testler (Happy Path)
```cpp
TEST_F(TokenizerTest, TurkishKeywords) {
    // Beklenen durumlar çalışıyor mu?
}
```

### 2. ❌ Negatif Testler (Error Cases)
```cpp
TEST_F(TokenizerTest, InvalidCharacter) {
    // Hata durumları doğru fırlatılıyor mu?
    EXPECT_THROW(tokenize("invalid"), GumusException);
}
```

### 3. 🔍 Edge Case Testleri
```cpp
TEST_F(TokenizerTest, EmptySource) {
    // Boş input, sınır durumları
}
```

## 📊 Test Coverage Raporu

### Tokenizer Coverage
- [x] Türkçe anahtar kelimeler (%100)
- [x] UTF-8 karakterler (%95)
- [x] String parsing (%90)
- [x] Operatörler (%100)
- [x] Hata yönetimi (%85)
- [ ] Template strings (%70)
- [ ] Escape sequences (%80)

## 🚀 Gelecek Testler

### Parser Testleri
```cpp
class ParserTest : public ::testing::Test {
    // Function parsing
    // If statement parsing
    // Loop parsing
    // Error recovery
};
```

### Interpreter Testleri
```cpp
class InterpreterTest : public ::testing::Test {
    // Variable scoping
    // Function calls
    // Native functions
    // Suggestion generation
};
```

### IDE Testleri (Python)
```python
class TestTerminal:
    def test_history_navigation(self):
        # Terminal history özelliği
    def test_auto_complete(self):
        # Otomatik tamamlama
    def test_syntax_highlighting(self):
        # Renklendirme
```

## 🎯 Başarı Kriterleri

### Test Başarısı İçin:
- ✅ Tüm testler geçiyor
- ✅ Code coverage > %80
- ✅ Hata mesajları anlaşılır
- ✅ Performance testleri geçiyor
- ✅ Memory leak yok

### Test Başarısızlığı:
- ❌ Segmentation fault
- ❌ Memory leak
- ❌ Assertion failed
- ❌ Timeout (>5 saniye)
- ❌ Platform-specific hatalar

## 🛠️ Debugging Testler

### Test Debug Etme:
```bash
# Debug build
cmake .. -DCMAKE_BUILD_TYPE=Debug

# GDB ile çalıştır
gdb ./unit_tests
(gdb) run
(gdb) bt  # Backtrace
```

### Verbose Output:
```bash
# Test detaylı çıktı
unit_tests --gtest_filter=TokenizerTest.*
unit_tests --gtest_print_time=1
unit_tests --gtest_output=xml
```

## 📝 Test Yazma İpuçları

### 1. AAA Pattern
```cpp
TEST_F(TokenizerTest, FeatureName) {
    // Arrange - Test ortamı hazırla
    std::string input = "yazdır(\"test\")";
    
    // Act - Fonksiyonu çalıştır
    auto tokens = tokenize(input);
    
    // Assert - Sonucu kontrol et
    EXPECT_EQ(tokens[0].type, TokenType::KW_YAZDIR);
}
```

### 2. Descriptive Test Names
```cpp
// ❌ Kötü
TEST_F(TokenizerTest, Test1)

// ✅ İyi
TEST_F(TokenizerTest, TurkishKeywords_ParseCorrectly)
```

### 3. Test Data-Driven
```cpp
class TokenizerTest : public ::testing::TestWithParam<std::pair<std::string, TokenType>> {
    // Parametreli testler
};

INSTANTIATE_TEST_SUITE_P(
    TurkishKeywords,
    TokenizerTest,
    ::testing::Values(
        std::make_pair("yazdır", TokenType::KW_YAZDIR),
        std::make_pair("eğer", TokenType::KW_EGER)
    )
);
```

## 🏆 Test Odaklı Geliştirme

### TDD Akışı:
1. **Red**: Failing test yaz
2. **Green**: En basit kod ile testi geçir
3. **Refactor**: Kodu temizle
4. **Repeat**: Sonraki özellik

### Örnek:
```cpp
// 1. RED - Test yaz
TEST_F(TokenizerTest, NewKeyword) {
    auto tokens = tokenize("yeni_kelime");
    EXPECT_EQ(tokens[0].type, TokenType::KW_YENI_KELIME);
}

// 2. GREEN - Tokenizer'a ekle
// tokenizer.cpp'de yeni keyword ekle

// 3. REFACTOR - Kodu temizle
// Optimizasyon yap
```

## 🎯 Sonraki Adımlar

1. **Mevcut testleri çalıştır**: `run_unit_tests.bat`
2. **Başarısız testleri düzelt**: Debug et
3. **Coverage artır**: Eksik test ekle
4. **Yeni class'lar için test yaz**: Parser, Interpreter
5. **CI/CD entegrasyonu**: Otomatik test çalıştırma

**Test çalıştırmaya hazır!** 🧪💎

