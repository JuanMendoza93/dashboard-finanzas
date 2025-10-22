"""
Página para gestión de movimientos financieros
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
from services.movimiento_service import MovimientoService
from services.cuenta_service import CuentaService
from utils.database import cargar_configuracion
from utils.helpers import show_fullscreen_loading, hide_fullscreen_loading
import time


def mostrar_movimientos():
    """Mostrar página de gestión de movimientos"""
    
    st.title("💰 Gestión de Movimientos Financieros")
    
    # Sin loading que se atasca
    
    # Manejar recarga de movimientos
    if st.session_state.get("recargar_movimientos", False):
        st.session_state["recargar_movimientos"] = False
        st.cache_data.clear()
    
    # Obtener datos
    movimientos = MovimientoService.obtener_todos()
    configuracion = cargar_configuracion()
    
    # Mostrar métricas
    ahora = datetime.now()
    gastos_mes = MovimientoService.calcular_gastos_mes(ahora.month, ahora.year)
    ingresos_mes = MovimientoService.calcular_ingresos_mes(ahora.month, ahora.year)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💸 Gastos del Mes", f"${gastos_mes:,.2f}")
    with col2:
        st.metric("💰 Ingresos del Mes", f"${ingresos_mes:,.2f}")
    with col3:
        balance = ingresos_mes - gastos_mes
        st.metric("📊 Balance del Mes", f"${balance:,.2f}")
    
    st.divider()
    
    # Formulario para agregar movimiento
    with st.expander("➕ Agregar Nuevo Movimiento", expanded=True):
        with st.form("nuevo_movimiento"):
            col1, col2 = st.columns(2)
            with col1:
                fecha = st.date_input("📅 Fecha", value=date.today())
                concepto = st.text_input("📝 Concepto")
                categoria = st.selectbox("🏷️ Categoría", configuracion["categorias"])
            with col2:
                tipo_gasto = st.selectbox("🔍 Tipo de Gasto", configuracion["tipos_gasto"])
                monto = st.number_input("💰 Monto", min_value=0.0, step=0.01)
                tipo = st.radio("📊 Tipo", ["Gasto", "Ingreso"])
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                submitted = st.form_submit_button("💾 Guardar", use_container_width=True)
            with col2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state["mostrar_formulario"] = False
                    st.rerun()
            
            if submitted:
                if concepto and monto > 0:
                    # Verificar duplicados directamente aquí
                    movimientos_existentes = MovimientoService.obtener_todos()
                    es_duplicado = False
                    
                    for mov in movimientos_existentes:
                        if (mov.fecha == fecha and 
                            mov.concepto.lower().strip() == concepto.lower().strip() and 
                            abs(mov.monto - monto) < 0.01):
                            es_duplicado = True
                            break
                    
                    if es_duplicado:
                        st.error("❌ Ya existe un movimiento con la misma fecha, concepto y monto")
                    else:
                        # Solo crear si no es duplicado
                        movimiento = MovimientoService.crear(
                            fecha, concepto, categoria, tipo_gasto, monto, tipo
                        )
                        if movimiento:
                            st.success("✅ Movimiento guardado exitosamente!")
                            # Limpiar cache y recargar
                            st.cache_data.clear()
                            st.session_state["recargar_movimientos"] = True
                            # Cerrar el formulario
                            st.session_state["mostrar_formulario"] = False
                            st.rerun()
                        else:
                            st.error("❌ Error al guardar el movimiento")
                else:
                    st.error("❌ Por favor completa todos los campos")
    
    # Botón de recargar movimientos eliminado - se recarga automáticamente
    
    # Filtro por mes
    st.subheader("📅 Filtro por Mes")
    col1, col2 = st.columns(2)
    
    with col1:
        mes_seleccionado = st.selectbox(
            "Seleccionar mes:",
            options=list(range(1, 13)),
            index=ahora.month - 1,
            format_func=lambda x: [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ][x-1]
        )
    
    with col2:
        año_seleccionado = st.selectbox(
            "Seleccionar año:",
            options=list(range(ahora.year - 2, ahora.year + 2)),
            index=2  # Año actual
        )
    
    st.divider()
    
    # Mostrar movimientos
    if movimientos:
        st.subheader(f"📋 Movimientos de {['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][mes_seleccionado-1]} {año_seleccionado}")
        
        # Filtrar movimientos del mes seleccionado y ordenar por fecha (más recientes primero)
        movimientos_mes = [m for m in movimientos if m.fecha.month == mes_seleccionado and m.fecha.year == año_seleccionado]
        movimientos_mes.sort(key=lambda x: x.fecha, reverse=True)
        
        if movimientos_mes:
            # CSS para reducir interlineado
            st.markdown("""
            <style>
            .compact-table {
                line-height: 1.0 !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            .compact-table .stMarkdown {
                margin: 0 !important;
                padding: 0 !important;
            }
            .compact-table p {
                margin: 0 !important;
                padding: 0 !important;
                line-height: 1.0 !important;
            }
            .compact-table .stButton {
                margin: 0 !important;
                padding: 0 !important;
            }
            .compact-table .stButton > button {
                padding: 0.2rem 0.4rem !important;
                font-size: 0.8rem !important;
                margin: 0 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Crear DataFrame para la tabla
            df_data = []
            for movimiento in movimientos_mes:
                # Manejar tanto objetos Movimiento como diccionarios
                if isinstance(movimiento, dict):
                    fecha_str = movimiento.get("fecha", "")
                    concepto = movimiento.get("concepto", "")
                    categoria = movimiento.get("categoria", "")
                    tipo = movimiento.get("tipo", "")
                    monto = movimiento.get("monto", 0)
                    tipo_gasto = movimiento.get("tipo_gasto", "")
                    movimiento_id = movimiento.get("id", "")
                else:
                    fecha_str = movimiento.fecha.strftime("%d/%m/%Y")
                    concepto = movimiento.concepto
                    categoria = movimiento.categoria
                    tipo = movimiento.tipo
                    monto = movimiento.monto
                    tipo_gasto = movimiento.tipo_gasto
                    movimiento_id = movimiento.id
                
                df_data.append({
                    "Fecha": fecha_str,
                    "Concepto": concepto,
                    "Categoría": categoria,
                    "Tipo": tipo,
                    "Monto": f"${monto:,.2f}",
                    "Tipo de Gasto": tipo_gasto,
                    "ID": movimiento_id
                })
            
            # Mostrar tabla compacta con botones en cada fila
            df = pd.DataFrame(df_data)
            # Ocultar la columna ID
            df_display = df.drop(columns=['ID'])
            
            # Crear tabla personalizada con botones
            for i, movimiento in enumerate(movimientos_mes):
                with st.container():
                    st.markdown('<div class="compact-table">', unsafe_allow_html=True)
                    col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 2, 1, 1, 1, 1, 1])
                
                # Manejar tanto objetos Movimiento como diccionarios
                if isinstance(movimiento, dict):
                    fecha_str = movimiento.get("fecha", "")
                    concepto = movimiento.get("concepto", "")
                    categoria = movimiento.get("categoria", "")
                    tipo = movimiento.get("tipo", "")
                    monto = movimiento.get("monto", 0)
                    tipo_gasto = movimiento.get("tipo_gasto", "")
                    movimiento_id = movimiento.get("id", "")
                else:
                    fecha_str = movimiento.fecha.strftime("%d/%m/%Y")
                    concepto = movimiento.concepto
                    categoria = movimiento.categoria
                    tipo = movimiento.tipo
                    monto = movimiento.monto
                    tipo_gasto = movimiento.tipo_gasto
                    movimiento_id = movimiento.id
                
                with col1:
                    st.write(f"**{fecha_str}**")
                
                with col2:
                    st.write(f"**{concepto}**")
                
                with col3:
                    st.write(f"{categoria}")
                
                with col4:
                    st.write(f"{tipo}")
                
                with col5:
                    st.write(f"**${monto:,.2f}**")
                
                with col6:
                    st.write(f"{tipo_gasto}")
                
                with col7:
                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        if st.button("✏️", key=f"edit_{movimiento_id}", help="Editar"):
                            st.session_state[f"editando_movimiento_{movimiento_id}"] = True
                    with col_del:
                        if st.button("🗑️", key=f"del_{movimiento_id}", help="Eliminar"):
                            if MovimientoService.eliminar(movimiento_id):
                                st.success(f"✅ Movimiento eliminado!")
                                st.session_state["recargar_movimientos"] = True
                                st.rerun()
                            else:
                                st.error("❌ Error al eliminar el movimiento")
                
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Separador entre filas (más delgado)
                if i < len(movimientos_mes) - 1:
                    st.markdown("<hr style='margin: 2px 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
            
            # Formulario de edición (se muestra si hay algún movimiento en edición)
            movimiento_en_edicion = None
            for movimiento in movimientos_mes:
                # Obtener ID del movimiento
                if isinstance(movimiento, dict):
                    movimiento_id = movimiento.get("id", "")
                else:
                    movimiento_id = movimiento.id
                
                if st.session_state.get(f"editando_movimiento_{movimiento_id}", False):
                    movimiento_en_edicion = movimiento
                    break
            
            if movimiento_en_edicion:
                # Obtener datos del movimiento en edición
                if isinstance(movimiento_en_edicion, dict):
                    fecha_edicion = movimiento_en_edicion.get("fecha", "")
                    concepto_edicion = movimiento_en_edicion.get("concepto", "")
                    categoria_edicion = movimiento_en_edicion.get("categoria", "")
                    tipo_edicion = movimiento_en_edicion.get("tipo", "")
                    monto_edicion = movimiento_en_edicion.get("monto", 0)
                    tipo_gasto_edicion = movimiento_en_edicion.get("tipo_gasto", "")
                    movimiento_id_edicion = movimiento_en_edicion.get("id", "")
                else:
                    fecha_edicion = movimiento_en_edicion.fecha.strftime("%d/%m/%Y")
                    concepto_edicion = movimiento_en_edicion.concepto
                    categoria_edicion = movimiento_en_edicion.categoria
                    tipo_edicion = movimiento_en_edicion.tipo
                    monto_edicion = movimiento_en_edicion.monto
                    tipo_gasto_edicion = movimiento_en_edicion.tipo_gasto
                    movimiento_id_edicion = movimiento_en_edicion.id
                
                # Convertir fecha al formato correcto para date_input
                if isinstance(movimiento_en_edicion, dict):
                    # Si es diccionario, la fecha ya está en formato ISO
                    fecha_para_input = datetime.fromisoformat(fecha_edicion).date()
                else:
                    # Si es objeto, usar la fecha directamente
                    fecha_para_input = movimiento_en_edicion.fecha
                
                st.markdown("---")
                st.subheader(f"✏️ Editando: {concepto_edicion}")
                
                with st.form(f"edit_movimiento_{movimiento_id_edicion}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nueva_fecha = st.date_input("📅 Fecha", value=fecha_para_input, key=f"edit_fecha_{movimiento_id_edicion}")
                        nuevo_concepto = st.text_input("📝 Concepto", value=concepto_edicion, key=f"edit_concepto_{movimiento_id_edicion}")
                        nueva_categoria = st.selectbox("🏷️ Categoría", configuracion["categorias"], index=configuracion["categorias"].index(categoria_edicion) if categoria_edicion in configuracion["categorias"] else 0, key=f"edit_categoria_{movimiento_id_edicion}")
                    with col2:
                        nuevo_tipo_gasto = st.selectbox("🔍 Tipo de Gasto", configuracion["tipos_gasto"], index=configuracion["tipos_gasto"].index(tipo_gasto_edicion) if tipo_gasto_edicion in configuracion["tipos_gasto"] else 0, key=f"edit_tipo_gasto_{movimiento_id_edicion}")
                        nuevo_monto = st.number_input("💰 Monto", value=float(monto_edicion), min_value=0.0, step=0.01, key=f"edit_monto_{movimiento_id_edicion}")
                        nuevo_tipo = st.radio("📊 Tipo", ["Gasto", "Ingreso"], index=0 if tipo_edicion == "Gasto" else 1, key=f"edit_tipo_{movimiento_id_edicion}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
                            # Crear objeto de datos actualizados
                            datos_actualizados = {
                                "fecha": nueva_fecha.isoformat(),
                                "concepto": nuevo_concepto,
                                "categoria": nueva_categoria,
                                "tipo_gasto": nuevo_tipo_gasto,
                                "monto": nuevo_monto,
                                "tipo": nuevo_tipo
                            }
                            
                            # Actualizar en Firebase
                            if MovimientoService.actualizar(movimiento_id_edicion, datos_actualizados):
                                st.success("✅ Movimiento actualizado exitosamente!")
                                st.session_state[f"editando_movimiento_{movimiento_id_edicion}"] = False
                                # Forzar recarga para mostrar cambios
                                st.session_state["recargar_movimientos"] = True
                                st.rerun()
                            else:
                                st.error("❌ Error al actualizar el movimiento")
                    
                    with col2:
                        if st.form_submit_button("❌ Cancelar", use_container_width=True):
                            st.session_state[f"editando_movimiento_{movimiento_id_edicion}"] = False
                st.markdown("---")
        else:
            st.info("ℹ️ No hay movimientos para el mes actual")
    else:
        st.info("ℹ️ No hay movimientos registrados")
    
    # Mostrar TOP 3 gastos del mes seleccionado
    st.subheader(f"🔥 TOP 3 Categorías con Más Gastos - {['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][mes_seleccionado-1]} {año_seleccionado}")
    
    # Calcular TOP 3 gastos del mes seleccionado
    if movimientos:
        # Filtrar solo gastos del mes seleccionado
        gastos_mes = [m for m in movimientos if m.fecha.month == mes_seleccionado and m.fecha.year == año_seleccionado and m.es_gasto]
        
        if gastos_mes:
            # Agrupar por categoría y sumar montos
            gastos_por_categoria = {}
            for gasto in gastos_mes:
                categoria = gasto.categoria
                if categoria not in gastos_por_categoria:
                    gastos_por_categoria[categoria] = 0
                gastos_por_categoria[categoria] += gasto.monto_absoluto
            
            # Convertir a lista y ordenar por monto
            top_categorias = []
            for categoria, total in gastos_por_categoria.items():
                top_categorias.append({
                    "categoria": categoria,
                    "total": total
                })
            
            # Ordenar por total descendente y tomar los primeros 3
            top_categorias.sort(key=lambda x: x["total"], reverse=True)
            top_3 = top_categorias[:3]
            
            if top_3:
                for i, gasto in enumerate(top_3, 1):
                    st.write(f"**#{i}** 🏷️ {gasto['categoria']} - ${gasto['total']:,.2f}")
            else:
                st.info("ℹ️ No hay gastos registrados para este mes")
        else:
            st.info("ℹ️ No hay gastos registrados para este mes")
    else:
        st.info("ℹ️ No hay movimientos registrados")
