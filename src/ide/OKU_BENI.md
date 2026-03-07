# 💎 Gümüşdil IDE - Modern Geliştirme Ortamı

Gümüşdil programlama dili için geliştirilmiş, modern ve kullanıcı dostu IDE.

## ✨ Yeni Özellikler

### 🎨 Modern Temimarir
- **🌙 Gece Mavisi** - GitHub Dark tarzı modern tema
- **🎨 Monokai Pro** - Popüler Monokai teması
- **🧛 Dracula** - Göz yormayan karanlık tema
- **❄️ Nord** - Soğuk tonlu minimalist tema
- **☀️ Aydınlık** - Klasik açık tema
- **🌅 Gün Batımı** - Sıcak tonlu tema

### 🚀 Kullanıcı Arayüzü
- **Hoş Geldin Ekranı** - İlk açılışta şık karşılama
- **Durum Çubuğu** - Satır/sütun, dosya bilgisi, tema seçici
- **Komut Paleti** - `Ctrl+Shift+P` ile hızlı erişim
- **Tema Değiştirici** - `Ctrl+Shift+T` veya durum çubuğundan
- **Smooth Animasyonlar** - Fade in/out efektleri

### 💻 Editör Özellikleri
- **Sözdizimi Vurgulama** - Gümüşdil için özel highlighting
- **Satır Numaraları** - Otomatik güncellenen satır numaraları
- **Hata Vurgulama** - Satır bazlı hata gösterimi
- **Otomatik Kaydetme** - Her tuş vuruşunda yedekleme
- **Cursor Takibi** - Anlık satır/sütun bilgisi

### 🔧 Geliştirici Araçları
- **AST Görselleştirme** - Kod yapısını görsel olarak inceleyin
- **Terminal Entegrasyonu** - Çıktıları anında görün
- **Dosya Gezgini** - Proje klasörlerini kolayca yönetin
- **Hızlı Çalıştırma** - `F5` ile anında test edin

## ⌨️ Klavye Kısayolları

| Kısayol | İşlev |
|---------|-------|
| `F5` | Programı çalıştır |
| `Ctrl+S` | Dosyayı kaydet |
| `Ctrl+Shift+P` | Komut paletini aç |
| `Ctrl+Shift+T` | Tema seçiciyi aç |
| `ESC` | Dialog'ları kapat |

## 🎯 Kullanım

### IDE'yi Başlatma

**Pro Mod (Tüm özellikler):**
```bash
python -m src.ide.main pro
```

**Öğrenci Modu (Basitleştirilmiş):**
```bash
python -m src.ide.main ogrenci
```

### Tema Değiştirme

1. **Durum Çubuğundan:** Sağ alttaki tema butonuna tıklayın
2. **Klavye:** `Ctrl+Shift+T` tuşlarına basın
3. **Komut Paleti:** `Ctrl+Shift+P` → "Tema Değiştir"

### Komut Paleti Kullanımı

1. `Ctrl+Shift+P` tuşlarına basın
2. Arama kutusuna komut adını yazın
3. `Enter` ile çalıştırın veya tıklayın
4. Ok tuşları ile navigasyon yapabilirsiniz

## 🎨 Tema Özelleştirme

`src/ide/config.py` dosyasından yeni temimarir ekleyebilirsiniz:

```python
'tema_adi': {
    'name': '🎨 Tema Adı',
    'bg': '#arka_plan',
    'fg': '#metin_rengi',
    'editor_bg': '#editor_arka_plan',
    'sidebar_bg': '#kenar_cubugu',
    'select_bg': '#secim_rengi',
    'accent': '#vurgu_rengi',
    'keyword': '#anahtar_kelime',
    'string': '#metin',
    'number': '#sayi',
    'comment': '#yorum',
    'function': '#fonksiyon',
    'class': '#sinif',
    'terminal_bg': '#terminal_arka_plan',
    'terminal_fg': '#terminal_metin',
    'border': '#cerceve',
    'hover': '#hover_efekti'
}
```

## 📚 Özellik Detayları

### Hoş Geldin Ekranı
- Hızlı başlangıç butonları
- Son açılan dosyalar
- Örnek projeler
- Dokümantasyon linkleri
- Fade-in animasyonu

### Durum Çubuğu
- Dosya adı göstergesi
- Anlık satır/sütun bilgisi
- Encoding bilgisi (UTF-8)
- Dil göstergesi
- Tek tıkla tema değiştirme

### Komut Paleti
- Fuzzy search (akıllı arama)
- Klavye navigasyonu
- Emoji destekli komutlar
- Hızlı erişim

## 🐛 Bilinen Sorunlar

- İlk açılışta hoş geldin ekranı kapatılabilir (config'den)
- Bazı fontlar sistemde yoksa Consolas kullanılır

## 🔮 Gelecek Özellikler

- [ ] Lambda fonksiyonlar
- [ ] Pattern matching
- [ ] Async/await desteği
- [ ] Decorator/annotation
- [ ] Otomatik tamamlama
- [ ] Kod snippet'leri
- [ ] Git entegrasyonu
- [ ] Debugging araçları

## 💡 İpuçları

1. **Performans:** Büyük dosyalarda syntax highlighting gecikmesi yaşarsanız, config'den basit tema kullanın
2. **Tema:** Gözlerinizi yormamak için karanlık temimarir önerilir
3. **Kısayollar:** Komut paletini (`Ctrl+Shift+P`) sık kullanarak hızlı çalışın
4. **Otomatik Kayıt:** Dosyalarınız otomatik yedeklenir, endişelenmeyin!

## 🎓 Öğrenci Modu

Basitleştirilmiş arayüz ile öğrenciler için:
- Daha büyük fontlar
- Daha az karmaşık menüler
- Temel özellikler
- Kolay kullanım

---

**Geliştirici:** Gümüşdil Ekibi  
**Versiyon:** 2.0 Modern UI  
**Lisans:** MIT


