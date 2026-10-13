from django.contrib import admin
# pyrefly: ignore [missing-import]
from unfold.admin import ModelAdmin, StackedInline as UnfoldStackedInline  # Importamos el motor visual de Unfold

from .models import (
    Proyecto, Etiqueta, Task, TareaEtiqueta,
    HistorialTarea, TiempoTarea, TaskNote, Reporte,
    PerfilEmpleado, Rol, Gerencia, NotificacionProyecto,
    ProyectoInhabilitado, ProyectoCulminado
)


# --- 0. Gerencias, Roles y Notificaciones ---
@admin.register(NotificacionProyecto)
class NotificacionProyectoAdmin(ModelAdmin):
    list_display = ('id', 'proyecto', 'tipo', 'usuario', 'leida', 'fecha_creacion')
    list_filter = ('tipo', 'leida', 'proyecto')
    search_fields = ('mensaje', 'proyecto__nombre', 'usuario__username')

@admin.register(Gerencia)
class GerenciaAdmin(ModelAdmin):
    list_display = ('id', 'nombre',)
    search_fields = ('nombre',)
    list_display_links = ('id', 'nombre',)

@admin.register(Rol)
class RolAdmin(ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)
    list_display_links = ('id', 'nombre',) if hasattr(Rol, 'nombre') else ('id', 'name',)

# --- 1. Proyectos ---
@admin.register(Proyecto)
class ProyectoAdmin(ModelAdmin): # Cambiado a ModelAdmin de Unfold
    """
    Configuración para gestionar proyectos.
    Permite crear, editar y listar proyectos.
    """
    list_display = ('nombre', 'identificador', 'proyecto_padre', 'tipo', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'tipo')
    search_fields = ('nombre', 'identificador')


# --- 1.1 Proyectos Inhabilitados y Culminados ---
@admin.register(ProyectoInhabilitado)
class ProyectoInhabilitadoAdmin(ModelAdmin):
    list_display = ('id', 'proyecto_original', 'fecha_inhabilitacion', 'inhabilitado_por')
    search_fields = ('proyecto_original__nombre', 'inhabilitado_por__username')

@admin.register(ProyectoCulminado)
class ProyectoCulminadoAdmin(ModelAdmin):
    list_display = ('id', 'proyecto_original', 'fecha_culminacion', 'culminado_por')
    search_fields = ('proyecto_original__nombre', 'culminado_por__username')


# --- 2. Etiquetas ---
@admin.register(Etiqueta)
class EtiquetaAdmin(ModelAdmin): # Cambiado a ModelAdmin de Unfold
    """
    Configuración para gestionar etiquetas.
    Permite organizar y clasificar tareas.
    """
    list_display = ('nombre', 'color')
    search_fields = ('nombre',)


# --- 3. Tareas ---
@admin.register(Task)
class TaskAdmin(ModelAdmin): # Cambiado a ModelAdmin de Unfold
    """
    Configuración para gestionar tareas.
    Permite filtrar por columna (estado), proyecto y usuario.
    """
    list_display = ('title', 'column', 'proyecto', 'assigned_to', 'created_by')
    list_filter = ('column', 'proyecto', 'assigned_to')
    search_fields = ('title', 'description')


# --- 4. Relación Tarea-Etiqueta ---
@admin.register(TareaEtiqueta)
class TareaEtiquetaAdmin(ModelAdmin): # Cambiado a ModelAdmin de Unfold
    """
    Admin para la relación muchos a muchos entre tareas y etiquetas.
    """
    list_display = ('tarea', 'etiqueta', 'asignado_en')
    list_filter = ('etiqueta',)
    search_fields = ('tarea__title', 'etiqueta__nombre')



# --- 6. Historial de Tareas ---
@admin.register(HistorialTarea)
class HistorialTareaAdmin(ModelAdmin): # Cambiado a ModelAdmin de Unfold
    """
    Admin para revisar los cambios de estado de las tareas.
    """
    list_display = ('tarea', 'estado_anterior', 'estado_nuevo', 'fecha_cambio', 'usuario')
    list_filter = ('estado_anterior', 'estado_nuevo')
    search_fields = ('tarea__title',)


# --- 7. Tiempos de Tareas ---
@admin.register(TiempoTarea)
class TiempoTareaAdmin(ModelAdmin): 
    """
    Admin para registrar y revisar el tiempo invertido en tareas.
    """
    list_display = ('tarea', 'usuario', 'horas_invertidas', 'fecha_registro')
    list_filter = ('fecha_registro',)
    search_fields = ('tarea__title', 'usuario__username')


# --- 8. Notas de Tareas ---
@admin.register(TaskNote)
class TaskNoteAdmin(ModelAdmin): 
    """
    Admin para agregar y revisar notas de tareas.
    """
    list_display = ('task', 'user', 'content')
    list_select_related = ('task', 'user')
    search_fields = ('task__title', 'user__username', 'content')

# --- 9. Reportes ---
@admin.register(Reporte)
class ReporteAdmin(ModelAdmin): 
    """
    Representa informes detallados sobre el estado de proyectos o tareas.
    """
    list_display = ('titulo', 'tipo_reporte', 'fecha_creacion', 'autor')
    list_filter = ('tipo_reporte', 'proyecto')
    search_fields = ('titulo', 'contenido')

# --- 10. Perfil de Empleados (Usuarios) ---
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class PerfilEmpleadoInline(UnfoldStackedInline):
    model = PerfilEmpleado
    can_delete = False
    verbose_name_plural = 'Perfil de Empleado'
    fields = ('rol_maestro', 'gerencia', 'fecha_nacimiento', 'sexo', 'telefono')

admin.site.unregister(User)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    inlines = (PerfilEmpleadoInline,)
