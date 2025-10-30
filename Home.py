"""
Dashboard Financiero - Punto de entrada principal
Refactorizado con arquitectura separada
"""

import streamlit as st
from pages.cuentas import mostrar_cuentas
from pages.movimientos import mostrar_movimientos
from pages.reportes import mostrar_reportes
from pages.configuracion import mostrar_configuracion
from pages.gastos_recurrentes import mostrar_gastos_recurrentes
from pages.metas import mostrar_metas
from services.cuenta_service import CuentaService
from services.reporte_service import ReporteService
from utils.database import cargar_configuracion
from utils.config_manager import config_manager, financial_config, ui_config
from utils.helpers import apply_css_styles, show_success_message, show_error_message, show_fullscreen_loading, hide_fullscreen_loading


def mostrar_graficas_principales(resumen):
    """Mostrar gráficas principales del dashboard"""
    import plotly.graph_objects as go
    import plotly.express as px
    
    st.subheader("📊 Resumen Visual")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de gastos mensuales (una barra con porcentaje)
        gastos_mes = resumen.get("gastos_mes", 0)
        
        # El presupuesto es solo la suma de gastos recurrentes
        gastos_recurrentes = resumen.get("gastos_recurrentes", 0)
        presupuesto_total = gastos_recurrentes
        
        if presupuesto_total > 0:
            # Calcular porcentaje gastado
            porcentaje_gastado = min((gastos_mes / presupuesto_total) * 100, 100)
            
            # Crear gráfico de una sola barra
            fig = go.Figure(data=[
                go.Bar(
                    x=['Gastos del Mes'],
                    y=[porcentaje_gastado],
                    marker_color='red' if porcentaje_gastado > 100 else 'lightblue',
                    text=[f"{porcentaje_gastado:.1f}%"],
                    textposition='auto',
                    width=0.5
                )
            ])
            
            # Agregar línea de referencia al 100%
            fig.add_hline(y=100, line_dash="dash", line_color="red", 
                         annotation_text="Límite del Presupuesto")
            
            fig.update_layout(
                title=f"Gastos del Mes: ${gastos_mes:,.2f} / ${presupuesto_total:,.2f}",
                xaxis_title="",
                yaxis_title="Porcentaje del Presupuesto (%)",
                yaxis=dict(range=[0, max(porcentaje_gastado * 1.2, 100)]),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar información adicional
            if gastos_mes > presupuesto_total:
                st.warning(f"⚠️ Te excediste del presupuesto por ${gastos_mes - presupuesto_total:,.2f}")
            elif presupuesto_total == 0:
                st.info("No hay presupuesto configurado")
            else:
                st.success(f"✅ Te quedan ${presupuesto_total - gastos_mes:,.2f} del presupuesto")            
    
    with col2:
        # Sección de progreso de ahorros
        st.subheader("🎯 Progreso de Ahorros")
        
        # Obtener metas
        meta_mensual = financial_config.get_meta_mensual()
        meta_anual = financial_config.get_meta_anual()
        ahorro_actual = resumen.get("ahorro_actual", 0)
        
        # Mostrar métricas de ahorro
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.metric(
                "💰 Ahorro Actual",
                f"${ahorro_actual:,.2f}",
                delta=f"Meta: ${meta_anual:,.2f}" if meta_anual > 0 else None
            )
        
        with col_b:
            if meta_mensual > 0:
                progreso_mensual = min(ahorro_actual / meta_mensual, 2.0) * 100
                st.metric(
                    "📅 Progreso Mensual",
                    f"{progreso_mensual:.1f}%",
                    delta=f"Meta: ${meta_mensual:,.2f}"
                )
        
        # Gráfico de progreso de ahorro anual (velocímetro)
        if meta_anual > 0:
            progreso_anual = min(ahorro_actual / meta_anual, 2.0) * 100  # Permitir hasta 200%
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=progreso_anual,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Progreso Ahorro Anual (%)"},
                delta={'reference': 100},
                gauge={
                    'axis': {'range': [0, 200]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 75], 'color': "red"},
                        {'range': [75, 100], 'color': "orange"},
                        {'range': [100, 150], 'color': "lightgreen"},
                        {'range': [150, 200], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "green", 'width': 4},
                        'thickness': 0.75,
                        'value': 100
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar información adicional
            if progreso_anual < 75:
                st.error("🔴 Necesitas más ahorro para alcanzar tu meta")
            elif progreso_anual < 100:
                st.warning("🟡 Estás cerca de tu meta anual")
            elif progreso_anual < 150:
                st.success("🟢 ¡Excelente! Has superado tu meta anual")
            else:
                st.success("🟢 ¡Increíble! Has duplicado tu meta anual")
        else:
            st.info("No hay meta de ahorro configurada")
    
    # Gráficas de pastel lado a lado
    col_pie1, col_pie2 = st.columns(2)
    
    with col_pie1:
        # Gráfico de pastel de gastos por categoría
        st.subheader("🥧 Gastos por Categoría")
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
        st.subheader("🥧 Gastos por Tipo")
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
    
# TOP 3 gastos ya se muestra en mostrar_graficas_principales()


# Función eliminada - el dashboard se muestra directamente en main()


def main():
    """Función principal del dashboard"""
    
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
    
    # Header principal (solo para dashboard principal)
    if st.session_state.get("pagina_actual", "dashboard") == "dashboard":
        st.markdown("""
        <div class="main-header">
            <h1>💰 Dashboard Financiero</h1>
            <p>Gestiona tus finanzas de manera inteligente</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Cargar datos sin loading que se atasca
    try:
        resumen = ReporteService.generar_resumen_financiero()
        configuracion = cargar_configuracion()
        
        # Sincronizar configuraciones con Firebase si es necesario
        if not config_manager.sync_with_firebase():
            st.warning("⚠️ No se pudo sincronizar con Firebase. Usando configuración local.")
    except Exception as e:
        show_error_message(f"Error cargando datos: {e}")
        return
    
    # Solo mostrar dashboard si está seleccionado
    if st.session_state.get("pagina_actual", "dashboard") == "dashboard":
        # Métricas principales (saldo total, gastos del mes y presupuesto mensual)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            saldo_total = resumen.get('saldo_total', 0)
            st.metric(
                "💰 Saldo Total",
                config_manager.get_formatted_currency(saldo_total)
            )
        
        with col2:
            gastos_mes = resumen.get('gastos_mes', 0)
            st.metric(
                "💸 Gastos del Mes",
                config_manager.get_formatted_currency(gastos_mes)
            )
        
        with col3:
            # El presupuesto mensual es solo la suma de gastos recurrentes
            gastos_recurrentes = resumen.get("gastos_recurrentes", 0)
            st.metric(
                "📊 Presupuesto Mensual",
                config_manager.get_formatted_currency(gastos_recurrentes)
            )
        
        st.divider()
        
        # Gráficas principales del dashboard
        if ui_config.should_show_charts():
            mostrar_graficas_principales(resumen)
        
        st.divider()
        
        # TOP 3 gastos del mes
        st.subheader("🔥 TOP 3 Categorías con Más Gastos")
        top_gastos = resumen.get("top_gastos", [])
        if top_gastos:
            for i, gasto in enumerate(top_gastos, 1):
                if isinstance(gasto, dict):
                    # Nuevo formato: categoría con total
                    st.write(f"**#{i}** 🏷️ {gasto['categoria']} - {config_manager.get_formatted_currency(gasto['total'])}")
                else:
                    # Formato anterior: movimiento individual
                    st.write(f"**#{i}** 💸 {gasto.concepto} - {config_manager.get_formatted_currency(gasto.monto_absoluto)} ({gasto.categoria})")
        else:
            st.info("No hay gastos registrados")
        
        st.divider()
    
    # Navegación principal
    st.sidebar.markdown("### 🧭 Navegación")
    
    # Obtener página actual
    pagina_actual = st.session_state.get("pagina_actual", "dashboard")
    
    # Botones de navegación
    if st.sidebar.button("🏠 Dashboard", use_container_width=True, type="primary" if pagina_actual == "dashboard" else "secondary"):
        st.session_state["pagina_actual"] = "dashboard"
        st.rerun()
    
    if st.sidebar.button("🏦 Cuentas", use_container_width=True, type="primary" if pagina_actual == "cuentas" else "secondary"):
        st.session_state["pagina_actual"] = "cuentas"
        st.rerun()
    
    if st.sidebar.button("💰 Movimientos", use_container_width=True, type="primary" if pagina_actual == "movimientos" else "secondary"):
        st.session_state["pagina_actual"] = "movimientos"
        st.rerun()
    
    if st.sidebar.button("📊 Reportes", use_container_width=True, type="primary" if pagina_actual == "reportes" else "secondary"):
        st.session_state["pagina_actual"] = "reportes"
        st.rerun()
    
    if st.sidebar.button("💳 Gastos Recurrentes", use_container_width=True, type="primary" if pagina_actual == "gastos_recurrentes" else "secondary"):
        st.session_state["pagina_actual"] = "gastos_recurrentes"
        st.rerun()
    
    if st.sidebar.button("🎯 Metas", use_container_width=True, type="primary" if pagina_actual == "metas" else "secondary"):
        st.session_state["pagina_actual"] = "metas"
        st.rerun()
    
    if st.sidebar.button("⚙️ Configuración", use_container_width=True, type="primary" if pagina_actual == "configuracion" else "secondary"):
        st.session_state["pagina_actual"] = "configuracion"
        st.rerun()
    
    if st.sidebar.button("🔥 Prueba Firebase", use_container_width=True, type="primary" if pagina_actual == "firebase_test" else "secondary"):
        st.session_state["pagina_actual"] = "firebase_test"
        st.rerun()
    
    # Debug: Mostrar página actual
    st.sidebar.write(f"Página actual: {pagina_actual}")
    
    if pagina_actual == "dashboard":
        # Dashboard principal (ya se muestra arriba)
        pass
    elif pagina_actual == "cuentas":
        mostrar_cuentas()
    elif pagina_actual == "movimientos":
        mostrar_movimientos()
    elif pagina_actual == "reportes":
        mostrar_reportes()
    elif pagina_actual == "gastos_recurrentes":
        mostrar_gastos_recurrentes()
    elif pagina_actual == "metas":
        mostrar_metas()
    elif pagina_actual == "configuracion":
        mostrar_configuracion()
    elif pagina_actual == "firebase_test":
        mostrar_firebase_test()
    else:
        # Página por defecto (dashboard)
        pass


def mostrar_configuracion():
    """Mostrar página de configuración"""
    st.title("⚙️ Configuración del Sistema")
    
    configuracion = cargar_configuracion()
    
    # Gestión de categorías
    st.subheader("🏷️ Categorías de Gastos")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        nueva_categoria = st.text_input("➕ Nueva Categoría", placeholder="Ej: Ropa, Deportes, etc.")
    with col2:
        if st.button("➕ Agregar", use_container_width=True):
            if nueva_categoria:
                from utils.database import agregar_categoria
                success, message = agregar_categoria(nueva_categoria)
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.error("❌ Por favor ingresa un nombre")
    
    # Lista de categorías
    st.write("**Categorías actuales:**")
    cols = st.columns(3)
    for i, categoria in enumerate(configuracion["categorias"]):
        with cols[i % 3]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"🏷️ {categoria}")
            with col2:
                if st.button("🗑️", key=f"del_cat_{categoria}"):
                    # Recargar configuración antes de eliminar
                    configuracion = cargar_configuracion()
                    if categoria in configuracion.get("categorias", []):
                        configuracion["categorias"].remove(categoria)
                        from utils.database import guardar_configuracion
                        if guardar_configuracion(configuracion):
                            st.success(f"✅ Categoría '{categoria}' eliminada!")
                            st.rerun()
                        else:
                            st.error("❌ Error al eliminar la categoría")
    
    st.divider()
    
    # Gestión de tipos de gasto
    st.subheader("🔍 Tipos de Gasto")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        nuevo_tipo = st.text_input("➕ Nuevo Tipo de Gasto", placeholder="Ej: Inversión, Ahorro, etc.")
    with col2:
        if st.button("➕ Agregar Tipo", use_container_width=True):
            if nuevo_tipo:
                from utils.database import agregar_tipo_gasto
                success, message = agregar_tipo_gasto(nuevo_tipo)
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.error("❌ Por favor ingresa un nombre")
    
    # Lista de tipos de gasto
    st.write("**Tipos de gasto actuales:**")
    cols = st.columns(3)
    for i, tipo in enumerate(configuracion["tipos_gasto"]):
        with cols[i % 3]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"🔍 {tipo}")
            with col2:
                if st.button("🗑️", key=f"del_tipo_{tipo}"):
                    # Recargar configuración antes de eliminar
                    configuracion = cargar_configuracion()
                    if tipo in configuracion.get("tipos_gasto", []):
                        configuracion["tipos_gasto"].remove(tipo)
                        from utils.database import guardar_configuracion
                        if guardar_configuracion(configuracion):
                            st.success(f"✅ Tipo '{tipo}' eliminado!")
                            st.rerun()
                        else:
                            st.error("❌ Error al eliminar el tipo")
    
    st.divider()
    st.info("💡 **Tip:** Los cambios en categorías y tipos se aplicarán inmediatamente en todos los formularios.")


def mostrar_firebase_test():
    """Mostrar página de prueba de Firebase"""
    st.title("🔥 Prueba de Conexión Firebase")
    
    st.subheader("🧪 Verificar Conexión a Firebase")
    
    if st.button("🚀 Probar Conexión Firebase"):
        try:
            from utils.database import firebase_get, firebase_push, FIREBASE_URL
            from datetime import datetime
            
            st.write(f"**URL Firebase:** `{FIREBASE_URL}`")
            
            # Probar GET
            st.write("**1. Probando GET...**")
            data = firebase_get("test")
            st.write(f"Resultado GET: {data}")
            
            # Probar PUSH
            st.write("**2. Probando PUSH...**")
            test_data = {
                "mensaje": "Prueba desde Streamlit",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "funcionando": True
            }
            result = firebase_push("test", test_data)
            st.write(f"Resultado PUSH: {result}")
            
            if result:
                st.success("✅ Firebase está funcionando correctamente!")
            else:
                st.error("❌ Firebase no está respondiendo")
                
        except Exception as e:
            st.error(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
