"""
Funciones auxiliares para evitar repetición de código
"""

import streamlit as st
from typing import Any, Dict, List, Optional
from datetime import datetime, date


def mostrar_navegacion_lateral():
    """Mostrar navegación lateral personalizada"""
    st.sidebar.markdown("### 🧭 Navegación")
    
    # Obtener la página actual para resaltar el botón correspondiente
    pagina_actual = st.query_params.get("page", "app.py")
    
    
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
    """Navegar a una página específica usando st.switch_page (disponible en 1.50.0+)"""
    try:
        # Usar st.switch_page que ahora está disponible en la versión 1.50.0
        st.switch_page(pagina)
    except Exception as e:
        # Si falla, mostrar error y sugerir navegación manual
        st.error(f"Error de navegación: {str(e)}")
        st.info(f"Por favor, navega manualmente a: {pagina}")
        st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0;">
            <a href="{pagina}" target="_self" style="
                display: inline-block;
                padding: 0.5rem 1rem;
                background-color: #ff4b4b;
                color: white;
                text-decoration: none;
                border-radius: 0.5rem;
                font-weight: bold;
            ">Ir a {pagina}</a>
        </div>
        """, unsafe_allow_html=True)


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


def handle_database_error(error: Exception, operation: str) -> None:
    """Manejar errores de base de datos de forma consistente"""
    error_message = f"Error en {operation}: {str(error)}"
    show_error_message(error_message)
    print(f"Database Error - {operation}: {error}")


def format_currency(amount: float) -> str:
    """Formatear cantidad como moneda"""
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """Formatear valor como porcentaje"""
    return f"{value:.1f}%"


def get_current_month_year() -> tuple:
    """Obtener mes y año actual"""
    now = datetime.now()
    return now.month, now.year


def validate_required_fields(fields: Dict[str, Any]) -> List[str]:
    """Validar campos requeridos"""
    missing_fields = []
    for field_name, field_value in fields.items():
        if not field_value or (isinstance(field_value, str) and not field_value.strip()):
            missing_fields.append(field_name)
    return missing_fields


def validate_numeric_field(value: Any, field_name: str, min_value: float = 0) -> bool:
    """Validar campo numérico"""
    try:
        numeric_value = float(value)
        if numeric_value < min_value:
            show_error_message(f"{field_name} debe ser mayor o igual a {min_value}")
            return False
        return True
    except (ValueError, TypeError):
        show_error_message(f"{field_name} debe ser un número válido")
        return False


def validate_date_field(date_value: date, field_name: str) -> bool:
    """Validar campo de fecha"""
    if not date_value:
        show_error_message(f"{field_name} es requerido")
        return False
    
    if date_value > date.today():
        show_error_message(f"{field_name} no puede ser una fecha futura")
        return False
    
    return True


def create_metric_card(title: str, value: str, delta: Optional[str] = None) -> None:
    """Crear tarjeta de métrica consistente"""
    st.markdown(f"""
    <div class="metric-card">
        <h4>{title}</h4>
        <h2>{value}</h2>
        {f'<p>{delta}</p>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)


def create_navigation_button(text: str, icon: str, key: str) -> bool:
    """Crear botón de navegación consistente"""
    return st.sidebar.button(f"{icon} {text}", key=key, use_container_width=True)


def create_form_button(text: str, icon: str, button_type: str = "primary") -> bool:
    """Crear botón de formulario consistente"""
    if button_type == "primary":
        return st.form_submit_button(f"{icon} {text}", use_container_width=True)
    elif button_type == "secondary":
        return st.form_submit_button(f"{icon} {text}", use_container_width=True, type="secondary")
    else:
        return st.form_submit_button(f"{icon} {text}", use_container_width=True)


def create_action_buttons(actions: List[Dict[str, str]]) -> Dict[str, bool]:
    """Crear botones de acción consistentes"""
    results = {}
    cols = st.columns(len(actions))
    
    for i, action in enumerate(actions):
        with cols[i]:
            results[action["key"]] = st.button(
                action["icon"], 
                key=action["key"], 
                help=action.get("tooltip", "")
            )
    
    return results


def create_data_table(data: List[Dict], columns: List[str]) -> None:
    """Crear tabla de datos consistente"""
    if not data:
        show_info_message("No hay datos para mostrar")
        return
    
    # Crear DataFrame
    import pandas as pd
    df = pd.DataFrame(data)
    
    # Mostrar tabla
    st.dataframe(df, use_container_width=True)


def create_loading_spinner(message: str = "Cargando..."):
    """Crear spinner de carga"""
    return st.spinner(message)


def show_fullscreen_loading(message: str = "Cargando..."):
    """Mostrar loading de pantalla completa que bloquea interacciones"""
    # Usar st.spinner que es más confiable
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
    # No necesitamos hacer nada, st.spinner se oculta automáticamente
    pass


def create_expander(title: str, expanded: bool = False):
    """Crear expander consistente"""
    return st.expander(title, expanded=expanded)


def create_columns(num_columns: int) -> List:
    """Crear columnas consistentes"""
    return st.columns(num_columns)


def create_tabs(tab_names: List[str]) -> List:
    """Crear tabs consistentes"""
    return st.tabs(tab_names)


def create_divider():
    """Crear divisor consistente"""
    st.divider()


def create_space():
    """Crear espacio consistente"""
    st.markdown("<br>", unsafe_allow_html=True)
