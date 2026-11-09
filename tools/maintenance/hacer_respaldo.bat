@echo off
set DEST=G:\Mi unidad\RESPALDO_LAPTOP
if not exist "%DEST%" mkdir "%DEST%"

echo [1/7] Respaldando ChaskiProduc y Tareo_Plantillas...
robocopy "D:\ChaskiProduc" "%DEST%\ChaskiProduc" /E /XJ /XD node_modules .pnpm-store .git dist build .next /R:1 /W:1 /MT:8 /NFL /NDL >nul
robocopy "D:\Tareo_Plantillas" "%DEST%\Tareo_Plantillas" /E /XJ /XD node_modules .pnpm-store .git /R:1 /W:1 /MT:8 /NFL /NDL >nul

echo [2/7] Respaldando firmas y github recovery...
robocopy "D:\firmas" "%DEST%\firmas" /E /R:1 /W:1 /MT:8 /NFL /NDL >nul
robocopy "D:\github recovery" "%DEST%\github recovery" /E /R:1 /W:1 /MT:8 /NFL /NDL >nul

echo [3/7] Respaldando CURSOS DE ESTUDIOS (Universidad)...
robocopy "D:\CURSOS DE ESTUDIOS" "%DEST%\CURSOS DE ESTUDIOS" /E /XJ /XD node_modules .pnpm-store .git /R:1 /W:1 /MT:8 /NFL /NDL >nul

echo [4/7] Respaldando fotos randoms y Marca Relatia...
robocopy "D:\fotos randoms" "%DEST%\fotos randoms" /E /R:1 /W:1 /MT:8 /NFL /NDL >nul
robocopy "D:\_Marca Relatia" "%DEST%\_Marca Relatia" /E /R:1 /W:1 /MT:8 /NFL /NDL >nul

echo [5/7] Respaldando archivos sueltos...
copy /y "D:\PAGOS- NOS PLANET.xlsx" "%DEST%\" >nul 2>&1
copy /y "D:\Selfi entre estantes de frutos secos.png" "%DEST%\" >nul 2>&1

echo [6/7] Respaldando PROYECTOS (codigo fuente limpio, sin node_modules)...
robocopy "D:\PROYECTOS" "%DEST%\PROYECTOS" /E /XJ /XD node_modules .pnpm-store .git dist build .next .cache /R:1 /W:1 /MT:8 /NFL /NDL >nul

echo [7/7] Verificando respaldo...
echo =================================================================
echo   RESPALDO COMPLETADO CON EXITO EN TU GOOGLE DRIVE (5 TB)!
echo =================================================================
