"""
Script de ayuda para configurar Edamam API (GRATUITA)
Ejecuta este script para verificar tu configuración
"""

import os
from pathlib import Path

def verificar_configuracion():
    """Verificar si Edamam está configurado"""
    print("=" * 70)
    print("🍎 Verificando configuración de Edamam API (GRATUITA)")
    print("=" * 70)
    
    # Cargar .env si existe
    try:
        from dotenv import load_dotenv
        env_path = Path('.') / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            print("✅ Archivo .env encontrado y cargado")
        else:
            print("⚠️  Archivo .env no encontrado")
            print("   Creando archivo .env...")
            crear_env()
            return
    except ImportError:
        print("⚠️  python-dotenv no está instalado")
        print("   Instalando...")
        os.system("pip install python-dotenv")
        from dotenv import load_dotenv
        load_dotenv()
    
    # Verificar API keys
    app_id = os.getenv("EDAMAM_APP_ID", "")
    app_key = os.getenv("EDAMAM_APP_KEY", "")
    
    if app_id and app_id != "tu_app_id_aqui" and app_key and app_key != "tu_app_key_aqui":
        print(f"✅ Application ID encontrado: {app_id[:8]}...{app_id[-4:]}")
        print(f"✅ Application Key encontrado: {app_key[:8]}...{app_key[-4:]}")
        print("\n✅ Edamam API está configurada correctamente!")
        print("\n🚀 El sistema usará Edamam para obtener valores nutricionales reales")
        
        # Probar la conexión
        print("\n🔍 Probando conexión con Edamam API...")
        probar_api(app_id, app_key)
    else:
        print("❌ Edamam API no configurada")
        print("\n📝 Pasos para configurar:")
        print("   1. Visita: https://developer.edamam.com/")
        print("   2. Crea una cuenta gratuita (Sign Up)")
        print("   3. Ve a 'Applications' → 'Create a New Application'")
        print("   4. Selecciona 'Food Database API'")
        print("   5. Completa el formulario y crea la aplicación")
        print("   6. Copia tu Application ID y Application Key")
        print("   7. Abre el archivo .env y agrega:")
        print("      EDAMAM_APP_ID=tu_application_id")
        print("      EDAMAM_APP_KEY=tu_application_key")
        print("   8. Guarda el archivo y reinicia la aplicación")
    
    print("\n" + "=" * 70)

def crear_env():
    """Crear archivo .env con plantilla para Edamam"""
    env_path = Path('.') / '.env'
    
    contenido = """# Edamam Food Database API (GRATUITA - 10,000 requests/mes)
# Obtén tus credenciales en: https://developer.edamam.com/
# 1. Crea una cuenta gratuita
# 2. Ve a "Applications" y crea una nueva aplicación
# 3. Selecciona "Food Database API"
# 4. Copia el Application ID y Application Key

EDAMAM_APP_ID=tu_app_id_aqui
EDAMAM_APP_KEY=tu_app_key_aqui

# Nutritionix API (Alternativa - 500 requests/día gratis)
# NUTRITIONIX_APP_ID=tu_app_id_aqui
# NUTRITIONIX_API_KEY=tu_api_key_aqui
"""
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(contenido)
    print("✅ Archivo .env creado")
    print("📝 Edita el archivo .env y agrega tus credenciales de Edamam")

def probar_api(app_id: str, app_key: str):
    """Probar la conexión con Edamam API"""
    try:
        import requests
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "ingr": "1 egg",
            "nutrition-type": "cooking"
        }
        
        response = requests.get(
            "https://api.edamam.com/api/food-database/v2/parser",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("parsed") and len(data["parsed"]) > 0:
                food = data["parsed"][0]["food"]
                print(f"✅ Conexión exitosa!")
                print(f"   Alimento de prueba: {food.get('label', 'N/A')}")
                print(f"   Calorías (100g): {food.get('nutrients', {}).get('ENERC_KCAL', 0):.0f}")
            else:
                print("⚠️  API respondió pero no encontró resultados")
        elif response.status_code == 401:
            print("❌ Error de autenticación. Verifica que tu Application ID y Key sean correctos")
        else:
            print(f"⚠️  Error en la API (status {response.status_code})")
            print(f"   Respuesta: {response.text[:200]}")
    except Exception as e:
        print(f"⚠️  Error al probar la API: {e}")

if __name__ == "__main__":
    verificar_configuracion()

