# Gümüşdil Referans Sözlüğü 📘

Merhaba! Gümüşdil programlama diline hoş geldin. Bu sözlük, dilin temel komutlarını, fonksiyonlarını ve kullanım şekillerini öğrenmen için hazırlandı.

---

## 📄 Dosya Uzantısı
Gümüşdil dosyaları **`.tr`** uzantısı kullanır (Türkiye/Türkçe'den). 
- Örnek: `program.tr`, `hesap_makinesi.tr`

---

## 🔑 Temel Anahtar Kelimeler

| Anahtar Kelime | Açıklama | Örnek Kullanım |
| :--- | :--- | :--- |
| **`degisken`** | Yeni bir değişken tanımlar. | `degisken isim = "Ahmet"` |
| **`yazdir`** | Ekrana çıktı verir. | `yazdir("Merhaba Dünya")` |
| **`eger`** | Bir koşul doğruysa çalışır. | `eger (x > 5) { ... }` |
| **`degilse`** | `eger` koşulu yanlışsa çalışır. | `degilse { ... }` |
| **`ve`** / **`veya`** | Mantıksal bağlaçlar. | `eger (x > 0 ve x < 10)` |
| **`dongu`** | Bir koşul doğru olduğu sürece çalışır. | `dongu (sayac < 10) { ... }` |
| **`fonksiyon`** | Yeni bir fonksiyon oluşturur. | `fonksiyon topla(a, b) { ... }` |
| **`don`** | Fonksiyondan değer döndürür. | `don a + b` |
| **`dogru`** / **`yanlis`** | Mantıksal doğru ve yanlış değerleri. | `degisken acik_mi = dogru` |
| **`deneme`** / **`yakala`** | Hata yakalama blokları (Try-Catch). | `deneme { ... } yakala (e) { ... }` |

### 🔬 Deneysel Özellikler (Beta)
| Anahtar Kelime | Açıklama | Durum |
| :--- | :--- | :--- |
| **`sinif`** | Nesne yönelimli programlama için sınıf tanımlar. | ⚠️ Deneysel |
| **`ben`** | Sınıf içinde o anki nesneyi ifade eder. | ⚠️ Deneysel |
| **`kurucu`** | Sınıf oluşturulurken otomatik çalışan özel fonksiyon. | ⚠️ Deneysel |

> **Not:** OOP özellikleri (sinif, ben, kurucu) henüz tam stabil değil. Basit projeler için kullanabilirsin ama karmaşık yapılarda hata verebilir.

#### 🔧 OOP Teknik Detaylar:
- **Kurucu (Constructor):** `fonksiyon kurucu(parametreler)` şeklinde tanımlanır. Nesne oluşturulurken (`Araba("Toyota", 100)`) otomatik çalışır.
- **Bind Mekanizması:** `ben` anahtar kelimesi her metot çağrısında doğru nesneye bağlanır (satır 108-117, objects.cpp).
- **Bilinen Sorunlar:** 
  - Karmaşık miras yapıları test edilmedi
  - Property binding bazı durumlarda eksik kalabilir (satır 90, objects.cpp)
  - Performans optimizasyonu yapılmadı

#### ⚠️ Hata Yakalama Detayları:
**Hata Nesnesi İçeriği:**
- `yakala (hata)` bloğundaki `hata` değişkeni **metin (string)** tipindedir
- İçeriği: Hatanın açıklama mesajı (örn: "Sifira bolunme hatasi.")
- Kaynak: `interpreter.cpp` satır 121-126
  - `LoxRuntimeException`: `ex.errorValue` döner (özel hata nesnesi)
  - `std::runtime_error`: `ex.what()` mesajı döner (C++ hatası)

**Örnek:**
```javascript
deneme {
    degisken x = 10 / 0
} yakala (hata) {
    yazdir("Hata mesaji: " + metin(hata))  // "Sifira bolunme hatasi."
}
```

**Bilinen Sınırlama:** Şu an hata nesnesi sadece metin içerir. `hata.mesaj`, `hata.satir` gibi özellikler henüz yok.

---

## 🛠️ Yerel (Gömülü) Fonksiyonlar

Gümüşdil'in içinde hazır gelen, işini kolaylaştıracak fonksiyonlar:

### 📝 Metin ve Giriş/Çıkış
*   **`yazdir(deger)`**: Bir değeri ekrana yazar ve alt satıra geçer.
*   **`girdi()`**: Kullanıcıdan klavye ile veri almanı sağlar.
    
    > ⚠️ **ÖNEMLİ:** `girdi()` **HER ZAMAN METİN** döndürür!  
    > Sayı işlemi yapacaksan mutlaka `sayi()` ile çevir:
    > ```javascript
    > degisken yas_metin = girdi()        // "25" (metin)
    > degisken yas_sayi = sayi(girdi())   // 25 (sayı) ✅ DOĞRU
    > ```
    > Aksi halde `"5" + "10" = "510"` gibi beklenmeyen sonuçlar alırsın!

*   **`renkli_yazdir(renk, mesaj)`**: Terminale renkli yazı yazar.
    *   *Renkler:* "kirmizi", "yesil", "mavi", "sari", "mor", "turkuaz", "beyaz".

### 🔢 Sayısal İşlemler
*   **`sayi(deger)`**: Bir metni sayıya çevirir. (`"123"` → `123`)
    ```javascript
    degisken metin_sayi = "42"
    degisken gercek_sayi = sayi(metin_sayi)  // 42 (sayı)
    degisken toplam = gercek_sayi + 8        // 50 ✅
    ```
*   **`karekok(deger)`**: Bir sayının karekökünü alır.
*   **`rastgele()`**: Rastgele bir sayı üretir.

### 📋 Liste ve Metin İşlemleri
*   **`uzunluk(liste_veya_metin)`**: Bir listenin eleman sayısını veya bir metnin karakter sayısını verir.
*   **`metin(deger)`**: Herhangi bir değeri metne (string) çevirir.
*   **`ekle(liste, eleman)`**: Bir listenin sonuna yeni eleman ekler.
*   **`sil(liste, indeks)`**: Belirtilen sıradaki elemanı listeden siler.
*   **`sirala(liste)`**: Listeyi küçükten büyüğe sıralar.
*   **`ters_cevir(liste)`**: Listeyi ters çevirir.
*   **`icerir(liste, eleman)`**: Listede elemanın olup olmadığını kontrol eder (`dogru`/`yanlis`).
*   **`buyuk(metin)`**: Metni BÜYÜK HARFLERE çevirir.
*   **`kucuk(metin)`**: Metni küçük harflere çevirir.
*   **`parcala(metin, ayirici)`**: Bir metni, ayırıcıya göre bölüp liste yapar.
*   **`bul(metin_veya_liste, aranan)`**: Metin içinde alt metni veya listede elemanı arar. Bulursa indeksini, bulamazsa -1 döndürür.
*   **`kirp(metin)`**: Metnin başındaki ve sonundaki boşlukları temizler.
*   **`yer_degistir(metin, eski, yeni)`**: Metin içindeki tüm `eski` değerlerini `yeni` ile değiştirir.

### 📂 Dosya ve Sistem
*   **`dosya_oku(dosya_yolu)`**: Belirtilen dosyanın içeriğini okur.
*   **`dosya_yaz(dosya_yolu, icerik)`**: Dosyaya içerik yazar (Önceki içeriği siler).
*   **`dosya_ekle(dosya_yolu, icerik)`**: Dosyanın sonuna ekleme yapar.
*   **`dosya_varmi(dosya_yolu)`**: Dosyanın olup olmadığını kontrol eder (`dogru`/`yanlis` döner).
*   **`dahil_et(dosya_adi)`**: Başka bir Gümüşdil dosyasını (`.tr`) projene dahil eder.
    ```javascript
    dahil_et("matematik.tr")  // matematik.tr dosyasını yükler
    ```
*   **`bekle(milisaniye)`**: Programı belirtilen süre kadar durdurur.
*   **`zaman()`**: Şimdiki zamanı sayı olarak verir.
*   **`tip(deger)`**: Değerin türünü metin olarak verir ("sayi", "metin", "liste" vb.).
*   **`sistem(komut)`**: İşletim sistemi komutu çalıştırır.

---

## 💡 Örnek Kod

```javascript
// Basit bir toplama programı (DOĞRU KULLANIM)
yazdir("Birinci sayiyi gir:")
degisken sayi1 = sayi(girdi())  // ⚠️ sayi() ile çevir!

yazdir("Ikinci sayiyi gir:")
degisken sayi2 = sayi(girdi())  // ⚠️ sayi() ile çevir!

degisken toplam = sayi1 + sayi2
yazdir("Toplam: " + metin(toplam))

// Liste örneği
degisken meyveler = ["Elma", "Armut"]
ekle(meyveler, "Muz")

yazdir("Meyve Listesi (" + metin(uzunluk(meyveler)) + " adet):")
degisken i = 0
dongu (i < uzunluk(meyveler)) {
    yazdir("- " + meyveler[i])
    i = i + 1
}
```

---

## ⚠️ Sık Yapılan Hatalar

### ❌ YANLIŞ:
```javascript
degisken x = girdi()  // "5" (metin)
degisken y = girdi()  // "10" (metin)
yazdir(x + y)         // "510" ❌ (metin birleştirme)
```

### ✅ DOĞRU:
```javascript
degisken x = sayi(girdi())  // 5 (sayı)
degisken y = sayi(girdi())  // 10 (sayı)
yazdir(x + y)               // 15 ✅ (sayı toplama)
```

---

## 🚀 Performans ve Bellek Yönetimi

### Bellek Kullanımı:
- **Değişkenler:** `std::shared_ptr` ile yönetilir (akıllı işaretçi, otomatik bellek temizleme)
- **Sınıflar:** Her nesne `LoxInstance` objesi oluşturur (~100-200 byte)
- **Listeler:** `std::vector` tabanlı, dinamik büyür
- **Environment (Kapsam):** Her blok/fonksiyon yeni `Environment` oluşturur

### Performans Notları:
- ✅ **Basit programlar:** Hızlı ve verimli (< 1MB bellek)
- ⚠️ **Çok sayıda sınıf:** Bellek kullanımı artabilir (her nesne ~200 byte)
- ⚠️ **Derin fonksiyon çağrıları:** Stack overflow riski (özyineleme dikkatli kullan)
- ⚠️ **Büyük listeler:** 10,000+ elemanlı listeler yavaşlayabilir

### Öneriler:
1. **Döngülerde dikkatli ol:** Sonsuz döngü sistemi kilitler
2. **Büyük verilerle çalışma:** 1000+ elemanlı listeler için test et
3. **Özyineleme limiti:** Maksimum ~1000 seviye (stack boyutuna bağlı)
4. **Bellek sızıntısı:** `std::shared_ptr` kullanıldığı için genelde sorun yok

> **Gümüşhane Üniversitesi Bilgisayarları İçin:** Normal kullanımda sorun yok! Ama 10,000+ nesne oluşturmaya çalışma 😄

---

## ⚠️ Bilinen Sınırlamimarir ve Gelecek Planları

### Mevcut Sınırlamimarir:
1. **Namespace Yok:** İki kütüphane aynı fonksiyon adını kullanırsa çakışır
   ```javascript
   dahil_et("matematik.tr")  // topla() fonksiyonu var
   fonksiyon topla(x, y) { don x * y }  // matematik.tr'deki kaybolur!
   ```

2. **Sonsuz Döngü Koruması Yok:** 
   ```javascript
   dongu (dogru) { degisken x = 1 }  // RAM'i sömürür, koruma yok!
   ```

3. **donanim.tr Simülasyon:** Gerçek GPIO/sensor erişimi yok, sadece log basıyor

4. **Parse Hataları:** Satır numarası gösterilmiyor (geliştirilecek)

### Gelecek Planları:
- 🔄 **Bytecode VM:** .exe yerine .gbc (GümüşByte Code) formatı
- 🔄 **Module Sistemi:** Python-style import/namespace
- 🔄 **Döngü Limiti:** Maksimum 1M iterasyon koruması
- 🔄 **Gerçek GPIO:** Arduino/Raspberry Pi desteği
- 🔄 **Daha İyi Hata Mesajları:** Satır numarası + öneriler

### Teknik Detaylar:
Daha fazla bilgi için `TEKNIK_DERINLIK_RAPORU.md` dosyasına bakın.

---

*Gümüşdil (v2.1) - Tamamen Türkçe Programlama Dili!* 🚀🇹🇷


