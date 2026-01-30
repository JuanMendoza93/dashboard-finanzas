import json
import os
from datetime import datetime
import requests
import streamlit as st
from config.firebase_config import firebase_config
from utils.firebase_namespace import get_financial_path, get_nutrition_path, is_migrated

# Configurar Firebase REST API
FIREBASE_URL = f"https://{firebase_config['projectId']}-default-rtdb.firebaseio.com"

# Flag para usar namespace (se activa después de migración)
USE_NAMESPACE = None  # Se detecta automáticamente

# Base de datos local para desarrollo (fallback)
DATA_FILE = "data.json"

# Inicializar datos si no existen
def init_data():
    if not os.path.exists(DATA_FILE):
        data = {
            "movimientos": [],
            "cuentas": [
                {"id": "1", "nombre": "Cuenta Principal", "saldo": 5000.0}
            ],
            "metas": {
                "meta_mensual": 10000,
                "meta_anual": 60000
            },
            "gastos_recurrentes": []
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def load_data():
    init_data()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Funciones para Firebase REST API
@st.cache_data(ttl=300, max_entries=50, show_spinner=False)
def _firebase_get_cached(url: str):
    """Función interna cacheada para consultas GET a Firebase"""
    try:
        print(f"[GET] Firebase GET (cached): {url}")
        response = requests.get(url, timeout=10)
        print(f"[DATA] Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json() or {}
            print(f"[OK] Firebase GET Success: {len(data) if isinstance(data, dict) else 'No data'}")
            return data
        return {}
    except Exception as e:
        print(f"[ERROR] Error Firebase GET: {e}")
        return {}

def _resolve_path(path: str) -> str:
    """
    Resolver path con namespace si es necesario
    
    Args:
        path: Path original (ej: "movimientos" o "financiero/movimientos")
    
    Returns:
        Path resuelto con namespace si aplica
    """
    global USE_NAMESPACE
    
    # Si el path ya incluye namespace, usarlo tal cual
    if "/" in path and path.split("/")[0] in ["financiero", "nutricional"]:
        return path
    
    # Detectar si se debe usar namespace (solo una vez)
    if USE_NAMESPACE is None:
        USE_NAMESPACE = is_migrated()
    
    # Si no está migrado, usar path original
    if not USE_NAMESPACE:
        return path
    
    # Si está migrado, agregar namespace financiero por defecto
    # (asumiendo que es una colección financiera)
    return get_financial_path(path)


def firebase_get(path=""):
    """Obtener datos de Firebase (con caché y namespace automático)"""
    try:
        resolved_path = _resolve_path(path)
        url = f"{FIREBASE_URL}/{resolved_path}.json"
        return _firebase_get_cached(url)
    except Exception as e:
        print(f"[ERROR] Error Firebase GET: {e}")
        return {}

def firebase_set(path, data):
    """Guardar datos en Firebase (invalida caché y usa namespace automático)"""
    try:
        resolved_path = _resolve_path(path)
        url = f"{FIREBASE_URL}/{resolved_path}.json"
        response = requests.put(url, json=data, timeout=10)
        if response.status_code == 200:
            # Invalidar caché relacionado
            _invalidate_cache_for_path(resolved_path)
            return True
        return False
    except Exception as e:
        print(f"Error Firebase SET: {e}")
        return False

def firebase_push(path, data):
    """Agregar datos a Firebase (invalida caché y usa namespace automático)"""
    try:
        resolved_path = _resolve_path(path)
        url = f"{FIREBASE_URL}/{resolved_path}.json"
        print(f"[PUSH] Firebase PUSH: {url}")
        print(f"[DATA] Data: {data}")
        response = requests.post(url, json=data, timeout=10)
        print(f"[DATA] Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Firebase PUSH Success: {result}")
            # Invalidar caché relacionado
            _invalidate_cache_for_path(resolved_path)
            return result
        return None
    except Exception as e:
        print(f"[ERROR] Error Firebase PUSH: {e}")
        return None

def firebase_delete(path):
    """Eliminar datos de Firebase (invalida caché y usa namespace automático)"""
    try:
        resolved_path = _resolve_path(path)
        url = f"{FIREBASE_URL}/{resolved_path}.json"
        response = requests.delete(url, timeout=10)
        if response.status_code == 200:
            # Invalidar caché relacionado
            _invalidate_cache_for_path(resolved_path)
            return True
        return False
    except Exception as e:
        print(f"Error Firebase DELETE: {e}")
        return False

# Clases para Firebase REST API
class FirebaseCollection:
    def __init__(self, collection_name):
        self.collection_name = collection_name
    
    def stream(self):
        data = firebase_get(self.collection_name)
        if isinstance(data, dict):
            for key, item in data.items():
                if isinstance(item, dict):
                    item['id'] = key
                    yield FirebaseDocument(item)
        else:
            # Fallback a datos locales si Firebase falla
            local_data = load_data()
            for item in local_data.get(self.collection_name, []):
                yield FirebaseDocument(item)
    
    def add(self, data):
        result = firebase_push(self.collection_name, data)
        if result and 'name' in result:
            data['id'] = result['name']
            return FirebaseDocument(data)
        else:
            # Fallback a datos locales si Firebase falla
            local_data = load_data()
            if self.collection_name not in local_data:
                local_data[self.collection_name] = []
            new_id = str(len(local_data[self.collection_name]) + 1)
            data['id'] = new_id
            local_data[self.collection_name].append(data)
            save_data(local_data)
            return FirebaseDocument(data)

class FirebaseDocument:
    def __init__(self, data):
        self.data = data
    
    def to_dict(self):
        return self.data

# Base de datos Firebase
class FirebaseDB:
    def collection(self, name):
        return FirebaseCollection(name)

# Inicializar la base de datos Firebase
db = FirebaseDB()

def cargar_movimientos():
    movimientos_ref = db.collection("movimientos")
    return [doc.to_dict() for doc in movimientos_ref.stream()]

def cargar_cuentas():
    cuentas_ref = db.collection("cuentas")
    return [doc.to_dict() for doc in cuentas_ref.stream()]

def guardar_movimiento(movimiento):
    db.collection("movimientos").add(movimiento)

def actualizar_meta_ahorro(meta_mensual, meta_anual):
    data = load_data()
    data["metas"]["meta_mensual"] = meta_mensual
    data["metas"]["meta_anual"] = meta_anual
    save_data(data)

def eliminar_cuenta(cuenta_id):
    data = load_data()
    data["cuentas"] = [c for c in data["cuentas"] if c["id"] != cuenta_id]
    save_data(data)

def cargar_configuracion():
    """Cargar configuración desde Firebase (usando namespace financiero)"""
    try:
        # Usar path con namespace financiero
        config_data = firebase_get(get_financial_path("configuracion"))
        if config_data:
            return config_data
        else:
            # Si no hay datos en Firebase, crear configuración por defecto
            config_default = {
                "categorias": ["Comida", "Transporte", "Vivienda", "Entretenimiento", "Salud", "Educación", "Otros"],
                "tipos_gasto": ["Necesario", "Innecesario", "Emergencia", "Lujo"]
            }
            firebase_set(get_financial_path("configuracion"), config_default)
            return config_default
    except Exception as e:
        print(f"Error cargando configuración: {e}")
        return {
            "categorias": ["Comida", "Transporte", "Vivienda", "Entretenimiento", "Salud", "Educación", "Otros"],
            "tipos_gasto": ["Necesario", "Innecesario", "Emergencia", "Lujo"]
        }

def guardar_configuracion(configuracion):
    """Guardar configuración completa en Firebase"""
    try:
        # Asegurar que siempre tenga las estructuras necesarias
        if "categorias" not in configuracion:
            configuracion["categorias"] = []
        if "tipos_gasto" not in configuracion:
            configuracion["tipos_gasto"] = []
        
        # Normalizar listas (eliminar duplicados preservando orden)
        categorias_normalizadas = []
        for cat in configuracion["categorias"]:
            cat_normalizada = str(cat).strip()
            if cat_normalizada and cat_normalizada.lower() not in [c.lower() for c in categorias_normalizadas]:
                categorias_normalizadas.append(cat_normalizada)
        
        tipos_normalizados = []
        for tipo in configuracion["tipos_gasto"]:
            tipo_normalizado = str(tipo).strip()
            if tipo_normalizado and tipo_normalizado.lower() not in [t.lower() for t in tipos_normalizados]:
                tipos_normalizados.append(tipo_normalizado)
        
        configuracion["categorias"] = categorias_normalizadas
        configuracion["tipos_gasto"] = tipos_normalizados
        
        return firebase_set(get_financial_path("configuracion"), configuracion)
    except Exception as e:
        print(f"Error guardando configuración: {e}")
        return False

def agregar_categoria(nueva_categoria):
    """Agregar una nueva categoría validando duplicados"""
    try:
        # Recargar configuración desde la base de datos para tener los datos más actuales
        configuracion = cargar_configuracion()
        
        # Normalizar la nueva categoría
        nueva_categoria = str(nueva_categoria).strip()
        
        if not nueva_categoria:
            return False, "El nombre de la categoría no puede estar vacío"
        
        # Validar duplicados (case-insensitive)
        categorias_lower = [c.lower() for c in configuracion.get("categorias", [])]
        if nueva_categoria.lower() in categorias_lower:
            return False, f"La categoría '{nueva_categoria}' ya existe"
        
        # Agregar la nueva categoría
        if "categorias" not in configuracion:
            configuracion["categorias"] = []
        configuracion["categorias"].append(nueva_categoria)
        
        # Guardar en la base de datos
        if guardar_configuracion(configuracion):
            return True, f"Categoría '{nueva_categoria}' agregada correctamente"
        else:
            return False, "Error al guardar la categoría en la base de datos"
    except Exception as e:
        print(f"Error agregando categoría: {e}")
        return False, f"Error: {str(e)}"

def agregar_tipo_gasto(nuevo_tipo):
    """Agregar un nuevo tipo de gasto validando duplicados"""
    try:
        # Recargar configuración desde la base de datos para tener los datos más actuales
        configuracion = cargar_configuracion()
        
        # Normalizar el nuevo tipo
        nuevo_tipo = str(nuevo_tipo).strip()
        
        if not nuevo_tipo:
            return False, "El nombre del tipo de gasto no puede estar vacío"
        
        # Validar duplicados (case-insensitive)
        tipos_lower = [t.lower() for t in configuracion.get("tipos_gasto", [])]
        if nuevo_tipo.lower() in tipos_lower:
            return False, f"El tipo de gasto '{nuevo_tipo}' ya existe"
        
        # Agregar el nuevo tipo
        if "tipos_gasto" not in configuracion:
            configuracion["tipos_gasto"] = []
        configuracion["tipos_gasto"].append(nuevo_tipo)
        
        # Guardar en la base de datos
        if guardar_configuracion(configuracion):
            return True, f"Tipo de gasto '{nuevo_tipo}' agregado correctamente"
        else:
            return False, "Error al guardar el tipo de gasto en la base de datos"
    except Exception as e:
        print(f"Error agregando tipo de gasto: {e}")
        return False, f"Error: {str(e)}"

def cargar_gastos_recurrentes():
    try:
        # Usar get_financial_path para apuntar a la nueva estructura
        gastos_data = firebase_get(get_financial_path("gastos_recurrentes"))
        if gastos_data:
            return gastos_data
        else:
            return []
    except Exception as e:
        print(f"Error cargando gastos recurrentes: {e}")
        return []

def guardar_gasto_recurrente(gasto):
    try:
        gastos_actuales = cargar_gastos_recurrentes()
        # Agregar ID único
        new_id = str(len(gastos_actuales) + 1)
        gasto['id'] = new_id
        gastos_actuales.append(gasto)
        # Usar get_financial_path para apuntar a la nueva estructura
        if firebase_set(get_financial_path("gastos_recurrentes"), gastos_actuales):
            return gasto
        return None
    except Exception as e:
        print(f"Error guardando gasto recurrente: {e}")
        return None

def eliminar_gasto_recurrente(gasto_id):
    try:
        gastos_actuales = cargar_gastos_recurrentes()
        gastos_actuales = [g for g in gastos_actuales if g["id"] != gasto_id]
        # Usar get_financial_path para apuntar a la nueva estructura
        return firebase_set(get_financial_path("gastos_recurrentes"), gastos_actuales)
    except Exception as e:
        print(f"Error eliminando gasto recurrente: {e}")
        return False

def actualizar_gasto_recurrente(gasto_id, datos_actualizados):
    """Actualizar un gasto recurrente existente"""
    try:
        gastos_actuales = cargar_gastos_recurrentes()
        for i, gasto in enumerate(gastos_actuales):
            if gasto["id"] == gasto_id:
                gastos_actuales[i].update(datos_actualizados)
                # Usar get_financial_path para apuntar a la nueva estructura
                return firebase_set(get_financial_path("gastos_recurrentes"), gastos_actuales)
        return False
    except Exception as e:
        print(f"Error actualizando gasto recurrente: {e}")
        return False

def actualizar_cuenta(cuenta_id, datos_actualizados):
    """Actualizar una cuenta en Firebase"""
    try:
        # Actualizar en Firebase usando la nueva estructura
        firebase_set(f"{get_financial_path('cuentas')}/{cuenta_id}", datos_actualizados)
        return True
    except:
        # Fallback a datos locales
        data = load_data()
        for i, cuenta in enumerate(data.get("cuentas", [])):
            if cuenta.get("id") == cuenta_id:
                data["cuentas"][i] = {**cuenta, **datos_actualizados}
                break
        save_data(data)
        return True

def agregar_dinero_cuenta(cuenta_id, monto):
    """Agregar dinero a una cuenta específica"""
    try:
        # Obtener datos actuales de la cuenta usando la nueva estructura
        cuenta_data = firebase_get(f"{get_financial_path('cuentas')}/{cuenta_id}")
        if cuenta_data:
            nuevo_saldo = float(cuenta_data.get("saldo", 0)) + monto
            datos_actualizados = {
                "nombre": cuenta_data.get("nombre", ""),
                "saldo": nuevo_saldo
            }
            firebase_set(f"{get_financial_path('cuentas')}/{cuenta_id}", datos_actualizados)
            return True
    except:
        # Fallback a datos locales
        data = load_data()
        for cuenta in data.get("cuentas", []):
            if cuenta.get("id") == cuenta_id:
                cuenta["saldo"] = float(cuenta.get("saldo", 0)) + monto
                break
        save_data(data)
        return True
    return False


def cargar_metas():
    """Cargar metas de ahorro"""
    try:
        # Intentar cargar desde Firebase usando la nueva estructura
        metas = firebase_get(get_financial_path("metas"))
        if metas:
            return metas
        
        # Fallback a datos locales
        data = load_data()
        return data.get("metas", {"meta_mensual": 0, "meta_anual": 0})
    except Exception as e:
        print(f"Error cargando metas: {e}")
        return {"meta_mensual": 0, "meta_anual": 0}


def guardar_metas(metas):
    """Guardar metas de ahorro"""
    try:
        # Intentar guardar en Firebase usando la nueva estructura
        if firebase_set(get_financial_path("metas"), metas):
            return True
        
        # Fallback a datos locales
        data = load_data()
        data["metas"] = metas
        save_data(data)
        return True
    except Exception as e:
        print(f"Error guardando metas: {e}")
        return False


def _invalidate_cache_for_path(path: str):
    """Invalidar caché basado en el path de Firebase"""
    try:
        # Extraer el nombre de la colección del path (puede tener namespace)
        # Ejemplos: "financiero/cuentas" -> "cuentas", "cuentas" -> "cuentas"
        path_parts = path.split("/")
        collection_name = path_parts[-1] if len(path_parts) > 1 else path_parts[0]
        
        # Si el path tiene namespace, extraer solo el nombre de la colección
        if len(path_parts) > 1 and path_parts[0] in ["financiero", "nutricional"]:
            collection_name = path_parts[1]
        
        # Mapear colecciones a funciones de caché específicas
        cache_functions = {
            'movimientos': [
                'services.movimiento_service.MovimientoService._obtener_todos_cached',
            ],
            'cuentas': [
                'services.cuenta_service.CuentaService._obtener_todas_cached',
            ],
            'configuracion': [
                'utils.database._firebase_get_cached',
            ],
            'gastos_recurrentes': [
                'utils.database._firebase_get_cached',
            ],
            'metas': [
                'utils.database._firebase_get_cached',
            ],
            'reportes_mensuales': [
                'services.reporte_service.ReporteService.obtener_reportes_mensuales',
            ],
        }
        
        # Limpiar caché específico si existe
        if collection_name in cache_functions:
            # Limpiar todo el caché de Streamlit para asegurar que se actualice
            st.cache_data.clear()
            # Invalidar resumen del dashboard para que al volver se recargue
            if "dashboard_resumen" in st.session_state:
                del st.session_state["dashboard_resumen"]
            print(f"[CACHE] Invalidado caché para: {collection_name}")
    except Exception as e:
        print(f"Error invalidando caché: {e}")
