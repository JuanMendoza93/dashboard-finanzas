"""
Funciones auxiliares para evitar repetición de código
"""

import streamlit as st
from typing import Any, Dict, List, Optional
from datetime import datetime, date


def mostrar_navegacion_lateral():
    """Mostrar navegación lateral personalizada"""
    st.sidebar.markdown("### 🧭 Navegación")
    
    # Botones de navegación principales
    if st.sidebar.button("🏠 Dashboard", use_container_width=True, type="primary"):
        navegar_a_pagina("app.py")
    
    if st.sidebar.button("🏦 Cuentas", use_container_width=True):
        navegar_a_pagina("pages/1_Cuentas.py")
    
    if st.sidebar.button("💰 Movimientos", use_container_width=True):
        navegar_a_pagina("pages/2_Movimientos.py")
    
    if st.sidebar.button("📊 Reportes", use_container_width=True):
        navegar_a_pagina("pages/3_Reportes.py")
    
    if st.sidebar.button("💳 Gastos Recurrentes", use_container_width=True):
        navegar_a_pagina("pages/4_Gastos_Recurrentes.py")
    
    if st.sidebar.button("🎯 Metas", use_container_width=True):
        navegar_a_pagina("pages/5_Metas.py")
    
    if st.sidebar.button("⚙️ Configuración", use_container_width=True):
        navegar_a_pagina("pages/6_Configuracion.py")


def navegar_a_pagina(pagina: str):
    """Navegar a una página específica"""
    try:
        st.switch_page(pagina)
    except AttributeError:
        # Si st.switch_page no está disponible, usar redirección directa
        if pagina == "app.py":
            url = "/"
        else:
            nombre_pagina = pagina.replace("pages/", "").replace(".py", "")
            url = f"/{nombre_pagina}"
        
        st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)


def get_css_styles() -> str:
    """Obtener estilos CSS reutilizables"""
    return """
    <style>
    /* Solo ocultar la sección superior específica (input y lista) */
    [data-testid="stSidebar"] > div:first-child > div:first-child {
        display: none !important;
    }
    
    /* Ocultar solo el input "app new" */
    [data-testid="stSidebar"] input[placeholder*="app"] {
        display: none !important;
    }
    
    /* Ocultar solo la lista de navegación automática */
    [data-testid="stSidebar"] > div:first-child > div:nth-child(2) {
        display: none !important;
    }
    
    /* Estilos para botones internos (no sidebar) */
    .stButton > button {
        background: #242424 !important;
        color: white !important;
        border: 1px solid #404040 !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: #404040 !important;
        border-color: #606060 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
        background: #1a1a1a !important;
    }
    .stButton > button:focus {
        box-shadow: 0 0 0 2px rgba(36, 36, 36, 0.5) !important;
    }
    
    /* Sobrescribir estilos del sidebar */
    .sidebar .stButton > button {
        background: linear-gradient(90deg, #00d4aa 0%, #00b894 100%) !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0, 212, 170, 0.3) !important;
    }
    .sidebar .stButton > button:hover {
        background: linear-gradient(90deg, #00c19a 0%, #00a085 100%) !important;
        box-shadow: 0 4px 8px rgba(0, 212, 170, 0.4) !important;
    }
    .sidebar .stButton > button:focus {
        box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.5) !important;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.375rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.375rem;
        border: 1px solid #f5c6cb;
    }
    .warning-message {
        background: #fff3cd;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.375rem;
        border: 1px solid #ffeaa7;
    }
    .info-message {
        background: #d1ecf1;
        color: #0c5460;
        padding: 0.75rem;
        border-radius: 0.375rem;
        border: 1px solid #bee5eb;
    }
    
    /* Fix para scroll en móviles - selectores y dropdown */
    div[data-baseweb="select"] {
        overflow: visible !important;
    }
    div[data-baseweb="popover"] {
        overflow: auto !important;
        max-height: 300px !important;
        -webkit-overflow-scrolling: touch !important;
    }
    div[data-baseweb="menu"] {
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        overscroll-behavior: contain !important;
    }
    
    /* Fix para radio buttons y otros controles en móviles */
    @media screen and (max-width: 768px) {
        div[data-baseweb="select"] {
            touch-action: pan-y !important;
        }
        div[role="listbox"] {
            -webkit-overflow-scrolling: touch !important;
            overscroll-behavior: contain !important;
        }
    }
    </style>
    """


def apply_css_styles():
    """Aplicar estilos CSS al dashboard"""
    st.markdown(get_css_styles(), unsafe_allow_html=True)


def show_success_message(message: str):
    """Mostrar mensaje de éxito"""
    st.markdown(f"""
    <div class="success-message">
        ✅ {message}
    </div>
    """, unsafe_allow_html=True)


def show_error_message(message: str):
    """Mostrar mensaje de error"""
    st.markdown(f"""
    <div class="error-message">
        ❌ {message}
    </div>
    """, unsafe_allow_html=True)


def show_warning_message(message: str):
    """Mostrar mensaje de advertencia"""
    st.markdown(f"""
    <div class="warning-message">
        ⚠️ {message}
    </div>
    """, unsafe_allow_html=True)


def show_info_message(message: str):
    """Mostrar mensaje informativo"""
    st.markdown(f"""
    <div class="info-message">
        ℹ️ {message}
    </div>
    """, unsafe_allow_html=True)


def show_fullscreen_loading(message: str = "Cargando..."):
    """Mostrar loading de pantalla completa que bloquea interacciones"""
    with st.spinner(message):
        st.markdown(f"""
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            flex-direction: column;
        ">
            <div style="
                background: white;
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 1px solid #e0e0e0;
            ">
                <div style="
                    width: 50px;
                    height: 50px;
                    border: 5px solid #f3f3f3;
                    border-top: 5px solid #3498db;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 1.5rem;
                "></div>
                <p style="margin: 0; font-size: 1.2rem; color: #333; font-weight: 500;">{message}</p>
                <p style="margin: 0.5rem 0 0; font-size: 0.9rem; color: #666;">Por favor espera...</p>
            </div>
        </div>
        
        <style>
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
        """, unsafe_allow_html=True)


def hide_fullscreen_loading():
    """Ocultar loading de pantalla completa"""
    pass
