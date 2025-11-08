"""
Metas Nutricionales
Página para configurar metas calóricas y nutricionales
"""

import streamlit as st
from datetime import date, datetime
from services.meta_calorica_service import MetaCaloricaService
from models.meta_calorica import MetaCalorica
from utils.helpers import apply_css_styles


def main():
    """Función principal de metas nutricionales"""
    
    # Aplicar CSS personalizado
    apply_css_styles()
    
    # Establecer página actual nutricional
    st.session_state["pagina_nutricional_actual"] = "metas"
    
    # Navegación lateral personalizada
    from utils.helpers import mostrar_navegacion_lateral
    mostrar_navegacion_lateral()
    
    st.title("🎯 Metas Nutricionales")
    
    # Obtener meta actual
    meta_actual = MetaCaloricaService.obtener_meta_actual()
    
    st.divider()
    
    # Formulario para crear/actualizar meta
    st.subheader("📝 Configurar Meta Calórica")
    
    with st.form("meta_calorica"):
        col1, col2 = st.columns(2)
        
        with col1:
            calorias_diarias = st.number_input(
                "🔥 Calorías Diarias",
                min_value=0.0,
                step=50.0,
                value=meta_actual.calorias_diarias if meta_actual else 2000.0,
                help="Calorías totales que necesitas consumir diariamente"
            )
            
            deficit_calorico = st.number_input(
                "📉 Déficit Calórico",
                min_value=0.0,
                step=50.0,
                value=meta_actual.deficit_calorico if meta_actual else 0.0,
                help="Calorías que quieres reducir para perder peso"
            )
        
        with col2:
            proteinas_objetivo = st.number_input(
                "🥩 Proteínas Objetivo (g)",
                min_value=0.0,
                step=5.0,
                value=meta_actual.proteinas_objetivo if meta_actual else 0.0,
                help="Gramos de proteínas objetivo por día"
            )
            
            carbohidratos_objetivo = st.number_input(
                "🍞 Carbohidratos Objetivo (g)",
                min_value=0.0,
                step=5.0,
                value=meta_actual.carbohidratos_objetivo if meta_actual else 0.0,
                help="Gramos de carbohidratos objetivo por día"
            )
        
        grasas_objetivo = st.number_input(
            "🧈 Grasas Objetivo (g)",
            min_value=0.0,
            step=5.0,
            value=meta_actual.grasas_objetivo if meta_actual else 0.0,
            help="Gramos de grasas objetivo por día"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input(
                "📅 Fecha de Inicio",
                value=meta_actual.fecha_inicio if meta_actual else date.today()
            )
        
        with col2:
            fecha_fin = st.date_input(
                "📅 Fecha de Fin (Opcional)",
                value=meta_actual.fecha_fin if meta_actual else None,
                help="Dejar vacío para meta indefinida"
            )
        
        if st.form_submit_button("💾 Guardar Meta", use_container_width=True):
            # Crear o actualizar meta
            meta = MetaCalorica(
                calorias_diarias=calorias_diarias,
                deficit_calorico=deficit_calorico,
                proteinas_objetivo=proteinas_objetivo,
                carbohidratos_objetivo=carbohidratos_objetivo,
                grasas_objetivo=grasas_objetivo,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin if fecha_fin else None
            )
            
            if MetaCaloricaService.guardar_meta(meta):
                st.success("✅ Meta guardada correctamente")
                st.rerun()
            else:
                st.error("❌ Error al guardar la meta")
    
    st.divider()
    
    # Mostrar meta actual
    if meta_actual:
        st.subheader("📊 Meta Actual")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🔥 Calorías Diarias",
                f"{meta_actual.calorias_diarias:.0f}"
            )
        
        with col2:
            st.metric(
                "📉 Déficit Calórico",
                f"{meta_actual.deficit_calorico:.0f}"
            )
        
        with col3:
            st.metric(
                "🎯 Calorías Objetivo",
                f"{meta_actual.calorias_objetivo:.0f}"
            )
        
        with col4:
            st.metric(
                "📅 Fecha de Inicio",
                meta_actual.fecha_inicio.strftime("%d/%m/%Y")
            )
        
        if meta_actual.proteinas_objetivo > 0 or meta_actual.carbohidratos_objetivo > 0 or meta_actual.grasas_objetivo > 0:
            st.subheader("🥧 Macros Objetivo")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🥩 Proteínas", f"{meta_actual.proteinas_objetivo:.1f}g")
            with col2:
                st.metric("🍞 Carbohidratos", f"{meta_actual.carbohidratos_objetivo:.1f}g")
            with col3:
                st.metric("🧈 Grasas", f"{meta_actual.grasas_objetivo:.1f}g")
    else:
        st.info("No hay meta configurada. ¡Crea tu primera meta!")


if __name__ == "__main__":
    main()

