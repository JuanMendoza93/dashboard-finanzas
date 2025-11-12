"""
Modelo para metas calóricas y nutricionales
"""

from typing import Optional, Dict, Any
from datetime import datetime, date


class MetaCalorica:
    """Modelo de meta calórica semanal"""
    
    def __init__(
        self,
        calorias_semanales: float,
        deficit_calorico: float = 0.0,
        proteinas_objetivo: float = 0.0,
        carbohidratos_objetivo: float = 0.0,
        grasas_objetivo: float = 0.0,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        meta_id: Optional[str] = None
    ):
        self.id = meta_id
        self.calorias_semanales = calorias_semanales
        self.deficit_calorico = deficit_calorico
        self.proteinas_objetivo = proteinas_objetivo
        self.carbohidratos_objetivo = carbohidratos_objetivo
        self.grasas_objetivo = grasas_objetivo
        self.fecha_inicio = fecha_inicio or date.today()
        self.fecha_fin = fecha_fin
    
    @property
    def calorias_objetivo(self) -> float:
        """Calorías objetivo diarias considerando déficit (semanal / 7)"""
        return (self.calorias_semanales - self.deficit_calorico) / 7
    
    @property
    def calorias_objetivo_semanal(self) -> float:
        """Calorías objetivo semanales considerando déficit"""
        return self.calorias_semanales - self.deficit_calorico
    
    # Mantener compatibilidad con código antiguo
    @property
    def calorias_diarias(self) -> float:
        """Calorías diarias (calculadas desde semanal)"""
        return self.calorias_semanales / 7
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para Firebase"""
        return {
            "calorias_semanales": self.calorias_semanales,
            "calorias_diarias": self.calorias_diarias,  # Para compatibilidad
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
        
        # Compatibilidad: si tiene calorias_diarias, convertir a semanal
        calorias_semanales = data.get("calorias_semanales")
        if not calorias_semanales:
            calorias_diarias = data.get("calorias_diarias", 2000.0)
            calorias_semanales = calorias_diarias * 7
        
        return cls(
            meta_id=meta_id or data.get("id"),
            calorias_semanales=calorias_semanales,
            deficit_calorico=data.get("deficit_calorico", 0.0),
            proteinas_objetivo=data.get("proteinas_objetivo", 0.0),
            carbohidratos_objetivo=data.get("carbohidratos_objetivo", 0.0),
            grasas_objetivo=data.get("grasas_objetivo", 0.0),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

