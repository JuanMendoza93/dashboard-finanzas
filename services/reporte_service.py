"""
Servicio para generación de reportes
"""

from typing import List, Dict, Any
from datetime import datetime, date
import pandas as pd
from models.cuenta import Cuenta
from models.movimiento import Movimiento
from models.presupuesto import Presupuesto, MetaAhorro
from services.cuenta_service import CuentaService
from services.movimiento_service import MovimientoService
from utils.database import firebase_get


class ReporteService:
    """Servicio para generación de reportes"""
    
    @staticmethod
    def generar_resumen_financiero() -> Dict[str, Any]:
        """Generar resumen financiero completo"""
        try:
            # Obtener datos
            cuentas = CuentaService.obtener_todas()
            movimientos = MovimientoService.obtener_todos()
            
            # Calcular métricas
            saldo_total = sum(cuenta.saldo for cuenta in cuentas)
            
            # Gastos del mes actual
            ahora = datetime.now()
            gastos_mes = MovimientoService.calcular_gastos_mes(ahora.month, ahora.year)
            ingresos_mes = MovimientoService.calcular_ingresos_mes(ahora.month, ahora.year)
            
            # Ahorro actual = Ingresos - Gastos (del mes actual)
            ahorro_actual = ingresos_mes - gastos_mes
            
            # Top gastos
            top_gastos = MovimientoService.obtener_top_gastos(5)
            
            # Gastos por categoría
            gastos_por_categoria = MovimientoService.obtener_gastos_por_categoria(ahora.month, ahora.year)
            
            # Gastos por tipo de gasto
            gastos_por_tipo = MovimientoService.obtener_gastos_por_tipo(ahora.month, ahora.year)
            
            # Obtener gastos recurrentes
            gastos_recurrentes = ReporteService._obtener_gastos_recurrentes()
            
            return {
                "saldo_total": saldo_total,
                "gastos_mes": gastos_mes,
                "ingresos_mes": ingresos_mes,
                "ahorro_actual": ahorro_actual,
                "top_gastos": top_gastos,
                "gastos_por_categoria": gastos_por_categoria,
                "gastos_por_tipo": gastos_por_tipo,
                "gastos_recurrentes": gastos_recurrentes,
                "total_cuentas": len(cuentas),
                "total_movimientos": len(movimientos)
            }
        except Exception as e:
            print(f"Error generando resumen financiero: {e}")
            return {}
    
    @staticmethod
    def _obtener_gastos_recurrentes() -> float:
        """Obtener total de gastos recurrentes"""
        try:
            from utils.database import cargar_gastos_recurrentes
            gastos_recurrentes = cargar_gastos_recurrentes()
            
            # Usar el mismo cálculo que en la página de Gastos Recurrentes
            # Sumar directamente monto_mensual (ya convertido)
            total_mensual = sum(gasto.get("monto_mensual", 0) for gasto in gastos_recurrentes)
            
            return total_mensual
        except Exception as e:
            print(f"Error obteniendo gastos recurrentes: {e}")
            return 0.0
    
    @staticmethod
    def generar_reporte_mensual(mes: int, año: int) -> Dict[str, Any]:
        """Generar reporte mensual detallado"""
        try:
            movimientos = MovimientoService.obtener_por_mes(mes, año)
            gastos = [m for m in movimientos if m.es_gasto]
            ingresos = [m for m in movimientos if m.es_ingreso]
            
            # Calcular totales
            total_gastos = sum(m.monto_absoluto for m in gastos)
            total_ingresos = sum(m.monto for m in ingresos)
            balance = total_ingresos - total_gastos
            
            # Gastos por categoría
            gastos_por_categoria = {}
            for gasto in gastos:
                categoria = gasto.categoria
                if categoria not in gastos_por_categoria:
                    gastos_por_categoria[categoria] = 0
                gastos_por_categoria[categoria] += gasto.monto_absoluto
            
            # Gastos por tipo
            gastos_por_tipo = {}
            for gasto in gastos:
                tipo = gasto.tipo_gasto
                if tipo not in gastos_por_tipo:
                    gastos_por_tipo[tipo] = 0
                gastos_por_tipo[tipo] += gasto.monto_absoluto
            
            return {
                "mes": mes,
                "año": año,
                "total_gastos": total_gastos,
                "total_ingresos": total_ingresos,
                "balance": balance,
                "gastos_por_categoria": gastos_por_categoria,
                "gastos_por_tipo": gastos_por_tipo,
                "total_movimientos": len(movimientos),
                "total_gastos_count": len(gastos),
                "total_ingresos_count": len(ingresos)
            }
        except Exception as e:
            print(f"Error generando reporte mensual: {e}")
            return {}
    
    @staticmethod
    def generar_reporte_ahorro() -> Dict[str, Any]:
        """Generar reporte de ahorro"""
        try:
            # Obtener metas
            metas_data = firebase_get("metas")
            if not metas_data:
                return {}
            
            meta_mensual = float(metas_data.get("meta_mensual", 0))
            meta_anual = float(metas_data.get("meta_anual", 0))
            
            # Calcular ahorro actual
            resumen = ReporteService.generar_resumen_financiero()
            ahorro_actual = resumen.get("ahorro_actual", 0)
            
            # Calcular progreso
            progreso_mensual = min(ahorro_actual / meta_mensual, 1.0) if meta_mensual > 0 else 0
            progreso_anual = min(ahorro_actual / meta_anual, 1.0) if meta_anual > 0 else 0
            
            return {
                "meta_mensual": meta_mensual,
                "meta_anual": meta_anual,
                "ahorro_actual": ahorro_actual,
                "progreso_mensual": progreso_mensual,
                "progreso_anual": progreso_anual,
                "diferencia_mensual": ahorro_actual - meta_mensual,
                "diferencia_anual": ahorro_actual - meta_anual
            }
        except Exception as e:
            print(f"Error generando reporte de ahorro: {e}")
            return {}
    
    @staticmethod
    def generar_reporte_presupuesto() -> Dict[str, Any]:
        """Generar reporte de presupuesto"""
        try:
            # Obtener presupuesto
            presupuesto_data = firebase_get("presupuesto")
            if not presupuesto_data:
                return {}
            
            presupuesto_base = float(presupuesto_data.get("presupuesto_base", 0))
            gastos_recurrentes = float(presupuesto_data.get("gastos_recurrentes", 0))
            total_mensual = presupuesto_base + gastos_recurrentes
            
            # Obtener gastos del mes actual
            ahora = datetime.now()
            gastos_mes = MovimientoService.calcular_gastos_mes(ahora.month, ahora.year)
            
            # Calcular diferencia
            diferencia = total_mensual - gastos_mes
            porcentaje_usado = (gastos_mes / total_mensual * 100) if total_mensual > 0 else 0
            
            return {
                "presupuesto_base": presupuesto_base,
                "gastos_recurrentes": gastos_recurrentes,
                "total_mensual": total_mensual,
                "gastos_mes": gastos_mes,
                "diferencia": diferencia,
                "porcentaje_usado": porcentaje_usado,
                "esta_dentro_presupuesto": gastos_mes <= total_mensual
            }
        except Exception as e:
            print(f"Error generando reporte de presupuesto: {e}")
            return {}
