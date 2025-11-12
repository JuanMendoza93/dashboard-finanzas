"""
Registro de Comidas
Página para registrar comidas consumidas
"""

import streamlit as st
from datetime import date, datetime
from services.registro_nutricional_service import RegistroNutricionalService
from utils.helpers import apply_css_styles
from utils.config_manager import config_manager


def main():
    """Función principal de registro de comidas"""
    
    # Aplicar CSS personalizado
    apply_css_styles()
    
    # Establecer página actual nutricional
    st.session_state["pagina_nutricional_actual"] = "registro"
    
    # Navegación lateral personalizada
    from utils.helpers import mostrar_navegacion_lateral
    mostrar_navegacion_lateral()
    
    st.title("🍽️ Registro de Comidas")
    
    # Selector de fecha
    fecha_seleccionada = st.date_input(
        "📅 Fecha",
        value=date.today(),
        key="fecha_registro_comida"
    )
    
    # Limpiar caché si hay cambios en la fecha
    if "ultima_fecha_registro" not in st.session_state or st.session_state["ultima_fecha_registro"] != fecha_seleccionada:
        RegistroNutricionalService._obtener_por_fecha_cached.clear()
        st.session_state["ultima_fecha_registro"] = fecha_seleccionada
    
    # Obtener registro del día
    registro_dia = RegistroNutricionalService.obtener_por_fecha(fecha_seleccionada)
    
    st.divider()
    
    # Formulario para agregar comida - VERSIÓN SIMPLIFICADA (colapsado por defecto)
    with st.expander("➕ Agregar Comida", expanded=False):
        st.markdown("💡 **Ingresa las calorías que consumiste.** Puedes investigar los valores nutricionales por tu cuenta.")
        
        # Formulario simplificado principal
        with st.form("nueva_comida_simple", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input(
                    "🍽️ Nombre de la comida *",
                    placeholder="Ej: Omelet con jamón y queso",
                    help="Nombre descriptivo de lo que comiste"
                )
                momento = st.selectbox(
                    "🕐 Momento del día *",
                    ["Desayuno", "Almuerzo", "Cena", "Snacks"],
                    index=0
                )
            
            with col2:
                calorias = st.number_input(
                    "🔥 Calorías *",
                    min_value=0.0,
                    step=1.0,
                    value=0.0,
                    help="Total de calorías de esta comida"
                )
                
                # Macronutrientes opcionales (colapsados)
                # Inicializar con valores por defecto
                proteinas = 0.0
                carbohidratos = 0.0
                grasas = 0.0
                
                with st.expander("📊 Macronutrientes (Opcional)", expanded=False):
                    proteinas = st.number_input("🥩 Proteínas (g)", min_value=0.0, step=0.1, value=0.0, key="proteinas_simple")
                    carbohidratos = st.number_input("🍞 Carbohidratos (g)", min_value=0.0, step=0.1, value=0.0, key="carbohidratos_simple")
                    grasas = st.number_input("🧈 Grasas (g)", min_value=0.0, step=0.1, value=0.0, key="grasas_simple")
            
            # Botón de guardar
            if st.form_submit_button("💾 Guardar Comida", use_container_width=True):
                if nombre and nombre.strip() and calorias > 0:
                    comida_data = {
                        "nombre": nombre.strip(),
                        "calorias": float(calorias),
                        "proteinas": float(proteinas),
                        "carbohidratos": float(carbohidratos),
                        "grasas": float(grasas),
                        "cantidad": 100.0,  # Valor por defecto
                        "unidad": "g",
                        "descripcion": nombre.strip(),
                        "momento": momento
                    }
                    
                    if RegistroNutricionalService.agregar_comida(fecha_seleccionada, comida_data):
                        st.success(f"✅ **{nombre}** agregado correctamente ({calorias:.0f} cal)")
                        # Limpiar caché para asegurar que se vean los datos actualizados
                        RegistroNutricionalService._obtener_por_fecha_cached.clear()
                        # Marcar que hay datos nuevos para que el dashboard se actualice automáticamente
                        st.session_state["datos_nutricionales_actualizados"] = True
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar la comida. Verifica la conexión a la base de datos.")
                elif not nombre or not nombre.strip():
                    st.error("❌ Por favor ingresa el nombre de la comida")
                elif calorias <= 0:
                    st.error("❌ Por favor ingresa las calorías (debe ser mayor a 0)")
    
    st.divider()
    
    # Mostrar comidas del día
    st.subheader(f"📋 Comidas de {fecha_seleccionada.strftime('%d/%m/%Y')}")
    
    if registro_dia and registro_dia.comidas:
        # Agrupar por momento
        momentos = ["Desayuno", "Almuerzo", "Cena", "Snacks"]
        
        for momento in momentos:
            comidas_momento = [c for c in registro_dia.comidas if c.get("momento") == momento]
            
            if comidas_momento:
                st.markdown(f"**{momento}**")
                
                for i, comida in enumerate(comidas_momento):
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
                        
                        with col1:
                            st.write(f"**{comida.get('nombre', 'Sin nombre')}**")
                            if comida.get('cantidad'):
                                st.caption(f"{comida.get('cantidad', 0):.1f} {comida.get('unidad', 'g')}")
                        
                        with col2:
                            st.write(f"🔥 {comida.get('calorias', 0):.0f} cal")
                        
                        with col3:
                            st.write(f"🥩 {comida.get('proteinas', 0):.1f}g")
                        
                        with col4:
                            st.write(f"🍞 {comida.get('carbohidratos', 0):.1f}g")
                        
                        with col5:
                            if st.button("🗑️", key=f"del_{fecha_seleccionada}_{i}"):
                                # Encontrar índice en la lista completa
                                idx = registro_dia.comidas.index(comida)
                                if RegistroNutricionalService.eliminar_comida(fecha_seleccionada, idx):
                                    st.success("✅ Comida eliminada")
                                    st.rerun()
                        
                        if i < len(comidas_momento) - 1:
                            st.divider()
                
                st.divider()
        
        # Resumen del día
        st.subheader("📊 Resumen del Día")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔥 Total Calorías", f"{registro_dia.total_calorias:.0f}")
        with col2:
            st.metric("🥩 Proteínas", f"{registro_dia.total_proteinas:.1f}g")
        with col3:
            st.metric("🍞 Carbohidratos", f"{registro_dia.total_carbohidratos:.1f}g")
        with col4:
            st.metric("🧈 Grasas", f"{registro_dia.total_grasas:.1f}g")
    else:
        st.info("No hay comidas registradas para este día. ¡Agrega tu primera comida!")


if __name__ == "__main__":
    main()

