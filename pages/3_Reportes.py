"""
Reportes y Análisis Financiero
Página para visualizar reportes detallados
"""

import streamlit as st
from datetime import datetime, timedelta
from services.reporte_service import ReporteService
from services.movimiento_service import MovimientoService
from services.cuenta_service import CuentaService
from utils.config_manager import config_manager
from utils.helpers import apply_css_styles
import plotly.graph_objects as go
import plotly.express as px


def main():
    """Función principal de la página de reportes"""
    
    # Aplicar CSS personalizado
    apply_css_styles()
    
    # Navegación lateral personalizada
    from utils.helpers import mostrar_navegacion_lateral
    mostrar_navegacion_lateral()
    
    st.title("📊 Reportes y Análisis")
    
    # Obtener datos
    resumen = ReporteService.generar_resumen_financiero()
    reporte_ahorro = ReporteService.generar_reporte_ahorro()
    
    # Tabs para diferentes reportes
    tab1, tab2 = st.tabs(["📈 Análisis Mensual", "📊 Análisis Anual"])
    
    with tab1:
        mostrar_analisis_detallado()
    
    with tab2:
        mostrar_analisis_anual()




def mostrar_analisis_detallado():
    """Mostrar análisis temporal detallado"""
    
    st.subheader("📈 Análisis por Mes")
    
    # Verificar y generar reporte mensual si es necesario (último día del mes)
    ReporteService.verificar_y_generar_reporte_mensual()
    
    # Botón para regenerar reporte del mes actual
    ahora = datetime.now()
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Regenerar Reporte del Mes Actual", use_container_width=True, help="Actualiza el reporte del mes actual con los datos más recientes (útil si actualizaste saldos o movimientos)"):
            if ReporteService.generar_reporte_mensual(ahora.month, ahora.year):
                st.success(f"✅ Reporte de {ahora.strftime('%B %Y')} regenerado correctamente")
                st.rerun()
            else:
                st.error("❌ Error al regenerar el reporte")
    
    # Obtener datos desde Octubre 2025 hasta el mes actual
    ahora = datetime.now()
    año_inicio = 2025
    mes_inicio = 10  # Octubre
    
    meses_datos = []
    gastos_mensuales = []
    ingresos_mensuales = []
    ahorros_mensuales = []
    ahorros_reales = []
    saldos_mensuales = []
    meses_labels = []
    
    # Calcular desde Octubre 2025 hasta el mes actual
    año_actual = ahora.year
    mes_actual = ahora.month
    
    # Obtener saldo inicial (saldo total de cuentas al inicio del primer mes)
    saldo_inicial = 0
    if año_inicio == 2025 and mes_inicio == 10:
        # Para el primer mes, obtener el saldo guardado en reportes o calcular desde cuentas
        reportes = ReporteService.obtener_reportes_mensuales()
        if reportes and len(reportes) > 0:
            # Buscar el reporte más antiguo para obtener el saldo inicial
            primer_reporte = min(reportes, key=lambda x: (x.get("año", 0), x.get("mes", 0)))
            if primer_reporte and "saldo_final_mes" in primer_reporte:
                saldo_inicial = primer_reporte["saldo_final_mes"] - primer_reporte.get("ahorro_real", 0)
    
    # Crear diccionario de reportes para acceso rápido por año-mes
    reportes_guardados = ReporteService.obtener_reportes_mensuales()
    reportes_dict = {}
    if reportes_guardados and len(reportes_guardados) > 0:
        for reporte in reportes_guardados:
            año_reporte = reporte.get("año")
            mes_reporte = reporte.get("mes")
            if año_reporte and mes_reporte:
                reportes_dict[(año_reporte, mes_reporte)] = reporte
    
    for año in range(año_inicio, año_actual + 1):
        mes_start = mes_inicio if año == año_inicio else 1
        mes_end = mes_actual if año == año_actual else 12
        
        for mes in range(mes_start, mes_end + 1):
            # Obtener movimientos del mes
            movimientos_mes = MovimientoService.obtener_por_mes(mes, año)
            
            # Gastos: sumar todos los gastos y restar los pagos recibidos
            gastos_mov = [m for m in movimientos_mes if m.tipo == "Gasto"]
            pagos_recibidos = [m for m in movimientos_mes if m.tipo == "Pago"]
            gastos_mes = sum(m.monto_absoluto for m in gastos_mov) - sum(m.monto for m in pagos_recibidos)
            
            # Ingresos: solo movimientos tipo "Ingreso"
            ingresos_mov = [m for m in movimientos_mes if m.tipo == "Ingreso"]
            ingresos_mes = sum(m.monto for m in ingresos_mov)
            
            ahorro_mes = ingresos_mes - gastos_mes
            
            # Calcular ahorro real
            ahorro_real = ReporteService.calcular_ahorro_real_mes(mes, año)
            
            # Obtener saldo total guardado del reporte mensual (saldo total de cuentas al final del mes)
            # Si existe un reporte guardado para este mes, usarlo; si no, calcular desde el saldo actual
            saldo_final_mes = None
            if (año, mes) in reportes_dict:
                reporte_mes = reportes_dict[(año, mes)]
                saldo_final_mes = reporte_mes.get("saldo_final_mes")
            
            # Si no hay reporte guardado para este mes, usar el saldo actual de las cuentas
            if saldo_final_mes is None:
                cuentas = CuentaService.obtener_todas()
                saldo_final_mes = sum(cuenta.saldo for cuenta in cuentas)
            
            fecha_mes = datetime(año, mes, 1)
            meses_datos.append(fecha_mes)
            gastos_mensuales.append(gastos_mes)
            ingresos_mensuales.append(ingresos_mes)
            ahorros_mensuales.append(ahorro_mes)
            ahorros_reales.append(ahorro_real)
            saldos_mensuales.append(saldo_final_mes)
            
            nombres_meses = [
                "Ene", "Feb", "Mar", "Abr", "May", "Jun",
                "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
            ]
            meses_labels.append(f"{nombres_meses[mes-1]} {año}")
    
    # Tabla de evaluación dentro de un expander (colapsada, arriba de la gráfica)
    with st.expander(f"📊 Ver Tabla de Análisis Mensual ({len(meses_labels)} meses)", expanded=False):
        import pandas as pd
        
        # Crear DataFrame con los datos
        df_data = {
            'Mes': meses_labels,
            'Gastos': [f"${g:,.2f}" for g in gastos_mensuales],
            'Ingresos': [f"${i:,.2f}" for i in ingresos_mensuales],
            'Ahorro': [f"${a:,.2f}" for a in ahorros_mensuales],
            'Ahorro Real': ahorros_reales,
            'Saldo': saldos_mensuales
        }
        df_evaluacion = pd.DataFrame(df_data)
        
        # Aplicar estilos de color al ahorro real
        def color_ahorro_real(val):
            if val > 0:
                return 'background-color: #90EE90; color: #006400; font-weight: bold'
            elif val < 0:
                return 'background-color: #FFB6C1; color: #8B0000; font-weight: bold'
            else:
                return 'background-color: #F0F0F0; color: #666666'
        
        # Crear DataFrame styled para aplicar colores y formatear
        styled_df = df_evaluacion.style.applymap(color_ahorro_real, subset=['Ahorro Real'])
        styled_df = styled_df.format({
            'Ahorro Real': '${:,.2f}',
            'Saldo': '${:,.2f}'
        })
        
        # Mostrar DataFrame sin índice
        st.dataframe(styled_df, use_container_width=True, height=400, hide_index=True)
    
    st.divider()
    
    # Gráfica de evolución (después de la tabla)
    st.subheader("📈 Evolución Temporal")
    
    # Crear gráfica con colores diferentes
    fig = go.Figure()
    
    # Línea de gastos en rojo
    fig.add_trace(go.Scatter(
        x=meses_labels,
        y=gastos_mensuales,
        mode='lines+markers',
        name='Gastos',
        line=dict(color='#DC143C', width=3),
        marker=dict(size=8, color='#DC143C')
    ))
    
    # Línea de ingresos en verde
    fig.add_trace(go.Scatter(
        x=meses_labels,
        y=ingresos_mensuales,
        mode='lines+markers',
        name='Ingresos',
        line=dict(color='#2E8B57', width=3),
        marker=dict(size=8, color='#2E8B57')
    ))
    
    # Línea de ahorro en azul
    fig.add_trace(go.Scatter(
        x=meses_labels,
        y=ahorros_mensuales,
        mode='lines+markers',
        name='Ahorro',
        line=dict(color='#4169E1', width=3),
        marker=dict(size=8, color='#4169E1')
    ))
    
    # Línea de ahorro real en naranja/dorado
    fig.add_trace(go.Scatter(
        x=meses_labels,
        y=ahorros_reales,
        mode='lines+markers',
        name='Ahorro Real',
        line=dict(color='#FF8C00', width=3),
        marker=dict(size=8, color='#FF8C00')
    ))
    
    fig.update_layout(
        title="Evolución de Gastos, Ingresos, Ahorro y Ahorro Real por Mes",
        xaxis_title="Mes",
        yaxis_title="Monto ($)",
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def mostrar_analisis_anual():
    """Mostrar análisis anual de finanzas"""
    
    st.subheader("📊 Análisis Anual")
    
    # Obtener datos desde 2025 hasta el año actual
    ahora = datetime.now()
    año_actual = ahora.year
    año_inicio = 2025
    años_datos = []
    gastos_anuales = []
    ingresos_anuales = []
    ahorros_anuales = []
    años_labels = []
    
    # Calcular años a analizar (desde 2025 hasta el año actual)
    años_a_analizar = list(range(año_inicio, año_actual + 1))
    
    for año_analisis in años_a_analizar:
        
        # Obtener todos los movimientos del año
        gastos_año = 0
        ingresos_año = 0
        ahorro_real_año = 0
        
        # Obtener reportes mensuales del año para calcular ahorro real
        reportes_anuales = ReporteService.obtener_reportes_mensuales()
        reportes_del_año = [r for r in reportes_anuales if r.get("año") == año_analisis]
        
        for mes in range(1, 13):
            movimientos_mes = MovimientoService.obtener_por_mes(mes, año_analisis)
            
            # Gastos: sumar todos los gastos y restar los pagos recibidos
            gastos_mov = [m for m in movimientos_mes if m.tipo == "Gasto"]
            pagos_recibidos = [m for m in movimientos_mes if m.tipo == "Pago"]
            gastos_mes = sum(m.monto_absoluto for m in gastos_mov) - sum(m.monto for m in pagos_recibidos)
            
            # Ingresos: solo movimientos tipo "Ingreso"
            ingresos_mov = [m for m in movimientos_mes if m.tipo == "Ingreso"]
            ingresos_mes = sum(m.monto for m in ingresos_mov)
            
            gastos_año += gastos_mes
            ingresos_año += ingresos_mes
            
            # Obtener ahorro real del mes desde reportes o calcular
            ahorro_real_mes = 0
            reporte_mes = next((r for r in reportes_del_año if r.get("mes") == mes), None)
            if reporte_mes and "ahorro_real" in reporte_mes:
                ahorro_real_mes = reporte_mes.get("ahorro_real", 0)
            else:
                # Si no hay reporte, calcular el ahorro real del mes
                ahorro_real_mes = ReporteService.calcular_ahorro_real_mes(mes, año_analisis)
            
            ahorro_real_año += ahorro_real_mes
        
        años_datos.append(año_analisis)
        gastos_anuales.append(gastos_año)
        ingresos_anuales.append(ingresos_año)
        ahorros_anuales.append(ahorro_real_año)  # Usar ahorro real en lugar de calculado
        años_labels.append(str(año_analisis))
    
    # Tabla de evaluación anual dentro de un expander (colapsada, arriba de la gráfica)
    with st.expander(f"📊 Ver Tabla de Análisis Anual ({len(años_labels)} años)", expanded=False):
        import pandas as pd
        
        df_anual = pd.DataFrame({
            'Año': años_labels[::-1],
            'Gastos': [f"${g:,.2f}" for g in gastos_anuales[::-1]],
            'Ingresos': [f"${i:,.2f}" for i in ingresos_anuales[::-1]],
            'Ahorro Real': ahorros_anuales[::-1]
        })
        
        # Aplicar estilos de color al ahorro real
        def color_ahorro_real_anual(val):
            if val > 0:
                return 'background-color: #90EE90; color: #006400; font-weight: bold'
            elif val < 0:
                return 'background-color: #FFB6C1; color: #8B0000; font-weight: bold'
            else:
                return 'background-color: #F0F0F0; color: #666666'
        
        styled_df_anual = df_anual.style.applymap(color_ahorro_real_anual, subset=['Ahorro Real'])
        styled_df_anual = styled_df_anual.format({'Ahorro Real': '${:,.2f}'})
        
        st.dataframe(styled_df_anual, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Gráfica de evolución anual (después de la tabla)
    st.subheader("📈 Evolución Anual")
    
    fig = go.Figure()
    
    # Línea de gastos en rojo
    fig.add_trace(go.Scatter(
        x=años_labels[::-1],
        y=gastos_anuales[::-1],
        mode='lines+markers',
        name='Gastos',
        line=dict(color='#DC143C', width=3),
        marker=dict(size=8, color='#DC143C')
    ))
    
    # Línea de ingresos en verde
    fig.add_trace(go.Scatter(
        x=años_labels[::-1],
        y=ingresos_anuales[::-1],
        mode='lines+markers',
        name='Ingresos',
        line=dict(color='#2E8B57', width=3),
        marker=dict(size=8, color='#2E8B57')
    ))
    
    # Línea de ahorro real en azul
    fig.add_trace(go.Scatter(
        x=años_labels[::-1],
        y=ahorros_anuales[::-1],
        mode='lines+markers',
        name='Ahorro Real',
        line=dict(color='#4169E1', width=3),
        marker=dict(size=8, color='#4169E1')
    ))
    
    fig.update_layout(
        title="Evolución de Gastos, Ingresos y Ahorro Real por Año",
        xaxis_title="Año",
        yaxis_title="Monto ($)",
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()