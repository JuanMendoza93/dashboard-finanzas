# Dashboard de Finanzas Personales

## Requisitos
- Python 3.8+
- Cuenta en Firebase (para la base de datos)
- (Opcional) API Key de DeepSeek para análisis nutricional con IA (gratuito)

## Instalación
1. Clona este repositorio.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   
## Configuración de DeepSeek (Análisis Nutricional con IA)

Para usar el análisis nutricional con IA (gratuito), configura tu API key de DeepSeek:

### Opción 1: Variables de Entorno del Sistema

**Windows (PowerShell):**
```powershell
$env:DEEPSEEK_API_KEY="tu_api_key_aqui"
```

**Windows (CMD):**
```cmd
set DEEPSEEK_API_KEY=tu_api_key_aqui
```

**Linux/Mac:**
```bash
export DEEPSEEK_API_KEY="tu_api_key_aqui"
```

### Opción 2: Archivo .env (Recomendado)

1. Crea un archivo `.env` en la raíz del proyecto
2. Agrega:
```
DEEPSEEK_API_KEY=tu_api_key_aqui
```

3. Instala `python-dotenv` si no lo tienes:
```bash
pip install python-dotenv
```

4. Agrega al inicio de `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Opción 3: Streamlit Secrets (Para Streamlit Cloud)

Crea un archivo `.streamlit/secrets.toml`:
```toml
DEEPSEEK_API_KEY = "tu_api_key_aqui"
```

### Obtener tu API Key de DeepSeek (Gratuito)

1. Visita: https://platform.deepseek.com/
2. Crea una cuenta (gratuita)
3. Ve a "API Keys" y crea una nueva key
4. Copia la key y configúrala según una de las opciones anteriores

### Uso

Una vez configurado, el sistema usará DeepSeek automáticamente para analizar descripciones de comida como:
- "Hoy desayuné una sincronizada de una tortilla de harina, 2 huevos revueltos con salsa verde, crema y unos 50g de espinacas, adicional unos quizá igual 50g de piña, y un café sin azúcar ni leche"

El sistema extraerá automáticamente todos los alimentos y sus valores nutricionales.
