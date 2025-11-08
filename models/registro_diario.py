"""
Modelo para registro diario de consumo de alimentos
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date


class RegistroDiario:
    """Modelo de registro diario de consumo"""
    
    def __init__(
        self,
        fecha: date,
        comidas: List[Dict[str, Any]],
        registro_id: Optional[str] = None
    ):
        self.id = registro_id
        self.fecha = fecha if isinstance(fecha, date) else datetime.strptime(fecha, "%Y-%m-%d").date()
        self.comidas = comidas  # Lista de dicts con {comida_id, cantidad, momento}
    
    @property
    def total_calorias(self) -> float:
        """Calcular total de calorías del día"""
        return sum(comida.get("calorias", 0) for comida in self.comidas)
    
    @property
    def total_proteinas(self) -> float:
        """Calcular total de proteínas del día"""
        return sum(comida.get("proteinas", 0) for comida in self.comidas)
    
    @property
    def total_carbohidratos(self) -> float:
        """Calcular total de carbohidratos del día"""
        return sum(comida.get("carbohidratos", 0) for comida in self.comidas)
    
    @property
    def total_grasas(self) -> float:
        """Calcular total de grasas del día"""
        return sum(comida.get("grasas", 0) for comida in self.comidas)
    
    def get_comidas_por_momento(self, momento: str) -> List[Dict[str, Any]]:
        """Obtener comidas de un momento específico (Desayuno, Almuerzo, Cena, Snacks)"""
        return [c for c in self.comidas if c.get("momento") == momento]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para Firebase"""
        return {
            "fecha": self.fecha.isoformat(),
            "comidas": self.comidas
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], registro_id: Optional[str] = None) -> "RegistroDiario":
        """Crear instancia desde diccionario"""
        return cls(
            registro_id=registro_id or data.get("id"),
            fecha=data.get("fecha"),
            comidas=data.get("comidas", [])
        )

