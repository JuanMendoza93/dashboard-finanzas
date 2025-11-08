"""
Servicio para generación de reportes
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
import pandas as pd
import streamlit as st
from calendar import monthrange
from models.cuenta import Cuenta
from models.movimiento import Movimiento
from models.presupuesto import Presupuesto, MetaAhorro
from services.cuenta_service import CuentaService
from services.movimiento_service import MovimientoService
from utils.database import firebase_get, firebase_set
from utils.firebase_namespace import get_financial_path


class ReporteService:
    """Servicio para generación de reportes"""
    
    @staticmethod
    @st.cache_data(ttl=60, max_entries=5, show_spinner=False)
    def generar_resumen_financiero() -> Dict[str, Any]:
        """Generar resumen financiero completo (con caché de 60 segundos)"""
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
            
            # Calcular ahorro acumulado del año actual usando ahorro REAL mensual
            # El ahorro real es el incremento real del saldo de las cuentas mes a mes
            ahorro_acumulado_anual = 0
            año_actual = ahora.year
            
            # Obtener reportes mensuales para usar ahorro real guardado
            reportes_mensuales = ReporteService.obtener_reportes_mensuales()
            
            for mes in range(1, ahora.month + 1):
                # Primero intentar obtener el ahorro real del reporte guardado
                ahorro_real_mes = None
                for reporte in reportes_mensuales:
                    if reporte.get("mes") == mes and reporte.get("año") == año_actual:
                        ahorro_real_mes = reporte.get("ahorro_real", 0)
                        break
                
                # Si no hay reporte guardado, calcular el ahorro real del mes
                if ahorro_real_mes is None:
                    ahorro_real_mes = ReporteService.calcular_ahorro_real_mes(mes, año_actual)
                
                ahorro_acumulado_anual += ahorro_real_mes
            
            # Top gastos del mes actual (top 5)
            top_gastos = MovimientoService.obtener_top_gastos(5, ahora.month, ahora.year)
            
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
                "ahorro_acumulado_anual": ahorro_acumulado_anual,
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
            gastos = [m for m in movimientos if m.tipo == "Gasto"]
            ingresos = [m for m in movimientos if m.tipo == "Ingreso"]
            pagos = [m for m in movimientos if m.tipo == "Pago"]
            
            # Calcular totales según la lógica correcta:
            # Gastos: sumar todos los gastos y restar los pagos recibidos
            total_gastos = sum(m.monto_absoluto for m in gastos) - sum(m.monto for m in pagos)
            # Ingresos: solo los movimientos tipo "Ingreso"
            total_ingresos = sum(m.monto for m in ingresos)
            balance = total_ingresos - total_gastos
            
            # Gastos por categoría (solo gastos, sin incluir pagos)
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
            # Obtener metas usando la nueva estructura
            metas_data = firebase_get(get_financial_path("metas"))
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
    
    @staticmethod
    def calcular_ahorro_real_mes(mes: int, año: int) -> float:
        """Calcular el ahorro real (incremento del saldo total de cuentas) para un mes"""
        try:
            ahora = datetime.now()
            es_mes_actual = (año == ahora.year and mes == ahora.month)
            
            # Obtener reportes guardados
            reportes = ReporteService.obtener_reportes_mensuales()
            
            # Determinar el saldo final del mes
            saldo_final = None
            if es_mes_actual:
                # Para el mes actual, usar el saldo actual de las cuentas
                cuentas = CuentaService.obtener_todas()
                saldo_final = sum(cuenta.saldo for cuenta in cuentas)
            else:
                # Para meses pasados, primero calcular el saldo teórico basado en movimientos
                # para detectar si hay movimientos retroactivos
                mes_anterior_temp = mes - 1
                año_anterior_temp = año
                if mes_anterior_temp == 0:
                    mes_anterior_temp = 12
                    año_anterior_temp = año - 1
                
                saldo_anterior = None
                if reportes:
                    for reporte in reportes:
                        if reporte.get("mes") == mes_anterior_temp and reporte.get("año") == año_anterior_temp:
                            saldo_anterior = reporte.get("saldo_final_mes")
                            break
                
                # Calcular saldo final teórico basado en movimientos actuales
                saldo_final_calculado = None
                if saldo_anterior is not None:
                    movimientos_mes = MovimientoService.obtener_por_mes(mes, año)
                    
                    # Gastos: sumar todos los gastos y restar los pagos recibidos
                    gastos_mov = [m for m in movimientos_mes if m.tipo == "Gasto"]
                    pagos_recibidos = [m for m in movimientos_mes if m.tipo == "Pago"]
                    gastos_mes = sum(m.monto_absoluto for m in gastos_mov) - sum(m.monto for m in pagos_recibidos)
                    
                    # Ingresos: solo movimientos tipo "Ingreso"
                    ingresos_mov = [m for m in movimientos_mes if m.tipo == "Ingreso"]
                    ingresos_mes = sum(m.monto for m in ingresos_mov)
                    
                    ahorro_mes = ingresos_mes - gastos_mes
                    saldo_final_calculado = saldo_anterior + ahorro_mes
                
                # Buscar el saldo guardado en el reporte de ese mes
                saldo_final_guardado = None
                if reportes:
                    for reporte in reportes:
                        if reporte.get("mes") == mes and reporte.get("año") == año:
                            saldo_final_guardado = reporte.get("saldo_final_mes")
                            break
                
                # Decidir qué saldo usar:
                # PRIMERO buscar el saldo guardado (es el saldo REAL del mes, guardado al cierre)
                # Solo si no existe, usar el calculado teóricamente
                if saldo_final_guardado is not None:
                    # Usar el saldo guardado - este es el saldo REAL que existió al cierre del mes
                    saldo_final = saldo_final_guardado
                elif saldo_final_calculado is not None:
                    # Si no hay reporte guardado, usar el calculado teóricamente
                    saldo_final = saldo_final_calculado
                else:
                    # Último recurso: usar saldo actual (poco preciso para meses pasados)
                    cuentas = CuentaService.obtener_todas()
                    saldo_final = sum(cuenta.saldo for cuenta in cuentas)
            
            # Obtener el saldo inicial (saldo final del mes anterior)
            saldo_inicial = None
            
            # Si es el primer mes (Octubre 2025)
            if año == 2025 and mes == 10:
                if reportes:
                    # Buscar reporte de septiembre 2025
                    for reporte in reportes:
                        if reporte.get("mes") == 9 and reporte.get("año") == 2025:
                            saldo_inicial = reporte.get("saldo_final_mes")
                            break
                
                # Si no hay reporte de septiembre, usar el saldo base de septiembre 2025
                if saldo_inicial is None:
                    saldo_inicial = 112750.48
            else:
                # Calcular el mes anterior
                mes_anterior = mes - 1
                año_anterior = año
                if mes_anterior == 0:
                    mes_anterior = 12
                    año_anterior = año - 1
                
                # Obtener el saldo final del mes anterior desde los reportes guardados
                if reportes:
                    for reporte in reportes:
                        if reporte.get("mes") == mes_anterior and reporte.get("año") == año_anterior:
                            saldo_inicial = reporte.get("saldo_final_mes")
                            break
                
                # Si no encontramos reporte del mes anterior y el mes anterior es septiembre 2025, usar el saldo base
                if saldo_inicial is None and año_anterior == 2025 and mes_anterior == 9:
                    saldo_inicial = 112750.48
                elif saldo_inicial is None:
                    # Fallback: calcular aproximado a partir del saldo actual restando el ahorro calculado
                    movimientos_mes = MovimientoService.obtener_por_mes(mes, año)
                    
                    # Gastos: sumar todos los gastos y restar los pagos recibidos
                    gastos_mov = [m for m in movimientos_mes if m.tipo == "Gasto"]
                    pagos_recibidos = [m for m in movimientos_mes if m.tipo == "Pago"]
                    gastos_mes = sum(m.monto_absoluto for m in gastos_mov) - sum(m.monto for m in pagos_recibidos)
                    
                    # Ingresos: solo movimientos tipo "Ingreso"
                    ingresos_mov = [m for m in movimientos_mes if m.tipo == "Ingreso"]
                    ingresos_mes = sum(m.monto for m in ingresos_mov)
                    
                    ahorro_calculado = ingresos_mes - gastos_mes
                    saldo_inicial = saldo_final - ahorro_calculado if saldo_final else 0
            
            # Calcular ahorro real como diferencia entre saldo final e inicial
            if saldo_final is not None and saldo_inicial is not None:
                ahorro_real = saldo_final - saldo_inicial
                return ahorro_real
            else:
                return 0.0
        except Exception as e:
            print(f"Error calculando ahorro real: {e}")
            return 0.0
    
    @staticmethod
    @st.cache_data(ttl=300, max_entries=20, show_spinner=False)
    def obtener_reportes_mensuales() -> List[Dict[str, Any]]:
        """Obtener todos los reportes mensuales guardados"""
        try:
            # Usar get_financial_path para apuntar a la nueva estructura
            reportes_data = firebase_get(get_financial_path("reportes_mensuales"))
            if not reportes_data:
                return []
            
            # Si es un diccionario, convertirlo a lista
            if isinstance(reportes_data, dict):
                # Ordenar por año y mes
                reportes_list = []
                for key, value in reportes_data.items():
                    if isinstance(value, dict):
                        reportes_list.append(value)
                # Ordenar por año y mes
                reportes_list.sort(key=lambda x: (x.get("año", 0), x.get("mes", 0)))
                return reportes_list
            return reportes_data if isinstance(reportes_data, list) else []
        except Exception as e:
            print(f"Error obteniendo reportes mensuales: {e}")
            return []
    
    @staticmethod
    def guardar_reporte_mensual(mes: int, año: int, datos: Dict[str, Any]) -> bool:
        """Guardar un reporte mensual"""
        try:
            # Agregar información del mes y año
            datos["mes"] = mes
            datos["año"] = año
            datos["fecha_generacion"] = datetime.now().isoformat()
            
            # Guardar en Firebase con una clave única usando la nueva estructura
            clave = f"{año}_{mes:02d}"
            result = firebase_set(f"{get_financial_path('reportes_mensuales')}/{clave}", datos)
            if result:
                # Invalidar caché de reportes mensuales
                ReporteService.obtener_reportes_mensuales.clear()
            return result
        except Exception as e:
            print(f"Error guardando reporte mensual: {e}")
            return False
    
    @staticmethod
    def generar_reporte_mensual(mes: int, año: int) -> bool:
        """Generar o regenerar un reporte mensual para un mes específico"""
        try:
            # Obtener movimientos del mes
            movimientos = MovimientoService.obtener_por_mes(mes, año)
            
            # Calcular gastos: sumar todos los gastos y restar los pagos recibidos
            gastos_movimientos = [m for m in movimientos if m.tipo == "Gasto"]
            pagos_recibidos = [m for m in movimientos if m.tipo == "Pago"]
            gastos = sum(m.monto_absoluto for m in gastos_movimientos) - sum(m.monto for m in pagos_recibidos)
            
            # Calcular ingresos: solo movimientos tipo "Ingreso"
            ingresos_movimientos = [m for m in movimientos if m.tipo == "Ingreso"]
            ingresos = sum(m.monto for m in ingresos_movimientos)
            
            ahorro = ingresos - gastos
            
            # Obtener saldo total de cuentas
            cuentas = CuentaService.obtener_todas()
            saldo_final = sum(cuenta.saldo for cuenta in cuentas)
            
            # Calcular ahorro real
            ahorro_real = ReporteService.calcular_ahorro_real_mes(mes, año)
            
            # Guardar reporte
            datos_reporte = {
                "gastos": gastos,
                "ingresos": ingresos,
                "ahorro": ahorro,
                "ahorro_real": ahorro_real,
                "saldo_final_mes": saldo_final
            }
            
            return ReporteService.guardar_reporte_mensual(mes, año, datos_reporte)
        except Exception as e:
            print(f"Error generando reporte mensual: {e}")
            return False
    
    @staticmethod
    def verificar_y_generar_reporte_mensual():
        """Verificar si es el último día del mes y generar reporte si es necesario"""
        try:
            ahora = datetime.now()
            ultimo_dia = monthrange(ahora.year, ahora.month)[1]
            
            # Si es el último día del mes
            if ahora.day == ultimo_dia:
                # Verificar si ya se generó el reporte para este mes
                reportes = ReporteService.obtener_reportes_mensuales()
                
                reporte_existente = False
                if reportes:
                    for reporte in reportes:
                        if reporte.get("mes") == ahora.month and reporte.get("año") == ahora.year:
                            reporte_existente = True
                            break
                
                # Si no existe, generar y guardar el reporte
                if not reporte_existente:
                    return ReporteService.generar_reporte_mensual(ahora.month, ahora.year)
            return False
        except Exception as e:
            print(f"Error verificando reporte mensual: {e}")
            return False
