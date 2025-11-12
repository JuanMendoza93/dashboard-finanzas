"""
Funciones auxiliares para trabajar con semanas (Lunes a Domingo)
"""

from datetime import date, timedelta


def get_week_start_end(fecha: date) -> tuple[date, date]:
    """
    Obtener el inicio (Lunes) y fin (Domingo) de la semana para una fecha dada
    
    Args:
        fecha: Fecha dentro de la semana
        
    Returns:
        Tupla (inicio_semana, fin_semana) donde inicio es Lunes y fin es Domingo
    """
    # Obtener el día de la semana (0=Lunes, 6=Domingo)
    dia_semana = fecha.weekday()
    
    # Calcular días hasta el lunes (inicio de semana)
    dias_hasta_lunes = dia_semana
    
    # Calcular inicio de semana (Lunes)
    inicio_semana = fecha - timedelta(days=dias_hasta_lunes)
    
    # Calcular fin de semana (Domingo = Lunes + 6 días)
    fin_semana = inicio_semana + timedelta(days=6)
    
    return inicio_semana, fin_semana


def get_current_week() -> tuple[date, date]:
    """
    Obtener el inicio y fin de la semana actual
    
    Returns:
        Tupla (inicio_semana, fin_semana) de la semana actual
    """
    hoy = date.today()
    return get_week_start_end(hoy)


def get_week_number(fecha: date) -> int:
    """
    Obtener el número de semana del año para una fecha
    
    Args:
        fecha: Fecha
        
    Returns:
        Número de semana (1-53)
    """
    return fecha.isocalendar()[1]

