import json
import os
from datetime import datetime
import requests
from config.firebase_config import firebase_config

# Configurar Firebase REST API
FIREBASE_URL = f"https://{firebase_config['projectId']}-default-rtdb.firebaseio.com"

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
def firebase_get(path=""):
    """Obtener datos de Firebase"""
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        print(f"[GET] Firebase GET: {url}")
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

def firebase_set(path, data):
    """Guardar datos en Firebase"""
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        response = requests.put(url, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error Firebase SET: {e}")
        return False

def firebase_push(path, data):
    """Agregar datos a Firebase"""
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        print(f"[PUSH] Firebase PUSH: {url}")
        print(f"[DATA] Data: {data}")
        response = requests.post(url, json=data, timeout=10)
        print(f"[DATA] Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Firebase PUSH Success: {result}")
            return result
        return None
    except Exception as e:
        print(f"[ERROR] Error Firebase PUSH: {e}")
        return None

def firebase_delete(path):
    """Eliminar datos de Firebase"""
    try:
        url = f"{FIREBASE_URL}/{path}.json"
        response = requests.delete(url, timeout=10)
        return response.status_code == 200
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
    try:
        config_data = firebase_get("configuracion")
        if config_data:
            return config_data
        else:
            # Si no hay datos en Firebase, crear configuración por defecto
            config_default = {
                "categorias": ["Comida", "Transporte", "Vivienda", "Entretenimiento", "Salud", "Educación", "Otros"],
                "tipos_gasto": ["Necesario", "Innecesario", "Emergencia", "Lujo"]
            }
            firebase_set("configuracion", config_default)
            return config_default
    except Exception as e:
        print(f"Error cargando configuración: {e}")
        return {
            "categorias": ["Comida", "Transporte", "Vivienda", "Entretenimiento", "Salud", "Educación", "Otros"],
            "tipos_gasto": ["Necesario", "Innecesario", "Emergencia", "Lujo"]
        }

def guardar_configuracion(configuracion):
    try:
        return firebase_set("configuracion", configuracion)
    except Exception as e:
        print(f"Error guardando configuración: {e}")
        return False

def cargar_gastos_recurrentes():
    try:
        gastos_data = firebase_get("gastos_recurrentes")
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
        if firebase_set("gastos_recurrentes", gastos_actuales):
            return gasto
        return None
    except Exception as e:
        print(f"Error guardando gasto recurrente: {e}")
        return None

def eliminar_gasto_recurrente(gasto_id):
    try:
        gastos_actuales = cargar_gastos_recurrentes()
        gastos_actuales = [g for g in gastos_actuales if g["id"] != gasto_id]
        return firebase_set("gastos_recurrentes", gastos_actuales)
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
                return firebase_set("gastos_recurrentes", gastos_actuales)
        return False
    except Exception as e:
        print(f"Error actualizando gasto recurrente: {e}")
        return False

def actualizar_cuenta(cuenta_id, datos_actualizados):
    """Actualizar una cuenta en Firebase"""
    try:
        # Actualizar en Firebase
        firebase_set(f"cuentas/{cuenta_id}", datos_actualizados)
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
        # Obtener datos actuales de la cuenta
        cuenta_data = firebase_get(f"cuentas/{cuenta_id}")
        if cuenta_data:
            nuevo_saldo = float(cuenta_data.get("saldo", 0)) + monto
            datos_actualizados = {
                "nombre": cuenta_data.get("nombre", ""),
                "saldo": nuevo_saldo
            }
            firebase_set(f"cuentas/{cuenta_id}", datos_actualizados)
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
