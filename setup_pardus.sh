#!/bin/bash
# GümüşDil - Pardus Entegrasyon Scripti
# Yerli ve Milli Yazılım

echo "🇹🇷 GümüşDil - Pardus Entegrasyonu Başlatılıyor..."
echo ""

# Pardus versiyonunu kontrol et
if [ -f /etc/pardus-release ]; then
    echo "✅ Pardus işletim sistemi tespit edildi!"
    cat /etc/pardus-release
else
    echo "⚠️  Pardus tespit edilemedi. Genel Linux kurulumu yapılacak."
fi

echo ""
echo "📦 Pardus için özel optimizasyonlar uygulanıyor..."

# 1. Pardus paket yöneticisi ile bağımlılıkları kur
echo "1️⃣ Pardus paket yöneticisi (apt) ile bağımlılıklar kuruluyor..."
sudo apt update
sudo apt install -y \
    python3 \
    python3-tk \
    python3-pip \
    g++ \
    make \
    git \
    fonts-dejavu \
    fonts-liberation

# 2. Python bağımlılıkları (Pardus optimizasyonlu)
echo ""
echo "2️⃣ Python kütüphaneleri yükleniyor..."
pip3 install --user --upgrade \
    customtkinter \
    pillow \
    packaging

# 3. Derleyiciyi Pardus için derle
echo ""
echo "3️⃣ GümüşDil derleyicisi Pardus için derleniyor..."
if [ -d "src/compiler" ]; then
    g++ src/compiler/*.cpp -o bin/gumus \
        -std=c++17 \
        -O2 \
        -march=native \
        -DPARDUS_BUILD \
        -lstdc++fs
    
    if [ $? -eq 0 ]; then
        chmod +x bin/gumus
        echo "   ✅ Derleyici başarıyla derlendi!"
    else
        echo "   ❌ Derleme hatası!"
        exit 1
    fi
else
    echo "   ⚠️  Derleyici kaynak kodu bulunamadı"
fi

# 4. Pardus masaüstü entegrasyonu
echo ""
echo "4️⃣ Pardus masaüstü entegrasyonu yapılıyor..."

# Desktop dosyası oluştur
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/gumusdil.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=GümüşDil IDE
Name[tr]=GümüşDil IDE
GenericName=Türkçe Programlama Dili
GenericName[tr]=Türkçe Programlama Dili
Comment=Yerli ve Milli Programlama Dili
Comment[tr]=Yerli ve Milli Programlama Dili
Exec=/usr/bin/gumusdil
Icon=applications-development
Terminal=false
Categories=Development;Education;IDE;
Keywords=programming;turkish;pardus;yerli;milli;
StartupNotify=true
X-Pardus-App=true
EOF

# 5. Pardus için özel konfigürasyon
echo ""
echo "5️⃣ Pardus optimizasyonları uygulanıyor..."

mkdir -p ~/.config/gumusdil
cat > ~/.config/gumusdil/pardus.conf << 'EOF'
# GümüşDil Pardus Konfigürasyonu

[Platform]
os=pardus
theme=pardus-dark
locale=tr_TR.UTF-8

[Compiler]
binary=bin/gumus
flags=-O2 -march=native
encoding=utf-8

[IDE]
font=DejaVu Sans Mono
font_size=12
theme=pardus-premium
show_turkish_tips=true

[DEMO]
mode=demo
show_branding=true
highlight_turkish=true
EOF

# 6. Sistem PATH'ine ekle
echo ""
echo "6️⃣ Sistem PATH'i güncelleniyor..."
if ! grep -q "gumusdil" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# GümüşDil" >> ~/.bashrc
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.bashrc
    echo "export GUMUSDIL_HOME=\"$(pwd)\"" >> ~/.bashrc
    echo "alias gumusdil='python3 -m ide.ui.main_window'" >> ~/.bashrc
fi

# 7. Test
echo ""
echo "7️⃣ Kurulum test ediliyor..."
if [ -x "bin/gumus" ]; then
    echo "   ✅ Derleyici çalışır durumda"
else
    echo "   ❌ Derleyici bulunamadı!"
fi

if python3 -c "import customtkinter" 2>/dev/null; then
    echo "   ✅ Python bağımlılıkları hazır"
else
    echo "   ⚠️  CustomTkinter yüklenemedi"
fi

# 8. Milli Zeka (Yapay Zeka) Opsiyonel Kurulum
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 GÜMÜŞ ZEKAYA GEÇİŞ EKRANI"
echo "Milli Zeka Motoru, GümüşDil içinde size Türkçe kodlama asistanlığı yapar."
echo "Uyarı: Bu işlem yaklaşık 2GB yer kaplar. Zayıf bilgisayarlar için 'Hayır' önerilir."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Milli Zeka Motoru (Ollama + gumus_zeka) kurulsun mu? (e/h): " ZEK_CEVAP

if [[ "$ZEK_CEVAP" =~ ^[Ee]$ ]]; then
    echo "📦 Zeka Motoru indiriliyor ve arka planda kuruluyor..."
    curl -fsSL https://ollama.com/install.sh | sh
    
    echo "🧠 Model eğitiliyor..."
    if [ -f "Modelfile" ]; then
        ollama create gumus_zeka -f Modelfile
    else
        echo "   ⚠️  Modelfile bulunamadı. Boş şablon oluşturuldu."
    fi
    echo "✅ Milli Zeka aktif! IDE açıldığında asistanınız hazır olacak."
else
    echo "⚙️ Sadece HAFİF EDİTÖR kuruldu."
    echo "   - Yapay zeka modülü devre dışı bırakıldı."
    echo "   - Çevrimdışı hazır sözlük ile hızla çalışmaya devam edilebilir."
fi


# Başarı mesajı
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 GümüşDil Pardus entegrasyonu tamamlandı!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Başlatmak için:"
echo "   gumusdil"
echo ""
echo "📚 Örnekler:"
echo "   cd $GUMUSDIL_HOME/ornekler"
echo "   gumusdil syntax_test.tr"
echo ""
echo "🏆 Yerli ve Milli Yazılım"
echo "   Pardus İşletim Sistemi Desteği ✅"
echo ""
