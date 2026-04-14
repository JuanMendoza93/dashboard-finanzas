"""
Gestión de Cuentas Bancarias
Página para administrar cuentas bancarias
"""

import streamlit as st
from services.cuenta_service import CuentaService
from utils.database import cargar_configuracion
from utils.config_manager import config_manager
from utils.helpers import apply_css_styles


def main():
    """Función principal de la página de cuentas"""
    
    # Aplicar CSS personalizado
    apply_css_styles()
    
    # Navegación lateral personalizada
    from utils.helpers import mostrar_navegacion_lateral
    mostrar_navegacion_lateral()
    
    st.title("🏦 Gestión de Cuentas Bancarias")
    
    # Cargar configuración
    configuracion = cargar_configuracion()
    
    # Saldo total al inicio con indicador de color (verde >= 100,000 / rojo < 100,000)
    cuentas = CuentaService.obtener_todas()
    saldo_total = sum(c.saldo for c in cuentas) if cuentas else 0
    es_verde = saldo_total >= 100_000
    icono_saldo = "💚" if es_verde else "🔴"
    bg_saldo = "#d4edda" if es_verde else "#f8d7da"
    border_saldo = "#28a745" if es_verde else "#dc3545"
    text_saldo = "#155724" if es_verde else "#721c24"
    st.markdown(f"""
    <div style="
        background: {bg_saldo};
        border: 2px solid {border_saldo};
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0 1.5rem 0;
    ">
        <h3 style="color: {text_saldo}; margin: 0;">{icono_saldo} Saldo Total</h3>
        <h2 style="color: {text_saldo}; margin: 0.5rem 0;">{config_manager.get_formatted_currency(saldo_total)}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar cuentas existentes
    mostrar_cuentas()
    
    # Formulario para agregar nueva cuenta (colapsado por defecto)
    st.divider()
    
    with st.expander("➕ Agregar Nueva Cuenta", expanded=False):
        with st.form("nueva_cuenta"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre_cuenta = st.text_input("🏦 Nombre de la Cuenta", placeholder="Ej: Cuenta Corriente, Ahorros, etc.")
            
            with col2:
                saldo_inicial = st.text_input("💰 Saldo Inicial", placeholder="0.00", help="Ingresa el saldo inicial de la cuenta")
            
            col3, col4 = st.columns(2)
            with col3:
                rendimiento_anual = st.text_input("📈 Rendimiento Anual (%)", placeholder="Ej: 15", help="Porcentaje anual estimado")
            with col4:
                limite = st.text_input("🚫 Límite", placeholder="0.00", help="Límite o tope asociado a la cuenta")
            
            if st.form_submit_button("💾 Crear Cuenta", use_container_width=True):
                if nombre_cuenta and saldo_inicial:
                    try:
                        saldo_float = float(saldo_inicial)
                        # Parsear opcionales
                        rendimiento_val = float(rendimiento_anual) if rendimiento_anual else 0.0
                        limite_val = float(limite) if limite else 0.0
                        cuenta = CuentaService.crear(nombre_cuenta, saldo_float, rendimiento_val, limite_val)
                        if cuenta:
                            st.success(f"✅ Cuenta '{nombre_cuenta}' creada exitosamente!")
                            st.rerun()
                        else:
                            st.error("❌ Error al crear la cuenta. Verifica que el nombre no esté duplicado.")
                    except ValueError:
                        st.error("❌ Por favor ingresa un saldo válido (solo números)")
                else:
                    st.error("❌ Por favor completa todos los campos")


def mostrar_cuentas():
    """Mostrar lista de cuentas con opciones de edición y eliminación"""
    
    st.subheader("📋 Cuentas Registradas")
    
    # Obtener cuentas
    cuentas = CuentaService.obtener_todas()
    
    if not cuentas:
        st.info("No hay cuentas registradas. Agrega una nueva cuenta arriba.")
        return
    
    # Mostrar cuentas en columnas
    cols = st.columns(3)
    
    for i, cuenta in enumerate(cuentas):
        with cols[i % 3]:
            with st.container():
                st.markdown(f"""
                <div style="border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin: 5px 0;">
                    <h4>🏦 {cuenta.nombre}</h4>
                    <p><strong>Saldo:</strong> {config_manager.get_formatted_currency(cuenta.saldo)}</p>
                    <p><strong>Rendimiento anual:</strong> {cuenta.rendimiento_anual}%</p>
                    <p><strong>Límite:</strong> {config_manager.get_formatted_currency(cuenta.limite)}</p>
                    <p><strong>Proyección 15 días:</strong> {config_manager.get_formatted_currency(CuentaService.proyectar_siguiente_quincena(cuenta.saldo, cuenta.rendimiento_anual))}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Botones de acción
                col_edit, col_del = st.columns(2)
                
                with col_edit:
                    if st.button("✏️", key=f"edit_{cuenta.id}", use_container_width=True):
                        st.session_state[f"editando_cuenta_{cuenta.id}"] = True
                
                with col_del:
                    if st.button("🗑️", key=f"del_{cuenta.id}", use_container_width=True):
                        if CuentaService.eliminar(cuenta.id):
                            # Limpiar caché explícitamente antes del rerun
                            CuentaService._obtener_todas_cached.clear()
                            st.cache_data.clear()
                            st.success(f"✅ Cuenta '{cuenta.nombre}' eliminada!")
                            st.rerun()
                        else:
                            st.error("❌ Error al eliminar la cuenta")
                
                # Formulario de edición (se muestra si está en modo edición)
                if st.session_state.get(f"editando_cuenta_{cuenta.id}", False):
                    st.markdown("---")
                    st.subheader(f"✏️ Editando: {cuenta.nombre}")
                    
                    with st.form(f"edit_cuenta_{cuenta.id}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            nuevo_nombre = st.text_input("Nombre", value=cuenta.nombre, key=f"nombre_{cuenta.id}")
                        
                        with col2:
                            nuevo_saldo = st.text_input("Saldo", value=str(cuenta.saldo), key=f"saldo_{cuenta.id}")

                        col3, col4 = st.columns(2)
                        with col3:
                            nuevo_rend = st.text_input("Rendimiento Anual (%)", value=str(cuenta.rendimiento_anual), key=f"rend_{cuenta.id}")
                        with col4:
                            nuevo_lim = st.text_input("Límite", value=str(cuenta.limite), key=f"lim_{cuenta.id}")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.form_submit_button("💾 Guardar", use_container_width=True):
                                try:
                                    saldo_float = float(nuevo_saldo)
                                    rend_val = float(nuevo_rend) if nuevo_rend else 0.0
                                    lim_val = float(nuevo_lim) if nuevo_lim else 0.0
                                    if CuentaService.actualizar(cuenta.id, nuevo_nombre, saldo_float, rend_val, lim_val):
                                        # Limpiar caché explícitamente antes del rerun
                                        CuentaService._obtener_todas_cached.clear()
                                        st.cache_data.clear()
                                        st.success("✅ Cuenta actualizada exitosamente!")
                                        st.session_state[f"editando_cuenta_{cuenta.id}"] = False
                                        st.rerun()
                                    else:
                                        st.error("❌ Error al actualizar. Verifica que el nombre no esté duplicado.")
                                except ValueError:
                                    st.error("❌ Por favor ingresa un saldo válido")
                        
                        with col2:
                            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                st.session_state[f"editando_cuenta_{cuenta.id}"] = False
                                st.rerun()


if __name__ == "__main__":
    main()