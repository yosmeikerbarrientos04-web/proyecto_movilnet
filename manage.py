import sys
import os

# Directorios base
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
NESTED_DIR = os.path.join(THIS_DIR, 'movilnet_proyect_18', 'movilnet_proyect')

if os.path.exists(NESTED_DIR):
    PROJECT_DIR = NESTED_DIR
else:
    PROJECT_DIR = THIS_DIR

VENV_SITE = os.path.join(PROJECT_DIR, 'venv_local', 'Lib', 'site-packages')
if os.path.exists(VENV_SITE):
    sys.path.insert(0, VENV_SITE)

sys.path.insert(0, PROJECT_DIR)
os.chdir(PROJECT_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movilnet_config.settings')

try:
    from django.core.management import execute_from_command_line
except ImportError as exc:
    raise ImportError(
        "No se pudo importar Django."
    ) from exc

execute_from_command_line(sys.argv)
