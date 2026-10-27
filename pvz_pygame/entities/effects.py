"""
Efectos visuales que no interactúan con nada: una animación que se reproduce
una vez en un lugar (ej: las ratas de Kenny) y un destello que se desvanece
(ej: el área de la explosión).
"""
import pygame
from ui.sprites import draw_sprite, anim_duration


class SpriteEffect:
    """Reproduce una animación de SPRITES una sola vez y desaparece."""

    def __init__(self, key, center):
        self.key = key
        self.center = center
        self.t = 0.0
        self.duration = anim_duration(key)
        self.alive = True

    def update(self, dt, world):
        self.t += dt
        if self.t >= self.duration:
            self.alive = False

    def draw(self, surface):
        draw_sprite(surface, self.key, self.center, 1.0, self.t)


class Flash:
    """Rectángulo de color que se desvanece (muestra el área de una explosión)."""

    def __init__(self, rect, color=(255, 170, 40), life=0.3, alpha=120):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.life = life
        self.max_life = life
        self.alpha = alpha
        self.alive = True

    def update(self, dt, world):
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def draw(self, surface):
        a = int(self.alpha * max(0.0, self.life) / self.max_life)
        overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(overlay, (*self.color, a), overlay.get_rect(), border_radius=14)
        surface.blit(overlay, self.rect.topleft)
