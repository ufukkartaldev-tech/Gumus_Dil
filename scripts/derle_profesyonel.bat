@echo off
setlocal
echo [INFO] Gumusdil Profesyonel Derleme Baslatiliyor (Security Enhanced)...

if not exist build mkdir build
if not exist logs mkdir logs

echo [1/12] Tokenizer Derleniyor...
g++ -std=c++17 -c src/compiler/lexer/tokenizer.cpp -o build/tokenizer.o -I.
if %errorlevel% neq 0 goto error

echo [2/12] Parser Derleniyor...
g++ -std=c++17 -c src/compiler/parser/parser.cpp -o build/parser.o -I.
if %errorlevel% neq 0 goto error

echo [3/12] Interpreter Derleniyor...
g++ -std=c++17 -c src/compiler/interpreter/interpreter.cpp -o build/interpreter.o -I.
if %errorlevel% neq 0 goto error

echo [4/12] Native Functions Derleniyor...
g++ -std=c++17 -c src/compiler/interpreter/native_functions.cpp -o build/native_functions.o -I.
if %errorlevel% neq 0 goto error

echo [5/12] Objects Derleniyor...
g++ -std=c++17 -c src/compiler/interpreter/objects.cpp -o build/objects.o -I.
if %errorlevel% neq 0 goto error

echo [6/12] Property Handlers Derleniyor...
g++ -std=c++17 -c src/compiler/interpreter/property_handlers.cpp -o build/property_handlers.o -I.
if %errorlevel% neq 0 goto error

echo [7/12] Hardware/Serial Derleniyor...
g++ -std=c++17 -c src/compiler/hardware/serial_port.cpp -o build/serial_port.o -I.
if %errorlevel% neq 0 goto error

echo [8/12] Resolver Derleniyor...
g++ -std=c++17 -c src/compiler/semantic/resolver.cpp -o build/resolver.o -I.
if %errorlevel% neq 0 goto error

echo [9/12] LSP Server Derleniyor...
g++ -std=c++17 -c src/compiler/lsp_server.cpp -o build/lsp_server.o -I.
if %errorlevel% neq 0 goto error

echo [10/12] Security Framework - Input Validator Derleniyor...
g++ -std=c++17 -c src/compiler/security/input_validator.cpp -o build/input_validator.o -I.
if %errorlevel% neq 0 goto error

echo [11/12] Security Framework - Secure Database Derleniyor...
g++ -std=c++17 -c src/compiler/security/secure_database.cpp -o build/secure_database.o -I.
if %errorlevel% neq 0 goto error

echo [12/12] Security Framework - Secure Subprocess Derleniyor...
g++ -std=c++17 -c src/compiler/security/secure_subprocess.cpp -o build/secure_subprocess.o -I.
if %errorlevel% neq 0 goto error

echo [13/13] Main Derleniyor...
g++ -std=c++17 -c src/compiler/main.cpp -o build/main.o -I.
if %errorlevel% neq 0 goto error

echo [LINK] Baglaniyor (Linking with Security Framework)...
g++ -std=c++17 -o gumus.exe build/main.o build/tokenizer.o build/parser.o build/interpreter.o build/native_functions.o build/objects.o build/property_handlers.o build/serial_port.o build/resolver.o build/lsp_server.o build/input_validator.o build/secure_database.o build/secure_subprocess.o -lwininet -lws2_32 -static -static-libgcc -static-libstdc++
if %errorlevel% neq 0 goto error

echo.
echo [BASARILI] Derleme tamamlandi: gumus.exe (Security Enhanced)
echo [GUVENLIK] SQL Injection koruması aktif
echo [GUVENLIK] Shell Injection koruması aktif  
echo [GUVENLIK] Input validation aktif
echo [GUVENLIK] Path traversal koruması aktif
exit /b 0

:error
echo.
echo [HATA] Derleme sirasinda hata olustu!
exit /b 1
