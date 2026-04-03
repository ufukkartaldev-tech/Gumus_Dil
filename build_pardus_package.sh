#!/bin/bash
# GümüşDil Pardus Paketi Oluşturma Script'i
# Eğitim Teknolojileri

set -e

echo "🔨 GümüşDil Pardus Paketi Oluşturuluyor..."
echo ""

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Değişkenler
PACKAGE_NAME="gumusdil"
VERSION="1.0.0"
ARCH="amd64"
BUILD_DIR="packaging/pardus"
PACKAGE_DIR="${BUILD_DIR}/${PACKAGE_NAME}_${VERSION}_${ARCH}"

# Temizlik
echo "🧹 Eski build dosyaları temizleniyor..."
rm -rf "${PACKAGE_DIR}" "${BUILD_DIR}/*.deb"

# Dizin yapısını oluştur
echo "📁 Paket dizin yapısı oluşturuluyor..."
mkdir -p "${PACKAGE_DIR}/DEBIAN"
mkdir -p "${PACKAGE_DIR}/usr/bin"
mkdir -p "${PACKAGE_DIR}/usr/share/gumusdil"
mkdir -p "${PACKAGE_DIR}/usr/share/applications"
mkdir -p "${PACKAGE_DIR}/usr/share/doc/gumusdil"

# DEBIAN dosyalarını kopyala
echo "📋 Paket meta dosyaları kopyalanıyor..."
cp "${BUILD_DIR}/DEBIAN/control" "${PACKAGE_DIR}/DEBIAN/"
cp "${BUILD_DIR}/DEBIAN/postinst" "${PACKAGE_DIR}/DEBIAN/"
chmod 755 "${PACKAGE_DIR}/DEBIAN/postinst"

# Launcher script
echo "🚀 Başlatıcı script kopyalanıyor..."
cp "${BUILD_DIR}/usr/bin/gumusdil" "${PACKAGE_DIR}/usr/bin/"
chmod 755 "${PACKAGE_DIR}/usr/bin/gumusdil"

# Uygulama dosyalarını kopyala
echo "📦 Uygulama dosyaları kopyalanıyor..."
cp -r src "${PACKAGE_DIR}/usr/share/gumusdil/"
cp -r lib "${PACKAGE_DIR}/usr/share/gumusdil/"
cp -r ornekler "${PACKAGE_DIR}/usr/share/gumusdil/"
cp -r examples "${PACKAGE_DIR}/usr/share/gumusdil/" 2>/dev/null || true

# Derleyici binary'sini kopyala (eğer varsa)
if [ -f "bin/gumus" ]; then
    echo "✅ Derleyici binary bulundu, kopyalanıyor..."
    mkdir -p "${PACKAGE_DIR}/usr/share/gumusdil/bin"
    cp bin/gumus "${PACKAGE_DIR}/usr/share/gumusdil/bin/"
    chmod 755 "${PACKAGE_DIR}/usr/share/gumusdil/bin/gumus"
else
    echo "${YELLOW}⚠️  Derleyici binary bulunamadı!${NC}"
    echo "   Pardus'ta şu komutla derleyin:"
    echo "   g++ src/compiler/*.cpp -o bin/gumus -std=c++17"
fi

# Dokümantasyon
echo "📚 Dokümantasyon ekleniyor..."
cp README.md "${PACKAGE_DIR}/usr/share/doc/gumusdil/" 2>/dev/null || echo "README bulunamadı"
cp LICENSE "${PACKAGE_DIR}/usr/share/doc/gumusdil/" 2>/dev/null || echo "LICENSE bulunamadı"

# Telif hakkı dosyası oluştur
cat > "${PACKAGE_DIR}/usr/share/doc/gumusdil/copyright" << EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: gumusdil
Source: https://github.com/ufukkartal/gumusdil

Files: *
Copyright: 2026 Ufuk Kartal
License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
EOF

# Dosya izinlerini düzelt
echo "🔐 Dosya izinleri ayarlanıyor..."
find "${PACKAGE_DIR}" -type d -exec chmod 755 {} \;
find "${PACKAGE_DIR}" -type f -exec chmod 644 {} \;
chmod 755 "${PACKAGE_DIR}/DEBIAN/postinst"
chmod 755 "${PACKAGE_DIR}/usr/bin/gumusdil"

# Paketi oluştur
echo ""
echo "🎁 .deb paketi oluşturuluyor..."
dpkg-deb --build "${PACKAGE_DIR}"

# Başarı mesajı
if [ -f "${PACKAGE_DIR}.deb" ]; then
    echo ""
    echo "${GREEN}✅ Paket başarıyla oluşturuldu!${NC}"
    echo ""
    echo "📦 Paket: ${PACKAGE_DIR}.deb"
    echo "📊 Boyut: $(du -h "${PACKAGE_DIR}.deb" | cut -f1)"
    echo ""
    echo "🔍 Paket içeriğini görmek için:"
    echo "   dpkg -c ${PACKAGE_DIR}.deb"
    echo ""
    echo "💾 Pardus'ta kurmak için:"
    echo "   sudo dpkg -i ${PACKAGE_DIR}.deb"
    echo "   sudo apt-get install -f  # Bağımlılıkları çöz"
    echo ""
else
    echo "${RED}❌ Paket oluşturulamadı!${NC}"
    exit 1
fi
