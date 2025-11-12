"""
Dashboard Financiero - Punto de entrada principal
Refactorizado con arquitectura separada
"""

import streamlit as st
import importlib.util
import sys
from datetime import datetime
from services.cuenta_service import CuentaService
from services.reporte_service import ReporteService
from utils.database import cargar_configuracion
from utils.config_manager import config_manager, financial_config, ui_config
from utils.helpers import apply_css_styles, show_success_message, show_error_message

# Importar funciones desde archivos con números en el nombre usando importlib
def import_function_from_file(module_name, function_name):
    """Importar una función desde un archivo con números en el nombre"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, f"pages/{module_name}.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return getattr(module, function_name)
    except Exception as e:
        print(f"Error importando {function_name} desde {module_name}: {e}")
        return None

# Importar funciones necesarias
mostrar_cuentas = import_function_from_file("1_Cuentas", "mostrar_cuentas")
mostrar_movimientos = import_function_from_file("2_Movimientos", "mostrar_movimientos")
# mostrar_reportes no existe, se usa main() del archivo 3_Reportes.py
mostrar_configuracion = import_function_from_file("6_Configuracion", "main")
mostrar_gastos_recurrentes = import_function_from_file("4_Gastos_Recurrentes", "mostrar_gastos_recurrentes")
mostrar_metas = import_function_from_file("5_Metas", "mostrar_metas_actuales")


def mostrar_graficas_principales(resumen):
    """Mostrar gráficas principales del dashboard"""
    import plotly.graph_objects as go
    import plotly.express as px
    
    # Crear fila de títulos alineados con las columnas
    col_title1, col_title2 = st.columns(2)
    
    with col_title1:
        st.subheader("📊 Resumen Visual")
    
    with col_title2:
        st.subheader("🎯 Progreso de Ahorros")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de gastos mensuales con textos y validaciones de colores
        gastos_mes = resumen.get("gastos_mes", 0)
        
        # El presupuesto es solo la suma de gastos recurrentes
        gastos_recurrentes = resumen.get("gastos_recurrentes", 0)
        presupuesto_total = gastos_recurrentes
        
        if presupuesto_total > 0:
            # Calcular porcentaje gastado (sin límite de 100%)
            porcentaje_gastado = (gastos_mes / presupuesto_total) * 100
            
            # Determinar color según el porcentaje
            if porcentaje_gastado >= 100:
                color_barra = 'red'
            elif porcentaje_gastado >= 80:
                color_barra = 'orange'
            elif porcentaje_gastado >= 50:
                color_barra = 'yellow'
            else:
                color_barra = 'lightblue'
            
            # Crear gráfico de una sola barra
            fig = go.Figure(data=[
                go.Bar(
                    x=['Gastos del Mes'],
                    y=[porcentaje_gastado],
                    marker_color=color_barra,
                    text=[f"{porcentaje_gastado:.1f}%"],
                    textposition='auto',
                    width=0.5
                )
            ])
            
            # Agregar línea de referencia al 100%
            fig.add_hline(y=100, line_dash="dash", line_color="red", 
                         annotation_text="Límite del Presupuesto")
            
            # Configurar límite del eje Y dinámico
            y_max = max(porcentaje_gastado * 1.1, 120)  # 10% más del valor o mínimo 120%
            
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Porcentaje del Presupuesto (%)",
                yaxis=dict(range=[0, y_max]),
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar información adicional con validaciones de colores
            if gastos_mes > presupuesto_total:
                st.error(f"⚠️ Te excediste del presupuesto por ${gastos_mes - presupuesto_total:,.2f}")
            elif porcentaje_gastado >= 80:
                st.warning(f"⚠️ Estás cerca del límite. Te quedan ${presupuesto_total - gastos_mes:,.2f} del presupuesto")
            elif presupuesto_total == 0:
                st.info("No hay presupuesto configurado")
            else:
                st.success(f"✅ Te quedan ${presupuesto_total - gastos_mes:,.2f} del presupuesto")            
    
    with col2:
        # Sección de progreso de ahorros (solo gráfica del velocímetro anual, sin métricas)
        
        # Obtener metas desde la base de datos
        from utils.database import cargar_metas
        metas = cargar_metas()
        meta_anual = metas.get("meta_anual", 0)
        ahorro_acumulado_anual = resumen.get("ahorro_acumulado_anual", 0)  # Ahorro acumulado del año
        
        # Gráfico de progreso de ahorro anual (velocímetro)
        # Usar ahorro acumulado del año, no solo del mes actual
        if meta_anual > 0:
            progreso_anual = min(ahorro_acumulado_anual / meta_anual, 2.0) * 100  # Permitir hasta 200%
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=progreso_anual,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Progreso Ahorro Anual"},
                number={'valueformat': '.1f', 'suffix': '%'},
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
            fig.update_layout(height=400)
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
    
# TOP 3 gastos ya se muestra en mostrar_graficas_principales()


# Función eliminada - el dashboard se muestra directamente en main()


def main():
    """Función principal del dashboard"""
    
    # Configuración de la página desde configuraciones centralizadas
    app_config = config_manager.get_config("app")
    st.set_page_config(
        page_title=app_config.get("name", "Dashboard Personal"),
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Aplicar CSS personalizado desde configuraciones
    apply_css_styles()
    
    # Obtener página actual PRIMERO
    pagina_actual = st.session_state.get("pagina_actual", "dashboard")
    
    # Limpiar flag de navegación al inicio para asegurar que los botones siempre se muestren
    # Esto es necesario porque el flag puede estar establecido desde una ejecución anterior
    if "nav_financiera_shown_this_run" in st.session_state:
        del st.session_state["nav_financiera_shown_this_run"]
    
    # Mostrar navegación lateral SIEMPRE PRIMERO (antes de cargar cualquier página)
    # Esto asegura que el menú lateral esté visible en todo momento y funcione correctamente
    from utils.helpers import mostrar_navegacion_lateral_financiera
    mostrar_navegacion_lateral_financiera()
    
    # Solo cargar datos del dashboard si estamos en la página del dashboard
    if pagina_actual == "dashboard":
        # Header principal del dashboard financiero
        st.markdown("""
        <div class="main-header">
            <h1>💰 Dashboard Financiero</h1>
            <p>Gestiona tus finanzas de manera inteligente</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Cargar datos del dashboard (solo cuando es necesario)
        try:
            resumen = ReporteService.generar_resumen_financiero()
            configuracion = cargar_configuracion()
            
            # Sincronizar configuraciones con Firebase si es necesario (sin bloquear)
            try:
                if not config_manager.sync_with_firebase():
                    st.warning("⚠️ No se pudo sincronizar con Firebase. Usando configuración local.")
            except Exception as sync_error:
                # Si falla la sincronización, continuar sin bloquear
                print(f"Error sincronizando con Firebase: {sync_error}")
        except Exception as e:
            show_error_message(f"Error cargando datos: {e}")
            st.info("💡 Intenta recargar la página o verifica tu conexión.")
            return
        
        # Mostrar dashboard
        # Métricas principales (saldo total con validación de colores, gastos del mes y ahorro del mes)
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
        
        # Gráficas principales del dashboard
        if ui_config.should_show_charts():
            mostrar_graficas_principales(resumen)
        
        st.divider()
        
        # TOP 5 gastos del mes
        st.subheader("🔥 TOP 5 Categorías con Más Gastos")
        top_gastos = resumen.get("top_gastos", [])
        if top_gastos:
            # Mostrar los primeros 5
            for i, gasto in enumerate(top_gastos[:5], 1):
                if isinstance(gasto, dict):
                    # Nuevo formato: categoría con total
                    st.write(f"**#{i}** 🏷️ {gasto['categoria']} - {config_manager.get_formatted_currency(gasto['total'])}")
                else:
                    # Formato anterior: movimiento individual
                    st.write(f"**#{i}** 💸 {gasto.concepto} - {config_manager.get_formatted_currency(gasto.monto_absoluto)} ({gasto.categoria})")
        else:
            st.info("No hay gastos registrados")
        
        st.divider()
    
    # Navegar a la página correspondiente
    if pagina_actual == "dashboard":
        # Dashboard principal (ya se muestra arriba)
        pass
    elif pagina_actual == "cuentas":
        # Siempre usar main() que incluye el formulario completo de agregar cuenta
        import importlib.util
        spec = importlib.util.spec_from_file_location("cuentas", "pages/1_Cuentas.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.main()
    elif pagina_actual == "movimientos":
        # Siempre usar main() que incluye el formulario completo de agregar movimiento
        import importlib.util
        spec = importlib.util.spec_from_file_location("movimientos", "pages/2_Movimientos.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.main()
    elif pagina_actual == "reportes":
        # Importar y ejecutar main() del archivo de reportes
        import importlib.util
        spec = importlib.util.spec_from_file_location("reportes", "pages/3_Reportes.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.main()
    elif pagina_actual == "gastos_recurrentes":
        # Siempre usar main() que incluye el formulario completo de agregar gasto recurrente
        import importlib.util
        spec = importlib.util.spec_from_file_location("gastos_recurrentes", "pages/4_Gastos_Recurrentes.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.main()
    elif pagina_actual == "metas":
        # Siempre usar main() que incluye el formulario completo de editar metas
        import importlib.util
        spec = importlib.util.spec_from_file_location("metas", "pages/5_Metas.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.main()
    elif pagina_actual == "configuracion":
        if mostrar_configuracion:
            mostrar_configuracion()
        else:
            import importlib.util
            spec = importlib.util.spec_from_file_location("configuracion", "pages/6_Configuracion.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.main()
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


if __name__ == "__main__":
    main()
