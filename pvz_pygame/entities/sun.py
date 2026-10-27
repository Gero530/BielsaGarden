"""Unidades de energía (el dedo): caen del cielo o las suelta Cartman cocinando. Se juntan con clic."""
import pygame
from settings import COLORS, SOL_VALOR, SOL_VIDA, SOL_VEL_CAIDA
from ui.sprites import draw_sprite

RADIO = 34              # tamaño del dedo (con su brillo) y de la zona donde se hace clic


class Sun:
    def __init__(self, x, y, target_y, value=SOL_VALOR):
        self.x = x
        self.y = y
        self.target_y = target_y      # hasta dónde cae
        self.value = value
        self.life = SOL_VIDA
        self.alive = True
        self.t = 0.0                  # para la animación de pulso

    @property
    def rect(self):
        return pygame.Rect(self.x - RADIO, self.y - RADIO, RADIO * 2, RADIO * 2)

    def update(self, dt):
        self.t += dt
        if self.y < self.target_y:
            self.y = min(self.target_y, self.y + SOL_VEL_CAIDA * dt)
        else:
            self.life -= dt
            if self.life <= 0:
                self.alive = False

    def clicked(self, pos):
        # Un poco más generoso que el dibujo para que sea fácil agarrarlo
        return (pos[0] - self.x) ** 2 + (pos[1] - self.y) ** 2 <= (RADIO + 8) ** 2

    def draw(self, surface):
        pulse = 2 if int(self.t * 4) % 2 == 0 else 0
        # Parpadea cuando está por desaparecer
        if self.life < 2.5 and int(self.t * 8) % 2 == 0:
            return
        c = (int(self.x), int(self.y))
        # El dedo con resplandor; si no está el sprite, el círculo amarillo de siempre
        if draw_sprite(surface, "dedo", c, 1.0, self.t):
            return
        pygame.draw.circle(surface, COLORS["sol_borde"], c, RADIO + pulse)
        pygame.draw.circle(surface, COLORS["sol"], c, RADIO - 5 + pulse)
