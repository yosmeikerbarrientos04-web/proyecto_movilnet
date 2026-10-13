"""
Configuración de rutas (URLs) '.
Este archivo mapea las direcciones web (URLs) a las funciones de vistas (views) correspondientes.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm

urlpatterns = [
    # Autenticación
    path('', views.login_usuario, name='login_usuario'), 
    path('home/', views.home, name='home'),
    path('registro/', views.registro, name='registro'),
    path('jefe/registro-usuario/', views.registro_jefe, name='registro_jefe'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # --- RECUPERACIÓN DE CONTRASEÑA ---
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='proyectos/password_reset_form.html',
        form_class=CustomPasswordResetForm,
        email_template_name='proyectos/password_reset_email.html',
        success_url='/password_reset/done/'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='proyectos/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='proyectos/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='proyectos/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Proyectos
    path('crear/', views.crear_proyecto, name='crear_proyecto'),
    path('crear-modulo/<int:parent_id>/', views.crear_modulo, name='crear_modulo'),
    path('editar-proyecto/<int:pk>/', views.editar_proyecto, name='editar_proyecto'),
    path('eliminar/<int:pk>/', views.eliminar_proyecto, name='eliminar_proyecto'),
    path('inhabilitar-proyecto/<int:pk>/', views.inhabilitar_proyecto, name='inhabilitar_proyecto'),
    path('finalizar-proyecto/<int:pk>/', views.finalizar_proyecto, name='finalizar_proyecto'),
    path('proyectos-inhabilitados/', views.proyectos_inhabilitados, name='proyectos_inhabilitados'),
    path('proyectos-culminados/', views.proyectos_culminados, name='proyectos_culminados'),
    path('restaurar-proyecto/<int:pk>/', views.restaurar_proyecto, name='restaurar_proyecto'),

    # Aceptación de Proyectos y Actas de Recepción
    path('proyecto/<int:proyecto_id>/acta/', views.ver_acta_aceptacion, name='ver_acta_aceptacion'),
    path('proyecto/<int:proyecto_id>/acta/excel/', views.descargar_acta_excel, name='descargar_acta_excel'),
    path('proyecto/<int:proyecto_id>/acta/editar/', views.editar_acta_aceptacion, name='editar_acta_aceptacion'),
    path('proyecto/<int:proyecto_id>/acta/aprobar/', views.aprobar_proyecto_acta, name='aprobar_proyecto_acta'),
    path('aceptacion-proyectos/', views.lista_aceptacion_proyectos, name='lista_aceptacion_proyectos'),
    path('proyecto/<int:proyecto_id>/marcar-notificaciones/', views.marcar_notificaciones_proyecto, name='marcar_notificaciones_proyecto'),

    # Tareas (Gerente)
    path('asignar-tarea/<int:proyecto_id>/', views.asignar_tarea, name='asignar_tarea'),
    path('gestionar-asignaciones/<int:proyecto_id>/', views.gestionar_asignaciones, name='gestionar_asignaciones'),
    path('tareas-generales/', views.gestionar_tareas_generales, name='gestionar_tareas_generales'),
    
    # Equipos y Revisión (Gerente/Jefe)
    path('desarrolladores/', views.lista_devs, name='lista_desarrolladores'),
    path('gerentes/', views.lista_gerentes, name='lista_gerentes'),
    path('revision-tareas/', views.revision_tareas, name='revision_tareas'),
    path('aprobar-tarea/<int:pk>/', views.aprobar_tarea, name='aprobar_tarea'),
    path('devolver-tarea/<int:pk>/', views.devolver_tarea, name='devolver_tarea'),

    # Panel Desarrollador
    path('panel_desarrollador/<int:proyecto_id>/', views.panel_desarrollador, name='panel_desarrollador'),
    path('eliminar-tarea/<int:pk>/', views.eliminar_tarea, name='eliminar_tarea'),
    path('tarea/<int:pk>/estado/<str:estado>/', views.cambiar_estado_tarea, name='cambiar_estado_tarea'),
    path('dev/crear-tarea/', views.dev_crear_tarea, name='dev_crear_tarea'),
    path('dev/editar-tarea/<int:pk>/', views.dev_editar_tarea, name='dev_editar_tarea'),
    path('tarea/<int:pk>/agregar-nota/', views.agregar_nota, name='agregar_nota'),
    path('nota/<int:pk>/eliminar/', views.eliminar_nota, name='eliminar_nota'),
    path('tarea/<int:pk>/registrar-tiempo/', views.registrar_tiempo, name='registrar_tiempo'),
    path('proyecto/<int:pk>/generar-reporte/', views.generar_reporte, name='generar_reporte'),
    path('gerente/crear-tarea/', views.gerente_crear_tarea, name='gerente_crear_tarea'),
    
    # Reportes
    path('reportes/', views.lista_reportes, name='lista_reportes'),
    path('reportes/<int:pk>/', views.ver_reporte, name='ver_reporte'),
]