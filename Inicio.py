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
        # Recuadro financiero visual con estructura original exacta (h2, h3, p)
        st.markdown("""
        <div id="recuadro_financiero" style="
            padding: 3rem 2rem;
            border-radius: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            margin: 1rem;
            cursor: pointer;
            text-align: center;
            color: white;
            position: relative;
            z-index: 1;
        " onmouseover="this.style.transform='translateY(-8px) scale(1.02)'; this.style.boxShadow='0 20px 50px rgba(102, 126, 234, 0.5)';" 
           onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 10px 30px rgba(102, 126, 234, 0.3)';">
            <h2 style="color: white; font-size: 3rem; margin-bottom: 1rem;">💰</h2>
            <h3 style="color: white; font-size: 1.8rem; margin-bottom: 0.5rem; font-weight: 700;">Dashboard Financiero</h3>
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin: 0;">Gestiona tus finanzas, movimientos y reportes</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón invisible detrás del recuadro para manejar el click
        btn_financiero = st.button("", key="btn_financiero", use_container_width=True, type="primary")
        
        # CSS para posicionar el botón invisible sobre el recuadro
        st.markdown("""
        <style>
        div[data-testid="column"]:nth-of-type(1) {
            position: relative !important;
        }
        
        div[data-testid="column"]:nth-of-type(1) .stButton:last-child {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            z-index: 10 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        div[data-testid="column"]:nth-of-type(1) .stButton:last-child > button {
            opacity: 0 !important;
            width: 100% !important;
            height: 100% !important;
            cursor: pointer !important;
            background: transparent !important;
            border: none !important;
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            min-height: 200px !important;
            color: transparent !important;
            box-shadow: none !important;
            outline: none !important;
        }
        
        div[data-testid="column"]:nth-of-type(1) .stButton:last-child > button:hover,
        div[data-testid="column"]:nth-of-type(1) .stButton:last-child > button:focus {
            opacity: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            outline: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    with col2:
        # Recuadro nutricional visual con estructura original exacta (h2, h3, p)
        st.markdown("""
        <div id="recuadro_nutricional" style="
            padding: 3rem 2rem;
            border-radius: 20px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            box-shadow: 0 10px 30px rgba(245, 87, 108, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            margin: 1rem;
            cursor: pointer;
            text-align: center;
            color: white;
            position: relative;
            z-index: 1;
        " onmouseover="this.style.transform='translateY(-8px) scale(1.02)'; this.style.boxShadow='0 20px 50px rgba(245, 87, 108, 0.5)';" 
           onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 10px 30px rgba(245, 87, 108, 0.3)';"> 
            <h2 style="color: white; font-size: 3rem; margin-bottom: 1rem;">🥗</h2>
            <h3 style="color: white; font-size: 1.8rem; margin-bottom: 0.5rem; font-weight: 700;">Dashboard Nutricional</h3>
            <p style="color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin: 0;">Registra comidas, calorías y metas nutricionales</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón invisible detrás del recuadro para manejar el click
        btn_nutricional = st.button("", key="btn_nutricional", use_container_width=True, type="primary")
    
    # CSS para posicionar el botón nutricional invisible sobre el recuadro
    st.markdown("""
    <style>
    div[data-testid="column"]:nth-of-type(2) {
        position: relative !important;
    }
    
    div[data-testid="column"]:nth-of-type(2) .stButton:last-child {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 10 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    div[data-testid="column"]:nth-of-type(2) .stButton:last-child > button {
        opacity: 0 !important;
        width: 100% !important;
        height: 100% !important;
        cursor: pointer !important;
        background: transparent !important;
        border: none !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        min-height: 200px !important;
        color: transparent !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    div[data-testid="column"]:nth-of-type(2) .stButton:last-child > button:hover,
    div[data-testid="column"]:nth-of-type(2) .stButton:last-child > button:focus {
        opacity: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        outline: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
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
