"""
Modelo para metas calóricas y nutricionales
"""

from typing import Optional, Dict, Any
from datetime import datetime, date


class MetaCalorica:
    """Modelo de meta calórica diaria"""
    
    def __init__(
        self,
        calorias_diarias: float,
        deficit_calorico: float = 0.0,
        proteinas_objetivo: float = 0.0,
        carbohidratos_objetivo: float = 0.0,
        grasas_objetivo: float = 0.0,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        meta_id: Optional[str] = None
    ):
        self.id = meta_id
        self.calorias_diarias = calorias_diarias
        self.deficit_calorico = deficit_calorico
        self.proteinas_objetivo = proteinas_objetivo
        self.carbohidratos_objetivo = carbohidratos_objetivo
        self.grasas_objetivo = grasas_objetivo
        self.fecha_inicio = fecha_inicio or date.today()
        self.fecha_fin = fecha_fin
    
    @property
    def calorias_objetivo(self) -> float:
        """Calorías objetivo considerando déficit"""
        return self.calorias_diarias - self.deficit_calorico
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para Firebase"""
        return {
            "calorias_diarias": self.calorias_diarias,
            "deficit_calorico": self.deficit_calorico,
            "proteinas_objetivo": self.proteinas_objetivo,
            "carbohidratos_objetivo": self.carbohidratos_objetivo,
            "grasas_objetivo": self.grasas_objetivo,
            "fecha_inicio": self.fecha_inicio.isoformat() if isinstance(self.fecha_inicio, date) else self.fecha_inicio,
            "fecha_fin": self.fecha_fin.isoformat() if isinstance(self.fecha_fin, date) else self.fecha_fin
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], meta_id: Optional[str] = None) -> "MetaCalorica":
        """Crear instancia desde diccionario"""
        fecha_inicio = data.get("fecha_inicio")
        if fecha_inicio and isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        
        fecha_fin = data.get("fecha_fin")
        if fecha_fin and isinstance(fecha_fin, str):
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        
        return cls(
            meta_id=meta_id or data.get("id"),
            calorias_diarias=data.get("calorias_diarias", 2000.0),
            deficit_calorico=data.get("deficit_calorico", 0.0),
            proteinas_objetivo=data.get("proteinas_objetivo", 0.0),
            carbohidratos_objetivo=data.get("carbohidratos_objetivo", 0.0),
            grasas_objetivo=data.get("grasas_objetivo", 0.0),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

