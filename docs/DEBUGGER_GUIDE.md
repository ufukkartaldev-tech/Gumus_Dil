# 🐛 GümüşIDE Debugger Paketi - Kullanım Kılavuzu

## 📋 Genel Bakış

GümüşIDE artık **dünya standartlarında** bir debugger (hata ayıklayıcı) paketi ile donatılmıştır! Bu paket, kodunuzu adım adım çalıştırmanıza, değişkenleri izlemenize ve program akışını görselleştirmenize olanak tanır.

---

## ✨ Özellikler

### 1. **Breakpoint Sistemi** 🔴
- **Nasıl Kullanılır:** Satır numaralarına tıklayarak breakpoint ekleyin/kaldırın
- **Görünüm:** Kırmızı daire ile işaretlenir
- **Fonksiyon:** Program bu noktalarda duraklar

### 2. **Step-by-Step Execution** 🚶
Programınızı satır satır ilerletin:

| Kısayol | Komut | Açıklama |
|---------|-------|----------|
| **F5** | Continue | Sonraki breakpoint'e kadar devam et |
| **F10** | Step Over | Mevcut satırı çalıştır, sonraki satıra geç |
| **F11** | Step Into | Fonksiyon çağrısına gir |
| **Shift+F11** | Step Out | Mevcut fonksiyondan çık |

### 3. **Variable Watch Panel** 🔬
Değişkenleri canlı olarak izleyin:

- **Tüm Değişkenler:** Local ve Global değişkenleri listeler
- **Canlı Güncelleme:** Değer değiştiğinde altın sarısı renkte parlar
- **Manuel Takip:** ⭐ işaretiyle favori değişkenlerinizi işaretleyin
- **Değer Düzenleme:** Runtime'da değişken değerlerini değiştirin
- **Filtreler:** All / Local / Global / Watched

**Nasıl Erişilir:**
- Activity Bar'dan 🔬 simgesine tıklayın

### 4. **Call Stack Panel** 📚
Fonksiyon çağrı zincirini görselleştirin:

- **Stack Frames:** Her fonksiyon çağrısını gösterir
- **Local Variables:** Her frame'deki değişkenleri önizler
- **Tıklanabilir:** Frame'e tıklayarak o satıra gidin
- **Depth Indicator:** Stack derinliğini gösterir

**Nasıl Erişilir:**
- Activity Bar'dan 📚 simgesine tıklayın

### 5. **Debug Control Bar** 🎮
Toolbar'da bulunan debug kontrolleri:

- **▶ Play/Pause:** Debug'ı başlat/duraklat
- **⏹ Stop:** Debug'ı durdur
- **⤵ Step Over (F10)**
- **⤓ Step Into (F11)**
- **⤒ Step Out (Shift+F11)**
- **Hız Kontrolü:** 0.5x - 2.0x arası ayarlanabilir

### 6. **Execution Line Highlighting** 💡
- Mevcut çalıştırılan satır **sarı arka plan** ile vurgulanır
- Otomatik scroll: Execution line her zaman görünür

---

## 🎯 Kullanım Senaryoları

### Senaryo 1: Basit Debug
```gümüşdil
// Örnek kod
değişken x = 10
değişken y = 20
değişken toplam = x + y
yazdır(toplam)
```

1. 3. satıra breakpoint ekleyin (satır numarasına tıklayın)
2. **F5** ile programı çalıştırın
3. Program 3. satırda duracak
4. 🔬 Variable Watch'a gidin, `x` ve `y` değerlerini görün
5. **F10** ile bir satır ilerleyin
6. `toplam` değişkeninin oluştuğunu görün

### Senaryo 2: Fonksiyon Debug
```gümüşdil
fonksiyon topla(a, b) {
    değişken sonuc = a + b
    dön sonuc
}

değişken x = topla(5, 3)
yazdır(x)
```

1. 6. satıra breakpoint ekleyin
2. **F5** ile çalıştırın
3. **F11** ile `topla` fonksiyonuna girin
4. 📚 Call Stack'te `topla()` frame'ini görün
5. **F10** ile fonksiyon içinde ilerleyin
6. **Shift+F11** ile fonksiyondan çıkın

### Senaryo 3: Değişken İzleme
```gümüşdil
değişken sayac = 0
döngü (i = 0; i < 10; i++) {
    sayac = sayac + i
}
```

1. 🔬 Variable Watch'ı açın
2. `sayac` değişkenini ⭐ ile işaretleyin
3. 3. satıra breakpoint ekleyin
4. **F5** ile çalıştırın
5. Her iterasyonda `sayac` değerinin değişimini izleyin
6. Hız kontrolü ile 2x hızda çalıştırın

---

## 🏗️ Mimari

### Dosya Yapısı
```
src/ide/
├── core/
│   └── debugger.py          # DebuggerManager (Core Engine)
├── ui/
│   ├── debug_panels.py      # UI Bileşenleri
│   │   ├── VariableWatchPanel
│   │   ├── CallStackPanel
│   │   └── DebugControlBar
│   ├── editor.py            # Execution line highlighting
│   ├── sidebar.py           # Debug panel entegrasyonu
│   └── main_window.py       # Klavye kısayolları
```

### Veri Akışı
```
DebuggerManager
    ↓ (callbacks)
MainWindow._on_debug_line_change()
    ↓
CodeEditor.highlight_execution_line()
    ↓
Sarı vurgu + scroll
```

---

## 🔧 Gelişmiş Özellikler

### Simüle Edilmiş Execution (Şu Anda)
Debugger şu anda **simüle edilmiş** modda çalışıyor. Gerçek program çalıştırma yerine, örnek değişkenler ve satırlar gösteriyor.

### Gerçek Implementasyon (Gelecek)
Compiler'a aşağıdaki özellikler eklenecek:
1. `--debug` flag ile çalıştırma
2. Satır satır execution bilgisi
3. Variable state export (JSON)
4. Breakpoint kontrolü

**Örnek Compiler Entegrasyonu:**
```python
# compiler.py içinde
def run_with_debug(file_path, breakpoints):
    process = subprocess.Popen(
        [compiler_path, "--debug", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    
    # Her satırda:
    # 1. Satır numarasını al
    # 2. Variable state'i parse et
    # 3. Breakpoint kontrolü yap
    # 4. Debugger'a bildir
```

---

## 🎨 Görsel Rehber

### Activity Bar İkonları
```
📂 - Explorer (Dosya Gezgini)
🔍 - Search (Arama)
📜 - Outline (Kod Yapısı)
💎 - Memory (Bellek Haritası)
🏋️ - Gümüş GYM (Eğitim)
🔬 - Variables (Değişkenler) ← YENİ!
📚 - Call Stack (Çağrı Yığını) ← YENİ!
🤖 - Gümüş Zeka (AI)
⚙️ - Settings (Ayarlar)
```

### Renk Kodları
- 🟢 **Yeşil:** Constructor (Yeni nesne)
- 🟡 **Sarı:** Execution line (Mevcut satır)
- 🔴 **Kırmızı:** Breakpoint / Error
- 🟠 **Turuncu:** Watched variable (Takip edilen)
- ⚪ **Gri:** Freed memory (Boşaltılmış bellek)

---

## 📊 Performans İpuçları

1. **Hız Kontrolü:** Hızlı döngüler için 2x kullanın
2. **Watched Variables:** Sadece gerekli değişkenleri izleyin
3. **Breakpoint Sayısı:** Çok fazla breakpoint performansı düşürür
4. **Call Stack Depth:** Derin recursion'larda dikkatli olun

---

## 🐞 Bilinen Sınırlamimarir

1. **Simüle Edilmiş Mod:** Gerçek program çalıştırmıyor (şimdilik)
2. **Compiler Entegrasyonu:** Henüz `gumus.exe` ile entegre değil
3. **Multi-threading:** Tek thread debug destekleniyor
4. **Conditional Breakpoints:** Henüz yok (gelecek özellik)

---

## 🚀 Sonraki Adımlar

### Kısa Vadeli
- [ ] Compiler'a `--debug` flag ekle
- [ ] Satır satır execution bilgisi
- [ ] Variable state export

### Orta Vadeli
- [ ] Conditional breakpoints
- [ ] Watch expressions (örn: `x + y > 10`)
- [ ] Memory profiling entegrasyonu

### Uzun Vadeli
- [ ] Time-travel debugging (geriye sarma)
- [ ] Multi-threading debug
- [ ] Remote debugging

---

## 💡 İpuçları

1. **Hızlı Breakpoint:** Satır numarasına çift tıklayın
2. **Tüm Breakpoint'leri Temizle:** Debugger menüsünden
3. **Execution Line'ı Takip Et:** Otomatik scroll açık
4. **Variable Değiştir:** Runtime'da test için kullanışlı
5. **Call Stack Tıkla:** Hızlıca frame'ler arası geçiş

---

## 🎓 Öğrenme Kaynakları

### Debugger Kullanımı
1. Basit bir program yazın
2. Breakpoint ekleyin
3. F10 ile adım adım ilerleyin
4. Variable Watch'ta değişimleri izleyin

### Best Practices
- Karmaşık fonksiyonlarda F11 kullanın
- Döngülerde conditional breakpoint kullanın (gelecek)
- Call Stack'i sık kontrol edin

---

## 🏆 GümüşIDE Debugger - Dünya Standartlarında!

Bu debugger paketi ile GümüşIDE, Visual Studio Code ve IntelliJ IDEA gibi profesyonel IDE'lerin debug özelliklerine kavuşmuştur. Artık kodunuzu daha hızlı ve etkili bir şekilde debug edebilirsiniz!

**Keyifli Debugging! 🐛✨**


