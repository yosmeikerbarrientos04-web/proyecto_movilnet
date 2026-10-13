@echo off
:: Compartir carpeta automaticamente al iniciar Windows
net share movilnet_proyect_18 /DELETE >nul 2>&1
net share movilnet_proyect_18="C:\Users\Usuario\Desktop\movilnet_proyect_18" /GRANT:Todos,FULL
netsh advfirewall firewall set rule group="Compartir archivos e impresoras" new enable=Yes
echo Carpeta compartida correctamente en red.
