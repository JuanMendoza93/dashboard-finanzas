"""
Página para gestión de cuentas bancarias
"""

import streamlit as st
from services.cuenta_service import CuentaService
from models.cuenta import Cuenta


def mostrar_cuentas():
    """Mostrar página de gestión de cuentas"""
    
    st.title("🏦 Gestión de Cuentas Bancarias")
    
    # Obtener cuentas
    cuentas = CuentaService.obtener_todas()
    
    # Mostrar saldo total
    saldo_total = CuentaService.calcular_saldo_total()
    st.write(f"💰 Saldo Total: ${saldo_total:,.2f}")
    
    st.divider()
    
    # Mostrar cuentas existentes
    if cuentas:
        st.subheader("📋 Cuentas Actuales")
        
        for cuenta in cuentas:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"🏦 **{cuenta.nombre}**: ${cuenta.saldo:,.2f}")
                
                with col2:
                    if st.button("🗑️", key=f"del_{cuenta.id}"):
                        if CuentaService.eliminar(cuenta.id):
                            st.success(f"✅ Cuenta '{cuenta.nombre}' eliminada!")
                            st.rerun()
                        else:
                            st.error("❌ Error al eliminar la cuenta")
                
                with col3:
                    if st.button("✏️", key=f"edit_{cuenta.id}"):
                        st.session_state[f"editando_cuenta_{cuenta.id}"] = True
                
                # Formulario de edición
                if st.session_state.get(f"editando_cuenta_{cuenta.id}", False):
                    st.markdown("---")
                    st.subheader(f"✏️ Editando: {cuenta.nombre}")
                    
                    with st.form(f"edit_form_{cuenta.id}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            nuevo_nombre = st.text_input("📝 Nombre de la Cuenta", value=cuenta.nombre, key=f"edit_nombre_{cuenta.id}")
                        with col2:
                            st.markdown("""
                            <style>
                            .custom-money-input-edit {
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                border: none;
                                border-radius: 12px;
                                padding: 15px 20px;
                                color: white;
                                font-size: 16px;
                                font-weight: 600;
                                text-align: right;
                                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                                transition: all 0.3s ease;
                                width: 100%;
                                box-sizing: border-box;
                            }
                            .custom-money-input-edit:focus {
                                outline: none;
                                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
                                transform: translateY(-2px);
                            }
                            .custom-money-input-edit::placeholder {
                                color: rgba(255,255,255,0.7);
                            }
                            .money-label-edit {
                                color: #2c3e50;
                                font-weight: 600;
                                margin-bottom: 8px;
                                font-size: 14px;
                            }
                            </style>
                            """, unsafe_allow_html=True)
                            
                            st.markdown('<div class="money-label-edit">💰 Saldo</div>', unsafe_allow_html=True)
                            saldo_texto = st.text_input("", value=f"{cuenta.saldo:.2f}", key=f"edit_saldo_{cuenta.id}", label_visibility="collapsed")
                            
                            try:
                                nuevo_saldo = float(saldo_texto) if saldo_texto else cuenta.saldo
                            except ValueError:
                                nuevo_saldo = cuenta.saldo
                                st.error("⚠️ Ingresa un valor numérico válido")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
                                if nuevo_nombre and (nuevo_nombre != cuenta.nombre or nuevo_saldo != cuenta.saldo):
                                    if CuentaService.actualizar(cuenta.id, nuevo_nombre, nuevo_saldo):
                                        st.success(f"✅ Cuenta '{nuevo_nombre}' actualizada exitosamente!")
                                        st.session_state[f"editando_cuenta_{cuenta.id}"] = False
                                        st.rerun()
                                    else:
                                        st.error("❌ Error al actualizar la cuenta. Verifica que el nombre no esté duplicado.")
                                else:
                                    st.warning("⚠️ No hay cambios para guardar")
                        with col2:
                            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                st.session_state[f"editando_cuenta_{cuenta.id}"] = False
                    st.markdown("---")
                
    else:
        st.info("No hay cuentas registradas")
    
    st.divider()
    
    # Formulario para agregar cuenta
    st.subheader("➕ Agregar Nueva Cuenta")
    
    with st.form("nueva_cuenta"):
        col1, col2 = st.columns(2)
        with col1:
            nombre_cuenta = st.text_input("📝 Nombre de la Cuenta")
        with col2:
            st.markdown("""
            <style>
            .custom-money-input {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                border-radius: 12px;
                padding: 15px 20px;
                color: white;
                font-size: 16px;
                font-weight: 600;
                text-align: right;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
                width: 100%;
                box-sizing: border-box;
            }
            .custom-money-input:focus {
                outline: none;
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
                transform: translateY(-2px);
            }
            .custom-money-input::placeholder {
                color: rgba(255,255,255,0.7);
            }
            .money-label {
                color: #2c3e50;
                font-weight: 600;
                margin-bottom: 8px;
                font-size: 14px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="money-label">💰 Saldo Inicial</div>', unsafe_allow_html=True)
            saldo_texto = st.text_input("", value="0.00", placeholder="0.00", key="saldo_inicial", label_visibility="collapsed")
            
            # Aplicar el estilo personalizado
            st.markdown(f"""
            <script>
            document.querySelector('input[data-testid="textInput"]').className = 'custom-money-input';
            </script>
            """, unsafe_allow_html=True)
            
            try:
                saldo_inicial = float(saldo_texto) if saldo_texto else 0.0
            except ValueError:
                saldo_inicial = 0.0
                st.error("⚠️ Ingresa un valor numérico válido")
        
        submitted = st.form_submit_button("➕ Agregar Cuenta", use_container_width=True)
        
        if submitted:
            if nombre_cuenta:
                try:
                    cuenta = CuentaService.crear(nombre_cuenta, saldo_inicial)
                    if cuenta:
                        st.success(f"✅ Cuenta '{nombre_cuenta}' agregada exitosamente!")
                        # No usar st.rerun() para evitar ciclo infinito
                    else:
                        st.error("❌ Error al crear la cuenta. Verifica que el nombre no esté duplicado.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.error("❌ Por favor ingresa un nombre para la cuenta")