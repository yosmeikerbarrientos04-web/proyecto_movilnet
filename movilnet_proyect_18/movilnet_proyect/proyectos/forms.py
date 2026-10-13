from django import forms
from .models import Proyecto, Task, ActaRecepcion

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['identificador', 'nombre', 'descripcion', 'tipo', 'fecha_tentativa', 'fecha_deadline']
        widgets = {
            'fecha_tentativa': forms.DateInput(
                attrs={'type': 'text', 'id': 'id_fecha_tentativa', 'placeholder': 'Seleccionar fecha (Laborable)', 'autocomplete': 'off'},
                format='%Y-%m-%d'
            ),
            'fecha_deadline': forms.DateInput(
                attrs={'type': 'text', 'placeholder': 'YYYY-MM-DD', 'autocomplete': 'off'},
                format='%Y-%m-%d'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['identificador'].required = True
        self.fields['fecha_tentativa'].required = True
        self.fields['descripcion'].required = True
        # Asegura que la fecha se muestre pre-cargada en el input date
        if self.instance and self.instance.fecha_tentativa:
            self.initial['fecha_tentativa'] = self.instance.fecha_tentativa.strftime('%Y-%m-%d')
        if self.instance and self.instance.fecha_deadline:
            self.initial['fecha_deadline'] = self.instance.fecha_deadline.strftime('%Y-%m-%d')

    def clean_identificador(self):
        identificador = self.cleaned_data.get('identificador')
        if identificador:
            identificador = identificador.strip()
            qs = Proyecto.objects.filter(identificador__iexact=identificador)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    f'Ya existe un proyecto con el ID "{identificador}". Por favor ingresa un ID único.'
                )
        return identificador

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'column']

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        # Quitar la opción de estado finalizado ('LISTO') para el desarrollador
        self.fields['column'].choices = [c for c in self.fields['column'].choices if c[0] != 'LISTO']

class ManagerTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to']

class ActaRecepcionForm(forms.ModelForm):
    class Meta:
        model = ActaRecepcion
        fields = [
            'siglas_solucion',
            'gerencia_receptora',
            'nombre_cliente_funcional',
            'unidad_funcional',
            'descripcion',
            'entregables',
            'observaciones',
            'detalles',
            'firmante_1_nombre', 'firmante_1_unidad',
            'firmante_2_nombre', 'firmante_2_unidad',
            'firmante_3_nombre', 'firmante_3_unidad',
            'firmante_4_nombre', 'firmante_4_unidad',
            'firmante_5_nombre', 'firmante_5_unidad',
            'firmante_6_nombre', 'firmante_6_unidad',
            'firmante_7_nombre', 'firmante_7_unidad',
            'firmante_8_nombre', 'firmante_8_unidad',
        ]
        widgets = {
            'siglas_solucion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: CSV, SIS'}),
            'gerencia_receptora': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Desarrollo de Aplicaciones para Gestión Empresarial'}),
            'nombre_cliente_funcional': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Juan Gamboa'}),
            'unidad_funcional': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Gerencia General Liberación e Implementación de Soluciones TI'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Detalle la descripción del requerimiento...'}),
            'entregables': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Ej:\n- Versión β del código fuente.\n- Documento de Análisis y Diseño.'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Observaciones adicionales...'}),
            'detalles': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Detalles adicionales...'}),
            'firmante_1_nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Gheisell Chong'}),
            'firmante_1_unidad': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Gerencia General de Desarrollo de Soluciones TI'}),
            'firmante_2_nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Marcos Sánchez'}),
            'firmante_2_unidad': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Gerencia de Arquitectura de Software TI'}),
            'firmante_3_nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Yoleidy Padilla'}),
            'firmante_3_unidad': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Gerencia de Desarrollo de Aplicaciones para Gestión Empresarial'}),
            'firmante_4_nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Osman Espinoza'}),
            'firmante_4_unidad': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Coordinación de Interfaces de Software para Gestión Empresarial'}),
            'firmante_5_nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Juan Gamboa'}),
            'firmante_5_unidad': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Gerencia General Liberación e Implementación de Soluciones TI'}),
            'firmante_6_nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Carlos Rodriguez'}),
            'firmante_6_unidad': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Coordinación de Ambiente y Versiones'}),
            'firmante_7_nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: José Luis Nieves'}),
            'firmante_7_unidad': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Gerencia General de Planificación y Proyectos TI'}),
            'firmante_8_nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Zaida Rivas'}),
            'firmante_8_unidad': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Gerencia Planificación de Soluciones TI'}),
        }

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User

class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("No existe ningún usuario registrado con este correo electrónico.")
        return email