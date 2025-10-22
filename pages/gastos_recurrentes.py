"""
Página para gestión de gastos recurrentes
"""

import streamlit as st
from utils.database import firebase_get, firebase_set, cargar_gastos_recurrentes, guardar_gasto_recurrente, eliminar_gasto_recurrente, actualizar_gasto_recurrente, cargar_configuracion
from utils.config_manager import config_manager
from datetime import datetime
import time


def calcular_monto_mensual(monto, periodicidad):
    """Calcular el monto mensual basado en la periodicidad"""
    factores = {
        "Semanal": 4.33,  # 52 semanas / 12 meses
        "Quincenal": 2.17,  # 26 quincenas / 12 meses
        "Mensual": 1.0,
        "Bimestral": 0.5,  # 6 bimestres / 12 meses
        "Trimestral": 0.33,  # 4 trimestres / 12 meses
        "Anual": 0.083  # 1 año / 12 meses
    }
    return monto * factores.get(periodicidad, 1.0)


def mostrar_gastos_recurrentes():
    """Mostrar página de gestión de gastos recurrentes"""
    
    st.title("💳 Gestión de Gastos Recurrentes")
    
    # Inicializar estado si no existe
    if "gastos_cargados" not in st.session_state:
        st.session_state["gastos_cargados"] = False
    
    # Manejar recarga controlada
    if st.session_state.get("recargar_gastos", False):
        st.session_state["recargar_gastos"] = False
        st.session_state["gastos_cargados"] = False
    
    # Obtener gastos recurrentes actuales solo si no se han cargado o se necesita recargar
    if not st.session_state["gastos_cargados"]:
        try:
            gastos_recurrentes = cargar_gastos_recurrentes()
            st.session_state["gastos_recurrentes"] = gastos_recurrentes
            st.session_state["gastos_cargados"] = True
        except:
            st.session_state["gastos_recurrentes"] = []
            st.session_state["gastos_cargados"] = True
    
    # Usar gastos del session state
    gastos_recurrentes = st.session_state["gastos_recurrentes"]
    
    # Obtener categorías desde la base de datos
    try:
        configuracion = cargar_configuracion()
        categorias_disponibles = configuracion.get("categorias", ["Vivienda", "Servicios", "Transporte", "Alimentación", "Otros"])
    except:
        categorias_disponibles = ["Vivienda", "Servicios", "Transporte", "Alimentación", "Otros"]
    
    # Calcular total de gastos recurrentes (convertido a monto mensual)
    total_gastos_recurrentes = sum(
        calcular_monto_mensual(gasto.get("monto", 0), gasto.get("periodicidad", "Mensual")) 
        for gasto in gastos_recurrentes
    )
    
    # Mostrar métricas
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Gastos Recurrentes", config_manager.get_formatted_currency(total_gastos_recurrentes))
    with col2:
        st.metric("Cantidad de Gastos", len(gastos_recurrentes))
    
    st.divider()
    
    # Formulario para agregar nuevo gasto recurrente
    with st.expander("➕ Agregar Nuevo Gasto Recurrente", expanded=True):
        with st.form("nuevo_gasto_recurrente"):
            st.subheader("💳 Nuevo Gasto Recurrente")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                descripcion = st.text_input("📝 Descripción", placeholder="Ej: Renta, Luz, Agua, etc.")
            with col2:
                monto = st.number_input("💰 Monto", min_value=0.01, step=0.01, format="%.2f")
            with col3:
                periodicidad = st.selectbox("🔄 Periodicidad", ["Semanal", "Quincenal", "Mensual", "Bimestral", "Trimestral", "Anual"])
            with col4:
                categoria = st.selectbox("🏷️ Categoría", categorias_disponibles)
            
            if st.form_submit_button("➕ Agregar Gasto Recurrente", use_container_width=True):
                if descripcion and monto > 0:
                    # Validar que no exista un gasto con la misma descripción
                    gastos_existentes = st.session_state.get("gastos_recurrentes", [])
                    descripciones_existentes = [g.get("descripcion", "").lower() for g in gastos_existentes]
                    
                    if descripcion.lower() in descripciones_existentes:
                        st.error("❌ Ya existe un gasto recurrente con esa descripción")
                    else:
                        try:
                            nuevo_gasto = {
                                "descripcion": descripcion,
                                "monto": monto,
                                "periodicidad": periodicidad,
                                "categoria": categoria,
                                "monto_mensual": calcular_monto_mensual(monto, periodicidad),
                                "fecha_creacion": datetime.now().isoformat()
                            }
                            
                            if guardar_gasto_recurrente(nuevo_gasto):
                                st.success(f"✅ Gasto '{descripcion}' agregado exitosamente!")
                                # Pequeño delay para que se actualice la base de datos
                                time.sleep(0.5)
                                # Actualizar session state y recargar
                                gastos_recurrentes = cargar_gastos_recurrentes()
                                st.session_state["gastos_recurrentes"] = gastos_recurrentes
                                st.session_state["recargar_gastos"] = True
                                st.rerun()
                            else:
                                st.error("❌ Error al agregar el gasto recurrente")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                else:
                    st.error("❌ Por favor completa todos los campos")
    
    st.divider()
    
    # Lista de gastos recurrentes
    if gastos_recurrentes:
        st.subheader("📋 Gastos Recurrentes Actuales")
        
        for gasto in gastos_recurrentes:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    monto_original = gasto.get('monto', 0)
                    periodicidad = gasto.get('periodicidad', 'Mensual')
                    monto_mensual = calcular_monto_mensual(monto_original, periodicidad)
                    
                    st.write(f"💳 **{gasto.get('descripcion', 'Sin descripción')}**")
                    st.write(f"🏷️ {gasto.get('categoria', 'Sin categoría')}")
                    st.write(f"💰 {config_manager.get_formatted_currency(monto_original)} {periodicidad}")
                    st.write(f"📊 {config_manager.get_formatted_currency(monto_mensual)} mensual")
                
                with col2:
                    if st.button("🗑️", key=f"del_{gasto.get('id', '')}"):
                        if eliminar_gasto_recurrente(gasto.get('id', '')):
                            st.success(f"✅ Gasto '{gasto.get('descripcion', '')}' eliminado!")
                            # Pequeño delay para que se actualice la base de datos
                            time.sleep(0.5)
                            # Actualizar session state y recargar
                            gastos_recurrentes = cargar_gastos_recurrentes()
                            st.session_state["gastos_recurrentes"] = gastos_recurrentes
                            st.session_state["recargar_gastos"] = True
                            st.rerun()
                        else:
                            st.error("❌ Error al eliminar el gasto")
                
                with col3:
                    if st.button("✏️", key=f"edit_{gasto.get('id', '')}"):
                        st.session_state[f"editando_gasto_{gasto.get('id', '')}"] = True
                
                # Formulario de edición
                if st.session_state.get(f"editando_gasto_{gasto.get('id', '')}", False):
                    st.markdown("---")
                    st.subheader(f"✏️ Editando: {gasto.get('descripcion', '')}")
                    
                    with st.form(f"edit_gasto_{gasto.get('id', '')}"):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            nueva_descripcion = st.text_input("📝 Descripción", value=gasto.get('descripcion', ''), key=f"edit_desc_{gasto.get('id', '')}")
                        with col2:
                            nuevo_monto = st.number_input("💰 Monto", value=float(gasto.get('monto', 0)), min_value=0.01, step=0.01, format="%.2f", key=f"edit_monto_{gasto.get('id', '')}")
                        with col3:
                            nueva_periodicidad = st.selectbox("🔄 Periodicidad", ["Semanal", "Quincenal", "Mensual", "Bimestral", "Trimestral", "Anual"], 
                                                            index=["Semanal", "Quincenal", "Mensual", "Bimestral", "Trimestral", "Anual"].index(gasto.get('periodicidad', 'Mensual')), 
                                                            key=f"edit_period_{gasto.get('id', '')}")
                        with col4:
                            try:
                                categoria_index = categorias_disponibles.index(gasto.get('categoria', 'Otros'))
                            except ValueError:
                                categoria_index = 0
                            nueva_categoria = st.selectbox("🏷️ Categoría", categorias_disponibles, 
                                                        index=categoria_index, 
                                                        key=f"edit_cat_{gasto.get('id', '')}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
                                # Validar que no exista otro gasto con la misma descripción
                                gastos_existentes = st.session_state.get("gastos_recurrentes", [])
                                descripciones_existentes = [g.get("descripcion", "").lower() for g in gastos_existentes if g.get("id") != gasto.get('id', '')]
                                
                                if nueva_descripcion.lower() in descripciones_existentes:
                                    st.error("❌ Ya existe otro gasto recurrente con esa descripción")
                                else:
                                    try:
                                        datos_actualizados = {
                                            "descripcion": nueva_descripcion,
                                            "monto": nuevo_monto,
                                            "periodicidad": nueva_periodicidad,
                                            "categoria": nueva_categoria,
                                            "monto_mensual": calcular_monto_mensual(nuevo_monto, nueva_periodicidad)
                                        }
                                        
                                        if actualizar_gasto_recurrente(gasto.get('id', ''), datos_actualizados):
                                            st.success("✅ Gasto actualizado exitosamente!")
                                            st.session_state[f"editando_gasto_{gasto.get('id', '')}"] = False
                                            # Pequeño delay para que se actualice la base de datos
                                            time.sleep(0.5)
                                            # Actualizar session state y recargar
                                            gastos_recurrentes = cargar_gastos_recurrentes()
                                            st.session_state["gastos_recurrentes"] = gastos_recurrentes
                                            st.session_state["recargar_gastos"] = True
                                            st.rerun()
                                        else:
                                            st.error("❌ Error al actualizar el gasto")
                                    except Exception as e:
                                        st.error(f"❌ Error: {e}")
                        with col2:
                            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                st.session_state[f"editando_gasto_{gasto.get('id', '')}"] = False
                    st.markdown("---")
    else:
        st.info("No hay gastos recurrentes registrados. ¡Agrega uno para empezar!")
    
    # Información adicional
    st.info("💡 Los gastos recurrentes se suman automáticamente para calcular tu presupuesto mensual total.")
