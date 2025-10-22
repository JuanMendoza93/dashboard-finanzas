"""
Gestión de Gastos Recurrentes
Página para administrar gastos que se repiten periódicamente
"""

import streamlit as st
from utils.database import cargar_gastos_recurrentes, guardar_gasto_recurrente, eliminar_gasto_recurrente, actualizar_gasto_recurrente, cargar_configuracion
from utils.config_manager import config_manager
from utils.helpers import apply_css_styles


def main():
    """Función principal de la página de gastos recurrentes"""
    
    # Aplicar CSS personalizado
    apply_css_styles()
    
    # Navegación lateral personalizada
    from utils.helpers import mostrar_navegacion_lateral
    mostrar_navegacion_lateral()
    
    st.title("💳 Gastos Recurrentes")
    
    # Cargar configuración
    configuracion = cargar_configuracion()
    categorias_disponibles = configuracion.get("categorias", [])
    
    # Formulario colapsable para agregar nuevo gasto recurrente
    with st.expander("➕ Agregar Nuevo Gasto Recurrente", expanded=False):
        with st.form("nuevo_gasto_recurrente"):
            col1, col2 = st.columns(2)
            
            with col1:
                descripcion = st.text_input("📝 Descripción", placeholder="Ej: Netflix, Spotify, etc.")
                categoria = st.selectbox("🏷️ Categoría", categorias_disponibles)
                monto = st.number_input("💰 Monto", min_value=0.0, step=0.01, format="%.2f")
            
            with col2:
                periodicidad = st.selectbox("🔄 Periodicidad", 
                                          ["Semanal", "Quincenal", "Mensual", "Bimestral", "Trimestral", "Anual"])
            
            if st.form_submit_button("💾 Agregar Gasto Recurrente", use_container_width=True):
                if descripcion and monto > 0:
                    # Validar duplicados
                    gastos_existentes = cargar_gastos_recurrentes()
                    duplicado = any(
                        g["descripcion"].lower() == descripcion.lower() 
                        for g in gastos_existentes
                    )
                    
                    if duplicado:
                        st.error("❌ Ya existe un gasto recurrente con esa descripción")
                    else:
                        monto_mensual = calcular_monto_mensual(monto, periodicidad)
                        gasto_data = {
                            "descripcion": descripcion,
                            "categoria": categoria,
                            "monto": monto,
                            "periodicidad": periodicidad,
                            "monto_mensual": monto_mensual
                        }
                        
                        if guardar_gasto_recurrente(gasto_data):
                            st.success("✅ Gasto recurrente agregado exitosamente!")
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar el gasto recurrente")
                else:
                    st.error("❌ Por favor completa todos los campos")
    
    st.divider()
    
    # Mostrar gastos recurrentes existentes
    mostrar_gastos_recurrentes(categorias_disponibles)

    
    

def mostrar_gastos_recurrentes(categorias_disponibles):
    """Mostrar lista de gastos recurrentes con opciones de edición y eliminación"""
    
    st.subheader("📋 Gastos Recurrentes Registrados")
    
    # Obtener gastos recurrentes
    gastos_recurrentes = cargar_gastos_recurrentes()
    
    if not gastos_recurrentes:
        st.info("No hay gastos recurrentes registrados. Agrega uno nuevo arriba.")
        return
    
    # Calcular total mensual
    total_gastos_recurrentes = sum(gasto.get("monto_mensual", 0) for gasto in gastos_recurrentes)
    
    st.metric("💰 Presupuesto Mensual Total", config_manager.get_formatted_currency(total_gastos_recurrentes))
    
    st.divider()
    
    # Mostrar gastos en columnas
    cols = st.columns(2)
    
    for i, gasto in enumerate(gastos_recurrentes):
        with cols[i % 2]:
            with st.container():
                st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin: 5px 0">
                    <h4>💳 {gasto['descripcion']}</h4>
                    <p><strong>Categoría:</strong> {gasto['categoria']}</p>
                    <p><strong>Monto:</strong> {config_manager.get_formatted_currency(gasto['monto'])}</p>
                    <p><strong>Periodicidad:</strong> {gasto['periodicidad']}</p>
                    <p><strong>Monto Mensual:</strong> {config_manager.get_formatted_currency(gasto.get('monto_mensual', 0))}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Botones de acción
                col_edit, col_del = st.columns(2)
                
                with col_edit:
                    if st.button("✏️", key=f"edit_gasto_{gasto['id']}_{i}", use_container_width=True):
                        st.session_state[f"editando_gasto_{gasto['id']}"] = True
                
                with col_del:
                    if st.button("🗑️", key=f"del_gasto_{gasto['id']}_{i}", use_container_width=True):
                        if eliminar_gasto_recurrente(gasto['id']):
                            st.success(f"✅ Gasto '{gasto['descripcion']}' eliminado!")
                            st.rerun()
                        else:
                            st.error("❌ Error al eliminar el gasto")
                
                # Formulario de edición (se muestra si está en modo edición)
                if st.session_state.get(f"editando_gasto_{gasto['id']}", False):
                    st.markdown("---")
                    st.subheader(f"✏️ Editando: {gasto['descripcion']}")
                    
                    with st.form(f"edit_gasto_{gasto['id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            nueva_descripcion = st.text_input("Descripción", value=gasto['descripcion'], key=f"desc_{gasto['id']}")
                            nueva_categoria = st.selectbox("Categoría", categorias_disponibles, 
                                                        index=categorias_disponibles.index(gasto['categoria']) 
                                                        if gasto['categoria'] in categorias_disponibles else 0, 
                                                        key=f"cat_{gasto['id']}")
                            nuevo_monto = st.number_input("Monto", value=float(gasto['monto']), 
                                                        min_value=0.0, step=0.01, key=f"monto_{gasto['id']}")
                        
                        with col2:
                            nueva_periodicidad = st.selectbox("Periodicidad", 
                                                            ["Semanal", "Quincenal", "Mensual", "Bimestral", "Trimestral", "Anual"],
                                                            index=["Semanal", "Quincenal", "Mensual", "Bimestral", "Trimestral", "Anual"].index(gasto['periodicidad']),
                                                            key=f"per_{gasto['id']}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.form_submit_button("💾 Guardar", use_container_width=True):
                                # Validar duplicados (excluyendo el actual)
                                gastos_existentes = cargar_gastos_recurrentes()
                                duplicado = any(
                                    g["descripcion"].lower() == nueva_descripcion.lower() and g["id"] != gasto['id']
                                    for g in gastos_existentes
                                )
                                
                                if duplicado:
                                    st.error("❌ Ya existe otro gasto recurrente con esa descripción")
                                else:
                                    nuevo_monto_mensual = calcular_monto_mensual(nuevo_monto, nueva_periodicidad)
                                    datos_actualizados = {
                                        "descripcion": nueva_descripcion,
                                        "categoria": nueva_categoria,
                                        "monto": nuevo_monto,
                                        "periodicidad": nueva_periodicidad,
                                        "monto_mensual": nuevo_monto_mensual
                                    }
                                    
                                    if actualizar_gasto_recurrente(gasto['id'], datos_actualizados):
                                        st.success("✅ Gasto recurrente actualizado exitosamente!")
                                        st.session_state[f"editando_gasto_{gasto['id']}"] = False
                                        st.rerun()
                                    else:
                                        st.error("❌ Error al actualizar el gasto")
                        
                        with col2:
                            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                st.session_state[f"editando_gasto_{gasto['id']}"] = False
                                st.rerun()


def calcular_monto_mensual(monto, periodicidad):
    """Calcular el monto mensual equivalente según la periodicidad"""
    factores = {
        "Semanal": 4.33,      # 52 semanas / 12 meses
        "Quincenal": 2.17,    # 26 quincenas / 12 meses
        "Mensual": 1.0,
        "Bimestral": 0.5,     # 6 bimestres / 12 meses
        "Trimestral": 0.33,   # 4 trimestres / 12 meses
        "Anual": 0.083        # 1 año / 12 meses
    }
    
    factor = factores.get(periodicidad, 1.0)
    return monto * factor


if __name__ == "__main__":
    main()