@echo off
echo ========================================
echo 🧹 GÜMÜŞDİL PROJE TEMİZLİĞİ
echo ========================================
echo.

:: Create directories if they don't exist
if not exist build mkdir build
if not exist logs mkdir logs
if not exist tests mkdir tests

echo [1/4] Build çıktılarını taşıyor...
move /Y *.exe build\ >nul 2>&1
move /Y *.obj build\ >nul 2>&1
move /Y *.o build\ >nul 2>&1
echo   ✓ Executable ve obje dosyaları build/ klasörüne taşındı

echo [2/4] Log dosyalarını taşıyor...
move /Y *.log logs\ >nul 2>&1
move /Y *.txt logs\ >nul 2>&1
echo   ✓ Log ve text dosyaları logs/ klasörüne taşındı

echo [3/4] Test dosyalarını düzenliyor...
move /Y *.tr tests\ >nul 2>&1
echo   ✓ Test dosyaları tests/ klasörüne taşındı

echo [4/4] Geçici dosyaları temizliyor...
del /Q temp\*.tr >nul 2>&1
del /Q temp\*.txt >nul 2>&1
del /Q temp\*.log >nul 2>&1
echo   ✓ Temp klasörü temizlendi

echo.
echo ========================================
echo ✅ TEMİZLİK TAMAMLANDI!
echo ========================================
echo Yapı:
echo   ├─ build/     (Executables ve objeler)
echo   ├─ logs/      (Log dosyaları)
echo   ├─ tests/     (Test dosyaları)
echo   ├─ src/       (Kaynak kodlar)
echo   ├─ scripts/   (Build scriptleri)
echo   └─ docs/      (Dokümantasyon)
echo.
pause