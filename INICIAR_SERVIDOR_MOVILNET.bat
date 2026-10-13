@echo off
title MOVILNET - INICIADOR DEL SISTEMA
color 0A

:: 1. Ir al directorio donde esta guardado este archivo .bat
cd /d "%~dp0"

:: 2. Si cloudflared.exe esta en la subcarpeta movilnet_proyect_18, saltar a ella
if not exist "cloudflared.exe" if exist "movilnet_proyect_18\cloudflared.exe" (
    cd /d "%~dp0movilnet_proyect_18"
    goto MAIN
)

:MAIN

echo =====================================================================
echo           SISTEMA DE GESTION MOVILNET - SERVIDOR LOCAL
echo =====================================================================
echo.
echo [1/3] Configurando DNS rapido (Google DNS)...
netsh interface ip add dns "Ethernet" 8.8.8.8 index=1 >nul 2>&1
netsh interface ip add dns "Wi-Fi" 8.8.8.8 index=1 >nul 2>&1
netsh interface ip add dns "Ethernet" 8.8.4.4 index=2 >nul 2>&1
netsh interface ip add dns "Wi-Fi" 8.8.4.4 index=2 >nul 2>&1
ipconfig /flushdns >nul 2>&1

echo [2/3] Iniciando servidor Django en segundo plano...
start "Django Server - Movilnet" /D "movilnet_proyect" cmd /k "venv_local\Scripts\python.exe manage.py runserver 0.0.0.0:8000"

echo [3/3] Conectando enlace publico para tu equipo...
timeout /t 5 >nul

echo.
echo =====================================================================
echo  EL ENLACE PUBLICO SE MOSTRARA A CONTINUACION.
echo  Copia el link que termina en .trycloudflare.com y pasalo a tu equipo.
echo  NOTA: NO cierres esta ventana mientras tu equipo este usando el sistema.
echo =====================================================================
echo.

cloudflared.exe tunnel --url http://127.0.0.1:8000
pause
