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
    
    # Mostrar meta actual primero
    if meta_actual:
        st.subheader("📊 Meta Actual")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🔥 Calorías Semanales",
                f"{meta_actual.calorias_semanales:.0f}"
            )
            st.caption(f"({meta_actual.calorias_diarias:.0f} cal/día)")
        
        with col2:
            st.metric(
                "📉 Déficit Calórico Semanal",
                f"{meta_actual.deficit_calorico:.0f}"
            )
        
        with col3:
            st.metric(
                "🎯 Calorías Objetivo Semanal",
                f"{meta_actual.calorias_objetivo_semanal:.0f}"
            )
            st.caption(f"({meta_actual.calorias_objetivo:.0f} cal/día)")
        
        with col4:
            st.metric(
                "📅 Fecha de Inicio",
                meta_actual.fecha_inicio.strftime("%d/%m/%Y")
            )
            st.caption("(Lunes de la semana)")
        
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
    
    st.divider()
    
    # Formulario para crear/actualizar meta (SEMANAL) - Colapsado
    with st.expander("📝 Configurar Meta Calórica Semanal", expanded=False):
        st.info("💡 La meta es **semanal** (Lunes a Domingo). Si no configuras una nueva, se usará la de la semana anterior.")
        
        with st.form("meta_calorica"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Calcular calorías diarias desde semanal si existe
                calorias_diarias_base = (meta_actual.calorias_diarias if meta_actual else 2000.0)
                calorias_diarias = st.number_input(
                    "🔥 Calorías Diarias",
                    min_value=0.0,
                    step=50.0,
                    value=calorias_diarias_base,
                    help="Calorías que quieres consumir por día"
                )
                
                # Calcular automáticamente las calorías semanales
                calorias_semanales = calorias_diarias * 7
                st.info(f"📊 **Calorías Semanales:** {calorias_semanales:.0f} cal (calculado automáticamente)")
                
                # Calcular TMB y TDEE para sugerir déficit
                from utils.metabolismo_helper import obtener_tmb_usuario, calcular_tdee
                tmb = obtener_tmb_usuario()
                
                # Campo para nivel de actividad
                nivel_actividad = st.selectbox(
                    "🏃 Nivel de Actividad Física",
                    ["sedentario", "ligera", "moderada", "intensa", "muy_intensa"],
                    index=0,  # Sedentario por defecto
                    format_func=lambda x: {
                        "sedentario": "Sedentario (poco o nada de ejercicio)",
                        "ligera": "Ligera (ejercicio ligero 1-3 días/semana)",
                        "moderada": "Moderada (ejercicio moderado 3-5 días/semana)",
                        "intensa": "Intensa (ejercicio intenso 6-7 días/semana)",
                        "muy_intensa": "Muy Intensa (ejercicio muy intenso, trabajo físico)"
                    }[x],
                    help="Tu nivel de actividad física para calcular necesidades calóricas"
                )
                
                # Calcular TDEE si hay TMB
                deficit_calorico = 0.0  # Inicializar variable
                
                if tmb:
                    tdee = calcular_tdee(tmb, nivel_actividad)
                    st.info(f"🔥 **TMB:** {tmb:.0f} cal/día | **TDEE:** {tdee:.0f} cal/día")
                    
                    # Calcular déficit sugerido (20% del TDEE es un déficit saludable)
                    deficit_sugerido_diario = tdee * 0.20
                    deficit_sugerido_semanal = deficit_sugerido_diario * 7
                    
                    # Calcular déficit automático basado en la diferencia entre TDEE y calorías diarias
                    if calorias_diarias < tdee:
                        deficit_calorico_auto = (tdee - calorias_diarias) * 7
                    else:
                        deficit_calorico_auto = 0.0
                    
                    st.info(f"💡 **Déficit Sugerido:** {deficit_sugerido_semanal:.0f} cal/semana (20% del TDEE)")
                    
                    if deficit_calorico_auto > 0:
                        st.success(f"✅ **Déficit Calculado Automáticamente:** {deficit_calorico_auto:.0f} cal/semana")
                        # Mostrar el déficit calculado pero permitir edición
                        deficit_calorico = st.number_input(
                            "📉 Déficit Calórico Semanal (Calculado)",
                            min_value=0.0,
                            step=100.0,
                            value=deficit_calorico_auto,
                            help="Calorías que quieres reducir semanalmente para perder peso (calculado automáticamente)"
                        )
                    else:
                        deficit_calorico = st.number_input(
                            "📉 Déficit Calórico Semanal",
                            min_value=0.0,
                            step=100.0,
                            value=deficit_sugerido_semanal,
                            help="Calorías que quieres reducir semanalmente para perder peso"
                        )
                else:
                    st.warning("⚠️ No se pudo calcular tu TMB. Asegúrate de tener peso y altura registrados.")
                    deficit_calorico = st.number_input(
                        "📉 Déficit Calórico Semanal",
                        min_value=0.0,
                        step=100.0,
                        value=meta_actual.deficit_calorico if meta_actual else 0.0,
                        help="Calorías que quieres reducir semanalmente para perder peso"
                    )
            
            with col2:
                proteinas_objetivo = st.number_input(
                    "🥩 Proteínas Objetivo (g/día)",
                    min_value=0.0,
                    step=5.0,
                    value=meta_actual.proteinas_objetivo if meta_actual else 0.0,
                    help="Gramos de proteínas objetivo por día"
                )
                
                carbohidratos_objetivo = st.number_input(
                    "🍞 Carbohidratos Objetivo (g/día)",
                    min_value=0.0,
                    step=5.0,
                    value=meta_actual.carbohidratos_objetivo if meta_actual else 0.0,
                    help="Gramos de carbohidratos objetivo por día"
                )
            
            grasas_objetivo = st.number_input(
                "🧈 Grasas Objetivo (g/día)",
                min_value=0.0,
                step=5.0,
                value=meta_actual.grasas_objetivo if meta_actual else 0.0,
                help="Gramos de grasas objetivo por día"
            )
            
            fecha_inicio = st.date_input(
                "📅 Fecha de Inicio (Lunes de la semana)",
                value=meta_actual.fecha_inicio if meta_actual else date.today(),
                help="Debe ser un Lunes. Si no, se ajustará al Lunes de esa semana."
            )
            
            # Ajustar fecha_inicio al Lunes de esa semana
            from utils.week_helpers import get_week_start_end
            fecha_inicio_lunes, _ = get_week_start_end(fecha_inicio)
            
            if fecha_inicio != fecha_inicio_lunes:
                st.info(f"ℹ️ La fecha se ajustará al Lunes de esa semana: {fecha_inicio_lunes.strftime('%d/%m/%Y')}")
            
            if st.form_submit_button("💾 Guardar Meta Semanal", use_container_width=True):
                # Crear o actualizar meta
                meta = MetaCalorica(
                    calorias_semanales=calorias_semanales,
                    deficit_calorico=deficit_calorico,
                    proteinas_objetivo=proteinas_objetivo,
                    carbohidratos_objetivo=carbohidratos_objetivo,
                    grasas_objetivo=grasas_objetivo,
                    fecha_inicio=fecha_inicio_lunes,
                    fecha_fin=None  # Semanal, sin fecha fin
                )
                
                if MetaCaloricaService.guardar_meta(meta):
                    st.success("✅ Meta semanal guardada correctamente")
                    st.rerun()
                else:
                    st.error("❌ Error al guardar la meta")


if __name__ == "__main__":
    main()

