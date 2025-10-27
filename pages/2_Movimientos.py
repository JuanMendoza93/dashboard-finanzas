"""
Gestión de Movimientos Financieros
Página para administrar ingresos y gastos
"""

import streamlit as st
from datetime import date, datetime
from services.movimiento_service import MovimientoService
from models.movimiento import Movimiento
from utils.database import cargar_configuracion
from utils.config_manager import config_manager
from utils.helpers import apply_css_styles


def main():
    """Función principal de la página de movimientos"""
    
    # Aplicar CSS personalizado
    apply_css_styles()
    
    # Navegación lateral personalizada
    from utils.helpers import mostrar_navegacion_lateral
    mostrar_navegacion_lateral()
    
    st.title("💰 Gestión de Movimientos")
    
    # Cargar configuración
    configuracion = cargar_configuracion()
    
    st.divider()
    
    # Filtros por mes y año
    st.subheader("📅 Filtros")
    col1, col2 = st.columns(2)
    
    with col1:
        # Crear lista de meses con nombres
        nombres_meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        mes_seleccionado = st.selectbox("Mes", nombres_meses, index=date.today().month - 1)
        # Convertir nombre a número para el procesamiento
        mes_seleccionado = nombres_meses.index(mes_seleccionado) + 1
    
    with col2:
        año_seleccionado = st.selectbox("Año", list(range(2020, 2030)), index=date.today().year - 2020)
    
    # Mover el formulario después de definir las variables
    st.divider()
    
    # Formulario colapsable para agregar nuevo movimiento
    with st.expander("➕ Agregar Nuevo Movimiento", expanded=False):
        with st.form("nuevo_movimiento"):
            col1, col2 = st.columns(2)
            
            with col1:
                concepto = st.text_input("📝 Concepto")
                fecha = st.date_input("📅 Fecha", value=date.today())
                monto = st.number_input("💰 Monto", min_value=0.0, step=0.01, format="%.2f")

            with col2:
                categoria = st.selectbox("📂 Categoría", configuracion["categorias"])
                tipo_gasto = st.selectbox("🔍 Tipo de Gasto", configuracion["tipos_gasto"])
                tipo = st.radio("📊 Tipo", ["Gasto", "Ingreso", "Pago"])
            
            st.divider()
            
            # Botones para agregar nuevas opciones (dentro del formulario)
            st.markdown("**🔧 ¿Necesitas agregar nuevas opciones?**")
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.form_submit_button("➕ Nueva Categoría", help="Agregar nueva categoría", use_container_width=True):
                    st.session_state["agregando_categoria"] = True
            with col_btn2:
                if st.form_submit_button("➕ Nuevo Tipo de Gasto", help="Agregar nuevo tipo de gasto", use_container_width=True):
                    st.session_state["agregando_tipo_gasto"] = True
            
            st.divider()
            
            if st.form_submit_button("💾 Guardar Movimiento", use_container_width=True):
                if concepto and monto > 0:
                    # Validar duplicados
                    movimientos_existentes = MovimientoService.obtener_por_mes(mes_seleccionado, año_seleccionado)
                    duplicado = any(
                        m.fecha == fecha and m.concepto == concepto and m.monto == monto
                        for m in movimientos_existentes
                    )
                    
                    if duplicado:
                        st.error("❌ Ya existe un movimiento con la misma fecha, concepto y monto")
                    else:
                        # Crear movimiento
                        movimiento = MovimientoService.crear(
                            fecha=fecha,
                            concepto=concepto,
                            categoria=categoria,
                            tipo_gasto=tipo_gasto,
                            monto=monto,
                            tipo=tipo
                        )
                        
                        if movimiento:
                            st.success("✅ Movimiento agregado correctamente")
                            st.rerun()
                        else:
                            st.error("❌ Error al agregar el movimiento")
                else:
                    st.error("❌ Por favor completa todos los campos")
    
    # Formularios para agregar nuevas categorías y tipos de gasto
    if st.session_state.get("agregando_categoria", False):
        st.markdown("---")
        st.subheader("➕ Agregar Nueva Categoría")
        with st.form("nueva_categoria"):
            nueva_categoria = st.text_input("📂 Nombre de la nueva categoría", placeholder="Ej: Entretenimiento, Salud, etc.")
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Agregar Categoría", use_container_width=True):
                    if nueva_categoria and nueva_categoria not in configuracion["categorias"]:
                        # Agregar a la configuración
                        configuracion["categorias"].append(nueva_categoria)
                        from utils.database import guardar_configuracion
                        if guardar_configuracion(configuracion):
                            st.success(f"✅ Categoría '{nueva_categoria}' agregada correctamente")
                            st.session_state["agregando_categoria"] = False
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar la categoría")
                    elif nueva_categoria in configuracion["categorias"]:
                        st.error("❌ Esta categoría ya existe")
                    else:
                        st.error("❌ Por favor ingresa un nombre válido")
            with col2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state["agregando_categoria"] = False
                    st.rerun()
    
    if st.session_state.get("agregando_tipo_gasto", False):
        st.markdown("---")
        st.subheader("➕ Agregar Nuevo Tipo de Gasto")
        with st.form("nuevo_tipo_gasto"):
            nuevo_tipo_gasto = st.text_input("🔍 Nombre del nuevo tipo de gasto", placeholder="Ej: Emergencia, Inversión, etc.")
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Agregar Tipo de Gasto", use_container_width=True):
                    if nuevo_tipo_gasto and nuevo_tipo_gasto not in configuracion["tipos_gasto"]:
                        # Agregar a la configuración
                        configuracion["tipos_gasto"].append(nuevo_tipo_gasto)
                        from utils.database import guardar_configuracion
                        if guardar_configuracion(configuracion):
                            st.success(f"✅ Tipo de gasto '{nuevo_tipo_gasto}' agregado correctamente")
                            st.session_state["agregando_tipo_gasto"] = False
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar el tipo de gasto")
                    elif nuevo_tipo_gasto in configuracion["tipos_gasto"]:
                        st.error("❌ Este tipo de gasto ya existe")
                    else:
                        st.error("❌ Por favor ingresa un nombre válido")
            with col2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state["agregando_tipo_gasto"] = False
                    st.rerun()
    
    # Mostrar movimientos del mes seleccionado
    mostrar_movimientos(mes_seleccionado, año_seleccionado, configuracion)


def mostrar_movimientos(mes, año, configuracion):
    """Mostrar movimientos del mes con opciones de edición y eliminación"""
    
    # Convertir número de mes a nombre
    nombres_meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    
    nombre_mes = nombres_meses.get(mes, f"Mes {mes}")
    st.subheader(f"📋 Movimientos de {nombre_mes} de {año}")
    
    # Obtener movimientos del mes
    movimientos_mes = MovimientoService.obtener_por_mes(mes, año)
    
    if not movimientos_mes:
        st.info("No hay movimientos registrados para este mes.")
        return
    
    # Ordenar por fecha descendente
    movimientos_mes.sort(key=lambda x: x.fecha, reverse=True)
    
    pagos_recibidos = sum(m.monto for m in movimientos_mes if m.tipo == "Pago")
    total_gastos = sum(m.monto for m in movimientos_mes if m.tipo == "Gasto") - pagos_recibidos
    total_ingresos = sum(m.monto for m in movimientos_mes if m.tipo == "Ingreso")
    saldo_mes = total_ingresos - total_gastos
    
    # Mostrar resumen de totales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "💸 Total Gastos",
            config_manager.get_formatted_currency(total_gastos),
            delta=None
        )
    
    with col2:
        st.metric(
            "💰 Total Ingresos", 
            config_manager.get_formatted_currency(total_ingresos),
            delta=None
        )
    
    with col3:
        st.metric(
            "📈 Saldo del Mes",
            config_manager.get_formatted_currency(saldo_mes),
            delta=None
        )
    
    st.divider()
    
    # Filtros para la tabla de movimientos
    st.markdown("**🔍 Filtrar por tipo:**")
    col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)
    
    with col_filtro1:
        mostrar_todos = st.button("📋 Todos", use_container_width=True)
        if mostrar_todos or "filtro_tipo_movimiento" not in st.session_state:
            st.session_state["filtro_tipo_movimiento"] = "todos"
    
    with col_filtro2:
        mostrar_gastos = st.button("💸 Gastos", use_container_width=True)
        if mostrar_gastos:
            st.session_state["filtro_tipo_movimiento"] = "gastos"
    
    with col_filtro3:
        mostrar_ingresos = st.button("💰 Ingresos", use_container_width=True)
        if mostrar_ingresos:
            st.session_state["filtro_tipo_movimiento"] = "ingresos"
    
    with col_filtro4:
        mostrar_pagos = st.button("💳 Pagos", use_container_width=True)
        if mostrar_pagos:
            st.session_state["filtro_tipo_movimiento"] = "pagos"
    
    # Aplicar filtro
    filtro_tipo = st.session_state.get("filtro_tipo_movimiento", "todos")
    
    if filtro_tipo == "gastos":
        movimientos_mes = [m for m in movimientos_mes if m.tipo == "Gasto"]
    elif filtro_tipo == "ingresos":
        movimientos_mes = [m for m in movimientos_mes if m.tipo == "Ingreso"]
    elif filtro_tipo == "pagos":
        movimientos_mes = [m for m in movimientos_mes if m.tipo == "Pago"]
    
    st.divider()
    
    # CSS para mejorar la tabla de movimientos (más ancha y legible)
    st.markdown("""
    <style>
    .movements-table {
        line-height: 1.3 !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
    }
    .movements-table .stMarkdown {
        margin: 0 !important;
        padding: 0.5rem 0.3rem !important;
        word-wrap: break-word !important;
    }
    .movements-table p {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.3 !important;
        font-size: 1rem !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    .movements-table .stButton {
        margin: 0 !important;
        padding: 0 !important;
    }
    .movements-table .stButton > button {
        padding: 0.4rem 0.8rem !important;
        font-size: 0.9rem !important;
        margin: 0 !important;
        min-height: 2.2rem !important;
        min-width: 2.5rem !important;
    }
    .movements-table .stColumn {
        padding: 0.4rem !important;
        min-width: 0 !important;
    }
    .movements-table .stColumn:first-child {
        min-width: 120px !important;
    }
    .movements-table .stColumn:nth-child(2) {
        min-width: 200px !important;
    }
    .movements-table .stColumn:last-child {
        min-width: 100px !important;
    }
    .main .block-container {
        max-width: 98% !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Crear tabla personalizada con botones (más ancha)
    for i, movimiento in enumerate(movimientos_mes):
        with st.container():
            st.markdown('<div class="movements-table">', unsafe_allow_html=True)
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 4, 2, 2, 2, 2, 2])
            
            with col1:
                st.write(f"**{movimiento.fecha.strftime('%d/%m/%Y')}**")
            
            with col2:
                st.write(f"**{movimiento.concepto}**")
            
            with col3:
                st.write(f"{movimiento.categoria}")
            
            with col4:
                st.write(f"{movimiento.tipo}")
            
            with col5:
                st.write(f"**${movimiento.monto:,.2f}**")
            
            with col6:
                st.write(f"{movimiento.tipo_gasto}")
            
            with col7:
                col_edit, col_del = st.columns(2)
                with col_edit:
                    if st.button("✏️", key=f"edit_{movimiento.id}", help="Editar"):
                        st.session_state[f"editando_movimiento_{movimiento.id}"] = True
                with col_del:
                    if st.button("🗑️", key=f"del_{movimiento.id}", help="Eliminar"):
                        if MovimientoService.eliminar(movimiento.id):
                            st.success(f"✅ Movimiento eliminado!")
                            st.rerun()
                        else:
                            st.error("❌ Error al eliminar el movimiento")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Separador entre filas
            if i < len(movimientos_mes) - 1:
                st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
    
    # Formulario de edición (se muestra si hay algún movimiento en edición)
    movimiento_en_edicion = None
    for movimiento in movimientos_mes:
        if st.session_state.get(f"editando_movimiento_{movimiento.id}", False):
            movimiento_en_edicion = movimiento
            break
    
    if movimiento_en_edicion:
        st.markdown("---")
        st.subheader(f"✏️ Editando: {movimiento_en_edicion.concepto}")
        
        with st.form(f"edit_movimiento_{movimiento_en_edicion.id}"):
            col1, col2 = st.columns(2)
            with col1:
                nueva_fecha = st.date_input("📅 Fecha", value=movimiento_en_edicion.fecha, key=f"edit_fecha_{movimiento_en_edicion.id}")
                nuevo_concepto = st.text_input("📝 Concepto", value=movimiento_en_edicion.concepto, key=f"edit_concepto_{movimiento_en_edicion.id}")
                nueva_categoria = st.selectbox("🏷️ Categoría", configuracion["categorias"], 
                                            index=configuracion["categorias"].index(movimiento_en_edicion.categoria) 
                                            if movimiento_en_edicion.categoria in configuracion["categorias"] else 0, 
                                            key=f"edit_categoria_{movimiento_en_edicion.id}")
            with col2:
                nuevo_tipo_gasto = st.selectbox("🔍 Tipo de Gasto", configuracion["tipos_gasto"], 
                                             index=configuracion["tipos_gasto"].index(movimiento_en_edicion.tipo_gasto) 
                                             if movimiento_en_edicion.tipo_gasto in configuracion["tipos_gasto"] else 0, 
                                             key=f"edit_tipo_gasto_{movimiento_en_edicion.id}")
                nuevo_monto = st.number_input("💰 Monto", value=float(movimiento_en_edicion.monto), 
                                           min_value=0.0, step=0.01, key=f"edit_monto_{movimiento_en_edicion.id}")
                nuevo_tipo = st.radio("📊 Tipo", ["Gasto", "Ingreso", "Pago"], 
                                    index=0 if movimiento_en_edicion.tipo == "Gasto" else (1 if movimiento_en_edicion.tipo == "Ingreso" else 2), 
                                    key=f"edit_tipo_{movimiento_en_edicion.id}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
                    datos_actualizados = {
                        "fecha": nueva_fecha.isoformat(),
                        "concepto": nuevo_concepto,
                        "categoria": nueva_categoria,
                        "tipo_gasto": nuevo_tipo_gasto,
                        "monto": nuevo_monto,
                        "tipo": nuevo_tipo
                    }
                    
                    if MovimientoService.actualizar(movimiento_en_edicion.id, datos_actualizados):
                        st.success("✅ Movimiento actualizado exitosamente!")
                        st.session_state[f"editando_movimiento_{movimiento_en_edicion.id}"] = False
                        st.rerun()
                    else:
                        st.error("❌ Error al actualizar el movimiento")
            
            with col2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state[f"editando_movimiento_{movimiento_en_edicion.id}"] = False
                    st.rerun()


if __name__ == "__main__":
    main()