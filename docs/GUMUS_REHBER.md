# 💎 GümüşDil Referans ve Kullanım Kılavuzu

GümüşDil, Türkçe sözdizimine sahip, modern, nesne yönelimli ve oyun geliştirme odaklı bir programlama dilidir.

---

## 1. Temel Yapı

### Yorum Satırları
```javascript
// Bu tek satırlık bir yorumdur
// Derleyici burayı görmezden gelir
```

### Değişken Tanımlama
Değişkenler dinamik tiplidir. Tür belirtmenize gerek yoktur.
```javascript
değişken isim = "Ahmet"; // String
değişken yas = 25;            // Integer
değişken oran = 3.14;    // Float
değişken aktif = doğru;  // Boolean (doğru/yanlış)
değişken bos_deger = boş;// Null
```

### Ekrana Yazdırma
```javascript
yazdır("Merhaba Dünya!");
yazdır("Yaş: " + yas);
```

---

## 2. Veri Yapıları

### Listeler (Diziler)
```javascript
değişken sayilar = [10, 20, 30];
yazdır(sayilar[0]); // 10

// Listeye ekleme yapma
ekle(sayilar, 40); 

// Listeden silme (indeks ile)
sil(sayilar, 0); // 10 silinir, [20, 30, 40] kalır

yazdır(uzunluk(sayilar)); // Listenin uzunluğu
```

### Sözlükler (Dictionary / Map)
```javascript
değişken kisi = {
    "ad": "Mehmet",
    "yas": 40,
    "admin": yanlış
};

yazdır(kisi["ad"]); // Mehmet
kisi["soyad"] = "Yılmaz"; // Yeni alan ekleme
```

---

## 3. Kontrol Yapıları

### Eğer - Değilse (If - Else)
```javascript
değişken not = 75;

eğer (not >= 50) {
    yazdır("Geçti");
} değilse eğer (not >= 40) {
    yazdır("Bütünleme");
} değilse {
    yazdır("Kaldı");
}
```

### Döngüler

**While Döngüsü:**
```javascript
değişken i = 0;
döngü (i < 5) {
    yazdır("Sayı: " + i);
    i = i + 1;
}
```

**For Döngüsü (C-Tarzı):**
```javascript
döngü (değişken j = 0; j < 10; j = j + 1) {
    eğer (j == 5) { devam; } // 5'i atla
    eğer (j == 8) { kır; }   // 8'de döngüyü bitir
    yazdır(j);
}
```

---

## 4. Fonksiyonlar

```javascript
fonksiyon topla(a, b) {
    dön a + b;
}

değişken sonuc = topla(5, 10);
yazdır(sonuc);
```

---

## 5. Nesne Yönelimli Programlama (OOP)

### Sınıf Tanımlama
```javascript
sınıf Hayvan {
    kurucu(ad) {
        öz.ad = ad; // 'öz' (this) anahtar kelimesi
    }

    ses_cikar() {
        yazdır(öz.ad + " ses çıkarıyor.");
    }
}
```

### Kalıtım (Miras Alma)
```javascript
sınıf Kedi < Hayvan {
    ses_cikar() {
        yazdır(öz.ad + " miyavlıyor!");
        ata.ses_cikar(); // Üst sınıf metodunu çağırma
    }
}

değişken kedi = yeni Kedi("Boncuk");
kedi.ses_cikar();
```

---

## 6. Oyun Motoru (Voxel Engine) 🎮

GümüşDil, yerleşik bir Voxel motoruna sahiptir. IDE üzerinde kodla 3D dünyalar yaratabilirsiniz.

```javascript
// (x, y, z, TipID)
// TipID: 1=Çimen, 2=Taş, 3=Su, 4=Tahta

// Blok Ekleme
insaa_et(0, 0, 0, 1); // Başlangıç noktasına çimen koy
insaa_et(0, 1, 0, 2); // Üstüne taş koy

// Blok Sorgulama
değişken blok = blok_ne(0, 1, 0); // 2 döner

// Blok Silme
blok_sil(0, 1, 0);
```

---

## 7. Dosya ve Sistem İşlemleri

### Dosya İşlemleri
```javascript
// Dosya Yazma (Üzerine yazar)
dosya_yaz("notlar.txt", "Alışveriş listesi...");

// Dosyaya Ekleme (Sonuna ekler)
dosya_ekle("log.txt", "\nHata oluştu!");

// Dosya Okuma
değişken icerik = dosya_oku("notlar.txt");
```

### Zaman ve Bekleme
```javascript
bekle(1000); // 1000 milisaniye (1 saniye) bekle

değişken simdi = zaman(); // Unix timestamp
```

### Kullanıcı Girdisi
```javascript
yazdır("Adın ne?");
değişken ad = girdi();
yazdır("Memnun oldum " + ad);
```

### Rastgele Sayı
```javascript
değişken zar = rastgele() % 6 + 1; // 1-6 arası sayı
```

---

## 8. Modüller

Başka dosyaları projenize dahil edebilirsiniz.

```javascript
dahil_et("matematik_kutuphanesi.tr");
```

---

## 9. Pratik İpuçları
*   **Template String:** `yazdır($"Adınız: {ad}, Yaşınız: {yas}");` (Yakında tam desteklenecek)
*   **Null Kontrolü:** `eğer (degisken == boş) { ... }`
*   **Mantıksal Operatörler:** `ve`, `veya`, `!` (değil)

