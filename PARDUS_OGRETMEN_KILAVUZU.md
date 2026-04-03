# 🇹🇷 GümüşDil - Pardus Öğretmen Kılavuzu
## Eğitim Kurumları İçin

---

## 📋 İçindekiler

1. [Pardus'ta Kurulum](#kurulum)
2. [Sınıf Yönetimi](#sinif-yonetimi)
3. [Ders Planları](#ders-planlari)
4. [Öğrenci Takibi](#ogrenci-takibi)
5. [Sorun Giderme](#sorun-giderme)

---

## 🚀 Pardus'ta Kurulum

### Tek Bilgisayara Kurulum (Öğretmen)

```bash
# 1. Paketi indir
wget https://gumusdil.org/downloads/gumusdil_1.0.0_amd64.deb

# 2. Kur
sudo dpkg -i gumusdil_1.0.0_amd64.deb
sudo apt-get install -f

# 3. Test et
gumusdil
```

### Bilgisayar Laboratuvarına Toplu Kurulum

```bash
# Tüm bilgisayarlara aynı anda kurmak için
# (Pardus Ağ Yönetimi kullanarak)

# 1. Ana bilgisayarda paket hazırla
sudo cp gumusdil_1.0.0_amd64.deb /var/www/html/packages/

# 2. Her bilgisayarda çalıştır
for i in {1..30}; do
    ssh ogrenci@pc$i "wget http://ogretmen-pc/packages/gumusdil_1.0.0_amd64.deb && sudo dpkg -i gumusdil_1.0.0_amd64.deb"
done
```

### FATİH Projesi Tabletlerine Kurulum

```bash
# USB üzerinden kurulum
# 1. USB'ye kopyala
cp gumusdil_1.0.0_amd64.deb /media/usb/

# 2. Her tablette
sudo dpkg -i /media/usb/gumusdil_1.0.0_amd64.deb
```

---

## 👨‍🏫 Sınıf Yönetimi

### Öğrenci Hesapları Oluşturma

```bash
#!/bin/bash
# Sınıf için öğrenci hesapları oluştur

SINIF="9A"
OGRENCILER=("ahmet" "ayse" "mehmet" "zeynep" "ali")

for ogrenci in "${OGRENCILER[@]}"; do
    # Kullanıcı oluştur
    sudo useradd -m -s /bin/bash ${SINIF}_${ogrenci}
    
    # GümüşDil dizini hazırla
    sudo mkdir -p /home/${SINIF}_${ogrenci}/GümüşDil/Projeler
    sudo mkdir -p /home/${SINIF}_${ogrenci}/GümüşDil/Ödevler
    
    # İzinleri ayarla
    sudo chown -R ${SINIF}_${ogrenci}:${SINIF}_${ogrenci} /home/${SINIF}_${ogrenci}/GümüşDil
    
    echo "✅ ${SINIF}_${ogrenci} hesabı oluşturuldu"
done
```

### Sınıf Paylaşım Klasörü

```bash
# Öğretmen ve öğrenciler arası dosya paylaşımı

# 1. Paylaşım klasörü oluştur
sudo mkdir -p /opt/gumusdil/sinif_9a
sudo chmod 777 /opt/gumusdil/sinif_9a

# 2. Alt klasörler
sudo mkdir -p /opt/gumusdil/sinif_9a/ornekler
sudo mkdir -p /opt/gumusdil/sinif_9a/odevler
sudo mkdir -p /opt/gumusdil/sinif_9a/projeler

# 3. Örnek kodları kopyala
sudo cp -r /usr/share/gumusdil/ornekler/* /opt/gumusdil/sinif_9a/ornekler/
```

---

## 📚 Ders Planları (Pardus Odaklı)

### Hafta 1: GümüşDil ve Pardus'a Giriş

**Hedef:** Öğrenciler Pardus ve GümüşDil'i tanır

**Aktiviteler:**
1. Pardus nedir? (TÜBİTAK, yerli yazılım)
2. GümüşDil kurulumu kontrolü
3. İlk program: "Merhaba Pardus!"

**Örnek Kod:**
```javascript
// Hafta 1 - İlk Program
değişken isim = "Pardus"
yazdır("Merhaba " + isim + "!")
yazdır("Ben GümüşDil ile kod yazıyorum!")
```

**Ödev:**
- Kendi adınızla "Merhaba" programı yazın
- Pardus hakkında 5 özellik araştırın

---

### Hafta 2: Değişkenler ve Türkçe Syntax

**Hedef:** Türkçe anahtar kelimeleri öğrenme

**Aktiviteler:**
1. `değişken`, `eğer`, `döngü` kelimelerini öğren
2. Pardus sistem bilgilerini göster

**Örnek Kod:**
```javascript
// Hafta 2 - Sistem Bilgileri
değişken isletim_sistemi = "Pardus"
değişken gelistirici = "TÜBİTAK"
değişken yil = 2026

yazdır("İşletim Sistemi: " + isletim_sistemi)
yazdır("Geliştirici: " + gelistirici)
yazdır("Yıl: " + metin(yil))
```

**Ödev:**
- Bilgisayarınızın özelliklerini (RAM, disk) gösteren program

---

### Hafta 3-4: Döngüler ve Koşullar

**Hedef:** Mantıksal düşünme

**Aktiviteler:**
1. Türk bayrağı çizimi (döngülerle)
2. Not hesaplama (koşullarla)

**Örnek Kod:**
```javascript
// Hafta 3 - Türk Bayrağı
için (değişken satir = 1; satir <= 5; satir = satir + 1) {
    eğer (satir == 3) {
        yazdır("████    ★    ☾    ████")
    } yoksa {
        yazdır("████████████████████")
    }
}
```

---

### Hafta 5-8: Fonksiyonlar ve Sınıflar

**Hedef:** Modüler programlama

**Aktiviteler:**
1. Pardus paket yöneticisi simülasyonu
2. Öğrenci bilgi sistemi

**Örnek Kod:**
```javascript
// Hafta 5 - Öğrenci Sistemi
sınıf Ogrenci {
    kurucu(ad, numara) {
        öz.ad = ad
        öz.numara = numara
        öz.notlar = []
    }
    
    fonksiyon not_ekle(not) {
        öz.notlar.ekle(not)
    }
    
    fonksiyon ortalama_hesapla() {
        değişken toplam = 0
        için (değişken i = 0; i < öz.notlar.uzunluk(); i = i + 1) {
            toplam = toplam + öz.notlar[i]
        }
        dön toplam / öz.notlar.uzunluk()
    }
}
```

---

## 🛠️ İleri Seviye Kütüphane Dersleri

Pardus laboratuvarlarında daha gelişmiş projeler için şu kütüphaneleri kullanabilirsiniz:

### 1. Robotik ve IoT (robotik.tr)
**Ders:** Temel robot kontrolü.
```javascript
dahil_et("robotik.tr")
değişken motor_sol = yeni Motor(10, 11)
değişken motor_sağ = yeni Motor(12, 13)
motor_sol.ileri(100)
motor_sağ.ileri(100)
```

### 2. Veri Bilimi (veribilimi.tr)
**Ders:** Veri setlerini analiz etme ve grafik çizme.
```javascript
dahil_et("veribilimi.tr")
değişken sınıf_notları = yeni VeriSeti("9-A Sınıfı")
sınıf_notları.satır_ekle([85, "Ali"])
sınıf_notları.satır_ekle([90, "Ayşe"])
sınıf_notları.çiz_çizgi()
```

### 3. Müzik ve Ses (muzik.tr)
**Ders:** Algoritmik müzik yapımı.
```javascript
dahil_et("muzik.tr")
Müzik.nota_çal(Müzik.NOTA_DO, 500)
Müzik.nota_çal(Müzik.NOTA_MI, 500)
Müzik.nota_çal(Müzik.NOTA_SOL, 500)
```

---

## 📊 Öğrenci Takibi

### İlerleme Raporu Şablonu

```bash
#!/bin/bash
# Öğrenci ilerleme raporu oluştur

OGRENCI=$1
RAPOR_DOSYA="/opt/gumusdil/raporlar/${OGRENCI}_rapor.txt"

cat > $RAPOR_DOSYA << EOF
╔════════════════════════════════════════════════════════════╗
║   GÜMÜŞDİL ÖĞRENCİ İLERLEME RAPORU                        ║
║   Pardus Eğitim Sistemi                                    ║
╚════════════════════════════════════════════════════════════╝

Öğrenci: $OGRENCI
Tarih: $(date +%d.%m.%Y)

TAMAMLANAN DERSLER:
☑ Hafta 1: GümüşDil'e Giriş
☑ Hafta 2: Değişkenler
☐ Hafta 3: Döngüler
☐ Hafta 4: Koşullar

PROJE DURUMU:
- Merhaba Dünya: ✅ Tamamlandı
- Hesap Makinesi: 🔄 Devam Ediyor
- Öğrenci Sistemi: ⏳ Başlanmadı

GENEL ORTALAMA: 85/100
BAŞARI DURUMU: İyi

ÖĞRETMEN NOTU:
Öğrenci Türkçe syntax'ı çok iyi kavramış.
Pardus entegrasyonu örneklerinde başarılı.
EOF

echo "✅ Rapor oluşturuldu: $RAPOR_DOSYA"
```

---

## 🔧 Sorun Giderme

### Sık Karşılaşılan Sorunlar

#### 1. "gumusdil: command not found"

**Çözüm:**
```bash
# PATH'i kontrol et
echo $PATH

# Eksikse ekle
echo 'export PATH="/usr/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### 2. "Derleyici bulunamadı"

**Çözüm:**
```bash
# Derleyiciyi kontrol et
ls -la /usr/share/gumusdil/bin/gumus

# Yoksa yeniden derle
cd /usr/share/gumusdil
sudo g++ src/compiler/*.cpp -o bin/gumus -std=c++17
sudo chmod +x bin/gumus
```

#### 3. "Türkçe karakterler görünmüyor"

**Çözüm:**
```bash
# Locale ayarlarını kontrol et
locale

# Türkçe locale kur
sudo apt install language-pack-tr
sudo update-locale LANG=tr_TR.UTF-8
```

#### 4. "Python modülü bulunamadı"

**Çözüm:**
```bash
# CustomTkinter kur
pip3 install --user customtkinter pillow

# Sistem geneli için
sudo pip3 install customtkinter pillow
```

---

## 🎯 Sınıf İçi Aktiviteler

### Aktivite 1: Pardus Keşif Yarışması

**Amaç:** Öğrenciler Pardus'u keşfeder

**Görevler:**
1. Pardus menüsünde kaç uygulama var? (GümüşDil ile say)
2. Sistem bilgilerini GümüşDil ile göster
3. Türk bayrağı ASCII art çiz

**Ödül:** En yaratıcı kod ödüllendirilir!

---

### Aktivite 2: Grup Projesi - Pardus Yönetim Paneli

**Gruplar:** 4-5 kişilik
**Süre:** 2 hafta

**Proje Gereksinimleri:**
- Sistem bilgilerini gösterme
- Paket arama simülasyonu
- Kullanıcı yönetimi (basit)
- Türkçe arayüz

---

## 📞 Destek ve Kaynaklar

### Öğretmen Desteği

**E-posta:** ogretmen@gumusdil.org  
**Forum:** https://forum.gumusdil.org/ogretmenler  
**Telegram:** @gumusdil_ogretmenler

### Pardus Kaynakları

**Pardus Wiki:** https://wiki.pardus.org.tr  
**TÜBİTAK:** https://ulakbim.tubitak.gov.tr  
**MEB FATİH:** http://fatihprojesi.meb.gov.tr

### Eğitim Materyalleri

**Sunum Dosyaları:** /usr/share/gumusdil/egitim/sunumlar  
**Çalışma Kağıtları:** /usr/share/gumusdil/egitim/calisma_kagitlari  
**Video Dersler:** https://gumusdil.org/videolar

---

## 🏆 Başarı Hikayeleri

### Örnek 1: Ankara Atatürk Lisesi

> "9. sınıf öğrencilerimiz GümüşDil ile Pardus yönetim paneli geliştirdi. Harika bir deneyim oldu!"  
> — Mehmet Öğretmen, Bilişim Teknolojileri

### Örnek 2: İzmir FATİH Projesi Okulu

> "Pardus tabletlerimizde GümüşDil çok iyi çalışıyor. Öğrenciler Türkçe kod yazmanın keyfini çıkarıyor!"  
> — Ayşe Öğretmen, Matematik

---

**🇹🇷 GümüşDil + Pardus = Eğitimde Yerli ve Milli Devrim!**

---

*Bu kılavuz eğitim kurumları için hazırlanmıştır.*

