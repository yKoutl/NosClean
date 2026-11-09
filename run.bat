@echo off
title PC Insight & Master Cleaner
color 0b

echo =========================================================
echo       INICIANDO PC INSIGHT ^& MASTER CLEANER
echo =========================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    color 0c
    echo [ERROR] No se encontro Python en tu sistema.
    echo Por favor instala Python o agregalo al PATH.
    pause
    exit /b 1
)

echo [1/2] Verificando dependencias...
python -m pip install -r requirements.txt --quiet --no-warn-script-location

echo [2/2] Iniciando el panel y abriendo navegador...
start "" "http://127.0.0.1:8000"

echo.
echo =========================================================
echo  El panel esta activo en: http://127.0.0.1:8000
echo  Para detener el servidor, cierra esta ventana.
echo =========================================================
echo.

python main.py

