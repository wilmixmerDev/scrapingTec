import time
import random

from loguru import logger
from playwright.sync_api import Page

from .human_behavior import random_delay, smooth_scroll_to, hover_and_click, human_type


def read_forum_posts(page: Page) -> None:
    """
    Lee y hace hover sobre los posts existentes del foro (BONUS).

    Por qué: Un estudiante real entraría al foro, leería los posts
    de otros compañeros antes de publicar el suyo. Esta función
    simula ese comportamiento para que el bot sea más natural.

    Estrategia:
    - Busca hasta 3 posts existentes en el foro
    - Hace scroll y hover sobre cada uno (simula "leer")
    - Espera un tiempo proporcional al "tiempo de lectura"

    Args:
        page: Página activa de Playwright
    """
    logger.info("👀 Leyendo posts existentes del foro (comportamiento humano)...")

    post_selectors = [
        ".forumpost",
        ".post.clearfix",
        ".discussion-list .discussion",
        "article.forum-post",
        "[data-region='post']",
    ]

    posts_found = False

    for selector in post_selectors:
        posts = page.locator(selector).all()
        if posts:
            posts_found = True
            posts_to_read = posts[:min(3, len(posts))]
            logger.info(f"   📖 Encontré {len(posts)} post(s). Leyendo {len(posts_to_read)}...")

            for i, post in enumerate(posts_to_read):
                try:
                    smooth_scroll_to(post)
                    post.hover()
                    read_time = random.uniform(2.0, 4.0)
                    logger.debug(f"   📰 Leyendo post {i + 1}/{len(posts_to_read)} ({read_time:.1f}s)...")
                    time.sleep(read_time)
                except Exception as e:
                    logger.debug(f"   ⚠️ No se pudo leer post {i + 1}: {e}")
                    continue
            break

    if not posts_found:
        logger.info(
            "   ℹ️ No se encontraron posts previos o el foro está vacío. "
            "Procediendo a publicar..."
        )


def post_comment(page: Page, comment_text: str) -> None:
    """
    Publica un comentario en el foro.

    Flujo:
    1. Encuentra el botón para iniciar la publicación
    2. Hace click en el botón
    3. Escribe el texto en el editor (TinyMCE o textarea)
    4. Envía el formulario
    5. Verifica que la publicación fue exitosa

    Args:
        page:         Página activa de Playwright
        comment_text: Texto del comentario a publicar

    Raises:
        Exception: Si no se puede publicar el comentario
    """
    logger.info(f"✍️  Preparando para publicar: '{comment_text}'")

    _click_reply_button(page)

    page.wait_for_load_state("networkidle")
    random_delay(1.5, 2.5)

    _write_in_editor(page, comment_text)
    random_delay(0.8, 1.5)

    _submit_post(page)

    _verify_post_published(page, comment_text)


def _click_reply_button(page: Page) -> None:
    """
    Encuentra y hace click en el botón para iniciar una publicación.

    En Moodle, este botón puede tener diferentes textos:
    - "Añadir un nuevo tema de debate" (para crear nuevo tema)
    - "Responder" (para responder a un tema existente)
    - "Reply" (en inglés)

    Raises:
        Exception: Si no se encuentra ningún botón de publicación
    """
    logger.info("🔘 Buscando botón para publicar...")

    selectors = [
        "a.btn-primary[href='#collapseAddForm']",      # ID del colapsable
        "a:has-text('Add discussion topic')",           # Texto en inglés
        "a:has-text('Añadir un nuevo tema')",           # Texto en español
        "a:has-text('Nuevo tema')",
    ]

    for selector in selectors:
        try:
            button = page.locator(selector).first
            if button.is_visible(timeout=3_000):
                logger.info(f"   ✅ Botón encontrado con selector: '{selector}'")
                smooth_scroll_to(button)
                random_delay(0.5, 1.0)
                button.click()

                page.wait_for_selector("input#id_subject", state="visible", timeout=10_000)
                return
        except Exception:
            continue

    try:
        button = page.get_by_role("button", name="Add discussion topic").first
        if button.is_visible(timeout=2_000):
            logger.info("   ✅ Botón (por rol) encontrado.")
            smooth_scroll_to(button)
            random_delay(0.5, 1.0)
            button.click()
            return
    except Exception:
        pass

    raise Exception(
        "❌ No se encontró botón para publicar en el foro. "
        "Puede que ya hayas publicado, o el foro esté cerrado."
    )


def _write_in_editor(page: Page, text: str) -> None:
    """
    Escribe el texto en el editor del foro.

    Moodle tiene dos tipos de editor según la configuración:
    1. TinyMCE: Editor visual dentro de un <iframe> (más común)
    2. Textarea: Campo de texto simple (versión accesible)

    Primero intentamos TinyMCE, y si falla, usamos textarea como fallback.

    Args:
        page: Página activa de Playwright
        text: Texto a escribir en el editor
    """
    logger.info("📝 Escribiendo texto en el editor...")

    try:
        logger.debug("   ✍️  Completando campo de Asunto...")
        subject = page.locator("input#id_subject")
        subject.click()
        human_type(page, "input#id_subject", "No soy un robot")
        random_delay(0.8, 1.2)
    except Exception as e:
        logger.warning(f"   ⚠️ No se pudo completar el asunto: {e}")

    try:
        editor_selector = "div#id_messageeditable"
        editor = page.locator(editor_selector)
        
        if editor.count() > 0:
            logger.info("   ✅ Editor Atto detectado (DIV editable)")
            editor.scroll_into_view_if_needed()
            editor.click()
            random_delay(0.5, 1.0)

            human_type(page, editor_selector, text)
            return
    except Exception as e:
        logger.debug(f"   ℹ️ Atto editor falló: {e}. Probando textarea...")

    try:
        textarea_selectors = [
            "textarea[id*='message']",
            "textarea[name*='message']",
            "textarea[id*='post']",
            ".fcontainer textarea",
            "form textarea",
        ]

        for sel in textarea_selectors:
            try:
                textarea = page.locator(sel).first
                if textarea.count() > 0 and textarea.is_visible(timeout=3_000):
                    textarea.click()
                    time.sleep(random.uniform(0.3, 0.6))
                    textarea.fill("")
                    time.sleep(0.2)
                    human_type(page, sel, text)
                    logger.info("   ✅ Texto escrito en textarea simple")
                    return
            except Exception:
                continue

    except Exception as e:
        logger.debug(f"   ℹ️ Textarea fallback también falló: {e}")

    try:
        content_editable = page.locator("[contenteditable='true']").first
        if content_editable.is_visible(timeout=3_000):
            content_editable.click()
            time.sleep(random.uniform(0.3, 0.6))
            for char in text:
                page.keyboard.type(char)
                time.sleep(random.uniform(0.06, 0.15))
            logger.info("   ✅ Texto escrito en elemento contenteditable")
            return
    except Exception:
        pass

    raise Exception(
        "❌ No se pudo encontrar el editor de texto del foro. "
        "Ni TinyMCE, textarea, ni contenteditable fueron encontrados."
    )


def _submit_post(page: Page) -> None:
    """
    Envía el formulario del post haciendo click en el botón de envío.

    En Moodle, el botón de envío puede tener diferentes textos
    dependiendo del idioma y la versión.

    Raises:
        Exception: Si no se encuentra el botón de envío
    """
    logger.info("📤 Enviando publicación...")

    submit_selectors = [
        "input#id_submitbutton",    # ID exacto verificado
        "input[type='submit'][value*='Post']",
        "input[type='submit'][value*='Enviar']",
    ]

    for sel in submit_selectors:
        try:
            button = page.locator(sel).first
            if button.is_visible(timeout=3_000):
                smooth_scroll_to(button)
                random_delay(1.5, 2.5)  # Pausa de seguridad antes de enviar
                button.click()
                page.wait_for_load_state("networkidle")
                logger.info("   ✅ Formulario enviado exitosamente.")
                return
        except Exception:
            continue

    raise Exception("❌ No se encontró el botón de envío del formulario del foro.")


def _verify_post_published(page: Page, comment_text: str) -> None:
    """
    Verifica que el comentario fue publicado correctamente.

    Busca el texto del comentario en la página actual para confirmar
    que la publicación fue exitosa.

    Args:
        page:         Página activa de Playwright
        comment_text: Texto que debería aparecer si la publicación fue exitosa
    """
    logger.info("🔍 Verificando que la publicación fue exitosa...")
    random_delay(1.0, 2.0)

    try:
        page.wait_for_selector(
            f"*:has-text('{comment_text}')",
            timeout=15_000
        )
        logger.success(f"✅ ¡Verificado! El texto '{comment_text}' está visible en el foro.")
    except Exception:
        logger.warning(
            f"⚠️ No se pudo verificar automáticamente la publicación del texto "
            f"'{comment_text}'. Revisa el screenshot para confirmar."
        )
