"""Pantalla de victoria / derrota. Se dibuja encima de la última imagen de la partida."""
import pygame
from settings import SCREEN_W, SCREEN_H, COLORS
from scenes.base import Scene
from ui.button import Button
from ui.fonts import draw_text


class ResultScene(Scene):
    def __init__(self, game, victory, level_index, background=None, stats=None):
        super().__init__(game)
        self.victory = victory
        self.level_index = level_index
        self.background = background      # captura de la partida
        self.stats = stats or {}
        cx = SCREEN_W // 2
        label = "Jugar de nuevo" if victory else "Reintentar"
        self.buttons = [
            Button(label, (cx, 370), self.retry, size=(260, 56)),
            Button("Menú principal", (cx, 445), self.to_menu, size=(260, 56)),
        ]

    def retry(self):
        from scenes.gameplay import GameplayScene
        self.game.change_scene(GameplayScene(self.game, self.level_index))

    def to_menu(self):
        from scenes.menu import MenuScene
        self.game.change_scene(MenuScene(self.game))

    def handle_event(self, event):
        for b in self.buttons:
            if b.handle_event(event):
                break

    def draw(self, surface):
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill(COLORS["bg"])
        shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 160))
        surface.blit(shade, (0, 0))

        if self.victory:
            draw_text(surface, "¡VICTORIA!", 90, COLORS["sol"], center=(SCREEN_W // 2, 170), bold=True)
            draw_text(surface, "Defendiste el jardín", 34, COLORS["texto"], center=(SCREEN_W // 2, 235))
        else:
            draw_text(surface, "LOS ZOMBIES", 80, COLORS["rojo"], center=(SCREEN_W // 2, 150), bold=True)
            draw_text(surface, "SE COMIERON TU CEREBRO", 52, COLORS["rojo"], center=(SCREEN_W // 2, 215), bold=True)

        if self.stats:
            line = f"Zombies eliminados: {self.stats.get('kills', 0)}   ·   Tiempo: {int(self.stats.get('time', 0))} s"
            draw_text(surface, line, 26, COLORS["texto"], center=(SCREEN_W // 2, 290))

        for b in self.buttons:
            b.draw(surface)
