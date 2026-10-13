from datetime import timedelta

def add_business_hours(start_date, hours_to_add):
    """
    Agrega horas a una fecha inicial saltando los fines de semana (sábado y domingo).
    Asume que 1 día de estimación = 24 horas.
    """
    if hours_to_add <= 0:
        return start_date

    days_to_add = hours_to_add // 24
    hours_left = hours_to_add % 24
    current_date = start_date
    
    while days_to_add > 0:
        current_date += timedelta(days=1)
        if current_date.weekday() < 5:  # 0=Lunes, 4=Viernes
            days_to_add -= 1
            
    while hours_left > 0:
        current_date += timedelta(hours=1)
        if current_date.weekday() < 5:
            hours_left -= 1
            
    return current_date
