# ============================================================
#  bot/auth.py — Módulo de Autenticación
#
#  PROPÓSITO:
#  Manejar todo el proceso de inicio de sesión en Ferrum (Moodle).
#
#  FLUJO:
#  1. Navega a la URL de login
#  2. Espera a que el formulario cargue completamente
#  3. Ingresa usuario y contraseña con comportamiento humano
#  4. Hace clic en el botón de login
#  5. Verifica que el login fue exitoso
#
#  MANEJO DE ERRORES:
#  - Si el login falla (URL sigue siendo /login), lanza excepción clara
#  - Si los campos no se encuentran, lanza excepción descriptiva
# ============================================================

from loguru import logger
from playwright.sync_api import Page

from .human_behavior import human_type, random_delay, smooth_scroll_to, hover_and_click


def login(page: Page, username: str, password: str, base_url: str) -> None:
    """
    Realiza el proceso de autenticación en la plataforma Ferrum.

    Moodle usa formularios HTML estándar con IDs fijos:
    - #username → campo de usuario
    - #password → campo de contraseña
    - #loginbtn  → botón de envío

    Args:
        page:     Página activa de Playwright
        username: Nombre de usuario de Ferrum
        password: Contraseña de Ferrum
        base_url: URL base de la plataforma (desde config.py)

    Raises:
        Exception: Si el login falla o los elementos no se encuentran
    """
    # ── Paso 1: Navegar a la página de login ──────────────────
    login_url = f"{base_url}login/index.php"
    logger.info(f"🔐 Navegando a login: {login_url}")
    page.goto(login_url)
    page.wait_for_load_state("networkidle")  # Esperar carga completa

    # ── Paso 2: Verificar que el formulario existe ─────────────
    try:
        page.wait_for_selector("#username", timeout=15_000)
        logger.info("✅ Formulario de login detectado")
    except Exception:
        raise Exception(
            "❌ No se encontró el formulario de login. "
            "Verifica que la URL es correcta."
        )

    # ── Paso 3: Ingresar nombre de usuario ─────────────────────
    logger.info("✍️  Ingresando nombre de usuario...")
    human_type(page, "#username", username)
    random_delay(0.5, 1.2)  # Pausa natural entre campos

    # ── Paso 4: Ingresar contraseña ────────────────────────────
    logger.info("🔑 Ingresando contraseña...")
    human_type(page, "#password", password)
    random_delay(0.8, 1.5)  # Pausa antes de enviar (como un humano leyendo)

    # ── Paso 5: Click en botón de login ───────────────────────
    logger.info("🚀 Enviando formulario de login...")
    login_btn = page.locator("#loginbtn")
    smooth_scroll_to(login_btn)
    hover_and_click(login_btn)

    # Esperar que la página cargue tras el login
    page.wait_for_load_state("networkidle")
    random_delay(1.0, 2.0)

    # ── Paso 6: Verificar login exitoso ────────────────────────
    current_url = page.url

    # Si seguimos en la página de login, algo salió mal
    if "login" in current_url and "index.php" in current_url:
        # Intentar detectar mensaje de error en la página
        error_msg = ""
        error_element = page.locator(".loginerrors, #loginerrormessage, .alert-danger")
        if error_element.count() > 0:
            error_msg = f" Mensaje: '{error_element.first.inner_text().strip()}'"

        raise Exception(
            f"❌ Login fallido. Verifica usuario y contraseña.{error_msg}"
        )

    logger.success(f"✅ Autenticación exitosa. Redirigido a: {current_url}")
