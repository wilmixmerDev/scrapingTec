import time
import random
from loguru import logger
from playwright.sync_api import Page, Locator


def random_delay(min_sec: float = 0.8, max_sec: float = 2.5) -> None:
    """
    Espera un tiempo ALEATORIO entre min_sec y max_sec segundos.

    Por qué: Los humanos no actúan a velocidad constante. Un bot que
    espera exactamente 1 segundo entre cada acción es fácilmente detectado.
    Usando delays aleatorios, el comportamiento se vuelve más natural.
    """
    delay = random.uniform(min_sec, max_sec)
    logger.debug(f"⏳ Pausa humana: {delay:.2f}s")
    time.sleep(delay)


def human_type(page: Page, selector: str, text: str) -> None:
    """
    Escribe el texto en un campo, tecla por tecla, con velocidad variable.

    Por qué: Un humano real no escribe a velocidad constante. Hay pausas
    más largas entre algunas letras y más rápidas en otras.

    Args:
        page:     Página activa de Playwright
        selector: Selector CSS del campo de texto
        text:     Texto a escribir
    """
    logger.debug(f"⌨️  Escribiendo en '{selector}': '{text}'")
    page.click(selector)
    time.sleep(random.uniform(0.2, 0.5))

    for char in text:
        page.keyboard.type(char)
        time.sleep(random.uniform(0.02, 0.07))


def smooth_scroll_to(element: Locator) -> None:
    """
    Hace scroll suave hasta que el elemento sea visible en pantalla.

    Por qué: Un humano hace scroll para ver el elemento antes de clickearlo.
    Playwright normalmente hace scroll automático, pero esto lo hace más natural.

    NOTA: La plataforma Ferrum usa el tema Adaptable de Moodle, que tiene una
    sticky header (cabecera fija). Después del scroll_into_view, hacemos un
    pequeño scroll adicional hacia arriba para que el elemento no quede
    tapado detrás de esa cabecera.

    Args:
        element: Locator del elemento objetivo
    """
    element.scroll_into_view_if_needed()
    try:
        element.evaluate("el => window.scrollBy(0, -120)")
    except Exception:
        pass
    time.sleep(random.uniform(0.4, 0.8))


def hover_and_click(element: Locator) -> None:
    """
    Mueve el cursor encima del elemento (hover) y luego hace click.

    Por qué: Los humanos típicamente mueven el mouse sobre un elemento y
    lo observan brevemente antes de clickearlo. Hacer hover primero activa
    estilos CSS y es más natural.

    FALLBACK: El tema Adaptable de Moodle usa divs superpuestos (como
    `.w-100.text-truncate`) y una sticky header que pueden interceptar
    los eventos de puntero. Si el hover/click normal falla por esta razón,
    usamos click(force=True) como alternativa, que ignora los overlays.

    Args:
        element: Locator del elemento a clickear
    """
    try:
        element.hover()
        time.sleep(random.uniform(0.2, 0.6))
        element.click()
    except Exception as e:
        error_str = str(e)
        if "intercepts pointer events" in error_str or "element is not stable" in error_str or "timeout" in error_str.lower():
            logger.debug("   ⚠️  Overlay bloqueando click. Usando click forzado (force=True)...")
            element.click(force=True)
        else:
            raise
