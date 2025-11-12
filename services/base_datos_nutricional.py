"""
Base de datos nutricional local con valores comunes de alimentos
Usado cuando no hay APIs externas configuradas
"""

from typing import Dict, Any, Optional
import re

# Base de datos de alimentos comunes con valores nutricionales por 100g (o unidad estándar)
BASE_DATOS_ALIMENTOS = {
    # Tortillas y panes
    "tortilla": {"calorias": 218, "proteinas": 5.7, "carbohidratos": 45.7, "grasas": 2.5, "por_unidad": True, "peso_unidad": 30},
    "tortilla de harina": {"calorias": 218, "proteinas": 5.7, "carbohidratos": 45.7, "grasas": 2.5, "por_unidad": True, "peso_unidad": 30},
    "tortilla de maíz": {"calorias": 218, "proteinas": 5.7, "carbohidratos": 45.7, "grasas": 2.5, "por_unidad": True, "peso_unidad": 30},
    "sincronizada": {"calorias": 300, "proteinas": 15, "carbohidratos": 25, "grasas": 15, "por_unidad": True, "peso_unidad": 100},
    "sincronizada de una tortilla de harina": {"calorias": 300, "proteinas": 15, "carbohidratos": 25, "grasas": 15, "por_unidad": True, "peso_unidad": 100},
    
    # Huevos
    "huevo": {"calorias": 155, "proteinas": 13, "carbohidratos": 1.1, "grasas": 11, "por_unidad": True, "peso_unidad": 50},
    "huevos": {"calorias": 155, "proteinas": 13, "carbohidratos": 1.1, "grasas": 11, "por_unidad": True, "peso_unidad": 50},
    "huevo revuelto": {"calorias": 155, "proteinas": 13, "carbohidratos": 1.1, "grasas": 11, "por_unidad": True, "peso_unidad": 50},
    "huevos revueltos": {"calorias": 155, "proteinas": 13, "carbohidratos": 1.1, "grasas": 11, "por_unidad": True, "peso_unidad": 50},
    
    # Verduras
    "espinacas": {"calorias": 23, "proteinas": 2.9, "carbohidratos": 3.6, "grasas": 0.4},
    "espinaca": {"calorias": 23, "proteinas": 2.9, "carbohidratos": 3.6, "grasas": 0.4},
    "piña": {"calorias": 50, "proteinas": 0.5, "carbohidratos": 13, "grasas": 0.1},
    "piña fresca": {"calorias": 50, "proteinas": 0.5, "carbohidratos": 13, "grasas": 0.1},
    
    # Lácteos
    "crema": {"calorias": 345, "proteinas": 2.1, "carbohidratos": 2.8, "grasas": 37},
    "crema ácida": {"calorias": 345, "proteinas": 2.1, "carbohidratos": 2.8, "grasas": 37},
    "queso": {"calorias": 300, "proteinas": 25, "carbohidratos": 1, "grasas": 22},
    
    # Bebidas
    "café": {"calorias": 2, "proteinas": 0.1, "carbohidratos": 0, "grasas": 0, "por_unidad": True, "peso_unidad": 240},
    "café sin azúcar": {"calorias": 2, "proteinas": 0.1, "carbohidratos": 0, "grasas": 0, "por_unidad": True, "peso_unidad": 240},
    "café sin azúcar ni leche": {"calorias": 2, "proteinas": 0.1, "carbohidratos": 0, "grasas": 0, "por_unidad": True, "peso_unidad": 240},
    
    # Salsas
    "salsa verde": {"calorias": 20, "proteinas": 0.5, "carbohidratos": 4, "grasas": 0.5},
    "salsa": {"calorias": 20, "proteinas": 0.5, "carbohidratos": 4, "grasas": 0.5},
}

def buscar_alimento(nombre: str) -> Optional[Dict[str, Any]]:
    """
    Buscar alimento en la base de datos local
    
    Args:
        nombre: Nombre del alimento a buscar
    
    Returns:
        Diccionario con información nutricional o None si no se encuentra
    """
    nombre_lower = nombre.lower().strip()
    
    # Buscar coincidencia exacta
    if nombre_lower in BASE_DATOS_ALIMENTOS:
        return BASE_DATOS_ALIMENTOS[nombre_lower].copy()
    
    # Buscar coincidencia parcial (contiene)
    for alimento_key, alimento_data in BASE_DATOS_ALIMENTOS.items():
        if alimento_key in nombre_lower or nombre_lower in alimento_key:
            return alimento_data.copy()
    
    # Buscar por palabras clave
    palabras = nombre_lower.split()
    for palabra in palabras:
        if palabra in BASE_DATOS_ALIMENTOS:
            return BASE_DATOS_ALIMENTOS[palabra].copy()
    
    return None

def calcular_valores_nutricionales(nombre: str, cantidad: float, unidad: str) -> Dict[str, float]:
    """
    Calcular valores nutricionales para una cantidad específica
    
    Args:
        nombre: Nombre del alimento
        cantidad: Cantidad
        unidad: Unidad de medida
    
    Returns:
        Diccionario con valores nutricionales calculados
    """
    alimento = buscar_alimento(nombre)
    
    if not alimento:
        return {"calorias": 0, "proteinas": 0, "carbohidratos": 0, "grasas": 0}
    
    # Si el alimento se mide por unidad
    if alimento.get("por_unidad", False):
        peso_unidad = alimento.get("peso_unidad", 100)
        if unidad == "unidad":
            factor = cantidad
        else:
            # Convertir cantidad a unidades
            factor = cantidad / peso_unidad
    else:
        # Si se mide por peso, calcular factor basado en cantidad
        if unidad == "g":
            factor = cantidad / 100.0
        elif unidad == "ml":
            factor = cantidad / 100.0  # Asumir densidad similar al agua
        else:
            factor = cantidad / 100.0
    
    return {
        "calorias": round(alimento["calorias"] * factor, 1),
        "proteinas": round(alimento["proteinas"] * factor, 1),
        "carbohidratos": round(alimento["carbohidratos"] * factor, 1),
        "grasas": round(alimento["grasas"] * factor, 1)
    }

