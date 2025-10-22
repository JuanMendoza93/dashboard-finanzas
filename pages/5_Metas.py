"""
Gestión de Metas de Ahorro
Página para establecer y monitorear metas de ahorro mensual y anual
"""

import streamlit as st
from utils.database import cargar_metas, guardar_metas
from utils.config_manager import config_manager
from utils.helpers import apply_css_styles


def main():
    """Función principal de la página de metas"""
    
    # Aplicar CSS personalizado
    apply_css_styles()
    
    # Navegación lateral personalizada
    from utils.helpers import mostrar_navegacion_lateral
    mostrar_navegacion_lateral()
    
    st.title("🎯 Metas de Ahorro")
    
    # Cargar metas existentes
    metas = cargar_metas()
    
    # Mostrar metas actuales
    mostrar_metas_actuales(metas)
    
    # Formulario para establecer/actualizar metas
    st.divider()
    st.subheader("🎯 Establecer Metas de Ahorro")
    
    with st.form("metas_ahorro"):
        col1, col2 = st.columns(2)
        
        with col1:
            meta_mensual = st.number_input("💰 Meta Mensual", 
                                        value=float(metas.get("meta_mensual", 0)), 
                                        min_value=0.0, step=100.0, format="%.2f",
                                        help="Cantidad que deseas ahorrar cada mes")
        
        with col2:
            meta_anual = st.number_input("🎯 Meta Anual", 
                                      value=float(metas.get("meta_anual", 0)), 
                                      min_value=0.0, step=1000.0, format="%.2f",
                                      help="Cantidad total que deseas ahorrar en el año")
        
        if st.form_submit_button("💾 Guardar Metas", use_container_width=True):
            if meta_mensual > 0 or meta_anual > 0:
                nuevas_metas = {
                    "meta_mensual": meta_mensual,
                    "meta_anual": meta_anual
                }
                
                if guardar_metas(nuevas_metas):
                    st.success("✅ Metas guardadas exitosamente!")
                    st.rerun()
                else:
                    st.error("❌ Error al guardar las metas")
            else:
                st.error("❌ Por favor establece al menos una meta")


def mostrar_metas_actuales(metas):
    """Mostrar las metas actuales con su progreso"""
    
    st.subheader("📊 Metas Actuales")
    
    meta_mensual = metas.get("meta_mensual", 0)
    meta_anual = metas.get("meta_anual", 0)
    
    if meta_mensual == 0 and meta_anual == 0:
        st.info("No hay metas establecidas. Establece tus metas abajo.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        if meta_mensual > 0:
            st.metric("💰 Meta Mensual", config_manager.get_formatted_currency(meta_mensual))
        else:
            st.info("No hay meta mensual establecida")
    
    with col2:
        if meta_anual > 0:
            st.metric("🎯 Meta Anual", config_manager.get_formatted_currency(meta_anual))
        else:
            st.info("No hay meta anual establecida")


if __name__ == "__main__":
    main()