import random
import pygame
import display
from settings import COLORS
from ui.fonts import draw_text

APRETADO = 0.1
DESTELLO = 0.35
_pendientes = []
_astillas = []


def apretar(rect, esc, accion, clave):
    _pendientes.append([clave, APRETADO, accion])
    for i in range(3):
        lado = (-1, 1, random.choice((-1, 1)))[i]
        x = rect.left + esc * 3 if lado < 0 else rect.right - esc * 3
        _astillas.append([x, rect.bottom - esc * 3, lado * random.uniform(120, 200), random.uniform(-220, -120), 0.0,
                          ((232, 190, 128), (58, 34, 14), (200, 150, 86))[i], esc])


def apretado(clave):
    return any(p[0] == clave for p in _pendientes)


def ocupado():
    return bool(_pendientes)


def actualizar(dt):
    for p in list(_pendientes):
        p[1] -= dt
        if p[1] <= 0:
            _pendientes.remove(p)
            p[2]()
    for a in _astillas:
        a[0] += a[2] * dt
        a[1] += a[3] * dt
        a[3] += 900 * dt
        a[4] += dt
    _astillas[:] = [a for a in _astillas if a[4] < 0.45]


def dibujar_efectos(surface):
    for x, y, _, _, _, color, t in _astillas:
        surface.fill(color, (int(x) // t * t, int(y) // t * t, t * 2, t))


class Button:

    def __init__(self, text, center, on_click, size=(220, 56), font_size=34):
        self.text = text
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = center
        self.on_click = on_click
        self.font_size = font_size
        self.enabled = True

    def handle_event(self, event):
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()
                return True
        return False

    def draw(self, surface):
        if self.enabled:
            hover = self.rect.collidepoint(display.get_mouse_pos())
            color = COLORS["boton_hover"] if hover else COLORS["boton"]
            text_color = COLORS["texto"]
        else:
            color = (90, 100, 90)
            text_color = (170, 170, 170)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (30, 60, 25), self.rect, 3, border_radius=10)
        draw_text(surface, self.text, self.font_size, text_color, center=self.rect.center)


def ancho_tablon(texto, w, texto_esc=1):
    from ui.pixel_font import text_width
    return max(w, text_width(texto, texto_esc) + 20) if texto else w


def tablon(texto, w, h, esc=3, texto_esc=1, hover=False, estado=None, destello=None):
    from ui.intro_art import build_cartel, con_destello, _cache
    w = ancho_tablon(texto, w, texto_esc)
    estado = estado or ("hover" if hover else "normal")
    if destello is not None:
        img = con_destello(build_cartel(texto, w, h, texto_esc, estado=estado), destello)
        return pygame.transform.scale(img, (w * esc, h * esc))
    key = ("tablon", texto, w, h, esc, texto_esc, estado)
    if key not in _cache:
        img = build_cartel(texto, w, h, texto_esc, estado=estado)
        _cache[key] = pygame.transform.scale(img, (w * esc, h * esc))
    return _cache[key]


class Destello:

    def __init__(self):
        self.desde = None

    def fase(self, hover):
        if not hover:
            self.desde = None
            return None
        ahora = pygame.time.get_ticks() / 1000
        if self.desde is None:
            self.desde = ahora
        u = (ahora - self.desde) / DESTELLO
        return u if u < 1 else None


class CartelButton:

    def __init__(self, text, center, on_click, size=(100, 16), esc=3, texto_esc=1):
        self.text = text
        self.size = (ancho_tablon(text, size[0], texto_esc), size[1])
        self.esc = esc
        self.texto_esc = texto_esc
        self.rect = pygame.Rect(0, 0, self.size[0] * esc, self.size[1] * esc)
        self.rect.center = center
        self.on_click = on_click
        self.enabled = True
        self.destello = Destello()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            if self.enabled and not ocupado():
                apretar(self.rect, self.esc, self.on_click, self)
            return True
        return False

    def estado(self):
        if not self.enabled:
            return "bloqueado"
        if apretado(self):
            return "apretado"
        return "hover" if self.rect.collidepoint(display.get_mouse_pos()) else "normal"

    def draw(self, surface):
        estado = self.estado()
        hover = estado == "hover"
        img = tablon(self.text, *self.size, self.esc, self.texto_esc, estado=estado,
                     destello=self.destello.fase(hover))
        surface.blit(img, self.rect.move(-self.esc * 2 if hover else 0, 0))
