"""
Validadores para datos de entrada del usuario
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import date, datetime
from config.settings import validation_config, dashboard_config


class DataValidator:
    """Clase para validar datos de entrada"""
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
        """Validar campos requeridos"""
        missing_fields = []
        
        for field in required_fields:
            if field not in data or not data[field] or (isinstance(data[field], str) and not data[field].strip()):
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields
    
    @staticmethod
    def validate_text_field(value: str, field_name: str, min_length: int = 1, max_length: int = 255) -> Tuple[bool, str]:
        """Validar campo de texto"""
        if not value or not isinstance(value, str):
            return False, f"{field_name} debe ser un texto válido"
        
        value = value.strip()
        if len(value) < min_length:
            return False, f"{field_name} debe tener al menos {min_length} caracteres"
        
        if len(value) > max_length:
            return False, f"{field_name} no puede tener más de {max_length} caracteres"
        
        return True, ""
    
    @staticmethod
    def validate_numeric_field(value: Any, field_name: str, min_value: float = 0, max_value: float = 999999.99) -> Tuple[bool, str]:
        """Validar campo numérico"""
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            return False, f"{field_name} debe ser un número válido"
        
        if numeric_value < min_value:
            return False, f"{field_name} debe ser mayor o igual a {min_value}"
        
        if numeric_value > max_value:
            return False, f"{field_name} no puede ser mayor a {max_value}"
        
        return True, ""
    
    @staticmethod
    def validate_date_field(date_value: date, field_name: str) -> Tuple[bool, str]:
        """Validar campo de fecha"""
        if not date_value:
            return False, f"{field_name} es requerido"
        
        if not isinstance(date_value, date):
            return False, f"{field_name} debe ser una fecha válida"
        
        if date_value > date.today():
            return False, f"{field_name} no puede ser una fecha futura"
        
        # Verificar fecha mínima
        min_date = date(2020, 1, 1)
        if date_value < min_date:
            return False, f"{field_name} no puede ser anterior a {min_date.strftime('%Y-%m-%d')}"
        
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validar email"""
        if not email:
            return False, "Email es requerido"
        
        pattern = validation_config.PATTERNS["email"]
        if not re.match(pattern, email):
            return False, "Email debe tener un formato válido"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Validar teléfono"""
        if not phone:
            return False, "Teléfono es requerido"
        
        pattern = validation_config.PATTERNS["phone"]
        if not re.match(pattern, phone):
            return False, "Teléfono debe tener un formato válido"
        
        return True, ""
    
    @staticmethod
    def validate_currency(amount: str) -> Tuple[bool, str]:
        """Validar formato de moneda"""
        if not amount:
            return False, "Monto es requerido"
        
        # Remover símbolos de moneda y espacios
        clean_amount = re.sub(r'[^\d.,]', '', amount)
        
        try:
            # Convertir a float
            if ',' in clean_amount and '.' in clean_amount:
                # Formato con comas y punto (ej: 1,234.56)
                clean_amount = clean_amount.replace(',', '')
            elif ',' in clean_amount:
                # Formato con comas como separador decimal (ej: 1234,56)
                clean_amount = clean_amount.replace(',', '.')
            
            float_value = float(clean_amount)
            if float_value < 0:
                return False, "El monto no puede ser negativo"
            
            return True, ""
        except ValueError:
            return False, "Formato de moneda inválido"


class CuentaValidator:
    """Validador específico para cuentas"""
    
    @staticmethod
    def validate_cuenta_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validar datos de cuenta"""
        errors = []
        
        # Validar nombre
        is_valid, error = DataValidator.validate_text_field(
            data.get("nombre", ""), 
            "Nombre de la cuenta",
            min_length=2,
            max_length=50
        )
        if not is_valid:
            errors.append(error)
        
        # Validar saldo
        is_valid, error = DataValidator.validate_numeric_field(
            data.get("saldo", 0),
            "Saldo inicial",
            min_value=0
        )
        if not is_valid:
            errors.append(error)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_cuenta_update(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validar actualización de cuenta"""
        errors = []
        
        # Validar nombre
        if "nombre" in data:
            is_valid, error = DataValidator.validate_text_field(
                data["nombre"], 
                "Nombre de la cuenta",
                min_length=2,
                max_length=50
            )
            if not is_valid:
                errors.append(error)
        
        # Validar saldo
        if "saldo" in data:
            is_valid, error = DataValidator.validate_numeric_field(
                data["saldo"],
                "Saldo",
                min_value=0
            )
            if not is_valid:
                errors.append(error)
        
        return len(errors) == 0, errors


class MovimientoValidator:
    """Validador específico para movimientos"""
    
    @staticmethod
    def validate_movimiento_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validar datos de movimiento"""
        errors = []
        
        # Validar concepto
        is_valid, error = DataValidator.validate_text_field(
            data.get("concepto", ""), 
            "Concepto",
            min_length=3,
            max_length=100
        )
        if not is_valid:
            errors.append(error)
        
        # Validar monto
        is_valid, error = DataValidator.validate_numeric_field(
            data.get("monto", 0),
            "Monto",
            min_value=0.01
        )
        if not is_valid:
            errors.append(error)
        
        # Validar fecha
        if "fecha" in data:
            is_valid, error = DataValidator.validate_date_field(
                data["fecha"],
                "Fecha"
            )
            if not is_valid:
                errors.append(error)
        
        # Validar tipo
        if "tipo" in data:
            if data["tipo"] not in ["Gasto", "Ingreso"]:
                errors.append("Tipo debe ser 'Gasto' o 'Ingreso'")
        
        # Validar categoría
        if "categoria" in data:
            if not data["categoria"] or not isinstance(data["categoria"], str):
                errors.append("Categoría es requerida")
        
        # Validar tipo de gasto
        if "tipo_gasto" in data:
            if not data["tipo_gasto"] or not isinstance(data["tipo_gasto"], str):
                errors.append("Tipo de gasto es requerido")
        
        return len(errors) == 0, errors


class ConfiguracionValidator:
    """Validador específico para configuración"""
    
    @staticmethod
    def validate_categoria(categoria: str) -> Tuple[bool, str]:
        """Validar categoría"""
        return DataValidator.validate_text_field(
            categoria,
            "Categoría",
            min_length=2,
            max_length=30
        )
    
    @staticmethod
    def validate_tipo_gasto(tipo: str) -> Tuple[bool, str]:
        """Validar tipo de gasto"""
        return DataValidator.validate_text_field(
            tipo,
            "Tipo de gasto",
            min_length=2,
            max_length=30
        )
    
    @staticmethod
    def validate_meta_ahorro(meta: float, tipo: str) -> Tuple[bool, str]:
        """Validar meta de ahorro"""
        return DataValidator.validate_numeric_field(
            meta,
            f"Meta {tipo}",
            min_value=0
        )


class PresupuestoValidator:
    """Validador específico para presupuesto"""
    
    @staticmethod
    def validate_presupuesto_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validar datos de presupuesto"""
        errors = []
        
        # Validar presupuesto base
        if "presupuesto_base" in data:
            is_valid, error = DataValidator.validate_numeric_field(
                data["presupuesto_base"],
                "Presupuesto base",
                min_value=0
            )
            if not is_valid:
                errors.append(error)
        
        # Validar gastos recurrentes
        if "gastos_recurrentes" in data:
            is_valid, error = DataValidator.validate_numeric_field(
                data["gastos_recurrentes"],
                "Gastos recurrentes",
                min_value=0
            )
            if not is_valid:
                errors.append(error)
        
        return len(errors) == 0, errors


class FormValidator:
    """Validador para formularios completos"""
    
    @staticmethod
    def validate_form_data(form_name: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """Validar datos de formulario completo"""
        errors = {}
        
        if form_name == "nueva_cuenta":
            is_valid, error_list = CuentaValidator.validate_cuenta_data(data)
            if not is_valid:
                for i, error in enumerate(error_list):
                    errors[f"field_{i}"] = error
        
        elif form_name == "nuevo_movimiento":
            is_valid, error_list = MovimientoValidator.validate_movimiento_data(data)
            if not is_valid:
                for i, error in enumerate(error_list):
                    errors[f"field_{i}"] = error
        
        elif form_name == "actualizar_cuenta":
            is_valid, error_list = CuentaValidator.validate_cuenta_update(data)
            if not is_valid:
                for i, error in enumerate(error_list):
                    errors[f"field_{i}"] = error
        
        elif form_name == "presupuesto":
            is_valid, error_list = PresupuestoValidator.validate_presupuesto_data(data)
            if not is_valid:
                for i, error in enumerate(error_list):
                    errors[f"field_{i}"] = error
        
        return len(errors) == 0, errors


# Instancias globales de validadores
data_validator = DataValidator()
cuenta_validator = CuentaValidator()
movimiento_validator = MovimientoValidator()
configuracion_validator = ConfiguracionValidator()
presupuesto_validator = PresupuestoValidator()
form_validator = FormValidator()
