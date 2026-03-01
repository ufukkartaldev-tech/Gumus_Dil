@echo off
echo ========================================
echo GUMUSDIL PRO - TAM DERLEME (REBUILD)
echo ========================================

taskkill /F /IM gumus.exe 2>nul
del gumus.exe 2>nul

echo [1/2] Baglantilar kuruluyor ve derleniyor...
g++ -std=c++17 -O3 -o gumus.exe ^
    src/compiler/main.cpp ^
    src/compiler/lexer/tokenizer.cpp ^
    src/compiler/parser/parser.cpp ^
    src/compiler/interpreter/interpreter.cpp ^
    src/compiler/interpreter/native_functions.cpp ^
    src/compiler/interpreter/objects.cpp ^
    src/compiler/interpreter/property_handlers.cpp ^
    src/compiler/semantic/resolver.cpp ^
    src/compiler/hardware/serial_port.cpp ^
    -I. -DUNICODE -D_UNICODE -lwininet -lws2_32 -static -static-libgcc -static-libstdc++

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [HATA] Derleme basarisiz oldu! Kodlari kontrol edin.
    pause
    exit /b 1
)

echo.
echo [2/2] BASARILI! gumus.exe hazir.
echo ========================================
echo Test icin: gumus.exe tests/tam_test.tr
echo ========================================
