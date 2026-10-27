import pygame
import display
from settings import COLORS
from ui.fonts import draw_text


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
