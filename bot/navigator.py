from loguru import logger
from playwright.sync_api import Page

from .human_behavior import random_delay, smooth_scroll_to, hover_and_click


def go_to_my_courses(page: Page) -> None:
    """
    Navega visualmente a la sección "Mis Cursos" haciendo click en el botón del menú superior.
    """
    logger.info("📚 Buscando pestaña 'Mis cursos' en el menú superior...")

    page.wait_for_load_state("networkidle")
    random_delay(2.0, 3.0)

    selectors = [
        "a.nav-link[title*='Courses']",               # Navbar superior (Inglés)
        "a.nav-link[title*='cursos']",                # Navbar superior (Español)
        ".primary-navigation a:has-text('cursos')",    # Bloque de navegación primaria
        "a:has-text('Mis cursos')",                   # Texto directo
    ]

    link = _find_element_with_fallback(page, selectors, "Boton Cursos")
    smooth_scroll_to(link)
    random_delay(0.5, 1.0)

    logger.debug("   🖱️  Haciendo click visual en la pestaña de cursos...")
    hover_and_click(link)

    page.wait_for_load_state("networkidle")
    random_delay(2.0, 3.0)
    logger.success("✅ Sección de Cursos cargada.")


def find_and_enter_course(page: Page, course_name: str) -> None:
    """
    Busca el curso por nombre y entra en él usando el selector exacto de Ferrum.
    """
    logger.info(f"🔍 Buscando curso: '{course_name}'")

    selectors = [
        f"a.coursename:has-text('{course_name}')",
        f"a.aalink:has-text('{course_name}')",
        f"a:has-text('{course_name}')",
    ]

    course_link = _find_element_with_fallback(page, selectors, course_name)
    smooth_scroll_to(course_link)
    random_delay(1.0, 2.0)

    logger.debug("   🖱️  Entrando al curso...")
    course_link.evaluate("el => el.click()")

    page.wait_for_load_state("networkidle")
    random_delay(2.0, 3.0)
    logger.success(f"✅ Dentro del curso: '{course_name}'")


def find_formative_section_and_enter_forum(
    page: Page, section_name: str, forum_name: str
) -> None:
    """
    Estrategia para formato 'Grid' de Ferrum:
    1. Clic en el mosaico/tarjeta de la sección (a.grid-section-inner).
    2. Clic en el enlace del foro (stretched-link) que se revela.
    """
    logger.info(f"📂 Buscando mosaico de sección: '{section_name}'")

    section_selectors = [
        f"a.grid-section-inner:has-text('{section_name}')",
        f".grid-section-inner:has-text('{section_name}')",
        f"*:has-text('{section_name}')",
    ]

    section_tile = _find_element_with_fallback(page, section_selectors, section_name)
    smooth_scroll_to(section_tile)
    random_delay(1.0, 1.5)

    logger.info(f"   🖱️  Haciendo click en mosaico '{section_name}' para abrir sección...")
    section_tile.click()
    page.wait_for_load_state("networkidle")
    random_delay(2.0, 3.0)

    logger.info(f"🗣️  Buscando foro: '{forum_name}'")

    forum_selectors = [
        f"a.stretched-link:has-text('{forum_name}')",  # Link interno del Grid
        f"a:has-text('{forum_name}')",                 # Texto directo
        "a:has-text('robot')",                         # Texto parcial robusto
    ]

    forum_link = _find_element_with_fallback(page, forum_selectors, forum_name)
    smooth_scroll_to(forum_link)
    random_delay(1.0, 1.5)

    logger.debug("   🖱️  Entrando al foro...")
    forum_link.evaluate("el => el.click()")

    page.wait_for_load_state("networkidle")
    random_delay(1.0, 2.0)

    logger.success(f"✅ Dentro del foro: '{forum_name}'")


def _find_element_with_fallback(page: Page, selectors: list, element_name: str):
    """
    Intenta encontrar un elemento usando múltiples selectores alternativos.

    Si el primer selector falla, intenta el siguiente. Esto hace el bot
    más robusto ante diferentes versiones o temas de Moodle.

    Args:
        page:         Página activa de Playwright
        selectors:    Lista de selectores CSS/texto a intentar
        element_name: Nombre descriptivo del elemento (para los logs de error)

    Returns:
        El primer Locator que encuentre un elemento visible

    Raises:
        Exception: Si ningún selector encuentra el elemento
    """
    for selector in selectors:
        try:
            element = page.locator(selector).first
            if element.count() > 0 and element.is_visible(timeout=3_000):
                logger.debug(f"   ✔ Selector exitoso: '{selector}'")
                return element
        except Exception:
            logger.debug(f"   ✗ Selector fallido: '{selector}'")
            continue

    raise Exception(
        f"❌ No se encontró '{element_name}' en la página. "
        f"Probados {len(selectors)} selectores distintos. "
        f"URL actual: {page.url}"
    )
