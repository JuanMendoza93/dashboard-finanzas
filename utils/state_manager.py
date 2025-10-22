"""
Manejo de estado de la aplicación con clases
"""

from typing import Any, Dict, Optional
import streamlit as st
from datetime import datetime


class AppState:
    """Clase para manejar el estado de la aplicación"""
    
    def __init__(self):
        self._initialize_default_state()
    
    def _initialize_default_state(self):
        """Inicializar estado por defecto"""
        if "pagina_actual" not in st.session_state:
            st.session_state["pagina_actual"] = "cuentas"
        
        if "mostrar_formulario" not in st.session_state:
            st.session_state["mostrar_formulario"] = False
        
        if "editando_cuenta" not in st.session_state:
            st.session_state["editando_cuenta"] = {}
        
        if "agregando_dinero" not in st.session_state:
            st.session_state["agregando_dinero"] = {}
        
        if "filtros_activos" not in st.session_state:
            st.session_state["filtros_activos"] = {}
        
        if "ultima_actualizacion" not in st.session_state:
            st.session_state["ultima_actualizacion"] = datetime.now()
    
    def get_pagina_actual(self) -> str:
        """Obtener página actual"""
        return st.session_state.get("pagina_actual", "cuentas")
    
    def set_pagina_actual(self, pagina: str) -> None:
        """Establecer página actual"""
        st.session_state["pagina_actual"] = pagina
        st.session_state["ultima_actualizacion"] = datetime.now()
    
    def get_mostrar_formulario(self) -> bool:
        """Obtener estado del formulario"""
        return st.session_state.get("mostrar_formulario", False)
    
    def set_mostrar_formulario(self, mostrar: bool) -> None:
        """Establecer estado del formulario"""
        st.session_state["mostrar_formulario"] = mostrar
    
    def is_editando_cuenta(self, cuenta_id: str) -> bool:
        """Verificar si se está editando una cuenta"""
        return st.session_state.get("editando_cuenta", {}).get(cuenta_id, False)
    
    def set_editando_cuenta(self, cuenta_id: str, editando: bool) -> None:
        """Establecer estado de edición de cuenta"""
        if "editando_cuenta" not in st.session_state:
            st.session_state["editando_cuenta"] = {}
        st.session_state["editando_cuenta"][cuenta_id] = editando
    
    def is_agregando_dinero(self, cuenta_id: str) -> bool:
        """Verificar si se está agregando dinero a una cuenta"""
        return st.session_state.get("agregando_dinero", {}).get(cuenta_id, False)
    
    def set_agregando_dinero(self, cuenta_id: str, agregando: bool) -> None:
        """Establecer estado de agregar dinero"""
        if "agregando_dinero" not in st.session_state:
            st.session_state["agregando_dinero"] = {}
        st.session_state["agregando_dinero"][cuenta_id] = agregando
    
    def get_filtro(self, filtro_name: str) -> Any:
        """Obtener valor de filtro"""
        return st.session_state.get("filtros_activos", {}).get(filtro_name)
    
    def set_filtro(self, filtro_name: str, valor: Any) -> None:
        """Establecer valor de filtro"""
        if "filtros_activos" not in st.session_state:
            st.session_state["filtros_activos"] = {}
        st.session_state["filtros_activos"][filtro_name] = valor
    
    def clear_filtros(self) -> None:
        """Limpiar todos los filtros"""
        st.session_state["filtros_activos"] = {}
    
    def get_ultima_actualizacion(self) -> datetime:
        """Obtener última actualización"""
        return st.session_state.get("ultima_actualizacion", datetime.now())
    
    def update_timestamp(self) -> None:
        """Actualizar timestamp"""
        st.session_state["ultima_actualizacion"] = datetime.now()
    
    def clear_all_state(self) -> None:
        """Limpiar todo el estado"""
        st.session_state.clear()
        self._initialize_default_state()
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Obtener resumen del estado"""
        return {
            "pagina_actual": self.get_pagina_actual(),
            "mostrar_formulario": self.get_mostrar_formulario(),
            "editando_cuentas": len(st.session_state.get("editando_cuenta", {})),
            "agregando_dinero": len(st.session_state.get("agregando_dinero", {})),
            "filtros_activos": len(st.session_state.get("filtros_activos", {})),
            "ultima_actualizacion": self.get_ultima_actualizacion().strftime("%Y-%m-%d %H:%M:%S")
        }


class NavigationState:
    """Clase para manejar estado de navegación"""
    
    def __init__(self):
        self.pages = {
            "cuentas": {"title": "🏦 Cuentas", "icon": "🏦"},
            "movimientos": {"title": "💰 Movimientos", "icon": "💰"},
            "reportes": {"title": "📊 Reportes", "icon": "📊"},
            "configuracion": {"title": "⚙️ Configuración", "icon": "⚙️"},
            "firebase_test": {"title": "🔥 Prueba Firebase", "icon": "🔥"}
        }
    
    def get_page_info(self, page_key: str) -> Dict[str, str]:
        """Obtener información de una página"""
        return self.pages.get(page_key, {"title": "Página Desconocida", "icon": "❓"})
    
    def get_all_pages(self) -> Dict[str, Dict[str, str]]:
        """Obtener todas las páginas"""
        return self.pages
    
    def is_valid_page(self, page_key: str) -> bool:
        """Verificar si una página es válida"""
        return page_key in self.pages


class FormState:
    """Clase para manejar estado de formularios"""
    
    def __init__(self):
        self.forms = {}
    
    def create_form_state(self, form_name: str) -> None:
        """Crear estado para un formulario"""
        if form_name not in st.session_state:
            st.session_state[form_name] = {
                "is_open": False,
                "data": {},
                "errors": {},
                "last_submission": None
            }
    
    def open_form(self, form_name: str) -> None:
        """Abrir formulario"""
        self.create_form_state(form_name)
        st.session_state[form_name]["is_open"] = True
    
    def close_form(self, form_name: str) -> None:
        """Cerrar formulario"""
        if form_name in st.session_state:
            st.session_state[form_name]["is_open"] = False
    
    def is_form_open(self, form_name: str) -> bool:
        """Verificar si formulario está abierto"""
        return st.session_state.get(form_name, {}).get("is_open", False)
    
    def set_form_data(self, form_name: str, data: Dict[str, Any]) -> None:
        """Establecer datos del formulario"""
        self.create_form_state(form_name)
        st.session_state[form_name]["data"] = data
    
    def get_form_data(self, form_name: str) -> Dict[str, Any]:
        """Obtener datos del formulario"""
        return st.session_state.get(form_name, {}).get("data", {})
    
    def set_form_errors(self, form_name: str, errors: Dict[str, str]) -> None:
        """Establecer errores del formulario"""
        self.create_form_state(form_name)
        st.session_state[form_name]["errors"] = errors
    
    def get_form_errors(self, form_name: str) -> Dict[str, str]:
        """Obtener errores del formulario"""
        return st.session_state.get(form_name, {}).get("errors", {})
    
    def clear_form_errors(self, form_name: str) -> None:
        """Limpiar errores del formulario"""
        if form_name in st.session_state:
            st.session_state[form_name]["errors"] = {}
    
    def record_submission(self, form_name: str, success: bool) -> None:
        """Registrar envío del formulario"""
        self.create_form_state(form_name)
        st.session_state[form_name]["last_submission"] = {
            "timestamp": datetime.now(),
            "success": success
        }
    
    def get_last_submission(self, form_name: str) -> Optional[Dict[str, Any]]:
        """Obtener último envío del formulario"""
        return st.session_state.get(form_name, {}).get("last_submission")


# Instancias globales para uso en toda la aplicación
app_state = AppState()
navigation_state = NavigationState()
form_state = FormState()
