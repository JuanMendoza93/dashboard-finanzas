"""
Modelo para registro de peso y metas de pérdida de peso
"""

from typing import Optional, Dict, Any
from datetime import datetime, date


class RegistroPeso:
    """Modelo de registro de peso"""
    
    def __init__(
        self,
        fecha: date,
        peso: float,
        grasa_corporal: Optional[float] = None,
        masa_muscular: Optional[float] = None,
        fuente: str = "manual",  # "manual" o "bascula_inteligente"
        # Campos adicionales
        altura: Optional[float] = None,  # en metros para calcular IMC
        porcentaje_agua: Optional[float] = None,
        porcentaje_masa_muscular: Optional[float] = None,
        porcentaje_masa_osea: Optional[float] = None,
        metabolismo_basal: Optional[float] = None,  # MB
        grasa_visceral: Optional[float] = None,
        masa_magra_corporal: Optional[float] = None,
        masa_grasa_corporal: Optional[float] = None,
        masa_osea: Optional[float] = None,
        registro_id: Optional[str] = None
    ):
        self.id = registro_id
        self.fecha = fecha if isinstance(fecha, date) else datetime.strptime(fecha, "%Y-%m-%d").date()
        self.peso = peso
        self.grasa_corporal = grasa_corporal
        self.masa_muscular = masa_muscular
        self.fuente = fuente
        self.altura = altura
        self.porcentaje_agua = porcentaje_agua
        self.porcentaje_masa_muscular = porcentaje_masa_muscular
        self.porcentaje_masa_osea = porcentaje_masa_osea
        self.metabolismo_basal = metabolismo_basal
        self.grasa_visceral = grasa_visceral
        self.masa_magra_corporal = masa_magra_corporal
        self.masa_grasa_corporal = masa_grasa_corporal
        self.masa_osea = masa_osea
    
    @property
    def imc(self) -> Optional[float]:
        """Calcular IMC si hay altura"""
        if self.altura and self.altura > 0 and self.peso > 0:
            return self.peso / (self.altura ** 2)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para Firebase"""
        return {
            "fecha": self.fecha.isoformat(),
            "peso": self.peso,
            "grasa_corporal": self.grasa_corporal,
            "masa_muscular": self.masa_muscular,
            "fuente": self.fuente,
            "altura": self.altura,
            "porcentaje_agua": self.porcentaje_agua,
            "porcentaje_masa_muscular": self.porcentaje_masa_muscular,
            "porcentaje_masa_osea": self.porcentaje_masa_osea,
            "metabolismo_basal": self.metabolismo_basal,
            "grasa_visceral": self.grasa_visceral,
            "masa_magra_corporal": self.masa_magra_corporal,
            "masa_grasa_corporal": self.masa_grasa_corporal,
            "masa_osea": self.masa_osea
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], registro_id: Optional[str] = None) -> "RegistroPeso":
        """Crear instancia desde diccionario"""
        fecha = data.get("fecha")
        if fecha and isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        
        return cls(
            registro_id=registro_id or data.get("id"),
            fecha=fecha,
            peso=data.get("peso", 0.0),
            grasa_corporal=data.get("grasa_corporal"),
            masa_muscular=data.get("masa_muscular"),
            fuente=data.get("fuente", "manual"),
            altura=data.get("altura"),
            porcentaje_agua=data.get("porcentaje_agua"),
            porcentaje_masa_muscular=data.get("porcentaje_masa_muscular"),
            porcentaje_masa_osea=data.get("porcentaje_masa_osea"),
            metabolismo_basal=data.get("metabolismo_basal"),
            grasa_visceral=data.get("grasa_visceral"),
            masa_magra_corporal=data.get("masa_magra_corporal"),
            masa_grasa_corporal=data.get("masa_grasa_corporal"),
            masa_osea=data.get("masa_osea")
        )


class MetaPeso:
    """Modelo de meta de pérdida de peso"""
    
    def __init__(
        self,
        peso_actual: float,
        peso_objetivo: float,
        fecha_inicio: Optional[date] = None,
        meta_id: Optional[str] = None
    ):
        self.id = meta_id
        self.peso_actual = peso_actual
        self.peso_objetivo = peso_objetivo
        self.fecha_inicio = fecha_inicio or date.today()
    
    @property
    def peso_a_perder(self) -> float:
        """Peso que se necesita perder"""
        return self.peso_actual - self.peso_objetivo
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para Firebase"""
        return {
            "peso_actual": self.peso_actual,
            "peso_objetivo": self.peso_objetivo,
            "fecha_inicio": self.fecha_inicio.isoformat() if isinstance(self.fecha_inicio, date) else self.fecha_inicio
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], meta_id: Optional[str] = None) -> "MetaPeso":
        """Crear instancia desde diccionario"""
        fecha_inicio = data.get("fecha_inicio")
        if fecha_inicio and isinstance(fecha_inicio, str):
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        
        return cls(
            meta_id=meta_id or data.get("id"),
            peso_actual=data.get("peso_actual", 0.0),
            peso_objetivo=data.get("peso_objetivo", 0.0),
            fecha_inicio=fecha_inicio
        )

