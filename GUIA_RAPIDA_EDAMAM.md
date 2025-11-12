# 🚀 Guía Rápida: Configurar Edamam API (5 minutos)

## ⚡ Pasos Rápidos

### Paso 1: Crear Cuenta en Edamam (2 minutos)

1. **Abre tu navegador** y ve a: **https://developer.edamam.com/**
2. **Haz clic en "Sign Up"** (es GRATIS, no requiere tarjeta de crédito)
3. **Completa el registro:**
   - Email
   - Contraseña
   - Nombre
   - Acepta los términos

### Paso 2: Crear Aplicación (2 minutos)

1. **Inicia sesión** en tu cuenta de Edamam
2. **Ve al menú superior** y haz clic en **"Applications"**
3. **Haz clic en "Create a New Application"** (botón verde/azul)
4. **Completa el formulario:**
   - **Application Name**: "Dashboard Nutricional" (o cualquier nombre)
   - **Application Type**: Selecciona **"Food Database API"**
   - **Description**: "Para análisis nutricional" (opcional)
   - Acepta los términos
5. **Haz clic en "Create Application"**

### Paso 3: Obtener Credenciales (30 segundos)

Una vez creada la aplicación, verás:

- **Application ID**: Un número (ej: `12345678`)
- **Application Key**: Una cadena larga (ej: `abcdef1234567890abcdef1234567890`)

**⚠️ IMPORTANTE:** Copia ambos valores AHORA, solo se muestran una vez.

### Paso 4: Configurar en el Proyecto (30 segundos)

1. **Abre el archivo `.env`** en la raíz del proyecto
2. **Busca estas líneas:**
   ```
   EDAMAM_APP_ID=tu_app_id_aqui
   EDAMAM_APP_KEY=tu_app_key_aqui
   ```
3. **Reemplaza con tus valores reales:**
   ```
   EDAMAM_APP_ID=12345678
   EDAMAM_APP_KEY=abcdef1234567890abcdef1234567890
   ```
4. **Guarda el archivo**

### Paso 5: Verificar (30 segundos)

Ejecuta el script de verificación:
```bash
python configurar_edamam.py
```

Deberías ver:
```
✅ Edamam API está configurada correctamente!
✅ Conexión exitosa!
```

## ✅ ¡Listo!

Ahora cuando ingreses una descripción como:
```
Hoy desayuné una sincronizada de una tortilla de harina, 2 huevos revueltos con salsa verde, crema y unos 50g de espinacas
```

El sistema:
- ✅ Consultará Edamam API para cada alimento
- ✅ Obtendrá valores nutricionales reales y precisos
- ✅ Calculará calorías, proteínas, carbohidratos y grasas automáticamente
- ✅ Guardará todo en la base de datos

## 🔍 Verificar que Funciona

1. **Ejecuta la aplicación:**
   ```bash
   streamlit run app.py
   ```

2. **Ve a:** Nutrición → Registro de Comidas

3. **Deberías ver:** "✅ **Edamam API activa** - Valores nutricionales precisos desde API gratuita"

4. **Prueba con una descripción** y verifica que los valores nutricionales se calculen automáticamente.

## 🆘 Problemas Comunes

### No encuentro "Applications"
- Busca en el menú superior derecho (icono de usuario)
- O busca "Dashboard" o "My Applications"

### No veo Application ID y Key
- Asegúrate de haber seleccionado "Food Database API" al crear la aplicación
- Si no los ves, puedes verlos en "Applications" → selecciona tu app → "View"

### El script dice "Error de autenticación"
- Verifica que copiaste TODO el Application Key (es muy largo)
- Asegúrate de que no hay espacios antes o después
- Verifica que el archivo `.env` está en la raíz del proyecto

### No veo "Edamam API activa"
- Verifica que el archivo `.env` tiene los valores correctos
- Reinicia la aplicación Streamlit
- Ejecuta `python configurar_edamam.py` para verificar

## 💰 ¿Es Realmente Gratis?

Sí, Edamam ofrece:
- **10,000 requests/mes GRATIS**
- Sin tarjeta de crédito requerida
- Suficiente para uso personal (aprox. 300-400 comidas/mes)

## 📞 Soporte

Si tienes problemas:
1. Verifica que tu cuenta de Edamam está activa
2. Revisa que tienes créditos disponibles (10,000/mes)
3. Ejecuta `python configurar_edamam.py` para diagnosticar
4. Verifica la consola de Streamlit para mensajes de error

