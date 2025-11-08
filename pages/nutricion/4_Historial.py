"""
Historial Nutricional
Página para ver historial de consumo calórico
"""

import streamlit as st
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from services.registro_nutricional_service import RegistroNutricionalService
from services.meta_calorica_service import MetaCaloricaService
from utils.helpers import apply_css_styles


def main():
    """Función principal de historial nutricional"""
    
    # Aplicar CSS personalizado
    apply_css_styles()
    
    # Establecer página actual nutricional
    st.session_state["pagina_nutricional_actual"] = "historial"
    
    # Navegación lateral personalizada
    from utils.helpers import mostrar_navegacion_lateral
    mostrar_navegacion_lateral()
    
    st.title("📊 Historial Nutricional")
    
    # Selector de rango de fechas
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_inicio = st.date_input(
            "📅 Fecha de Inicio",
            value=date.today() - timedelta(days=7)
        )
    
    with col2:
        fecha_fin = st.date_input(
            "📅 Fecha de Fin",
            value=date.today()
        )
    
    st.divider()
    
    # Obtener registros del rango
    registros = RegistroNutricionalService.obtener_por_rango(fecha_inicio, fecha_fin)
    meta_actual = MetaCaloricaService.obtener_meta_actual()
    
    if registros:
        # Gráfico de calorías consumidas por día
        st.subheader("🔥 Calorías Consumidas por Día")
        
        fechas = [r.fecha for r in registros]
        calorias = [r.total_calorias for r in registros]
        
        fig = go.Figure()
        
        # Línea de calorías consumidas
        fig.add_trace(go.Scatter(
            x=fechas,
            y=calorias,
            mode='lines+markers',
            name='Calorías Consumidas',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8)
        ))
        
        # Línea de meta calórica
        if meta_actual:
            meta_calorias = [meta_actual.calorias_objetivo] * len(fechas)
            fig.add_trace(go.Scatter(
                x=fechas,
                y=meta_calorias,
                mode='lines',
                name='Meta Calórica',
                line=dict(color='#4ECDC4', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title="Evolución de Calorías Consumidas",
            xaxis_title="Fecha",
            yaxis_title="Calorías",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Tabla de resumen
        st.subheader("📋 Resumen por Día")
        
        resumen_data = []
        for registro in registros:
            resumen_data.append({
                "Fecha": registro.fecha.strftime("%d/%m/%Y"),
                "Calorías": f"{registro.total_calorias:.0f}",
                "Proteínas (g)": f"{registro.total_proteinas:.1f}",
                "Carbohidratos (g)": f"{registro.total_carbohidratos:.1f}",
                "Grasas (g)": f"{registro.total_grasas:.1f}",
                "Progreso": f"{(registro.total_calorias / meta_actual.calorias_objetivo * 100) if meta_actual else 0:.1f}%"
            })
        
        st.dataframe(resumen_data, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Estadísticas del período
        st.subheader("📊 Estadísticas del Período")
        
        total_calorias = sum(r.total_calorias for r in registros)
        promedio_calorias = total_calorias / len(registros) if registros else 0
        total_proteinas = sum(r.total_proteinas for r in registros)
        total_carbohidratos = sum(r.total_carbohidratos for r in registros)
        total_grasas = sum(r.total_grasas for r in registros)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔥 Total Calorías", f"{total_calorias:.0f}")
            st.metric("📊 Promedio Diario", f"{promedio_calorias:.0f}")
        
        with col2:
            st.metric("🥩 Total Proteínas", f"{total_proteinas:.1f}g")
            st.metric("📊 Promedio Diario", f"{total_proteinas / len(registros):.1f}g" if registros else "0g")
        
        with col3:
            st.metric("🍞 Total Carbohidratos", f"{total_carbohidratos:.1f}g")
            st.metric("📊 Promedio Diario", f"{total_carbohidratos / len(registros):.1f}g" if registros else "0g")
        
        with col4:
            st.metric("🧈 Total Grasas", f"{total_grasas:.1f}g")
            st.metric("📊 Promedio Diario", f"{total_grasas / len(registros):.1f}g" if registros else "0g")
    else:
        st.info("No hay registros en el rango de fechas seleccionado")


if __name__ == "__main__":
    main()

