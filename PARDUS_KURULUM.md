# 🐧 GümüşDil Pardus Kurulum Kılavuzu

## 📦 Paket Oluşturma (Windows'tan)

### Adım 1: WSL (Windows Subsystem for Linux) Kur
```powershell
# PowerShell'de (Yönetici olarak)
wsl --install -d Ubuntu
```

### Adım 2: WSL'de Gerekli Araçları Yükle
```bash
# WSL terminalinde
sudo apt update
sudo apt install dpkg-dev build-essential
```

### Adım 3: Paketi Oluştur
```bash
# Proje dizinine git
cd /mnt/c/Users/90538/Desktop/Ufuk\ Kartal/programlama_dili/

# Build script'ini çalıştırılabilir yap
chmod +x build_pardus_package.sh

# Paketi oluştur
./build_pardus_package.sh
```

---

## 🚀 Pardus'ta Kurulum

### Yöntem 1: .deb Paketi ile (Önerilen)
```bash
# Paketi indir/kopyala
cd ~/Downloads

# Kur
sudo dpkg -i gumusdil_1.0.0_amd64.deb

# Bağımlılıkları çöz (eğer hata varsa)
sudo apt-get install -f
```

### Yöntem 2: Kaynak Koddan
```bash
# Gerekli paketleri yükle
sudo apt update
sudo apt install python3 python3-tk python3-pip g++ git

# Python bağımlılıkları
pip3 install customtkinter pillow

# Derleyiciyi derle
cd ~/gumusdil
g++ src/compiler/*.cpp -o bin/gumus -std=c++17 -lstdc++fs
chmod +x bin/gumus

# IDE'yi başlat
export PYTHONPATH=src
python3 -m ide.ui.main_window
```

---

## ✅ Kurulum Testi

```bash
# Komut satırından test
gumusdil

# Derleyiciyi test
/usr/share/gumusdil/bin/gumus ornekler/merhaba.tr

# Versiyon kontrolü
/usr/share/gumusdil/bin/gumus --version
```

---

## 🔧 Sorun Giderme

### "gumusdil: command not found"
```bash
# PATH'e ekle
echo 'export PATH="/usr/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "ModuleNotFoundError: No module named 'customtkinter'"
```bash
pip3 install --user customtkinter pillow
```

### "Permission denied: /usr/share/gumusdil/bin/gumus"
```bash
sudo chmod +x /usr/share/gumusdil/bin/gumus
```

### Derleyici çalışmıyor
```bash
# Yeniden derle
cd /usr/share/gumusdil
sudo g++ src/compiler/*.cpp -o bin/gumus -std=c++17
sudo chmod +x bin/gumus
```

---

## 🐆 Pardus Özelleştirmeleri

GümüşDil IDE, Pardus işletim sistemi için özel araçlar ve temimarir içerir:

1.  **Pardus Temimarirı**: 
    - `🐆 Pardus Derin Gece`: Pardus estetiğine uygun koyu tema.
    - `🖥️ Pardus ETAP`: Akıllı tahtalar için optimize edilmiş yüksek kontrastlı aydınlık tema.
2.  **Pardus Paneli**: Sidebar'da yer alan 🐆 ikonuna tıklayarak sistem bilgilerine, Pardus kaynaklarına ve hızlı araçlara ulaşabilirsiniz.
3.  **Sınıf Modu (ETAP)**: Pardus paneli üzerinden 'Sınıf Modu'nu aktif ederek arayüzü öğrenciler ve sunumlar için sadeleştirebilirsiniz.
4.  **Otomatik Entegrasyon**: Linux sistemlerde GümüşDil otomatik olarak Pardus temasıyla açılır.

---

## 📋 TEKNOFEST Demo Hazırlığı

### 1. Temiz Pardus Kurulumu
```bash
# Sistem güncellemesi
sudo apt update && sudo apt upgrade -y

# GümüşDil kur
sudo dpkg -i gumusdil_1.0.0_amd64.deb
sudo apt-get install -f
```

### 2. Demo Kodlarını Hazırla
```bash
# Örnek dizinine git
cd /usr/share/gumusdil/ornekler/

# Favori editörle aç
gumusdil gumus_kale_savunma.tr
```

### 3. Sunum İçin Ekran Ayarları
```bash
# Büyük font (Projeksiyon için)
# IDE Ayarlar > Tema > Font Boyutu: 16
```

---

## 🎯 Hızlı Başlangıç Komutları

```bash
# IDE'yi aç
gumusdil

# Belirli dosyayı aç
gumusdil merhaba.tr

# Sadece derleyici
/usr/share/gumusdil/bin/gumus dosya.tr

# Yardım
gumusdil --help
```

---

## 📞 Destek

- **GitHub:** https://github.com/ufukkartal/gumusdil
- **E-posta:** ufukkartal@gumusdil.org
- **TEKNOFEST:** Eğitim Teknolojileri Kategorisi

---

**🌟 GümüşDil - Türkçe Kodlamanın Gücü!**


