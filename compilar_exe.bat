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

echo [2/3] Generando NosClean.exe con PyInstaller...
python -m PyInstaller ^
    --noconsole ^
    --onefile ^
    --icon="NosClean.ico" ^
    --add-data="static;static" ^
    --add-data="NosClean.ico;." ^
    --name="NosClean" ^
    --collect-all="webview" ^
    --collect-all="pythonnet" ^
    --collect-all="uvicorn" ^
    --collect-all="anyio" ^
    --collect-all="h11" ^
    --hidden-import="webview" ^
    --hidden-import="clr" ^
    --hidden-import="win32com.client" ^
    --hidden-import="uvicorn.logging" ^
    --hidden-import="uvicorn.loops.asyncio" ^
    --hidden-import="uvicorn.protocols.http.h11_impl" ^
    --hidden-import="uvicorn.lifespan.off" ^
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

