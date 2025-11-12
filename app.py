"""
Dashboard Personal - Punto de entrada principal
Página de inicio para seleccionar entre Dashboard Financiero y Nutricional
"""

import streamlit as st
import os

# Cargar variables de entorno desde archivo .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Si python-dotenv no está instalado, continuar sin él
    pass

from Inicio import main as mostrar_inicio

# Verificar si ya se seleccionó un dashboard
if st.session_state.get("mostrar_dashboard") == "financiero":
    from Home import main as mostrar_dashboard_financiero
    mostrar_dashboard_financiero()
elif st.session_state.get("mostrar_dashboard") == "nutricional":
    # Obtener página actual nutricional
    pagina_nutricional = st.session_state.get("pagina_nutricional_actual", "dashboard")
    
    # Limpiar flag de navegación al inicio para asegurar que los botones siempre se muestren
    # Esto es necesario porque el flag puede estar establecido desde una ejecución anterior
    if "nav_nutricional_shown_this_run" in st.session_state:
        del st.session_state["nav_nutricional_shown_this_run"]
    if "nav_lateral_shown_this_run" in st.session_state:
        del st.session_state["nav_lateral_shown_this_run"]
    
    # Mostrar navegación lateral SIEMPRE (antes de cargar cualquier página)
    # Esto asegura que el menú lateral esté visible en todo momento
    # Las páginas individuales también la mostrarán, pero el flag evitará duplicados
    from utils.helpers import mostrar_navegacion_lateral_nutricional
    mostrar_navegacion_lateral_nutricional()
    
    if pagina_nutricional == "dashboard":
        from pages.nutricion.dashboard_nutricional import main as mostrar_dashboard_nutricional
        mostrar_dashboard_nutricional()
    elif pagina_nutricional == "registro":
        # Importar y ejecutar la página de registro
        import importlib.util
        spec = importlib.util.spec_from_file_location("registro_comidas", "pages/nutricion/2_Registro_Comidas.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.main()
    elif pagina_nutricional == "metas":
        import importlib.util
        spec = importlib.util.spec_from_file_location("metas_nutricionales", "pages/nutricion/3_Metas_Nutricionales.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.main()
    elif pagina_nutricional == "historial":
        import importlib.util
        spec = importlib.util.spec_from_file_location("historial", "pages/nutricion/4_Historial.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.main()
    else:
        from pages.nutricion.dashboard_nutricional import main as mostrar_dashboard_nutricional
        mostrar_dashboard_nutricional()
else:
    # Mostrar página de inicio
    mostrar_inicio()
