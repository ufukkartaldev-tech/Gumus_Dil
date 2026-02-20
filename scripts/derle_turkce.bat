@echo off
echo ========================================
echo GUMUSDIL DERLEYICI - TURKCE KARAKTER
echo ========================================
echo.

g++ -std=c++17 -c src/compiler/lexer/tokenizer.cpp -o tokenizer.o -I.
if %ERRORLEVEL% NEQ 0 (
    echo HATA: tokenizer.cpp derlenemedi!
    pause
    exit /b 1
)

g++ -std=c++17 -c src/compiler/parser/parser.cpp -o parser.o -I.
if %ERRORLEVEL% NEQ 0 (
    echo HATA: parser.cpp derlenemedi!
    pause
    exit /b 1
)

g++ -std=c++17 -c src/compiler/interpreter/interpreter.cpp -o interpreter.o -I.
if %ERRORLEVEL% NEQ 0 (
    echo HATA: interpreter.cpp derlenemedi!
    pause
    exit /b 1
)

g++ -std=c++17 -c src/compiler/interpreter/native_functions.cpp -o native_functions.o -I.
if %ERRORLEVEL% NEQ 0 (
    echo HATA: native_functions.cpp derlenemedi!
    pause
    exit /b 1
)

g++ -std=c++17 -c src/compiler/interpreter/objects.cpp -o objects.o -I.
if %ERRORLEVEL% NEQ 0 (
    echo HATA: objects.cpp derlenemedi!
    pause
    exit /b 1
)

g++ -std=c++17 -c src/compiler/hardware/serial_port.cpp -o serial_port.o -I.
if %ERRORLEVEL% NEQ 0 (
    echo HATA: serial_port.cpp derlenemedi!
    pause
    exit /b 1
)

g++ -std=c++17 -c src/compiler/main.cpp -o main.o -I.
if %ERRORLEVEL% NEQ 0 (
    echo HATA: main.cpp derlenemedi!
    pause
    exit /b 1
)

echo.
echo Linkleniyor...
g++ -std=c++17 -o gumus.exe main.o tokenizer.o parser.o interpreter.o native_functions.o objects.o serial_port.o
if %ERRORLEVEL% NEQ 0 (
    echo HATA: Linkleme basarisiz!
    pause
    exit /b 1
)

echo.
echo ========================================
echo BASARILI! gumus.exe olusturuldu!
echo ========================================
echo.

pause
