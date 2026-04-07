# 🤖 Ferrum Bot — Automatización de Foros (Tecnológico Comfenalco)

Este es un bot de automatización de punta a punta diseñado para la plataforma educativa **Ferrum** (Moodle-based). Utiliza **Playwright** para simular la navegación humana y automatizar la publicación en el foro "¿Eres un robot?".

## ✨ Características Principales
- **Autenticación Automática**: Manejo seguro de credenciales mediante el archivo `.env`.
- **Navegación Visual**: Simulación de clics en la barra de navegación y selección de cursos mediante selectores CSS precisos.
- **Formato Mosaico (Grid)**: El bot sabe cómo interactuar con el formato de cuadrícula de Ferrum para abrir secciones.
- **Editor Atto**: Automatización avanzada para escribir en el editor de Moodle 4, completando el **Asunto** y el **Mensaje** automáticamente con: **"No soy un robot"**.
- **Comportamiento Humano**: Scrolls suaves, tipeo a velocidad natural (20-70ms) y pausas aleatorias para evitar detecciones.

## 🚀 Instalación y Uso

### 1. Instalar dependencias
```powershell
pip install -r requirements.txt
playwright install chromium
```

### 2. Configurar credenciales
Crea un archivo `.env` en la raíz del proyecto (clona el archivo `.env.example` y rellénalo):
```env
FERRUM_USERNAME=tu_usuario
FERRUM_PASSWORD=tu_contraseña
```

### 3. Ejecutar el Bot
Para ver al bot trabajando en vivo:
```powershell
python main.py --headed --slow-mo 200
```

## 📂 Estructura del Proyecto
- `main.py`: Lógica central y orquestación del bot.
- `bot/`: Módulos de automatización (Auth, Navigator, Forum, HumanBehavior).
- `config.py`: Parámetros de configuración global.
- `logs/`: Capturas de pantalla y registros de las ejecuciones.
