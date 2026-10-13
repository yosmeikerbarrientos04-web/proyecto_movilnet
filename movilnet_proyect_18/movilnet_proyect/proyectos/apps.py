from django.apps import AppConfig

class ProyectosConfig(AppConfig):
    """
    Configuración de la aplicación 'proyectos'.
    Define los metadatos necesarios para que Django reconozca y
    gestione este módulo dentro del ecosistema del proyecto.
    """
    """
    Nota: no modificar el atributo name ya que hacerlo romera todo el mapeo del proyecto 
    y detendra la carga del servidor
    """
    name = 'proyectos'  # Ruta del paquete de la aplicación
    
    # Opcional: Nombre legible para el panel de administración
    verbose_name = 'Gestión de proyecto y tarea'