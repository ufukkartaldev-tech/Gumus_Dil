@echo off
echo ========================================
echo GUMUSDIL DERLEYICI - KESIN COZUM
echo ========================================
echo.

taskkill /F /IM gumus.exe 2>nul
taskkill /F /IM python.exe 2>nul

echo Eski gumus.exe temizleniyor...
del gumus.exe 2>nul

echo Derleniyor...
g++ -std=c++17 -o gumus.exe ^
    src/compiler/main.cpp ^
    src/compiler/lexer/tokenizer.cpp ^
    src/compiler/parser/parser.cpp ^
    src/compiler/interpreter/interpreter.cpp ^
    src/compiler/interpreter/native_functions.cpp ^
    src/compiler/interpreter/objects.cpp ^
    src/compiler/hardware/serial_port.cpp ^
    -I. -DUNICODE -D_UNICODE -lwininet -lws2_32 -static -static-libgcc -static-libstdc++

if %ERRORLEVEL% NEQ 0 (
    echo HATA: Derleme basarisiz!
    exit /b 1
)

echo.
echo ========================================
echo BASARILI! gumus.exe guncellendi (SADECE TURKCE MODU)!
echo ========================================
echo.

echo IDE Baslatiliyor...
python -m src.ide.main pro
