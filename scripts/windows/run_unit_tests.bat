@echo off
echo 🧪 Gümüşdil Unit Test Runner
echo ================================

echo.
echo 📋 Test seçenekleri:
echo 1. Tokenizer Testleri
echo 2. Tüm Testler (gelecek)
echo 3. Test Build + Run
echo 4. Coverage Report (gelecek)
echo.

set /p choice="Seçiminiz (1-4): "

if "%choice%"=="1" goto tokenizer_tests
if "%choice%"=="3" goto build_and_run
if "%choice%"=="2" goto all_tests
if "%choice%"=="4" goto coverage
goto invalid

:tokenizer_tests
echo.
echo 🎯 Tokenizer Testleri Çalıştırılıyor...
echo =================================
cd tests
if not exist build mkdir build
cd build

echo 📦 CMake ile build ediliyor...
cmake .. -G "MinGW Makefiles" || goto error

echo 🔨 Derleniyor...
mingw32-make || goto error

echo ✅ Testler çalıştırılıyor...
unit_tests.exe || goto error

echo.
echo 🎉 Tokenizer testleri başarıyla tamamlandı!
goto end

:build_and_run
echo.
echo 🔨 Test Build ve Run
echo ==================
cd tests
if not exist build mkdir build
cd build

echo 📦 CMake configure...
cmake .. -G "MinGW Makefiles" || goto error

echo 🔨 Build...
mingw32-make || goto error

echo ✅ Testler çalıştırılıyor...
unit_tests.exe || goto error

goto end

:all_tests
echo.
echo 🚧 Tüm testler henüz implement edilmedi!
echo Tokenizer testleri çalıştırılıyor...
goto tokenizer_tests

:coverage
echo.
echo 📊 Coverage raporu henüz implement edilmedi!
goto tokenizer_tests

:error
echo.
echo ❌ HATA: Testler çalıştırılamadı!
echo Lütfen Google Test kurulumunu kontrol edin.
pause
exit /b 1

:invalid
echo.
echo ❌ Geçersiz seçim!
pause
exit /b 1

:end
echo.
echo 🏁 Test tamamlandı!
pause
