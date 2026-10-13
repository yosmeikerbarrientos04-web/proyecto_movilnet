from django import template

register = template.Library()

@register.filter
def notif_count(proyecto, user):
    if proyecto and hasattr(proyecto, 'notificaciones_no_leidas_count_for_user'):
        return proyecto.notificaciones_no_leidas_count_for_user(user)
    return 0

@register.filter
def notif_list(proyecto, user):
    if proyecto and hasattr(proyecto, 'ultimas_notificaciones_for_user'):
        return proyecto.ultimas_notificaciones_for_user(user)
    return []
