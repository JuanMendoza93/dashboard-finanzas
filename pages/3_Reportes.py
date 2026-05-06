"""
Reportes y Análisis Financiero
Página para visualizar reportes detallados
"""

import streamlit as st
from datetime import datetime, timedelta
from services.reporte_service import ReporteService
from services.movimiento_service import MovimientoService
from services.cuenta_service import CuentaService
from utils.config_manager import config_manager
from utils.helpers import apply_css_styles
import plotly.graph_objects as go
import plotly.express as px


def main():
    """Función principal de la página de reportes"""
    
    # Aplicar CSS personalizado
    apply_css_styles()
    
    # Navegación lateral personalizada
    from utils.helpers import mostrar_navegacion_lateral
    mostrar_navegacion_lateral()
    
    st.title("📊 Reportes y Análisis")
    
    # Obtener datos
    resumen = ReporteService.generar_resumen_financiero()
    reporte_ahorro = ReporteService.generar_reporte_ahorro()
    
    # Tabs para diferentes reportes
    tab1, tab2 = st.tabs(["📈 Análisis Mensual", "📊 Análisis Anual"])
    
    with tab1:
        mostrar_analisis_detallado()
    
    with tab2:
        mostrar_analisis_anual()




def mostrar_analisis_detallado():
    """Mostrar análisis temporal detallado"""
    
    st.subheader("📈 Análisis por Mes")
    
    # Verificar y generar reporte mensual si es necesario (último día del mes)
    ReporteService.verificar_y_generar_reporte_mensual()
    
    # Botones para generar reportes
    ahora = datetime.now()
    
    # Calcular mes anterior
    mes_anterior = ahora.month - 1
    año_anterior = ahora.year
    if mes_anterior == 0:
        mes_anterior = 12
        año_anterior = ahora.year - 1
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("🔄 Mes Actual", use_container_width=True, help="Regenera el reporte del mes actual con los datos más recientes"):
            if ReporteService.generar_reporte_mensual(ahora.month, ahora.year):
                st.success(f"✅ Reporte de {ahora.strftime('%B %Y')} regenerado correctamente")
                st.rerun()
            else:
                st.error("❌ Error al regenerar el reporte")
    with col3:
        nombre_mes_anterior = datetime(año_anterior, mes_anterior, 1).strftime('%B %Y')
        if st.button("📅 Mes Anterior", use_container_width=True, help=f"Genera o regenera el reporte de {nombre_mes_anterior}"):
            if ReporteService.generar_reporte_mensual(mes_anterior, año_anterior):
                st.success(f"✅ Reporte de {nombre_mes_anterior} generado correctamente")
                st.rerun()
            else:
                st.error("❌ Error al generar el reporte")
    
    # Obtener datos desde Octubre 2025 hasta el mes actual
    ahora = datetime.now()
    año_inicio = 2025
    mes_inicio = 10  # Octubre
    
    meses_datos = []
    gastos_mensuales = []
    ingresos_mensuales = []
    ahorros_mensuales = []
    ahorros_reales = []
    saldos_mensuales = []
    meses_labels = []
    
    # Calcular desde Octubre 2025 hasta el mes actual
    año_actual = ahora.year
    mes_actual = ahora.month
    
    # Obtener saldo inicial (saldo total de cuentas al inicio del primer mes)
    saldo_anterior = 0
    if año_inicio == 2025 and mes_inicio == 10:
        # Para el primer mes, obtener el saldo guardado en reportes o calcular desde cuentas
        reportes = ReporteService.obtener_reportes_mensuales()
        if reportes and len(reportes) > 0:
            # Buscar el reporte más antiguo para obtener el saldo inicial
            primer_reporte = min(reportes, key=lambda x: (x.get("año", 0), x.get("mes", 0)))
            if primer_reporte and "saldo_final_mes" in primer_reporte:
                saldo_anterior = primer_reporte["saldo_final_mes"] - primer_reporte.get("ahorro_real", 0)
    
    # Crear diccionario de reportes para acceso rápido por año-mes
    reportes_guardados = ReporteService.obtener_reportes_mensuales()
    reportes_dict = {}
    if reportes_guardados and len(reportes_guardados) > 0:
        for reporte in reportes_guardados:
            año_reporte = reporte.get("año")
            mes_reporte = reporte.get("mes")
            if año_reporte and mes_reporte:
                reportes_dict[(año_reporte, mes_reporte)] = reporte
    
    for año in range(año_inicio, año_actual + 1):
        mes_start = mes_inicio if año == año_inicio else 1
        mes_end = mes_actual if año == año_actual else 12
        
        for mes in range(mes_start, mes_end + 1):
            # Obtener movimientos del mes
            movimientos_mes = MovimientoService.obtener_por_mes(mes, año)
            
            # Gastos: sumar todos los gastos y restar los pagos recibidos
            gastos_mov = [m for m in movimientos_mes if m.tipo == "Gasto"]
            pagos_recibidos = [m for m in movimientos_mes if m.tipo == "Pago"]
            gastos_mes = sum(m.monto_absoluto for m in gastos_mov) - sum(m.monto for m in pagos_recibidos)
            
            # Ingresos: solo movimientos tipo "Ingreso"
            ingresos_mov = [m for m in movimientos_mes if m.tipo == "Ingreso"]
            ingresos_mes = sum(m.monto for m in ingresos_mov)
            
            ahorro_mes = ingresos_mes - gastos_mes
            
            # Obtener saldo total guardado del reporte mensual (saldo total de cuentas al final del mes)
            # Si existe un reporte guardado para este mes, usarlo; si no, calcular desde el saldo actual
            saldo_final_mes = None
            if (año, mes) in reportes_dict:
                reporte_mes = reportes_dict[(año, mes)]
                saldo_final_mes = reporte_mes.get("saldo_final_mes")
            
            # Si no hay reporte guardado para este mes, usar el saldo actual de las cuentas
            if saldo_final_mes is None:
                cuentas = CuentaService.obtener_todas()
                saldo_final_mes = sum(cuenta.saldo for cuenta in cuentas)
            
            # Calcular ahorro real como la diferencia entre el saldo actual y el anterior
            ahorro_real = saldo_final_mes - saldo_anterior
            
            fecha_mes = datetime(año, mes, 1)
            meses_datos.append(fecha_mes)
            gastos_mensuales.append(gastos_mes)
            ingresos_mensuales.append(ingresos_mes)
            ahorros_mensuales.append(ahorro_mes)
            ahorros_reales.append(ahorro_real)
            saldos_mensuales.append(saldo_final_mes)
            
            # Actualizar saldo anterior para el próximo mes
            saldo_anterior = saldo_final_mes
            
            nombres_meses = [
                "Ene", "Feb", "Mar", "Abr", "May", "Jun",
                "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
            ]
            meses_labels.append(f"{nombres_meses[mes-1]} {año}")
    
    # Tabla de evaluación dentro de un expander (colapsada, arriba de la gráfica)
    with st.expander(f"📊 Ver Tabla de Análisis Mensual ({len(meses_labels)} meses)", expanded=False):
        import pandas as pd
        
        # Crear DataFrame con los datos
        df_data = {
            'Mes': meses_labels,
            'Gastos': [f"${g:,.2f}" for g in gastos_mensuales],
            'Ingresos': [f"${i:,.2f}" for i in ingresos_mensuales],
            'Ahorro': [f"${a:,.2f}" for a in ahorros_mensuales],
            'Ahorro Real': ahorros_reales,
            'Saldo': saldos_mensuales
        }
        df_evaluacion = pd.DataFrame(df_data)
        
        # Aplicar estilos de color al ahorro real
        def color_ahorro_real(val):
            if val > 0:
                return 'background-color: #90EE90; color: #006400; font-weight: bold'
            elif val < 0:
                return 'background-color: #FFB6C1; color: #8B0000; font-weight: bold'
            else:
                return 'background-color: #F0F0F0; color: #666666'
        
        # Crear DataFrame styled para aplicar colores y formatear
        styled_df = df_evaluacion.style.applymap(color_ahorro_real, subset=['Ahorro Real'])
        styled_df = styled_df.format({
            'Ahorro Real': '${:,.2f}',
            'Saldo': '${:,.2f}'
        })
        
        # Mostrar DataFrame sin índice
        st.dataframe(styled_df, use_container_width=True, height=400, hide_index=True)
    
    st.divider()
    
    # Gráfica de evolución (después de la tabla)
    st.subheader("📈 Evolución Temporal")
    
    # Crear gráfica con colores diferentes
    fig = go.Figure()
    
    # Línea de gastos en rojo
    fig.add_trace(go.Scatter(
        x=meses_labels,
        y=gastos_mensuales,
        mode='lines+markers',
        name='Gastos',
        line=dict(color='#DC143C', width=3),
        marker=dict(size=8, color='#DC143C')
    ))
    
    # Línea de ingresos en verde
    fig.add_trace(go.Scatter(
        x=meses_labels,
        y=ingresos_mensuales,
        mode='lines+markers',
        name='Ingresos',
        line=dict(color='#2E8B57', width=3),
        marker=dict(size=8, color='#2E8B57')
    ))
    
    # Línea de ahorro en azul
    fig.add_trace(go.Scatter(
        x=meses_labels,
        y=ahorros_mensuales,
        mode='lines+markers',
        name='Ahorro',
        line=dict(color='#4169E1', width=3),
        marker=dict(size=8, color='#4169E1')
    ))
    
    # Línea de ahorro real en naranja/dorado
    fig.add_trace(go.Scatter(
        x=meses_labels,
        y=ahorros_reales,
        mode='lines+markers',
        name='Ahorro Real',
        line=dict(color='#FF8C00', width=3),
        marker=dict(size=8, color='#FF8C00')
    ))
    
    fig.update_layout(
        title="Evolución de Gastos, Ingresos, Ahorro y Ahorro Real por Mes",
        xaxis_title="Mes",
        yaxis_title="Monto ($)",
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Agregar sección de Progreso Mensual
    st.divider()
    st.subheader("📅 Progreso Mensual")
    
    # Obtener metas desde la base de datos
    from utils.database import cargar_metas
    metas = cargar_metas()
    meta_mensual = metas.get("meta_mensual", 0)
    
    if meta_mensual > 0:
        # Obtener ahorro real y progreso desde el servicio (usa ahorro real)
        reporte_ahorro = ReporteService.generar_reporte_ahorro()
        ahorro_actual = reporte_ahorro.get("ahorro_actual", 0)
        progreso_mensual = reporte_ahorro.get("progreso_mensual", 0) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "💰 Ahorro del Mes Actual",
                config_manager.get_formatted_currency(ahorro_actual),
                delta=f"Meta: {config_manager.get_formatted_currency(meta_mensual)}"
            )
        
        with col2:
            st.metric(
                "📅 Progreso Mensual",
                f"{progreso_mensual:.1f}%",
                delta=f"Meta: {config_manager.get_formatted_currency(meta_mensual)}"
            )
        
        # Gráfico de progreso mensual (velocímetro)
        fig_mensual = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progreso_mensual,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Progreso Ahorro Mensual"},
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
        fig_mensual.update_layout(height=300)
        st.plotly_chart(fig_mensual, use_container_width=True)
        
        # Mostrar información adicional
        if progreso_mensual < 75:
            st.error("🔴 Necesitas más ahorro para alcanzar tu meta mensual")
        elif progreso_mensual < 100:
            st.warning("🟡 Estás cerca de tu meta mensual")
        elif progreso_mensual < 150:
            st.success("🟢 ¡Excelente! Has superado tu meta mensual")
        else:
            st.success("🟢 ¡Increíble! Has duplicado tu meta mensual")
    else:
        st.info("No hay meta mensual configurada")

def mostrar_analisis_anual():
    """Mostrar análisis anual de finanzas"""
    
    st.subheader("📊 Análisis Anual")
    
    # Obtener datos desde 2025 hasta el año actual
    ahora = datetime.now()
    año_actual = ahora.year
    año_inicio = 2025
    años_datos = []
    gastos_anuales = []
    ingresos_anuales = []
    ahorros_anuales = []
    saldos_iniciales_anuales = []
    saldos_finales_anuales = []
    años_labels = []
    
    # Calcular años a analizar (desde 2025 hasta el año actual)
    años_a_analizar = list(range(año_inicio, año_actual + 1))
    
    # Crear diccionario de reportes para acceso rápido
    reportes_anuales = ReporteService.obtener_reportes_mensuales()
    reportes_dict_anual = {}
    if reportes_anuales and len(reportes_anuales) > 0:
        for reporte in reportes_anuales:
            año_reporte = reporte.get("año")
            mes_reporte = reporte.get("mes")
            if año_reporte and mes_reporte:
                reportes_dict_anual[(año_reporte, mes_reporte)] = reporte
    
    for año_analisis in años_a_analizar:
        
        # Obtener todos los movimientos del año
        gastos_año = 0
        ingresos_año = 0
        
        # Obtener saldo inicial y saldo final considerando el mes de inicio
        # Para 2025, comienza en octubre; para otros años, comienza en enero
        mes_inicio_año = 10 if año_analisis == 2025 else 1
        mes_actual = ahora.month
        mes_fin_año = 12 if año_analisis != año_actual else mes_actual
        
        # Obtener saldo inicial (primer mes del período) y saldo final (último mes del período)
        saldo_inicial_año = 0
        saldo_final_año = 0
        
        for mes in range(1, 13):
            movimientos_mes = MovimientoService.obtener_por_mes(mes, año_analisis)
            
            # Gastos: sumar todos los gastos y restar los pagos recibidos
            gastos_mov = [m for m in movimientos_mes if m.tipo == "Gasto"]
            pagos_recibidos = [m for m in movimientos_mes if m.tipo == "Pago"]
            gastos_mes = sum(m.monto_absoluto for m in gastos_mov) - sum(m.monto for m in pagos_recibidos)
            
            # Ingresos: solo movimientos tipo "Ingreso"
            ingresos_mov = [m for m in movimientos_mes if m.tipo == "Ingreso"]
            ingresos_mes = sum(m.monto for m in ingresos_mov)
            
            # Solo contar meses dentro del rango del año
            if mes >= mes_inicio_año and mes <= mes_fin_año:
                gastos_año += gastos_mes
                ingresos_año += ingresos_mes
            
            # Obtener saldo del mes desde reportes o calcular
            saldo_mes = None
            if (año_analisis, mes) in reportes_dict_anual:
                reporte_mes = reportes_dict_anual[(año_analisis, mes)]
                saldo_mes = reporte_mes.get("saldo_final_mes")
            
            # Si no hay reporte guardado, usar el saldo actual de las cuentas
            if saldo_mes is None:
                cuentas = CuentaService.obtener_todas()
                saldo_mes = sum(cuenta.saldo for cuenta in cuentas)
            
            # Asignar saldo inicial (primer mes del período) y saldo final (último mes del período)
            if mes == mes_inicio_año:
                saldo_inicial_año = saldo_mes
            if mes == mes_fin_año:
                saldo_final_año = saldo_mes
        
        # Calcular ahorro real anual como la diferencia entre saldo final e inicial
        ahorro_real_año = saldo_final_año - saldo_inicial_año
        
        años_datos.append(año_analisis)
        gastos_anuales.append(gastos_año)
        ingresos_anuales.append(ingresos_año)
        ahorros_anuales.append(ahorro_real_año)
        saldos_iniciales_anuales.append(saldo_inicial_año)
        saldos_finales_anuales.append(saldo_final_año)
        años_labels.append(str(año_analisis))
    
    # Tabla de evaluación anual dentro de un expander (colapsada, arriba de la gráfica)
    with st.expander(f"📊 Ver Tabla de Análisis Anual ({len(años_labels)} años)", expanded=False):
        import pandas as pd
        
        df_anual = pd.DataFrame({
            'Año': años_labels[::-1],
            'Gastos': [f"${g:,.2f}" for g in gastos_anuales[::-1]],
            'Ingresos': [f"${i:,.2f}" for i in ingresos_anuales[::-1]],
            'Saldo Inicial': [f"${s:,.2f}" for s in saldos_iniciales_anuales[::-1]],
            'Saldo Final': [f"${s:,.2f}" for s in saldos_finales_anuales[::-1]],
            'Ahorro Real': ahorros_anuales[::-1]
        })
        
        # Aplicar estilos de color al ahorro real
        def color_ahorro_real_anual(val):
            if val > 0:
                return 'background-color: #90EE90; color: #006400; font-weight: bold'
            elif val < 0:
                return 'background-color: #FFB6C1; color: #8B0000; font-weight: bold'
            else:
                return 'background-color: #F0F0F0; color: #666666'
        
        styled_df_anual = df_anual.style.applymap(color_ahorro_real_anual, subset=['Ahorro Real'])
        styled_df_anual = styled_df_anual.format({'Ahorro Real': '${:,.2f}'})
        
        st.dataframe(styled_df_anual, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Gráfica de evolución anual (después de la tabla)
    st.subheader("📈 Evolución Anual")
    
    fig = go.Figure()
    
    # Línea de gastos en rojo
    fig.add_trace(go.Scatter(
        x=años_labels[::-1],
        y=gastos_anuales[::-1],
        mode='lines+markers',
        name='Gastos',
        line=dict(color='#DC143C', width=3),
        marker=dict(size=8, color='#DC143C')
    ))
    
    # Línea de ingresos en verde
    fig.add_trace(go.Scatter(
        x=años_labels[::-1],
        y=ingresos_anuales[::-1],
        mode='lines+markers',
        name='Ingresos',
        line=dict(color='#2E8B57', width=3),
        marker=dict(size=8, color='#2E8B57')
    ))
    
    # Línea de ahorro real en azul
    fig.add_trace(go.Scatter(
        x=años_labels[::-1],
        y=ahorros_anuales[::-1],
        mode='lines+markers',
        name='Ahorro Real',
        line=dict(color='#4169E1', width=3),
        marker=dict(size=8, color='#4169E1')
    ))
    
    fig.update_layout(
        title="Evolución de Gastos, Ingresos y Ahorro Real por Año",
        xaxis_title="Año",
        yaxis_title="Monto ($)",
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Agregar sección de Ahorro Anual Acumulado
    st.divider()
    st.subheader("💰 Ahorro Anual Acumulado")
    
    # Obtener metas desde la base de datos
    from utils.database import cargar_metas
    metas = cargar_metas()
    meta_anual = metas.get("meta_anual", 0)
    
    if meta_anual > 0:
        # Obtener ahorro acumulado y progreso desde el servicio (usa ahorro real)
        reporte_ahorro = ReporteService.generar_reporte_ahorro()
        ahorro_acumulado_anual = reporte_ahorro.get("ahorro_acumulado_anual", 0)
        progreso_anual = reporte_ahorro.get("progreso_anual", 0) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "💰 Ahorro Anual Acumulado",
                config_manager.get_formatted_currency(ahorro_acumulado_anual),
                delta=f"Meta: {config_manager.get_formatted_currency(meta_anual)}"
            )
        
        with col2:
            st.metric(
                "📅 Progreso Anual",
                f"{progreso_anual:.1f}%",
                delta=f"Meta: {config_manager.get_formatted_currency(meta_anual)}"
            )
        
        # Gráfico de progreso anual (velocímetro)
        fig_anual = go.Figure(go.Indicator(
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
        fig_anual.update_layout(height=300)
        st.plotly_chart(fig_anual, use_container_width=True)
        
        # Mostrar información adicional
        if progreso_anual < 75:
            st.error("🔴 Necesitas más ahorro para alcanzar tu meta anual")
        elif progreso_anual < 100:
            st.warning("🟡 Estás cerca de tu meta anual")
        elif progreso_anual < 150:
            st.success("🟢 ¡Excelente! Has superado tu meta anual")
        else:
            st.success("🟢 ¡Increíble! Has duplicado tu meta anual")
    else:
        st.info("No hay meta anual configurada")
    
    # Análisis de tipos de gasto del año actual
    st.divider()
    st.subheader("🔍 Análisis de Tipos de Gasto - Año Actual")
    
    ahora = datetime.now()
    gastos_por_tipo_anual = MovimientoService.obtener_gastos_por_tipo_anual(ahora.year)
    
    if gastos_por_tipo_anual:
        # Ordenar tipos por monto descendente
        tipos_ordenados_anual = sorted(gastos_por_tipo_anual.items(), key=lambda x: x[1], reverse=True)
        
        # Definir paleta de colores para tipos de gasto
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
        
        # Paleta de colores adicionales para tipos no definidos
        colores_adicionales = ['#FF1493', '#00CED1', '#FF69B4', '#8A2BE2', '#FF4500', 
                              '#00FF7F', '#4682B4', '#FF7F50', '#DA70D6', '#98FB98']
        
        # Asignar colores a cada tipo
        colores_lista = []
        tipos_lista = list(gastos_por_tipo_anual.keys())
        valores_lista = list(gastos_por_tipo_anual.values())
        
        for tipo in tipos_lista:
            if tipo in colores_por_tipo:
                colores_lista.append(colores_por_tipo[tipo])
            else:
                # Usar colores adicionales rotando si no hay color definido
                colores_lista.append(colores_adicionales[len(colores_lista) % len(colores_adicionales)])
        
        # Gráfico de pastel con colores diferentes
        st.markdown("**📊 Distribución de Gastos por Tipo de Gasto del Año:**")
        fig_pastel_tipos = go.Figure(data=[
            go.Pie(
                labels=tipos_lista,
                values=valores_lista,
                textinfo='label+percent+value',
                texttemplate='%{label}<br>%{percent}<br>$%{value:,.0f}',
                hovertemplate='<b>%{label}</b><br>Monto: $%{value:,.2f}<br>Porcentaje: %{percent}<extra></extra>',
                marker=dict(colors=colores_lista)
            )
        ])
        fig_pastel_tipos.update_layout(
            title=f"Distribución de Gastos por Tipo de Gasto del Año {ahora.year}",
            height=500
        )
        st.plotly_chart(fig_pastel_tipos, use_container_width=True)
    else:
        st.info("No hay gastos registrados por tipo para el año actual")
    
    # Análisis de categorías de gastos del año actual
    st.divider()
    st.subheader("🏷️ Análisis de Categorías - Año Actual")
    
    gastos_por_categoria_anual = MovimientoService.obtener_gastos_por_categoria_anual(ahora.year)
    
    if gastos_por_categoria_anual:
        # Ordenar categorías por monto descendente
        categorias_ordenadas_anual = sorted(gastos_por_categoria_anual.items(), key=lambda x: x[1], reverse=True)
        
        # Gráfico de pastel con todas las categorías del año
        st.markdown("**📊 Distribución Completa de Gastos por Categoría del Año:**")
        fig_pastel_anual = go.Figure(data=[
            go.Pie(
                labels=list(gastos_por_categoria_anual.keys()),
                values=list(gastos_por_categoria_anual.values()),
                textinfo='label+percent+value',
                texttemplate='%{label}<br>%{percent}<br>$%{value:,.0f}',
                hovertemplate='<b>%{label}</b><br>Monto: $%{value:,.2f}<br>Porcentaje: %{percent}<extra></extra>'
            )
        ])
        fig_pastel_anual.update_layout(
            title=f"Distribución de Gastos por Categoría del Año {ahora.year}",
            height=500
        )
        st.plotly_chart(fig_pastel_anual, use_container_width=True)
        
        # Análisis comparativo por año (si hay datos de años anteriores)
        st.divider()
        st.subheader("📈 Comparación de Categorías por Año")
        
        # Crear un selector para elegir el año a analizar
        año_seleccionado = st.selectbox(
            "Selecciona un año para ver su análisis de categorías:",
            años_a_analizar[::-1],
            index=0,
            key="selector_año_categorias"
        )
        
        if año_seleccionado:
            gastos_por_categoria_seleccionado = MovimientoService.obtener_gastos_por_categoria_anual(año_seleccionado)
            
            if gastos_por_categoria_seleccionado:
                categorias_ordenadas_seleccionado = sorted(
                    gastos_por_categoria_seleccionado.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                
                st.markdown(f"**🏷️ Top 5 Categorías de {año_seleccionado}:**")
                for i, (categoria, monto) in enumerate(categorias_ordenadas_seleccionado[:5], 1):
                    porcentaje = (monto / sum(gastos_por_categoria_seleccionado.values())) * 100
                    st.write(f"**#{i}** 🏷️ {categoria} - {config_manager.get_formatted_currency(monto)} ({porcentaje:.1f}%)")
                
                # Gráfico de barras para el año seleccionado con colores diferentes
                top_5_seleccionado = dict(categorias_ordenadas_seleccionado[:5])
                
                # Paleta de colores para las barras
                colores_barras = ['#DC143C', '#4169E1', '#2E8B57', '#FF8C00', '#9370DB', 
                                 '#FF1493', '#00CED1', '#FF69B4', '#8A2BE2', '#FF4500']
                
                fig_barras_seleccionado = go.Figure(data=[
                    go.Bar(
                        y=list(top_5_seleccionado.keys()),
                        x=list(top_5_seleccionado.values()),
                        orientation='h',
                        marker=dict(color=colores_barras[:len(top_5_seleccionado)]),
                        text=[f"${val:,.2f}" for val in top_5_seleccionado.values()],
                        textposition='auto'
                    )
                ])
                fig_barras_seleccionado.update_layout(
                    title=f"Top 5 Categorías de {año_seleccionado}",
                    xaxis_title="Monto ($)",
                    yaxis_title="Categoría",
                    height=300
                )
                st.plotly_chart(fig_barras_seleccionado, use_container_width=True)
            else:
                st.info(f"No hay gastos registrados para el año {año_seleccionado}")
    else:
        st.info("No hay gastos registrados para el año actual")


if __name__ == "__main__":
    main()