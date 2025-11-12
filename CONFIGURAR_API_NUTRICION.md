# 🍎 Configurar API de Nutrición (GRATUITA)

## ¿Por qué usar una API?

Las APIs de nutrición proporcionan valores nutricionales **precisos y actualizados** para miles de alimentos. El sistema intentará usar la API primero, y si no está configurada, usará una base de datos local básica.

## Opción 1: Edamam Food Database API (RECOMENDADA) ⭐

### ✅ Ventajas:
- **100% GRATUITA** (10,000 requests/mes)
- Base de datos muy completa
- Valores nutricionales precisos
- Fácil de configurar

### 📝 Pasos para configurar:

1. **Crear cuenta:**
   - Visita: https://developer.edamam.com/
   - Haz clic en "Sign Up" (es gratis)
   - Completa el registro

2. **Crear aplicación:**
   - Inicia sesión
   - Ve a "Applications" en el menú
   - Haz clic en "Create a New Application"
   - Selecciona "Food Database API"
   - Completa el formulario (puedes poner cualquier nombre)

3. **Obtener credenciales:**
   - Una vez creada la aplicación, verás:
     - **Application ID** (algo como: `12345678`)
     - **Application Key** (algo como: `abcdef1234567890...`)

4. **Configurar en el proyecto:**
   - Abre el archivo `.env` en la raíz del proyecto
   - Agrega:
     ```
     EDAMAM_APP_ID=tu_application_id_aqui
     EDAMAM_APP_KEY=tu_application_key_aqui
     ```
   - Guarda el archivo

5. **¡Listo!** Reinicia la aplicación y el sistema usará Edamam automáticamente.

## Opción 2: Nutritionix API (Alternativa)

### ✅ Ventajas:
- **GRATUITA** (500 requests/día)
- Buena base de datos
- API moderna

### 📝 Pasos para configurar:

1. **Crear cuenta:**
   - Visita: https://www.nutritionix.com/business/api
   - Haz clic en "Get Started" o "Sign Up"
   - Completa el registro

2. **Obtener credenciales:**
   - Ve a tu dashboard
   - Encuentra tu **Application ID** y **API Key**

3. **Configurar en el proyecto:**
   - Abre el archivo `.env`
   - Agrega:
     ```
     NUTRITIONIX_APP_ID=tu_app_id_aqui
     NUTRITIONIX_API_KEY=tu_api_key_aqui
     ```

## Prioridad del Sistema

El sistema intenta usar las APIs en este orden:

1. **Edamam** (si está configurada)
2. **Nutritionix** (si Edamam no está disponible)
3. **Base de datos local** (si ninguna API está configurada)

## Verificar que Funciona

Una vez configurada, cuando ingreses una descripción como:
```
Hoy desayuné una sincronizada de una tortilla de harina, 2 huevos revueltos con salsa verde, crema y unos 50g de espinacas
```

El sistema debería:
- ✅ Usar la API para obtener valores nutricionales precisos
- ✅ Calcular calorías, proteínas, carbohidratos y grasas automáticamente
- ✅ Guardar todo en la base de datos

## Límites Gratuitos

- **Edamam**: 10,000 requests/mes (suficiente para uso personal)
- **Nutritionix**: 500 requests/día (también suficiente para uso personal)

## ¿Qué pasa si no configuro una API?

El sistema seguirá funcionando usando una base de datos local básica con alimentos comunes. Puedes agregar valores nutricionales manualmente después si es necesario.

