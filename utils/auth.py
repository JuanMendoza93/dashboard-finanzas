import streamlit as st
from config.firebase_config import firebase_config

def iniciar_sesion():
    st.title("Iniciar Sesión")
    
    # Para desarrollo, usamos autenticación simple
    st.info("Modo de desarrollo - Autenticación simplificada")
    
    email = st.text_input("Correo")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar Sesión"):
        if email and password:
            # Simulamos autenticación exitosa
            st.session_state["user"] = {
                "email": email,
                "uid": "dev_user_123"
            }
            st.success("¡Sesión iniciada correctamente!")
            st.rerun()
        else:
            st.error("Por favor, ingresa email y contraseña")
