"""Pantalla de inicio."""
import pygame
from settings import SCREEN_W, SCREEN_H, COLORS
from scenes.base import Scene
from ui.button import Button
from ui.fonts import draw_text
from entities.plants import draw_plant_icon


def draw_menu_background(surface):
    """Fondo de franjas de césped (lo comparten el menú y la pantalla de opciones)."""
    surface.fill(COLORS["cesped_2"])
    for i in range(0, SCREEN_W, 80):
        if (i // 80) % 2 == 0:
            pygame.draw.rect(surface, COLORS["cesped_1"], (i, 0, 80, SCREEN_H))


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        cx = SCREEN_W // 2
        self.buttons = [
            Button("Jugar", (cx, 310), self.start),
            Button("Opciones", (cx, 380), self.options),
            Button("Salir", (cx, 450), game.quit),
        ]
        self.t = 0.0

    def start(self):
        from scenes.gameplay import GameplayScene
        self.game.change_scene(GameplayScene(self.game, level_index=0))

    def options(self):
        from scenes.options import OptionsScene
        self.game.change_scene(OptionsScene(self.game))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.start()
        for b in self.buttons:
            if b.handle_event(event):
                break

    def update(self, dt):
        self.t += dt

    def draw(self, surface):
        draw_menu_background(surface)

        panel = pygame.Rect(0, 0, 560, 400)
        panel.center = (SCREEN_W // 2, SCREEN_H // 2 + 10)
        shade = pygame.Surface(panel.size, pygame.SRCALPHA)
        shade.fill((0, 0, 0, 120))
        surface.blit(shade, panel.topleft)

        draw_text(surface, "PLANTAS vs ZOMBIES", 64, COLORS["sol"], center=(SCREEN_W // 2, 160), bold=True)
        draw_text(surface, "versión pygame", 28, COLORS["texto"], center=(SCREEN_W // 2, 205))

        draw_plant_icon(surface, "girasol", (SCREEN_W // 2 - 200, 260), 0.9)
        draw_plant_icon(surface, "lanzaguisantes", (SCREEN_W // 2 + 200, 260), 0.9)

        for b in self.buttons:
            b.draw(surface)

        draw_text(surface, "Clic: plantar / juntar soles   ·   Clic der.: cancelar   ·   P / Esc: pausa",
                  22, COLORS["texto"], center=(SCREEN_W // 2, SCREEN_H - 30))
