# 🇹🇷 GümüşDil - Türkiye'nin Başmühendis Yazılım Ekosistemi

<div align="center">

![GümüşDil Logo](docs/logo.png)

[![Pardus](https://img.shields.io/badge/Pardus-Tam_Uyum-2c5aa0?style=for-the-badge&logo=linux)](https://pardus.org.tr)
[![GitHub Stars](https://img.shields.io/github/stars/ufukkartal/gumusdil?style=for-the-badge&logo=github)](https://github.com/ufukkartal/gumusdil)
[![License](https://img.shields.io/badge/Lisans-MIT-green?style=for-the-badge)](LICENSE)

[Özellikler](#-özellikler) • [Pardus Entegrasyonu](#-pardus-özel-ekosistemi) • [AI & Eğitim](#-yapay-zeka-ve-eğitim) • [Kurulum](#-kurulum) • [İletişim](#-iletişim)

</div>

---

## 🌟 Vizyonumuz

**GümüşDil**, Türkiye'nin teknoloji hamlesinde gençlerin kendi dillerinde, kendi kültürlerinde ve yerli işletim sistemimiz **Pardus** üzerinde dünya standartlarında yazılım geliştirebilmelerini sağlamak için tasarlanmış hibrit bir ekosistemdir.

### 🎯 Neden GümüşDil?

- 💎 **Bilişsel Kolaylık:** Yabancı dil bariyerini aşan %100 Türkçe sözdizimi.
- ⚡ **Yüksek Performans:** C++ tabanlı güçlü derleyici (Gümüş Compiler).
- 🐆 **Milli İşbirliği:** Pardus ile çekirdek seviyesinde entegrasyon.
- 🏢 **Akıllı Geliştirme:** Yapay zeka destekli yerli asistan (Gümüş Zeka).

---

## 🚀 Öne Çıkan Özellikler

### 💎 Dilin Gücü
- **Modern Syntax:** `değişken`, `fonksiyon`, `sınıf`, `eğer`, `döngü` gibi sezgisel anahtar kelimeler.
- **Güçlü Kütüphaneler:**
  - `pardus_sistem.tr`: 🐆 Pardus sistem servisleri ve paket yönetimi.
  - `veribilimi.tr`: 📊 Veri setleri, analiz ve görselleştirme araçları.
  - `robotik.tr`: 🤖 Motor kontrolü, mesafe sensörleri ve otonom hareket.
  - `muzik.tr`: 🎵 Nota çalma, melodi sentezleme ve enstrüman simülasyonu.
  - `donanim.tr`: 🔌 GPIO ve IoT geliştirme desteği.
  - `grafik_3d.tr`: 🎮 Voxel tabanlı 3D oyun motoru entegrasyonu.

### 🖥️ Next-Generation IDE
- **GümüşHafıza V3.0:** Real-time memory visualization with 3D stack/heap representation, pointer tracking, and performance analytics.
- **Interactive 3D Memory Canvas:** Drag-to-rotate, zoom-enabled 3D visualization of memory blocks with heat mapping.
- **Advanced Memory Cards:** Enhanced variable cards with performance metrics, breakpoints, and watch functionality.
- **Performance Dashboard:** Real-time tracking of allocations, deallocations, peak memory usage, and garbage collection cycles.
- **Gümüş Scene Editor:** Drag-and-drop voxel world designer for `grafik_3d.tr`.
- **Glassmorphism UI:** Modern, aesthetic, and premium user interface.
- **Multi-Theme Support:** Cyberpunk, Nord, Monokai, and Pardus special themes.
- **Gümüş-Module:** Plugin system for IDE customization.

---

## 🐆 Pardus Özel Ekosistemi

GümüşDil, Pardus işletim sistemi için sadece bir uygulama değil, sistemin bir parçasıdır:

### 🧩 Pardus Paneli
IDE içerisindeki özel **Leopar Butonu** ile:
- **Sistem Analizi:** Pardus sürümü ve kaynak kullanımını izleyin.
- **ETAP Entegrasyonu:** Akıllı tahtalar için tek tıkla **Sınıf Modu**'na geçin.
- **Pardus Kaynakları:** Wiki ve Forum dökümanlarına doğrudan erişin.

### 🎨 Pardus Temimarirı
- `🐆 Pardus Derin Gece`: Gece çalışmimarirı için optimize edilmiş kurumsal koyu tema.
- `🖥️ Pardus ETAP`: Sınıf ortamında en arka sıradan bile görülebilen yüksek kontrastlı aydınlık tema.

### 📦 Sistem Entegrasyonu
- **.deb Paketi:** Debian tabanlı sistemler için tam uyumlu paketleme.
- **Mime-Type:** `.tr` dosyaları sistemde otomatik olarak GümüşDil ile ilişkilendirilir.
- **Desktop Actions:** Sağ tık menüsünden doğrudan örnek kodlara erişim.

---

## 🧠 Yapay Zeka ve Eğitim

### 🤖 Gümüş Zeka (AI Sidekick)
- **Hata Analizi:** Syntax hatalarını sadece söylemez, nedenini açıklar ve çözüm önerir.
- **Kod Özetleme:** Karmaşık kod bloklarını Türkçe cümlelerle özetler.
- **Gümüş Akış:** Yazılan kodu anlık olarak profesyonel akış şemalarına (flowchart) dönüştürür.
- **Gümüş Anlatıcı:** Kodun ne yaptığını hikayeleştirerek anlatır.

### 🏋️ Gümüş GYM (Antrenman)
- **Etkileşimli Görevler:** Başlangıçtan ileri seviyeye kadar kodlama görevleri.
- **Canlı Kontrol:** Yazılan kodun doğruluğunu anında test eden puanlama sistemi.
- **Başarı Sertifikaları:** Görevleri tamamlayan öğrencilere dijital motivasyon rozetleri.

---

## 📦 Kurulum

### 🐆 Pardus / Linux
```bash
# 1. deb paketini kurun
sudo dpkg -i gumusdil_1.0.0_amd64.deb
sudo apt-get install -f

# 2. Sistem entegrasyonunu tamamlayın
./pardus_system_integration.sh
```

### 🪟 Windows
```powershell
# Setup.exe dosyasını çalıştırın
.\GumusDil_Setup.exe
```

---

## 📚 Dokümantasyon

| Döküman | İçerik |
|---------|---------|
| [📖 Kullanım Kılavuzu](docs/baslangic.md) | Temel syntax ve ilk adımlar. |
| [🎓 Öğretmen Kılavuzu](PARDUS_OGRETMEN_KILAVUZU.md) | Sınıf yönetimi ve ders planları. |
| [🛠️ Pardus Entegrasyonu](PARDUS_KURULUM.md) | Sistem seviyesinde yapılandırma. |

---

## 🤝 Katkıda Bulunma

GümüşDil bir topluluk projesidir. Siz de katkıda bulunabilirsiniz:
1. Projeyi **Fork** edin.
2. `ozellik/yeni-ozellik` branch'i açın.
3. Değişikliklerinizi yapın ve **Pull Request** gönderin.

---

## 📞 İletişim

- **Geliştirici:** Ufuk Kartal ([ufuk.kartal.dev@gmail.com](mailto:ufuk.kartal.dev@gmail.com))

---

<div align="center">

**"GümüşDil ile Kodla, Pardus ile Dünyaya Hükmet!"**

🇹🇷 **Türkiye'nin Geleceği, Türkiye'nin Diliyle Yazılıyor.** 🇹🇷

[⬆ Başa Dön](#-gümüşdil---türkiyenin-başmühendis-yazılım-ekosistemi)

</div>


