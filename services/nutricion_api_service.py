"""
Servicio para integración con API de nutrición
Usa Edamam Food Database API para parsear comidas desde lenguaje natural
"""

import requests
import os
import re
from typing import Dict, Any, List, Optional
import streamlit as st


class NutricionAPIService:
    """Servicio para consultar información nutricional desde APIs"""
    
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
    @st.cache_data(ttl=86400, max_entries=100, show_spinner=False)
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
            
            return None
        except Exception as e:
            print(f"Error parseando comida con Edamam: {e}")
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
        
        Intenta primero con Edamam, luego con Nutritionix
        
        Args:
            descripcion: Descripción en lenguaje natural
            cantidad: Cantidad en gramos
            unidad: Unidad de medida
        
        Returns:
            Diccionario con información nutricional o None
        """
        # Intentar primero con Edamam
        resultado = NutricionAPIService.parsear_comida_edamam(descripcion, cantidad, unidad)
        if resultado:
            return resultado
        
        # Si falla, intentar con Nutritionix
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
    
    @staticmethod
    def parsear_comida_completa(descripcion_completa: str) -> List[Dict[str, Any]]:
        """
        Parsear descripción completa de comida que puede incluir múltiples alimentos
        
        Ejemplo: "Hoy desayuné un omelet con jamón, 100g de frijoles refritos, un plátano y café"
        
        Args:
            descripcion_completa: Descripción completa en lenguaje natural
        
        Returns:
            Lista de diccionarios con información nutricional de cada alimento
        """
        # Dividir por comas o "y"
        # Esto es una implementación básica, se puede mejorar con NLP
        alimentos = []
        
        # Separar por comas y "y"
        partes = descripcion_completa.replace(" y ", ", ").split(",")
        
        for parte in partes:
            parte = parte.strip()
            if not parte:
                continue
            
            # Extraer cantidad si existe (ej: "100g de frijoles")
            cantidad = 100.0
            unidad = "g"
            
            # Buscar patrones de cantidad
            cantidad_match = re.search(r'(\d+(?:\.\d+)?)\s*(g|kg|ml|l|oz|lb)', parte, re.IGNORECASE)
            if cantidad_match:
                cantidad = float(cantidad_match.group(1))
                unidad = cantidad_match.group(2).lower()
                # Convertir a gramos si es necesario
                if unidad == "kg":
                    cantidad *= 1000
                    unidad = "g"
                elif unidad == "l":
                    cantidad *= 1000
                    unidad = "ml"
                elif unidad == "oz":
                    cantidad *= 28.35
                    unidad = "g"
                elif unidad == "lb":
                    cantidad *= 453.59
                    unidad = "g"
            
            # Limpiar descripción (remover cantidad)
            descripcion_limpia = re.sub(r'\d+(?:\.\d+)?\s*(g|kg|ml|l|oz|lb)', '', parte, flags=re.IGNORECASE)
            descripcion_limpia = descripcion_limpia.replace(" de ", " ").strip()
            
            # Parsear alimento
            alimento = NutricionAPIService.parsear_comida(descripcion_limpia, cantidad, unidad)
            if alimento:
                alimentos.append(alimento)
            else:
                # Si no se puede parsear, crear entrada básica
                alimentos.append({
                    "nombre": descripcion_limpia,
                    "calorias": 0,  # Se puede estimar después
                    "proteinas": 0,
                    "carbohidratos": 0,
                    "grasas": 0,
                    "cantidad": cantidad,
                    "unidad": unidad,
                    "descripcion": descripcion_limpia,
                    "sin_parsear": True
                })
        
        return alimentos

