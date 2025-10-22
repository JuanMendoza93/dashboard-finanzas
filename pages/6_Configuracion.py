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
            if nueva_categoria and nueva_categoria not in configuracion["categorias"]:
                configuracion["categorias"].append(nueva_categoria)
                if guardar_configuracion(configuracion):
                    st.success(f"✅ Categoría '{nueva_categoria}' agregada!")
                else:
                    st.error("❌ Error al guardar la categoría")
            elif nueva_categoria in configuracion["categorias"]:
                st.error("❌ Esta categoría ya existe")
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
                    configuracion["categorias"].remove(categoria)
                    guardar_configuracion(configuracion)
                    st.success(f"✅ Categoría '{categoria}' eliminada!")
                    st.rerun()
    
    st.divider()
    
    # Gestión de tipos de gasto
    st.subheader("🔍 Tipos de Gasto")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        nuevo_tipo = st.text_input("➕ Nuevo Tipo de Gasto", placeholder="Ej: Inversión, Ahorro, etc.")
    with col2:
        if st.button("➕ Agregar Tipo", use_container_width=True):
            if nuevo_tipo and nuevo_tipo not in configuracion["tipos_gasto"]:
                configuracion["tipos_gasto"].append(nuevo_tipo)
                if guardar_configuracion(configuracion):
                    st.success(f"✅ Tipo '{nuevo_tipo}' agregado!")
                else:
                    st.error("❌ Error al guardar el tipo")
            elif nuevo_tipo in configuracion["tipos_gasto"]:
                st.error("❌ Este tipo ya existe")
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
                    configuracion["tipos_gasto"].remove(tipo)
                    guardar_configuracion(configuracion)
                    st.success(f"✅ Tipo '{tipo}' eliminado!")
                    st.rerun()
    
    st.divider()
    st.info("💡 **Tip:** Los cambios en categorías y tipos se aplicarán inmediatamente en todos los formularios.")


if __name__ == "__main__":
    main()