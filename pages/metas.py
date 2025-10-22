"""
Página para gestión de metas de ahorro
"""

import streamlit as st
from utils.database import firebase_get, firebase_set
from utils.config_manager import config_manager


def mostrar_metas():
    """Mostrar página de gestión de metas de ahorro"""
    
    st.title("🎯 Gestión de Metas de Ahorro")
    
    # Inicializar estado si no existe
    if "metas_cargadas" not in st.session_state:
        st.session_state["metas_cargadas"] = False
    
    # Obtener metas actuales solo si no se han cargado
    if not st.session_state["metas_cargadas"]:
        try:
            metas_data = firebase_get("metas")
            meta_mensual = float(metas_data.get("meta_mensual", 0)) if metas_data else 0
            meta_anual = float(metas_data.get("meta_anual", 0)) if metas_data else 0
            
            # Guardar en session state
            st.session_state["meta_mensual"] = meta_mensual
            st.session_state["meta_anual"] = meta_anual
            st.session_state["metas_cargadas"] = True
        except:
            st.session_state["meta_mensual"] = 0
            st.session_state["meta_anual"] = 0
            st.session_state["metas_cargadas"] = True
    
    # Usar valores del session state
    meta_mensual = st.session_state["meta_mensual"]
    meta_anual = st.session_state["meta_anual"]
    
    # Mostrar métricas actuales
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Meta Mensual", config_manager.get_formatted_currency(meta_mensual))
    with col2:
        st.metric("Meta Anual", config_manager.get_formatted_currency(meta_anual))
    
    st.divider()
    
    # Formulario para configurar metas
    with st.expander("⚙️ Configurar Metas de Ahorro", expanded=True):
        st.subheader("🎯 Configuración de Metas")
        
        col1, col2 = st.columns(2)
        with col1:
            nueva_meta_mensual = st.number_input(
                "Meta Mensual de Ahorro", 
                min_value=0.0, 
                value=float(meta_mensual),
                step=100.0,
                key="meta_mensual_input"
            )
        
        with col2:
            nueva_meta_anual = st.number_input(
                "Meta Anual de Ahorro", 
                min_value=0.0, 
                value=float(meta_anual),
                step=1000.0,
                key="meta_anual_input"
            )
        
        # Botón fuera del formulario para evitar ciclos
        if st.button("💾 Guardar Metas", use_container_width=True, key="guardar_metas_btn"):
            # Usar los valores actuales del session state para comparar
            meta_mensual_actual = st.session_state["meta_mensual"]
            meta_anual_actual = st.session_state["meta_anual"]
            
            if nueva_meta_mensual != meta_mensual_actual or nueva_meta_anual != meta_anual_actual:
                try:
                    # Guardar en Firebase
                    metas_config = {
                        "meta_mensual": nueva_meta_mensual,
                        "meta_anual": nueva_meta_anual
                    }
                    
                    if firebase_set("metas", metas_config):
                        # Actualizar session state
                        st.session_state["meta_mensual"] = nueva_meta_mensual
                        st.session_state["meta_anual"] = nueva_meta_anual
                        st.success("✅ Metas guardadas exitosamente!")
                        # No usar st.rerun() para evitar ejecución doble
                    else:
                        st.error("❌ Error al guardar las metas")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.warning("⚠️ No hay cambios para guardar")
    
    # Información adicional
    st.info("💡 Las metas te ayudan a planificar tus objetivos de ahorro mensual y anual.")
