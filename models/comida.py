"""
Modelo para representar una comida o alimento
"""

from typing import Optional, Dict, Any
from datetime import datetime, date


class Comida:
    """Modelo de comida con información nutricional"""
    
    def __init__(
        self,
        nombre: str,
        calorias: float,
        proteinas: float = 0.0,
        carbohidratos: float = 0.0,
        grasas: float = 0.0,
        cantidad: float = 100.0,
        unidad: str = "g",
        descripcion: str = "",
        comida_id: Optional[str] = None
    ):
        self.id = comida_id
        self.nombre = nombre
        self.calorias = calorias
        self.proteinas = proteinas
        self.carbohidratos = carbohidratos
        self.grasas = grasas
        self.cantidad = cantidad
        self.unidad = unidad
        self.descripcion = descripcion
    
    def calcular_macros_por_cantidad(self, cantidad_deseada: float) -> Dict[str, float]:
        """Calcular macros para una cantidad específica"""
        factor = cantidad_deseada / self.cantidad if self.cantidad > 0 else 1.0
        return {
            "calorias": self.calorias * factor,
            "proteinas": self.proteinas * factor,
            "carbohidratos": self.carbohidratos * factor,
            "grasas": self.grasas * factor
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para Firebase"""
        return {
            "nombre": self.nombre,
            "calorias": self.calorias,
            "proteinas": self.proteinas,
            "carbohidratos": self.carbohidratos,
            "grasas": self.grasas,
            "cantidad": self.cantidad,
            "unidad": self.unidad,
            "descripcion": self.descripcion
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], comida_id: Optional[str] = None) -> "Comida":
        """Crear instancia desde diccionario"""
        return cls(
            comida_id=comida_id or data.get("id"),
            nombre=data.get("nombre", ""),
            calorias=data.get("calorias", 0.0),
            proteinas=data.get("proteinas", 0.0),
            carbohidratos=data.get("carbohidratos", 0.0),
            grasas=data.get("grasas", 0.0),
            cantidad=data.get("cantidad", 100.0),
            unidad=data.get("unidad", "g"),
            descripcion=data.get("descripcion", "")
        )

