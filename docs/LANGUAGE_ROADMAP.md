# 🚀 GÜMÜŞDİL - Dil Geliştirme Planı

## 📊 Mevcut Durum Analizi

### ✅ Var Olan Özellikler
- ✅ Değişkenler (`değişken`)
- ✅ Fonksiyonlar (`fonksiyon`, `dön`)
- ✅ Sınıflar (`sınıf`, `kurucu`, `öz`)
- ✅ Kontrol Yapıları (`eğer`, `değilse`, `döngü`)
- ✅ Döngü Kontrolleri (`kır`, `devam`)
- ✅ Hata Yönetimi (`deneme`, `yakala`)
- ✅ Veri Tipleri (sayı, metin, liste, boolean)
- ✅ Operatörler (+, -, *, /, ==, !=, <, >, <=, >=, ve, veya, !)
- ✅ Modül Sistemi (`modul`)
- ✅ Miras (`ata`)
- ✅ Native Fonksiyonlar (yazdır, girdi, sayı, metin, uzunluk, ekle, vb.)

### ❌ Eksik/Geliştirilmesi Gereken Özellikler

#### 1. **Modern Syntax Özellikleri**
- [ ] **Arrow Functions** (Ok Fonksiyonları)
  ```gümüşdil
  değişken topla = (a, b) => a + b
  değişken kare = x => x * x
  ```

- [ ] **Template Strings** (Şablon Metinler)
  ```gümüşdil
  değişken isim = "Ahmet"
  yazdır(`Merhaba ${isim}, yaşın ${yaş}`)
  ```

- [ ] **Destructuring** (Yapı Bozma)
  ```gümüşdil
  değişken [a, b, c] = [1, 2, 3]
  değişken {isim, yaş} = kişi
  ```

- [ ] **Spread Operator** (Yayma Operatörü)
  ```gümüşdil
  değişken liste1 = [1, 2, 3]
  değişken liste2 = [...liste1, 4, 5]
  ```

- [ ] **Default Parameters** (Varsayılan Parametreler)
  ```gümüşdil
  fonksiyon selamla(isim = "Misafir") {
      yazdır("Merhaba " + isim)
  }
  ```

#### 2. **Gelişmiş Veri Yapıları**
- [ ] **Dictionary/Map** (Sözlük)
  ```gümüşdil
  değişken kişi = {
      "isim": "Ahmet",
      "yaş": 25,
      "şehir": "İstanbul"
  }
  ```

- [ ] **Set** (Küme)
  ```gümüşdil
  değişken sayılar = küme(1, 2, 3, 4, 5)
  ```

- [ ] **Tuple** (Demet)
  ```gümüşdil
  değişken konum = (41.0082, 28.9784)  // İstanbul koordinatları
  ```

#### 3. **Fonksiyonel Programlama**
- [ ] **Map, Filter, Reduce**
  ```gümüşdil
  değişken sayılar = [1, 2, 3, 4, 5]
  değişken kareler = sayılar.map(x => x * x)
  değişken çiftler = sayılar.filter(x => x % 2 == 0)
  değişken toplam = sayılar.reduce((a, b) => a + b, 0)
  ```

- [ ] **Higher-Order Functions** (Yüksek Seviye Fonksiyonlar)
  ```gümüşdil
  fonksiyon uygula(fn, değer) {
      dön fn(değer)
  }
  ```

#### 4. **Asenkron Programlama**
- [ ] **Async/Await**
  ```gümüşdil
  asenkron fonksiyon veriAl() {
      değişken sonuç = bekle http.get("api.com/data")
      dön sonuç
  }
  ```

- [ ] **Promise/Söz**
  ```gümüşdil
  değişken söz = Söz((çöz, reddet) => {
      // İşlem
      çöz(sonuç)
  })
  ```

#### 5. **Tip Sistemi (Opsiyonel)**
- [ ] **Type Annotations** (Tip Belirteçleri)
  ```gümüşdil
  fonksiyon topla(a: sayı, b: sayı): sayı {
      dön a + b
  }
  
  değişken isim: metin = "Ahmet"
  değişken yaş: sayı = 25
  ```

- [ ] **Interfaces** (Arayüzler)
  ```gümüşdil
  arayüz Kişi {
      isim: metin
      yaş: sayı
      selamla(): metin
  }
  ```

#### 6. **Pattern Matching** (Desen Eşleştirme)
```gümüşdil
değişken sonuç = eşleştir(değer) {
    1 => "Bir",
    2 => "İki",
    3 => "Üç",
    _ => "Diğer"
}
```

#### 7. **Enum (Numaralandırma)**
```gümüşdil
enum Renk {
    KIRMIZI,
    YEŞİL,
    MAVİ
}

değişken favori = Renk.MAVİ
```

#### 8. **Gelişmiş Hata Yönetimi**
- [ ] **Custom Exceptions** (Özel Hatalar)
  ```gümüşdil
  sınıf ÖzelHata < Hata {
      kurucu(mesaj) {
          öz.mesaj = mesaj
      }
  }
  
  fırlat ÖzelHata("Bir şeyler yanlış gitti!")
  ```

- [ ] **Finally Block**
  ```gümüşdil
  deneme {
      // Kod
  } yakala (hata) {
      // Hata yönetimi
  } sonunda {
      // Her durumda çalışır
  }
  ```

#### 9. **Operatör Aşırı Yükleme**
```gümüşdil
sınıf Vektör {
    kurucu(x, y) {
        öz.x = x
        öz.y = y
    }
    
    operatör +(diğer) {
        dön Vektör(öz.x + diğer.x, öz.y + diğer.y)
    }
}
```

#### 10. **Decorator/Süsleyici**
```gümüşdil
@zamanla
fonksiyon yavaşFonksiyon() {
    // Kod
}

@önbellek
fonksiyon hesapla(n) {
    // Kod
}
```

---

## 🎯 Öncelikli Geliştirme Listesi

### **Faz 1: Temel Syntax İyileştirmeleri** (1-2 Hafta)
1. ✅ Template Strings (En çok kullanılacak)
2. ✅ Arrow Functions (Modern syntax)
3. ✅ Default Parameters (Kullanışlı)
4. ✅ Dictionary/Map (Çok gerekli)

### **Faz 2: Fonksiyonel Programlama** (1 Hafta)
1. ✅ Map, Filter, Reduce
2. ✅ Higher-Order Functions
3. ✅ Lambda Expressions

### **Faz 3: Gelişmiş Özellikler** (2-3 Hafta)
1. ✅ Pattern Matching
2. ✅ Enum
3. ✅ Spread Operator
4. ✅ Destructuring

### **Faz 4: Tip Sistemi (Opsiyonel)** (2 Hafta)
1. ⏳ Type Annotations
2. ⏳ Type Checking
3. ⏳ Interfaces

### **Faz 5: Asenkron Programlama** (2-3 Hafta)
1. ⏳ Async/Await
2. ⏳ Promise/Söz
3. ⏳ Event Loop

---

## 🛠️ Teknik Implementasyon Planı

### **1. Template Strings**
**Lexer Değişiklikleri:**
- Backtick (`) karakterini tanı
- `${}` içindeki ifadeleri parse et

**Parser Değişiklikleri:**
- `TemplateStringExpr` AST node'u ekle
- İçerideki ifadeleri parse et

**Interpreter Değişiklikleri:**
- Template string'i evaluate et
- İçerideki ifadeleri çalıştır ve birleştir

**Örnek Kod:**
```cpp
// lexer.cpp
if (current == '`') {
    return scanTemplateString();
}

// parser.cpp
Expr* Parser::parseTemplateString() {
    // Parse template parts and expressions
}

// interpreter.cpp
Value Interpreter::visitTemplateStringExpr(TemplateStringExpr* expr) {
    // Evaluate and concatenate
}
```

### **2. Arrow Functions**
**Lexer Değişiklikleri:**
- `=>` operatörünü tanı

**Parser Değişiklikleri:**
- `ArrowFunctionExpr` AST node'u ekle
- Parametreleri ve body'yi parse et

**Interpreter Değişiklikleri:**
- Arrow function'ı closure olarak sakla
- Çağrıldığında evaluate et

### **3. Dictionary/Map**
**Lexer Değişiklikleri:**
- Zaten var (`{`, `}`, `:`)

**Parser Değişiklikleri:**
- `DictionaryExpr` AST node'u ekle
- Key-value pair'leri parse et

**Interpreter Değişiklikleri:**
- `std::unordered_map` kullan
- Get/Set operasyonları

### **4. Map, Filter, Reduce**
**Native Functions:**
```cpp
// native_functions.cpp
Value nativeMap(const std::vector<Value>& args) {
    // Implement map
}

Value nativeFilter(const std::vector<Value>& args) {
    // Implement filter
}

Value nativeReduce(const std::vector<Value>& args) {
    // Implement reduce
}
```

---

## 📝 Örnek Kullanım Senaryoları

### **Senaryo 1: Modern Web API**
```gümüşdil
// Template strings ve arrow functions
değişken kullanıcılar = [
    {isim: "Ahmet", yaş: 25},
    {isim: "Ayşe", yaş: 30},
    {isim: "Mehmet", yaş: 22}
]

// Filter ve map kullanımı
değişken yetişkinler = kullanıcılar
    .filter(k => k.yaş >= 25)
    .map(k => `${k.isim} (${k.yaş} yaşında)`)

yetişkinler.forEach(k => yazdır(k))
```

### **Senaryo 2: Veri İşleme**
```gümüşdil
// Dictionary kullanımı
değişken öğrenci = {
    isim: "Ali",
    notlar: [85, 90, 78, 92],
    sınıf: "10-A"
}

// Destructuring
değişken {isim, notlar} = öğrenci

// Reduce ile ortalama
değişken ortalama = notlar.reduce((toplam, not) => toplam + not, 0) / notlar.length

yazdır(`${isim}'nin ortalaması: ${ortalama}`)
```

### **Senaryo 3: Pattern Matching**
```gümüşdil
fonksiyon işlemYap(komut, değer) {
    dön eşleştir(komut) {
        "topla" => değer + 10,
        "çarp" => değer * 2,
        "kare" => değer * değer,
        _ => değer
    }
}
```

---

## 🎨 Syntax Tasarım Kararları

### **Türkçe vs İngilizce**
- **Temel Anahtar Kelimeler:** Türkçe (değişken, fonksiyon, sınıf)
- **Modern Özellikler:** Türkçe (eşleştir, bekle, asenkron)
- **Operatörler:** Evrensel (=>, ->, ...)

### **Tutarlılık**
- Tüm yeni özellikler mevcut syntax ile uyumlu olmalı
- Türkçe karakter desteği korunmalı
- Geriye dönük uyumluluk sağlanmalı

---

## 🚀 Başlangıç Noktası

**Hangi özellikle başlamalıyız?**

1. **Template Strings** - En çok kullanılacak, kolay implement
2. **Dictionary/Map** - Çok gerekli, orta zorluk
3. **Arrow Functions** - Modern syntax, orta zorluk
4. **Map/Filter/Reduce** - Fonksiyonel programlama, kolay

**Öneri:** Template Strings ile başlayalım! 🎯

