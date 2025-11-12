"""
Utilidades para calcular metabolismo basal (TMB/BMR) y necesidades calóricas
"""

from typing import Optional
from services.peso_service import PesoService


def calcular_tmb_mifflin_st_jeor(
    peso: float,
    altura_cm: float,
    edad: int,
    sexo: str
) -> float:
    """
    Calcular TMB usando la fórmula de Mifflin-St Jeor (más precisa)
    
    Args:
        peso: Peso en kg
        altura_cm: Altura en centímetros
        edad: Edad en años
        sexo: "hombre" o "mujer"
    
    Returns:
        TMB en calorías por día
    """
    altura_m = altura_cm / 100.0
    
    if sexo.lower() in ["hombre", "masculino", "m"]:
        tmb = (10 * peso) + (6.25 * altura_cm) - (5 * edad) + 5
    else:  # mujer
        tmb = (10 * peso) + (6.25 * altura_cm) - (5 * edad) - 161
    
    return max(tmb, 0)  # Asegurar que no sea negativo


def calcular_tmb_harris_benedict(
    peso: float,
    altura_cm: float,
    edad: int,
    sexo: str
) -> float:
    """
    Calcular TMB usando la fórmula de Harris-Benedict (clásica)
    
    Args:
        peso: Peso en kg
        altura_cm: Altura en centímetros
        edad: Edad en años
        sexo: "hombre" o "mujer"
    
    Returns:
        TMB en calorías por día
    """
    if sexo.lower() in ["hombre", "masculino", "m"]:
        tmb = 88.362 + (13.397 * peso) + (4.799 * altura_cm) - (5.677 * edad)
    else:  # mujer
        tmb = 447.593 + (9.247 * peso) + (3.098 * altura_cm) - (4.330 * edad)
    
    return max(tmb, 0)


def calcular_tmb_katch_mcardle(
    peso: float,
    porcentaje_grasa: float
) -> Optional[float]:
    """
    Calcular TMB usando la fórmula de Katch-McArdle (requiere % grasa corporal)
    
    Args:
        peso: Peso en kg
        porcentaje_grasa: Porcentaje de grasa corporal (0-100)
    
    Returns:
        TMB en calorías por día, o None si no hay datos suficientes
    """
    if porcentaje_grasa <= 0 or porcentaje_grasa >= 100:
        return None
    
    masa_magra = peso * (1 - porcentaje_grasa / 100)
    tmb = 370 + (21.6 * masa_magra)
    
    return max(tmb, 0)


def calcular_tdee(tmb: float, nivel_actividad: str) -> float:
    """
    Calcular TDEE (Total Daily Energy Expenditure) basado en nivel de actividad
    
    Args:
        tmb: Tasa metabólica basal en calorías
        nivel_actividad: Nivel de actividad física
            - "sedentario": 1.2
            - "ligera": 1.375
            - "moderada": 1.55
            - "intensa": 1.725
            - "muy_intensa": 1.9
    
    Returns:
        TDEE en calorías por día
    """
    factores = {
        "sedentario": 1.2,
        "ligera": 1.375,
        "moderada": 1.55,
        "intensa": 1.725,
        "muy_intensa": 1.9
    }
    
    factor = factores.get(nivel_actividad.lower(), 1.2)
    return tmb * factor


def obtener_tmb_usuario() -> Optional[float]:
    """
    Obtener TMB del usuario usando los datos disponibles
    
    Returns:
        TMB en calorías por día, o None si no hay datos suficientes
    """
    registro_peso = PesoService.obtener_mas_reciente()
    
    if not registro_peso or not registro_peso.peso:
        return None
    
    # Intentar obtener altura del registro más reciente
    altura_cm = None
    if registro_peso.altura and registro_peso.altura > 0:
        altura_cm = registro_peso.altura * 100  # Convertir metros a cm
    
    # Si no hay altura, no podemos calcular TMB
    if not altura_cm:
        return None
    
    # Por ahora, usar valores por defecto para edad y sexo
    # TODO: Agregar estos campos al perfil del usuario
    edad = 30  # Valor por defecto
    sexo = "hombre"  # Valor por defecto
    
    # Intentar usar Katch-McArdle si hay % grasa
    if registro_peso.grasa_corporal and registro_peso.grasa_corporal > 0:
        tmb = calcular_tmb_katch_mcardle(registro_peso.peso, registro_peso.grasa_corporal)
        if tmb:
            return tmb
    
    # Usar Mifflin-St Jeor como alternativa
    return calcular_tmb_mifflin_st_jeor(registro_peso.peso, altura_cm, edad, sexo)

