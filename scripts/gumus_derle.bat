@echo off
echo Derleme baslatiliyor...
g++ -std=c++17 -o gumus.exe src/compiler/main.cpp src/compiler/lexer/*.cpp src/compiler/parser/*.cpp src/compiler/interpreter/*.cpp src/compiler/hardware/*.cpp -lwininet -lws2_32 -static -static-libgcc -static-libstdc++
if %errorlevel% neq 0 (
    echo Derleme HATALI!
    exit /b %errorlevel%
)
echo Derleme BASARILI: gumus.exe
