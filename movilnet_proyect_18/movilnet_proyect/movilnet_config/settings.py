import os
from pathlib import Path
from django.contrib.messages import constants as message_constants
import dj_database_url

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SEGURIDAD ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-(w0l(o!qmnniszv(9hmrz7x%!(xw2%76b*^bbo*xn!(89a@#+l')

# DEBUG=True solo para desarrollo.
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

# Permite que Cloudflare / ngrok / Render puedan enviar formularios (POST) sin error de CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://*.trycloudflare.com',
    'https://*.ngrok-free.app',
    'https://*.ngrok.io',
    'https://*.onrender.com',
]

# --- APLICACIONES ---
INSTALLED_APPS = [
    "unfold",  # DEBE IR PRIMERO
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'proyectos',  # Tu aplicación principal
]

# --- MIDDLEWARE ---
# Procesan las peticiones antes de llegar a las vistas (seguridad, sesiones, etc.)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'movilnet_config.urls'

# --- PLANTILLAS (TEMPLATES) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'movilnet_config.wsgi.application'

# --- BASE DE DATOS ---
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'gestion_de_seguimiento',
            'USER': 'postgres',
            'PASSWORD': '1234',
            'HOST': '127.0.0.1',
            'PORT': '5432',
            'OPTIONS': {
                'client_encoding': 'UTF8',
            },
        }
    }

# --- VALIDACIÓN DE CONTRASEÑAS ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- IDIOMA Y TIEMPO ---
LANGUAGE_CODE = 'es-ve'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

# --- ARCHIVOS ESTÁTICOS Y MULTIMEDIA ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
# CONFIGURACIÓN IMPORTANTE PARA ARCHIVOS:
MEDIA_ROOT = BASE_DIR / 'media' if os.environ.get('DATABASE_URL') else (Path.home() / 'Movilnet_Archivos')

# --- AUTENTICACIÓN Y SESIONES ---
LOGIN_URL = 'login_usuario'

# Configuración de caducidad de sesión (10 minutos = 600 segundos)
SESSION_COOKIE_AGE = 600 
SESSION_SAVE_EVERY_REQUEST = True

# --- CONFIGURACIÓN DE MENSAJES (Notificaciones al usuario) ---
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger', 
}
UNFOLD = {
    "SITE_TITLE": "Movilnet Gestión",
    "SITE_HEADER": "MI MOVILNET",
    "COLORS": {
        "primary": {
            "50": "255 241 242",
            "100": "255 225 227",
            "200": "255 197 200",
            "300": "255 153 158",
            "400": "255 88 95",
            "500": "255 88 95",
            "600": "229 79 86",
            "700": "191 66 71",
            "800": "153 53 57",
            "900": "127 44 47",
            "950": "76 26 28",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    },
}

# --- CONFIGURACIÓN DE CORREO ELECTRÓNICO (GMAIL) ---
# Se utiliza para el envío de enlaces de recuperación de contraseña
import os
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# TODO: Reemplaza con tu correo de Gmail y la Contraseña de Aplicación
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'tu_correo@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'tu_contraseña_de_aplicacion')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER