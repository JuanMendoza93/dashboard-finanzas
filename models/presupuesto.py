"""
Modelo para Presupuesto y Metas
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Presupuesto:
    """Modelo para presupuesto mensual"""
    
    presupuesto_base: float
    gastos_recurrentes: float
    total_mensual: float
    fecha_actualizacion: Optional[datetime] = None
    
    def __post_init__(self):
        if self.fecha_actualizacion is None:
            self.fecha_actualizacion = datetime.now()
        self.total_mensual = self.presupuesto_base + self.gastos_recurrentes
    
    def actualizar_gastos_recurrentes(self, nuevos_gastos: float) -> None:
        """Actualizar gastos recurrentes"""
        self.gastos_recurrentes = nuevos_gastos
        self.total_mensual = self.presupuesto_base + self.gastos_recurrentes
        self.fecha_actualizacion = datetime.now()
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para Firebase"""
        return {
            "presupuesto_base": self.presupuesto_base,
            "gastos_recurrentes": self.gastos_recurrentes,
            "total_mensual": self.total_mensual,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Presupuesto':
        """Crear instancia desde diccionario de Firebase"""
        return cls(
            presupuesto_base=float(data.get("presupuesto_base", 0)),
            gastos_recurrentes=float(data.get("gastos_recurrentes", 0)),
            total_mensual=float(data.get("total_mensual", 0)),
            fecha_actualizacion=datetime.fromisoformat(data["fecha_actualizacion"]) if data.get("fecha_actualizacion") else None
        )


@dataclass
class MetaAhorro:
    """Modelo para metas de ahorro"""
    
    meta_mensual: float
    meta_anual: float
    fecha_actualizacion: Optional[datetime] = None
    
    def __post_init__(self):
        if self.fecha_actualizacion is None:
            self.fecha_actualizacion = datetime.now()
    
    def calcular_progreso_mensual(self, ahorro_actual: float) -> float:
        """Calcular progreso mensual (0-1)"""
        if self.meta_mensual == 0:
            return 0
        return min(ahorro_actual / self.meta_mensual, 1.0)
    
    def calcular_progreso_anual(self, ahorro_actual: float) -> float:
        """Calcular progreso anual (0-1)"""
        if self.meta_anual == 0:
            return 0
        return min(ahorro_actual / self.meta_anual, 1.0)
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para Firebase"""
        return {
            "meta_mensual": self.meta_mensual,
            "meta_anual": self.meta_anual,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MetaAhorro':
        """Crear instancia desde diccionario de Firebase"""
        return cls(
            meta_mensual=float(data.get("meta_mensual", 0)),
            meta_anual=float(data.get("meta_anual", 0)),
            fecha_actualizacion=datetime.fromisoformat(data["fecha_actualizacion"]) if data.get("fecha_actualizacion") else None
        )
