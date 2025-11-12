"""
Servicio para gestión de registros nutricionales diarios
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
import streamlit as st
from models.registro_diario import RegistroDiario
from utils.database import firebase_get, firebase_push, firebase_set, firebase_delete
from utils.firebase_namespace import get_nutrition_path


class RegistroNutricionalService:
    """Servicio para operaciones con registros nutricionales"""
    
    @staticmethod
    @st.cache_data(ttl=60, max_entries=30, show_spinner=False)
    def _obtener_por_fecha_cached(fecha: date) -> Optional[RegistroDiario]:
        """Obtener registro por fecha (función interna cacheada)"""
        try:
            fecha_str = fecha.isoformat()
            path = get_nutrition_path(f"registros_diarios/{fecha_str}")
            registro_data = firebase_get(path)
            
            if not registro_data:
                return None
            
            return RegistroDiario.from_dict(registro_data, fecha_str)
        except Exception as e:
            print(f"Error obteniendo registro del {fecha}: {e}")
            return None
    
    @staticmethod
    def obtener_por_fecha(fecha: date) -> Optional[RegistroDiario]:
        """Obtener registro de una fecha específica (con caché)"""
        return RegistroNutricionalService._obtener_por_fecha_cached(fecha)
    
    @staticmethod
    def obtener_por_rango(fecha_inicio: date, fecha_fin: date) -> List[RegistroDiario]:
        """Obtener registros en un rango de fechas"""
        try:
            registros = []
            current_date = fecha_inicio
            
            while current_date <= fecha_fin:
                registro = RegistroNutricionalService.obtener_por_fecha(current_date)
                if registro:
                    registros.append(registro)
                current_date = datetime(current_date.year, current_date.month, current_date.day).date()
                from datetime import timedelta
                current_date = current_date + timedelta(days=1)
            
            return registros
        except Exception as e:
            print(f"Error obteniendo registros por rango: {e}")
            return []
    
    @staticmethod
    def crear_o_actualizar(fecha: date, comidas: List[Dict[str, Any]]) -> bool:
        """Crear o actualizar registro del día (invalida caché)"""
        try:
            fecha_str = fecha.isoformat()
            path = get_nutrition_path(f"registros_diarios/{fecha_str}")
            
            registro_data = {
                "fecha": fecha_str,
                "comidas": comidas
            }
            
            result = firebase_set(path, registro_data)
            if result:
                RegistroNutricionalService._obtener_por_fecha_cached.clear()
            return result
        except Exception as e:
            print(f"Error creando/actualizando registro del {fecha}: {e}")
            return False
    
    @staticmethod
    def agregar_comida(fecha: date, comida: Dict[str, Any]) -> bool:
        """Agregar una comida al registro del día"""
        try:
            # Limpiar caché antes de obtener el registro para asegurar datos actualizados
            RegistroNutricionalService._obtener_por_fecha_cached.clear()
            
            registro = RegistroNutricionalService.obtener_por_fecha(fecha)
            
            if registro:
                # Agregar a comidas existentes
                registro.comidas.append(comida)
                comidas_actualizadas = registro.comidas
            else:
                # Crear nuevo registro
                comidas_actualizadas = [comida]
            
            # Guardar y limpiar caché
            result = RegistroNutricionalService.crear_o_actualizar(fecha, comidas_actualizadas)
            
            # Limpiar caché después de guardar para asegurar que se obtenga el registro actualizado
            if result:
                RegistroNutricionalService._obtener_por_fecha_cached.clear()
            
            return result
        except Exception as e:
            print(f"Error agregando comida al registro del {fecha}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def eliminar_comida(fecha: date, comida_index: int) -> bool:
        """Eliminar una comida del registro del día"""
        try:
            registro = RegistroNutricionalService.obtener_por_fecha(fecha)
            
            if not registro or comida_index >= len(registro.comidas):
                return False
            
            registro.comidas.pop(comida_index)
            return RegistroNutricionalService.crear_o_actualizar(fecha, registro.comidas)
        except Exception as e:
            print(f"Error eliminando comida del registro del {fecha}: {e}")
            return False

