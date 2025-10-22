"""
Página para gestión de configuraciones del sistema
"""

import streamlit as st
from utils.config_manager import config_manager, financial_config, ui_config
from utils.helpers import show_success_message, show_error_message, show_info_message
from utils.validators import data_validator


def mostrar_configuracion():
    """Mostrar página de configuración del sistema"""
    
    st.title("⚙️ Configuración del Sistema")
    
    # Tabs para diferentes tipos de configuración
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💰 Financiero", 
        "🎨 Interfaz", 
        "✅ Validaciones", 
        "📊 Reportes", 
        "🔧 Avanzado"
    ])
    
    with tab1:
        mostrar_configuracion_financiera()
    
    with tab2:
        mostrar_configuracion_ui()
    
    with tab3:
        mostrar_configuracion_validaciones()
    
    with tab4:
        mostrar_configuracion_reportes()
    
    with tab5:
        mostrar_configuracion_avanzada()


def mostrar_configuracion_financiera():
    """Mostrar configuración financiera"""
    st.subheader("💰 Configuración Financiera")
    
    # Obtener valores actuales
    presupuesto_base = financial_config.get_presupuesto_base()
    meta_mensual = financial_config.get_meta_mensual()
    meta_anual = financial_config.get_meta_anual()
    moneda = financial_config.get_moneda()
    decimales = financial_config.get_decimales()
    
    with st.form("config_financiera"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Presupuesto y Metas**")
            nuevo_presupuesto = st.number_input(
                "💵 Presupuesto Base Mensual",
                value=presupuesto_base,
                min_value=0.0,
                step=100.0,
                help="Presupuesto base mensual para gastos"
            )
            
            nueva_meta_mensual = st.number_input(
                "🎯 Meta de Ahorro Mensual",
                value=meta_mensual,
                min_value=0.0,
                step=100.0,
                help="Meta de ahorro mensual"
            )
            
            nueva_meta_anual = st.number_input(
                "🎯 Meta de Ahorro Anual",
                value=meta_anual,
                min_value=0.0,
                step=1000.0,
                help="Meta de ahorro anual"
            )
        
        with col2:
            st.write("**Formato de Moneda**")
            nueva_moneda = st.selectbox(
                "💱 Símbolo de Moneda",
                options=["USD", "EUR", "MXN", "COP", "ARS"],
                index=["USD", "EUR", "MXN", "COP", "ARS"].index(moneda) if moneda in ["USD", "EUR", "MXN", "COP", "ARS"] else 0
            )
            
            nuevos_decimales = st.selectbox(
                "🔢 Decimales",
                options=[0, 1, 2, 3],
                index=decimales if decimales in [0, 1, 2, 3] else 2
            )
            
            st.write("**Vista Previa**")
            st.code(f"Formato: {config_manager.get_formatted_currency(1234.56)}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Guardar Configuración", use_container_width=True):
                try:
                    # Validar datos
                    if nuevo_presupuesto < 0 or nueva_meta_mensual < 0 or nueva_meta_anual < 0:
                        show_error_message("Los valores no pueden ser negativos")
                    else:
                        # Guardar configuración
                        financial_config.set_presupuesto_base(nuevo_presupuesto)
                        financial_config.set_meta_mensual(nueva_meta_mensual)
                        financial_config.set_meta_anual(nueva_meta_anual)
                        config_manager.set_config("finances.moneda", nueva_moneda)
                        config_manager.set_config("finances.decimales", nuevos_decimales)
                        
                        show_success_message("Configuración financiera guardada exitosamente!")
                        st.rerun()
                except Exception as e:
                    show_error_message(f"Error guardando configuración: {e}")
        
        with col2:
            if st.form_submit_button("🔄 Restaurar Valores", use_container_width=True):
                config_manager.reset_to_default()
                show_info_message("Configuración restaurada a valores por defecto")
                st.rerun()


def mostrar_configuracion_ui():
    """Mostrar configuración de interfaz"""
    st.subheader("🎨 Configuración de Interfaz")
    
    # Obtener configuración actual
    tema = ui_config.get_tema()
    colores = ui_config.get_colores()
    items_por_pagina = ui_config.get_items_por_pagina()
    mostrar_graficos = ui_config.should_show_charts()
    
    with st.form("config_ui"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Tema y Colores**")
            nuevo_tema = st.selectbox(
                "🎨 Tema",
                options=["light", "dark", "auto"],
                index=["light", "dark", "auto"].index(tema) if tema in ["light", "dark", "auto"] else 0
            )
            
            st.write("**Colores Personalizados**")
            color_primario = st.color_picker(
                "Color Primario",
                value=colores.get("primario", "#667eea")
            )
            color_secundario = st.color_picker(
                "Color Secundario", 
                value=colores.get("secundario", "#764ba2")
            )
        
        with col2:
            st.write("**Configuración de Visualización**")
            nuevos_items = st.number_input(
                "📄 Items por Página",
                value=items_por_pagina,
                min_value=5,
                max_value=50,
                step=5
            )
            
            mostrar_graficos_nuevo = st.checkbox(
                "📊 Mostrar Gráficos",
                value=mostrar_graficos
            )
            
            st.write("**Vista Previa de Colores**")
            st.markdown(f"""
            <div style="display: flex; gap: 10px;">
                <div style="width: 50px; height: 30px; background-color: {color_primario}; border-radius: 5px;"></div>
                <div style="width: 50px; height: 30px; background-color: {color_secundario}; border-radius: 5px;"></div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.form_submit_button("💾 Guardar Configuración UI", use_container_width=True):
            try:
                config_manager.update_config({
                    "ui": {
                        "tema": nuevo_tema,
                        "colores": {
                            "primario": color_primario,
                            "secundario": color_secundario,
                            "exito": colores.get("exito", "#28a745"),
                            "advertencia": colores.get("advertencia", "#ffc107"),
                            "peligro": colores.get("peligro", "#dc3545")
                        },
                        "metricas": {
                            "items_por_pagina": nuevos_items,
                            "mostrar_graficos": mostrar_graficos_nuevo
                        }
                    }
                })
                show_success_message("Configuración de interfaz guardada!")
                st.rerun()
            except Exception as e:
                show_error_message(f"Error guardando configuración UI: {e}")


def mostrar_configuracion_validaciones():
    """Mostrar configuración de validaciones"""
    st.subheader("✅ Configuración de Validaciones")
    
    # Obtener configuración actual
    validaciones = config_manager.get_validation_config()
    
    with st.form("config_validaciones"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Límites de Montos**")
            monto_minimo = st.number_input(
                "💰 Monto Mínimo",
                value=validaciones.get("monto_minimo", 0.01),
                min_value=0.0,
                step=0.01
            )
            
            monto_maximo = st.number_input(
                "💰 Monto Máximo",
                value=validaciones.get("monto_maximo", 999999.99),
                min_value=0.0,
                step=100.0
            )
        
        with col2:
            st.write("**Límites de Texto**")
            nombre_min = st.number_input(
                "📝 Longitud Mínima Nombre",
                value=validaciones.get("nombre_min_length", 2),
                min_value=1,
                max_value=10
            )
            
            nombre_max = st.number_input(
                "📝 Longitud Máxima Nombre",
                value=validaciones.get("nombre_max_length", 50),
                min_value=10,
                max_value=100
            )
        
        if st.form_submit_button("💾 Guardar Validaciones", use_container_width=True):
            try:
                config_manager.update_config({
                    "validaciones": {
                        "monto_minimo": monto_minimo,
                        "monto_maximo": monto_maximo,
                        "nombre_min_length": nombre_min,
                        "nombre_max_length": nombre_max,
                        "concepto_min_length": validaciones.get("concepto_min_length", 3),
                        "concepto_max_length": validaciones.get("concepto_max_length", 100)
                    }
                })
                show_success_message("Configuración de validaciones guardada!")
                st.rerun()
            except Exception as e:
                show_error_message(f"Error guardando validaciones: {e}")


def mostrar_configuracion_reportes():
    """Mostrar configuración de reportes"""
    st.subheader("📊 Configuración de Reportes")
    
    # Obtener configuración actual
    reportes = config_manager.get_report_config()
    
    with st.form("config_reportes"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Formato de Datos**")
            formato_fecha = st.selectbox(
                "📅 Formato de Fecha",
                options=["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y"],
                index=0
            )
            
            formato_moneda = st.selectbox(
                "💰 Formato de Moneda",
                options=["${:,.2f}", "€{:,.2f}", "₱{:,.2f}", "{:,.2f} USD"],
                index=0
            )
        
        with col2:
            st.write("**Configuración de Exportación**")
            formato_exportacion = st.selectbox(
                "📁 Formato de Exportación",
                options=["excel", "csv", "pdf"],
                index=0
            )
            
            st.write("**Vista Previa**")
            from datetime import datetime
            fecha_ejemplo = datetime.now()
            st.code(f"Fecha: {fecha_ejemplo.strftime(formato_fecha)}")
            st.code(f"Moneda: {formato_moneda.format(1234.56)}")
        
        if st.form_submit_button("💾 Guardar Configuración de Reportes", use_container_width=True):
            try:
                config_manager.update_config({
                    "reportes": {
                        "formato_fecha": formato_fecha,
                        "formato_moneda": formato_moneda,
                        "exportar_formato": formato_exportacion,
                        "graficos_por_defecto": reportes.get("graficos_por_defecto", [])
                    }
                })
                show_success_message("Configuración de reportes guardada!")
                st.rerun()
            except Exception as e:
                show_error_message(f"Error guardando configuración de reportes: {e}")


def mostrar_configuracion_avanzada():
    """Mostrar configuración avanzada"""
    st.subheader("🔧 Configuración Avanzada")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Sincronización con Firebase**")
        if st.button("🔄 Sincronizar con Firebase", use_container_width=True):
            if config_manager.sync_with_firebase():
                show_success_message("Sincronización exitosa!")
            else:
                show_error_message("Error en la sincronización")
        
        if st.button("💾 Guardar en Firebase", use_container_width=True):
            if config_manager.save_to_firebase():
                show_success_message("Configuración guardada en Firebase!")
            else:
                show_error_message("Error guardando en Firebase")
    
    with col2:
        st.write("**Gestión de Configuración**")
        if st.button("🔄 Restaurar Configuración", use_container_width=True):
            if config_manager.reset_to_default():
                show_success_message("Configuración restaurada!")
                st.rerun()
            else:
                show_error_message("Error restaurando configuración")
        
        st.write("**Información del Sistema**")
        app_info = config_manager.get_app_info()
        st.code(f"""
        Aplicación: {app_info.get('name', 'N/A')}
        Versión: {app_info.get('version', 'N/A')}
        """)
    
    # Mostrar configuración actual
    st.subheader("📋 Configuración Actual")
    if st.button("👁️ Ver Configuración Completa"):
        config_completa = config_manager.get_config()
        st.json(config_completa)
