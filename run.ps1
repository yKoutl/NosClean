Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "       INICIANDO PC INSIGHT & MASTER CLEANER" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python no está disponible en tu sistema." -ForegroundColor Red
    pause
    exit 1
}

Write-Host "[1/2] Verificando dependencias..." -ForegroundColor Yellow
python -m pip install -r requirements.txt --quiet

Write-Host "[2/2] Abriendo panel en navegador..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000"

Write-Host ""
Write-Host "Panel activo en: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Para detener el servidor presiona Ctrl+C." -ForegroundColor Gray
Write-Host ""

python main.py

