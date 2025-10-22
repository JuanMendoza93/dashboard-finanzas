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
    
    # Mostrar cuentas existentes
    mostrar_cuentas()
    
    # Formulario para agregar nueva cuenta
    st.divider()
    st.subheader("➕ Agregar Nueva Cuenta")
    
    with st.form("nueva_cuenta"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_cuenta = st.text_input("🏦 Nombre de la Cuenta", placeholder="Ej: Cuenta Corriente, Ahorros, etc.")
        
        with col2:
            saldo_inicial = st.text_input("💰 Saldo Inicial", placeholder="0.00", help="Ingresa el saldo inicial de la cuenta")
        
        if st.form_submit_button("💾 Crear Cuenta", use_container_width=True):
            if nombre_cuenta and saldo_inicial:
                try:
                    saldo_float = float(saldo_inicial)
                    cuenta = CuentaService.crear(nombre_cuenta, saldo_float)
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
                    <p><strong>Saldo:</strong> {config_manager.get_formatted_currency(cuenta.saldo)}</p></p>
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
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.form_submit_button("💾 Guardar", use_container_width=True):
                                try:
                                    saldo_float = float(nuevo_saldo)
                                    if CuentaService.actualizar(cuenta.id, nuevo_nombre, saldo_float):
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