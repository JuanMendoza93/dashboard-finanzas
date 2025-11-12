"""
Servicio para gestión de peso y metas de pérdida de peso
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
import streamlit as st
from models.peso import RegistroPeso, MetaPeso
from utils.database import firebase_get, firebase_push, firebase_set, firebase_delete
from utils.firebase_namespace import get_nutrition_path


class PesoService:
    """Servicio para operaciones con peso"""
    
    @staticmethod
    @st.cache_data(ttl=60, max_entries=30, show_spinner=False)
    def _obtener_registros_cached() -> List[RegistroPeso]:
        """Obtener todos los registros de peso (función interna cacheada)"""
        try:
            path = get_nutrition_path("registros_peso")
            registros_data = firebase_get(path)
            
            if not registros_data:
                return []
            
            registros = []
            for registro_id, registro_data in registros_data.items():
                registro_data["id"] = registro_id
                registros.append(RegistroPeso.from_dict(registro_data, registro_id))
            
            # Ordenar por fecha (más reciente primero)
            registros.sort(key=lambda x: x.fecha, reverse=True)
            return registros
        except Exception as e:
            print(f"Error obteniendo registros de peso: {e}")
            return []
    
    @staticmethod
    def obtener_todos() -> List[RegistroPeso]:
        """Obtener todos los registros de peso (con caché)"""
        return PesoService._obtener_registros_cached()
    
    @staticmethod
    def obtener_por_fecha(fecha: date) -> Optional[RegistroPeso]:
        """Obtener registro de peso por fecha"""
        registros = PesoService.obtener_todos()
        return next((r for r in registros if r.fecha == fecha), None)
    
    @staticmethod
    def obtener_mas_reciente() -> Optional[RegistroPeso]:
        """Obtener el registro de peso más reciente"""
        registros = PesoService.obtener_todos()
        return registros[0] if registros else None
    
    @staticmethod
    def agregar_registro(registro: RegistroPeso) -> bool:
        """Agregar nuevo registro de peso (invalida caché)"""
        try:
            path = get_nutrition_path("registros_peso")
            result = firebase_push(path, registro.to_dict())
            if result:
                PesoService._obtener_registros_cached.clear()
            return result is not None
        except Exception as e:
            print(f"Error agregando registro de peso: {e}")
            return False
    
    @staticmethod
    @st.cache_data(ttl=300, max_entries=5, show_spinner=False)
    def obtener_meta_actual() -> Optional[MetaPeso]:
        """Obtener la meta de peso actual (con caché)"""
        try:
            path = get_nutrition_path("metas_peso/actual")
            meta_data = firebase_get(path)
            
            if not meta_data:
                return None
            
            return MetaPeso.from_dict(meta_data)
        except Exception as e:
            print(f"Error obteniendo meta de peso: {e}")
            return None
    
    @staticmethod
    def guardar_meta(meta: MetaPeso) -> bool:
        """Guardar o actualizar meta de peso (invalida caché)"""
        try:
            path = get_nutrition_path("metas_peso/actual")
            result = firebase_set(path, meta.to_dict())
            if result:
                PesoService.obtener_meta_actual.clear()
            return result
        except Exception as e:
            print(f"Error guardando meta de peso: {e}")
            return False
    
    @staticmethod
    def calcular_perdida_esperada(deficit_calorico_semanal: float, semanas: int = 1) -> float:
        """
        Calcular pérdida de peso esperada basada en déficit calórico
        
        Fórmula: 1 kg de grasa ≈ 7700 calorías
        Si tienes un déficit de X calorías por semana, perderás aproximadamente X/7700 kg por semana
        
        Args:
            deficit_calorico_semanal: Déficit calórico semanal en calorías
            semanas: Número de semanas
            
        Returns:
            Pérdida de peso esperada en kg
        """
        # 1 kg de grasa = aproximadamente 7700 calorías
        CALORIAS_POR_KG = 7700.0
        
        # Calcular pérdida por semana
        perdida_por_semana = deficit_calorico_semanal / CALORIAS_POR_KG
        
        # Multiplicar por número de semanas
        return perdida_por_semana * semanas

