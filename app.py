"""
Dashboard Financiero - Punto de entrada principal
Refactorizado para usar navegación nativa de Streamlit
"""

import streamlit as st
from services.reporte_service import ReporteService
from utils.database import cargar_configuracion
from utils.config_manager import config_manager
from utils.helpers import apply_css_styles, show_error_message
import plotly.graph_objects as go
import plotly.express as px



def mostrar_graficas_principales(resumen):
    """Mostrar gráficas principales del dashboard"""
    
    st.subheader("📊 Resumen Visual")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de gastos mensuales (una barra con porcentaje)
        gastos_mes = resumen.get("gastos_mes", 0)
        
        # El presupuesto es solo la suma de gastos recurrentes
        gastos_recurrentes = resumen.get("gastos_recurrentes", 0)
        presupuesto_total = gastos_recurrentes
        
        if presupuesto_total > 0:
            # Calcular porcentaje gastado (sin límite de 100%)
            porcentaje_gastado = (gastos_mes / presupuesto_total) * 100
            
            # Determinar color según si se superó el presupuesto
            color_barra = 'red' if porcentaje_gastado > 100 else 'lightblue'
            estado = "🔴 SUPERADO" if porcentaje_gastado > 100 else "🟢 DENTRO DEL PRESUPUESTO"
            
            # Crear gráfico de una sola barra
            fig = go.Figure(data=[
                go.Bar(
                    x=['Gastos del Mes'],
                    y=[porcentaje_gastado],
                    marker_color=color_barra,
                    text=[f"{porcentaje_gastado:.1f}%<br>{estado}"],
                    textposition='auto',
                    width=0.5
                )
            ])
            
            # Configurar límite del eje Y dinámico
            y_max = max(porcentaje_gastado * 1.1, 120)  # 10% más del valor o mínimo 120%
            
            fig.update_layout(
                title="Gastos del Mes vs Presupuesto",
                yaxis_title="Porcentaje (%)",
                yaxis=dict(range=[0, y_max]),
                height=400,
                showlegend=False
            )
            
            # Agregar línea de 100%
            fig.add_hline(y=100, line_dash="dash", line_color="red", 
                         annotation_text="Límite del presupuesto")
            
            st.plotly_chart(fig, use_container_width=True)
        elif presupuesto_total == 0:
            st.info("No hay presupuesto configurado")
        else:
            st.info("No hay gastos registrados")
    
    with col2:
        # Gráfico de ahorro anual (velocímetro)
        ahorro_actual = resumen.get("ahorro_actual", 0)
        meta_anual = resumen.get("meta_anual", 0)
        
        if meta_anual > 0:
            progreso_anual = min((ahorro_actual / meta_anual) * 100, 200)
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = progreso_anual,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Progreso Ahorro Anual (%)"},
                delta = {'reference': 100},
                gauge = {'axis': {'range': [None, 200]},
                        'bar': {'color': "darkgreen"},
                        'steps': [
                            {'range': [0, 75], 'color': "red"},
                            {'range': [75, 100], 'color': "orange"},
                            {'range': [100, 150], 'color': "lightgreen"},
                            {'range': [150, 200], 'color': "green"}],
                        'threshold': {'line': {'color': "green", 'width': 4},
                                    'thickness': 0.75, 'value': 100}}))
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Mensaje dinámico
            if progreso_anual >= 100:
                st.success(f"🎉 ¡Excelente! Has alcanzado tu meta anual ({progreso_anual:.1f}%)")
            elif progreso_anual >= 75:
                st.info(f"📈 Muy bien, vas por buen camino ({progreso_anual:.1f}%)")
            else:
                st.warning(f"⚠️ Necesita más ahorro para alcanzar la meta ({progreso_anual:.1f}%)")
        else:
            st.info("No hay meta anual configurada")
    
    # Gráficas de pastel lado a lado
    col_pie1, col_pie2 = st.columns(2)
    
    with col_pie1:
        # Gráfico de pastel de gastos por categoría
        st.subheader("📊 Gastos por Categoría")
        gastos_por_categoria = resumen.get("gastos_por_categoria", {})
        if gastos_por_categoria:
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(gastos_por_categoria.keys()),
                    values=list(gastos_por_categoria.values()),
                    textinfo='label+percent+value',
                    texttemplate='%{label}<br>%{percent}<br>$%{value:,.0f}',
                    hovertemplate='<b>%{label}</b><br>Monto: $%{value:,.2f}<br>Porcentaje: %{percent}<extra></extra>'
                )
            ])
            fig.update_layout(
                title="Distribución de Gastos por Categoría",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de gastos por categoría para mostrar")
    
    with col_pie2:
        # Gráfico de pastel de gastos por tipo de gasto
        st.subheader("📈 Gastos por Tipo")
        gastos_por_tipo = resumen.get("gastos_por_tipo", {})
        if gastos_por_tipo:
            # Definir colores según el tipo de gasto
            colores_por_tipo = {
                'Necesario': '#2E8B57',      # Verde mar
                'Innecesario': '#FFD700',    # Amarillo dorado
                'Emergencia': '#DC143C',     # Rojo carmesí
                'Lujo': '#9370DB',           # Púrpura medio
                'Ocio': '#FF6347',           # Tomate
                'Salud': '#20B2AA',          # Verde azulado
                'Educación': '#4169E1',      # Azul real
                'Transporte': '#FF8C00',     # Naranja oscuro
                'Alimentación': '#32CD32',   # Verde lima
                'Vivienda': '#8B4513'        # Marrón silla de montar
            }
            
            # Asignar colores a cada tipo
            colores = []
            for tipo in gastos_por_tipo.keys():
                colores.append(colores_por_tipo.get(tipo, '#808080'))  # Gris por defecto
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(gastos_por_tipo.keys()),
                    values=list(gastos_por_tipo.values()),
                    textinfo='label+percent+value',
                    texttemplate='%{label}<br>%{percent}<br>$%{value:,.0f}',
                    hovertemplate='<b>%{label}</b><br>Monto: $%{value:,.2f}<br>Porcentaje: %{percent}<extra></extra>',
                    marker=dict(colors=colores)
                )
            ])
            fig.update_layout(
                title="Distribución de Gastos por Tipo",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de gastos por tipo para mostrar")


def main():
    """Función principal del dashboard"""
    
    # Verificar si ya se inicializó para evitar recargas
    if "dashboard_initialized" not in st.session_state:
        st.session_state["dashboard_initialized"] = True
        
        # Configuración de la página desde configuraciones centralizadas
        app_config = config_manager.get_config("app")
        st.set_page_config(
            page_title=app_config.get("name", "Dashboard Finanzas"),
            page_icon="💰",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    # Aplicar CSS personalizado desde configuraciones
    apply_css_styles()
    
    # Navegación lateral personalizada
    from utils.helpers import mostrar_navegacion_lateral
    mostrar_navegacion_lateral()
    
    # Header principal con botón de refrescar
    col_header, col_refresh = st.columns([4, 1])
    
    with col_header:
        st.markdown("""
        <div class="main-header">
            <h1>💰 Dashboard Financiero</h1>
            <p>Gestiona tus finanzas de manera inteligente</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_refresh:
        if st.button("🔄 Refrescar Datos", help="Actualizar datos del dashboard"):
            # Limpiar cache y recargar datos
            if "dashboard_data" in st.session_state:
                del st.session_state["dashboard_data"]
            st.rerun()
    
    # Cargar datos con cache para evitar recálculos
    try:
        # Usar cache de sesión para evitar recálculos constantes
        if "dashboard_data" not in st.session_state:
            st.session_state["dashboard_data"] = ReporteService.generar_resumen_financiero()
        
        resumen = st.session_state["dashboard_data"]
        configuracion = cargar_configuracion()
        
        # Cargar metas por separado
        from utils.database import cargar_metas
        metas = cargar_metas()
        resumen["meta_anual"] = metas.get("meta_anual", 0)
        resumen["meta_mensual"] = metas.get("meta_mensual", 0)
        
        # Sincronizar configuraciones con Firebase si es necesario
        if not config_manager.sync_with_firebase():
            st.warning("⚠️ No se pudo sincronizar con Firebase. Usando configuración local.")
    except Exception as e:
        show_error_message(f"Error cargando datos: {e}")
        return
    
    # Métricas principales (saldo total, gastos del mes y presupuesto mensual)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        saldo_total = resumen.get('saldo_total', 0)
        
        # Determinar color e icono según el saldo
        if saldo_total >= 100000:
            color = "green"
            icono = "💚"
        else:
            color = "red"
            icono = "🔴"
        
        # Mostrar métrica con color personalizado (texto grande como original)
        st.markdown(f"""
        <div style="
            background: {'#d4edda' if saldo_total >= 100000 else '#f8d7da'};
            border: 2px solid {'#28a745' if saldo_total >= 100000 else '#dc3545'};
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            margin: 0.5rem 0;
        ">
            <h3 style="color: {'#155724' if saldo_total >= 100000 else '#721c24'}; margin: 0;">
                {icono} Saldo Total
            </h3>
            <h2 style="color: {'#155724' if saldo_total >= 100000 else '#721c24'}; margin: 0.5rem 0;">
                {config_manager.get_formatted_currency(saldo_total)}
            </h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        gastos_mes = resumen.get('gastos_mes', 0)
        gastos_recurrentes = resumen.get('gastos_recurrentes', 0)
        
        # Calcular porcentaje de gasto del presupuesto
        if gastos_recurrentes > 0:
            porcentaje_gasto = (gastos_mes / gastos_recurrentes) * 100
        else:
            porcentaje_gasto = 0
        
        # Determinar color e icono según el porcentaje de gasto
        if porcentaje_gasto >= 100:
            color_gasto = "red"
            icono_gasto = "🔴"
        elif porcentaje_gasto >= 80:
            color_gasto = "orange"
            icono_gasto = "🟠"
        elif porcentaje_gasto >= 50:
            color_gasto = "yellow"
            icono_gasto = "🟡"
        else:
            color_gasto = "green"
            icono_gasto = "🟢"
        
        # Mostrar métrica de gastos con color personalizado
        st.markdown(f"""
        <div style="
            background: {'#f8d7da' if porcentaje_gasto >= 100 else '#fff3cd' if porcentaje_gasto >= 80 else '#d1ecf1' if porcentaje_gasto >= 50 else '#d4edda'};
            border: 2px solid {'#dc3545' if porcentaje_gasto >= 100 else '#ffc107' if porcentaje_gasto >= 80 else '#17a2b8' if porcentaje_gasto >= 50 else '#28a745'};
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            margin: 0.5rem 0;
        ">
            <h3 style="color: {'#721c24' if porcentaje_gasto >= 100 else '#856404' if porcentaje_gasto >= 80 else '#0c5460' if porcentaje_gasto >= 50 else '#155724'}; margin: 0;">
                {icono_gasto} Gastos del Mes
            </h3>
            <h2 style="color: {'#721c24' if porcentaje_gasto >= 100 else '#856404' if porcentaje_gasto >= 80 else '#0c5460' if porcentaje_gasto >= 50 else '#155724'}; margin: 0.5rem 0;">
                {config_manager.get_formatted_currency(gastos_mes)}
            </h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        ahorro_actual = resumen.get('ahorro_actual', 0)
        meta_mensual = resumen.get('meta_mensual', 0)
        
        # Calcular porcentaje de ahorro vs meta
        if meta_mensual > 0:
            porcentaje_ahorro = (ahorro_actual / meta_mensual) * 100
        else:
            porcentaje_ahorro = 0
        
        # Determinar color e icono según el porcentaje de ahorro
        if porcentaje_ahorro >= 100:
            color_ahorro = "green"
            icono_ahorro = "🎯"
        elif porcentaje_ahorro >= 80:
            color_ahorro = "blue"
            icono_ahorro = "📈"
        elif porcentaje_ahorro >= 50:
            color_ahorro = "orange"
            icono_ahorro = "🟡"
        else:
            color_ahorro = "red"
            icono_ahorro = "🔴"
        
        # Mostrar métrica de ahorro con color personalizado
        st.markdown(f"""
        <div style="
            background: {'#d4edda' if porcentaje_ahorro >= 100 else '#d1ecf1' if porcentaje_ahorro >= 80 else '#fff3cd' if porcentaje_ahorro >= 50 else '#f8d7da'};
            border: 2px solid {'#28a745' if porcentaje_ahorro >= 100 else '#17a2b8' if porcentaje_ahorro >= 80 else '#ffc107' if porcentaje_ahorro >= 50 else '#dc3545'};
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
            margin: 0.5rem 0;
        ">
            <h3 style="color: {'#155724' if porcentaje_ahorro >= 100 else '#0c5460' if porcentaje_ahorro >= 80 else '#856404' if porcentaje_ahorro >= 50 else '#721c24'}; margin: 0;">
                {icono_ahorro} Ahorro del Mes
            </h3>
            <h2 style="color: {'#155724' if porcentaje_ahorro >= 100 else '#0c5460' if porcentaje_ahorro >= 80 else '#856404' if porcentaje_ahorro >= 50 else '#721c24'}; margin: 0.5rem 0;">
                {config_manager.get_formatted_currency(ahorro_actual)}
            </h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Mostrar gráficas principales
    mostrar_graficas_principales(resumen)
    
    st.divider()
    
    # TOP 3 gastos del mes
    st.subheader("🏆 TOP 5 Gastos del Mes")
    top_gastos = resumen.get("top_gastos", [])
    
    if top_gastos:
        for i, gasto in enumerate(top_gastos[:5], 1):
            col1, col2 = st.columns([1, 5])
            with col1:
                st.write(f"**#{i}**")
            with col2:
                st.write(f"🏷️ {gasto['categoria']}: {config_manager.get_formatted_currency(gasto['total'])}")
    else:
        st.info("No hay gastos registrados")


if __name__ == "__main__":
    main()
