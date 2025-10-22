"""
Configuraciones externas del dashboard financiero
"""

from typing import Dict, List, Any
from datetime import datetime


class DashboardConfig:
    """Configuración principal del dashboard"""
    
    # Configuración de la página
    PAGE_CONFIG = {
        "page_title": "Dashboard Finanzas",
        "page_icon": "💰",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    # Configuración de colores
    COLORS = {
        "primary": "#667eea",
        "secondary": "#764ba2",
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#dc3545",
        "info": "#17a2b8",
        "light": "#f8f9fa",
        "dark": "#343a40"
    }
    
    # Configuración de métricas
    METRICS = {
        "saldo_total": {
            "title": "💰 Saldo Total",
            "icon": "💰",
            "color": "success"
        },
        "gastos_mes": {
            "title": "💸 Gastos del Mes",
            "icon": "💸",
            "color": "danger"
        },
        "ingresos_mes": {
            "title": "📈 Ingresos del Mes",
            "icon": "📈",
            "color": "info"
        },
        "ahorro_actual": {
            "title": "💎 Ahorro Actual",
            "icon": "💎",
            "color": "success"
        }
    }
    
    # Configuración de navegación
    NAVIGATION = {
        "cuentas": {
            "title": "🏦 Cuentas",
            "icon": "🏦",
            "description": "Gestionar cuentas bancarias"
        },
        "movimientos": {
            "title": "💰 Movimientos",
            "icon": "💰",
            "description": "Registrar movimientos financieros"
        },
        "reportes": {
            "title": "📊 Reportes",
            "icon": "📊",
            "description": "Ver análisis y reportes"
        },
        "configuracion": {
            "title": "⚙️ Configuración",
            "icon": "⚙️",
            "description": "Configurar categorías y tipos"
        },
        "firebase_test": {
            "title": "🔥 Prueba Firebase",
            "icon": "🔥",
            "description": "Probar conexión a Firebase"
        }
    }
    
    # Configuración de formularios
    FORMS = {
        "nueva_cuenta": {
            "title": "➕ Agregar Nueva Cuenta",
            "fields": {
                "nombre": {
                    "label": "📝 Nombre de la Cuenta",
                    "type": "text",
                    "required": True,
                    "placeholder": "Ej: Cuenta Principal"
                },
                "saldo_inicial": {
                    "label": "💰 Saldo Inicial",
                    "type": "number",
                    "required": True,
                    "min_value": 0.0,
                    "step": 0.01
                }
            }
        },
        "nuevo_movimiento": {
            "title": "➕ Agregar Nuevo Movimiento",
            "fields": {
                "fecha": {
                    "label": "📅 Fecha",
                    "type": "date",
                    "required": True,
                    "default": "today"
                },
                "concepto": {
                    "label": "📝 Concepto",
                    "type": "text",
                    "required": True,
                    "placeholder": "Ej: Compra en supermercado"
                },
                "categoria": {
                    "label": "🏷️ Categoría",
                    "type": "selectbox",
                    "required": True,
                    "options": "categorias"
                },
                "tipo_gasto": {
                    "label": "🔍 Tipo de Gasto",
                    "type": "selectbox",
                    "required": True,
                    "options": "tipos_gasto"
                },
                "monto": {
                    "label": "💰 Monto",
                    "type": "number",
                    "required": True,
                    "min_value": 0.0,
                    "step": 0.01
                },
                "tipo": {
                    "label": "📊 Tipo",
                    "type": "radio",
                    "required": True,
                    "options": ["Gasto", "Ingreso"]
                }
            }
        }
    }
    
    # Configuración de mensajes
    MESSAGES = {
        "success": {
            "cuenta_creada": "✅ Cuenta '{nombre}' agregada exitosamente!",
            "cuenta_actualizada": "✅ Cuenta actualizada exitosamente!",
            "cuenta_eliminada": "✅ Cuenta '{nombre}' eliminada exitosamente!",
            "movimiento_creado": "✅ Movimiento guardado exitosamente!",
            "movimiento_eliminado": "✅ Movimiento eliminado exitosamente!",
            "configuracion_guardada": "✅ Configuración guardada exitosamente!",
            "firebase_conectado": "✅ Firebase está funcionando correctamente!"
        },
        "error": {
            "cuenta_no_creada": "❌ Error al crear la cuenta",
            "cuenta_no_actualizada": "❌ Error al actualizar la cuenta",
            "cuenta_no_eliminada": "❌ Error al eliminar la cuenta",
            "movimiento_no_creado": "❌ Error al guardar el movimiento",
            "movimiento_no_eliminado": "❌ Error al eliminar el movimiento",
            "firebase_no_conectado": "❌ Firebase no está respondiendo",
            "campos_requeridos": "❌ Por favor completa todos los campos requeridos",
            "monto_invalido": "❌ El monto debe ser mayor a 0",
            "fecha_invalida": "❌ La fecha no puede ser futura"
        },
        "warning": {
            "sin_datos": "⚠️ No hay datos para mostrar",
            "sin_cuentas": "ℹ️ No hay cuentas bancarias registradas",
            "sin_movimientos": "ℹ️ No hay movimientos registrados",
            "presupuesto_excedido": "⚠️ Has excedido el presupuesto",
            "meta_no_cumplida": "⚠️ No has cumplido la meta de ahorro"
        },
        "info": {
            "cargando": "🔄 Cargando datos...",
            "guardando": "💾 Guardando...",
            "procesando": "⚙️ Procesando...",
            "conectando_firebase": "🔥 Conectando a Firebase..."
        }
    }
    
    # Configuración de validaciones
    VALIDATIONS = {
        "nombre_cuenta": {
            "min_length": 2,
            "max_length": 50,
            "pattern": r"^[a-zA-Z0-9\s]+$"
        },
        "concepto_movimiento": {
            "min_length": 3,
            "max_length": 100,
            "pattern": r"^[a-zA-Z0-9\s\-_.,]+$"
        },
        "monto": {
            "min_value": 0.01,
            "max_value": 999999.99,
            "decimal_places": 2
        },
        "fecha": {
            "max_date": "today",
            "min_date": "2020-01-01"
        }
    }
    
    # Configuración de gráficos
    CHARTS = {
        "gastos_por_categoria": {
            "type": "bar",
            "title": "Gastos por Categoría",
            "x_title": "Categoría",
            "y_title": "Monto ($)",
            "color": "lightblue"
        },
        "progreso_ahorro": {
            "type": "gauge",
            "title": "Progreso de Ahorro",
            "min_value": 0,
            "max_value": 100,
            "color": "darkblue"
        },
        "presupuesto_vs_gastos": {
            "type": "bar",
            "title": "Presupuesto vs Gastos",
            "x_title": "Concepto",
            "y_title": "Monto ($)",
            "colors": ["lightgreen", "lightcoral"]
        }
    }
    
    # Configuración de reportes
    REPORTS = {
        "resumen_general": {
            "title": "📊 Resumen General",
            "sections": ["gastos_por_categoria", "top_gastos"]
        },
        "presupuesto": {
            "title": "💰 Reporte de Presupuesto",
            "sections": ["metricas_presupuesto", "grafico_presupuesto", "estado_presupuesto"]
        },
        "metas": {
            "title": "🎯 Reporte de Metas",
            "sections": ["metricas_metas", "graficos_progreso", "estado_metas"]
        },
        "analisis": {
            "title": "📈 Análisis Detallado",
            "sections": ["analisis_categoria", "analisis_temporal"]
        }
    }
    
    # Configuración de Firebase
    FIREBASE = {
        "timeout": 10,
        "retry_attempts": 3,
        "collections": {
            "cuentas": "cuentas",
            "movimientos": "movimientos",
            "metas": "metas",
            "presupuesto": "presupuesto",
            "configuracion": "configuracion",
            "gastos_recurrentes": "gastos_recurrentes"
        }
    }
    
    # Configuración de paginación
    PAGINATION = {
        "items_per_page": 10,
        "max_items": 100
    }
    
    # Configuración de cache
    CACHE = {
        "ttl": 300,  # 5 minutos
        "max_entries": 100
    }


class UIConfig:
    """Configuración de interfaz de usuario"""
    
    # Configuración de columnas
    COLUMNS = {
        "metrics": 4,
        "form": 2,
        "actions": 3,
        "navigation": 1
    }
    
    # Configuración de botones
    BUTTONS = {
        "primary": {
            "type": "primary",
            "use_container_width": True
        },
        "secondary": {
            "type": "secondary",
            "use_container_width": True
        },
        "danger": {
            "type": "secondary",
            "use_container_width": True
        }
    }
    
    # Configuración de expanders
    EXPANDERS = {
        "default": {
            "expanded": False
        },
        "form": {
            "expanded": True
        }
    }
    
    # Configuración de tabs
    TABS = {
        "reportes": ["📊 Resumen", "💰 Presupuesto", "🎯 Metas", "📈 Análisis"]
    }


class ValidationConfig:
    """Configuración de validaciones"""
    
    # Patrones de validación
    PATTERNS = {
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "phone": r"^\+?1?-?\.?\s?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})$",
        "currency": r"^\$?[\d,]+\.?\d{0,2}$"
    }
    
    # Límites de validación
    LIMITS = {
        "text": {
            "min_length": 1,
            "max_length": 255
        },
        "number": {
            "min_value": 0,
            "max_value": 999999.99
        },
        "date": {
            "min_date": "2020-01-01",
            "max_date": "2030-12-31"
        }
    }


# Instancias globales de configuración
dashboard_config = DashboardConfig()
ui_config = UIConfig()
validation_config = ValidationConfig()
