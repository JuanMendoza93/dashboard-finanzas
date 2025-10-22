"""
Sistema de configuraciones centralizadas
"""

import json
import os
from typing import Any, Dict, Optional, Union
from datetime import datetime
from utils.database import firebase_get, firebase_set


class ConfigManager:
    """Gestor de configuraciones centralizadas"""
    
    def __init__(self):
        self.config_file = "config/app_config.json"
        self.default_config = self._get_default_config()
        self._ensure_config_exists()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Obtener configuración por defecto"""
        return {
            "app": {
                "name": "Dashboard Financiero",
                "version": "2.0.0",
                "description": "Sistema de gestión financiera personal"
            },
            "finances": {
                "presupuesto_base": 10000.0,
                "meta_mensual": 5000.0,
                "meta_anual": 60000.0,
                "moneda": "USD",
                "decimales": 2
            },
            "ui": {
                "tema": "light",
                "colores": {
                    "primario": "#667eea",
                    "secundario": "#764ba2",
                    "exito": "#28a745",
                    "advertencia": "#ffc107",
                    "peligro": "#dc3545"
                },
                "metricas": {
                    "mostrar_graficos": True,
                    "mostrar_tablas": True,
                    "items_por_pagina": 10
                }
            },
            "firebase": {
                "timeout": 10,
                "reintentos": 3,
                "cache_ttl": 300
            },
            "validaciones": {
                "monto_minimo": 0.01,
                "monto_maximo": 999999.99,
                "nombre_min_length": 2,
                "nombre_max_length": 50,
                "concepto_min_length": 3,
                "concepto_max_length": 100
            },
            "reportes": {
                "formato_fecha": "%d/%m/%Y",
                "formato_moneda": "${:,.2f}",
                "graficos_por_defecto": ["gastos_por_categoria", "progreso_ahorro"],
                "exportar_formato": "excel"
            },
            "notificaciones": {
                "mostrar_success": True,
                "mostrar_errors": True,
                "mostrar_warnings": True,
                "auto_close_delay": 5
            },
            "categorias_default": [
                "Comida", "Transporte", "Vivienda", "Entretenimiento", 
                "Salud", "Educación", "Ropa", "Servicios", "Otros"
            ],
            "tipos_gasto_default": [
                "Necesario", "Innecesario", "Emergencia", "Lujo", 
                "Inversión", "Ahorro"
            ],
            "metas": {
                "ahorro_mensual_objetivo": 5000.0,
                "ahorro_anual_objetivo": 60000.0,
                "gasto_maximo_mensual": 8000.0,
                "reserva_emergencia": 10000.0
            },
            "presupuesto": {
                "porcentaje_ahorro": 20.0,
                "porcentaje_gastos_fijos": 50.0,
                "porcentaje_gastos_variables": 30.0,
                "alerta_presupuesto": 80.0
            }
        }
    
    def _ensure_config_exists(self):
        """Asegurar que existe el archivo de configuración"""
        if not os.path.exists(self.config_file):
            self._save_config(self.default_config)
    
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración desde archivo"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.default_config.copy()
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Guardar configuración en archivo"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando configuración: {e}")
            return False
    
    def get_config(self, key: str = None) -> Any:
        """Obtener configuración"""
        config = self._load_config()
        
        if key is None:
            return config
        
        # Soporte para claves anidadas (ej: "finances.presupuesto_base")
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def set_config(self, key: str, value: Any) -> bool:
        """Establecer configuración"""
        config = self._load_config()
        
        # Soporte para claves anidadas
        keys = key.split('.')
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        
        return self._save_config(config)
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Actualizar múltiples configuraciones"""
        config = self._load_config()
        
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
        
        config = deep_update(config, updates)
        return self._save_config(config)
    
    def reset_to_default(self) -> bool:
        """Resetear a configuración por defecto"""
        return self._save_config(self.default_config.copy())
    
    def get_financial_config(self) -> Dict[str, Any]:
        """Obtener configuración financiera"""
        return self.get_config("finances") or {}
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Obtener configuración de UI"""
        return self.get_config("ui") or {}
    
    def get_validation_config(self) -> Dict[str, Any]:
        """Obtener configuración de validaciones"""
        return self.get_config("validaciones") or {}
    
    def get_report_config(self) -> Dict[str, Any]:
        """Obtener configuración de reportes"""
        return self.get_config("reportes") or {}
    
    def get_metas_config(self) -> Dict[str, Any]:
        """Obtener configuración de metas"""
        return self.get_config("metas") or {}
    
    def get_presupuesto_config(self) -> Dict[str, Any]:
        """Obtener configuración de presupuesto"""
        return self.get_config("presupuesto") or {}
    
    def sync_with_firebase(self) -> bool:
        """Sincronizar configuraciones con Firebase"""
        try:
            # Obtener configuraciones de Firebase
            firebase_config = firebase_get("configuracion")
            if firebase_config:
                # Actualizar configuración local con datos de Firebase
                self.update_config({"firebase_sync": firebase_config})
                return True
            return False
        except Exception as e:
            print(f"Error sincronizando con Firebase: {e}")
            return False
    
    def save_to_firebase(self) -> bool:
        """Guardar configuraciones en Firebase"""
        try:
            config = self._load_config()
            return firebase_set("configuracion", config)
        except Exception as e:
            print(f"Error guardando en Firebase: {e}")
            return False
    
    def get_formatted_currency(self, amount: float) -> str:
        """Obtener moneda formateada según configuración"""
        config = self.get_financial_config()
        formato = config.get("formato_moneda", "${:,.2f}")
        decimales = config.get("decimales", 2)
        
        if "{:,.2f}" in formato:
            formato = formato.replace("{:,.2f}", f"{{:,.{decimales}f}}")
        
        return formato.format(amount)
    
    def get_formatted_date(self, date_obj: datetime) -> str:
        """Obtener fecha formateada según configuración"""
        config = self.get_report_config()
        formato = config.get("formato_fecha", "%d/%m/%Y")
        return date_obj.strftime(formato)
    
    def get_validation_limits(self) -> Dict[str, Any]:
        """Obtener límites de validación"""
        return self.get_validation_config()
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Verificar si una característica está habilitada"""
        config = self.get_config("features")
        return config.get(feature, True) if config else True
    
    def get_app_info(self) -> Dict[str, str]:
        """Obtener información de la aplicación"""
        return self.get_config("app") or {}


class FinancialConfig:
    """Configuración específica para finanzas"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
    
    def get_presupuesto_base(self) -> float:
        """Obtener presupuesto base"""
        return self.config_manager.get_config("finances.presupuesto_base") or 10000.0
    
    def set_presupuesto_base(self, value: float) -> bool:
        """Establecer presupuesto base"""
        return self.config_manager.set_config("finances.presupuesto_base", value)
    
    def get_meta_mensual(self) -> float:
        """Obtener meta mensual"""
        return self.config_manager.get_config("finances.meta_mensual") or 5000.0
    
    def set_meta_mensual(self, value: float) -> bool:
        """Establecer meta mensual"""
        return self.config_manager.set_config("finances.meta_mensual", value)
    
    def get_meta_anual(self) -> float:
        """Obtener meta anual"""
        return self.config_manager.get_config("finances.meta_anual") or 60000.0
    
    def set_meta_anual(self, value: float) -> bool:
        """Establecer meta anual"""
        return self.config_manager.set_config("finances.meta_anual", value)
    
    def get_moneda(self) -> str:
        """Obtener símbolo de moneda"""
        return self.config_manager.get_config("finances.moneda") or "USD"
    
    def get_decimales(self) -> int:
        """Obtener número de decimales"""
        return self.config_manager.get_config("finances.decimales") or 2


class UIConfig:
    """Configuración específica para UI"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
    
    def get_tema(self) -> str:
        """Obtener tema actual"""
        return self.config_manager.get_config("ui.tema") or "light"
    
    def get_colores(self) -> Dict[str, str]:
        """Obtener colores del tema"""
        return self.config_manager.get_config("ui.colores") or {}
    
    def get_color(self, color_name: str) -> str:
        """Obtener color específico"""
        colores = self.get_colores()
        return colores.get(color_name, "#667eea")
    
    def get_items_por_pagina(self) -> int:
        """Obtener items por página"""
        return self.config_manager.get_config("ui.metricas.items_por_pagina") or 10
    
    def should_show_charts(self) -> bool:
        """Verificar si mostrar gráficos"""
        return self.config_manager.get_config("ui.metricas.mostrar_graficos") or True


# Instancias globales
config_manager = ConfigManager()
financial_config = FinancialConfig(config_manager)
ui_config = UIConfig(config_manager)
