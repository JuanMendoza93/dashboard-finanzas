"""
Página de Inicio
Selector principal para elegir entre Dashboard Financiero y Nutricional
"""

import streamlit as st
from utils.helpers import apply_css_styles


def main():
    """Función principal de la página de inicio"""
    
    # Configuración de la página
    st.set_page_config(
        page_title="Dashboard Personal",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Ocultar sidebar por defecto en la página de inicio
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Aplicar CSS personalizado DESPUÉS para que no sobrescriba nuestros estilos
    apply_css_styles()
    
    # Título principal con fondo (más arriba)
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #A8D8EA 0%, #B0E0E6 100%);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 24px rgba(168, 216, 234, 0.3);
        text-align: center;
    ">
        <h1 style="
            font-size: 3.5rem;
            font-weight: 700;
            color: #1e1e1e;
            margin-bottom: 0.5rem;
            text-align: center;
        ">🏠 Dashboard Personal</h1>
        <p style="
            font-size: 1.5rem;
            color: #2d2d2d;
            margin: 0;
            text-align: center;
        ">Gestiona tus finanzas y nutrición en un solo lugar</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botones de selección de dashboard - Recuadros grandes clickeables
    col1, col2 = st.columns(2)
    
    with col1:
        btn_financiero = st.button("💰\n\nDashboard Financiero\n\nGestiona tus finanzas, movimientos y reportes", 
                                   key="btn_financiero", use_container_width=True, type="primary")
    
    with col2:
        btn_nutricional = st.button("🥗\n\nDashboard Nutricional\n\nRegistra comidas, calorías y metas nutricionales", 
                                    key="btn_nutricional", use_container_width=True, type="primary")
    
    
    if btn_financiero:
        st.session_state["dashboard_actual"] = "financiero"
        st.session_state["mostrar_dashboard"] = "financiero"
        st.rerun()
    
    if btn_nutricional:
        st.session_state["dashboard_actual"] = "nutricional"
        st.session_state["mostrar_dashboard"] = "nutricional"
        st.rerun()
    
    # Información adicional (más abajo)
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #666;">
        <p style="font-size: 1.1rem; margin-bottom: 1rem;">
            <strong>✨ Características principales:</strong>
        </p>
        <div style="display: flex; justify-content: center; gap: 3rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px;">
                <h4 style="color: #667eea;">💰 Financiero</h4>
                <ul style="text-align: left; list-style: none; padding: 0;">
                    <li>📊 Reportes y análisis</li>
                    <li>💳 Gestión de cuentas</li>
                    <li>📈 Seguimiento de gastos</li>
                    <li>🎯 Metas de ahorro</li>
                </ul>
            </div>
            <div style="flex: 1; min-width: 200px;">
                <h4 style="color: #f5576c;">🥗 Nutricional</h4>
                <ul style="text-align: left; list-style: none; padding: 0;">
                    <li>🍽️ Registro de comidas</li>
                    <li>🔥 Seguimiento calórico</li>
                    <li>📊 Análisis nutricional</li>
                    <li>🎯 Metas calóricas</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
