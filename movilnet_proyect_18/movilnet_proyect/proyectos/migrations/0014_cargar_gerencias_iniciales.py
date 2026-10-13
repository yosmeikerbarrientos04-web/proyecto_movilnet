from django.db import migrations

def poblar_gerencias(apps, schema_editor):
    Gerencia = apps.get_model('proyectos', 'Gerencia')
    gerencias = [
        'Desarrollo de Soluciones TI',
        'Desarrollo de Aplicaciones para Gestión al Cliente',
        'Desarrollo de Aplicaciones para Saldos y Consumos',
        'Desarrollo de Aplicaciones para Gestión Empresarial',
        'Arquitectura de Software TI',
    ]
    for nombre in gerencias:
        Gerencia.objects.get_or_create(nombre=nombre)

def revertir_gerencias(apps, schema_editor):
    Gerencia = apps.get_model('proyectos', 'Gerencia')
    gerencias = [
        'Desarrollo de Soluciones TI',
        'Desarrollo de Aplicaciones para Gestión al Cliente',
        'Desarrollo de Aplicaciones para Saldos y Consumos',
        'Desarrollo de Aplicaciones para Gestión Empresarial',
        'Arquitectura de Software TI',
    ]
    Gerencia.objects.filter(nombre__in=gerencias).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('proyectos', '0013_gerencia_alter_proyecto_identificador_and_more'),
    ]

    operations = [
        migrations.RunPython(poblar_gerencias, revertir_gerencias),
    ]
