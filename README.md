# 🤖 Ferrum Bot — Automatización de Foros (Tecnológico Comfenalco)

Este es un bot de automatización de punta a punta diseñado para la plataforma educativa **Ferrum** (Moodle-based). Utiliza **Playwright** para simular la navegación humana directamente desde la línea de comandos.

## ✨ Características Principales
- **Navegación Visual**: Simulación de clics en la barra de navegación (navbar) y selección de cursos.
- **Formato Mosaico (Grid)**: El bot interactúa con el formato de cuadrícula de Ferrum para abrir secciones dinámicamente.
- **Editor Atto**: Automatización avanzada para escribir en el editor de Moodle 4, incluyendo el campo obligatorio de Asunto.
- **Comportamiento Humano**: Scrolls suaves, tipeo a velocidad natural (20-70ms) y pausas aleatorias para evitar detecciones de bot.
- **Seguridad**: Gestión de credenciales mediante variables de entorno (`.env`) para evitar filtración de datos sensibles en el repositorio.

## 🚀 Instalación y Uso

### 1. Instalar dependencias
```powershell
pip install -r requirements.txt
playwright install chromium
```

### 2. Configurar credenciales
Crea un archivo `.env` en la raíz del proyecto:
```env
FERRUM_USERNAME=tu_usuario
FERRUM_PASSWORD=tu_contraseña
```

### 3. Ejecutar el Bot
```powershell
python main.py --headed --slow-mo 200
```

## 📂 Estructura del Proyecto
- `main.py`: Lógica central y punto de entrada.
- `bot/`: Módulos de automatización (Auth, Navigator, Forum, Human Behavior).
- `config.py`: Parámetros de configuración global.
- `logs/`: Screenshots y registros detallados de ejecución.

---
*Desarrollado con ❤️ para el Tecnológico Comfenalco.*
