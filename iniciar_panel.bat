@echo off
cd /d "%~dp0"
if exist "%~dp0NosClean.exe" (
    start "" "%~dp0NosClean.exe"
    exit
)
start "" wscript.exe "%~dp0iniciar_panel.vbs"
exit
