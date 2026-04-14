"""
Modelo para Cuenta Bancaria
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Cuenta:
    """Modelo para una cuenta bancaria"""
    
    id: str
    nombre: str
    saldo: float
    rendimiento_anual: float = 0.0
    limite: float = 0.0
    fecha_creacion: Optional[datetime] = None
    
    def __post_init__(self):
        if self.fecha_creacion is None:
            self.fecha_creacion = datetime.now()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Cuenta':
        """Crear instancia desde diccionario"""
        return cls(
            id=data.get('id', ''),
            nombre=data.get('nombre', ''),
            saldo=float(data.get('saldo', 0)),
            rendimiento_anual=float(data.get('rendimiento_anual', data.get('rendimiento', 0))) ,
            limite=float(data.get('limite', 0)),
            fecha_creacion=data.get('fecha_creacion')
        )
    
    def agregar_dinero(self, monto: float) -> None:
        """Agregar dinero a la cuenta"""
        if monto < 0:
            raise ValueError("El monto debe ser positivo")
        self.saldo += monto
    
    def retirar_dinero(self, monto: float) -> None:
        """Retirar dinero de la cuenta"""
        if monto < 0:
            raise ValueError("El monto debe ser positivo")
        if monto > self.saldo:
            raise ValueError("Fondos insuficientes")
        self.saldo -= monto
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para Firebase"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "saldo": self.saldo,
            "rendimiento_anual": self.rendimiento_anual,
            "limite": self.limite,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
    
