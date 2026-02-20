# 🇹🇷 SADECE TÜRKÇE! - GÜMÜŞDİL

## ✅ ZORUNLU TÜRKÇE KARAKTERLER

GümüşDil artık **SADECE TÜRKÇE** karakterlerle çalışır!

### ❌ YANLIŞ (HATA VERİR!)

```gumusdil
degisken x = 10    // ❌ HATA!
eger (x > 5) {     // ❌ HATA!
    yazdir("Test") // ❌ HATA!
}
```

**Hata Mesajı:**
```
❌ 'eger' değil, 'eğer' yazılmalı! (Türkçe karakter kullan)
```

### ✅ DOĞRU (ÇALIŞIR!)

```gumusdil
değişken x = 10     // ✅ DOĞRU!
eğer (x > 5) {      // ✅ DOĞRU!
    yazdır("Test")  // ✅ DOĞRU!
}
```

## 📝 ZORUNLU TÜRKÇE ANAHTAR KELİMELER

| Türkçe (ZORUNLU!) | ❌ Yanlış | Açıklama |
|-------------------|-----------|----------|
| **değişken** | degisken | Değişken tanımlama |
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

## 🎯 TAM TÜRKÇE ÖRNEK

```gumusdil
// GÜMÜŞDİL - TAM TÜRKÇE! 🇹🇷

değişken öğrenci_sayısı = 100
değişken başarı_oranı = 95.5

eğer (başarı_oranı > 90) {
    yazdır("Mükemmel başarı! ✅")
} değilse {
    yazdır("Daha fazla çalışmalı ❌")
}

sınıf Öğrenci {
    fonksiyon kur(isim, yaş) {
        öz.isim = isim
        öz.yaş = yaş
    }
    
    fonksiyon bilgi_göster() {
        yazdır("İsim: " + öz.isim)
        yazdır("Yaş: " + metin(öz.yaş))
    }
}

değişken öğrenci = Öğrenci("Mehmet", 20)
öğrenci.bilgi_göster()

döngü (değişken i = 0; i < 5; i = i + 1) {
    eğer (i == 3) {
        kır  // Döngüden çık
    }
    yazdır("Sayı: " + metin(i))
}
```

## 🚀 DERLEME

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

### Doğru Kullanım
```bash
.\gumus.exe test_dogru_turkce.tr
```
**Sonuç:** ✅ Çalışır!

### Yanlış Kullanım
```bash
.\gumus.exe test_yanlis.tr
```
**Sonuç:** ❌ Hata verir!
```
❌ 'eger' değil, 'eğer' yazılmalı! (Türkçe karakter kullan)
```

## 💪 NEDEN SADECE TÜRKÇE?

1. **Dil Saflığı** - Tam Türkçe bir programlama dili
2. **Eğitim** - Öğrenciler Türkçe karakterleri öğrenir
3. **Milliyetçilik** - Türk dilini korumak ve yaşatmak
4. **Standart** - Herkes aynı şekilde yazar

## 🇹🇷 SONUÇ

**GÜMÜŞDİL = %100 TÜRKÇE!**

- ❌ "eger" → HATA!
- ✅ "eğer" → ÇALIŞIR!

- ❌ "degisken" → HATA!
- ✅ "değişken" → ÇALIŞIR!

- ❌ "sinif" → HATA!
- ✅ "sınıf" → ÇALIŞIR!

---

**ASKER, GÜMÜŞDİL TÜRK MİLLİYETÇİSİ! 🇹🇷💪**

**TÜRKÇE KARAKTER KULLANMAK ZORUNLU!**

