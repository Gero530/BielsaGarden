import pygame
import display
from ui.pixel_font import draw_pixel_text
from ui.button import tablon

ESC = 3
CREMA = (255, 240, 200)
OSCURO = (30, 18, 6)
GRIS = (150, 146, 140)
_cache = {}


def _hueco(w, h):
    key = ("hueco", w, h)
    if key not in _cache:
        a, b = w // ESC, h // ESC
        s = pygame.Surface((a, b))
        s.fill((58, 34, 14))
        s.fill((76, 48, 22), (1, 1, a - 2, b - 2))
        s.fill((52, 32, 14), (1, 1, a - 2, 1)); s.fill((52, 32, 14), (1, 1, 1, b - 2))
        s.fill((164, 116, 60), (1, b - 2, a - 2, 1)); s.fill((164, 116, 60), (a - 2, 1, 1, b - 2))
        _cache[key] = pygame.transform.scale(s, (a * ESC, b * ESC))
    return _cache[key]


def _flecha(direccion, estado):
    key = ("flecha", direccion, estado)
    if key not in _cache:
        from ui.intro_art import build_cartel
        s = build_cartel("", 12, 14, 1, estado=estado).copy()
        top = {"normal": 1, "hover": 0, "apretado": 2, "bloqueado": 1}[estado]
        color = (110, 106, 100) if estado == "bloqueado" else (40, 22, 6)
        cy = top + 6
        for i in range(4):
            x = 4 + i if direccion > 0 else 7 - i
            s.fill(color, (x, cy - (3 - i), 1, 2 * (3 - i) + 1))
        _cache[key] = pygame.transform.scale(s, (12 * ESC, 14 * ESC))
    return _cache[key]


TILDE = ["......#", ".....##", "#...##.", "##.##..", ".###...", "..#...."]


def _casilla(marcada, hover):
    key = ("casilla", marcada, hover)
    if key not in _cache:
        s = pygame.Surface((11, 11))
        s.fill((232, 186, 112) if hover else (58, 34, 14))
        s.fill((76, 48, 22), (1, 1, 9, 9))
        s.fill((52, 32, 14), (1, 1, 9, 1)); s.fill((52, 32, 14), (1, 1, 1, 9))
        if marcada:
            for y, fila in enumerate(TILDE):
                for x, c in enumerate(fila):
                    if c == "#":
                        s.set_at((2 + x, 2 + y), (255, 214, 64))
        _cache[key] = pygame.transform.scale(s, (11 * ESC, 11 * ESC))
    return _cache[key]


class Tabs:

    def __init__(self, names, topleft, on_change, tab_size=(60, 14)):
        self.names = names
        self.active = 0
        self.on_change = on_change
        x, y = topleft
        self.size = tab_size
        self.rects = []
        for name in names:
            img = tablon(name, *tab_size)
            self.rects.append(img.get_rect(topleft=(x, y)))
            x += img.get_width() + 6

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.rects):
                if r.collidepoint(event.pos):
                    if i != self.active:
                        self.active = i
                        self.on_change(self.names[i])
                    return True
        return False

    def draw(self, surface):
        for i, (name, r) in enumerate(zip(self.names, self.rects)):
            surface.blit(tablon(name, *self.size, estado="hover" if i == self.active else "normal"), r)


class Selector:

    def __init__(self, label, options, index, topleft, on_change, width=600, x_valor=250, ancho_valor=90):
        self.label = label
        self.options = options
        self.index = index
        self.on_change = on_change
        self.enabled = True
        self.note = None
        x, y = topleft
        self.rect = pygame.Rect(x, y, width, 42)
        vx = x + x_valor
        self.left = pygame.Rect(vx, y, 12 * ESC, 14 * ESC)
        self.value_rect = pygame.Rect(self.left.right + 6, y, ancho_valor * ESC, 14 * ESC)
        self.right = pygame.Rect(self.value_rect.right + 6, y, 12 * ESC, 14 * ESC)

    @property
    def value(self):
        return self.options[self.index][0]

    def set_value(self, value):
        for i, (v, _) in enumerate(self.options):
            if v == value:
                self.index = i

    def handle_event(self, event):
        if not self.enabled or event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        if self.left.collidepoint(event.pos) and self.index > 0:
            self.index -= 1
        elif self.right.collidepoint(event.pos) and self.index < len(self.options) - 1:
            self.index += 1
        else:
            return False
        self.on_change(self.value)
        return True

    def _estado(self, rect, activa, mouse):
        if not activa:
            return "bloqueado"
        return "hover" if rect.collidepoint(mouse) else "normal"

    def draw(self, surface):
        mouse = display.get_mouse_pos()
        color = CREMA if self.enabled else GRIS
        draw_pixel_text(surface, self.label, color, 3, outline=OSCURO, midleft=(self.rect.x, self.rect.centery))
        surface.blit(_flecha(-1, self._estado(self.left, self.enabled and self.index > 0, mouse)), self.left)
        surface.blit(_flecha(1, self._estado(self.right, self.enabled and self.index < len(self.options) - 1, mouse)),
                     self.right)
        surface.blit(_hueco(self.value_rect.w, self.value_rect.h), self.value_rect)
        draw_pixel_text(surface, self.options[self.index][1], color, 2, center=self.value_rect.center)
        if not self.enabled and self.note:
            draw_pixel_text(surface, self.note, (255, 230, 140), 2, outline=OSCURO,
                            topleft=(self.rect.x, self.rect.bottom + 8))


class Checkbox:

    def __init__(self, label, value, topleft, on_change, escala=3):
        self.label = label
        self.value = value
        self.on_change = on_change
        self.escala = escala
        x, y = topleft
        from ui.pixel_font import text_width
        ancho_texto = text_width(label, escala) + 24
        self.box = pygame.Rect(x + ancho_texto, y + 4, 11 * ESC, 11 * ESC)
        self.rect = pygame.Rect(x, y, ancho_texto + self.box.w + 10, 42)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.value = not self.value
            self.on_change(self.value)
            return True
        return False

    def draw(self, surface):
        hover = self.rect.collidepoint(display.get_mouse_pos())
        draw_pixel_text(surface, self.label, CREMA, self.escala, outline=OSCURO,
                        midleft=(self.rect.x, self.box.centery))
        surface.blit(_casilla(self.value, hover), self.box)


def _perilla(estado):
    key = ("perilla", estado)
    if key not in _cache:
        from ui.intro_art import build_cartel
        s = build_cartel("", 8, 13, 1, estado=estado)
        _cache[key] = pygame.transform.scale(s, (8 * ESC, 13 * ESC))
    return _cache[key]


class Slider:

    ANCHO_BARRA = 300

    def __init__(self, label, valor, silenciado, topleft, on_change, x_barra=170):
        self.label = label
        self.valor = int(valor)
        self.silenciado = silenciado
        self.on_change = on_change
        self.arrastrando = False
        x, y = topleft
        self.rect = pygame.Rect(x, y, 0, 36)
        self.barra = pygame.Rect(x + x_barra, y + 9, self.ANCHO_BARRA, 6 * ESC)
        self.zona = self.barra.inflate(24, 20)
        self.valor_pos = (self.barra.right + 48, self.rect.centery)
        self.box = pygame.Rect(self.barra.right + 100, y + 2, 11 * ESC, 11 * ESC)
        self.rect.w = self.box.right - x

    def _desde_x(self, x):
        u = (x - self.barra.x) / self.barra.w
        nuevo = int(round(max(0.0, min(1.0, u)) * 100))
        if nuevo != self.valor:
            self.valor = nuevo
            self.on_change(self.valor, self.silenciado)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.box.inflate(8, 8).collidepoint(event.pos):
                self.silenciado = not self.silenciado
                self.on_change(self.valor, self.silenciado)
                return True
            if self.zona.collidepoint(event.pos):
                self.arrastrando = True
                self._desde_x(event.pos[0])
                return True
        elif event.type == pygame.MOUSEMOTION and self.arrastrando:
            self._desde_x(event.pos[0])
            return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.arrastrando:
            self.arrastrando = False
            return True
        elif event.type == pygame.MOUSEWHEEL:
            if self.zona.collidepoint(display.get_mouse_pos()):
                nuevo = max(0, min(100, self.valor + 5 * event.y))
                if nuevo != self.valor:
                    self.valor = nuevo
                    self.on_change(self.valor, self.silenciado)
                return True
        return False

    def draw(self, surface):
        mouse = display.get_mouse_pos()
        apagado = self.silenciado
        color = GRIS if apagado else CREMA
        draw_pixel_text(surface, self.label, color, 2, outline=OSCURO, midleft=(self.rect.x, self.rect.centery))
        surface.blit(_hueco(self.barra.w, self.barra.h), self.barra)
        lleno = (self.barra.w - 2 * ESC) * self.valor // 100 // ESC * ESC
        if lleno > 0:
            r = pygame.Rect(self.barra.x + ESC, self.barra.y + ESC, lleno, self.barra.h - 2 * ESC)
            surface.fill((120, 116, 110) if apagado else (226, 170, 40), r)
            surface.fill((160, 156, 150) if apagado else (255, 222, 96), (r.x, r.y, r.w, ESC))
        perilla_estado = ("hover" if self.arrastrando or self.zona.collidepoint(mouse) else "normal")
        if apagado:
            perilla_estado = "bloqueado"
        img = _perilla(perilla_estado)
        px = self.barra.x + (self.barra.w - 2 * ESC) * self.valor // 100 // ESC * ESC + ESC
        surface.blit(img, img.get_rect(center=(px, self.barra.centery + ESC)))
        draw_pixel_text(surface, f"{self.valor}%", color, 2, outline=OSCURO, center=self.valor_pos)
        surface.blit(_casilla(self.silenciado, self.box.inflate(8, 8).collidepoint(mouse)), self.box)


class CampoTexto:

    def __init__(self, texto, center, max_letras, on_enter, escala=3):
        self.texto = texto
        self.max = max_letras
        self.on_enter = on_enter
        self.escala = escala
        from ui.pixel_font import AVANCE
        w = (max_letras + 1) * AVANCE * escala + 36
        self.rect = pygame.Rect(0, 0, w // ESC * ESC, 20 * ESC)
        self.rect.center = center
        self.t = 0.0
        try:
            pygame.key.start_text_input()
        except pygame.error:
            pass

    @staticmethod
    def _valida(c):
        from ui.pixel_font import _G
        return c.upper() in _G and c not in "\r\n\t"

    def handle_event(self, event):
        if event.type == pygame.TEXTINPUT:
            for c in event.text:
                if self._valida(c) and len(self.texto) < self.max:
                    self.texto += c
            self.t = 0.0
            return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.texto = self.texto[:-1]
                self.t = 0.0
                return True
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.on_enter()
                return True
        return False

    def update(self, dt):
        self.t += dt

    def draw(self, surface):
        surface.blit(_hueco(self.rect.w, self.rect.h), self.rect)
        x = self.rect.x + 18
        r = draw_pixel_text(surface, self.texto.upper(), CREMA, self.escala, outline=OSCURO,
                            midleft=(x, self.rect.centery)) if self.texto else pygame.Rect(x, 0, 0, 0)
        if int(self.t * 2) % 2 == 0:
            alto = 7 * self.escala
            surface.fill((255, 214, 64), (r.right + (4 if self.texto else 0), self.rect.centery - alto // 2,
                                          self.escala * 2, alto))
