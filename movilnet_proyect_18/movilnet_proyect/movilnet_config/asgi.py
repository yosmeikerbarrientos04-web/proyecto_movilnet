import os
from django.core.asgi import get_asgi_application

# Configura la variable de entorno para que Django sepa qué archivo de configuración usar.
# Esto asegura que el servidor asíncrono cargue tus ajustes de 'movilnet_config.settings'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movilnet_config.settings')

# Crea la instancia de la aplicación ASGI (Asynchronous Server Gateway Interface).
# Este objeto es el punto de entrada que utilizarán servidores asíncronos (como Uvicorn o Daphne)
# para comunicarse con tu proyecto Django.
application = get_asgi_application()