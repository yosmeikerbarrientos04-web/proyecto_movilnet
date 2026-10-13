import sys
import os

# Directorios base
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(THIS_DIR, 'movilnet_proyect_18', 'movilnet_proyect')
VENV_SITE  = os.path.join(PROJECT_DIR, 'venv_local', 'Lib', 'site-packages')

# Agregar venv y proyecto al path de Python
sys.path.insert(0, VENV_SITE)
sys.path.insert(0, PROJECT_DIR)

# Cambiar directorio de trabajo al proyecto real
os.chdir(PROJECT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movilnet_config.settings')

try:
    from django.core.management import execute_from_command_line
except ImportError as exc:
    raise ImportError(
        "No se pudo importar Django. Verifica que el entorno virtual existe en:\n"
        f"  {VENV_SITE}"
    ) from exc

execute_from_command_line(sys.argv)
