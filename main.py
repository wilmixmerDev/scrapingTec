"""
╔══════════════════════════════════════════════════════════════════╗
║               BOT FERRUM — Tecnológico Comfenalco               ║
║          Automatización de publicación en foro del aula         ║
╚══════════════════════════════════════════════════════════════════╝

FLUJO COMPLETO DEL BOT:
  1. Obtiene credenciales (interactivo o desde .env)
  2. Inicia el navegador Chromium
  3. Realiza login en la plataforma Ferrum
  4. Navega a "Mis Cursos"
  5. Entra al curso "ELECTIVA III (CLASE 2651)"
  6. Localiza la sección "Evaluación Formativa"
  7. Entra al foro "¿Eres un robot?"
  8. Lee otros posts (comportamiento humano - BONUS)
  9. Publica el comentario "No soy un robot"
 10. Toma screenshot de confirmación
 11. Guarda todo en logs/

USO:
  python main.py                          # Pide credenciales interactivamente
  python main.py --headed                 # Con navegador visible (para video)
  python main.py --slow-mo 800            # Lento, para ver cada paso
  python main.py --profile estudiante1   # Usa perfil del users.json (BONUS)
  python main.py --username mi_usuario    # Usuario por argumento
"""

import sys
import os
import json
import getpass
import argparse
from pathlib import Path

from loguru import logger
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

import config
from bot.auth import login
from bot.navigator import (
    go_to_my_courses,
    find_and_enter_course,
    find_formative_section_and_enter_forum,
)
from bot.forum import read_forum_posts, post_comment


def setup_logging() -> None:
    """
    Configura el sistema de logs con dos destinos:
    1. Consola: Con colores, fácil de leer durante la ejecución
    2. Archivo: En logs/bot.log, para revisión posterior
    """
    Path("logs").mkdir(exist_ok=True)

    logger.remove()

    logger.add(
        sys.stdout,
        colorize=True,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "{message}"
        ),
        level="INFO",
    )

    logger.add(
        "logs/bot.log",
        rotation="1 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        level="DEBUG",
        encoding="utf-8",
    )


def get_credentials(args: argparse.Namespace) -> tuple[str, str]:
    """
    Obtiene las credenciales del usuario con el siguiente orden de prioridad:
      1. Perfil del users.json (si se usa --profile)
      2. Variables de entorno del .env
      3. Input interactivo (si no se encontró en las opciones anteriores)

    Este diseño permite:
    - Uso simple (input interactivo) para la mayoría de los casos
    - Uso automatizado (via .env) para integraciones CI/CD (BONUS)
    - Multi-perfil (via --profile) para múltiples estudiantes (BONUS)

    Args:
        args: Argumentos parseados de la línea de comandos

    Returns:
        Tupla (username, password)
    """
    load_dotenv()

    username = None
    password = None

    if args.profile and args.profile != "default":
        logger.info(f"👤 Usando perfil: '{args.profile}'")
        username, password = _load_profile_credentials(args.profile)

    if not username:
        username = os.getenv("FERRUM_USERNAME")
    if not password:
        password = os.getenv("FERRUM_PASSWORD")

    if not username and args.username:
        username = args.username

    if not username or not password:
        print()
        print("=" * 55)
        print("  🔐  CREDENCIALES DE ACCESO — PLATAFORMA FERRUM")
        print("=" * 55)
        print("  (También puedes usar un archivo .env para no")
        print("   ingresar las credenciales cada vez)")
        print("=" * 55)

        if not username:
            username = input("  👤  Usuario: ").strip()

        if not password:
            password = getpass.getpass("  🔒  Contraseña: ")

        print("=" * 55)
        print()

    return username, password


def _load_profile_credentials(profile_name: str) -> tuple[str | None, str | None]:
    """
    Carga las credenciales de un perfil desde profiles/users.json.

    Los perfiles definen qué variables de entorno usar para cada usuario.
    Las contraseñas en sí siempre vienen del .env (nunca del JSON).

    Args:
        profile_name: Nombre del perfil a cargar

    Returns:
        Tupla (username, password) o (None, None) si no se encuentra
    """
    profiles_path = Path("profiles/users.json")

    if not profiles_path.exists():
        logger.warning("⚠️  No se encontró profiles/users.json. Usando credenciales por defecto.")
        return None, None

    try:
        with open(profiles_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        profiles = data.get("profiles", [])
        profile = next(
            (p for p in profiles if p["name"] == profile_name), None
        )

        if not profile:
            logger.warning(
                f"⚠️  Perfil '{profile_name}' no encontrado en users.json. "
                f"Perfiles disponibles: {[p['name'] for p in profiles]}"
            )
            return None, None

        username = os.getenv(profile["username_env"])
        password = os.getenv(profile["password_env"])

        if not username or not password:
            logger.warning(
                f"⚠️  Variables de entorno del perfil '{profile_name}' no encontradas: "
                f"{profile['username_env']}, {profile['password_env']}"
            )

        return username, password

    except Exception as e:
        logger.error(f"❌ Error leyendo perfiles: {e}")
        return None, None


def run_bot(username: str, password: str, headed: bool = False, slow_mo: int = 0) -> bool:
    """
    Ejecuta el flujo completo de automatización del bot Ferrum.

    Esta es la función principal que orquesta todos los módulos:
    auth → navigator → forum

    Args:
        username: Nombre de usuario de Ferrum
        password: Contraseña de Ferrum
        headed:   True = navegador visible, False = modo headless (invisible)
        slow_mo:  Milisegundos de delay entre acciones (0 = velocidad normal)

    Returns:
        True si el bot completó el flujo exitosamente, False si hubo error
    """
    logger.info("=" * 60)
    logger.info("🤖  BOT FERRUM — Iniciando ejecución")
    logger.info(f"📍  Plataforma: {config.FERRUM_URL}")
    logger.info(f"📚  Curso:      {config.COURSE_NAME}")
    logger.info(f"🗣️   Foro:       {config.FORUM_NAME}")
    logger.info(f"💬  Comentario: '{config.COMMENT_TEXT}'")
    logger.info(f"🖥️   Modo:       {'Visible (headed)' if headed else 'Headless (invisible)'}")
    logger.info("=" * 60)

    with sync_playwright() as playwright:

        logger.info("🌐 [1/8] Iniciando navegador Chromium...")

        browser = playwright.chromium.launch(
            headless=not headed,
            slow_mo=slow_mo,
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        context.set_default_timeout(config.DEFAULT_TIMEOUT)
        context.set_default_navigation_timeout(config.NAVIGATION_TIMEOUT)

        page = context.new_page()

        try:
            logger.info("🔐 [2/8] Realizando autenticación...")
            login(page, username, password, config.FERRUM_URL)

            logger.info("📚 [3/8] Navegando a 'Mis Cursos'...")
            go_to_my_courses(page)

            logger.info(f"📖 [4/8] Buscando curso '{config.COURSE_NAME}'...")
            find_and_enter_course(page, config.COURSE_NAME)

            logger.info(f"📂 [5/8] Accediendo a '{config.SECTION_NAME}' → '{config.FORUM_NAME}'...")
            find_formative_section_and_enter_forum(
                page, config.SECTION_NAME, config.FORUM_NAME
            )

            logger.info("👀 [6/8] Leyendo posts del foro...")
            read_forum_posts(page)

            logger.info(f"✍️  [7/8] Publicando comentario...")
            post_comment(page, config.COMMENT_TEXT)

            logger.info("📸 [8/8] Tomando screenshot de confirmación...")
            screenshot_path = "logs/confirmacion_publicacion.png"
            page.screenshot(path=screenshot_path, full_page=False)

            logger.success("=" * 60)
            logger.success("🎉  ¡BOT COMPLETADO EXITOSAMENTE!")
            logger.success(f"💬  Comentario publicado: '{config.COMMENT_TEXT}'")
            logger.success(f"📸  Screenshot: {screenshot_path}")
            logger.success(f"📄  Logs:       logs/bot.log")
            logger.success("=" * 60)

            return True

        except Exception as error:
            logger.error("=" * 60)
            logger.error(f"💥  ERROR DURANTE LA EJECUCIÓN")
            logger.error(f"    {error}")
            logger.error("=" * 60)

            try:
                error_screenshot_path = "logs/error_screenshot.png"
                page.screenshot(path=error_screenshot_path)
                logger.info(f"📸  Screenshot del error guardado en: {error_screenshot_path}")
            except Exception:
                pass

            return False

        finally:
            context.close()
            browser.close()
            logger.info("🔒 Navegador cerrado.")


def parse_arguments() -> argparse.Namespace:
    """
    Define y parsea los argumentos de la línea de comandos.

    Permite controlar el comportamiento del bot sin modificar el código.
    """
    parser = argparse.ArgumentParser(
        prog="bot-ferrum",
        description=(
            "Bot Ferrum — Automatiza la publicación en el foro "
            "'¿Eres un robot?' de la plataforma educativa."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py                       # Pide credenciales interactivamente
  python main.py --headed              # Ejecuta con navegador visible
  python main.py --headed --slow-mo 800  # Visible y lento (ideal para video)
  python main.py --profile estudiante1   # Usa perfil del users.json
  python main.py --username mi_usuario   # Usuario por argumento
        """,
    )

    parser.add_argument(
        "--username", "-u",
        help="Nombre de usuario de Ferrum (opcional, se puede ingresar interactivamente)",
        default=None,
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Ejecutar con navegador visible (recomendado para grabar el video)",
        default=False,
    )
    parser.add_argument(
        "--slow-mo",
        type=int,
        default=0,
        metavar="MS",
        help="Milisegundos de delay entre cada acción (ej. 800). Útil para demostración.",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default="default",
        metavar="NOMBRE",
        help="Nombre del perfil a usar (definidos en profiles/users.json). BONUS: multi-perfil.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    setup_logging()

    args = parse_arguments()

    username, password = get_credentials(args)

    success = run_bot(
        username=username,
        password=password,
        headed=args.headed,
        slow_mo=args.slow_mo,
    )

    sys.exit(0 if success else 1)
