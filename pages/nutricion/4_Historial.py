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
from utils.week_helpers import get_week_start_end


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
    
    # Obtener todos los registros disponibles (últimas 12 semanas por defecto)
    fecha_fin = date.today()
    fecha_inicio = fecha_fin - timedelta(weeks=12)
    
    st.divider()
    
    # Obtener registros del rango
    registros = RegistroNutricionalService.obtener_por_rango(fecha_inicio, fecha_fin)
    meta_actual = MetaCaloricaService.obtener_meta_actual()
    
    if registros:
        # Agrupar por semana
        semanas_data = {}
        for registro in registros:
            inicio_semana, fin_semana = get_week_start_end(registro.fecha)
            semana_key = inicio_semana.strftime("%Y-%m-%d")
            
            if semana_key not in semanas_data:
                semanas_data[semana_key] = {
                    "fecha_inicio": inicio_semana,
                    "fecha_fin": fin_semana,
                    "calorias": 0.0,
                    "proteinas": 0.0,
                    "carbohidratos": 0.0,
                    "grasas": 0.0
                }
            
            semanas_data[semana_key]["calorias"] += registro.total_calorias
            semanas_data[semana_key]["proteinas"] += registro.total_proteinas
            semanas_data[semana_key]["carbohidratos"] += registro.total_carbohidratos
            semanas_data[semana_key]["grasas"] += registro.total_grasas
        
        # Ordenar semanas por fecha
        semanas_ordenadas = sorted(semanas_data.values(), key=lambda x: x["fecha_inicio"])
        
        # Gráfico de calorías consumidas por semana
        st.subheader("🔥 Calorías Consumidas por Semana")
        
        fechas_semana = [f"{s['fecha_inicio'].strftime('%d/%m')} - {s['fecha_fin'].strftime('%d/%m')}" for s in semanas_ordenadas]
        calorias_semanales = [s["calorias"] for s in semanas_ordenadas]
        
        fig = go.Figure()
        
        # Línea de calorías consumidas
        fig.add_trace(go.Scatter(
            x=fechas_semana,
            y=calorias_semanales,
            mode='lines+markers',
            name='Calorías Consumidas',
            line=dict(color='#FF6B6B', width=3),
            marker=dict(size=8)
        ))
        
        # Línea de meta calórica semanal
        if meta_actual:
            meta_calorias_semanal = meta_actual.calorias_objetivo_semanal
            fig.add_trace(go.Scatter(
                x=fechas_semana,
                y=[meta_calorias_semanal] * len(fechas_semana),
                mode='lines',
                name='Meta Calórica Semanal',
                line=dict(color='#4ECDC4', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title="Evolución de Calorías Consumidas (Semanal)",
            xaxis_title="Semana",
            yaxis_title="Calorías",
            height=400,
            hovermode='x unified',
            xaxis=dict(tickangle=-45)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Tabla de resumen semanal
        st.subheader("📋 Resumen por Semana")
        
        resumen_data = []
        for semana in semanas_ordenadas:
            progreso = (semana["calorias"] / meta_actual.calorias_objetivo_semanal * 100) if meta_actual else 0.0
            # Calcular déficit calórico alcanzado
            if meta_actual:
                deficit_alcanzado = meta_actual.calorias_objetivo_semanal - semana["calorias"]
            else:
                deficit_alcanzado = 0.0
            
            resumen_data.append({
                "Semana": f"{semana['fecha_inicio'].strftime('%d/%m')} - {semana['fecha_fin'].strftime('%d/%m')}",
                "Calorías Consumidas": f"{semana['calorias']:.0f}",
                "Déficit Calórico": f"{deficit_alcanzado:.0f}",
                "Proteínas (g)": f"{semana['proteinas']:.1f}",
                "Carbohidratos (g)": f"{semana['carbohidratos']:.1f}",
                "Grasas (g)": f"{semana['grasas']:.1f}",
                "Progreso": f"{progreso:.1f}%"
            })
        
        st.dataframe(resumen_data, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Estadísticas del período
        st.subheader("📊 Estadísticas del Período")
        
        total_calorias = sum(s["calorias"] for s in semanas_ordenadas)
        promedio_semanal = total_calorias / len(semanas_ordenadas) if semanas_ordenadas else 0
        total_proteinas = sum(s["proteinas"] for s in semanas_ordenadas)
        total_carbohidratos = sum(s["carbohidratos"] for s in semanas_ordenadas)
        total_grasas = sum(s["grasas"] for s in semanas_ordenadas)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔥 Total Calorías", f"{total_calorias:.0f}")
            st.metric("📊 Promedio Semanal", f"{promedio_semanal:.0f}")
        
        with col2:
            st.metric("🥩 Total Proteínas", f"{total_proteinas:.1f}g")
            st.metric("📊 Promedio Semanal", f"{total_proteinas / len(semanas_ordenadas):.1f}g" if semanas_ordenadas else "0g")
        
        with col3:
            st.metric("🍞 Total Carbohidratos", f"{total_carbohidratos:.1f}g")
            st.metric("📊 Promedio Semanal", f"{total_carbohidratos / len(semanas_ordenadas):.1f}g" if semanas_ordenadas else "0g")
        
        with col4:
            st.metric("🧈 Total Grasas", f"{total_grasas:.1f}g")
            st.metric("📊 Promedio Semanal", f"{total_grasas / len(semanas_ordenadas):.1f}g" if semanas_ordenadas else "0g")
    else:
        st.info("No hay registros en el rango de fechas seleccionado")


if __name__ == "__main__":
    main()

