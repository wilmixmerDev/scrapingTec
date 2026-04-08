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
    login_url = f"{base_url}login/index.php"
    logger.info(f"🔐 Navegando a login: {login_url}")
    page.goto(login_url)
    page.wait_for_load_state("networkidle")

    try:
        page.wait_for_selector("#username", timeout=15_000)
        logger.info("✅ Formulario de login detectado")
    except Exception:
        raise Exception(
            "❌ No se encontró el formulario de login. "
            "Verifica que la URL es correcta."
        )

    logger.info("✍️  Ingresando nombre de usuario...")
    human_type(page, "#username", username)
    random_delay(0.5, 1.2)

    logger.info("🔑 Ingresando contraseña...")
    human_type(page, "#password", password)
    random_delay(0.8, 1.5)

    logger.info("🚀 Enviando formulario de login...")
    login_btn = page.locator("#loginbtn")
    smooth_scroll_to(login_btn)
    hover_and_click(login_btn)

    page.wait_for_load_state("networkidle")
    random_delay(1.0, 2.0)

    current_url = page.url

    if "login" in current_url and "index.php" in current_url:
        error_msg = ""
        error_element = page.locator(".loginerrors, #loginerrormessage, .alert-danger")
        if error_element.count() > 0:
            error_msg = f" Mensaje: '{error_element.first.inner_text().strip()}'"

        raise Exception(
            f"❌ Login fallido. Verifica usuario y contraseña.{error_msg}"
        )

    logger.success(f"✅ Autenticación exitosa. Redirigido a: {current_url}")
