"""
Gestión de Peso y Metas de Pérdida de Peso
Página para registrar peso y configurar metas de pérdida
"""

import streamlit as st
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from services.peso_service import PesoService
from services.meta_calorica_service import MetaCaloricaService
from utils.helpers import apply_css_styles
from models.peso import RegistroPeso, MetaPeso


def main():
    """Función principal de gestión de peso"""
    
    # Aplicar CSS personalizado
    apply_css_styles()
    
    # Establecer página actual nutricional
    st.session_state["pagina_nutricional_actual"] = "peso"
    
    # Navegación lateral personalizada
    from utils.helpers import mostrar_navegacion_lateral
    mostrar_navegacion_lateral()
    
    st.title("⚖️ Peso y Metas de Pérdida")
    
    st.divider()
    
    # Sección: Registrar Peso
    st.subheader("📝 Registrar Peso")
    
    with st.expander("➕ Agregar Registro de Peso", expanded=False):
        with st.form("registro_peso", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                fecha_peso = st.date_input(
                    "📅 Fecha",
                    value=date.today(),
                    key="fecha_peso"
                )
                peso = st.number_input(
                    "⚖️ Peso (kg)",
                    min_value=0.0,
                    step=0.1,
                    value=0.0,
                    help="Peso en kilogramos"
                )
            
            with col2:
                fuente = st.selectbox(
                    "📱 Fuente",
                    ["manual", "bascula_inteligente"],
                    format_func=lambda x: "Manual" if x == "manual" else "Báscula Inteligente",
                    help="Origen del registro"
                )
                
                altura = st.number_input(
                    "📏 Altura (m)",
                    min_value=0.0,
                    max_value=3.0,
                    step=0.01,
                    value=0.0,
                    help="Altura en metros (para calcular IMC)"
                )
            
            with st.expander("📊 Datos Adicionales (Opcional)", expanded=False):
                col_ad1, col_ad2 = st.columns(2)
                
                with col_ad1:
                    grasa_corporal = st.number_input(
                        "💪 Grasa Corporal (%)",
                        min_value=0.0,
                        max_value=100.0,
                        step=0.1,
                        value=0.0,
                        help="Porcentaje de grasa corporal"
                    )
                    masa_muscular = st.number_input(
                        "💪 Masa Muscular (kg)",
                        min_value=0.0,
                        step=0.1,
                        value=0.0,
                        help="Masa muscular en kilogramos"
                    )
                    porcentaje_agua = st.number_input(
                        "💧 % Agua",
                        min_value=0.0,
                        max_value=100.0,
                        step=0.1,
                        value=0.0,
                        help="Porcentaje de agua corporal"
                    )
                    porcentaje_masa_muscular = st.number_input(
                        "💪 % Masa Muscular",
                        min_value=0.0,
                        max_value=100.0,
                        step=0.1,
                        value=0.0,
                        help="Porcentaje de masa muscular"
                    )
                    porcentaje_masa_osea = st.number_input(
                        "🦴 % Masa Ósea",
                        min_value=0.0,
                        max_value=100.0,
                        step=0.1,
                        value=0.0,
                        help="Porcentaje de masa ósea"
                    )
                
                with col_ad2:
                    metabolismo_basal = st.number_input(
                        "🔥 MB (kcal)",
                        min_value=0.0,
                        step=1.0,
                        value=0.0,
                        help="Metabolismo basal en calorías"
                    )
                    grasa_visceral = st.number_input(
                        "🫀 Grasa Visceral",
                        min_value=0.0,
                        step=0.1,
                        value=0.0,
                        help="Nivel de grasa visceral"
                    )
                    masa_magra_corporal = st.number_input(
                        "💪 Masa Magra Corporal (kg)",
                        min_value=0.0,
                        step=0.1,
                        value=0.0,
                        help="Masa magra corporal en kg"
                    )
                    masa_grasa_corporal = st.number_input(
                        "🧈 Masa Grasa Corporal (kg)",
                        min_value=0.0,
                        step=0.1,
                        value=0.0,
                        help="Masa grasa corporal en kg"
                    )
                    masa_osea = st.number_input(
                        "🦴 Masa Ósea (kg)",
                        min_value=0.0,
                        step=0.1,
                        value=0.0,
                        help="Masa ósea en kilogramos"
                    )
            
            if st.form_submit_button("💾 Guardar Registro", use_container_width=True, type="primary"):
                if peso > 0:
                    registro = RegistroPeso(
                        fecha=fecha_peso,
                        peso=peso,
                        grasa_corporal=grasa_corporal if grasa_corporal > 0 else None,
                        masa_muscular=masa_muscular if masa_muscular > 0 else None,
                        fuente=fuente,
                        altura=altura if altura > 0 else None,
                        porcentaje_agua=porcentaje_agua if porcentaje_agua > 0 else None,
                        porcentaje_masa_muscular=porcentaje_masa_muscular if porcentaje_masa_muscular > 0 else None,
                        porcentaje_masa_osea=porcentaje_masa_osea if porcentaje_masa_osea > 0 else None,
                        metabolismo_basal=metabolismo_basal if metabolismo_basal > 0 else None,
                        grasa_visceral=grasa_visceral if grasa_visceral > 0 else None,
                        masa_magra_corporal=masa_magra_corporal if masa_magra_corporal > 0 else None,
                        masa_grasa_corporal=masa_grasa_corporal if masa_grasa_corporal > 0 else None,
                        masa_osea=masa_osea if masa_osea > 0 else None
                    )
                    
                    if PesoService.agregar_registro(registro):
                        st.success(f"✅ Peso registrado: {peso:.1f} kg")
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar el registro")
                else:
                    st.error("❌ Por favor ingresa un peso válido")
    
    st.divider()
    
    # Sección: Configurar Meta de Pérdida de Peso
    st.subheader("🎯 Meta de Pérdida de Peso")
    
    meta_peso_actual = PesoService.obtener_meta_actual()
    peso_mas_reciente = PesoService.obtener_mas_reciente()
    peso_actual_valor = (peso_mas_reciente.peso if peso_mas_reciente else 
                        (meta_peso_actual.peso_actual if meta_peso_actual else 0.0))
    
    with st.form("meta_peso"):
        col1, col2 = st.columns(2)
        
        with col1:
            peso_actual = st.number_input(
                "⚖️ Peso Actual (kg)",
                min_value=0.0,
                step=0.1,
                value=peso_actual_valor,
                help="Tu peso actual"
            )
        
        with col2:
            peso_objetivo = st.number_input(
                "🎯 Peso Objetivo (kg)",
                min_value=0.0,
                step=0.1,
                value=meta_peso_actual.peso_objetivo if meta_peso_actual else 0.0,
                help="Peso que deseas alcanzar"
            )
        
        fecha_inicio_meta = st.date_input(
            "📅 Fecha de Inicio",
            value=meta_peso_actual.fecha_inicio if meta_peso_actual else date.today(),
            key="fecha_inicio_meta"
        )
        
        if st.form_submit_button("💾 Guardar Meta", use_container_width=True):
            if peso_actual > 0 and peso_objetivo > 0:
                meta = MetaPeso(
                    peso_actual=peso_actual,
                    peso_objetivo=peso_objetivo,
                    fecha_inicio=fecha_inicio_meta
                )
                
                if PesoService.guardar_meta(meta):
                    st.success("✅ Meta de peso guardada correctamente")
                    st.rerun()
                else:
                    st.error("❌ Error al guardar la meta")
            else:
                st.error("❌ Por favor completa todos los campos")
    
    st.divider()
    
    # Sección: Análisis y Proyección
    meta_peso = PesoService.obtener_meta_actual()
    meta_calorica = MetaCaloricaService.obtener_meta_actual()
    
    if meta_peso and meta_calorica:
        st.subheader("📊 Análisis de Progreso")
        
        # Calcular pérdida esperada con déficit
        deficit_semanal = meta_calorica.deficit_calorico
        semanas_transcurridas = (date.today() - meta_peso.fecha_inicio).days / 7
        
        perdida_esperada = PesoService.calcular_perdida_esperada(deficit_semanal, semanas_transcurridas)
        peso_actual_mostrar = peso_mas_reciente.peso if peso_mas_reciente else meta_peso.peso_actual
        perdida_real = meta_peso.peso_actual - peso_actual_mostrar
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "⚖️ Peso Actual",
                f"{peso_actual_mostrar:.1f} kg"
            )
        
        with col2:
            st.metric(
                "🎯 Peso Objetivo",
                f"{meta_peso.peso_objetivo:.1f} kg"
            )
        
        with col3:
            peso_restante = peso_actual_mostrar - meta_peso.peso_objetivo
            st.metric(
                "📉 Peso a Perder",
                f"{peso_restante:.1f} kg",
                delta="Restante" if peso_restante > 0 else "¡Meta alcanzada!"
            )
        
        st.divider()
        
        # Proyección de pérdida
        st.subheader("🔮 Proyección de Pérdida de Peso")
        
        if deficit_semanal > 0:
            perdida_semanal_esperada = PesoService.calcular_perdida_esperada(deficit_semanal, 1)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"📊 **Pérdida esperada por semana:** {perdida_semanal_esperada:.2f} kg")
                st.caption(f"Basado en un déficit calórico semanal de {deficit_semanal:.0f} calorías")
            
            with col2:
                if semanas_transcurridas > 0:
                    st.info(f"📊 **Pérdida esperada total:** {perdida_esperada:.2f} kg")
                    st.caption(f"En {semanas_transcurridas:.1f} semanas")
            
            # Gráfico de proyección
            semanas_proyeccion = 12
            fechas_proyeccion = []
            pesos_proyeccion = []
            peso_inicial = peso_mas_reciente.peso if peso_mas_reciente else meta_peso.peso_actual
            
            for semana in range(semanas_proyeccion + 1):
                fecha = meta_peso.fecha_inicio + timedelta(weeks=semana)
                perdida_acumulada = PesoService.calcular_perdida_esperada(deficit_semanal, semana)
                peso_proyectado = peso_inicial - perdida_acumulada
                
                fechas_proyeccion.append(fecha)
                pesos_proyeccion.append(peso_proyectado)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=fechas_proyeccion,
                y=pesos_proyeccion,
                mode='lines+markers',
                name='Proyección',
                line=dict(color='#4ECDC4', width=2),
                marker=dict(size=6)
            ))
            
            # Línea de meta
            fig.add_trace(go.Scatter(
                x=[fechas_proyeccion[0], fechas_proyeccion[-1]],
                y=[meta_peso.peso_objetivo, meta_peso.peso_objetivo],
                mode='lines',
                name='Meta',
                line=dict(color='#FF6B6B', width=2, dash='dash')
            ))
            
            # Punto actual si hay registro
            if peso_mas_reciente and peso_mas_reciente.fecha >= meta_peso.fecha_inicio:
                fig.add_trace(go.Scatter(
                    x=[peso_mas_reciente.fecha],
                    y=[peso_mas_reciente.peso],
                    mode='markers',
                    name='Peso Actual',
                    marker=dict(color='green', size=10)
                ))
            
            fig.update_layout(
                title="Proyección de Pérdida de Peso",
                xaxis_title="Fecha",
                yaxis_title="Peso (kg)",
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No hay déficit calórico configurado. Configura una meta calórica con déficit para ver proyecciones.")
    
    st.divider()
    
    # Historial de peso
    st.subheader("📊 Historial de Peso")
    
    registros_peso = PesoService.obtener_todos()
    
    if registros_peso:
        # Gráfico de evolución
        # Ordenar por fecha ascendente
        registros_peso_ordenados = sorted(registros_peso, key=lambda x: x.fecha)
        # Formatear fechas como strings para mostrar solo días (sin horas)
        fechas_str = [r.fecha.strftime("%d/%m/%Y") for r in registros_peso_ordenados]
        pesos = [r.peso for r in registros_peso_ordenados]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=fechas_str,
            y=pesos,
            mode='lines+markers',
            name='Peso',
            line=dict(color='#FF6B6B', width=2),
            marker=dict(size=8)
        ))
        
        # Línea de meta si existe
        if meta_peso:
            fig.add_trace(go.Scatter(
                x=[fechas_str[0], fechas_str[-1]],
                y=[meta_peso.peso_objetivo, meta_peso.peso_objetivo],
                mode='lines',
                name='Meta',
                line=dict(color='#4ECDC4', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title="Evolución del Peso",
            xaxis_title="Fecha",
            yaxis_title="Peso (kg)",
            height=400,
            hovermode='x unified',
            xaxis=dict(
                type='category',  # Tratar como categorías para evitar timestamps
                tickangle=-45,  # Rotar etiquetas para mejor legibilidad
                tickmode='linear'
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de registros recientes
        st.subheader("📋 Registros Recientes")
        datos_tabla = []
        for registro in registros_peso[:10]:  # Últimos 10
            imc_val = registro.imc
            datos_tabla.append({
                "Fecha": registro.fecha.strftime("%d/%m/%Y"),
                "Peso (kg)": f"{registro.peso:.1f}",
                "IMC": f"{imc_val:.1f}" if imc_val else "-",
                "Grasa (%)": f"{registro.grasa_corporal:.1f}" if registro.grasa_corporal else "-",
                "% Agua": f"{registro.porcentaje_agua:.1f}" if registro.porcentaje_agua else "-",
                "% Masa Muscular": f"{registro.porcentaje_masa_muscular:.1f}" if registro.porcentaje_masa_muscular else "-",
                "% Masa Ósea": f"{registro.porcentaje_masa_osea:.1f}" if registro.porcentaje_masa_osea else "-",
                "MB (kcal)": f"{registro.metabolismo_basal:.0f}" if registro.metabolismo_basal else "-",
                "Grasa Visceral": f"{registro.grasa_visceral:.1f}" if registro.grasa_visceral else "-",
                "Masa Magra (kg)": f"{registro.masa_magra_corporal:.1f}" if registro.masa_magra_corporal else "-",
                "Masa Grasa (kg)": f"{registro.masa_grasa_corporal:.1f}" if registro.masa_grasa_corporal else "-",
                "Masa Ósea (kg)": f"{registro.masa_osea:.1f}" if registro.masa_osea else "-",
                "Masa Muscular (kg)": f"{registro.masa_muscular:.1f}" if registro.masa_muscular else "-",
                "Fuente": "Báscula" if registro.fuente == "bascula_inteligente" else "Manual"
            })
        
        import pandas as pd
        df = pd.DataFrame(datos_tabla)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay registros de peso. ¡Agrega tu primer registro!")


if __name__ == "__main__":
    main()

