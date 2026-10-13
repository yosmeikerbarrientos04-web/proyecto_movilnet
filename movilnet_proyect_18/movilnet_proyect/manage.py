#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.
Este script es el punto de entrada para todas las acciones de gestión 
de tu proyecto (como ejecutar el servidor, migrar base de datos, crear apps, etc.).
"""
import os
import sys

def main():
    """
    Configura las variables de entorno y ejecuta los comandos de Django.
    """
    # 1. Le dice a Django qué archivo de configuración (settings) usar.
    # Si notas, aquí está apuntando a 'movilnet_config.settings'.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movilnet_config.settings')
    
    try:
        # 2. Intenta importar las herramientas de gestión de Django
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # 3. Si falla (ej: no está instalado Django o no activaste el venv),
        # lanza un error informativo claro.
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # 4. Ejecuta el comando que escribiste en la terminal (ej: 'runserver')
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()