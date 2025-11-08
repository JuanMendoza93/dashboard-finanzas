"""
Dashboard Personal - Punto de entrada principal
Página de inicio para seleccionar entre Dashboard Financiero y Nutricional
"""

import streamlit as st
from Inicio import main as mostrar_inicio

# Verificar si ya se seleccionó un dashboard
if st.session_state.get("mostrar_dashboard") == "financiero":
    from Home import main as mostrar_dashboard_financiero
    mostrar_dashboard_financiero()
elif st.session_state.get("mostrar_dashboard") == "nutricional":
    # Determinar qué página nutricional mostrar
    pagina_nutricional = st.session_state.get("pagina_nutricional_actual", "dashboard")
    
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
