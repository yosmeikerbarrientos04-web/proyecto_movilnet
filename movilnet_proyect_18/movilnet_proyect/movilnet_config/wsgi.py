import os
from django.core.wsgi import get_wsgi_application

# Establece el módulo de configuración predeterminado que Django debe utilizar.
# Esto asegura que cuando el servidor web inicie, apunte a tus 'settings.py'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movilnet_config.settings')

# Crea la instancia de la aplicación WSGI.
# Este es el objeto 'application' que los servidores web (como Gunicorn o Apache)
# utilizarán para gestionar todas las peticiones HTTP que lleguen a tu sitio.
application = get_wsgi_application()
