"""
Página para reportes y análisis
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from services.reporte_service import ReporteService
from services.movimiento_service import MovimientoService
from utils.database import cargar_configuracion
from utils.helpers import show_fullscreen_loading, hide_fullscreen_loading


def mostrar_reportes():
    """Mostrar página de reportes y análisis"""
    
    st.title("📊 Reportes y Análisis Financiero")
    
    # Sin loading que se atasca
    
    # Obtener datos
    resumen = ReporteService.generar_resumen_financiero()
    reporte_ahorro = ReporteService.generar_reporte_ahorro()
    
    # Mostrar métricas principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Saldo Total", f"${resumen.get('saldo_total', 0):,.2f}")
    with col2:
        st.metric("💸 Gastos del Mes", f"${resumen.get('gastos_mes', 0):,.2f}")
    with col3:
        st.metric("📈 Ingresos del Mes", f"${resumen.get('ingresos_mes', 0):,.2f}")
    with col4:
        st.metric("💎 Ahorro Actual", f"${resumen.get('ahorro_actual', 0):,.2f}")
    
    st.divider()
    
    # Tabs para diferentes reportes
    tab1, tab2, tab3 = st.tabs(["📊 Resumen", "🎯 Metas", "📈 Análisis"])
    
    with tab1:
        mostrar_resumen_general(resumen)
    
    with tab2:
        mostrar_reporte_metas(reporte_ahorro)
    
    with tab3:
        mostrar_analisis_detallado()


def mostrar_resumen_general(resumen):
    """Mostrar resumen general"""
    st.subheader("📊 Resumen General")
    
    # Gráfico de gastos por categoría
    gastos_por_categoria = resumen.get("gastos_por_categoria", {})
    if gastos_por_categoria:
        st.subheader("💸 Gastos por Categoría")
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(gastos_por_categoria.keys()),
                y=list(gastos_por_categoria.values()),
                marker_color='lightblue'
            )
        ])
        fig.update_layout(
            title="Gastos por Categoría",
            xaxis_title="Categoría",
            yaxis_title="Monto ($)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top gastos
    top_gastos = resumen.get("top_gastos", [])
    if top_gastos:
        st.subheader("🔥 TOP Categorías con Más Gastos")
        for i, gasto in enumerate(top_gastos, 1):
            if isinstance(gasto, dict):
                # Nuevo formato: categoría con total
                st.write(f"#{i} 🏷️ {gasto['categoria']} - ${gasto['total']:,.2f}")
            else:
                # Formato anterior: movimiento individual
                st.write(f"#{i} 💸 {gasto.concepto} - ${gasto.monto_absoluto:,.2f} ({gasto.categoria})")


def mostrar_reporte_presupuesto(reporte_presupuesto):
    """Mostrar reporte de presupuesto"""
    st.subheader("💰 Reporte de Presupuesto")
    
    if not reporte_presupuesto:
        st.info("ℹ️ No hay datos de presupuesto disponibles")
        return
    
    # Métricas del presupuesto
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💵 Presupuesto Base", f"${reporte_presupuesto.get('presupuesto_base', 0):,.2f}")
    with col2:
        st.metric("🔄 Gastos Recurrentes", f"${reporte_presupuesto.get('gastos_recurrentes', 0):,.2f}")
    with col3:
        st.metric("📊 Total Mensual", f"${reporte_presupuesto.get('total_mensual', 0):,.2f}")
    
    # Gráfico de presupuesto vs gastos
    presupuesto_total = reporte_presupuesto.get('total_mensual', 0)
    gastos_mes = reporte_presupuesto.get('gastos_mes', 0)
    
    if presupuesto_total > 0:
        fig = go.Figure(data=[
            go.Bar(
                x=['Presupuesto', 'Gastos'],
                y=[presupuesto_total, gastos_mes],
                marker_color=['lightgreen', 'lightcoral']
            )
        ])
        fig.update_layout(
            title="Presupuesto vs Gastos del Mes",
            yaxis_title="Monto ($)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Estado del presupuesto
        diferencia = reporte_presupuesto.get('diferencia', 0)
        porcentaje_usado = reporte_presupuesto.get('porcentaje_usado', 0)
        
        if diferencia >= 0:
            st.success(f"✅ Te quedan ${diferencia:,.2f} del presupuesto ({100-porcentaje_usado:.1f}% disponible)")
        else:
            st.error(f"❌ Has excedido el presupuesto por ${abs(diferencia):,.2f} ({porcentaje_usado:.1f}% usado)")


def mostrar_reporte_metas(reporte_ahorro):
    """Mostrar reporte de metas"""
    st.subheader("🎯 Reporte de Metas de Ahorro")
    
    if not reporte_ahorro:
        st.info("ℹ️ No hay datos de metas disponibles")
        return
    
    # Métricas de metas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Meta Mensual", f"${reporte_ahorro.get('meta_mensual', 0):,.2f}")
    with col2:
        st.metric("🎯 Meta Anual", f"${reporte_ahorro.get('meta_anual', 0):,.2f}")
    with col3:
        st.metric("💎 Ahorro Actual", f"${reporte_ahorro.get('ahorro_actual', 0):,.2f}")
    
    # Gráficos de progreso
    col1, col2 = st.columns(2)
    
    with col1:
        # Progreso mensual
        progreso_mensual = reporte_ahorro.get('progreso_mensual', 0)
        fig_mensual = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progreso_mensual * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Progreso Mensual (%)"},
            gauge={'axis': {'range': [None, 200]},
                   'bar': {'color': "darkgreen"},
                   'steps': [{'range': [0, 75], 'color': "red"},
                            {'range': [75, 100], 'color': "orange"},
                            {'range': [100, 150], 'color': "lightgreen"},
                            {'range': [150, 200], 'color': "green"}],
                   'threshold': {'line': {'color': "green", 'width': 4},
                               'thickness': 0.75, 'value': 100}}
        ))
        fig_mensual.update_layout(height=300)
        st.plotly_chart(fig_mensual, use_container_width=True)
    
    with col2:
        # Progreso anual
        progreso_anual = reporte_ahorro.get('progreso_anual', 0)
        fig_anual = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progreso_anual * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Progreso Anual (%)"},
            gauge={'axis': {'range': [None, 200]},
                   'bar': {'color': "darkgreen"},
                   'steps': [{'range': [0, 75], 'color': "red"},
                            {'range': [75, 100], 'color': "orange"},
                            {'range': [100, 150], 'color': "lightgreen"},
                            {'range': [150, 200], 'color': "green"}],
                   'threshold': {'line': {'color': "green", 'width': 4},
                               'thickness': 0.75, 'value': 100}}
        ))
        fig_anual.update_layout(height=300)
        st.plotly_chart(fig_anual, use_container_width=True)
    
    # Estado de las metas
    diferencia_mensual = reporte_ahorro.get('diferencia_mensual', 0)
    diferencia_anual = reporte_ahorro.get('diferencia_anual', 0)
    
    if diferencia_mensual >= 0:
        st.success(f"✅ Meta mensual cumplida! Te sobraron ${diferencia_mensual:,.2f}")
    else:
        st.warning(f"⚠️ Te faltan ${abs(diferencia_mensual):,.2f} para cumplir la meta mensual")
    
    if diferencia_anual >= 0:
        st.success(f"✅ Meta anual cumplida! Te sobraron ${diferencia_anual:,.2f}")
    else:
        st.warning(f"⚠️ Te faltan ${abs(diferencia_anual):,.2f} para cumplir la meta anual")


def mostrar_analisis_detallado():
    """Mostrar análisis detallado"""
    st.subheader("📈 Análisis Detallado")
    
    # Obtener movimientos del mes actual
    ahora = datetime.now()
    movimientos = MovimientoService.obtener_por_mes(ahora.month, ahora.year)
    
    if not movimientos:
        st.info("ℹ️ No hay movimientos para analizar")
        return
    
    # Crear DataFrame para análisis
    import pandas as pd
    
    df_data = []
    for movimiento in movimientos:
        df_data.append({
            "Fecha": movimiento.fecha,
            "Concepto": movimiento.concepto,
            "Categoría": movimiento.categoria,
            "Tipo": movimiento.tipo,
            "Monto": movimiento.monto,
            "Tipo de Gasto": movimiento.tipo_gasto
        })
    
    df = pd.DataFrame(df_data)
    
    # Análisis por categoría
    st.subheader("📊 Análisis por Categoría")
    gastos_por_categoria = df[df['Tipo'] == 'Gasto'].groupby('Categoría')['Monto'].sum().abs()
    
    if not gastos_por_categoria.empty:
        fig = px.pie(
            values=gastos_por_categoria.values,
            names=gastos_por_categoria.index,
            title="Distribución de Gastos por Categoría"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Análisis temporal por mes
    st.subheader("📅 Análisis Temporal por Mes")
    
    # Obtener datos de los últimos 12 meses
    from datetime import timedelta
    
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
        ahorro_mes = ingresos_mes - gastos_mes  # Ahorro = Ingresos - Gastos
        
        meses_datos.append(fecha_analisis)
        gastos_mensuales.append(gastos_mes)
        ingresos_mensuales.append(ingresos_mes)
        ahorros_mensuales.append(ahorro_mes)
        meses_labels.append(f"{fecha_analisis.strftime('%b')} {año}")
    
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
