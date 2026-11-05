import random
import pygame
import display
from settings import COLORS
from ui.fonts import draw_text

APRETADO = 0.1          # segundos que se ve hundido el tablón antes de hacer la acción
DESTELLO = 0.35         # segundos que tarda el brillo en cruzar el tablón al pasar el mouse
_pendientes = []        # [clave, segundos, acción]: tablones apretados esperando para actuar
_astillas = []          # [x, y, vx, vy, edad, color, tamaño]


def apretar(rect, esc, accion, clave):
    """Hunde el tablón un momento, hace saltar astillas y recién después ejecuta la acción."""
    _pendientes.append([clave, APRETADO, accion])
    # Saltan desde las esquinas de abajo hacia afuera, para que se vean contra el fondo
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
    """Lo llama el bucle principal en cada cuadro (en tiempo real, no se acelera)."""
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
    """Astillas encima de todo (cuadraditos del tamaño de un píxel del tablón)."""
    for x, y, _, _, _, color, t in _astillas:
        surface.fill(color, (int(x) // t * t, int(y) // t * t, t * 2, t))     # astilla de 2x1 píxeles


class Button:
    """Botón rectangular simple con hover, callback y estado deshabilitado."""

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
    """Ancho mínimo para que los clavos de las esquinas no tapen las letras."""
    from ui.pixel_font import text_width
    return max(w, text_width(texto, texto_esc) + 20) if texto else w


def tablon(texto, w, h, esc=3, texto_esc=1, hover=False, estado=None, destello=None):
    """El tablón de madera (ui/intro_art.build_cartel) agrandado x`esc` sin suavizado.
    estado: normal / hover / apretado / bloqueado. destello: 0..1 mientras cruza el brillo."""
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
    """Recuerda cuándo empezó el mouse a estar encima, para que el brillo cruce una sola vez."""

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
    """Botón con el tablón de madera del menú. size: tamaño en píxeles de dibujo (se agranda x`esc`)."""

    def __init__(self, text, center, on_click, size=(100, 16), esc=3, texto_esc=1):
        self.text = text
        self.size = (ancho_tablon(text, size[0], texto_esc), size[1])
        self.esc = esc
        self.texto_esc = texto_esc
        self.rect = pygame.Rect(0, 0, self.size[0] * esc, self.size[1] * esc)
        self.rect.center = center
        self.on_click = on_click
        self.enabled = True          # False: bloqueado (gris con tablas cruzadas, no responde)
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
