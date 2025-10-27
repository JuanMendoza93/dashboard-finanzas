"""
Servicio para gestión de movimientos financieros
"""

from typing import List, Optional
from datetime import date, datetime
from models.movimiento import Movimiento
from utils.database import db, firebase_get, firebase_set, firebase_delete
from utils.config_manager import config_manager


class MovimientoService:
    """Servicio para operaciones con movimientos"""
    
    @staticmethod
    def obtener_todos() -> List[Movimiento]:
        """Obtener todos los movimientos"""
        try:
            movimientos_data = firebase_get("movimientos")
            if not movimientos_data:
                return []
            
            movimientos = []
            for movimiento_id, movimiento_data in movimientos_data.items():
                movimiento_data["id"] = movimiento_id
                movimientos.append(Movimiento.from_dict(movimiento_data))
            return movimientos
        except Exception as e:
            print(f"Error obteniendo movimientos: {e}")
            return []
    
    @staticmethod
    def obtener_por_mes(mes: int, año: int) -> List[Movimiento]:
        """Obtener movimientos de un mes específico"""
        try:
            movimientos = MovimientoService.obtener_todos()
            return [m for m in movimientos if m.fecha.month == mes and m.fecha.year == año]
        except Exception as e:
            print(f"Error obteniendo movimientos del mes: {e}")
            return []
    
    @staticmethod
    def crear(fecha: date, concepto: str, categoria: str, tipo_gasto: str, 
              monto: float, tipo: str, pagos_recibidos: float = 0.0) -> Optional[Movimiento]:
        """Crear nuevo movimiento"""
        try:
            movimiento_data = {
                "fecha": fecha.isoformat(),
                "concepto": concepto,
                "categoria": categoria,
                "tipo_gasto": tipo_gasto,
                "monto": monto,
                "tipo": tipo,
                "pagos_recibidos": pagos_recibidos
            }
            
            # Agregar a Firebase Realtime Database
            from utils.database import firebase_push
            result = firebase_push("movimientos", movimiento_data)
            if result and "name" in result:
                movimiento_data["id"] = result["name"]
                return Movimiento.from_dict(movimiento_data)
            return None
        except Exception as e:
            print(f"Error creando movimiento: {e}")
            return None
    
    @staticmethod
    def eliminar(movimiento_id: str) -> bool:
        """Eliminar movimiento"""
        try:
            return firebase_delete(f"movimientos/{movimiento_id}")
        except Exception as e:
            print(f"Error eliminando movimiento {movimiento_id}: {e}")
            return False
    
    @staticmethod
    def calcular_gastos_mes(mes: int, año: int) -> float:
        """Calcular gastos totales de un mes (restar pagos recibidos de los gastos)"""
        try:
            movimientos = MovimientoService.obtener_por_mes(mes, año)
            total_gastos = sum(m.monto for m in movimientos if m.tipo == "Gasto")
            total_pagos = sum(m.monto for m in movimientos if m.tipo == "Pago")
            return total_gastos - total_pagos
        except Exception as e:
            print(f"Error calculando gastos del mes: {e}")
            return 0.0
    
    @staticmethod
    def calcular_ingresos_mes(mes: int, año: int) -> float:
        """Calcular ingresos totales de un mes"""
        try:
            movimientos = MovimientoService.obtener_por_mes(mes, año)
            return sum(m.monto for m in movimientos if m.es_ingreso)
        except Exception as e:
            print(f"Error calculando ingresos del mes: {e}")
            return 0.0
    
    @staticmethod
    def obtener_top_gastos(limite: int = 3) -> List[dict]:
        """Obtener las categorías con más gastos (agrupado por categoría)"""
        try:
            movimientos = MovimientoService.obtener_todos()
            gastos = [m for m in movimientos if m.es_gasto]
            
            # Agrupar por categoría y sumar montos
            gastos_por_categoria = {}
            for gasto in gastos:
                categoria = gasto.categoria
                if categoria not in gastos_por_categoria:
                    gastos_por_categoria[categoria] = 0
                gastos_por_categoria[categoria] += gasto.monto_absoluto
            
            # Convertir a lista y ordenar por monto
            top_categorias = []
            for categoria, total in gastos_por_categoria.items():
                top_categorias.append({
                    "categoria": categoria,
                    "total": total
                })
            
            # Ordenar por total descendente
            top_categorias.sort(key=lambda x: x["total"], reverse=True)
            return top_categorias[:limite]
        except Exception as e:
            print(f"Error obteniendo top gastos: {e}")
            return []
    
    @staticmethod
    def obtener_gastos_por_categoria(mes: int, año: int) -> dict:
        """Obtener gastos agrupados por categoría"""
        try:
            movimientos = MovimientoService.obtener_por_mes(mes, año)
            gastos_por_categoria = {}
            
            for movimiento in movimientos:
                if movimiento.es_gasto:
                    categoria = movimiento.categoria
                    if categoria not in gastos_por_categoria:
                        gastos_por_categoria[categoria] = 0
                    gastos_por_categoria[categoria] += movimiento.monto_absoluto
            
            return gastos_por_categoria
        except Exception as e:
            print(f"Error obteniendo gastos por categoría: {e}")
            return {}
    
    @staticmethod
    def obtener_gastos_por_tipo(mes: int, año: int) -> dict:
        """Obtener gastos agrupados por tipo de gasto"""
        try:
            movimientos = MovimientoService.obtener_por_mes(mes, año)
            gastos_por_tipo = {}
            
            for movimiento in movimientos:
                if movimiento.es_gasto:
                    tipo_gasto = movimiento.tipo_gasto
                    if tipo_gasto not in gastos_por_tipo:
                        gastos_por_tipo[tipo_gasto] = 0
                    gastos_por_tipo[tipo_gasto] += movimiento.monto_absoluto
            
            return gastos_por_tipo
        except Exception as e:
            print(f"Error obteniendo gastos por tipo: {e}")
            return {}
    
    @staticmethod
    def actualizar(movimiento_id: str, datos_actualizados: dict) -> bool:
        """Actualizar un movimiento existente"""
        try:
            from utils.database import firebase_set
            return firebase_set(f"movimientos/{movimiento_id}", datos_actualizados)
        except Exception as e:
            print(f"Error actualizando movimiento {movimiento_id}: {e}")
            return False
