@echo off
setlocal
echo [INFO] Gumusdil Profesyonel Derleme Baslatiliyor...

if not exist build mkdir build
if not exist logs mkdir logs

echo [1/7] Tokenizer Derleniyor...
g++ -std=c++17 -c src/compiler/lexer/tokenizer.cpp -o build/tokenizer.o -I.
if %errorlevel% neq 0 goto error

echo [2/7] Parser Derleniyor...
g++ -std=c++17 -c src/compiler/parser/parser.cpp -o build/parser.o -I.
if %errorlevel% neq 0 goto error

echo [3/7] Interpreter Derleniyor...
g++ -std=c++17 -c src/compiler/interpreter/interpreter.cpp -o build/interpreter.o -I.
if %errorlevel% neq 0 goto error

echo [4/7] Native Functions Derleniyor...
g++ -std=c++17 -c src/compiler/interpreter/native_functions.cpp -o build/native_functions.o -I.
if %errorlevel% neq 0 goto error

echo [5/7] Objects Derleniyor...
g++ -std=c++17 -c src/compiler/interpreter/objects.cpp -o build/objects.o -I.
if %errorlevel% neq 0 goto error

echo [6/7] Property Handlers Derleniyor...
g++ -std=c++17 -c src/compiler/interpreter/property_handlers.cpp -o build/property_handlers.o -I.
if %errorlevel% neq 0 goto error

echo [7/7] Hardware/Serial Derleniyor...
g++ -std=c++17 -c src/compiler/hardware/serial_port.cpp -o build/serial_port.o -I.
if %errorlevel% neq 0 goto error

echo [8/8] Main Derleniyor...
g++ -std=c++17 -c src/compiler/main.cpp -o build/main.o -I.
if %errorlevel% neq 0 goto error

echo [LINK] Baglaniyor (Linking)...
g++ -std=c++17 -o gumus.exe build/main.o build/tokenizer.o build/parser.o build/interpreter.o build/native_functions.o build/objects.o build/property_handlers.o build/serial_port.o -lwininet
if %errorlevel% neq 0 goto error

echo.
echo [BASARILI] Derleme tamamlandi: gumus.exe
exit /b 0

:error
echo.
echo [HATA] Derleme sirasinda hata olustu!
exit /b 1
