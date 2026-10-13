"""
SISTEMA DE GESTIÓN DE ACTIVIDADES 
Descripción: Gestión de autenticación, registro con restricciones robustas y Dashboard.
"""

import re  # Módulo para Expresiones Regulares
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages 
from .models import TaskNote, Proyecto, Task, TAREAS_PRECARGADAS, KanbanColumn, Etiqueta, HistorialTarea, TiempoTarea, Reporte, ActaRecepcion, NotificacionProyecto
from .forms import ProyectoForm, TaskForm, ManagerTaskForm, ActaRecepcionForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from functools import wraps

def gerente_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        rol = 'GERENTE'
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
            rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')
        if rol not in ['GERENTE', 'JEFE'] and not request.user.is_superuser:
            messages.error(request, 'Acceso denegado: no tienes permiso para acceder a esta sección.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def jefe_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        rol = 'GERENTE'
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
            rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')
        if rol != 'JEFE' and not request.user.is_superuser:
            messages.error(request, 'Acceso denegado: solo el Jefe puede acceder a esta sección.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def crear_actas_required(view_func):
    """Permite acceso a Crear Actas para: Gerente, Desarrollador, Analista y Analista Especializado."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        rol = 'GERENTE'
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
            rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')
        roles_permitidos = ['GERENTE', 'DESARROLLADOR', 'ANALISTA', 'ANALISTA_ESPECIALIZADO']
        if rol not in roles_permitidos and not request.user.is_superuser:
            messages.error(request, 'Acceso denegado: no tienes permiso para acceder a Crear Actas.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# 1. VISTA DE LOGIN
def login_usuario(request):
    error = None
    if request.method == 'POST':
        usuario_input = (request.POST.get('usuario') or '').strip()
        clave = request.POST.get('password')
        
        # El sistema permite iniciar sesión tanto con correo como con nombre de usuario
        user_obj = User.objects.filter(Q(email__iexact=usuario_input) | Q(username__iexact=usuario_input)).first()
        if user_obj:
            usuario_para_auth = user_obj.username
        else:
            usuario_para_auth = usuario_input

        # El sistema aplica el algoritmo de cifrado y compara el hash
        user = authenticate(request, username=usuario_para_auth, password=clave)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = "Nombre de usuario, correo o contraseña incorrectos."

    return render(request, 'proyectos/index.html', {'error': error})

# 2. VISTA DE REGISTRO CON RESTRICCIONES ACTUALIZADAS
def registro(request):
    messages.error(request, 'El registro público está deshabilitado. Solo el Jefe puede registrar nuevos empleados.')
    return redirect('login_usuario')

# 3. VISTA DEL HOME
@login_required
def home(request):
    from datetime import date
    if not request.user.is_authenticated:
        return redirect('login_usuario')
        
    rol = 'GERENTE'
    if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
        rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')

    if rol == 'DESARROLLADOR':
        proyectos_ids = Task.objects.filter(assigned_to=request.user, proyecto__isnull=False).values_list('proyecto_id', flat=True).distinct()
        
        # Obtener los proyectos que son padre o que son los padres de los módulos donde tiene tareas
        proyectos_donde_hay_tareas = Proyecto.objects.filter(id__in=proyectos_ids)
        padres_ids = set()
        for p in proyectos_donde_hay_tareas:
            if p.proyecto_padre_id:
                padres_ids.add(p.proyecto_padre_id)
            else:
                padres_ids.add(p.id)
                
        proyectos = Proyecto.objects.filter(id__in=padres_ids, activo=True)
        tiene_tareas_generales = Task.objects.filter(assigned_to=request.user, proyecto__isnull=True).exists()
        return render(request, 'proyectos/home_dev.html', {
            'proyectos': proyectos,
            'tiene_tareas_generales': tiene_tareas_generales,
            'today': date.today(),
        })
    elif rol == 'ANALISTA_ESPECIALIZADO':
        # Ve TODOS los proyectos para poder ayudar a cualquier desarrollador
        proyectos = Proyecto.objects.filter(activo=True, proyecto_padre__isnull=True)
        tiene_tareas_generales = Task.objects.filter(proyecto__isnull=True).exists()
        return render(request, 'proyectos/home_analista_especializado.html', {
            'proyectos': proyectos,
            'tiene_tareas_generales': tiene_tareas_generales,
            'today': date.today(),
        })
    elif rol == 'JEFE':
        proyectos = Proyecto.objects.filter(activo=True, proyecto_padre__isnull=True)
        # Crear ActaRecepcion para proyectos activos que aún no la tengan
        for p in proyectos:
            ActaRecepcion.objects.get_or_create(proyecto=p)
        tareas_en_revision = Task.objects.filter(
            column__name='EN_REVISION',
            proyecto__activo=True
        ).filter(
            Q(proyecto__proyecto_padre__isnull=True) | Q(proyecto__proyecto_padre__activo=True)
        ).count()
        actas_pendientes_count = ActaRecepcion.objects.filter(estado='PENDIENTE', proyecto__activo=True).count()
        return render(request, 'proyectos/home_jefe.html', {
            'proyectos': proyectos,
            'today': date.today(),
            'tareas_en_revision': tareas_en_revision,
            'actas_pendientes_count': actas_pendientes_count,
        })
    elif rol == 'ANALISTA':
        proyectos = Proyecto.objects.filter(activo=True, proyecto_padre__isnull=True)
        return render(request, 'proyectos/home_analista.html', {
            'proyectos': proyectos,
            'today': date.today(),
        })
    else:
        # GERENTE
        proyectos = Proyecto.objects.filter(activo=True, proyecto_padre__isnull=True)
        for p in proyectos:
            ActaRecepcion.objects.get_or_create(proyecto=p)
        tareas_en_revision = Task.objects.filter(
            column__name='EN_REVISION',
            proyecto__activo=True
        ).filter(
            Q(proyecto__proyecto_padre__isnull=True) | Q(proyecto__proyecto_padre__activo=True)
        ).count()
        actas_pendientes_count = ActaRecepcion.objects.filter(estado='PENDIENTE', proyecto__activo=True).count()
        return render(request, 'proyectos/home.html', {
            'proyectos': proyectos,
            'today': date.today(),
            'tareas_en_revision': tareas_en_revision,
            'actas_pendientes_count': actas_pendientes_count,
        })

# 4. VISTA DE LOGOUT
def cerrar_sesion(request):
    logout(request)
    return redirect('login_usuario')

@login_required
@jefe_required
def registro_jefe(request):
    from proyectos.models import Rol, PerfilEmpleado, Gerencia
    roles = Rol.objects.all().order_by('name')
    gerencias = Gerencia.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        correo = request.POST.get('correo', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        rol_id = request.POST.get('rol_id')
        gerencia_id = request.POST.get('gerencia_id')
        pass1 = request.POST.get('pass1', '')
        pass2 = request.POST.get('pass2', '')
        
        if not nombre or not apellido or not correo or not rol_id or not pass1:
            messages.error(request, '⚠️ Todos los campos obligatorios deben ser completados.')
        elif pass1 != pass2:
            messages.error(request, '⚠️ Las contraseñas no coinciden.')
        elif User.objects.filter(email=correo).exists():
            messages.error(request, '⚠️ Ya existe un usuario con este correo electrónico.')
        else:
            username = correo.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            try:
                user = User.objects.create_user(
                    username=username,
                    email=correo,
                    password=pass1,
                    first_name=nombre,
                    last_name=apellido
                )
                
                rol_obj = Rol.objects.get(id=rol_id)
                gerencia_obj = Gerencia.objects.get(id=gerencia_id) if gerencia_id else None

                PerfilEmpleado.objects.create(
                    usuario=user,
                    rol_maestro=rol_obj,
                    gerencia=gerencia_obj,
                    telefono=telefono
                )
                
                messages.success(request, f'✅ Usuario "{user.get_full_name() or user.username}" registrado exitosamente con el rol {rol_obj.name}.')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'⚠️ Error al registrar el usuario: {str(e)}')
                
    return render(request, 'proyectos/registro_jefe.html', {'roles': roles, 'gerencias': gerencias})

@login_required
def marcar_notificaciones_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    if request.method == 'POST':
        proyecto.get_notificaciones_para_usuario(request.user).filter(leida=False).update(leida=True)
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'home'
    return redirect(next_url)


@login_required
@gerente_required
def crear_proyecto(request):
    rol = 'GERENTE'
    if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
        rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')
    if rol == 'JEFE':
        messages.error(request, '⛔ El rol de Jefe no tiene permiso para crear proyectos.')
        return redirect('home')

    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.gerencia:
                proyecto.gerencia = request.user.perfil.gerencia
            proyecto.save()
            # Crear Acta de Recepción para el proyecto
            ActaRecepcion.objects.get_or_create(proyecto=proyecto)
            # --- Crear tareas pre-cargadas según el tipo de proyecto ---
            tareas_tipo = TAREAS_PRECARGADAS.get(proyecto.tipo, [])
            for titulo, descripcion in tareas_tipo:
                t = Task.objects.create(
                    title=titulo,
                    description=descripcion,
                    proyecto=proyecto,
                    created_by=request.user,
                    assigned_to=request.user,  # sin asignar aún: se asigna después
                    column=KanbanColumn.objects.get_or_create(name='POR_HACER', defaults={'position': 1})[0],
                )
            if tareas_tipo:
                messages.success(
                    request,
                    f'✅ Proyecto "{proyecto.nombre}" creado con {len(tareas_tipo)} tareas pre-cargadas. '
                    f'Ahora asigna cada tarea a un desarrollador.'
                )
            else:
                messages.success(request, '✅ Proyecto creado con éxito. Puedes crear las tareas manualmente.')
            return redirect('home')
    else:
        form = ProyectoForm()
    return render(request, 'proyectos/crear_proyecto.html', {'form': form})
    
@login_required
@gerente_required
def crear_modulo(request, parent_id):
    rol = 'GERENTE'
    if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
        rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')
    if rol == 'JEFE':
        messages.error(request, '⛔ El rol de Jefe no tiene permiso para crear proyectos ni módulos.')
        return redirect('home')

    proyecto_padre = get_object_or_404(Proyecto, id=parent_id)
    if request.method == 'POST':
        post_data = request.POST.copy()
        # Generar un identificador único basado en el padre + sufijo incremental
        base_id = str(proyecto_padre.identificador) if proyecto_padre.identificador else "MOD"
        nuevo_id = base_id
        suffix = 1
        while Proyecto.objects.filter(identificador=nuevo_id).exists():
            suffix_str = str(suffix).zfill(2)
            max_base_len = 12 - len(suffix_str)
            nuevo_id = base_id[:max_base_len] + suffix_str
            suffix += 1
        post_data['identificador'] = nuevo_id

        form = ProyectoForm(post_data)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.proyecto_padre = proyecto_padre
            proyecto.identificador = nuevo_id
            proyecto.save()
            # Crear Acta de Recepción para el módulo
            ActaRecepcion.objects.get_or_create(proyecto=proyecto)
            
            # --- Crear tareas pre-cargadas según el tipo de proyecto ---
            tareas_tipo = TAREAS_PRECARGADAS.get(proyecto.tipo, [])
            for titulo, descripcion in tareas_tipo:
                t = Task.objects.create(
                    title=titulo,
                    description=descripcion,
                    proyecto=proyecto,
                    created_by=request.user,
                    assigned_to=request.user,
                    column=KanbanColumn.objects.get_or_create(name='POR_HACER', defaults={'position': 1})[0],
                )
            if tareas_tipo:
                messages.success(
                    request,
                    f'✅ Módulo "{proyecto.nombre}" creado con {len(tareas_tipo)} tareas pre-cargadas. '
                    f'Ahora asigna cada tarea a un desarrollador.'
                )
            else:
                messages.success(request, f'✅ Módulo "{proyecto.nombre}" creado con éxito. Puedes crear las tareas manualmente.')
            return redirect('home')
    else:
        form = ProyectoForm(initial={'identificador': proyecto_padre.identificador})
        
    return render(request, 'proyectos/crear_proyecto.html', {
        'form': form,
        'proyecto_padre': proyecto_padre
    })
    
@login_required
@gerente_required
def gestionar_asignaciones(request, proyecto_id):
    """
    Panel del gerente para gestionar la asignación de tareas de un proyecto.
    Permite:
      - Asignar desarrollador a una tarea individual (POST action=individual)
      - Asignar todas las tareas sin desarrollador a un mismo usuario (POST action=asignar_todos)
      - Crear nuevas tareas manualmente (POST action=nueva_tarea)
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    # Determinar el rol del usuario actual
    rol_usuario = 'GERENTE'
    if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
        rol_usuario = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')

    gerencia_actual = getattr(getattr(request.user, 'perfil', None), 'gerencia', None)

    if rol_usuario == 'JEFE':
        # El jefe puede asignar a todos los desarrolladores, analistas y gerentes del equipo
        desarrolladores = User.objects.filter(
            is_active=True, 
            is_superuser=False
        ).exclude(perfil__rol_maestro__name__iexact='JEFE').order_by('first_name', 'username')
    else:
        # El gerente solo puede asignar a trabajadores de su misma gerencia o a otros GERENTES (para pasar tareas/proyectos)
        query_gerencia = Q(perfil__rol_maestro__name__iexact='GERENTE')
        if gerencia_actual:
            query_gerencia |= Q(perfil__gerencia=gerencia_actual)

        desarrolladores = User.objects.filter(is_active=True, is_superuser=False).filter(
            query_gerencia
        ).exclude(
            perfil__rol_maestro__name__iexact='JEFE'
        ).exclude(
            id=request.user.id
        ).order_by('first_name', 'username')

    fases_desarrollo = Etiqueta.objects.filter(es_fase=True).order_by('orden', 'id')
    etiquetas = Etiqueta.objects.all()
    tareas = Task.objects.filter(proyecto=proyecto).prefetch_related('etiquetas_relacionadas').order_by('id')

    if request.method == 'POST':
        action = request.POST.get('action')

        # --- Asignación individual de una tarea y/o fase de desarrollo ---
        if action == 'individual':
            tarea_id = request.POST.get('tarea_id')
            dev_id   = request.POST.get('dev_id')
            fase_id  = request.POST.get('fase_id')
            tarea = get_object_or_404(Task, pk=tarea_id, proyecto=proyecto)

            # Reasignación de desarrollador si se especificó
            if dev_id:
                dev = get_object_or_404(User, pk=dev_id)
                # Validar que un gerente no se asigne tareas a sí mismo
                if rol_usuario == 'GERENTE' and dev.id == request.user.id:
                    messages.error(request, '⚠️ No puedes asignarte tareas a ti mismo.')
                else:
                    tarea.assigned_to = dev
                    tarea.save()
                    HistorialTarea.objects.create(
                        tarea=tarea,
                        usuario=request.user,
                        estado_anterior="N/A", estado_nuevo="ASIGNADO"
                    )
                    messages.success(request, f'✅ Tarea "{tarea.title}" asignada a {dev.get_full_name() or dev.username}.')

            # Asignación o cambio de fase de desarrollo
            if 'fase_id' in request.POST:
                fases_previas = tarea.etiquetas_relacionadas.filter(es_fase=True)
                if fases_previas.exists():
                    tarea.etiquetas_relacionadas.remove(*fases_previas)
                if fase_id:
                    try:
                        fase_obj = Etiqueta.objects.get(id=fase_id, es_fase=True)
                        tarea.etiquetas_relacionadas.add(fase_obj)
                    except Etiqueta.DoesNotExist:
                        pass
                if not dev_id:
                    messages.success(request, f'✅ Fase de la tarea "{tarea.title}" actualizada.')

        # --- Asignar TODAS las tareas sin asignar a un desarrollador ---
        elif action == 'asignar_todos':
            dev_id = request.POST.get('dev_id_todos')
            dev    = get_object_or_404(User, pk=dev_id)
            # Solo reasigna las que aún tienen assigned_to = gerente (el que creó el proyecto)
            sin_asignar = tareas.filter(assigned_to=proyecto.tasks.first().created_by if tareas.exists() else request.user)
            count = sin_asignar.count()
            sin_asignar.update(assigned_to=dev)
            messages.success(request, f'✅ {count} tarea(s) asignadas a {dev.get_full_name() or dev.username}.')

        # --- Crear nueva tarea (solo para Proyecto Personalizado) ---
        elif action == 'nueva_tarea':
            if rol_usuario == 'JEFE':
                messages.error(request, '⛔ El rol de Jefe no tiene permiso para crear tareas directamente.')
                return redirect('gestionar_asignaciones', proyecto_id=proyecto.id)
            titulo      = request.POST.get('titulo', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            dev_id      = request.POST.get('dev_id_nueva')
            fase_id     = request.POST.get('fase_id')
            prioridad   = request.POST.get('prioridad', 'MEDIA')
            horas_estimadas = request.POST.get('horas_estimadas', 0)
            try: horas_estimadas = int(horas_estimadas)
            except ValueError: horas_estimadas = 0
            from django.utils import timezone
            from proyectos.utils import add_business_hours
            fecha_limite = add_business_hours(timezone.now(), horas_estimadas) if horas_estimadas > 0 else None

            if titulo:
                dev = get_object_or_404(User, pk=dev_id) if dev_id else request.user
                archivo = request.FILES.get('archivo_nueva')
                t = Task.objects.create(
                    archivo=archivo,
                    title=titulo,
                    description=descripcion,
                    proyecto=proyecto,
                    created_by=request.user,
                    assigned_to=dev,
                    column=KanbanColumn.objects.get_or_create(name='POR_HACER', defaults={'position': 1})[0],
                    prioridad=prioridad,
                    horas_estimadas=horas_estimadas,
                    fecha_limite=fecha_limite,
                )
                if fase_id:
                    try:
                        fase_obj = Etiqueta.objects.get(id=fase_id, es_fase=True)
                        t.etiquetas_relacionadas.add(fase_obj)
                    except Etiqueta.DoesNotExist:
                        pass

                if dev_id:
                    messages.success(request, f'✅ Tarea "{titulo}" creada y asignada correctamente.')
                else:
                    messages.success(request, f'✅ Tarea "{titulo}" creada correctamente (sin asignar).')
            else:
                messages.error(request, '⚠️ El título de la tarea no puede estar vacío.')

        return redirect('gestionar_asignaciones', proyecto_id=proyecto.id)

    # --- Contexto para el template ---
    # Roles que pueden tener tareas propias (no son gerente ni jefe)
    ROLES_DEV = {'DESARROLLADOR', 'ANALISTA_ESPECIALIZADO', 'ANALISTA'}

    # Pre-cargar roles de los creadores para no hacer N queries
    creator_ids = tareas.values_list('created_by_id', flat=True).distinct()
    from django.contrib.auth import get_user_model
    _User = get_user_model()
    creator_roles = {}
    for u in _User.objects.filter(id__in=creator_ids).select_related('perfil__rol_maestro'):
        rol_name = ''
        if hasattr(u, 'perfil') and u.perfil and u.perfil.rol_maestro:
            rol_name = u.perfil.rol_maestro.name.upper().replace(' ', '_')
        creator_roles[u.id] = rol_name

    tareas_info = []
    for tarea in tareas:
        creator_rol = creator_roles.get(tarea.created_by_id, '')
        # Tarea propia del desarrollador: la creó él mismo y se la asignó a sí mismo
        es_propia_dev = (
            tarea.assigned_to_id == tarea.created_by_id
            and creator_rol in ROLES_DEV
        )
        # Sin asignar: assigned_to == created_by y el creador NO es un desarrollador (es gerente)
        sin_asignar = (tarea.assigned_to_id == tarea.created_by_id) and not es_propia_dev
        fase_tarea = next((e for e in tarea.etiquetas_relacionadas.all() if e.es_fase), None)
        tareas_info.append({
            'tarea': tarea,
            'sin_asignar': sin_asignar,
            'es_propia_dev': es_propia_dev,
            'fase': fase_tarea,
        })

    return render(request, 'proyectos/gestionar_asignaciones.html', {
        'proyecto': proyecto,
        'desarrolladores': desarrolladores,
        'etiquetas': etiquetas,
        'fases_desarrollo': fases_desarrollo,
        'tareas_info': tareas_info,
        'total': tareas.count(),
        'sin_asignar': sum(1 for t in tareas_info if t['sin_asignar']),
        'rol_usuario': rol_usuario,
    })

@login_required
@gerente_required
def gestionar_tareas_generales(request):
    """
    Panel del gerente para gestionar tareas sin proyecto.
    """
    # Determinar el rol del usuario actual
    rol_usuario = 'GERENTE'
    if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
        rol_usuario = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')

    gerencia_actual = getattr(getattr(request.user, 'perfil', None), 'gerencia', None)

    if rol_usuario == 'JEFE':
        # El rol de Jefe solo puede asignar tareas generales a los Gerentes de cualquier gerencia
        desarrolladores = User.objects.filter(
            is_active=True, 
            is_superuser=False,
            perfil__rol_maestro__name__iexact='GERENTE'
        ).order_by('first_name', 'username')
    else:
        query_gerencia = Q(perfil__rol_maestro__name__iexact='GERENTE')
        if gerencia_actual:
            query_gerencia |= Q(perfil__gerencia=gerencia_actual)

        desarrolladores = User.objects.filter(is_active=True, is_superuser=False).filter(
            query_gerencia
        ).exclude(
            perfil__rol_maestro__name__iexact='JEFE'
        ).exclude(
            id=request.user.id
        ).order_by('first_name', 'username')

    etiquetas = Etiqueta.objects.all()
    tareas = Task.objects.filter(proyecto__isnull=True).order_by('id')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'individual':
            tarea_id = request.POST.get('tarea_id')
            dev_id   = request.POST.get('dev_id')
            tarea = get_object_or_404(Task, pk=tarea_id, proyecto__isnull=True)
            dev   = get_object_or_404(User, pk=dev_id)

            dev_rol = dev.perfil.rol_maestro.name.upper().replace(' ', '_') if (hasattr(dev, 'perfil') and dev.perfil and dev.perfil.rol_maestro) else ''

            # Validar que un gerente no se asigne tareas a sí mismo
            if rol_usuario == 'GERENTE' and dev.id == request.user.id:
                messages.error(request, '⚠️ No puedes asignarte tareas a ti mismo.')
            elif rol_usuario == 'JEFE' and dev_rol != 'GERENTE':
                messages.error(request, '⚠️ Como Jefe, solo puedes asignar tareas generales a usuarios con rol de Gerente.')
            else:
                tarea.assigned_to = dev
                tarea.save()
                HistorialTarea.objects.create(
                    tarea=tarea,
                    usuario=request.user,
                    estado_anterior="N/A", estado_nuevo="ASIGNADO"
                )
                messages.success(request, f'✅ Tarea "{tarea.title}" asignada a {dev.get_full_name() or dev.username}.')

        elif action == 'nueva_tarea':
            if rol_usuario == 'JEFE':
                messages.error(request, '⛔ El rol de Jefe no tiene permiso para crear tareas generales.')
                return redirect('gestionar_tareas_generales')
            titulo      = request.POST.get('titulo', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()
            dev_id      = request.POST.get('dev_id_nueva')
            prioridad   = request.POST.get('prioridad', 'MEDIA')
            horas_estimadas = request.POST.get('horas_estimadas', 0)
            try: horas_estimadas = int(horas_estimadas)
            except ValueError: horas_estimadas = 0
            from django.utils import timezone
            from proyectos.utils import add_business_hours
            fecha_limite = add_business_hours(timezone.now(), horas_estimadas) if horas_estimadas > 0 else None

            if titulo:
                if dev_id:
                    dev = get_object_or_404(User, pk=dev_id)
                else:
                    if rol_usuario == 'JEFE':
                        messages.error(request, '⚠️ Como Jefe, debes seleccionar un Gerente para asignarle la tarea general.')
                        return redirect('gestionar_tareas_generales')
                    dev = request.user

                if rol_usuario == 'JEFE':
                    dev_rol = dev.perfil.rol_maestro.name.upper().replace(' ', '_') if (hasattr(dev, 'perfil') and dev.perfil and dev.perfil.rol_maestro) else ''
                    if dev_rol != 'GERENTE':
                        messages.error(request, '⚠️ Como Jefe, solo puedes asignar tareas generales a usuarios con rol de Gerente.')
                        return redirect('gestionar_tareas_generales')

                archivo = request.FILES.get('archivo_nueva')
                t = Task.objects.create(
                    archivo=archivo,
                    title=titulo,
                    description=descripcion,
                    created_by=request.user,
                    assigned_to=dev,
                    column=KanbanColumn.objects.get_or_create(name='POR_HACER', defaults={'position': 1})[0],
                    prioridad=prioridad,
                    horas_estimadas=horas_estimadas,
                    fecha_limite=fecha_limite,
                )
                messages.success(request, f'✅ Tarea General "{titulo}" creada y asignada correctamente.')
            else:
                messages.error(request, '⚠️ El título de la tarea no puede estar vacío.')

        return redirect('gestionar_tareas_generales')

    tareas_info = []
    gerente_ids = set(Task.objects.filter(proyecto__isnull=True).values_list('created_by', flat=True))
    for tarea in tareas:
        sin_asignar = (tarea.assigned_to_id == tarea.created_by_id)
        tareas_info.append({
            'tarea': tarea,
            'sin_asignar': sin_asignar,
        })

    return render(request, 'proyectos/gestionar_tareas_generales.html', {
        'desarrolladores': desarrolladores,
        'etiquetas': etiquetas,
        'tareas_info': tareas_info,
        'total': tareas.count(),
        'sin_asignar': sum(1 for t in tareas_info if t['sin_asignar']),
        'rol_usuario': rol_usuario,
    })


@login_required
@gerente_required
def asignar_tarea(request, proyecto_id):
    """Redirecciona al nuevo panel de gestión de asignaciones."""
    return redirect('gestionar_asignaciones', proyecto_id=proyecto_id)

@login_required
@gerente_required
def lista_devs(request):
    rol = 'GERENTE'
    if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
        rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')

    usuarios = User.objects.filter(is_active=True, is_superuser=False).exclude(
        perfil__rol_maestro__name__iexact='JEFE'
    )

    if rol == 'GERENTE' and hasattr(request.user, 'perfil') and request.user.perfil.gerencia:
        usuarios = usuarios.filter(perfil__gerencia=request.user.perfil.gerencia)

    usuarios = usuarios.annotate(
        total_tareas=Count('assigned_tasks', filter=Q(assigned_tasks__proyecto__activo=True)),
        tareas_pendientes=Count('assigned_tasks', filter=Q(assigned_tasks__column__name='POR_HACER', assigned_tasks__proyecto__activo=True)),
        tareas_en_proceso=Count('assigned_tasks', filter=Q(assigned_tasks__column__name='EN_PROCESO', assigned_tasks__proyecto__activo=True)),
        tareas_en_revision=Count('assigned_tasks', filter=Q(assigned_tasks__column__name='EN_REVISION', assigned_tasks__proyecto__activo=True)),
        tareas_finalizadas=Count('assigned_tasks', filter=Q(assigned_tasks__column__name='LISTO', assigned_tasks__proyecto__activo=True))
    ).order_by('-total_tareas')

    # Cargar tareas asignadas de proyectos activos para cada desarrollador
    tareas_proyectos = Task.objects.filter(
        assigned_to__in=usuarios,
        proyecto__isnull=False,
        proyecto__activo=True
    ).select_related('proyecto', 'proyecto__proyecto_padre', 'column')

    from collections import defaultdict
    user_project_tasks = defaultdict(lambda: defaultdict(list))
    for t in tareas_proyectos:
        user_project_tasks[t.assigned_to_id][t.proyecto_id].append(t)

    for u in usuarios:
        proyectos_info = []
        for pid, task_list in user_project_tasks.get(u.id, {}).items():
            proy = task_list[0].proyecto
            total = len(task_list)
            pendientes = sum(1 for t in task_list if t.column and t.column.name == 'POR_HACER')
            en_proceso = sum(1 for t in task_list if t.column and t.column.name == 'EN_PROCESO')
            en_revision = sum(1 for t in task_list if t.column and t.column.name == 'EN_REVISION')
            finalizadas = sum(1 for t in task_list if t.column and t.column.name == 'LISTO')
            porcentaje = round((finalizadas / total) * 100) if total > 0 else 0

            proyectos_info.append({
                'proyecto': proy,
                'total': total,
                'pendientes': pendientes,
                'en_proceso': en_proceso,
                'en_revision': en_revision,
                'finalizadas': finalizadas,
                'porcentaje': porcentaje,
            })
        proyectos_info.sort(key=lambda x: x['total'], reverse=True)
        u.proyectos_asignados = proyectos_info

    tareas_en_revision = Task.objects.filter(
        column__name='EN_REVISION',
        proyecto__activo=True
    ).filter(
        Q(proyecto__proyecto_padre__isnull=True) | Q(proyecto__proyecto_padre__activo=True)
    ).count()

    return render(request, 'proyectos/desarrolladores.html', {
        'usuarios': usuarios,
        'rol': rol,
        'tareas_en_revision': tareas_en_revision,
    })

@login_required
@jefe_required
def lista_gerentes(request):
    gerentes = User.objects.filter(is_active=True, perfil__rol_maestro__name__iexact='GERENTE').order_by('first_name', 'username')
    
    for g in gerentes:
        proyectos_ids = Task.objects.filter(created_by=g, proyecto__isnull=False).values_list('proyecto_id', flat=True).distinct()
        g.proyectos_creados = proyectos_ids.count()
        g.proyectos_inhabilitados = g.proyectoinhabilitado_set.count()

    return render(request, 'proyectos/gerentes.html', {'gerentes': gerentes})

# 5. EDICIÓN DEL PROYECTO
@login_required
@gerente_required
def editar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == "POST":
        form = ProyectoForm(request.POST, instance=proyecto)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProyectoForm(instance=proyecto)
    return render(request, 'proyectos/editar_proyecto.html', {'form': form, 'proyecto': proyecto})

# 6. INHABILITACION DEL PROYECTO
@login_required
@gerente_required
def inhabilitar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == "POST":
        nombre = proyecto.nombre
        proyecto.activo = False
        proyecto.save()
        # Inhabilitar también submódulos si existen
        proyecto.modulos.all().update(activo=False)
        # Create record in new table
        from proyectos.models import ProyectoInhabilitado
        ProyectoInhabilitado.objects.get_or_create(
            proyecto_original=proyecto,
            defaults={'inhabilitado_por': request.user}
        )
        messages.success(request, f'⚠️ Proyecto "{nombre}" inhabilitado. Puedes restaurarlo desde la sección de proyectos inhabilitados.')
        return redirect('home')
    return redirect('home')

@login_required
@gerente_required
def finalizar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == "POST":
        if not proyecto.todas_tareas_finalizadas:
            messages.error(request, 'No puedes finalizar un proyecto con tareas pendientes.')
            return redirect('home')
        
        nombre = proyecto.nombre
        proyecto.activo = False
        proyecto.save()
        
        from proyectos.models import ProyectoCulminado
        ProyectoCulminado.objects.get_or_create(
            proyecto_original=proyecto,
            defaults={'culminado_por': request.user}
        )
        
        NotificacionProyecto.objects.create(
            proyecto=proyecto,
            usuario=request.user,
            tipo='PROYECTO_FINALIZADO',
            mensaje=f'El proyecto {proyecto.nombre} ha sido marcado como finalizado por {request.user.get_full_name() or request.user.username}.'
        )
        
        messages.success(request, f'✅ Proyecto "{nombre}" finalizado con éxito.')
        return redirect('home')
    return redirect('home')

@login_required
@gerente_required
def proyectos_inhabilitados(request):
    from proyectos.models import ProyectoInhabilitado
    # Get original projects from the new table
    cancelados_records = ProyectoInhabilitado.objects.all()
    cancelados = [record.proyecto_original for record in cancelados_records]
    return render(request, 'proyectos/cancelados.html', {'proyectos': cancelados})

@login_required
@gerente_required
def restaurar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == "POST":
        nombre = proyecto.nombre
        proyecto.activo = True
        proyecto.save()
        # Restaurar también submódulos si existen
        proyecto.modulos.all().update(activo=True)
        # Remove from the disabled table
        from proyectos.models import ProyectoInhabilitado
        ProyectoInhabilitado.objects.filter(proyecto_original=proyecto).delete()
        messages.success(request, f'✅ Proyecto "{nombre}" restaurado correctamente.')
        return redirect('proyectos_inhabilitados')
    return redirect('proyectos_inhabilitados')

@login_required
@gerente_required
def proyectos_culminados(request):
    from django.db.models import Count, Q
    proyectos = Proyecto.objects.filter(
        activo=False,
        proyecto_padre__isnull=True
    ).exclude(
        proyectoinhabilitado__isnull=False
    ).annotate(
        _tareas_count=Count('tasks'),
        _tareas_listas=Count('tasks', filter=Q(tasks__column__name='LISTO'))
    ).order_by('-id')

    # Attach as simple attributes to avoid property conflict
    for p in proyectos:
        p.num_total_tareas = p._tareas_count
        p.num_tareas_finalizadas = p._tareas_listas

    rol = 'GERENTE'
    if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
        rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')

    return render(request, 'proyectos/proyectos_culminados.html', {
        'proyectos': proyectos,
        'rol': rol,
    })

#Panel del desarollador y kanban
@login_required
def panel_desarrollador(request, proyecto_id):
    if proyecto_id == 0:
        proyecto = None
    else:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        if not proyecto.activo:
            messages.error(request, 'Este proyecto se encuentra inhabilitado. No puedes ver ni gestionar sus tareas.')
            return redirect('home')

    rol = 'GERENTE'
    if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
        rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')

    if rol == 'DESARROLLADOR':
        if proyecto is None:
            tareas = Task.objects.filter(proyecto__isnull=True, assigned_to=request.user)
        else:
            tareas = Task.objects.filter(Q(proyecto=proyecto) | Q(proyecto__proyecto_padre=proyecto), assigned_to=request.user)
    elif rol == 'ANALISTA_ESPECIALIZADO':
        # Ve todo el tablero Kanban para poder visualizar y ayudar
        if proyecto is None:
            tareas = Task.objects.filter(proyecto__isnull=True)
        else:
            tareas = Task.objects.filter(Q(proyecto=proyecto) | Q(proyecto__proyecto_padre=proyecto))
    else:
        # Analistas y Gerentes ven todo el tablero
        if proyecto is None:
            tareas = Task.objects.filter(proyecto__isnull=True)
        else:
            tareas = Task.objects.filter(Q(proyecto=proyecto) | Q(proyecto__proyecto_padre=proyecto))

    from django.utils import timezone
    from proyectos.models import KanbanColumn, HistorialTarea

    today = timezone.now().date()
    try:
        col_por_hacer = KanbanColumn.objects.get(name='POR_HACER')
        col_en_proceso = KanbanColumn.objects.get(name='EN_PROCESO')
        
        tareas_auto = tareas.filter(column=col_por_hacer, fecha_inicio__lte=today)
        for t in tareas_auto:
            t.column = col_en_proceso
            t.save()
            HistorialTarea.objects.create(
                tarea=t,
                estado_anterior=col_por_hacer.name,
                estado_nuevo=col_en_proceso.name,
                usuario=request.user
            )
    except (KanbanColumn.DoesNotExist, KanbanColumn.MultipleObjectsReturned):
        pass

    # Optimizar consultas pre-cargando notas, historial, tiempos y etiquetas relacionadas
    tareas = tareas.prefetch_related(
        'tasknote_set', 'tasknote_set__user',
        'historial', 'historial__usuario',
        'tiempos', 'tiempos__usuario',
        'etiquetas_relacionadas'
    )

    # Lista de desarrolladores para asignación desde Kanban según Gerencia
    gerencia_actual = getattr(getattr(request.user, 'perfil', None), 'gerencia', None)
    if rol == 'JEFE':
        desarrolladores = User.objects.filter(is_active=True, is_superuser=False).exclude(perfil__rol_maestro__name__iexact='JEFE').order_by('first_name', 'username')
    else:
        query_gerencia = Q(perfil__rol_maestro__name__iexact='GERENTE')
        if gerencia_actual:
            query_gerencia |= Q(perfil__gerencia=gerencia_actual)
        desarrolladores = User.objects.filter(is_active=True, is_superuser=False).filter(query_gerencia).exclude(perfil__rol_maestro__name__iexact='JEFE').exclude(id=request.user.id).order_by('first_name', 'username')
    etiquetas = Etiqueta.objects.all()
    # Comprobar si todas las tareas del desarrollador están finalizadas (todas en estado LISTO)
    tareas_dev = tareas.filter(assigned_to=request.user)
    total_dev_tasks = tareas_dev.count()
    todas_tareas_finalizadas = (total_dev_tasks > 0 and not tareas_dev.exclude(column__name__icontains='LISTO').exists())

    fecha_finalizacion_tareas = None
    if todas_tareas_finalizadas:
        from proyectos.models import HistorialTarea
        from django.utils.timezone import localtime
        ultimo_historial = HistorialTarea.objects.filter(
            tarea__in=tareas_dev, 
            estado_nuevo__icontains='LISTO'
        ).order_by('-fecha_cambio').first()
        if ultimo_historial:
            fecha_finalizacion_tareas = localtime(ultimo_historial.fecha_cambio)
    # IDs de tareas propias del desarrollador (created_by == assigned_to y creador es dev/analista)
    ROLES_DEV_KANBAN = {'DESARROLLADOR', 'ANALISTA_ESPECIALIZADO', 'ANALISTA'}
    from django.contrib.auth import get_user_model as _gum
    _Usr = _gum()
    _creator_ids = list(tareas.values_list('created_by_id', flat=True).distinct())
    _creator_roles_map = {}
    for _u in _Usr.objects.filter(id__in=_creator_ids).select_related('perfil__rol_maestro'):
        _r = ''
        if hasattr(_u, 'perfil') and _u.perfil and _u.perfil.rol_maestro:
            _r = _u.perfil.rol_maestro.name.upper().replace(' ', '_')
        _creator_roles_map[_u.id] = _r
    tareas_propias_dev_ids = set(
        t.pk for t in tareas
        if t.assigned_to_id == t.created_by_id and _creator_roles_map.get(t.created_by_id, '') in ROLES_DEV_KANBAN
    )
    from django.utils import timezone
    now = timezone.now()
    # Auto-registrar en el historial las tareas que ya superaron su fecha límite
    for t in tareas:
        if t.fecha_limite and now > t.fecha_limite:
            if not any(h.estado_nuevo == 'ATRASADA' for h in t.historial.all()):
                HistorialTarea.objects.get_or_create(
                    tarea=t,
                    estado_nuevo='ATRASADA',
                    defaults={'usuario': t.assigned_to, 'estado_anterior': 'SISTEMA'}
                )

    # Cálculo de avance según las fases de desarrollo (Línea de Procesos)
    fases_desarrollo = list(Etiqueta.objects.filter(es_fase=True).order_by('orden', 'id'))
    fases_progreso_detalle = []
    porcentaje_fases_realizado = 0
    porcentaje_fases_en_curso = 0

    for f in fases_desarrollo:
        # Tareas asociadas a esta fase visibles en este tablero
        tareas_fase = [t for t in tareas if any(e.id == f.id for e in t.etiquetas_relacionadas.all())]
        total_tf = len(tareas_fase)
        completadas_tf = len([t for t in tareas_fase if t.column.name == 'LISTO'])
        en_proceso_tf = len([t for t in tareas_fase if t.column.name in ['EN_PROCESO', 'EN_REVISION']])
        por_hacer_tf = len([t for t in tareas_fase if t.column.name == 'POR_HACER'])

        if total_tf > 0:
            if completadas_tf == total_tf:
                estado_fase = 'COMPLETADA'
                porcentaje_fase = f.porcentaje
            elif completadas_tf > 0:
                estado_fase = 'EN_PROCESO'
                porcentaje_fase = round(f.porcentaje * (completadas_tf / total_tf), 1)
            elif en_proceso_tf > 0:
                estado_fase = 'EN_PROCESO'
                porcentaje_fase = 0
            else:
                estado_fase = 'POR_HACER'
                porcentaje_fase = 0
        else:
            estado_fase = 'PENDIENTE'
            porcentaje_fase = 0

        porcentaje_fases_realizado += porcentaje_fase
        if estado_fase == 'EN_PROCESO':
            porcentaje_fases_en_curso += (f.porcentaje - porcentaje_fase)

        fases_progreso_detalle.append({
            'fase': f,
            'estado': estado_fase,
            'total_tareas': total_tf,
            'completadas': completadas_tf,
            'en_proceso': en_proceso_tf,
            'por_hacer': por_hacer_tf,
            'porcentaje_obtenido': int(porcentaje_fase) if isinstance(porcentaje_fase, float) and porcentaje_fase.is_integer() else porcentaje_fase,
        })

    porcentaje_fases_realizado = min(100, round(porcentaje_fases_realizado, 1))
    if isinstance(porcentaje_fases_realizado, float) and porcentaje_fases_realizado.is_integer():
        porcentaje_fases_realizado = int(porcentaje_fases_realizado)

    porcentaje_fases_en_curso = min(100, round(porcentaje_fases_en_curso, 1))
    if isinstance(porcentaje_fases_en_curso, float) and porcentaje_fases_en_curso.is_integer():
        porcentaje_fases_en_curso = int(porcentaje_fases_en_curso)

    fases_completadas_count = sum(1 for item in fases_progreso_detalle if item['estado'] == 'COMPLETADA')

    return render(request, 'proyectos/desarrollador.html', {
        'proyecto': proyecto,
        'tareas': tareas,
        'rol': rol,
        'desarrolladores': desarrolladores,
        'etiquetas': etiquetas,
        'fases_desarrollo': fases_desarrollo,
        'fases_progreso_detalle': fases_progreso_detalle,
        'porcentaje_fases_realizado': porcentaje_fases_realizado,
        'porcentaje_fases_en_curso': porcentaje_fases_en_curso,
        'fases_completadas_count': fases_completadas_count,
        'todas_tareas_finalizadas': todas_tareas_finalizadas,
        'fecha_finalizacion_tareas': fecha_finalizacion_tareas,
        'is_weekend': now.weekday() >= 5,
        'tareas_propias_dev_ids': tareas_propias_dev_ids,
    })


# 7. INHABILITACIÓN DEL PROYECTO (alias para compatibilidad — redirige a inhabilitar)
@login_required
@gerente_required
def eliminar_proyecto(request, pk):
    """Alias mantenido por compatibilidad. Redirige a inhabilitar_proyecto."""
    return inhabilitar_proyecto(request, pk)

@login_required
def eliminar_tarea(request, pk):
    tarea = get_object_or_404(Task, pk=pk)
    proyecto_id = tarea.proyecto.id if tarea.proyecto else 0
    if request.method == 'POST':
        rol = 'GERENTE'
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
            rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')

        # Detectar si es una tarea propia del desarrollador
        ROLES_DEV = {'DESARROLLADOR', 'ANALISTA_ESPECIALIZADO', 'ANALISTA'}
        creador = tarea.created_by
        creador_rol = ''
        if hasattr(creador, 'perfil') and creador.perfil and creador.perfil.rol_maestro:
            creador_rol = creador.perfil.rol_maestro.name.upper().replace(' ', '_')
        es_propia_dev = (
            tarea.assigned_to_id == tarea.created_by_id
            and creador_rol in ROLES_DEV
        )

        if es_propia_dev and rol in ['GERENTE', 'JEFE'] and not request.user.is_superuser:
            messages.error(request, '⛔ No puedes eliminar una tarea creada por el propio desarrollador.')
        elif rol in ['GERENTE', 'JEFE'] or request.user.is_superuser:
            # El gerente o jefe puede eliminar cualquier tarea (excepto propias del dev)
            tarea.delete()
            messages.success(request, '🗑️ Tarea eliminada correctamente.')
        elif rol in ['DESARROLLADOR', 'ANALISTA_ESPECIALIZADO', 'ANALISTA'] and tarea.created_by == request.user and tarea.assigned_to == request.user:
            tarea.delete()
            messages.success(request, '🗑️ Tarea eliminada correctamente.')
        else:
            messages.error(request, '⛔ No puedes eliminar una tarea asignada a otro usuario o creada por el gerente.')
    return redirect('panel_desarrollador', proyecto_id=proyecto_id)
@login_required
def dev_crear_tarea(request):
    """Permite al desarrollador crear una tarea para sí mismo (va a POR_HACER)."""
    if request.method == 'POST':
        titulo      = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        prioridad   = request.POST.get('prioridad', 'MEDIA')
        proyecto_id = request.POST.get('proyecto_id')
        etiquetas_ids = request.POST.getlist('etiquetas')
        horas_estimadas = request.POST.get('horas_estimadas', 0)
        try: horas_estimadas = int(horas_estimadas)
        except ValueError: horas_estimadas = 0
        from django.utils import timezone
        from proyectos.utils import add_business_hours
        fecha_limite = add_business_hours(timezone.now(), horas_estimadas) if horas_estimadas > 0 else None

        if not titulo:
            messages.error(request, '⚠️ El título no puede estar vacío.')
        else:
            proyecto = None
            if proyecto_id and proyecto_id != '0':
                proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
            archivo = request.FILES.get('archivo')
            t = Task.objects.create(
                archivo=archivo,
                title=titulo,
                description=descripcion,
                proyecto=proyecto,
                created_by=request.user,
                assigned_to=request.user,
                column=KanbanColumn.objects.get_or_create(name='POR_HACER', defaults={'position': 1})[0],
                prioridad=prioridad,
                horas_estimadas=horas_estimadas,
                fecha_limite=fecha_limite,
            )
            etiquetas_ids = [e for e in etiquetas_ids if e]
            if etiquetas_ids:
                t.etiquetas_relacionadas.set(etiquetas_ids)
            HistorialTarea.objects.create(
                tarea=t,
                usuario=request.user,
                estado_anterior="N/A",
                estado_nuevo="CREADA"
            )
            messages.success(request, f'✅ Tarea "{titulo}" creada y añadida a Pendientes.')

        pid = int(proyecto_id) if proyecto_id else 0
        return redirect('panel_desarrollador', proyecto_id=pid)

    return redirect('home')


@login_required
def dev_editar_tarea(request, pk):
    """Permite al desarrollador editar una tarea que él mismo creó, o al gerente editar tareas del proyecto (excepto las propias del dev)."""
    tarea = get_object_or_404(Task, pk=pk)
    proyecto_id = tarea.proyecto.id if tarea.proyecto else 0

    rol = 'GERENTE'
    if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
        rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')

    # Detectar si es una tarea propia del desarrollador
    ROLES_DEV = {'DESARROLLADOR', 'ANALISTA_ESPECIALIZADO', 'ANALISTA'}
    creador = tarea.created_by
    creador_rol = ''
    if hasattr(creador, 'perfil') and creador.perfil and creador.perfil.rol_maestro:
        creador_rol = creador.perfil.rol_maestro.name.upper().replace(' ', '_')
    es_propia_dev = (
        tarea.assigned_to_id == tarea.created_by_id
        and creador_rol in ROLES_DEV
    )

    # Bloquear al gerente/jefe si intenta editar una tarea propia del desarrollador
    if es_propia_dev and rol in ['GERENTE', 'JEFE'] and not request.user.is_superuser:
        messages.error(request, '⛔ No puedes editar una tarea creada por el propio desarrollador.')
        return redirect('panel_desarrollador', proyecto_id=proyecto_id)

    # Los desarrolladores/analistas solo pueden editar las que tienen asignadas o crearon
    if rol in ['DESARROLLADOR', 'ANALISTA_ESPECIALIZADO', 'ANALISTA']:
        if tarea.assigned_to != request.user and tarea.created_by != request.user:
            messages.error(request, '⛔ No puedes editar tareas asignadas a otros usuarios.')
            return redirect('panel_desarrollador', proyecto_id=proyecto_id)
    elif rol not in ['GERENTE', 'JEFE'] and not request.user.is_superuser:
        messages.error(request, '⛔ No tienes permiso para editar esta tarea.')
        return redirect('panel_desarrollador', proyecto_id=proyecto_id)

    if request.method == 'POST':
        titulo      = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        prioridad   = request.POST.get('prioridad', tarea.prioridad)
        etiquetas_ids = request.POST.getlist('etiquetas')
        horas_estimadas = request.POST.get('horas_estimadas', tarea.horas_estimadas)
        try: horas_estimadas = int(horas_estimadas)
        except ValueError: horas_estimadas = tarea.horas_estimadas

        if not titulo:
            messages.error(request, '⚠️ El título no puede estar vacío.')
        else:
            tarea.title       = titulo
            tarea.description = descripcion
            tarea.prioridad   = prioridad
            if horas_estimadas != tarea.horas_estimadas:
                tarea.horas_estimadas = horas_estimadas
                if horas_estimadas > 0:
                    from django.utils import timezone
                    from proyectos.utils import add_business_hours
                    tarea.fecha_limite = add_business_hours(timezone.now(), horas_estimadas)
                else:
                    tarea.fecha_limite = None
            tarea.save()
            HistorialTarea.objects.create(
                tarea=tarea,
                usuario=request.user,
                estado_anterior="N/A", estado_nuevo="ASIGNADO"
            )
            etiquetas_ids = [e for e in etiquetas_ids if e]
            if etiquetas_ids:
                tarea.etiquetas_relacionadas.set(etiquetas_ids)
            messages.success(request, f'✅ Tarea "{titulo}" actualizada correctamente.')

    return redirect('panel_desarrollador', proyecto_id=proyecto_id)


@login_required
@gerente_required
def gerente_crear_tarea(request):
    """Permite al Gerente crear tareas directamente desde el tablero Kanban con asignación a cualquier usuario."""
    if request.method == 'POST':
        titulo      = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        prioridad   = request.POST.get('prioridad', 'MEDIA')
        proyecto_id = request.POST.get('proyecto_id')
        dev_id      = request.POST.get('dev_id')
        fase_id     = request.POST.get('fase_id')
        etiquetas_ids = request.POST.getlist('etiquetas')
        horas_estimadas = request.POST.get('horas_estimadas', 0)
        try: horas_estimadas = int(horas_estimadas)
        except ValueError: horas_estimadas = 0
        from django.utils import timezone
        from proyectos.utils import add_business_hours
        fecha_limite = add_business_hours(timezone.now(), horas_estimadas) if horas_estimadas > 0 else None

        if not titulo:
            messages.error(request, '⚠️ El título no puede estar vacío.')
        else:
            proyecto = None
            if proyecto_id and proyecto_id != '0':
                proyecto = get_object_or_404(Proyecto, pk=proyecto_id)

            dev = get_object_or_404(User, pk=dev_id) if dev_id and dev_id != '' else request.user
            
            archivo = request.FILES.get('archivo')
            t = Task.objects.create(
                archivo=archivo,
                title=titulo,
                description=descripcion,
                proyecto=proyecto,
                created_by=request.user,
                assigned_to=dev,
                column=KanbanColumn.objects.get_or_create(name='POR_HACER', defaults={'position': 1})[0],
                prioridad=prioridad,
                horas_estimadas=horas_estimadas,
                fecha_limite=fecha_limite,
            )
            etiquetas_ids = [e for e in etiquetas_ids if e]
            if etiquetas_ids:
                t.etiquetas_relacionadas.set(etiquetas_ids)
            if fase_id:
                try:
                    fase_obj = Etiqueta.objects.get(id=fase_id, es_fase=True)
                    t.etiquetas_relacionadas.add(fase_obj)
                except Etiqueta.DoesNotExist:
                    pass
            HistorialTarea.objects.create(
                tarea=t,
                usuario=request.user,
                estado_anterior="N/A",
                estado_nuevo="CREADA"
            )
            messages.success(request, f'✅ Tarea "{titulo}" creada y asignada correctamente.')

        pid = int(proyecto_id) if proyecto_id and proyecto_id != '0' else 0
        return redirect('panel_desarrollador', proyecto_id=pid)

    return redirect('home')

@login_required
def cambiar_estado_tarea(request, pk, estado):
    tarea = get_object_or_404(Task, pk=pk)
    proyecto_id = tarea.proyecto.id if tarea.proyecto else 0
    if request.method == 'POST':
        from django.utils import timezone
        
        if timezone.now().weekday() >= 5:
            messages.error(request, '🚫 Acciones bloqueadas: No puedes mover tareas fuera de horario laboral (fin de semana).')
            return redirect('panel_desarrollador', proyecto_id=proyecto_id)
            
        rol = 'GERENTE'
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
            rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')
            
        if rol in ['DESARROLLADOR', 'ANALISTA_ESPECIALIZADO', 'ANALISTA'] and tarea.assigned_to != request.user:
            messages.error(request, '🚫 No puedes cambiar el estado de una tarea asignada a otro usuario.')
            return redirect('panel_desarrollador', proyecto_id=proyecto_id)
            
        # Si la fecha límite de la tarea expiró, se registra como atrasada en el historial
        if tarea.fecha_limite and timezone.now() > tarea.fecha_limite:
            HistorialTarea.objects.get_or_create(
                tarea=tarea,
                estado_nuevo='ATRASADA',
                defaults={'usuario': request.user, 'estado_anterior': 'SISTEMA'}
            )

        # Se eliminó la validación de trabajo en progreso para permitir realizar varias tareas a la vez.
            
        if estado == 'EN_REVISION':
            archivo = request.FILES.get('archivo')
            if not archivo and not tarea.archivo:
                messages.error(request, '⚠️ Debes adjuntar un documento para enviar la tarea a revisión.')
                return redirect('panel_desarrollador', proyecto_id=proyecto_id)
            
            if archivo:
                ext = str(archivo.name).lower().split('.')[-1]
                if ext in ['zip', 'rar']:
                    messages.error(request, '⚠️ No se permiten archivos .zip o .rar. Sube el documento directamente.')
                    return redirect('panel_desarrollador', proyecto_id=proyecto_id)
                tarea.archivo = archivo

        if estado in ['POR_HACER', 'EN_PROCESO', 'EN_REVISION', 'LISTO']:
            tarea.column, _ = KanbanColumn.objects.get_or_create(name=estado, defaults={'position': 4})
            tarea.save()
            HistorialTarea.objects.create(
                tarea=tarea,
                usuario=request.user,
                estado_anterior="N/A", estado_nuevo="ASIGNADO"
            )

            # Notificaciones del proyecto
            if tarea.proyecto:
                user_display = request.user.get_full_name() or request.user.username
                rol_display = 'desarrollador'
                if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
                    rol_display = request.user.perfil.rol_maestro.name.lower()

                if estado == 'EN_REVISION':
                    NotificacionProyecto.objects.create(
                        proyecto=tarea.proyecto,
                        tarea=tarea,
                        usuario=request.user,
                        tipo='EN_REVISION',
                        mensaje=f'El {rol_display} "{user_display}" acaba de terminar y enviar a revisión su tarea "{tarea.title}".'
                    )
                elif estado == 'LISTO':
                    NotificacionProyecto.objects.create(
                        proyecto=tarea.proyecto,
                        tarea=tarea,
                        usuario=request.user,
                        tipo='TAREA_FINALIZADA',
                        mensaje=f'El {rol_display} "{user_display}" acaba de terminar su tarea "{tarea.title}".'
                    )
                    # Comprobar si todas las tareas del proyecto finalizaron
                    if not tarea.proyecto.tasks.exclude(pk=tarea.pk).exclude(column__name='LISTO').exists():
                        NotificacionProyecto.objects.create(
                            proyecto=tarea.proyecto,
                            tarea=tarea,
                            usuario=request.user,
                            tipo='PROYECTO_FINALIZADO',
                            mensaje=f'El {rol_display} "{user_display}" acaba de terminar el proyecto "{tarea.proyecto.nombre}". ¡Todas las tareas están listas!'
                        )

            messages.success(request, f'Tarea actualizada correctamente.')
    return redirect('panel_desarrollador', proyecto_id=proyecto_id)

@login_required
@gerente_required
def revision_tareas(request):
    # Obtener todas las tareas que están esperando revisión de proyectos activos
    tareas_revision = Task.objects.filter(
        column__name='EN_REVISION',
        proyecto__activo=True
    ).filter(
        Q(proyecto__proyecto_padre__isnull=True) | Q(proyecto__proyecto_padre__activo=True)
    ).order_by('-id')
    return render(request, 'proyectos/revision_tareas.html', {'tareas': tareas_revision})

@login_required
@gerente_required
def aprobar_tarea(request, pk):
    tarea = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        from django.utils import timezone
        if tarea.fecha_limite and timezone.now() > tarea.fecha_limite:
            HistorialTarea.objects.get_or_create(
                tarea=tarea,
                estado_nuevo='ATRASADA',
                defaults={'usuario': request.user, 'estado_anterior': 'SISTEMA'}
            )
        tarea.column, _ = KanbanColumn.objects.get_or_create(name='LISTO', defaults={'position': 4})
        tarea.save()
        HistorialTarea.objects.create(
            tarea=tarea,
            usuario=request.user,
            estado_anterior="EN_REVISION", estado_nuevo="LISTO"
        )

        # Notificación para el proyecto
        if tarea.proyecto:
            assigned_user = tarea.assigned_to
            user_display = assigned_user.get_full_name() or assigned_user.username
            rol_display = 'desarrollador'
            if hasattr(assigned_user, 'perfil') and assigned_user.perfil and assigned_user.perfil.rol_maestro:
                rol_display = assigned_user.perfil.rol_maestro.name.lower()

            NotificacionProyecto.objects.create(
                proyecto=tarea.proyecto,
                tarea=tarea,
                usuario=assigned_user,
                tipo='TAREA_FINALIZADA',
                mensaje=f'El {rol_display} "{user_display}" acaba de terminar su tarea "{tarea.title}".'
            )

            # Verificar si todas las tareas del proyecto finalizaron
            if not tarea.proyecto.tasks.exclude(pk=tarea.pk).exclude(column__name='LISTO').exists():
                NotificacionProyecto.objects.create(
                    proyecto=tarea.proyecto,
                    tarea=tarea,
                    usuario=assigned_user,
                    tipo='PROYECTO_FINALIZADO',
                    mensaje=f'El {rol_display} "{user_display}" acaba de terminar el proyecto "{tarea.proyecto.nombre}". ¡Todas las tareas están listas!'
                )

        messages.success(request, f'✅ Tarea "{tarea.title}" aprobada y finalizada.')
    return redirect('revision_tareas')

@login_required
@gerente_required
def devolver_tarea(request, pk):
    """Devuelve una tarea de EN_REVISION a EN_PROCESO para que el desarrollador la corrija."""
    tarea = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        tarea.column, _ = KanbanColumn.objects.get_or_create(name='EN_PROCESO', defaults={'position': 2})
        tarea.save()
        HistorialTarea.objects.create(
            tarea=tarea,
            usuario=request.user,
            estado_anterior="EN_REVISION", estado_nuevo="EN_PROCESO"
        )
        
        comentario = request.POST.get('comentario', '').strip()
        if comentario:
            TaskNote.objects.create(
                task=tarea,
                user=request.user,
                content=comentario
            )
            HistorialTarea.objects.create(
                tarea=tarea,
                usuario=request.user,
                estado_anterior="N/A", estado_nuevo="COMENTARIO"
            )
            messages.success(request, f'↩️ Tarea "{tarea.title}" devuelta al desarrollador con comentario.')
        else:
            messages.success(request, f'↩️ Tarea "{tarea.title}" devuelta al desarrollador para que la corrija.')
    return redirect('revision_tareas')


@login_required
def agregar_nota(request, pk):
    if request.method == 'POST':
        tarea = get_object_or_404(Task, pk=pk)
        proyecto_id = tarea.proyecto.id if tarea.proyecto else 0

        rol = 'GERENTE'
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
            rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')

        # Restringir a desarrolladores y analistas para que solo interactúen con sus tareas asignadas
        if rol in ['DESARROLLADOR', 'ANALISTA_ESPECIALIZADO', 'ANALISTA'] and tarea.assigned_to != request.user:
            messages.error(request, '🚫 No puedes agregar comentarios en una tarea asignada a otro usuario.')
            return redirect('panel_desarrollador', proyecto_id=proyecto_id)

        comentario = request.POST.get('comentario', '').strip()
        if comentario:
            TaskNote.objects.create(
                task=tarea,
                user=request.user,
                content=comentario
            )
            HistorialTarea.objects.create(
                tarea=tarea,
                usuario=request.user,
                estado_anterior="N/A", estado_nuevo="COMENTARIO"
            )

            # Notificación al proyecto para que el gerente y equipo se enteren
            if tarea.proyecto:
                user_display = request.user.get_full_name() or request.user.username
                rol_display = 'desarrollador'
                if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
                    rol_display = request.user.perfil.rol_maestro.name.lower()
                coment_corte = (comentario[:65] + '...') if len(comentario) > 65 else comentario
                NotificacionProyecto.objects.create(
                    proyecto=tarea.proyecto,
                    tarea=tarea,
                    usuario=request.user,
                    tipo='COMENTARIO',
                    mensaje=f'El {rol_display} "{user_display}" dejó un comentario en la tarea "{tarea.title}": "{coment_corte}"'
                )

            messages.success(request, '💬 Comentario añadido a la tarea.')
        
        return redirect('panel_desarrollador', proyecto_id=proyecto_id)
    return redirect('home')

@login_required
def eliminar_nota(request, pk):
    if request.method == 'POST':
        nota = get_object_or_404(TaskNote, pk=pk)
        tarea = nota.task
        proyecto_id = tarea.proyecto.id if tarea.proyecto else 0
        
        rol = 'GERENTE'
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
            rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')

        if nota.user == request.user:
            nota.delete()
            HistorialTarea.objects.create(
                tarea=tarea,
                usuario=request.user,
                estado_anterior="N/A", estado_nuevo="NOTA_ELIMINADA"
            )
            messages.success(request, '🗑️ Nota eliminada correctamente.')
        else:
            messages.error(request, '⛔ No tienes permiso para eliminar esta nota. Solo el creador de la nota puede eliminarla.')
            
        return redirect('panel_desarrollador', proyecto_id=proyecto_id)
    return redirect('home')

from datetime import date

@login_required
def registrar_tiempo(request, pk):
    if request.method == 'POST':
        tarea = get_object_or_404(Task, pk=pk)
        pid = tarea.proyecto.id if tarea.proyecto else 0

        rol = 'GERENTE'
        if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
            rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')

        # Restricción: Los roles de Jefe y Gerente no pueden editar ni asignar fecha de inicio ni culminación
        # de una tarea asignada a usuarios tales como Desarrollador, Analista o Analista Especializado.
        # Solo el usuario responsable asignado puede asignar y editar las fechas de sus tareas.
        if tarea.assigned_to != request.user:
            nombre_asignado = tarea.assigned_to.get_full_name() or tarea.assigned_to.username
            messages.error(
                request,
                f'🚫 No tienes permiso para asignar o modificar fechas en esta tarea. '
                f'Solo {nombre_asignado} (usuario asignado) puede definir las fechas de sus tareas.'
            )
            return redirect('panel_desarrollador', proyecto_id=pid)

        fecha_inicio_str = request.POST.get('fecha_inicio', '').strip()
        fecha_limite_str = request.POST.get('fecha_limite', '').strip()
        horas_input = request.POST.get('horas', '').strip()

        from datetime import datetime, timedelta
        from django.utils import timezone

        # Procesar fecha de inicio si fue enviada
        start_date = None
        if fecha_inicio_str:
            try:
                start_date = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                if start_date.weekday() >= 5:
                    messages.error(request, '⚠️ La fecha de inicio no puede caer en fin de semana.')
                    return redirect('panel_desarrollador', proyecto_id=pid)
                tarea.fecha_inicio = start_date
            except ValueError:
                messages.error(request, '⚠️ Formato de fecha de inicio inválido.')

        if fecha_limite_str:
            try:
                target_date = datetime.strptime(fecha_limite_str, '%Y-%m-%d').date()

                # Validar que no sea fin de semana
                if target_date.weekday() >= 5:
                    messages.error(request, '⚠️ No se pueden seleccionar fines de semana para la fecha de finalización.')
                    return redirect('panel_desarrollador', proyecto_id=pid)

                # Validar que finalización no sea antes de inicio
                if start_date and target_date < start_date:
                    messages.error(request, '⚠️ La fecha de finalización no puede ser anterior a la fecha de inicio.')
                    return redirect('panel_desarrollador', proyecto_id=pid)

                # LÍMITE MÁXIMO POR TAREA DE 2 MESES PARA TERMINAR
                base_start = start_date if start_date else timezone.now().date()
                max_2_meses = base_start + timedelta(days=62)
                if target_date > max_2_meses:
                    messages.error(
                        request,
                        f'⚠️ El límite máximo para terminar una tarea es de 2 meses '
                        f'(fecha máxima permitida: {max_2_meses.strftime("%d/%m/%Y")}).'
                    )
                    return redirect('panel_desarrollador', proyecto_id=pid)

                # Validar que no supere el límite permitido por el proyecto si aplica
                if tarea.proyecto and tarea.proyecto.fecha_tentativa:
                    limite_maximo = max(tarea.proyecto.fecha_tentativa, max_2_meses)
                    if target_date > limite_maximo:
                        messages.error(
                            request,
                            f'⚠️ La fecha estimada de finalización supera el límite máximo '
                            f'({limite_maximo.strftime("%d/%m/%Y")}).'
                        )
                        return redirect('panel_desarrollador', proyecto_id=pid)

                # Calcular días laborables desde fecha_inicio (o hoy) hasta target_date
                base_start = start_date if start_date else timezone.now().date()
                cur = base_start
                business_days = 0
                while cur <= target_date:
                    if cur.weekday() < 5:
                        business_days += 1
                    cur += timedelta(days=1)

                horas = max(8, business_days * 8)
                tarea.horas_estimadas = horas
                
                # Asignar fecha_limite al final del día seleccionado
                current_tz = timezone.get_current_timezone()
                dt_naive = datetime.combine(target_date, datetime.max.time())
                tarea.fecha_limite = timezone.make_aware(dt_naive, current_tz)

                messages.success(
                    request,
                    f'✅ Fechas estimadas registradas para "{tarea.title}": '
                    f'Inicio {start_date.strftime("%d/%m/%Y") if start_date else "hoy"} | Finalización {target_date.strftime("%d/%m/%Y")}.'
                )
            except ValueError:
                messages.error(request, '⚠️ Formato de fecha de finalización inválido.')
        elif start_date:
            messages.success(request, f'✅ Fecha de inicio registrada para "{tarea.title}": {start_date.strftime("%d/%m/%Y")}.')

        tarea.save()
        return redirect('panel_desarrollador', proyecto_id=pid)
    return redirect('home')

@login_required
@gerente_required
def generar_reporte(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    tareas = Task.objects.filter(proyecto=proyecto)
    
    total_tareas = tareas.count()
    completadas = tareas.filter(column__name='LISTO').count()
    
    # Calcular horas totales
    from django.db.models import Sum
    tiempos = TiempoTarea.objects.filter(tarea__proyecto=proyecto).aggregate(Sum('horas_invertidas'))
    total_horas = tiempos['horas_invertidas__sum'] or 0
    
    contenido = f"<h3>Reporte de {proyecto.nombre}</h3>"
    contenido += f"<p>Total tareas: {total_tareas}</p>"
    contenido += f"<p>Completadas: {completadas}</p>"
    contenido += f"<p>Horas totales invertidas: {total_horas}</p>"
    
    contenido += "<br><h4 style='font-size: 1.3em; margin-bottom: 10px;'>Detalle de Tareas:</h4>"
    for tarea in tareas:
        desc = tarea.description if tarea.description else "Sin descripción"
        estado_texto = "✅ Completada" if tarea.column and tarea.column.name == 'LISTO' else "⏳ Pendiente"
        
        contenido += f"<div style='margin-bottom: 15px;'>"
        contenido += f"<div style='font-size: 1.15em; font-weight: bold;'>{tarea.title} <span style='font-weight: normal; font-size: 0.85em; color: #555;'>({estado_texto})</span></div>"
        contenido += f"<div style='font-size: 1em; margin-top: 4px;'>{desc}</div>"
        contenido += "</div>"
    
    Reporte.objects.update_or_create(
        proyecto=proyecto,
        tipo_reporte="Resumen",
        defaults={
            'titulo': f"Reporte Final - {proyecto.nombre}",
            'contenido': contenido,
            'autor': request.user,
        }
    )
    messages.success(request, '📊 Reporte generado exitosamente. (Imprime esta página para guardarlo en PDF)')
    
    # Renderizamos una vista rápida con el HTML directamente para simular el reporte
    from django.http import HttpResponse
    html_report = f"""
    <html><head><title>Reporte - {proyecto.nombre}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    </head>
    <body style="font-family: Arial; padding: 40px; max-width: 800px; margin: auto;">
        <div class="no-print" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <a href="/" style="color:#666; text-decoration:none; font-weight: bold;">⬅ Volver al Panel</a>
            <div style="display:flex; gap: 10px;">
                <button onclick="window.print()" style="padding:10px 20px; background:#475569; color:white; border:none; border-radius:8px; cursor:pointer; font-weight: bold;">🖨️ Imprimir</button>
                <button onclick="guardarPDF()" style="padding:10px 20px; background:#ff6600; color:white; border:none; border-radius:8px; cursor:pointer; font-weight: bold;">💾 Guardar PDF</button>
            </div>
        </div>
        <hr>
        <div id="report-content">
            {contenido}
            <br><br>
            <p>Generado por: {request.user.first_name} {request.user.last_name}</p>
            <p>Fecha: {date.today()}</p>
        </div>
        <script>
            function guardarPDF() {{
                var element = document.getElementById('report-content');
                var opt = {{
                    margin:       0.5,
                    filename:     'Reporte_{proyecto.nombre}.pdf',
                    image:        {{ type: 'jpeg', quality: 0.98 }},
                    html2canvas:  {{ scale: 2 }},
                    jsPDF:        {{ unit: 'in', format: 'letter', orientation: 'portrait' }}
                }};
                html2pdf().set(opt).from(element).save();
            }}
        </script>
        <style>@media print {{ .no-print {{ display: none !important; }} }}</style>
    </body></html>
    """
    return HttpResponse(html_report)

@login_required
@gerente_required
def lista_reportes(request):
    reportes = Reporte.objects.all().order_by('-fecha_creacion')
    return render(request, 'proyectos/lista_reportes.html', {'reportes': reportes})

@login_required
@gerente_required
def ver_reporte(request, pk):
    reporte = get_object_or_404(Reporte, pk=pk)
    from django.http import HttpResponse
    html_report = f"""
    <html><head><title>{reporte.titulo}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    </head>
    <body style="font-family: Arial; padding: 40px; max-width: 800px; margin: auto;">
        <div class="no-print" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <a href="/reportes/" style="color:#666; text-decoration:none; font-weight: bold;">⬅ Volver a la Lista</a>
            <div style="display:flex; gap: 10px;">
                <button onclick="window.print()" style="padding:10px 20px; background:#475569; color:white; border:none; border-radius:8px; cursor:pointer; font-weight: bold;">🖨️ Imprimir</button>
                <button onclick="guardarPDF()" style="padding:10px 20px; background:#ff6600; color:white; border:none; border-radius:8px; cursor:pointer; font-weight: bold;">💾 Guardar PDF</button>
            </div>
        </div>
        <hr>
        <div id="report-content">
            {reporte.contenido}
            <br><br>
            <p>Generado por: {reporte.autor.first_name if reporte.autor else ''} {reporte.autor.last_name if reporte.autor else ''}</p>
            <p>Fecha Original de Generación: {reporte.fecha_creacion.strftime('%d/%m/%Y')}</p>
        </div>
        <script>
            function guardarPDF() {{
                var element = document.getElementById('report-content');
                var opt = {{
                    margin:       0.5,
                    filename:     '{reporte.titulo}.pdf',
                    image:        {{ type: 'jpeg', quality: 0.98 }},
                    html2canvas:  {{ scale: 2 }},
                    jsPDF:        {{ unit: 'in', format: 'letter', orientation: 'portrait' }}
                }};
                html2pdf().set(opt).from(element).save();
            }}
        </script>
        <style>@media print {{ .no-print {{ display: none !important; }} }}</style>
    </body></html>
    """
    return HttpResponse(html_report)


# --- VISTAS PARA ACEPTACIÓN DE PROYECTOS Y ACTA DE RECEPCIÓN DE REQUERIMIENTOS ---

@login_required
def ver_acta_aceptacion(request, proyecto_id):
    """
    Vista del documento imprimible del Acta de Recepción de Requerimiento (2 páginas).
    """
    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    acta, _ = ActaRecepcion.objects.get_or_create(proyecto=proyecto)
    
    rol = 'GERENTE'
    if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
        rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')
    
    if rol == 'DESARROLLADOR' and not request.user.is_superuser:
        proyectos_ids = Task.objects.filter(assigned_to=request.user, proyecto__isnull=False).values_list('proyecto_id', flat=True).distinct()
        proyectos_donde_hay_tareas = Proyecto.objects.filter(id__in=proyectos_ids)
        padres_ids = set()
        for p in proyectos_donde_hay_tareas:
            if p.proyecto_padre_id:
                padres_ids.add(p.proyecto_padre_id)
            else:
                padres_ids.add(p.id)
        if proyecto.id not in padres_ids:
            messages.error(request, 'No tienes permiso para ver el acta de un proyecto que no tienes asignado.')
            return redirect('lista_aceptacion_proyectos')

    es_jefe = (rol == 'JEFE' or request.user.is_superuser)

    return render(request, 'proyectos/acta_aceptacion.html', {
        'proyecto': proyecto,
        'acta': acta,
        'es_jefe': es_jefe,
        'rol': rol,
    })


@login_required
def descargar_acta_excel(request, proyecto_id):
    """
    Genera y descarga el Acta de Recepción de Requerimiento en formato Excel (.xlsx).
    """
    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    acta, _ = ActaRecepcion.objects.get_or_create(proyecto=proyecto)

    rol = 'GERENTE'
    if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
        rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')

    if rol == 'DESARROLLADOR' and not request.user.is_superuser:
        proyectos_ids = Task.objects.filter(assigned_to=request.user, proyecto__isnull=False).values_list('proyecto_id', flat=True).distinct()
        proyectos_donde_hay_tareas = Proyecto.objects.filter(id__in=proyectos_ids)
        padres_ids = set()
        for p in proyectos_donde_hay_tareas:
            if p.proyecto_padre_id:
                padres_ids.add(p.proyecto_padre_id)
            else:
                padres_ids.add(p.id)
        if proyecto.id not in padres_ids:
            messages.error(request, 'No tienes permiso para descargar el acta de un proyecto que no tienes asignado.')
            return redirect('lista_aceptacion_proyectos')

    from proyectos.excel_acta import generar_excel_acta
    from django.http import HttpResponse

    excel_file = generar_excel_acta(proyecto, acta)
    nombre_limpio = "".join(c for c in proyecto.nombre if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    filename = f"Acta_Recepcion_{nombre_limpio or proyecto.id}.xlsx"

    response = HttpResponse(
        excel_file.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
@crear_actas_required
def editar_acta_aceptacion(request, proyecto_id):
    """
    Permite editar los campos del Acta de Recepción del Proyecto (siglas, gerencia, entregables, observaciones, detalles, etc.)
    """
    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    acta, _ = ActaRecepcion.objects.get_or_create(proyecto=proyecto)

    rol = 'GERENTE'
    if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
        rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')

    if rol == 'DESARROLLADOR' and not request.user.is_superuser:
        proyectos_ids = Task.objects.filter(assigned_to=request.user, proyecto__isnull=False).values_list('proyecto_id', flat=True).distinct()
        proyectos_donde_hay_tareas = Proyecto.objects.filter(id__in=proyectos_ids)
        padres_ids = set()
        for p in proyectos_donde_hay_tareas:
            if p.proyecto_padre_id:
                padres_ids.add(p.proyecto_padre_id)
            else:
                padres_ids.add(p.id)
        if proyecto.id not in padres_ids:
            messages.error(request, 'No tienes permiso para editar el acta de un proyecto que no tienes asignado.')
            return redirect('lista_aceptacion_proyectos')

    if request.method == 'POST':
        form = ActaRecepcionForm(request.POST, instance=acta)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Requerimientos y detalles del proyecto "{proyecto.nombre}" actualizados correctamente.')
            return redirect('ver_acta_aceptacion', proyecto_id=proyecto.id)
    else:
        form = ActaRecepcionForm(instance=acta)

    return render(request, 'proyectos/editar_acta.html', {
        'proyecto': proyecto,
        'acta': acta,
        'form': form,
        'rol': rol,
    })


@login_required
@jefe_required
def aprobar_proyecto_acta(request, proyecto_id):
    """
    Acción ejecutada por el Jefe para aprobar oficialmente el proyecto y su Acta de Recepción.
    """
    from django.utils import timezone
    proyecto = get_object_or_404(Proyecto, pk=proyecto_id)
    acta, _ = ActaRecepcion.objects.get_or_create(proyecto=proyecto)

    if request.method == 'POST':
        acta.estado = 'APROBADO'
        acta.aprobado_por = request.user
        acta.fecha_aprobacion = timezone.now()
        acta.save()
        messages.success(request, f'🎉 El proyecto "{proyecto.nombre}" ha sido APROBADO oficialmente por el Jefe de Proyectos.')

    return redirect('ver_acta_aceptacion', proyecto_id=proyecto.id)


@login_required
def lista_aceptacion_proyectos(request):
    """
    Listado general de todas las actas de Crear Actas.
    """
    rol = 'GERENTE'
    if hasattr(request.user, 'perfil') and request.user.perfil and request.user.perfil.rol_maestro:
        rol = request.user.perfil.rol_maestro.name.upper().replace(' ', '_')
    es_jefe = (rol == 'JEFE' or request.user.is_superuser)

    if rol == 'DESARROLLADOR':
        proyectos_ids = Task.objects.filter(assigned_to=request.user, proyecto__isnull=False).values_list('proyecto_id', flat=True).distinct()
        proyectos_donde_hay_tareas = Proyecto.objects.filter(id__in=proyectos_ids)
        padres_ids = set()
        for p in proyectos_donde_hay_tareas:
            if p.proyecto_padre_id:
                padres_ids.add(p.proyecto_padre_id)
            else:
                padres_ids.add(p.id)
        proyectos_qs = Proyecto.objects.filter(id__in=padres_ids, activo=True).order_by('-fecha_creacion')
    else:
        proyectos_qs = Proyecto.objects.filter(activo=True, proyecto_padre__isnull=True).order_by('-fecha_creacion')

    actas = []
    for p in proyectos_qs:
        acta, _ = ActaRecepcion.objects.get_or_create(proyecto=p)
        actas.append({
            'proyecto': p,
            'acta': acta,
        })

    return render(request, 'proyectos/lista_aceptacion.html', {
        'actas': actas,
        'proyectos': proyectos_qs,
        'es_jefe': es_jefe,
        'rol': rol,
    })