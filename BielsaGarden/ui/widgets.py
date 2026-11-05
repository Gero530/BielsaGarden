"""
Controles para menús: pestañas, selector con flechas y casilla de verificación.
Todos tienen handle_event(event) -> bool (True si usaron el evento) y draw(surface).
"""
import pygame
import display
from settings import COLORS
from ui.fonts import draw_text

PANEL = (40, 52, 36)
PANEL_BORDE = (25, 35, 22)
TAB_INACTIVA = (70, 90, 62)
TAB_HOVER = (90, 115, 80)


class Tabs:
    """Fila de pestañas. La activa se une visualmente con el panel de abajo."""

    def __init__(self, names, topleft, on_change, tab_size=(150, 40)):
        self.names = names
        self.active = 0
        self.on_change = on_change
        x, y = topleft
        w, h = tab_size
        self.rects = [pygame.Rect(x + i * (w + 6), y, w, h) for i in range(len(names))]

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
        mouse = display.get_mouse_pos()
        for i, (name, r) in enumerate(zip(self.names, self.rects)):
            if i == self.active:
                color = PANEL
            else:
                color = TAB_HOVER if r.collidepoint(mouse) else TAB_INACTIVA
            pygame.draw.rect(surface, color, r, border_top_left_radius=8, border_top_right_radius=8)
            pygame.draw.rect(surface, PANEL_BORDE, r, 3, border_top_left_radius=8, border_top_right_radius=8)
            if i == self.active:   # tapa el borde inferior (y el del panel) para que la pestaña "entre" al panel
                pygame.draw.rect(surface, PANEL, (r.x + 3, r.bottom - 3, r.w - 6, 7))
            draw_text(surface, name, 28, COLORS["texto"] if i == self.active else (210, 220, 200),
                      center=r.center)


class Selector:
    """Etiqueta + valor con flechas  <  valor  >  para recorrer opciones."""

    def __init__(self, label, options, index, topleft, on_change, width=520):
        self.label = label
        self.options = options          # lista de (valor, texto)
        self.index = index
        self.on_change = on_change
        self.enabled = True
        self.note = None                # texto aclaratorio cuando está deshabilitado
        x, y = topleft
        self.rect = pygame.Rect(x, y, width, 44)
        vx = x + 210
        self.left = pygame.Rect(vx, y + 4, 36, 36)
        self.value_rect = pygame.Rect(vx + 40, y + 4, 220, 36)
        self.right = pygame.Rect(self.value_rect.right + 4, y + 4, 36, 36)

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

    def _arrow(self, surface, rect, direction, active, mouse):
        if not active:
            color = (70, 80, 66)
        else:
            color = COLORS["boton_hover"] if rect.collidepoint(mouse) else COLORS["boton"]
        pygame.draw.rect(surface, color, rect, border_radius=6)
        pygame.draw.rect(surface, PANEL_BORDE, rect, 2, border_radius=6)
        cx, cy = rect.center
        pts = [(cx + 6, cy - 9), (cx + 6, cy + 9), (cx - 7, cy)] if direction < 0 else \
              [(cx - 6, cy - 9), (cx - 6, cy + 9), (cx + 7, cy)]
        pygame.draw.polygon(surface, COLORS["texto"] if active else (140, 140, 140), pts)

    def draw(self, surface):
        mouse = display.get_mouse_pos()
        txt_color = COLORS["texto"] if self.enabled else (150, 150, 150)
        draw_text(surface, self.label, 30, txt_color, topleft=(self.rect.x, self.rect.y + 10))
        self._arrow(surface, self.left, -1, self.enabled and self.index > 0, mouse)
        self._arrow(surface, self.right, 1, self.enabled and self.index < len(self.options) - 1, mouse)
        pygame.draw.rect(surface, (25, 32, 22), self.value_rect, border_radius=6)
        draw_text(surface, self.options[self.index][1], 28, txt_color, center=self.value_rect.center)
        if not self.enabled and self.note:
            draw_text(surface, self.note, 20, (200, 200, 170), topleft=(self.left.x, self.rect.bottom + 2))


class Checkbox:
    """Casilla de verificación con etiqueta. Se puede hacer clic en la casilla o en el texto."""

    def __init__(self, label, value, topleft, on_change):
        self.label = label
        self.value = value
        self.on_change = on_change
        x, y = topleft
        self.box = pygame.Rect(x + 210, y + 6, 32, 32)
        self.rect = pygame.Rect(x, y, 210 + 32 + 10, 44)   # zona clickeable (texto + casilla)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.value = not self.value
            self.on_change(self.value)
            return True
        return False

    def draw(self, surface):
        hover = self.rect.collidepoint(display.get_mouse_pos())
        draw_text(surface, self.label, 30, COLORS["texto"], topleft=(self.rect.x, self.rect.y + 10))
        pygame.draw.rect(surface, (25, 32, 22), self.box, border_radius=6)
        pygame.draw.rect(surface, COLORS["boton_hover"] if hover else COLORS["boton"], self.box, 3, border_radius=6)
        if self.value:
            b = self.box
            pygame.draw.lines(surface, COLORS["verde"], False,
                              [(b.x + 7, b.centery), (b.x + 13, b.bottom - 8), (b.right - 6, b.y + 7)], 5)
