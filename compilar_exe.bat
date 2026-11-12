@echo off
echo ========================================================
echo        Compilando NosClean v5.0.7 a Ejecutable (.exe)
echo ========================================================
echo.

REM Asegurarse de estar en el directorio del script
cd /d "%~dp0"

echo [1/3] Limpiando carpetas de compilaciones previas...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [2/3] Generando NosClean.exe ultra-optimizado con PyInstaller...
python -m PyInstaller ^
    --noconsole ^
    --onefile ^
    --clean ^
    --icon="NosClean.ico" ^
    --add-data="static;static" ^
    --add-data="NosClean.ico;." ^
    --add-data="app;app" ^
    --name="NosClean" ^
    --exclude-module numpy ^
    --exclude-module PIL ^
    --exclude-module Pillow ^
    --exclude-module cryptography ^
    --exclude-module jinja2 ^
    --exclude-module pygments ^
    --exclude-module rich ^
    --exclude-module gunicorn ^
    --exclude-module mako ^
    --exclude-module yaml ^
    --exclude-module watchfiles ^
    --exclude-module websockets ^
    --exclude-module wsproto ^
    main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] La compilacion ha fallado. Revisa los mensajes anteriores.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [3/3] Compilacion completada con exito!
echo.
echo ========================================================
echo El ejecutable portable se encuentra en:
echo dist\NosClean.exe
echo ========================================================
pause

