"""
Dashboard Nutricional
Página principal del módulo nutricional
"""

import streamlit as st
from datetime import date, datetime
import plotly.graph_objects as go
import plotly.express as px
from services.registro_nutricional_service import RegistroNutricionalService
from services.meta_calorica_service import MetaCaloricaService
from utils.helpers import apply_css_styles
from utils.config_manager import config_manager


def main():
    """Función principal del dashboard nutricional"""
    
    # Aplicar CSS personalizado
    apply_css_styles()
    
    # Navegación lateral personalizada
    from utils.helpers import mostrar_navegacion_lateral
    mostrar_navegacion_lateral()
    
    st.title("🥗 Dashboard Nutricional")
    
    # Obtener datos del día actual
    hoy = date.today()
    registro_hoy = RegistroNutricionalService.obtener_por_fecha(hoy)
    meta_actual = MetaCaloricaService.obtener_meta_actual()
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        calorias_consumidas = registro_hoy.total_calorias if registro_hoy else 0.0
        meta_calorias = meta_actual.calorias_objetivo if meta_actual else 2000.0
        st.metric(
            "🔥 Calorías Consumidas",
            f"{calorias_consumidas:.0f}",
            delta=f"Meta: {meta_calorias:.0f}" if meta_actual else None
        )
    
    with col2:
        deficit = meta_calorias - calorias_consumidas if meta_actual else 0.0
        st.metric(
            "📉 Déficit Calórico",
            f"{deficit:.0f}",
            delta="Restante" if deficit > 0 else "Excedido"
        )
    
    with col3:
        progreso = (calorias_consumidas / meta_calorias * 100) if meta_calorias > 0 else 0.0
        st.metric(
            "📊 Progreso del Día",
            f"{progreso:.1f}%",
            delta=f"Meta: {meta_calorias:.0f} cal"
        )
    
    st.divider()
    
    # Gráfico de progreso calórico (velocímetro)
    if meta_actual:
        st.subheader("🎯 Progreso Calórico del Día")
        progreso_porcentaje = min((calorias_consumidas / meta_calorias) * 100, 200.0)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progreso_porcentaje,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Progreso Calórico"},
            number={'valueformat': '.1f', 'suffix': '%'},
            gauge={
                'axis': {'range': [0, 200]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 75], 'color': "red"},
                    {'range': [75, 100], 'color': "orange"},
                    {'range': [100, 150], 'color': "lightgreen"},
                    {'range': [150, 200], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "green", 'width': 4},
                    'thickness': 0.75,
                    'value': 100
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Mensaje según progreso
        if progreso_porcentaje < 75:
            st.warning("⚠️ Estás por debajo de tu meta. Considera agregar más calorías.")
        elif progreso_porcentaje < 100:
            st.info("📈 Vas bien. Estás cerca de tu meta.")
        elif progreso_porcentaje < 150:
            st.success("✅ ¡Excelente! Has alcanzado tu meta.")
        else:
            st.warning("⚠️ Has excedido tu meta. Considera ajustar tu consumo.")
    
    st.divider()
    
    # Distribución de macronutrientes
    if registro_hoy:
        st.subheader("🥧 Distribución de Macronutrientes")
        
        proteinas = registro_hoy.total_proteinas
        carbohidratos = registro_hoy.total_carbohidratos
        grasas = registro_hoy.total_grasas
        
        if proteinas + carbohidratos + grasas > 0:
            fig = go.Figure(data=[
                go.Pie(
                    labels=["Proteínas", "Carbohidratos", "Grasas"],
                    values=[proteinas, carbohidratos, grasas],
                    textinfo='label+percent+value',
                    texttemplate='%{label}<br>%{percent}<br>%{value:.1f}g',
                    hovertemplate='<b>%{label}</b><br>Cantidad: %{value:.1f}g<br>Porcentaje: %{percent}<extra></extra>',
                    marker=dict(colors=['#FF6B6B', '#4ECDC4', '#FFE66D'])
                )
            ])
            fig.update_layout(
                title="Distribución de Macronutrientes del Día",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar valores
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🥩 Proteínas", f"{proteinas:.1f}g")
            with col2:
                st.metric("🍞 Carbohidratos", f"{carbohidratos:.1f}g")
            with col3:
                st.metric("🧈 Grasas", f"{grasas:.1f}g")
        else:
            st.info("No hay macronutrientes registrados para hoy")
    else:
        st.info("No hay registro de comidas para hoy. ¡Agrega tu primera comida!")


if __name__ == "__main__":
    main()

