"""
Registro de Comidas
Página para registrar comidas consumidas
"""

import streamlit as st
from datetime import date, datetime
from services.registro_nutricional_service import RegistroNutricionalService
from services.nutricion_api_service import NutricionAPIService
from services.comida_service import ComidaService
from models.comida import Comida
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
    
    # Formulario para agregar comida
    st.subheader("➕ Agregar Comida")
    
    with st.expander("🍽️ Agregar Comida con Descripción Natural", expanded=True):
        with st.form("nueva_comida_natural"):
            st.markdown("**💡 Escribe tu comida en lenguaje natural:**")
            st.markdown("*Ejemplo: 'Hoy desayuné un omelet con jamón, 100g de frijoles refritos, un plátano y café sin azúcar'*")
            
            # Información sobre APIs de nutrición
            from services.nutricion_api_service import NutricionAPIService
            tiene_edamam = NutricionAPIService.EDAMAM_APP_ID and NutricionAPIService.EDAMAM_APP_KEY
            tiene_nutritionix = NutricionAPIService.NUTRITIONIX_APP_ID and NutricionAPIService.NUTRITIONIX_API_KEY
            
            if tiene_edamam:
                st.success("✅ **Edamam API activa** - Valores nutricionales precisos desde API gratuita")
            elif tiene_nutritionix:
                st.info("✅ **Nutritionix API activa** - Valores nutricionales desde API")
            else:
                st.warning("💡 **Tip:** Configura Edamam API (gratuita) en el archivo `.env` para obtener valores nutricionales precisos automáticamente.\n\nVer: `CONFIGURAR_API_NUTRICION.md`")
            
            descripcion_completa = st.text_area(
                "📝 Descripción de la comida:",
                placeholder="Ej: Omelet con jamón, 100g de frijoles refritos, un plátano y café sin azúcar",
                height=100
            )
            
            momento = st.selectbox(
                "🕐 Momento del día:",
                ["Desayuno", "Almuerzo", "Cena", "Snacks"],
                index=0
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("🔍 Parsear y Agregar", use_container_width=True):
                    if descripcion_completa:
                        with st.spinner("🔍 Parseando descripción..."):
                            try:
                                # Parsear descripción completa
                                alimentos = NutricionAPIService.parsear_comida_completa(descripcion_completa)
                                
                                if alimentos and len(alimentos) > 0:
                                    alimentos_guardados = 0
                                    alimentos_con_error = 0
                                    alimentos_sin_api = 0
                                    alimentos_con_valores = 0
                                    
                                    # Verificar si hay API configurada
                                    tiene_edamam = NutricionAPIService.EDAMAM_APP_ID and NutricionAPIService.EDAMAM_APP_KEY
                                    tiene_nutritionix = NutricionAPIService.NUTRITIONIX_APP_ID and NutricionAPIService.NUTRITIONIX_API_KEY
                                    tiene_api = tiene_edamam or tiene_nutritionix
                                    
                                    # Agregar cada alimento al registro
                                    for alimento in alimentos:
                                        try:
                                            # Verificar si el alimento necesita API
                                            necesita_api = alimento.get("necesita_api", False)
                                            tiene_valores = alimento.get("calorias", 0) > 0
                                            
                                            if necesita_api and not tiene_api:
                                                alimentos_sin_api += 1
                                            elif tiene_valores:
                                                alimentos_con_valores += 1
                                            
                                            comida_data = {
                                                "nombre": alimento.get("nombre", "Comida sin nombre"),
                                                "calorias": alimento.get("calorias", 0),
                                                "proteinas": alimento.get("proteinas", 0),
                                                "carbohidratos": alimento.get("carbohidratos", 0),
                                                "grasas": alimento.get("grasas", 0),
                                                "cantidad": alimento.get("cantidad", 100.0),
                                                "unidad": alimento.get("unidad", "g"),
                                                "descripcion": alimento.get("descripcion", descripcion_completa),
                                                "momento": momento
                                            }
                                            
                                            if RegistroNutricionalService.agregar_comida(fecha_seleccionada, comida_data):
                                                alimentos_guardados += 1
                                            else:
                                                alimentos_con_error += 1
                                        except Exception as e:
                                            st.error(f"❌ Error al guardar alimento: {e}")
                                            alimentos_con_error += 1
                                    
                                    if alimentos_guardados > 0:
                                        mensaje = f"✅ {alimentos_guardados} alimento(s) agregado(s) correctamente"
                                        
                                        if alimentos_sin_api > 0:
                                            st.error(f"❌ **API no configurada:** {alimentos_sin_api} alimento(s) no tienen valores nutricionales porque no hay API configurada.")
                                            st.warning("⚠️ **Configura Edamam API (gratuita)** para obtener valores nutricionales precisos.\n\nVer: `CONFIGURAR_API_NUTRICION.md`")
                                        elif alimentos_con_valores < alimentos_guardados:
                                            st.warning(f"⚠️ Algunos alimentos no tienen valores nutricionales. Configura una API para obtenerlos automáticamente.")
                                        
                                        if alimentos_con_error > 0:
                                            st.warning(f"⚠️ {alimentos_con_error} alimento(s) no se pudieron guardar")
                                        
                                        st.success(mensaje)
                                        st.rerun()
                                    else:
                                        st.error("❌ No se pudieron guardar los alimentos. Verifica la conexión a la base de datos.")
                                else:
                                    st.warning("⚠️ No se pudieron identificar alimentos. Intenta ser más específico o usa el formulario manual.")
                            except Exception as e:
                                st.error(f"❌ Error al parsear la descripción: {e}")
                                st.info("💡 **Tip:** Intenta usar el formulario manual si el parseo automático no funciona.")
                    else:
                        st.error("❌ Por favor ingresa una descripción")
            
            with col2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.rerun()
    
    st.divider()
    
    # Formulario para agregar comida manual
    with st.expander("✏️ Agregar Comida Manualmente", expanded=False):
        with st.form("nueva_comida_manual"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("🍽️ Nombre de la comida")
                momento = st.selectbox(
                    "🕐 Momento:",
                    ["Desayuno", "Almuerzo", "Cena", "Snacks"],
                    key="momento_manual"
                )
                cantidad = st.number_input("📏 Cantidad", min_value=0.0, step=0.1, value=100.0)
                unidad = st.selectbox("📐 Unidad", ["g", "ml", "oz", "unidad"], index=0)
            
            with col2:
                calorias = st.number_input("🔥 Calorías", min_value=0.0, step=0.1, value=0.0)
                proteinas = st.number_input("🥩 Proteínas (g)", min_value=0.0, step=0.1, value=0.0)
                carbohidratos = st.number_input("🍞 Carbohidratos (g)", min_value=0.0, step=0.1, value=0.0)
                grasas = st.number_input("🧈 Grasas (g)", min_value=0.0, step=0.1, value=0.0)
            
            if st.form_submit_button("💾 Guardar Comida", use_container_width=True):
                if nombre and calorias >= 0:
                    comida_data = {
                        "nombre": nombre,
                        "calorias": calorias,
                        "proteinas": proteinas,
                        "carbohidratos": carbohidratos,
                        "grasas": grasas,
                        "cantidad": cantidad,
                        "unidad": unidad,
                        "descripcion": nombre,
                        "momento": momento
                    }
                    
                    if RegistroNutricionalService.agregar_comida(fecha_seleccionada, comida_data):
                        st.success("✅ Comida agregada correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al agregar la comida")
                else:
                    st.error("❌ Por favor completa todos los campos requeridos")
    
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

