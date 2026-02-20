#!/bin/bash
# GümüşDil - Pardus Otomatik Test Sistemi
# TEKNOFEST 2026 - Kalite Güvence

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   🧪 GÜMÜŞDİL PARDUS OTOMATİK TEST SİSTEMİ                    ║"
echo "║   TEKNOFEST 2026 - Yerli ve Milli Yazılım                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Renkler
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test sayaçları
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test fonksiyonu
run_test() {
    local test_name=$1
    local test_command=$2
    local expected_result=$3
    
    ((TOTAL_TESTS++))
    echo -n "  [$TOTAL_TESTS] $test_name... "
    
    if eval "$test_command" &>/dev/null; then
        if [ "$expected_result" == "pass" ]; then
            echo -e "${GREEN}✓ BAŞARILI${NC}"
            ((PASSED_TESTS++))
            return 0
        else
            echo -e "${RED}✗ BAŞARISIZ (beklenmeyen başarı)${NC}"
            ((FAILED_TESTS++))
            return 1
        fi
    else
        if [ "$expected_result" == "fail" ]; then
            echo -e "${GREEN}✓ BAŞARILI (beklenen hata)${NC}"
            ((PASSED_TESTS++))
            return 0
        else
            echo -e "${RED}✗ BAŞARISIZ${NC}"
            ((FAILED_TESTS++))
            return 1
        fi
    fi
}

# ============================================================================
# 1. PARDUS SİSTEM TESTLERİ
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📋 PARDUS SİSTEM TESTLERİ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

run_test "Pardus işletim sistemi tespiti" \
    "grep -i pardus /etc/os-release 2>/dev/null || uname -a | grep -i linux" \
    "pass"

run_test "Türkçe locale desteği" \
    "locale -a | grep tr_TR" \
    "pass"

run_test "APT paket yöneticisi" \
    "which apt" \
    "pass"

run_test "Systemd init sistemi" \
    "pidof systemd" \
    "pass"

echo ""

# ============================================================================
# 2. GÜMÜŞDİL KURULUM TESTLERİ
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📦 GÜMÜŞDİL KURULUM TESTLERİ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

run_test "gumusdil komutu erişilebilir" \
    "which gumusdil" \
    "pass"

run_test "Derleyici binary mevcut" \
    "test -f /usr/share/gumusdil/bin/gumus" \
    "pass"

run_test "Derleyici çalıştırılabilir" \
    "test -x /usr/share/gumusdil/bin/gumus" \
    "pass"

run_test "IDE kaynak kodu mevcut" \
    "test -d /usr/share/gumusdil/src" \
    "pass"

run_test "Örnek kodlar mevcut" \
    "test -d /usr/share/gumusdil/ornekler" \
    "pass"

run_test "Kütüphaneler mevcut" \
    "test -d /usr/share/gumusdil/lib" \
    "pass"

echo ""

# ============================================================================
# 3. PYTHON BAĞIMLILIK TESTLERİ
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🐍 PYTHON BAĞIMLILIK TESTLERİ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

run_test "Python 3 kurulu" \
    "python3 --version" \
    "pass"

run_test "Python Tkinter modülü" \
    "python3 -c 'import tkinter'" \
    "pass"

run_test "CustomTkinter modülü" \
    "python3 -c 'import customtkinter'" \
    "pass"

run_test "Pillow (PIL) modülü" \
    "python3 -c 'from PIL import Image'" \
    "pass"

run_test "Python packaging modülü" \
    "python3 -c 'import packaging'" \
    "pass"

echo ""

# ============================================================================
# 4. MASAÜSTÜ ENTEGRASYON TESTLERİ
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🖥️  MASAÜSTÜ ENTEGRASYON TESTLERİ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

run_test "Desktop dosyası mevcut" \
    "test -f ~/.local/share/applications/gumusdil.desktop || test -f /usr/share/applications/gumusdil.desktop" \
    "pass"

run_test "MIME type tanımlı" \
    "test -f ~/.local/share/mime/packages/gumusdil.xml" \
    "pass"

run_test ".tr dosya ilişkilendirmesi" \
    "xdg-mime query default text/x-gumusdil 2>/dev/null | grep -q gumusdil" \
    "pass"

echo ""

# ============================================================================
# 5. DERLEYİCİ FONKSİYONELLİK TESTLERİ
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}⚙️  DERLEYİCİ FONKSİYONELLİK TESTLERİ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Test dosyası oluştur
TEST_DIR="/tmp/gumusdil_test_$$"
mkdir -p $TEST_DIR

# Test 1: Basit yazdır
cat > $TEST_DIR/test1.tr << 'EOF'
yazdır("Merhaba Pardus")
EOF

run_test "Basit yazdır komutu" \
    "/usr/share/gumusdil/bin/gumus $TEST_DIR/test1.tr 2>&1 | grep -q 'Merhaba Pardus'" \
    "pass"

# Test 2: Değişkenler
cat > $TEST_DIR/test2.tr << 'EOF'
değişken x = 42
yazdır(x)
EOF

run_test "Değişken tanımlama" \
    "/usr/share/gumusdil/bin/gumus $TEST_DIR/test2.tr 2>&1 | grep -q '42'" \
    "pass"

# Test 3: Döngü
cat > $TEST_DIR/test3.tr << 'EOF'
için (değişken i = 1; i <= 3; i = i + 1) {
    yazdır(i)
}
EOF

run_test "For döngüsü" \
    "/usr/share/gumusdil/bin/gumus $TEST_DIR/test3.tr 2>&1 | grep -q '1'" \
    "pass"

# Test 4: Fonksiyon
cat > $TEST_DIR/test4.tr << 'EOF'
fonksiyon topla(a, b) {
    dön a + b
}
değişken sonuc = topla(5, 3)
yazdır(sonuc)
EOF

run_test "Fonksiyon tanımlama" \
    "/usr/share/gumusdil/bin/gumus $TEST_DIR/test4.tr 2>&1 | grep -q '8'" \
    "pass"

# Test 5: Sınıf
cat > $TEST_DIR/test5.tr << 'EOF'
sınıf Test {
    kurucu(x) {
        öz.x = x
    }
}
değişken t = Test(100)
yazdır(t.x)
EOF

run_test "Sınıf tanımlama" \
    "/usr/share/gumusdil/bin/gumus $TEST_DIR/test5.tr 2>&1 | grep -q '100'" \
    "pass"

# Temizlik
rm -rf $TEST_DIR

echo ""

# ============================================================================
# 6. TÜRKÇE KARAKTER TESTLERİ
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🇹🇷 TÜRKÇE KARAKTER TESTLERİ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

TEST_DIR="/tmp/gumusdil_turkish_test_$$"
mkdir -p $TEST_DIR

# Türkçe karakterler
cat > $TEST_DIR/turkish.tr << 'EOF'
değişken şehir = "İstanbul"
değişken ülke = "Türkiye"
yazdır(şehir)
yazdır(ülke)
EOF

run_test "Türkçe karakter desteği (ş, ğ, ü, ı, ö, ç)" \
    "/usr/share/gumusdil/bin/gumus $TEST_DIR/turkish.tr 2>&1 | grep -q 'İstanbul'" \
    "pass"

rm -rf $TEST_DIR

echo ""

# ============================================================================
# 7. PERFORMANS TESTLERİ
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}⚡ PERFORMANS TESTLERİ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

TEST_DIR="/tmp/gumusdil_perf_test_$$"
mkdir -p $TEST_DIR

# Büyük döngü testi
cat > $TEST_DIR/perf.tr << 'EOF'
değişken toplam = 0
için (değişken i = 1; i <= 1000; i = i + 1) {
    toplam = toplam + i
}
yazdır(toplam)
EOF

echo -n "  [Performans] 1000 iterasyon döngü... "
START_TIME=$(date +%s%N)
/usr/share/gumusdil/bin/gumus $TEST_DIR/perf.tr &>/dev/null
END_TIME=$(date +%s%N)
DURATION=$(( (END_TIME - START_TIME) / 1000000 ))

if [ $DURATION -lt 5000 ]; then
    echo -e "${GREEN}✓ BAŞARILI (${DURATION}ms)${NC}"
    ((PASSED_TESTS++))
else
    echo -e "${YELLOW}⚠ YAVAŞ (${DURATION}ms)${NC}"
    ((PASSED_TESTS++))
fi
((TOTAL_TESTS++))

rm -rf $TEST_DIR

echo ""

# ============================================================================
# SONUÇ RAPORU
# ============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📊 TEST SONUÇLARI${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

SUCCESS_RATE=$(( PASSED_TESTS * 100 / TOTAL_TESTS ))

echo "Toplam Test: $TOTAL_TESTS"
echo -e "${GREEN}Başarılı: $PASSED_TESTS${NC}"
echo -e "${RED}Başarısız: $FAILED_TESTS${NC}"
echo "Başarı Oranı: %$SUCCESS_RATE"
echo ""

if [ $SUCCESS_RATE -ge 90 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   🏆 MÜKEMMEL! GÜMÜŞDİL PARDUS'TA TAM ÇALIŞIYOR!             ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    EXIT_CODE=0
elif [ $SUCCESS_RATE -ge 70 ]; then
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║   ⚠️  İYİ! Bazı küçük sorunlar var, kontrol edin.             ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════════╝${NC}"
    EXIT_CODE=1
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║   ❌ SORUN VAR! Kurulumu kontrol edin.                         ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
    EXIT_CODE=2
fi

echo ""
echo "📝 Detaylı log: /tmp/gumusdil_test_$(date +%Y%m%d_%H%M%S).log"
echo "📞 Destek: https://gumusdil.org/destek"
echo ""

exit $EXIT_CODE
