"""
Dashboard Nutricional
Página principal del módulo nutricional
"""

import streamlit as st
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from services.registro_nutricional_service import RegistroNutricionalService
from services.meta_calorica_service import MetaCaloricaService
from utils.helpers import apply_css_styles
from utils.config_manager import config_manager
from utils.week_helpers import get_current_week, get_week_start_end


def main():
    """Función principal del dashboard nutricional"""
    
    # Aplicar CSS personalizado
    from utils.helpers import apply_css_styles
    apply_css_styles()
    
    # Navegación lateral personalizada
    from utils.helpers import mostrar_navegacion_lateral
    mostrar_navegacion_lateral()
    
    # Establecer página actual nutricional
    st.session_state["pagina_nutricional_actual"] = "dashboard"
    
    st.title("🥗 Dashboard Nutricional")
    st.markdown("Gestiona tu consumo calórico semanal y alcanza tus metas nutricionales")
    
    # Obtener rango de la semana actual (Lunes a Domingo)
    inicio_semana, fin_semana = get_current_week()
    
    # Verificar si hay datos nuevos y actualizar automáticamente
    if st.session_state.get("datos_nutricionales_actualizados", False):
        RegistroNutricionalService._obtener_por_fecha_cached.clear()
        st.session_state["datos_nutricionales_actualizados"] = False  # Resetear el flag
    
    # Obtener registros de la semana
    registros_semana = RegistroNutricionalService.obtener_por_rango(inicio_semana, fin_semana)
    
    # Obtener registro del día actual
    registro_hoy = RegistroNutricionalService.obtener_por_fecha(date.today())
    calorias_hoy = registro_hoy.total_calorias if registro_hoy else 0.0
    
    # Calcular totales semanales
    calorias_semanales = sum(r.total_calorias for r in registros_semana)
    proteinas_semanales = sum(r.total_proteinas for r in registros_semana)
    carbohidratos_semanales = sum(r.total_carbohidratos for r in registros_semana)
    grasas_semanales = sum(r.total_grasas for r in registros_semana)
    
    # Obtener meta semanal
    meta_actual = MetaCaloricaService.obtener_meta_actual()
    meta_calorias_semanal = meta_actual.calorias_objetivo_semanal if meta_actual else (2000.0 * 7)
    meta_calorias_diaria = meta_actual.calorias_objetivo if meta_actual else 2000.0
    
    # Métricas principales (semanal y diario)
    st.subheader("📊 Métricas Semanales")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "🔥 Calorías Consumidas (Semana)",
            f"{calorias_semanales:.0f}",
            delta=f"Meta: {meta_calorias_semanal:.0f} cal" if meta_actual else None
        )
    
    with col2:
        deficit_semanal = meta_calorias_semanal - calorias_semanales if meta_actual else 0.0
        st.metric(
            "📉 Déficit Calórico Semanal",
            f"{deficit_semanal:.0f}",
            delta="Restante" if deficit_semanal > 0 else "Excedido"
        )
    
    st.subheader("📊 Métricas Diarias")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "🔥 Calorías Consumidas (Hoy)",
            f"{calorias_hoy:.0f}",
            delta=f"Meta: {meta_calorias_diaria:.0f} cal" if meta_actual else None
        )
    
    with col2:
        deficit_diario = meta_calorias_diaria - calorias_hoy if meta_actual else 0.0
        st.metric(
            "📉 Déficit Calórico Diario",
            f"{deficit_diario:.0f}",
            delta="Restante" if deficit_diario > 0 else "Excedido"
        )
    
    st.divider()
    
    # Gráfico de progreso calórico semanal (velocímetro)
    if meta_actual:
        st.subheader("🎯 Progreso Calórico Semanal")
        progreso_porcentaje = min((calorias_semanales / meta_calorias_semanal) * 100, 200.0)
        
        # Determinar color de la barra según el porcentaje
        if progreso_porcentaje <= 100:
            color_bar = "#28a745"  # Verde más vibrante
        elif progreso_porcentaje <= 150:
            color_bar = "#ffc107"  # Amarillo/Ámbar
        else:
            color_bar = "#dc3545"  # Rojo más intenso
        
        # Configurar los rangos de colores (siempre mostrar los 3 rangos)
        color_steps = [
            {'range': [0, 100], 'color': "#28a745"},      # Verde: dentro de la meta
            {'range': [100, 150], 'color': "#ffc107"},    # Amarillo: exceso moderado
            {'range': [150, 200], 'color': "#dc3545"}     # Rojo: exceso significativo
        ]
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=progreso_porcentaje,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Progreso Calórico Semanal", 'font': {'size': 18}},
            number={'valueformat': '.1f', 'suffix': '%', 'font': {'size': 24}},
            delta={'reference': 100, 'position': "top", 'font': {'size': 16}},
            gauge={
                'axis': {'range': [None, 200], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': color_bar, 'thickness': 0.3},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': color_steps,
                'threshold': {
                    'line': {'color': "#28a745", 'width': 4},
                    'thickness': 0.75,
                    'value': 100
                }
            }
        ))
        fig.update_layout(
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Mensaje según progreso
        if progreso_porcentaje <= 100:
            st.success(f"✅ Excelente! Estás dentro de tu meta semanal ({progreso_porcentaje:.1f}%)")
        elif progreso_porcentaje <= 150:
            st.warning(f"⚠️ Has superado tu meta semanal ({progreso_porcentaje:.1f}%). Considera ajustar tu consumo.")
        else:
            st.error(f"❌ Has excedido significativamente tu meta semanal ({progreso_porcentaje:.1f}%). Considera ajustar tu consumo.")
    
    st.divider()
    
    # Tabla de consumo semanal
    st.subheader("📊 Consumo Semanal")
    
    if registros_semana:
        # Crear datos para la tabla
        datos_tabla = []
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        for i in range(7):
            fecha_dia = inicio_semana + timedelta(days=i)
            registro_dia = next((r for r in registros_semana if r.fecha == fecha_dia), None)
            
            datos_tabla.append({
                "Día": dias_semana[i],
                "Fecha": fecha_dia.strftime("%d/%m"),
                "Calorías": f"{registro_dia.total_calorias:.0f}" if registro_dia else "0",
                "Proteínas (g)": f"{registro_dia.total_proteinas:.1f}" if registro_dia else "0.0",
                "Carbohidratos (g)": f"{registro_dia.total_carbohidratos:.1f}" if registro_dia else "0.0",
                "Grasas (g)": f"{registro_dia.total_grasas:.1f}" if registro_dia else "0.0"
            })
        
        df = pd.DataFrame(datos_tabla)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Gráfico de barras de consumo diario
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[d["Día"] for d in datos_tabla],
            y=[float(d["Calorías"]) for d in datos_tabla],
            name="Calorías",
            marker_color='#FF6B6B'
        ))
        
        # Línea de meta diaria
        if meta_actual:
            meta_diaria = meta_actual.calorias_objetivo
            fig.add_trace(go.Scatter(
                x=[d["Día"] for d in datos_tabla],
                y=[meta_diaria] * 7,
                mode='lines',
                name='Meta Diaria',
                line=dict(color='#4ECDC4', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title="Calorías Consumidas por Día (Semana)",
            xaxis_title="Día",
            yaxis_title="Calorías",
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No hay registros para esta semana ({inicio_semana.strftime('%d/%m')} - {fin_semana.strftime('%d/%m')}). ¡Agrega tu primera comida!")
    
    st.divider()
    
    # Gráfica de progreso de peso
    from services.peso_service import PesoService
    registros_peso = PesoService.obtener_todos()
    
    if registros_peso:
        st.subheader("⚖️ Progreso de Peso")
        
        # Ordenar por fecha ascendente para la gráfica
        registros_peso_ordenados = sorted(registros_peso, key=lambda x: x.fecha)
        # Formatear fechas como strings para mostrar solo días (sin horas)
        fechas_peso_str = [r.fecha.strftime("%d/%m/%Y") for r in registros_peso_ordenados]
        pesos = [r.peso for r in registros_peso_ordenados]
        
        fig_peso = go.Figure()
        fig_peso.add_trace(go.Scatter(
            x=fechas_peso_str,
            y=pesos,
            mode='lines+markers',
            name='Peso',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8, color='#FF6B6B')
        ))
        
        fig_peso.update_layout(
            title="Evolución del Peso",
            xaxis_title="Fecha",
            yaxis_title="Peso (kg)",
            height=400,
            hovermode='x unified',
            xaxis=dict(
                type='category',  # Tratar como categorías para evitar timestamps
                tickangle=-45,  # Rotar etiquetas para mejor legibilidad
                tickmode='linear'
            )
        )
        st.plotly_chart(fig_peso, use_container_width=True)

