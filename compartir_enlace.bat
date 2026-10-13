@echo off
title MOVILNET - Compartir Enlace para Desarrolladores

:: 1. Ir al directorio donde esta guardado este archivo .bat
cd /d "%~dp0"

:: 2. Si cloudflared.exe esta en la subcarpeta movilnet_proyect_18, saltar a ella
if not exist "cloudflared.exe" if exist "movilnet_proyect_18\cloudflared.exe" (
    cd /d "%~dp0movilnet_proyect_18"
    goto MAIN
)

:MAIN

echo ========================================================
echo   GENERANDO ENLACE PUBLICO PARA EL EQUIPO DE MOVILNET
echo ========================================================
echo.
echo Presiona Ctrl+C en cualquier momento para detener el enlace.
echo.
cloudflared.exe tunnel --url http://127.0.0.1:8000
pause
