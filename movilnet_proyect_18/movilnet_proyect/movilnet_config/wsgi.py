import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Asegurar que el directorio del proyecto esté en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Establece el módulo de configuración predeterminado que Django debe utilizar.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movilnet_config.settings')

application = get_wsgi_application()
