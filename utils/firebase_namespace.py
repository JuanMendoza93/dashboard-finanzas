"""
Sistema de namespaces para Firebase
Permite organizar datos en módulos (financiero, nutricional, etc.)
"""

from typing import Optional

# Configuración de namespaces
NAMESPACES = {
    "financiero": "financiero",
    "nutricional": "nutricional"
}

# Mapeo de colecciones a namespaces
COLLECTION_NAMESPACES = {
    # Colecciones financieras
    "configuracion": "financiero",
    "cuentas": "financiero",
    "gastos_recurrentes": "financiero",
    "metas": "financiero",
    "movimientos": "financiero",
    "reportes_mensuales": "financiero",
    
    # Colecciones nutricionales (futuro)
    "comidas": "nutricional",
    "registros_diarios": "nutricional",
    "metas_caloricas": "nutricional",
    "peso_historico": "nutricional",
    "configuracion_nutricional": "nutricional",
}


def get_namespace_path(collection: str, namespace: Optional[str] = None) -> str:
    """
    Obtener el path completo con namespace para una colección
    
    Args:
        collection: Nombre de la colección
        namespace: Namespace explícito (opcional). Si no se proporciona, se usa el mapeo
    
    Returns:
        Path completo con namespace (ej: "financiero/movimientos")
    """
    # Si se proporciona namespace explícito, usarlo
    if namespace:
        if namespace in NAMESPACES:
            return f"{NAMESPACES[namespace]}/{collection}"
        return f"{namespace}/{collection}"
    
    # Usar mapeo automático
    if collection in COLLECTION_NAMESPACES:
        namespace = COLLECTION_NAMESPACES[collection]
        return f"{NAMESPACES[namespace]}/{collection}"
    
    # Si no hay mapeo, usar raíz (para compatibilidad)
    return collection


def get_financial_path(collection: str) -> str:
    """Obtener path para colección financiera"""
    return get_namespace_path(collection, "financiero")


def get_nutrition_path(collection: str) -> str:
    """Obtener path para colección nutricional"""
    return get_namespace_path(collection, "nutricional")


def is_migrated() -> bool:
    """Verificar si la migración ya se realizó"""
    try:
        import requests
        from config.firebase_config import firebase_config
        
        # Usar requests directamente para evitar importación circular
        firebase_url = f"https://{firebase_config['projectId']}-default-rtdb.firebaseio.com"
        url = f"{firebase_url}/financiero.json"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # Verificar si existe y tiene contenido
            return bool(data and len(data) > 0)
        return False
    except:
        # Si hay error, asumir que no está migrado (modo seguro)
        return False

