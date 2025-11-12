"""
Servicio para gestión de metas calóricas
"""

from typing import Optional, Dict, Any
from datetime import date, datetime, timedelta
import streamlit as st
from models.meta_calorica import MetaCalorica
from utils.database import firebase_get, firebase_set
from utils.firebase_namespace import get_nutrition_path
from utils.week_helpers import get_week_start_end, get_current_week


class MetaCaloricaService:
    """Servicio para operaciones con metas calóricas"""
    
    @staticmethod
    @st.cache_data(ttl=300, max_entries=10, show_spinner=False)
    def obtener_meta_actual() -> Optional[MetaCalorica]:
        """Obtener la meta calórica actual para la semana actual (con caché)"""
        try:
            path = get_nutrition_path("metas_caloricas")
            metas_data = firebase_get(path)
            
            if not metas_data:
                return None
            
            # Obtener la meta más reciente o la actual
            meta_data = metas_data.get("actual")
            if not meta_data:
                # Si no hay "actual", obtener la primera disponible
                if isinstance(metas_data, dict):
                    for key, value in metas_data.items():
                        if isinstance(value, dict):
                            meta_data = value
                            break
            
            if not meta_data:
                return None
            
            meta = MetaCalorica.from_dict(meta_data)
            
            # Verificar si la meta es para la semana actual
            inicio_semana_actual, _ = get_current_week()
            inicio_semana_meta, _ = get_week_start_end(meta.fecha_inicio)
            
            # Si la meta es de una semana anterior, usar esa meta (como solicitó el usuario)
            # Si no hay meta para esta semana, usar la última disponible
            if inicio_semana_meta <= inicio_semana_actual:
                return meta
            
            # Si la meta es de una semana futura, buscar la última meta anterior
            # Por ahora, retornamos la meta disponible
            return meta
        except Exception as e:
            print(f"Error obteniendo meta calórica: {e}")
            return None
    
    @staticmethod
    def guardar_meta(meta: MetaCalorica) -> bool:
        """Guardar o actualizar meta calórica (invalida caché)"""
        try:
            path = get_nutrition_path("metas_caloricas/actual")
            result = firebase_set(path, meta.to_dict())
            if result:
                MetaCaloricaService.obtener_meta_actual.clear()
            return result
        except Exception as e:
            print(f"Error guardando meta calórica: {e}")
            return False

