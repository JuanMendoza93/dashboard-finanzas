"""
Servicio para gestión de comidas y alimentos
"""

from typing import List, Optional, Dict, Any
import streamlit as st
from models.comida import Comida
from utils.database import firebase_get, firebase_push, firebase_set, firebase_delete
from utils.firebase_namespace import get_nutrition_path


class ComidaService:
    """Servicio para operaciones con comidas"""
    
    @staticmethod
    @st.cache_data(ttl=300, max_entries=50, show_spinner=False)
    def _obtener_todas_cached() -> List[Comida]:
        """Obtener todas las comidas (función interna cacheada)"""
        try:
            path = get_nutrition_path("comidas")
            comidas_data = firebase_get(path)
            if not comidas_data:
                return []
            
            comidas = []
            for comida_id, comida_data in comidas_data.items():
                comida_data["id"] = comida_id
                comidas.append(Comida.from_dict(comida_data, comida_id))
            return comidas
        except Exception as e:
            print(f"Error obteniendo comidas: {e}")
            return []
    
    @staticmethod
    def obtener_todas() -> List[Comida]:
        """Obtener todas las comidas (con caché)"""
        return ComidaService._obtener_todas_cached()
    
    @staticmethod
    def obtener_por_id(comida_id: str) -> Optional[Comida]:
        """Obtener comida por ID"""
        try:
            path = get_nutrition_path(f"comidas/{comida_id}")
            comida_data = firebase_get(path)
            if not comida_data:
                return None
            
            comida_data["id"] = comida_id
            return Comida.from_dict(comida_data, comida_id)
        except Exception as e:
            print(f"Error obteniendo comida {comida_id}: {e}")
            return None
    
    @staticmethod
    def crear(comida: Comida) -> Optional[Comida]:
        """Crear nueva comida (invalida caché)"""
        try:
            path = get_nutrition_path("comidas")
            result = firebase_push(path, comida.to_dict())
            if result and "name" in result:
                ComidaService._obtener_todas_cached.clear()
                comida.id = result["name"]
                return comida
            return None
        except Exception as e:
            print(f"Error creando comida: {e}")
            return None
    
    @staticmethod
    def actualizar(comida_id: str, datos_actualizados: Dict[str, Any]) -> bool:
        """Actualizar comida existente (invalida caché)"""
        try:
            path = get_nutrition_path(f"comidas/{comida_id}")
            result = firebase_set(path, datos_actualizados)
            if result:
                ComidaService._obtener_todas_cached.clear()
            return result
        except Exception as e:
            print(f"Error actualizando comida {comida_id}: {e}")
            return False
    
    @staticmethod
    def eliminar(comida_id: str) -> bool:
        """Eliminar comida (invalida caché)"""
        try:
            path = get_nutrition_path(f"comidas/{comida_id}")
            result = firebase_delete(path)
            if result:
                ComidaService._obtener_todas_cached.clear()
            return result
        except Exception as e:
            print(f"Error eliminando comida {comida_id}: {e}")
            return False

