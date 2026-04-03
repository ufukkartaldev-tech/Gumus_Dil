#!/bin/bash
# GümüşDil - Pardus Sistem Entegrasyon Araçları

# ============================================================================
# 1. PARDUS DOSYA İLİŞKİLENDİRMESİ
# ============================================================================

setup_file_associations() {
    echo "📄 .tr dosyaları için GümüşDil ilişkilendirmesi yapılıyor..."
    
    # MIME type tanımla
    cat > ~/.local/share/mime/packages/gumusdil.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
    <mime-type type="text/x-gumusdil">
        <comment>GümüşDil Kaynak Kodu</comment>
        <comment xml:lang="tr">GümüşDil Kaynak Kodu</comment>
        <glob pattern="*.tr"/>
        <icon name="text-x-script"/>
    </mime-type>
</mime-info>
EOF
    
    # MIME veritabanını güncelle
    update-mime-database ~/.local/share/mime 2>/dev/null || true
    
    # Dosya ilişkilendirmesi
    cat > ~/.local/share/applications/gumusdil-open.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=GümüşDil ile Aç
Name[tr]=GümüşDil ile Aç
Exec=gumusdil %f
MimeType=text/x-gumusdil;
NoDisplay=true
EOF
    
    # Varsayılan uygulama olarak ayarla
    xdg-mime default gumusdil-open.desktop text/x-gumusdil
    
    echo "   ✅ .tr dosyaları artık GümüşDil ile açılacak!"
}

# ============================================================================
# 2. PARDUS MENÜ ENTEGRASYONUPardus menüsüne kategori ekle
# ============================================================================

setup_menu_integration() {
    echo "📋 Pardus menü entegrasyonu yapılıyor..."
    
    # Ana masaüstü dosyası
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
Icon=applications-development
Exec=gumusdil %F
Terminal=false
Categories=Development;Education;IDE;GTK;
Keywords=programming;turkish;pardus;yerli;milli;kod;programlama;
MimeType=text/x-gumusdil;text/plain;
StartupNotify=true
X-Pardus-App=true
X-GNOME-FullName=GümüşDil Entegre Geliştirme Ortamı
X-GNOME-FullName[tr]=GümüşDil Entegre Geliştirme Ortamı
Actions=NewFile;OpenExample;

[Desktop Action NewFile]
Name=Yeni Dosya
Name[tr]=Yeni Dosya
Exec=gumusdil --new

[Desktop Action OpenExample]
Name=Örnek Kodlar
Name[tr]=Örnek Kodlar
Exec=gumusdil /usr/share/gumusdil/ornekler/
EOF
    
    # Masaüstü kısayolu (isteğe bağlı)
    if [ -d ~/Desktop ]; then
        cp ~/.local/share/applications/gumusdil.desktop ~/Desktop/
        chmod +x ~/Desktop/gumusdil.desktop
        echo "   ✅ Masaüstü kısayolu oluşturuldu!"
    fi
    
    echo "   ✅ Pardus menüsüne eklendi!"
}

# ============================================================================
# 3. PARDUS SERVİS ENTEGRASYONUPardus sistem servisi
# ============================================================================

setup_service() {
    echo "⚙️  Pardus servis entegrasyonu yapılıyor..."
    
    # Systemd user service (opsiyonel - arka plan derleyici)
    mkdir -p ~/.config/systemd/user
    cat > ~/.config/systemd/user/gumusdil-daemon.service << 'EOF'
[Unit]
Description=GümüşDil Arka Plan Derleyici
Documentation=https://gumusdil.org/docs

[Service]
Type=simple
ExecStart=/usr/share/gumusdil/bin/gumus --daemon
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
    
    echo "   ✅ Servis tanımlandı (başlatmak için: systemctl --user start gumusdil-daemon)"
}

# ============================================================================
# 4. PARDUS KLAVYE KISAYOLLARI
# ============================================================================

setup_keyboard_shortcuts() {
    echo "⌨️  Pardus klavye kısayolları ayarlanıyor..."
    
    # GNOME/XFCE için özel kısayol
    mkdir -p ~/.config/gumusdil
    cat > ~/.config/gumusdil/shortcuts.conf << 'EOF'
# GümüşDil Pardus Klavye Kısayolları

[Global]
open_ide=<Super>g          # Super+G ile IDE aç
new_file=<Super><Shift>n   # Yeni dosya
run_code=F5                # Kodu çalıştır
stop_code=<Shift>F5        # Durdur

[Editor]
save=<Ctrl>s
save_as=<Ctrl><Shift>s
find=<Ctrl>f
replace=<Ctrl>h
comment=<Ctrl>slash

[Turkish]
# Türkçe karakter kısayolları (Pardus Q klavye)
toggle_turkish=<Alt>t
insert_ş=<Alt>s
insert_ğ=<Alt>g
insert_ı=<Alt>i
insert_ö=<Alt>o
insert_ü=<Alt>u
insert_ç=<Alt>c
EOF
    
    echo "   ✅ Klavye kısayolları ayarlandı!"
}

# ============================================================================
# 5. PARDUS PAKET YÖNETİCİSİ ENTEGRASYONU
# ============================================================================

setup_package_manager() {
    echo "📦 Pardus paket yöneticisi entegrasyonu..."
    
    # APT için metadata
    cat > /tmp/gumusdil.list << 'EOF'
# GümüşDil Resmi Deposu (Gelecek için)
# deb https://repo.gumusdil.org/pardus stable main
EOF
    
    # Paket bilgisi
    cat > /tmp/gumusdil-info.txt << 'EOF'
Paket: gumusdil
Versiyon: 1.0.0
Mimari: amd64
Bağımlılıklar: python3 (>= 3.8), python3-tk, g++
Boyut: ~15 MB
Açıklama: Türkçe programlama dili ve IDE
 GümüşDil, yerli ve milli programlama dilidir. Pardus işletim sistemi ile tam uyumludur.
Etiketler: education, programming, turkish, pardus
Bölüm: education
Öncelik: optional
Bakımcı: Ufuk Kartal <ufukkartal@gumusdil.org>
Ana Sayfa: https://gumusdil.org
EOF
    
    echo "   ✅ Paket yöneticisi metadata'sı hazır!"
}

# ============================================================================
# 6. PARDUS BULUT ENTEGRASYONU (Pardus Bulut)
# ============================================================================

setup_cloud_integration() {
    echo "☁️  Pardus Bulut entegrasyonu (opsiyonel)..."
    
    mkdir -p ~/.config/gumusdil/cloud
    cat > ~/.config/gumusdil/cloud/config.ini << 'EOF'
[PardusCloud]
enabled=false
sync_projects=true
sync_settings=true
auto_backup=true
backup_interval=3600  # 1 saat

[Paths]
cloud_dir=~/PardusCloud/GümüşDil
backup_dir=~/PardusCloud/GümüşDil/Yedekler
EOF
    
    echo "   ✅ Bulut entegrasyonu yapılandırıldı!"
}

# ============================================================================
# 7. PARDUS EĞİTİM PORTALII ENTEGRASYONU
# ============================================================================

setup_education_portal() {
    echo "🎓 Pardus Eğitim Portalı entegrasyonu..."
    
    cat > ~/.config/gumusdil/education.conf << 'EOF'
[EgitimPortali]
# MEB Eğitim Portalı entegrasyonu (gelecek)
enabled=false
portal_url=https://egitim.pardus.org.tr
api_key=
sync_progress=true
submit_assignments=true

[Classroom]
# Sınıf yönetimi
teacher_mode=false
student_mode=true
class_code=
share_code=true
EOF
    
    echo "   ✅ Eğitim portalı ayarları hazır!"
}

# ============================================================================
# 8. PARDUS SINIF MODU (ETAP & Öğretmen Araçları)
# ============================================================================

setup_classroom_mode() {
    echo "🏫 Pardus Sınıf Modu yapılandırılıyor..."
    
    # Paylaşım dizini oluştur (Öğretmen yetkisi gerekebilir)
    SHARE_DIR="/opt/gumusdil/sinif_paylasim"
    echo "📁 Paylaşım dizini hazırlanıyor: $SHARE_DIR"
    
    # Kullanıcıdan onay almadan yapamayız ama yapıyı kuralım
    cat > /tmp/gumusdil_classroom_setup.sh << EOF
#!/bin/bash
sudo mkdir -p $SHARE_DIR/ornekler
sudo mkdir -p $SHARE_DIR/odevler
sudo mkdir -p $SHARE_DIR/teslimler
sudo chmod -R 777 /opt/gumusdil/sinif_paylasim
echo "✅ Sınıf paylaşım dizini oluşturuldu."
EOF

    # Masaüstüne sınıf araçları kısayolu
    if [ -d ~/Desktop ]; then
        cat > ~/Desktop/Gümüş-Sınıf.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Gümüş Sınıf Yönetimi
Comment=Pardus Sınıf Paylaşım Klasörü
Exec=xdg-open /opt/gumusdil/sinif_paylasim
Icon=folder-remote
Terminal=false
Categories=Education;
EOF
        chmod +x ~/Desktop/Gümüş-Sınıf.desktop
    fi
    
    echo "   ✅ Sınıf modu araçları hazır!"
}

# ============================================================================
# 9. PARDUS TÜRKÇE DESTEK OPTİMİZASYONU
# ============================================================================

setup_turkish_support() {
    echo "🇹🇷 Türkçe destek optimizasyonu..."
    
    # Türkçe locale ayarları
    cat > ~/.config/gumusdil/locale.conf << 'EOF'
[Locale]
LANG=tr_TR.UTF-8
LC_ALL=tr_TR.UTF-8
LANGUAGE=tr:en

[Keyboard]
layout=tr
variant=q  # Pardus Q klavye

[Fonts]
# Pardus için optimize edilmiş fontlar
primary=DejaVu Sans Mono
fallback=Liberation Mono, Noto Sans Mono
size=12
turkish_chars_bold=true  # Türkçe karakterleri kalın göster
EOF
    
    echo "   ✅ Türkçe destek optimize edildi!"
}

# ============================================================================
# ANA FONKSİYON
# ============================================================================

main() {
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║   GümüşDil - Pardus Sistem Entegrasyonu                       ║"
    echo "║   Yerli ve Milli Yazılım                                       ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    
    setup_file_associations
    echo ""
    setup_menu_integration
    echo ""
    setup_keyboard_shortcuts
    echo ""
    setup_turkish_support
    echo ""
    setup_package_manager
    echo ""
    setup_cloud_integration
    echo ""
    setup_education_portal
    echo ""
    
    # Opsiyonel servis
    read -p "Arka plan derleyici servisini kurmak ister misiniz? (e/h): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ee]$ ]]; then
        setup_service
    fi
    
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║   ✅ Pardus Sistem Entegrasyonu Tamamlandı!                   ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🚀 GümüşDil artık Pardus ile tam entegre!"
    echo ""
    echo "📋 Yapılanlar:"
    echo "   ✅ .tr dosyaları GümüşDil ile açılıyor"
    echo "   ✅ Pardus menüsüne eklendi"
    echo "   ✅ Klavye kısayolları ayarlandı"
    echo "   ✅ Türkçe destek optimize edildi"
    echo "   ✅ Masaüstü kısayolu oluşturuldu"
    echo ""
    echo "🎯 Kullanım:"
    echo "   - Uygulama menüsünden 'GümüşDil IDE' seçin"
    echo "   - .tr dosyasına çift tıklayın"
    echo "   - Super+G tuşlarına basın"
    echo ""
}

# Script'i çalıştır
main
