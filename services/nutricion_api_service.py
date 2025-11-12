"""
Servicio para integración con API de nutrición
Usa Edamam Food Database API o Nutritionix para parsear comidas desde lenguaje natural
Si no hay APIs configuradas, usa un método básico de parseo
"""

import requests
import os
import re
import json
from typing import Dict, Any, List, Optional


class NutricionAPIService:
    """Servicio para consultar información nutricional desde APIs"""
    
    # Cargar variables de entorno al inicio
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Configuración de APIs disponibles
    # Edamam Food Database API (gratis: 10,000 requests/mes)
    EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID", "")
    EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY", "")
    EDAMAM_BASE_URL = "https://api.edamam.com/api/food-database/v2/parser"
    
    # Nutritionix API (alternativa, gratis: 500 requests/día)
    NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID", "")
    NUTRITIONIX_API_KEY = os.getenv("NUTRITIONIX_API_KEY", "")
    NUTRITIONIX_BASE_URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    
    
    @staticmethod
    def parsear_comida_edamam(descripcion: str, cantidad: float = 100.0, unidad: str = "g") -> Optional[Dict[str, Any]]:
        """
        Parsear descripción de comida usando Edamam API
        
        Args:
            descripcion: Descripción en lenguaje natural (ej: "omelet con jamón")
            cantidad: Cantidad en gramos
            unidad: Unidad de medida (g, ml, etc.)
        
        Returns:
            Diccionario con información nutricional o None si hay error
        """
        if not NutricionAPIService.EDAMAM_APP_ID or not NutricionAPIService.EDAMAM_APP_KEY:
            return None
        
        try:
            params = {
                "app_id": NutricionAPIService.EDAMAM_APP_ID,
                "app_key": NutricionAPIService.EDAMAM_APP_KEY,
                "ingr": descripcion,
                "nutrition-type": "cooking"
            }
            
            response = requests.get(
                NutricionAPIService.EDAMAM_BASE_URL,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("parsed") and len(data["parsed"]) > 0:
                    food = data["parsed"][0]["food"]
                    nutrients = food.get("nutrients", {})
                    
                    # Calcular factor de cantidad
                    base_quantity = food.get("servingWeight", 100.0)
                    factor = cantidad / base_quantity if base_quantity > 0 else 1.0
                    
                    return {
                        "nombre": food.get("label", descripcion),
                        "calorias": nutrients.get("ENERC_KCAL", 0) * factor,
                        "proteinas": nutrients.get("PROCNT", 0) * factor,
                        "carbohidratos": nutrients.get("CHOCDF", 0) * factor,
                        "grasas": nutrients.get("FAT", 0) * factor,
                        "cantidad": cantidad,
                        "unidad": unidad,
                        "descripcion": descripcion
                    }
                else:
                    # Si no hay resultados parseados, intentar con "hints"
                    if data.get("hints") and len(data["hints"]) > 0:
                        food = data["hints"][0]["food"]
                        nutrients = food.get("nutrients", {})
                        base_quantity = 100.0
                        factor = cantidad / base_quantity if base_quantity > 0 else 1.0
                        
                        return {
                            "nombre": food.get("label", descripcion),
                            "calorias": nutrients.get("ENERC_KCAL", 0) * factor,
                            "proteinas": nutrients.get("PROCNT", 0) * factor,
                            "carbohidratos": nutrients.get("CHOCDF", 0) * factor,
                            "grasas": nutrients.get("FAT", 0) * factor,
                            "cantidad": cantidad,
                            "unidad": unidad,
                            "descripcion": descripcion
                        }
            
            # Manejar errores específicos
            if response.status_code == 401:
                print(f"❌ Edamam: Error de autenticación. Verifica tu Application ID y Key")
            elif response.status_code == 403:
                print(f"❌ Edamam: Acceso denegado. Verifica que tu aplicación tenga acceso a Food Database API")
            elif response.status_code == 429:
                print(f"⚠️ Edamam: Límite de requests excedido. Espera un momento o verifica tu plan")
            else:
                print(f"⚠️ Edamam: Error {response.status_code} - {response.text[:100]}")
            
            return None
        except Exception as e:
            print(f"Error parseando comida con Edamam: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def parsear_comida_nutritionix(descripcion: str) -> Optional[Dict[str, Any]]:
        """
        Parsear descripción de comida usando Nutritionix API
        
        Args:
            descripcion: Descripción en lenguaje natural
        
        Returns:
            Diccionario con información nutricional o None si hay error
        """
        if not NutricionAPIService.NUTRITIONIX_APP_ID or not NutricionAPIService.NUTRITIONIX_API_KEY:
            return None
        
        try:
            headers = {
                "x-app-id": NutricionAPIService.NUTRITIONIX_APP_ID,
                "x-app-key": NutricionAPIService.NUTRITIONIX_API_KEY,
                "Content-Type": "application/json"
            }
            
            data = {
                "query": descripcion
            }
            
            response = requests.post(
                NutricionAPIService.NUTRITIONIX_BASE_URL,
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("foods") and len(result["foods"]) > 0:
                    food = result["foods"][0]
                    return {
                        "nombre": food.get("food_name", descripcion),
                        "calorias": food.get("nf_calories", 0),
                        "proteinas": food.get("nf_protein", 0),
                        "carbohidratos": food.get("nf_total_carbohydrate", 0),
                        "grasas": food.get("nf_total_fat", 0),
                        "cantidad": food.get("serving_weight_grams", 100.0),
                        "unidad": "g",
                        "descripcion": descripcion
                    }
            
            return None
        except Exception as e:
            print(f"Error parseando comida con Nutritionix: {e}")
            return None
    
    @staticmethod
    def parsear_comida(descripcion: str, cantidad: float = 100.0, unidad: str = "g") -> Optional[Dict[str, Any]]:
        """
        Parsear descripción de comida usando la API disponible
        
        Intenta primero con Edamam, luego con Nutritionix.
        SIEMPRE intenta usar API primero antes de usar base de datos local.
        
        Args:
            descripcion: Descripción en lenguaje natural
            cantidad: Cantidad en gramos
            unidad: Unidad de medida
        
        Returns:
            Diccionario con información nutricional o None si no hay API configurada
        """
        # Intentar primero con Edamam (prioridad)
        if NutricionAPIService.EDAMAM_APP_ID and NutricionAPIService.EDAMAM_APP_KEY:
            resultado = NutricionAPIService.parsear_comida_edamam(descripcion, cantidad, unidad)
            if resultado:
                return resultado
        
        # Si Edamam no está disponible o falló, intentar con Nutritionix
        if NutricionAPIService.NUTRITIONIX_APP_ID and NutricionAPIService.NUTRITIONIX_API_KEY:
            resultado = NutricionAPIService.parsear_comida_nutritionix(descripcion)
            if resultado:
                # Ajustar cantidad si es necesario
                if cantidad != resultado.get("cantidad", 100.0):
                    factor = cantidad / resultado.get("cantidad", 100.0)
                    resultado["calorias"] *= factor
                    resultado["proteinas"] *= factor
                    resultado["carbohidratos"] *= factor
                    resultado["grasas"] *= factor
                    resultado["cantidad"] = cantidad
                return resultado
        
        # Si no hay APIs configuradas, retornar None para forzar uso de API
        return None
    
    @staticmethod
    def parsear_comida_completa(descripcion_completa: str) -> List[Dict[str, Any]]:
        """
        Parsear descripción completa de comida que puede incluir múltiples alimentos
        
        Ejemplo: "Hoy desayuné un omelet con jamón, 100g de frijoles refritos, un plátano y café"
        
        Usa un método básico de parseo que divide la descripción y extrae alimentos.
        Si hay APIs de nutrición configuradas (Edamam/Nutritionix), intenta obtener valores nutricionales.
        
        Args:
            descripcion_completa: Descripción completa en lenguaje natural
        
        Returns:
            Lista de diccionarios con información nutricional de cada alimento
        """
        # Dividir la descripción en alimentos individuales
        alimentos = []
        
        # Limpiar descripción inicial (remover frases comunes al inicio)
        descripcion_limpia = descripcion_completa.strip()
        # Remover frases comunes como "Hoy desayuné", "Hoy comí", etc.
        descripcion_limpia = re.sub(r'^(Hoy|hoy)\s+(desayuné|desayune|comí|comi|cené|cene|almorzé|almorce|tomé|tome)\s+', '', descripcion_limpia, flags=re.IGNORECASE)
        descripcion_limpia = descripcion_limpia.strip()
        
        # Separar por comas y "y", pero preservar mejor la estructura
        # Primero reemplazar "adicional" y "más" por comas
        descripcion_limpia = descripcion_limpia.replace(" adicional ", ", ").replace(" más ", ", ")
        # Separar por comas, pero también considerar "y" al final
        partes = descripcion_limpia.split(",")
        
        for parte in partes:
            parte = parte.strip()
            
            # Si la parte contiene "y" al final, puede tener múltiples alimentos
            if " y " in parte:
                subpartes = parte.split(" y ")
                for subparte in subpartes:
                    subparte = subparte.strip()
                    if subparte:
                        # Para cada alimento, SIEMPRE intentar obtener valores de la API
                        alimento = NutricionAPIService._extraer_alimento(subparte)
                        if alimento:
                            alimentos.append(alimento)
                continue
            
            # Procesar parte individual - SIEMPRE intentar obtener valores de la API
            alimento = NutricionAPIService._extraer_alimento(parte)
            if alimento:
                alimentos.append(alimento)
        
        return alimentos
    
    @staticmethod
    def _extraer_alimento(parte: str) -> Optional[Dict[str, Any]]:
        """Extraer información de un alimento individual"""
        if not parte or len(parte) < 2:
            return None
        
        parte_original = parte.strip()
        
        # Extraer cantidad si existe (ej: "100g de frijoles", "2 huevos")
        cantidad = 100.0
        unidad = "g"
        
        # Buscar patrones de cantidad con números (ej: "50g", "2 huevos", "100ml")
        cantidad_match = re.search(r'(\d+(?:\.\d+)?)\s*(g|kg|ml|l|oz|lb|unidad|unidades|huevo|huevos|taza|tazas|pieza|piezas)', parte, re.IGNORECASE)
        if cantidad_match:
            cantidad = float(cantidad_match.group(1))
            unidad_raw = cantidad_match.group(2).lower()
            
            # Convertir unidades a estándar
            if unidad_raw in ["g", "gramo", "gramos"]:
                unidad = "g"
            elif unidad_raw in ["kg", "kilogramo", "kilogramos"]:
                cantidad *= 1000
                unidad = "g"
            elif unidad_raw in ["ml", "mililitro", "mililitros"]:
                unidad = "ml"
            elif unidad_raw in ["l", "litro", "litros"]:
                cantidad *= 1000
                unidad = "ml"
            elif unidad_raw in ["oz", "onza", "onzas"]:
                cantidad *= 28.35
                unidad = "g"
            elif unidad_raw in ["lb", "libra", "libras"]:
                cantidad *= 453.59
                unidad = "g"
            elif unidad_raw in ["huevo", "huevos", "unidad", "unidades", "pieza", "piezas", "taza", "tazas"]:
                unidad = "unidad"
        
        # Limpiar descripción pero preservar mejor el nombre
        nombre = parte_original
        
        # Caso especial: si tiene "huevos" como unidad, preservarlo en el nombre
        # Ejemplo: "2 huevos revueltos" -> "Huevos revueltos"
        if cantidad_match and unidad_raw in ["huevo", "huevos"]:
            # Remover solo el número, mantener "huevos" en el nombre
            nombre = re.sub(r'^\d+(?:\.\d+)?\s+', '', nombre, flags=re.IGNORECASE)
        else:
            # Remover cantidad numérica y unidad
            nombre = re.sub(r'\d+(?:\.\d+)?\s*(g|kg|ml|l|oz|lb|gramos?|kilogramos?|mililitros?|litros?|onzas?|libras?|unidades?|tazas?|piezas?)\s*', '', nombre, flags=re.IGNORECASE)
        
        # Remover palabras comunes al inicio
        nombre = re.sub(r'^(unos?|unas?|el|la|los|las|un|una|quizá|igual|y)\s+', '', nombre, flags=re.IGNORECASE)
        
        # Limpiar "de" solo si está al inicio o al final
        nombre = re.sub(r'^(de|del|de la|de los|de las)\s+', '', nombre, flags=re.IGNORECASE)
        nombre = re.sub(r'\s+(de|del|de la|de los|de las)$', '', nombre, flags=re.IGNORECASE)
        
        # Remover "quizá igual" si quedó en medio
        nombre = re.sub(r'\s+quizá\s+igual\s+', ' ', nombre, flags=re.IGNORECASE)
        nombre = re.sub(r'quizá\s+igual\s+', '', nombre, flags=re.IGNORECASE)
        
        # Normalizar espacios
        nombre = re.sub(r'\s+', ' ', nombre)
        nombre = nombre.strip()
        
        # Si la descripción está vacía o muy corta después de limpiar, usar la parte original
        if not nombre or len(nombre) < 2:
            nombre = parte_original.strip()
            # Limpiar solo "y" al inicio si existe
            nombre = re.sub(r'^y\s+', '', nombre, flags=re.IGNORECASE)
        
        # Capitalizar primera letra
        if nombre:
            nombre = nombre[0].upper() + nombre[1:] if len(nombre) > 1 else nombre.upper()
        
        # SIEMPRE intentar parsear con API primero
        alimento = NutricionAPIService.parsear_comida(nombre, cantidad, unidad)
        if alimento:
            return alimento
        
        # Si no hay API configurada, crear entrada sin valores y marcar que necesita API
        # Esto forzará al usuario a configurar una API
        return {
            "nombre": nombre,
            "calorias": 0,
            "proteinas": 0,
            "carbohidratos": 0,
            "grasas": 0,
            "cantidad": cantidad,
            "unidad": unidad,
            "descripcion": nombre,
            "sin_parsear": True,
            "necesita_api": True  # Marcar que necesita API para obtener valores
        }

