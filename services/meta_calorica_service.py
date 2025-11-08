"""
Servicio para gestión de metas calóricas
"""

from typing import Optional, Dict, Any
from datetime import date, datetime
import streamlit as st
from models.meta_calorica import MetaCalorica
from utils.database import firebase_get, firebase_set
from utils.firebase_namespace import get_nutrition_path


class MetaCaloricaService:
    """Servicio para operaciones con metas calóricas"""
    
    @staticmethod
    @st.cache_data(ttl=300, max_entries=10, show_spinner=False)
    def obtener_meta_actual() -> Optional[MetaCalorica]:
        """Obtener la meta calórica actual (con caché)"""
        try:
            path = get_nutrition_path("metas_caloricas")
            metas_data = firebase_get(path)
            
            if not metas_data:
                return None
            
            # Obtener la meta más reciente o la actual
            # Por ahora, asumimos que hay una meta "actual"
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
            
            return MetaCalorica.from_dict(meta_data)
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

