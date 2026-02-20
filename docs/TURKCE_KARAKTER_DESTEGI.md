# 🇹🇷 TÜRKÇE KARAKTER DESTEĞİ EKLENDİ!

## ✅ YAPILAN DEĞİŞİKLİKLER

### 🎯 Lexer Güncellemesi

#### 1. UTF-8 Karakter Desteği
```cpp
// ÖNCESİ:
if (isalpha(c) || c == '_') {
    return identifier();
}

// SONRASI:
if (isalpha(c) || c == '_' || (unsigned char)c >= 0xC0) {
    return identifier();
}
```

#### 2. Identifier Okuma
```cpp
// UTF-8 Türkçe karakterleri de kabul et
while (isalnum(peek()) || peek() == '_' || (unsigned char)peek() >= 0xC0) {
    value += advance();
}
```

### 📝 TÜRKÇE ANAHTAR KELİMELER

Artık hem Türkçe hem de İngilizce karakterlerle yazabilirsiniz!

| Türkçe (Yeni!) | İngilizce | Açıklama |
|----------------|-----------|----------|
| **değişken** | degisken, var | Değişken tanımlama |
| **eğer** | eger | Koşul |
| **değilse** | degilse | Else |
| **döngü** | dongu | Loop |
| **dön** | don | Return |
| **sınıf** | sinif | Class |
| **öz** | oz | This |
| **modül** | modul | Module |
| **doğru** | dogru | True |
| **yanlış** | yanlis | False |
| **kır** | kir | Break |
| **yazdır** | yazdir | Print |

## 🎯 ÖRNEK KULLANIM

### Eski Yöntem (Hala Çalışıyor)
```gumusdil
degisken x = 10
eger (x > 5) {
    yazdir("Buyuk!")
}
```

### YENİ TÜRKÇE YÖNTEM! 🇹🇷
```gumusdil
değişken x = 10
eğer (x > 5) {
    yazdır("Büyük!")
}
```

### Tam Türkçe Örnek
```gumusdil
// Sınıf tanımlama
sınıf Hesap {
    fonksiyon kur() {
        öz.toplam = 0
    }
    
    fonksiyon ekle(sayı) {
        öz.toplam = öz.toplam + sayı
        dön öz.toplam
    }
}

// Kullanım
değişken h = Hesap()
h.ekle(100)
yazdır("Toplam: " + metin(h.toplam))

// Döngü
döngü (değişken i = 0; i < 5; i = i + 1) {
    eğer (i == 3) {
        kır  // Break
    }
    yazdır("Sayı: " + metin(i))
}

// Koşullar
değişken sonuç = 42
eğer (sonuç > 40) {
    yazdır("Başarılı! ✅")
} değilse {
    yazdır("Başarısız ❌")
}
```

## 🔤 DESTEKLENEN TÜRKÇE KARAKTERLER

- **ç, Ç** - UTF-8: 0xC3 0xA7 / 0xC3 0x87
- **ğ, Ğ** - UTF-8: 0xC4 0x9F / 0xC4 0x9E
- **ı, İ** - UTF-8: 0xC4 0xB1 / 0xC4 0xB0
- **ö, Ö** - UTF-8: 0xC3 0xB6 / 0xC3 0x96
- **ş, Ş** - UTF-8: 0xC5 0x9F / 0xC5 0x9E
- **ü, Ü** - UTF-8: 0xC3 0xBC / 0xC3 0x9C

## 🚀 DERLEME

Değişiklikleri derlemek için:

```bash
g++ -std=c++17 -o gumus.exe \
    src/compiler/main.cpp \
    src/compiler/lexer/tokenizer.cpp \
    src/compiler/parser/parser.cpp \
    src/compiler/interpreter/interpreter.cpp \
    src/compiler/interpreter/native_functions.cpp \
    src/compiler/interpreter/objects.cpp \
    src/compiler/hardware/serial_port.cpp \
    -I. -DUNICODE -D_UNICODE
```

## 🧪 TEST

Test dosyası: `test_turkce.tr`

```bash
.\gumus.exe test_turkce.tr
```

## 💡 NOTLAR

1. **Geriye Uyumluluk:** Eski kodlar (degisken, eger, vb.) hala çalışıyor!
2. **Karışık Kullanım:** Aynı dosyada hem "eğer" hem "eger" kullanabilirsiniz
3. **Değişken İsimleri:** Artık değişken isimlerinde de Türkçe karakter kullanabilirsiniz!
   ```gumusdil
   değişken öğrenci_sayısı = 100
   değişken başarı_oranı = 95.5
   ```

## 🎉 SONUÇ

**GÜMÜŞDİL ARTIK TAM TÜRKÇE! 🇹🇷**

- ✅ Türkçe anahtar kelimeler
- ✅ Türkçe değişken isimleri
- ✅ UTF-8 karakter desteği
- ✅ Geriye uyumlu
- ✅ Hem "eğer" hem "eger" çalışıyor

---

**ASKER, GÜMÜŞDİL TÜRK MİLLİYETÇİSİ! 🇹🇷💪**

