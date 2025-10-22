"""
Modelo para Movimiento Financiero
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date


@dataclass
class Movimiento:
    """Modelo para un movimiento financiero"""
    
    id: str
    fecha: date
    concepto: str
    categoria: str
    tipo_gasto: str
    monto: float
    tipo: str  # "Gasto" o "Ingreso"
    fecha_creacion: Optional[datetime] = None
    
    def __post_init__(self):
        if self.fecha_creacion is None:
            self.fecha_creacion = datetime.now()
    
    @property
    def es_gasto(self) -> bool:
        """Verificar si es un gasto"""
        return self.tipo == "Gasto"
    
    @property
    def es_ingreso(self) -> bool:
        """Verificar si es un ingreso"""
        return self.tipo == "Ingreso"
    
    @property
    def monto_absoluto(self) -> float:
        """Obtener el monto absoluto"""
        return abs(self.monto)
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para Firebase"""
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat(),
            "concepto": self.concepto,
            "categoria": self.categoria,
            "tipo_gasto": self.tipo_gasto,
            "monto": self.monto,
            "tipo": self.tipo,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Movimiento':
        """Crear instancia desde diccionario de Firebase"""
        return cls(
            id=data.get("id", ""),
            fecha=datetime.fromisoformat(data["fecha"]).date() if data.get("fecha") else date.today(),
            concepto=data.get("concepto", ""),
            categoria=data.get("categoria", ""),
            tipo_gasto=data.get("tipo_gasto", ""),
            monto=float(data.get("monto", 0)),
            tipo=data.get("tipo", "Gasto"),
            fecha_creacion=datetime.fromisoformat(data["fecha_creacion"]) if data.get("fecha_creacion") else None
        )
