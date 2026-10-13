@echo off
title MOVILNET - Servidor Django
echo.
echo  ==========================================
echo   MOVILNET GESTION - Iniciando servidor...
echo  ==========================================
echo.
cd /d "%~dp0movilnet_proyect_18\movilnet_proyect"
"%~dp0movilnet_proyect_18\movilnet_proyect\venv_local\Scripts\python.exe" manage.py runserver
pause
