"""
Servicio para gestión de cuentas bancarias
"""

from typing import List, Optional
import streamlit as st
from models.cuenta import Cuenta
from utils.database import db, firebase_get, firebase_set, firebase_delete, firebase_push
from utils.config_manager import config_manager


class CuentaService:
    """Servicio para operaciones con cuentas"""
    
    @staticmethod
    @st.cache_data(ttl=300, max_entries=10, show_spinner=False)
    def _obtener_todas_cached() -> List[Cuenta]:
        """Obtener todas las cuentas (función interna cacheada)"""
        try:
            cuentas_data = firebase_get("cuentas")
            if not cuentas_data:
                return []
            
            cuentas = []
            for cuenta_id, cuenta_data in cuentas_data.items():
                cuenta_data["id"] = cuenta_id
                cuenta_obj = Cuenta.from_dict(cuenta_data)
                cuentas.append(cuenta_obj)
            return cuentas
        except Exception as e:
            print(f"Error obteniendo cuentas: {e}")
            return []
    
    @staticmethod
    def obtener_todas() -> List[Cuenta]:
        """Obtener todas las cuentas (con caché)"""
        return CuentaService._obtener_todas_cached()
    
    @staticmethod
    def obtener_por_id(cuenta_id: str) -> Optional[Cuenta]:
        """Obtener cuenta por ID"""
        try:
            cuenta_data = firebase_get(f"cuentas/{cuenta_id}")
            if not cuenta_data:
                return None
            
            cuenta_data["id"] = cuenta_id
            return Cuenta.from_dict(cuenta_data)
        except Exception as e:
            print(f"Error obteniendo cuenta {cuenta_id}: {e}")
            return None
    
    @staticmethod
    def crear(nombre: str, saldo_inicial: float = 0.0) -> Optional[Cuenta]:
        """Crear nueva cuenta (invalida caché)"""
        try:
            # Validar que el nombre no esté duplicado
            cuentas_existentes = CuentaService.obtener_todas()
            nombres_existentes = [cuenta.nombre.lower() for cuenta in cuentas_existentes]
            
            if nombre.lower() in nombres_existentes:
                print(f"Error: Ya existe una cuenta con el nombre '{nombre}'")
                return None
            
            cuenta_data = {
                "nombre": nombre,
                "saldo": saldo_inicial
            }
            
            # Agregar a Firebase Realtime Database
            result = firebase_push("cuentas", cuenta_data)
            if result and "name" in result:
                # Invalidar caché de cuentas
                CuentaService._obtener_todas_cached.clear()
                cuenta_data["id"] = result["name"]
                return Cuenta.from_dict(cuenta_data)
            return None
        except Exception as e:
            print(f"Error creando cuenta: {e}")
            return None
    
    @staticmethod
    def actualizar(cuenta_id: str, nombre: str, saldo: float) -> bool:
        """Actualizar cuenta existente (invalida caché)"""
        try:
            # Validar que el nombre no esté duplicado (excluyendo la cuenta actual)
            cuentas_existentes = CuentaService.obtener_todas()
            nombres_existentes = [cuenta.nombre.lower() for cuenta in cuentas_existentes if cuenta.id != cuenta_id]
            
            if nombre.lower() in nombres_existentes:
                print(f"Error: Ya existe otra cuenta con el nombre '{nombre}'")
                return False
            
            cuenta_data = {
                "nombre": nombre,
                "saldo": saldo
            }
            result = firebase_set(f"cuentas/{cuenta_id}", cuenta_data)
            if result:
                # Invalidar caché de cuentas
                CuentaService._obtener_todas_cached.clear()
            return result
        except Exception as e:
            print(f"Error actualizando cuenta {cuenta_id}: {e}")
            return False
    
    @staticmethod
    def eliminar(cuenta_id: str) -> bool:
        """Eliminar cuenta (invalida caché)"""
        try:
            result = firebase_delete(f"cuentas/{cuenta_id}")
            if result:
                # Invalidar caché de cuentas
                CuentaService._obtener_todas_cached.clear()
            return result
        except Exception as e:
            print(f"Error eliminando cuenta {cuenta_id}: {e}")
            return False
    
    @staticmethod
    def agregar_dinero(cuenta_id: str, monto: float) -> bool:
        """Agregar dinero a una cuenta"""
        try:
            cuenta = CuentaService.obtener_por_id(cuenta_id)
            if not cuenta:
                return False
            
            cuenta.agregar_dinero(monto)
            return CuentaService.actualizar(cuenta_id, cuenta.nombre, cuenta.saldo)
        except Exception as e:
            print(f"Error agregando dinero a cuenta {cuenta_id}: {e}")
            return False
    
    @staticmethod
    def calcular_saldo_total() -> float:
        """Calcular saldo total de todas las cuentas"""
        try:
            cuentas = CuentaService.obtener_todas()
            return sum(cuenta.saldo for cuenta in cuentas)
        except Exception as e:
            print(f"Error calculando saldo total: {e}")
            return 0.0
