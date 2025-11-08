"""
Modelo para historial de peso
"""

from typing import Optional, Dict, Any
from datetime import datetime, date


class PesoHistorico:
    """Modelo de registro de peso"""
    
    def __init__(
        self,
        fecha: date,
        peso: float,
        grasa_corporal: Optional[float] = None,
        masa_muscular: Optional[float] = None,
        fuente: str = "manual",  # "manual", "eufy", "fitbit", etc.
        notas: str = "",
        peso_id: Optional[str] = None
    ):
        self.id = peso_id
        self.fecha = fecha if isinstance(fecha, date) else datetime.strptime(fecha, "%Y-%m-%d").date()
        self.peso = peso
        self.grasa_corporal = grasa_corporal
        self.masa_muscular = masa_muscular
        self.fuente = fuente
        self.notas = notas
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para Firebase"""
        return {
            "fecha": self.fecha.isoformat(),
            "peso": self.peso,
            "grasa_corporal": self.grasa_corporal,
            "masa_muscular": self.masa_muscular,
            "fuente": self.fuente,
            "notas": self.notas
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], peso_id: Optional[str] = None) -> "PesoHistorico":
        """Crear instancia desde diccionario"""
        fecha = data.get("fecha")
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        
        return cls(
            peso_id=peso_id or data.get("id"),
            fecha=fecha,
            peso=data.get("peso", 0.0),
            grasa_corporal=data.get("grasa_corporal"),
            masa_muscular=data.get("masa_muscular"),
            fuente=data.get("fuente", "manual"),
            notas=data.get("notas", "")
        )

