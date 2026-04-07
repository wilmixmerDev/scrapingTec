# ============================================================
#  config.py — Configuración Central del Bot Ferrum
#
#  Aquí se centraliza TODA la información que el bot necesita:
#  - URL de la plataforma
#  - Nombres de cursos, secciones y foros
#  - Tiempos de espera (timeouts)
#  - Texto del comentario a publicar
#
#  Modificar solo este archivo si cambian los datos de la tarea.
# ============================================================

# ── URL base de la plataforma ──────────────────────────────
FERRUM_URL = "https://ferrum.tecnologicocomfenalco.edu.co/ferrum/"

# ── Objetivos académicos ───────────────────────────────────
COURSE_NAME  = "ELECTIVA III (CLASE 2651)"  # Nombre exacto del curso
SECTION_NAME = "Evaluación Formativa"        # Sección dentro del curso
FORUM_NAME   = "¿Eres un robot?"             # Nombre del foro objetivo

# ── Contenido a publicar ───────────────────────────────────
COMMENT_TEXT = "No soy un robot"

# ── Timeouts (en milisegundos) ─────────────────────────────
DEFAULT_TIMEOUT    = 30_000   # 30 segundos para elementos individuales
NAVIGATION_TIMEOUT = 60_000   # 60 segundos para carga de páginas completas
