@echo off
echo ========================================
echo GUMUSDIL UNIT TESTLERI BASLATILIYOR
echo ========================================

if not exist gumus.exe (
    echo [HATA] gumus.exe bulunamadi! Once GUMUS_DERLE.bat calistirin.
    pause
    exit /b 1
)

echo [INFO] Python unittest calistiriliyor...
python tests/test_integration.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [HATA] Testler BASARISIZ oldu!
    exit /b 1
)

echo.
echo [BASARILI] Tum testler gecti!
echo ========================================
pause
