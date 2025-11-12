"""
Funciones auxiliares para evitar repetición de código
"""

import streamlit as st
from typing import Any, Dict, List, Optional
from datetime import datetime, date


def mostrar_navegacion_lateral():
    """Mostrar navegación lateral personalizada (detecta automáticamente el módulo)"""
    # Detectar si estamos en el módulo nutricional o financiero
    mostrar_dashboard = st.session_state.get("mostrar_dashboard")
    
    # Verificar si ya se mostró la navegación en esta ejecución para evitar duplicados
    # Solo verificar si se llama desde una página individual cuando ya se mostró desde app.py/Home.py
    nav_key = "nav_lateral_shown_this_run"
    
    # Si el flag está en True, significa que ya se mostró en esta ejecución
    # En ese caso, no mostrar de nuevo para evitar duplicados
    if st.session_state.get(nav_key, False) == True:
        return  # Ya se mostró en esta ejecución, evitar duplicados
    
    # Marcar como mostrado
    st.session_state[nav_key] = True
    
    if mostrar_dashboard == "nutricional":
        mostrar_navegacion_lateral_nutricional()
    else:
        mostrar_navegacion_lateral_financiera()


def mostrar_navegacion_lateral_financiera():
    """Mostrar navegación lateral para el módulo financiero"""
    # Verificar si ya se mostró la navegación en esta ejecución para evitar duplicados
    # Este flag previene que se muestre dos veces cuando se llama desde Home.py y desde páginas individuales
    nav_key = "nav_financiera_shown_this_run"
    
    # Solo verificar el flag si se llama desde una página individual (no desde Home.py)
    # Si se llama desde Home.py, siempre mostrar los botones
    # Detectar si se llama desde una página individual verificando si ya se mostró desde Home.py
    if st.session_state.get(nav_key, False):
        # Si el flag está establecido, significa que ya se mostró desde Home.py
        # En este caso, no mostrar de nuevo para evitar duplicados
        return  # Ya se mostró en esta ejecución, evitar duplicados
    
    # Establecer el flag para indicar que se mostró la navegación
    st.session_state[nav_key] = True
    
    # Ocultar solo el menú automático de Streamlit (campo de búsqueda "app" y lista de páginas en texto)
    # pero mantener nuestros botones personalizados
    st.markdown("""
    <style>
    /* Ocultar el menú de navegación automático de Streamlit (solo la parte superior) */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    /* Ocultar cualquier input de búsqueda en el sidebar */
    section[data-testid="stSidebar"] input[type="search"],
    section[data-testid="stSidebar"] input[placeholder*="app"],
    section[data-testid="stSidebar"] input[placeholder*="Search"] {
        display: none !important;
    }
    
    /* Ocultar la lista de páginas automática (solo texto, no botones) */
    section[data-testid="stSidebar"] nav,
    section[data-testid="stSidebar"] ul[role="navigation"],
    section[data-testid="stSidebar"] div[role="navigation"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Botón de inicio en la parte superior
    if st.sidebar.button("🏠 Página de Inicio", use_container_width=True, type="primary", key="nav_inicio_fin"):
        st.session_state["mostrar_dashboard"] = None
        # Limpiar flags de navegación para permitir rerun
        if nav_key in st.session_state:
            del st.session_state[nav_key]
        if "nav_lateral_shown_this_run" in st.session_state:
            del st.session_state["nav_lateral_shown_this_run"]
        st.rerun()
    
    st.sidebar.divider()
    
    # Obtener página actual
    pagina_actual = st.session_state.get("pagina_actual", "dashboard")
    
    # Botones de navegación principales con keys únicos
    if st.sidebar.button("💰 Dashboard", use_container_width=True, type="tertiary" if pagina_actual == "dashboard" else "primary", key="nav_dashboard_fin"):
        st.session_state["pagina_actual"] = "dashboard"
        # Limpiar flags de navegación para permitir rerun
        if nav_key in st.session_state:
            del st.session_state[nav_key]
        if "nav_lateral_shown_this_run" in st.session_state:
            del st.session_state["nav_lateral_shown_this_run"]
        st.rerun()
    
    if st.sidebar.button("🏦 Cuentas", use_container_width=True, type="tertiary" if pagina_actual == "cuentas" else "primary", key="nav_cuentas_fin"):
        st.session_state["pagina_actual"] = "cuentas"
        # Limpiar flags de navegación para permitir rerun
        if nav_key in st.session_state:
            del st.session_state[nav_key]
        if "nav_lateral_shown_this_run" in st.session_state:
            del st.session_state["nav_lateral_shown_this_run"]
        st.rerun()
    
    if st.sidebar.button("💰 Movimientos", use_container_width=True, type="tertiary" if pagina_actual == "movimientos" else "primary", key="nav_movimientos_fin"):
        st.session_state["pagina_actual"] = "movimientos"
        # Limpiar flags de navegación para permitir rerun
        if nav_key in st.session_state:
            del st.session_state[nav_key]
        if "nav_lateral_shown_this_run" in st.session_state:
            del st.session_state["nav_lateral_shown_this_run"]
        st.rerun()
    
    if st.sidebar.button("📊 Reportes", use_container_width=True, type="tertiary" if pagina_actual == "reportes" else "primary", key="nav_reportes_fin"):
        st.session_state["pagina_actual"] = "reportes"
        # Limpiar flags de navegación para permitir rerun
        if nav_key in st.session_state:
            del st.session_state[nav_key]
        if "nav_lateral_shown_this_run" in st.session_state:
            del st.session_state["nav_lateral_shown_this_run"]
        st.rerun()
    
    if st.sidebar.button("💳 Gastos Recurrentes", use_container_width=True, type="tertiary" if pagina_actual == "gastos_recurrentes" else "primary", key="nav_gastos_recurrentes_fin"):
        st.session_state["pagina_actual"] = "gastos_recurrentes"
        # Limpiar flags de navegación para permitir rerun
        if nav_key in st.session_state:
            del st.session_state[nav_key]
        if "nav_lateral_shown_this_run" in st.session_state:
            del st.session_state["nav_lateral_shown_this_run"]
        st.rerun()
    
    if st.sidebar.button("🎯 Metas", use_container_width=True, type="tertiary" if pagina_actual == "metas" else "primary", key="nav_metas_fin"):
        st.session_state["pagina_actual"] = "metas"
        # Limpiar flags de navegación para permitir rerun
        if nav_key in st.session_state:
            del st.session_state[nav_key]
        if "nav_lateral_shown_this_run" in st.session_state:
            del st.session_state["nav_lateral_shown_this_run"]
        st.rerun()
    
    if st.sidebar.button("⚙️ Configuración", use_container_width=True, type="tertiary" if pagina_actual == "configuracion" else "primary", key="nav_configuracion_fin"):
        st.session_state["pagina_actual"] = "configuracion"
        # Limpiar flags de navegación para permitir rerun
        if nav_key in st.session_state:
            del st.session_state[nav_key]
        if "nav_lateral_shown_this_run" in st.session_state:
            del st.session_state["nav_lateral_shown_this_run"]
        st.rerun()


def mostrar_navegacion_lateral_nutricional():
    """Mostrar navegación lateral para el módulo nutricional"""
    # Verificar si ya se mostró la navegación en esta ejecución para evitar duplicados
    # Este flag previene que se muestre dos veces cuando se llama desde app.py y desde páginas individuales
    nav_key = "nav_nutricional_shown_this_run"
    
    # Si el flag está explícitamente en False o no existe, significa que podemos mostrar la navegación
    # Si está en True, significa que ya se mostró en esta ejecución, así que no mostrar de nuevo
    if st.session_state.get(nav_key, False) == True:
        # Ya se mostró en esta ejecución, evitar duplicados
        return
    
    # Establecer el flag para indicar que se mostró la navegación
    st.session_state[nav_key] = True
    
    # Ocultar solo el menú automático de Streamlit (campo de búsqueda "app" y lista de páginas en texto)
    # pero mantener nuestros botones personalizados
    st.markdown("""
    <style>
    /* Ocultar el menú de navegación automático de Streamlit (solo la parte superior) */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    /* Ocultar cualquier input de búsqueda en el sidebar */
    section[data-testid="stSidebar"] input[type="search"],
    section[data-testid="stSidebar"] input[placeholder*="app"],
    section[data-testid="stSidebar"] input[placeholder*="Search"] {
        display: none !important;
    }
    
    /* Ocultar la lista de páginas automática (solo texto, no botones) */
    section[data-testid="stSidebar"] nav,
    section[data-testid="stSidebar"] ul[role="navigation"],
    section[data-testid="stSidebar"] div[role="navigation"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Botón de inicio en la parte superior
    if st.sidebar.button("🏠 Página de Inicio", use_container_width=True, type="primary", key="nav_inicio_nut"):
        st.session_state["mostrar_dashboard"] = None
        # Resetear flags de navegación para permitir rerun
        st.session_state[nav_key] = False
        if "nav_lateral_shown_this_run" in st.session_state:
            st.session_state["nav_lateral_shown_this_run"] = False
        st.rerun()
    
    st.sidebar.divider()
    
    # Obtener página actual nutricional
    pagina_actual = st.session_state.get("pagina_nutricional_actual", "dashboard")
    
    # Botones de navegación nutricional con keys únicos
    if st.sidebar.button("🥗 Dashboard Nutricional", use_container_width=True, type="tertiary" if pagina_actual == "dashboard" else "primary", key="nav_dashboard_nut"):
        st.session_state["pagina_nutricional_actual"] = "dashboard"
        st.session_state["mostrar_dashboard"] = "nutricional"
        # Resetear flags de navegación para permitir rerun
        st.session_state[nav_key] = False
        if "nav_lateral_shown_this_run" in st.session_state:
            st.session_state["nav_lateral_shown_this_run"] = False
        st.rerun()
    
    if st.sidebar.button("🍽️ Registro de Comidas", use_container_width=True, type="tertiary" if pagina_actual == "registro" else "primary", key="nav_registro_nut"):
        st.session_state["pagina_nutricional_actual"] = "registro"
        st.session_state["mostrar_dashboard"] = "nutricional"
        # Resetear flags de navegación para permitir rerun
        st.session_state[nav_key] = False
        if "nav_lateral_shown_this_run" in st.session_state:
            st.session_state["nav_lateral_shown_this_run"] = False
        st.rerun()
    
    if st.sidebar.button("🎯 Metas Nutricionales", use_container_width=True, type="tertiary" if pagina_actual == "metas" else "primary", key="nav_metas_nut"):
        st.session_state["pagina_nutricional_actual"] = "metas"
        st.session_state["mostrar_dashboard"] = "nutricional"
        # Resetear flags de navegación para permitir rerun
        st.session_state[nav_key] = False
        if "nav_lateral_shown_this_run" in st.session_state:
            st.session_state["nav_lateral_shown_this_run"] = False
        st.rerun()
    
    if st.sidebar.button("📊 Historial", use_container_width=True, type="tertiary" if pagina_actual == "historial" else "primary", key="nav_historial_nut"):
        st.session_state["pagina_nutricional_actual"] = "historial"
        st.session_state["mostrar_dashboard"] = "nutricional"
        # Resetear flags de navegación para permitir rerun
        st.session_state[nav_key] = False
        if "nav_lateral_shown_this_run" in st.session_state:
            st.session_state["nav_lateral_shown_this_run"] = False
        st.rerun()
    
    if st.sidebar.button("⚖️ Peso y Metas", use_container_width=True, type="tertiary" if pagina_actual == "peso" else "primary", key="nav_peso_nut"):
        st.session_state["pagina_nutricional_actual"] = "peso"
        st.session_state["mostrar_dashboard"] = "nutricional"
        # Resetear flags de navegación para permitir rerun
        st.session_state[nav_key] = False
        if "nav_lateral_shown_this_run" in st.session_state:
            st.session_state["nav_lateral_shown_this_run"] = False
        st.rerun()


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
        
        st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_html=True)


def get_css_styles() -> str:
    """Obtener estilos CSS reutilizables"""
    return """
    <style>
    .main-header {
        text-align: center;
        padding: 2.5rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: white;
    }
    
    .main-header p {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
    }
    
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        margin: 0 0 0.5rem 0;
        color: #333;
    }
    
    .metric-card .value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    button[kind="primary"] {
        background-color: transparent !important;
        color: inherit !important;
        border: 1px solid rgb(78 162 189) !important;
    }
    
    button[kind="primary"]:hover {
        background-color: rgba(250, 250, 250, 0.1) !important;
        border: 1px solid rgba(250, 250, 250, 0.3) !important;
        color: rgb(78 162 189) !important;
    }

    button[kind="tertiary"] {
        background-color: rgba(250, 250, 250, 0.1) !important;
        border: 1px solid rgb(78 162 189) !important;
        color: rgb(78 162 189) !important;
    }

    button[kind="tertiary"]:hover {
        background-color: rgba(250, 250, 250, 0.1) !important;
        border: 1px solid rgba(250, 250, 250, 0.3) !important;
        color: white !important;
    }
    
    """


def apply_css_styles():
    """Aplicar estilos CSS personalizados"""
    st.markdown(get_css_styles(), unsafe_allow_html=True)


def show_error_message(message: str):
    """Mostrar mensaje de error de forma consistente"""
    st.error(f"❌ {message}")


def show_success_message(message: str):
    """Mostrar mensaje de éxito de forma consistente"""
    st.success(f"✅ {message}")


def show_warning_message(message: str):
    """Mostrar mensaje de advertencia de forma consistente"""
    st.warning(f"⚠️ {message}")


def show_info_message(message: str):
    """Mostrar mensaje informativo de forma consistente"""
    st.info(f"ℹ️ {message}")


def format_currency(amount: float, currency: str = "$") -> str:
    """Formatear cantidad como moneda"""
    return f"{currency}{amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Formatear valor como porcentaje"""
    return f"{value:.{decimals}f}%"


def format_date(date_obj: date, format_str: str = "%d/%m/%Y") -> str:
    """Formatear fecha"""
    return date_obj.strftime(format_str)


def format_datetime(datetime_obj: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
    """Formatear fecha y hora"""
    return datetime_obj.strftime(format_str)


def get_month_name(month: int) -> str:
    """Obtener nombre del mes"""
    months = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    return months[month - 1] if 1 <= month <= 12 else ""


def validate_email(email: str) -> bool:
    """Validar formato de email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validar formato de teléfono"""
    import re
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Dividir de forma segura evitando división por cero"""
    return numerator / denominator if denominator != 0 else default


def calculate_percentage(part: float, total: float) -> float:
    """Calcular porcentaje"""
    return safe_divide(part, total, 0.0) * 100


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncar texto a una longitud máxima"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def group_by_key(items: List[Dict], key: str) -> Dict[Any, List[Dict]]:
    """Agrupar items por una clave"""
    grouped = {}
    for item in items:
        group_key = item.get(key)
        if group_key not in grouped:
            grouped[group_key] = []
        grouped[group_key].append(item)
    return grouped


def sort_dict_by_value(d: Dict, reverse: bool = True) -> List[tuple]:
    """Ordenar diccionario por valor"""
    return sorted(d.items(), key=lambda x: x[1], reverse=reverse)


def get_top_items(items: List[Dict], key: str, top_n: int = 5) -> List[Dict]:
    """Obtener los top N items ordenados por una clave"""
    sorted_items = sorted(items, key=lambda x: x.get(key, 0), reverse=True)
    return sorted_items[:top_n]


def filter_by_date_range(items: List[Dict], date_key: str, start_date: date, end_date: date) -> List[Dict]:
    """Filtrar items por rango de fechas"""
    filtered = []
    for item in items:
        item_date = item.get(date_key)
        if isinstance(item_date, str):
            item_date = datetime.fromisoformat(item_date).date()
        if start_date <= item_date <= end_date:
            filtered.append(item)
    return filtered


def calculate_sum(items: List[Dict], key: str) -> float:
    """Calcular suma de valores en una lista de diccionarios"""
    return sum(item.get(key, 0) for item in items)


def calculate_average(items: List[Dict], key: str) -> float:
    """Calcular promedio de valores en una lista de diccionarios"""
    if not items:
        return 0.0
    total = calculate_sum(items, key)
    return total / len(items)


def get_unique_values(items: List[Dict], key: str) -> List[Any]:
    """Obtener valores únicos de una clave en una lista de diccionarios"""
    return list(set(item.get(key) for item in items if key in item))


def merge_dicts(*dicts: Dict) -> Dict:
    """Fusionar múltiples diccionarios"""
    merged = {}
    for d in dicts:
        merged.update(d)
    return merged


def deep_copy_dict(d: Dict) -> Dict:
    """Crear copia profunda de un diccionario"""
    import copy
    return copy.deepcopy(d)


def remove_none_values(d: Dict) -> Dict:
    """Remover valores None de un diccionario"""
    return {k: v for k, v in d.items() if v is not None}


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
    """Aplanar diccionario anidado"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
