"""
HUD superior: contador de soles, barra de cartas (semillas), pala y
barra de progreso del nivel.
"""
import pygame
from settings import COLORS, PLANT_DATA, SCREEN_W
from ui.fonts import draw_text
from entities.plants import draw_plant_icon
from ui.sprites import draw_sprite

CARD_W, CARD_H = 70, 80
HUD_H = 92


class SeedCard:
    def __init__(self, key, x, y):
        self.key = key
        self.data = PLANT_DATA[key]
        self.rect = pygame.Rect(x, y, CARD_W, CARD_H)
        self.cooldown = 0.0          # segundos restantes de recarga

    @property
    def cost(self):
        return self.data["costo"]

    def ready(self, sun):
        return self.cooldown <= 0 and sun >= self.cost

    def start_cooldown(self):
        self.cooldown = self.data["recarga"]

    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown = max(0.0, self.cooldown - dt)

    def draw(self, surface, sun, selected):
        border = COLORS["carta_sel"] if selected else COLORS["carta_borde"]
        pygame.draw.rect(surface, COLORS["carta"], self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, 4 if selected else 2, border_radius=6)

        draw_plant_icon(surface, self.key, (self.rect.centerx, self.rect.y + 30), 0.55)
        draw_text(surface, self.data["nombre"], 16, COLORS["texto_osc"],
                  center=(self.rect.centerx, self.rect.bottom - 22))
        draw_text(surface, str(self.cost), 20, COLORS["texto_osc"],
                  center=(self.rect.centerx, self.rect.bottom - 9), bold=True)

        # Oscurecer si no se puede usar; la parte en recarga se ve más oscura
        if not self.ready(sun):
            shade = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            shade.fill((0, 0, 0, 90))
            surface.blit(shade, self.rect.topleft)
        if self.cooldown > 0:
            frac = self.cooldown / self.data["recarga"]
            h = int(self.rect.height * frac)
            shade = pygame.Surface((self.rect.width, h), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 120))
            surface.blit(shade, self.rect.topleft)


class HUD:
    def __init__(self, plant_keys):
        self.sun_rect = pygame.Rect(10, 6, 90, CARD_H)
        self.cards = [SeedCard(k, 110 + i * (CARD_W + 6), 6) for i, k in enumerate(plant_keys)]
        x_pala = 110 + len(self.cards) * (CARD_W + 6) + 14
        self.shovel_rect = pygame.Rect(x_pala, 6, CARD_W, CARD_H)

    def update(self, dt):
        for c in self.cards:
            c.update(dt)

    def card_at(self, pos):
        for c in self.cards:
            if c.rect.collidepoint(pos):
                return c
        return None

    def get_card(self, key):
        for c in self.cards:
            if c.key == key:
                return c
        return None

    def draw(self, surface, sun, selected, progress, level_name):
        # Sin franja de fondo: las cartas y el contador se ven sobre el fondo del jardín

        # Contador de soles
        pygame.draw.rect(surface, COLORS["carta"], self.sun_rect, border_radius=8)
        pygame.draw.rect(surface, COLORS["carta_borde"], self.sun_rect, 2, border_radius=8)
        c = (self.sun_rect.centerx, self.sun_rect.y + 30)
        if not draw_sprite(surface, "dedo", c, 0.55, pygame.time.get_ticks() / 1000):
            pygame.draw.circle(surface, COLORS["sol_borde"], c, 20)
            pygame.draw.circle(surface, COLORS["sol"], c, 16)
        draw_text(surface, str(sun), 30, COLORS["texto_osc"],
                  center=(self.sun_rect.centerx, self.sun_rect.bottom - 16), bold=True)

        for card in self.cards:
            card.draw(surface, sun, selected == card.key)

        # Pala
        sel = selected == "pala"
        pygame.draw.rect(surface, (170, 160, 150), self.shovel_rect, border_radius=6)
        pygame.draw.rect(surface, COLORS["carta_sel"] if sel else COLORS["carta_borde"],
                         self.shovel_rect, 4 if sel else 2, border_radius=6)
        draw_shovel(surface, (self.shovel_rect.centerx, self.shovel_rect.y + 34))
        draw_text(surface, "Pala", 18, COLORS["texto_osc"],
                  center=(self.shovel_rect.centerx, self.shovel_rect.bottom - 12))

        # Nombre del nivel + barra de progreso
        draw_text_shadow(surface, level_name, 26, topleft=(SCREEN_W - 270, 14))
        bar = pygame.Rect(SCREEN_W - 270, 46, 250, 18)
        pygame.draw.rect(surface, (50, 35, 20), bar, border_radius=6)
        fill = bar.copy()
        fill.width = int(bar.width * progress)
        pygame.draw.rect(surface, COLORS["verde"], fill, border_radius=6)
        pygame.draw.rect(surface, (30, 20, 10), bar, 2, border_radius=6)
        draw_text_shadow(surface, "Progreso", 18, topleft=(bar.x, bar.bottom + 4))


def draw_text_shadow(surface, text, size, topleft):
    """Texto blanco con sombra oscura, para que se lea sobre el cielo del fondo."""
    x, y = topleft
    draw_text(surface, text, size, (30, 30, 30), topleft=(x + 2, y + 2))
    draw_text(surface, text, size, COLORS["texto"], topleft=(x, y))


def draw_shovel(surface, center, scale=1.0):
    x, y = center
    s = scale
    pygame.draw.line(surface, (120, 80, 40), (x - 14 * s, y - 14 * s), (x + 6 * s, y + 6 * s), max(1, int(5 * s)))
    pygame.draw.polygon(surface, (190, 190, 200), [
        (x + 2 * s, y + 2 * s), (x + 18 * s, y + 6 * s),
        (x + 20 * s, y + 20 * s), (x + 6 * s, y + 18 * s)])
