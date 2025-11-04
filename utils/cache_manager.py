"""
Gestor de caché para optimizar consultas a Firebase
Usa st.cache_data de Streamlit para cachear consultas frecuentes
"""

import streamlit as st
from typing import Any, Callable, Optional
from functools import wraps
import hashlib
import json


class CacheManager:
    """Gestor centralizado de caché"""
    
    # Tiempo de expiración del caché (en segundos)
    CACHE_TTL = 300  # 5 minutos por defecto
    
    # Claves de caché para invalidar
    CACHE_KEYS = {
        'movimientos': 'cache_movimientos',
        'cuentas': 'cache_cuentas',
        'configuracion': 'cache_configuracion',
        'gastos_recurrentes': 'cache_gastos_recurrentes',
        'metas': 'cache_metas',
        'reportes_mensuales': 'cache_reportes_mensuales',
    }
    
    @staticmethod
    def invalidar_cache(clave: str):
        """Invalidar caché específico"""
        if clave in CacheManager.CACHE_KEYS:
            cache_key = CacheManager.CACHE_KEYS[clave]
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            # También invalidar el caché de Streamlit si existe
            try:
                st.cache_data.clear()
            except:
                pass
    
    @staticmethod
    def invalidar_todos():
        """Invalidar todos los cachés"""
        for cache_key in CacheManager.CACHE_KEYS.values():
            if cache_key in st.session_state:
                del st.session_state[cache_key]
        try:
            st.cache_data.clear()
        except:
            pass
    
    @staticmethod
    def obtener_cache_key(*args, **kwargs) -> str:
        """Generar clave única para caché basada en argumentos"""
        # Crear hash de los argumentos
        cache_str = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()


def cache_firebase_query(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorador para cachear consultas a Firebase
    
    Args:
        ttl: Tiempo de vida del caché en segundos (None = usar default)
        key_prefix: Prefijo para la clave del caché
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave única para esta consulta
            cache_key = f"{key_prefix}_{CacheManager.obtener_cache_key(*args, **kwargs)}"
            
            # Verificar si existe en caché
            if cache_key in st.session_state:
                cached_data, timestamp = st.session_state[cache_key]
                ttl_actual = ttl or CacheManager.CACHE_TTL
                import time
                if time.time() - timestamp < ttl_actual:
                    return cached_data
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            import time
            st.session_state[cache_key] = (result, time.time())
            return result
        
        return wrapper
    return decorator


def cache_streamlit(ttl: Optional[int] = None, max_entries: int = 100):
    """
    Wrapper para st.cache_data con configuración personalizada
    
    Args:
        ttl: Tiempo de vida del caché en segundos
        max_entries: Número máximo de entradas en caché
    """
    def decorator(func: Callable) -> Callable:
        ttl_actual = ttl or CacheManager.CACHE_TTL
        return st.cache_data(
            ttl=ttl_actual,
            max_entries=max_entries,
            show_spinner=False
        )(func)
    return decorator

