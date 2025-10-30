"""
Configuración del Sistema
Página para gestionar categorías y tipos de gasto
"""

import streamlit as st
from utils.database import cargar_configuracion, guardar_configuracion
from utils.helpers import apply_css_styles


def main():
    """Función principal de la página de configuración"""
    
    # Aplicar CSS personalizado
    apply_css_styles()
    
    # Navegación lateral personalizada
    from utils.helpers import mostrar_navegacion_lateral
    mostrar_navegacion_lateral()
    
    st.title("⚙️ Configuración del Sistema")
    
    # Cargar configuración
    configuracion = cargar_configuracion()
    
    # Gestión de categorías
    st.subheader("🏷️ Gestión de Categorías")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        nueva_categoria = st.text_input("➕ Nueva Categoría", placeholder="Ej: Alimentación, Transporte, etc.")
    with col2:
        if st.button("➕ Agregar", use_container_width=True):
            if nueva_categoria:
                from utils.database import agregar_categoria
                success, message = agregar_categoria(nueva_categoria)
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.error("❌ Por favor ingresa un nombre")
    
    # Lista de categorías
    st.write("**Categorías actuales:**")
    cols = st.columns(3)
    for i, categoria in enumerate(configuracion["categorias"]):
        with cols[i % 3]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"🏷️ {categoria}")
            with col2:
                if st.button("🗑️", key=f"del_cat_{categoria}"):
                    # Recargar configuración antes de eliminar
                    configuracion = cargar_configuracion()
                    if categoria in configuracion.get("categorias", []):
                        configuracion["categorias"].remove(categoria)
                        if guardar_configuracion(configuracion):
                            st.success(f"✅ Categoría '{categoria}' eliminada!")
                            st.rerun()
                        else:
                            st.error("❌ Error al eliminar la categoría")
    
    st.divider()
    
    # Gestión de tipos de gasto
    st.subheader("🔍 Tipos de Gasto")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        nuevo_tipo = st.text_input("➕ Nuevo Tipo de Gasto", placeholder="Ej: Inversión, Ahorro, etc.")
    with col2:
        if st.button("➕ Agregar Tipo", use_container_width=True):
            if nuevo_tipo:
                from utils.database import agregar_tipo_gasto
                success, message = agregar_tipo_gasto(nuevo_tipo)
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.error("❌ Por favor ingresa un nombre")
    
    # Lista de tipos de gasto
    st.write("**Tipos de gasto actuales:**")
    cols = st.columns(3)
    for i, tipo in enumerate(configuracion["tipos_gasto"]):
        with cols[i % 3]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"🔍 {tipo}")
            with col2:
                if st.button("🗑️", key=f"del_tipo_{tipo}"):
                    # Recargar configuración antes de eliminar
                    configuracion = cargar_configuracion()
                    if tipo in configuracion.get("tipos_gasto", []):
                        configuracion["tipos_gasto"].remove(tipo)
                        if guardar_configuracion(configuracion):
                            st.success(f"✅ Tipo '{tipo}' eliminado!")
                            st.rerun()
                        else:
                            st.error("❌ Error al eliminar el tipo")
    
    st.divider()
    st.info("💡 **Tip:** Los cambios en categorías y tipos se aplicarán inmediatamente en todos los formularios.")


if __name__ == "__main__":
    main()