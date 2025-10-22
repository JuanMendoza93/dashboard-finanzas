"""
Reportes y Análisis Financiero
Página para visualizar reportes detallados
"""

import streamlit as st
from datetime import datetime, timedelta
from services.reporte_service import ReporteService
from services.movimiento_service import MovimientoService
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
    
    # Obtener datos de los últimos 12 meses
    ahora = datetime.now()
    meses_datos = []
    gastos_mensuales = []
    ingresos_mensuales = []
    ahorros_mensuales = []
    meses_labels = []
    
    for i in range(12):
        fecha_analisis = ahora - timedelta(days=30*i)
        mes = fecha_analisis.month
        año = fecha_analisis.year
        
        # Obtener movimientos del mes
        movimientos_mes = MovimientoService.obtener_por_mes(mes, año)
        
        gastos_mes = sum(abs(m.monto) for m in movimientos_mes if m.es_gasto)
        ingresos_mes = sum(m.monto for m in movimientos_mes if not m.es_gasto)
        ahorro_mes = ingresos_mes - gastos_mes
        
        meses_datos.append(fecha_analisis)
        gastos_mensuales.append(gastos_mes)
        ingresos_mensuales.append(ingresos_mes)
        ahorros_mensuales.append(ahorro_mes)
        meses_labels.append(f"{fecha_analisis.strftime('%b')} {año}")
    
    # Crear tabla de evaluación
    import pandas as pd
    
    df_evaluacion = pd.DataFrame({
        'Mes': meses_labels[::-1],
        'Gastos': [f"${g:,.2f}" for g in gastos_mensuales[::-1]],
        'Ingresos': [f"${i:,.2f}" for i in ingresos_mensuales[::-1]],
        'Ahorro': [f"${a:,.2f}" for a in ahorros_mensuales[::-1]],
        'Estado': ['✅ Positivo' if a > 0 else '❌ Negativo' for a in ahorros_mensuales[::-1]]
    })
    
    st.dataframe(df_evaluacion, use_container_width=True)
    
    st.divider()
    
    # Gráfica de evolución
    st.subheader("📈 Evolución Temporal")
    
    # Crear gráfica con colores diferentes
    fig = go.Figure()
    
    # Línea de gastos en rojo
    fig.add_trace(go.Scatter(
        x=meses_labels[::-1],  # Invertir para mostrar cronológicamente
        y=gastos_mensuales[::-1],
        mode='lines+markers',
        name='Gastos',
        line=dict(color='#DC143C', width=3),
        marker=dict(size=8, color='#DC143C')
    ))
    
    # Línea de ingresos en verde
    fig.add_trace(go.Scatter(
        x=meses_labels[::-1],
        y=ingresos_mensuales[::-1],
        mode='lines+markers',
        name='Ingresos',
        line=dict(color='#2E8B57', width=3),
        marker=dict(size=8, color='#2E8B57')
    ))
    
    # Línea de ahorro en azul
    fig.add_trace(go.Scatter(
        x=meses_labels[::-1],
        y=ahorros_mensuales[::-1],
        mode='lines+markers',
        name='Ahorro',
        line=dict(color='#4169E1', width=3),
        marker=dict(size=8, color='#4169E1')
    ))
    
    fig.update_layout(
        title="Evolución de Gastos, Ingresos y Ahorro por Mes",
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
        
        for mes in range(1, 13):
            movimientos_mes = MovimientoService.obtener_por_mes(mes, año_analisis)
            gastos_mes = sum(abs(m.monto) for m in movimientos_mes if m.es_gasto)
            ingresos_mes = sum(m.monto for m in movimientos_mes if not m.es_gasto)
            
            gastos_año += gastos_mes
            ingresos_año += ingresos_mes
        
        ahorro_año = ingresos_año - gastos_año
        
        años_datos.append(año_analisis)
        gastos_anuales.append(gastos_año)
        ingresos_anuales.append(ingresos_año)
        ahorros_anuales.append(ahorro_año)
        años_labels.append(str(año_analisis))
    
    # Crear tabla de evaluación anual
    import pandas as pd
    
    df_anual = pd.DataFrame({
        'Año': años_labels[::-1],
        'Gastos': [f"${g:,.2f}" for g in gastos_anuales[::-1]],
        'Ingresos': [f"${i:,.2f}" for i in ingresos_anuales[::-1]],
        'Ahorro': [f"${a:,.2f}" for a in ahorros_anuales[::-1]],
        'Estado': ['✅ Positivo' if a > 0 else '❌ Negativo' for a in ahorros_anuales[::-1]]
    })
    
    st.dataframe(df_anual, use_container_width=True)
    
    st.divider()
    
    # Gráfica de evolución anual
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
    
    # Línea de ahorro en azul
    fig.add_trace(go.Scatter(
        x=años_labels[::-1],
        y=ahorros_anuales[::-1],
        mode='lines+markers',
        name='Ahorro',
        line=dict(color='#4169E1', width=3),
        marker=dict(size=8, color='#4169E1')
    ))
    
    fig.update_layout(
        title="Evolución de Gastos, Ingresos y Ahorro por Año",
        xaxis_title="Año",
        yaxis_title="Monto ($)",
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()