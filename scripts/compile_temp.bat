@echo on
g++ -std=c++17 -o gumus_test.exe src/compiler/main.cpp src/compiler/lexer/*.cpp src/compiler/parser/*.cpp src/compiler/interpreter/*.cpp src/compiler/hardware/*.cpp -lwininet
if %errorlevel% neq 0 exit /b %errorlevel%
echo Compilation Success
