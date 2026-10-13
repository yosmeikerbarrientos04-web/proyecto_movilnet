from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# --- 1. DEFINICIÓN DE OPCIONES EN CÓDIGO ---


TIPOS_PROYECTO = [
    ('FRONTEND', 'Frontend'),
    ('BACKEND', 'Backend'),
    ('BASE_DE_DATOS', 'Base de Datos'),
    ('DOCUMENTACION', 'Documentación / Análisis'),
    ('PERSONALIZADO', 'Proyecto Personalizado'),
]

# Tareas que se crean automáticamente según el tipo de proyecto
TAREAS_PRECARGADAS = {
    'FRONTEND': [
        ('Análisis de Requerimientos UI',
         'Reunión con el cliente para definir mockups, paleta de colores y flujos de navegación.'),
        ('Diseño de Wireframes',
         'Crear prototipos de baja fidelidad para cada pantalla principal del sistema.'),
        ('Maquetación HTML/CSS Base',
         'Estructura semántica y estilos globales: variables CSS, tipografía y colores.'),
        ('Desarrollo de Componentes',
         'Implementar componentes reutilizables: botones, cards, formularios y modales.'),
        ('Integración con API/Backend',
         'Conectar vistas con endpoints REST y manejar estados de carga y error.'),
        ('Validaciones de Formularios',
         'Implementar validaciones en el lado del cliente con mensajes de error claros.'),
        ('Responsive Design',
         'Adaptar todas las vistas a dispositivos móviles, tablet y escritorio.'),
        ('Pruebas de Compatibilidad',
         'Verificar funcionamiento en Chrome, Firefox, Edge y Safari.'),
        ('Optimización de Rendimiento',
         'Minimizar CSS/JS, lazy loading de imágenes y revisión de Core Web Vitals.'),
        ('Entrega y Documentación',
         'Documentar componentes, estilos usados y guía de uso del proyecto.'),
    ],
    'BACKEND': [
        ('Análisis de Requerimientos del Sistema',
         'Definir endpoints, modelos de datos y reglas de negocio con el equipo.'),
        ('Diseño de Arquitectura',
         'Definir estructura de carpetas, patrones (MVC/MVT) y servicios externos.'),
        ('Configuración del Entorno',
         'Setup del proyecto: variables de entorno, dependencias y base de datos.'),
        ('Modelado de Base de Datos',
         'Definir y crear los modelos/entidades y sus relaciones en el ORM.'),
        ('Desarrollo de Endpoints REST',
         'Implementar los endpoints CRUD con validaciones y serialización de datos.'),
        ('Autenticación y Autorización',
         'Implementar JWT/sesiones, roles y permisos de acceso al sistema.'),
        ('Lógica de Negocio',
         'Desarrollar las reglas y procesos del dominio de la aplicación.'),
        ('Manejo de Errores y Logging',
         'Centralizar el manejo de excepciones y configurar logs del sistema.'),
        ('Pruebas Unitarias e Integración',
         'Escribir y ejecutar tests que cubran los casos críticos del sistema.'),
        ('Documentación de API',
         'Generar documentación (Swagger/Postman) y guía de despliegue del proyecto.'),
    ],
    'BASE_DE_DATOS': [
        ('Levantamiento de Información',
         'Entender los datos existentes, fuentes y necesidades del negocio.'),
        ('Diseño del Modelo Entidad-Relación',
         'Crear diagrama ER con entidades, atributos y cardinalidades.'),
        ('Normalización del Esquema',
         'Aplicar formas normales (1FN, 2FN, 3FN) para eliminar redundancias.'),
        ('Creación de Tablas y Relaciones',
         'Ejecutar scripts DDL para crear la estructura en el motor de base de datos.'),
        ('Definición de Índices y Constraints',
         'Crear índices, claves foráneas y restricciones de integridad referencial.'),
        ('Carga de Datos Iniciales (Seeding)',
         'Insertar datos de prueba o datos maestros necesarios para el sistema.'),
        ('Desarrollo de Procedimientos y Vistas',
         'Crear stored procedures, vistas y funciones reutilizables en la BD.'),
        ('Optimización de Consultas',
         'Analizar y optimizar queries lentas con EXPLAIN y ajuste de índices.'),
        ('Backup y Plan de Recuperación',
         'Configurar políticas de respaldo y realizar prueba de restauración.'),
        ('Documentación del Esquema',
         'Entregar diccionario de datos y diagrama actualizado del modelo final.'),
    ],
    'DOCUMENTACION': [
        ('Relevamiento de Requerimientos',
         'Reuniones con stakeholders para identificar necesidades, objetivos y restricciones del sistema o proceso a documentar.'),
        ('Análisis del Proceso de Negocio',
         'Mapear y modelar los procesos actuales (AS-IS) utilizando diagramas de flujo o BPMN para identificar brechas y oportunidades de mejora.'),
        ('Definición del Alcance del Proyecto',
         'Documentar el alcance, entregables, exclusiones y criterios de aceptación acordados con el equipo y el cliente.'),
        ('Elaboración de Casos de Uso',
         'Redactar casos de uso detallados con actores, flujos principales, alternativos y precondiciones/postcondiciones.'),
        ('Especificación de Requerimientos (SRS)',
         'Producir el documento de especificación de requerimientos del software con requerimientos funcionales y no funcionales.'),
        ('Modelado de Datos y Entidades',
         'Crear diagramas de entidad-relación y diccionarios de datos que reflejen la estructura de la información del sistema.'),
        ('Diseño del Proceso TO-BE',
         'Documentar el proceso futuro optimizado (TO-BE) con los cambios propuestos y la justificación técnica de cada decisión.'),
        ('Revisión y Validación con Stakeholders',
         'Presentar los documentos generados al equipo técnico y a los usuarios clave para recoger feedback y validar la precisión.'),
        ('Control de Cambios y Versionado',
         'Gestionar el registro de cambios en los documentos, asegurando el control de versiones y la trazabilidad de modificaciones.'),
        ('Entrega del Paquete de Documentación',
         'Compilar y entregar el paquete final de documentación (SRS, diagramas, diccionario de datos, manuales) en los formatos acordados.'),
    ],
    'PERSONALIZADO': [],  # El gerente crea las tareas manualmente
}

SEXO_OPCIONES = [
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ('O', 'Otro'),
]

# --- MODELO DE GERENCIAS ---
class Gerencia(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre de la Gerencia")

    def __str__(self):
        return self.nombre

    class Meta:
        managed = True
        db_table = 'gerencias'
        verbose_name = 'Gerencia'
        verbose_name_plural = 'Gerencias'

# --- MODELO ADICIONADO PARA LA TABLA MAESTRA DE ROLES ---
class Rol(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nombre del Rol")

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'roles'
        verbose_name = 'Rol Maestro'
        verbose_name_plural = 'Roles Maestros'

class PerfilEmpleado(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de Nacimiento')
    sexo = models.CharField(max_length=1, choices=SEXO_OPCIONES, null=True, blank=True, verbose_name='Sexo')
    telefono = models.CharField(max_length=20, null=True, blank=True, verbose_name='Teléfono')
    
    rol_maestro = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Rol')
    gerencia = models.ForeignKey(Gerencia, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Gerencia')

    def __str__(self):
        if self.rol_maestro:
            return f"Perfil de {self.usuario.username} - {self.rol_maestro.name}"
        return f"Perfil de {self.usuario.username} - Sin Rol Asignado"

    class Meta:
        db_table = 'perfiles_empleados'
        verbose_name = 'Perfil de Empleado'
        verbose_name_plural = 'Perfiles de Empleados'

# --- 1. MODELO DE COLUMNAS 
class KanbanColumn(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nombre")
    position = models.IntegerField(verbose_name="Posición")

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = 'columnas'
        verbose_name = 'Columna'
        verbose_name_plural = 'Columnas'


# --- 2. MODELO DE PROYECTO ---
class Proyecto(models.Model):
    identificador = models.CharField(
        max_length=12,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^\S{4,12}$', 'El ID debe tener entre 4 y 12 caracteres sin espacios.')],
        verbose_name='ID Único de Proyecto',
        help_text='Ejemplo: AB-1234 (entre 4 y 12 caracteres, letras, números o especiales)')

    proyecto_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='modulos',
        verbose_name='Proyecto Padre'
    )

    
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_inicio = models.DateField(
        blank=True, null=True,
        verbose_name='Fecha de Inicio del Proyecto'
    )
    fecha_deadline = models.DateField(
        blank=True, null=True,
        verbose_name='Fecha Límite (Deadline)'
    )
    fecha_tentativa = models.DateField(
        blank=True, null=True,
        verbose_name='Fecha Tentativa de Finalización'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_PROYECTO,
        default='PERSONALIZADO',
        verbose_name='Tipo de Proyecto'
    )
    gerencia = models.ForeignKey(
        Gerencia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Gerencia Responsable'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')

    @property
    def todas_tareas_finalizadas(self):
        # Un proyecto está listo para finalizar si tiene tareas y ninguna está en un estado distinto a 'LISTO'
        todas_tareas = self.tasks.all()
        if not todas_tareas.exists():
            return False
        return not todas_tareas.exclude(column__name='LISTO').exists()

    def get_notificaciones_para_usuario(self, user):
        if not user or not user.is_authenticated:
            return self.notificaciones.none()
            
        # Excluir las notificaciones generadas por el propio usuario
        qs = self.notificaciones.exclude(usuario=user)
        
        # Determinar el rol del usuario que está consultando
        rol_viewer = 'GERENTE'
        if hasattr(user, 'perfil') and user.perfil and user.perfil.rol_maestro:
            rol_viewer = user.perfil.rol_maestro.name.upper().replace(' ', '_')
            
        # Si el usuario NO es GERENTE ni JEFE ni superusuario:
        # Solo le deben aparecer notificaciones generadas por GERENTE o JEFE (o superusuarios)
        if rol_viewer not in ['GERENTE', 'JEFE'] and not user.is_superuser:
            qs = qs.filter(
                models.Q(usuario__perfil__rol_maestro__name__iexact='GERENTE') |
                models.Q(usuario__perfil__rol_maestro__name__iexact='JEFE') |
                models.Q(usuario__is_superuser=True)
            )
            
        return qs

    def notificaciones_no_leidas_count_for_user(self, user):
        return self.get_notificaciones_para_usuario(user).filter(leida=False).count()

    def ultimas_notificaciones_for_user(self, user):
        return self.get_notificaciones_para_usuario(user)[:15]

    @property
    def notificaciones_no_leidas_count(self):
        return self.notificaciones.filter(leida=False).count()

    @property
    def ultimas_notificaciones(self):
        return self.notificaciones.all()[:15]


    @property
    def total_tareas(self):
        total = self.tasks.count()
        for modulo in self.modulos.all():
            total += modulo.tasks.count()
        return total

    @property
    def deadline_calculado(self):
        from django.db.models import Max, Sum
        from proyectos.utils import add_business_hours
        
        # Excluir las tareas que ya estan listas para que no sumen tiempo al agregar nuevas
        tareas_activas = self.tasks.exclude(column__name__icontains='LISTO')

        # Priorizar la fecha límite máxima directa que los desarrolladores establecieron para las tareas
        max_fecha_limite = tareas_activas.filter(fecha_limite__isnull=False).aggregate(Max('fecha_limite'))['fecha_limite__max']
        if max_fecha_limite:
            return max_fecha_limite
            
        total_horas = tareas_activas.aggregate(Sum('horas_estimadas'))['horas_estimadas__sum'] or 0
        if total_horas > 0:
            return add_business_hours(self.fecha_creacion, total_horas)
        return None

    def get_tipo_display_icon(self):
        icons = {
            'FRONTEND': '🎨',
            'BACKEND': '⚙️',
            'BASE_DE_DATOS': '🗄️',
            'DOCUMENTACION': '📋',
            'PERSONALIZADO': '🔧',
        }
        return icons.get(self.tipo, '📂')

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'proyectos'
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'


# --- 3. MODELO DE ETIQUETAS ---
class Etiqueta(models.Model):
    nombre = models.CharField(max_length=150)
    color = models.CharField(max_length=7, help_text="Código hexadecimal del color")
    porcentaje = models.PositiveIntegerField(default=0, help_text="Porcentaje de avance que representa esta fase")
    es_fase = models.BooleanField(default=False, help_text="Indica si pertenece a la línea de procesos de desarrollo")
    orden = models.PositiveIntegerField(default=0, help_text="Orden en la línea de procesos")

    def __str__(self):
        if self.es_fase and self.porcentaje > 0:
            return f"{self.nombre} ({self.porcentaje}%)"
        return self.nombre

    class Meta:
        db_table = 'etiquetas'
        verbose_name = 'Etiqueta'
        verbose_name_plural = 'Etiquetas'
        ordering = ['orden', 'id']


# --- 4. MODELO PRINCIPAL: TAREAS 
class Task(models.Model):
    title = models.CharField(max_length=255, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")

    column = models.ForeignKey(
        KanbanColumn,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Columna/Estado"
    )

    PRIORIDADES_TAREA = [
        ('ALTA', 'Alta'),
        ('MEDIA', 'Media'),
        ('BAJA', 'Baja'),
    ]

    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDADES_TAREA,
        default='MEDIA',
        verbose_name="Prioridad"
    )

    horas_estimadas = models.PositiveIntegerField(
        default=0,
        verbose_name="Horas Estimadas"
    )

    fecha_inicio = models.DateField(
        null=True, blank=True,
        verbose_name="Fecha Estimada de Inicio"
    )

    fecha_limite = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Fecha Límite (Countdown)"
    )

    archivo = models.FileField(
        upload_to='entregables/', 
        null=True, 
        blank=True, 
        verbose_name="Archivo Adjunto"
    )

    etiquetas_relacionadas = models.ManyToManyField(
        'Etiqueta', 
        through='TareaEtiqueta', 
        related_name='tareas_asociadas', 
        blank=True
    )


    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='assigned_to',
        related_name='assigned_tasks',
        verbose_name="Asignado a"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='created_by',
        related_name='tasks_created',
        verbose_name="Creado por"
    )

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )

    @property
    def es_atrasada(self):
        """
        Determina si una tarea está atrasada sin requerir nuevas columnas en la BD.
        Una tarea está atrasada si:
        - Su fecha límite ya expiró mientras no está en LISTO.
        - O si ya está en LISTO (aprobada), pero su entrega/aprobación ocurrió después de la fecha límite
          o fue registrada como atrasada en el historial.
        """
        if not self.fecha_limite:
            return False

        from django.utils import timezone
        now = timezone.now()

        # Si ya está en LISTO (aprobada):
        if self.column and self.column.name == 'LISTO':
            # Revisar si en el historial hay marca de atrasada o si se aprobó después de la fecha límite
            try:
                historiales = list(self.historial.all())
                for h in historiales:
                    if h.estado_nuevo == 'ATRASADA':
                        return True
                    if h.estado_nuevo == 'LISTO' and h.fecha_cambio and h.fecha_cambio > self.fecha_limite:
                        return True
            except Exception:
                pass
            # Si la fecha límite ya había expirado
            return now > self.fecha_limite

        # Si está en POR_HACER, EN_PROCESO o EN_REVISION:
        return now > self.fecha_limite

    @property
    def esta_atrasada(self):
        return self.es_atrasada

    def __str__(self):
        return self.title

    class Meta:
        managed = True
        db_table = 'tareas'
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'


# --- 5. RELACIÓN MUCHOS A MUCHOS: TAREA - ETIQUETA ---
class TareaEtiqueta(models.Model):
    tarea = models.ForeignKey(Task, on_delete=models.CASCADE)
    etiqueta = models.ForeignKey(Etiqueta, on_delete=models.CASCADE)
    asignado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tarea_etiquetas'
        verbose_name = "Relación Tarea-Etiqueta"
        verbose_name_plural = "Relaciones Tareas-Etiquetas"




# --- 7. HISTORIAL DE CAMBIOS ---
class HistorialTarea(models.Model):
    tarea = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=50)
    estado_nuevo = models.CharField(max_length=50)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'historial_tareas'
        verbose_name = 'Historial de Tarea'
        verbose_name_plural = 'Historiales de Tareas'


# --- 8. TIEMPO DE TRABAJO ---
class TiempoTarea(models.Model):
    tarea = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='tiempos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    horas_invertidas = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_registro = models.DateField()
    descripcion = models.TextField(blank=True)

    class Meta:
        db_table = 'tiempos_tareas'
        verbose_name = 'Tiempo de Tarea'
        verbose_name_plural = 'Tiempos de Tareas'


# --- 9. NOTAS / COMENTARIOS ---
class TaskNote(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, db_column='task_id', verbose_name="Tarea")
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id', verbose_name="Usuario")
    content = models.TextField(verbose_name="Contenido")

    class Meta:
        managed = True
        db_table = 'notas'
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'


# --- 10. MODELO DE REPORTES ---
class Reporte(models.Model):
    titulo = models.CharField(max_length=100, verbose_name="Título")
    contenido = models.TextField(verbose_name="Contenido")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    tipo_reporte = models.CharField(max_length=50, verbose_name="Tipo de Reporte") 
    
    autor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Autor"
    )
    proyecto = models.ForeignKey(
        Proyecto, 
        on_delete=models.CASCADE, 
        related_name='reportes',
        verbose_name="Proyecto"
    )

    def __str__(self):
        return f"{self.titulo} - {self.fecha_creacion.strftime('%d/%m/%Y')}"

    class Meta:
        db_table = 'reporte'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
# --- 11. TABLA FÍSICA PARA PROYECTOS INHABILITADOS ---
class ProyectoInhabilitado(models.Model):
    proyecto_original = models.OneToOneField(Proyecto, on_delete=models.CASCADE, verbose_name='Proyecto Original')
    fecha_inhabilitacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Inhabilitación')
    inhabilitado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Inhabilitado Por')

    def __str__(self):
        return f"Inhabilitado: {self.proyecto_original.nombre}"

    class Meta:
        db_table = 'proyectos_inhabilitados_historial'
        verbose_name = 'Proyecto Inhabilitado'
        verbose_name_plural = 'Proyectos Inhabilitados'


# --- 11.1 TABLA FÍSICA PARA PROYECTOS CULMINADOS ---
class ProyectoCulminado(models.Model):
    proyecto_original = models.OneToOneField(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='culminado_registro',
        verbose_name='Proyecto Original'
    )
    fecha_culminacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Culminación')
    culminado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Culminado Por'
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones de Cierre')

    def __str__(self):
        return f"Culminado: {self.proyecto_original.nombre}"

    class Meta:
        db_table = 'proyectos_culminados'
        verbose_name = 'Proyecto Culminado'
        verbose_name_plural = 'Proyectos Culminados'


# --- 12. MODELO PARA ACTA DE RECEPCIÓN DE REQUERIMIENTO (ACEPTACIÓN DE PROYECTO) ---
class ActaRecepcion(models.Model):
    ESTADOS_ACTA = [
        ('PENDIENTE', 'Pendiente de Aprobación'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    proyecto = models.OneToOneField(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='acta_recepcion',
        verbose_name='Proyecto'
    )
    fecha = models.DateField(auto_now_add=True, verbose_name='Fecha de Documento')
    siglas_solucion = models.CharField(max_length=50, blank=True, null=True, verbose_name='Siglas de la Solución')
    gerencia_receptora = models.CharField(max_length=250, blank=True, null=True, verbose_name='Gerencia Receptora')
    nombre_cliente_funcional = models.CharField(max_length=250, blank=True, null=True, verbose_name='Nombre Cliente Funcional')
    unidad_funcional = models.CharField(max_length=250, blank=True, null=True, verbose_name='Unidad Funcional')

    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción del Requerimiento')
    entregables = models.TextField(blank=True, null=True, verbose_name='Entregables')
    observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    detalles = models.TextField(blank=True, null=True, verbose_name='Detalles')

    # Firmas Autorizadas - Hoja 2
    firmante_1_nombre = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 1 - Nombre y Apellido')
    firmante_1_unidad = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 1 - Unidad')
    firmante_2_nombre = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 2 - Nombre y Apellido')
    firmante_2_unidad = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 2 - Unidad')
    firmante_3_nombre = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 3 - Nombre y Apellido')
    firmante_3_unidad = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 3 - Unidad')
    firmante_4_nombre = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 4 - Nombre y Apellido')
    firmante_4_unidad = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 4 - Unidad')
    firmante_5_nombre = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 5 - Nombre y Apellido')
    firmante_5_unidad = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 5 - Unidad')
    firmante_6_nombre = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 6 - Nombre y Apellido')
    firmante_6_unidad = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 6 - Unidad')
    firmante_7_nombre = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 7 - Nombre y Apellido')
    firmante_7_unidad = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 7 - Unidad')
    firmante_8_nombre = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 8 - Nombre y Apellido')
    firmante_8_unidad = models.CharField(max_length=250, blank=True, null=True, verbose_name='Firmante 8 - Unidad')

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_ACTA,
        default='PENDIENTE',
        verbose_name='Estado de Aprobación'
    )
    aprobado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actas_aprobadas',
        verbose_name='Aprobado Por'
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Aprobación')

    def __str__(self):
        return f"Acta de Recepción ({self.proyecto.nombre}) - {self.get_estado_display()}"

    class Meta:
        db_table = 'actas_recepcion'
        verbose_name = 'Acta de Recepción de Requerimiento'
        verbose_name_plural = 'Actas de Recepción de Requerimiento'


# --- 13. MODELO DE NOTIFICACIONES POR PROYECTO ---
class NotificacionProyecto(models.Model):
    TIPOS = [
        ('COMENTARIO', 'Comentario en Tarea'),
        ('TAREA_FINALIZADA', 'Tarea Finalizada'),
        ('PROYECTO_FINALIZADO', 'Proyecto Finalizado'),
        ('EN_REVISION', 'Tarea Enviada a Revisión'),
    ]

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name='Proyecto'
    )
    tarea = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificaciones',
        verbose_name='Tarea Asociada'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuario Emisor'
    )
    tipo = models.CharField(max_length=30, choices=TIPOS, default='COMENTARIO', verbose_name='Tipo')
    mensaje = models.TextField(verbose_name='Mensaje')
    leida = models.BooleanField(default=False, verbose_name='Leída')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Notificación')

    def __str__(self):
        return f"[{self.tipo}] {self.proyecto.nombre} - {self.mensaje[:40]}"

    class Meta:
        db_table = 'notificaciones_proyecto'
        verbose_name = 'Notificación de Proyecto'
        verbose_name_plural = 'Notificaciones de Proyectos'
        ordering = ['-fecha_creacion']