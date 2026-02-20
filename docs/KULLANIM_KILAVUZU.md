# 💎 GÜMÜŞDİL & GÜMÜŞIDE PRO - KULLANIM KILAVUZU

Hoş geldin Yeğenim! Burası GümüşDil'in kitabıdır. Daktiloyu eline almadan önce burayı okursan kodların yağ gibi akar, hata yapmazsın.

---

## 🚀 1. Başlangıç

### IDE'yi Çalıştırma
Masaüstündeki veya klasördeki **`gumus_ide.bat`** dosyasına çift tıklaman yeterli. Daktilo (IDE) ve Derleyici (Compiler) otomatik olarak hazır duruma gelecektir.

---

## ✨ 2. Yeni Dil Özellikleri

GümüşDil sürekli gelişiyor. İşte en son eklenen pırlanta özellikler:

### 📜 Şablon Dizeler (Template Strings)
Eskiden metinleri `+` ile birleştirmekten parmaklarımız yorulurdu. Artık `$` işareti ile işi çözüyoruz.
```gumus
değişken isim = "Ahmet";
değişken yas = 25;

// Eski Usul (Amelelik)
yazdır("Merhaba " + isim + ", yaşın: " + metin(yas));

// Yeni Usul (Pırlanta) 💎
yazdır($"Merhaba {isim}, yaşın: {yas}");
yazdır($"Seneye {yas + 1} yaşında olacaksın.");
```

### 📂 Dosya İşlemleri (Native)
Verileri hafızada tutup kaybetme devri bitti. Artık dosyaya mühürlüyoruz.

*   **`dosya_yaz(yol, icerik)`**: Dosyayı sıfırdan oluşturur ve yazar.
*   **`dosya_ekle(yol, icerik)`**: Var olan dosyanın sonuna ekler.
*   **`dosya_oku(yol)`**: Dosyanın tüm içeriğini metin olarak okur.

**Örnek:**
```gumus
// Günlük yazalım
dosya_yaz("gunluk.txt", $"Sevgili Günlük, bugün hava çok güzel.\n");
dosya_ekle("gunluk.txt", "Kodlar tıkır tıkır çalışıyor.");

// Okuyalım
değişken icerik = dosya_oku("gunluk.txt");
yazdır("Günlükte ne var:\n" + icerik);
```

### 📚 Sözlükler (Dictionaries)
Anahtar-Değer ilişkisi kurmak artık çok kolay.
```gumus
değişken ogrenci = {
    "ad": "Mehmet",
    "not": 85,
    "aktif": doğru
};

yazdır(ogrenci["ad"]); // Mehmet
ogrenci["not"] = 90;   // Notu güncelle
```

---

## 🎨 3. IDE Özelleştirme (Daktilo Ayarları)

Daktilo senin, kurallar senin! `src/ide/data/` klasöründeki dosyalarla oynayabilirsin.

### 🌈 Temimarir (`src/ide/data/temimarir.json`)
Burada "Karanlık", "Aydınlık", "Matrix" gibi temimarir var. Kendi temanı da ekleyebilirsin!
`"aktif_tema": "matrix"` yaparsan IDE Matrix moduna geçer.

**Örnek Tema Ayarı:**
```json
"benim_temam": {
    "arka_plan": "#10002b",
    "font_rengi": "#e0aaff",
    "anahtar_kelime": "#ff9e00"
}
```

### ⌨️ Kısayollar ve AI Modu (`src/ide/data/ayarlar.json`)
Klavye düzenini ve Gümüş Zeka'nın sana nasıl hitap edeceğini buradan seçersin.

**AI Modları (`ai_modu`):**
*   `"dayi"`: (Varsayılan) "Yeğenim" der, samimidir, babacan tavsiyeler verir.
*   `"akademik"`: "Sayın Meslektaşım" der, resmi ve teknik konuşur.
*   `"agresif"`: "Bak koçum" der, hata yaparsan fırçayı basar (Usta-Çırak modu).

---

## 🧠 4. Gümüş Zeka ve Hata Avcısı

### 🤖 AI Asistanı
Sağ paneldeki Gümüş Zeka, yerel bilgi tabanını (RAG) kullanarak sana anında yardım eder. İnternete bile ihtiyacı yoktur. Kodunla ilgili soruları sor, anında cevaplasın.

### 🚨 Hata Yakalayıcı (Interceptor)
Kodunda hata mı var?
*   Kırmızı çizgiler titrer.
*   Gümüş duman efekti çıkar.
*   AI paneli hatayı Türkçeye çevirir ve "Şunu mu demek istedin?" diye çözüm önerir.
*   Tek tıkla "Düzelt" diyebilirsin.

---

## 🔌 5. Eklenti Sistemi (Gümüş-Modül)

IDE'ye yeni özellikler mi eklemek istiyorsun? Python biliyorsan sorun yok!
`plugins/` klasörüne bir `.py` dosyası atman yeterli.

**Örnek Eklenti (`plugins/merhaba.py`):**
```python
def gumus_kayit(manager):
    # IDE açılınca çalışır
    manager.register_hook("on_startup", selamla)

def selamla():
    print("Merhaba GümüşIDE!")
```

**Kancalar (Hooks):**
*   `on_startup`: IDE açıldığında.
*   `on_ui_setup`: Arayüz kurulurken.
*   `on_code_change`: Kod değiştiğinde.
*   `on_save`: Kaydetme sırasında.

---

## 🐞 6. Hata Ayıklama (Debugger)

Kodun nerede patladığını bulmak için satır satır gezebilirsin.
*   **F10**: Adım Adım İlerle (Step Over)
*   **F11**: Fonksiyonun İçine Gir (Step Into)
*   **Sol Tık (Satır Numarası)**: Breakpoint koy (Kırmızı nokta).
*   **Değişken Paneli**: Değişkenlerin o anki değerlerini canlı izle.

---

## ⚠️ Önemli Notlar

1.  **Türkçe Karakterler**: GümüşDil `%100 UTF-8` uyumludur. Değişken isimlerinde `ç, ğ, ı, ö, ş, ü` kullanmaktan korkma.
    *   `değişken ağaç = "Meşe";` ✅
2.  **Native Derleyici**: Kodların C hızında "Native" olarak çalışır. Hata alırsan "Temizle" butonuna basıp tekrar derle.

**İyi Kodlamimarir Yeğenim!** 💎
*GümüşDil Geliştirici Ekibi*


