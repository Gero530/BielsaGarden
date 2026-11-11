import pygame
import logros
from settings import SCREEN_W
from ui.button import tablon
from ui.pixel_font import draw_pixel_text, text_width

DURACION = 3.6
ENTRADA = 0.3
_cache = {}
_cola = []
_actual = None


def icono(logro, tam, gris=False):
    key = (logro["id"], tam, gris)
    if key in _cache:
        return _cache[key]
    fuente, cual = logro["icono"]
    img = None
    if fuente == "retrato":
        from ui.dialogo import retrato_img
        img = retrato_img(cual)
    else:
        from ui.sprites import get_frames
        frames = get_frames(fuente, 1)
        if frames:
            img = frames[min(cual, len(frames) - 1)]
    out = pygame.Surface((tam, tam), pygame.SRCALPHA)
    if img is None:
        draw_pixel_text(out, "?", (255, 230, 140), 6, center=(tam // 2, tam // 2))
    else:
        caja = img.get_bounding_rect()
        if fuente == "retrato":
            caja.h = min(caja.h, caja.w)
        img = img.subsurface(caja)
        w, h = img.get_size()
        f = min(tam / w, tam / h)
        if f >= 2:
            f = int(f)
        img = pygame.transform.scale(img, (max(1, int(w * f)), max(1, int(h * f))))
        out.blit(img, img.get_rect(center=(tam // 2, tam // 2)))
    if gris:
        out = pygame.transform.grayscale(out)
        out.fill((150, 150, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)
    _cache[key] = out
    return out


def recortar(texto, escala, ancho):
    if text_width(texto, escala) <= ancho:
        return texto
    while texto and text_width(texto + "...", escala) > ancho:
        texto = texto[:-1]
    return texto.rstrip(" ,.") + "..."


def dibujar(surface, dt):
    global _actual
    _cola.extend(logros.tomar_nuevos())
    if _actual is None:
        if not _cola:
            return
        _actual = [_cola.pop(0), 0.0]
    logro, t = _actual
    t += dt
    _actual[1] = t
    if t >= DURACION:
        _actual = None
        return
    panel = tablon("", 216, 32, 2)
    entra = min(1.0, t / ENTRADA, (DURACION - t) / ENTRADA)
    x = SCREEN_W - int((panel.get_width() + 12) * (1 - (1 - entra) ** 2))
    r = panel.get_rect(topleft=(x, 104))
    surface.blit(panel, r)
    surface.blit(icono(logro, 44), (r.x + 12, r.y + 9))
    draw_pixel_text(surface, "¡LOGRO DESBLOQUEADO!", (255, 230, 120), 2, outline=(30, 18, 6),
                    topleft=(r.x + 66, r.y + 11))
    draw_pixel_text(surface, recortar(logro["nombre"].upper(), 2, panel.get_width() - 86), (255, 240, 200), 2,
                    outline=(30, 18, 6), topleft=(r.x + 66, r.y + 34))
