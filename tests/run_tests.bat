@echo off
REM GümüşDil C++ Compiler Tests Runner (Windows)
REM Bu script tüm C++ derleyici testlerini çalıştırır

echo 🧪 GümüşDil C++ Compiler Tests
echo ================================

REM Test dizinine git
cd /d "%~dp0"

REM Build directory oluştur
if not exist build mkdir build
cd build

echo 📦 Building tests...
cmake ..
if %errorlevel% neq 0 (
    echo ❌ CMake configuration failed!
    exit /b 1
)

cmake --build . --config Release
if %errorlevel% neq 0 (
    echo ❌ Build failed!
    exit /b 1
)

echo.
echo 🚀 Running tests...
echo ===================

REM Test sayaçları
set TOTAL_TESTS=0
set PASSED_TESTS=0
set FAILED_TESTS=0

REM Unit Tests
echo.
echo 📋 UNIT TESTS
echo =============

call :run_test "Tokenizer Tests" "test_tokenizer.exe"
call :run_test "Parser Tests" "test_parser.exe"
call :run_test "Interpreter Tests" "test_interpreter.exe"
call :run_test "Garbage Collector Tests" "test_garbage_collector.exe"
call :run_test "VM Tests" "test_vm.exe"

REM Integration Tests
echo.
echo 🔗 INTEGRATION TESTS
echo ===================

call :run_test "Compiler Pipeline Tests" "test_compiler_pipeline.exe"
call :run_test "IDE-Compiler Integration Tests" "test_ide_compiler_integration.exe"

REM Sonuçları göster
echo.
echo 📊 TEST RESULTS
echo ===============
echo Total Tests: %TOTAL_TESTS%
echo Passed: %PASSED_TESTS%
echo Failed: %FAILED_TESTS%

if %FAILED_TESTS% equ 0 (
    echo.
    echo 🎉 ALL TESTS PASSED!
    echo The GümüşDil C++ compiler is ready for production.
    exit /b 0
) else (
    echo.
    echo 💥 SOME TESTS FAILED!
    echo Please fix the failing tests before proceeding.
    exit /b 1
)

:run_test
set test_name=%~1
set test_executable=%~2

echo.
echo 🧪 Running %test_name%...
echo ------------------------

set /a TOTAL_TESTS+=1

%test_executable%
if %errorlevel% equ 0 (
    echo ✅ %test_name% PASSED
    set /a PASSED_TESTS+=1
) else (
    echo ❌ %test_name% FAILED
    set /a FAILED_TESTS+=1
)

goto :eof