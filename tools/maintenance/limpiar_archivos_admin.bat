@echo off
:: Comprobar si se ejecuta como Administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo =================================================================
    echo   [AVISO] ESTE SCRIPT REQUIERE PERMISOS DE ADMINISTRADOR
    echo =================================================================
    echo.
    echo   Haz clic derecho sobre este archivo y elige "Ejecutar como administrador".
    echo.
    echo =================================================================
    pause
    exit /b 1
)

color 0a
title Optimizador de Servicios y Limpieza del Sistema
echo =================================================================
echo        OPTIMIZACION DE SERVICIOS EN SEGUNDO PLANO Y RAM
echo =================================================================
echo.

echo [1/4] Deteniendo y configurando MongoDB en MANUAL...
net stop MongoDB >nul 2>&1
sc config MongoDB start= demand >nul 2>&1
echo       -> MongoDB ahora esta en Manual (no se encendera solo).

echo [2/4] Deteniendo y configurando MySQL (MySQL_Signa) en MANUAL...
net stop MySQL_Signa >nul 2>&1
sc config MySQL_Signa start= demand >nul 2>&1
echo       -> MySQL ahora esta en Manual (no se encendera solo).

echo [3/4] Deteniendo y deshabilitando Microsoft PC Manager...
net stop "PCManager Service Store" >nul 2>&1
sc config "PCManager Service Store" start= disabled >nul 2>&1
taskkill /F /IM MSPCManagerService.exe >nul 2>&1
taskkill /F /IM msedge.exe >nul 2>&1
echo       -> PC Manager y Edge background cerrados.

echo [4/4] Limpiando claves de inyeccion en Chrome...
reg delete "HKLM\SOFTWARE\Google\Chrome\Extensions\fheoggkfdfchfphceeifdbepaooicaho" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\WOW6432Node\Google\Chrome\Extensions\fheoggkfdfchfphceeifdbepaooicaho" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\WOW6432Node\Google\Chrome\Extensions\llbcnfanfmjhpedaedhbcnpgeepdnnok" /f >nul 2>&1

echo.
echo =================================================================
echo   COMPLETADO! 
echo   - MySQL y MongoDB ya no se prenderan solos con Windows.
echo   - PC Manager fue desactivado.
echo   - Se libero la memoria RAM de estos servicios.
echo =================================================================
echo.
pause
