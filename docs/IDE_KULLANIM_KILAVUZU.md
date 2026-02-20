# 🎨 GÜMÜŞDIL IDE - Kurulum ve Kullanım Kılavuzu

## 📋 Gereksinimler

- **Python 3.7+** (Tkinter dahil)
- **Windows 10/11** (veya Linux/Mac için uyarlanabilir)
- **gumus.exe** (Derlenmiş Gümüşdil compiler'ı)

##  Kurulum

### 1. Python Kontrolü

```bash
python --version
```

Python 3.7 veya üstü yüklü olmalıdır.

### 2. IDE'yi Başlatma

**Windows:**
```bash
IDE_BASLAT.bat
```

**Linux/Mac:**
```bash
python3 gumus_editor/gumusdil_ide.py
```

##  Özellikler

###  Temel Özellikler

1. **Syntax Highlighting**
   - Türkçe anahtar kelimeler (eger, dongu, fonksiyon...)
   - String'ler (kırmızı/turuncu)
   - Yorumlar (yeşil)
   - Sayılar (açık yeşil)
   - Fonksiyonlar (sarı)

2. **Kod Editörü**
   - Satır numaraları
   - Otomatik girinti
   - Geri al/Yinele (Ctrl+Z/Ctrl+Y)
   - Kes/Kopyala/Yapıştır

3. **Dosya İşlemleri**
   - Yeni dosya (Ctrl+N)
   - Aç (Ctrl+O)
   - Kaydet (Ctrl+S)
   - Farklı kaydet

4. **Çalıştırma**
   - Tek tıkla çalıştır (F5)
   - Entegre terminal
   - Hata gösterimi

###  Görsel Özellikler

1. **Tema Desteği**
   - Koyu tema (varsayılan)
   - Açık tema
   - Görünüm menüsünden değiştirilebilir

2. **Panel Düzeni**
   - Sol: Dosya gezgini
   - Orta: Kod editörü
   - Alt: Terminal
   - Sağ: Yardımcı paneller

###  Yardımcı Paneller

1. **Kütüphaneler Sekmesi**
   - Tüm std_lib kütüphanelerini listeler
   - Hızlı erişim

2. **Fonksiyonlar Sekmesi**
   - Native fonksiyonlar
   - Kullanıcı fonksiyonları

3. **Örnekler Sekmesi**
   - 10+ hazır örnek proje
   - Çift tıkla aç

##  Klavye Kısayolları

| Kısayol | İşlev |
|---------|-------|
| `Ctrl+N` | Yeni dosya |
| `Ctrl+O` | Dosya aç |
| `Ctrl+S` | Kaydet |
| `Ctrl+Z` | Geri al |
| `Ctrl+Y` | Yinele |
| `Ctrl+X` | Kes |
| `Ctrl+C` | Kopyala |
| `Ctrl+V` | Yapıştır |
| `F5` | Programı çalıştır |

##  Kullanım Örnekleri

### Yeni Proje Başlatma

1. `Dosya` → `Yeni Dosya` (veya Ctrl+N)
2. Kodunuzu yazın
3. `Dosya` → `Kaydet` (veya Ctrl+S)
4. `.tr` uzantısıyla kaydedin
5. `Çalıştır` → `Programı Çalıştır` (veya F5)

### Örnek Proje Açma

1. Sağ panelde `Örnekler` sekmesine tıklayın
2. Bir örneğe çift tıklayın
3. Kod otomatik olarak editöre yüklenir
4. F5 ile çalıştırın

### Kütüphane Kullanma

1. Sol panelden `std_lib` klasörünü açın
2. Bir kütüphaneye çift tıklayın
3. Fonksiyonları inceleyin
4. Kendi kodunuzda kullanın:
   ```tr
   dahil_et("std_lib/metin_gelismis.tr")
   ```

## 🎨 Tema Değiştirme

**Koyu Tema:**
- `Görünüm` → `Koyu Tema`

**Açık Tema:**
- `Görünüm` → `Açık Tema`

## 🐛 Hata Ayıklama

### Program Çalışmıyor?

1. **gumus.exe kontrolü:**
   - Proje kök dizininde `gumus.exe` olmalı
   - Yoksa compiler'ı derleyin

2. **Dosya yolu kontrolü:**
   - Dosya kaydedilmiş olmalı
   - Türkçe karakter içeren yollarda sorun olabilir

3. **Syntax hatası:**
   - Terminal'de hata mesajlarını kontrol edin
   - Satır numarasına dikkat edin

### IDE Açılmıyor?

1. **Python kontrolü:**
   ```bash
   python --version
   ```

2. **Tkinter kontrolü:**
   ```bash
   python -m tkinter
   ```
   Küçük bir pencere açılmalı.

3. **Hata mesajları:**
   - Terminal'den manuel başlatın:
   ```bash
   python gumus_editor/gumusdil_ide.py
   ```

## 🎯 İpuçları

1. **Otomatik Kaydetme:**
   - Sık sık Ctrl+S ile kaydedin
   - Çalıştırmadan önce mutlaka kaydedin

2. **Kod Organizasyonu:**
   - Fonksiyonları ayrı dosyalarda tutun
   - `dahil_et()` ile import edin

3. **Terminal Kullanımı:**
   - Çıktıları terminal'de görün
   - Hata mesajlarını okuyun
   - `Temizle` butonu ile terminal'i temizleyin

4. **Dosya Gezgini:**
   - Çift tıkla ile hızlı dosya açma
   - Proje yapısını görün

## 🔧 Gelişmiş Özellikler (Yakında)

- [ ] Code completion (otomatik tamamlama)
- [ ] Error highlighting (satır içi hata gösterimi)
- [ ] Debugger (adım adım çalıştırma)
- [ ] Git entegrasyonu
- [ ] Snippet'ler (kod şablonları)
- [ ] Find & Replace (bul ve değiştir)
- [ ] Multi-file support (çoklu dosya)
- [ ] Split view (bölünmüş görünüm)

## 📞 Destek

Sorun yaşıyorsanız:

1. `KUTUPHANE_REHBERI.md` dosyasını okuyun
2. Örnek projeleri inceleyin
3. Terminal'deki hata mesajlarını kontrol edin

## 🎉 Başarılı Kullanımlar!

IDE ile mutlu kodlamimarir! 🚀

---

**Not:** IDE sürekli geliştirilmektedir. Önerileriniz için geri bildirim bekliyoruz!


