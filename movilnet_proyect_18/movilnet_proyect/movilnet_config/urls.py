"""
Configuración de rutas raíz del proyecto.

Este archivo actúa como el orquestador principal. Todas las peticiones web
llegan primero aquí para que Django decida qué aplicación debe procesarlas.
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Ruta del Panel de Administración:
    # Todo lo que empiece por '/admin/' es gestionado por Django automáticamente.
    path('admin/', admin.site.urls),

    # Redirección a la App 'ventas':
    # La cadena vacía '' indica que esta es la ruta base.
    path('', include('proyectos.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)