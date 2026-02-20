#!/bin/bash
# GümüşDil Hızlı Test Script'i
# Pardus kurulumunu test eder

echo "🧪 GümüşDil Test Başlatılıyor..."
echo ""

# Renkler
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

# Test fonksiyonu
test_command() {
    local name=$1
    local command=$2
    
    echo -n "Testing $name... "
    if eval "$command" &>/dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
    fi
}

# Testler
echo "📋 Sistem Kontrolleri:"
test_command "Python3" "which python3"
test_command "Python Tk" "python3 -c 'import tkinter'"
test_command "CustomTkinter" "python3 -c 'import customtkinter'"
test_command "Pillow" "python3 -c 'from PIL import Image'"

echo ""
echo "📋 GümüşDil Kontrolleri:"
test_command "gumusdil komutu" "which gumusdil"
test_command "Derleyici binary" "test -x /usr/share/gumusdil/bin/gumus"
test_command "IDE kaynak kodu" "test -d /usr/share/gumusdil/src"
test_command "Örnek kodlar" "test -d /usr/share/gumusdil/ornekler"

echo ""
echo "📋 Desktop Entegrasyonu:"
test_command "Desktop dosyası" "test -f /usr/share/applications/gumusdil.desktop"
test_command "Launcher script" "test -x /usr/bin/gumusdil"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Sonuç: ${GREEN}$PASSED geçti${NC}, ${RED}$FAILED başarısız${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Tüm testler başarılı!${NC}"
    echo ""
    echo "🚀 GümüşDil'i başlatmak için:"
    echo "   gumusdil"
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠️  Bazı testler başarısız oldu.${NC}"
    echo ""
    echo "🔧 Sorunları gidermek için:"
    echo "   cat PARDUS_KURULUM.md"
    exit 1
fi
