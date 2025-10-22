#!/usr/bin/env python3
"""
Script para probar la conexion a Firebase
"""
import requests
import json

# Configuracion de Firebase
firebase_config = {
    "apiKey": "AIzaSyCrB9d86e89K9ThKm2t8NNEgBkj5eeKJyA",
    "authDomain": "dashboard-finanzas-cc205.firebaseapp.com",
    "projectId": "dashboard-finanzas-cc205",
    "storageBucket": "dashboard-finanzas-cc205.firebasestorage.app",
    "messagingSenderId": "116754522917",
    "appId": "1:116754522917:web:c39c26f4449895d161b0cc",
}

FIREBASE_URL = f"https://{firebase_config['projectId']}-default-rtdb.firebaseio.com"

def test_firebase_connection():
    print("Probando conexion a Firebase...")
    print(f"URL: {FIREBASE_URL}")
    print("-" * 50)
    
    # Test 1: GET (leer datos)
    print("1. Probando GET (leer datos)...")
    try:
        url = f"{FIREBASE_URL}/test.json"
        response = requests.get(url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   GET exitoso: {data}")
        else:
            print(f"   GET fallo: {response.text}")
    except Exception as e:
        print(f"   Error GET: {e}")
    
    print("-" * 50)
    
    # Test 2: POST (escribir datos)
    print("2. Probando POST (escribir datos)...")
    try:
        url = f"{FIREBASE_URL}/test.json"
        test_data = {
            "mensaje": "Prueba desde script Python",
            "timestamp": "2025-10-20",
            "funcionando": True
        }
        response = requests.post(url, json=test_data, timeout=10)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   POST exitoso: {result}")
        else:
            print(f"   POST fallo: {response.text}")
    except Exception as e:
        print(f"   Error POST: {e}")
    
    print("-" * 50)
    
    # Test 3: Verificar datos escritos
    print("3. Verificando datos escritos...")
    try:
        url = f"{FIREBASE_URL}/test.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   Datos en Firebase: {data}")
        else:
            print(f"   No se pudieron leer los datos")
    except Exception as e:
        print(f"   Error verificando datos: {e}")
    
    print("-" * 50)
    print("Prueba completada")

if __name__ == "__main__":
    test_firebase_connection()
