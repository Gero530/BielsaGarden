import math
import random
import pygame
from settings import SCREEN_W, SCREEN_H, COLORS
from scenes.base import Scene
from levels import LEVELS
from ui.button import CartelButton, tablon, ancho_tablon
from ui.pixel_font import draw_pixel_text
from ui.sprites import draw_sprite, anim_duration
from data.catalogo import FRASE_KENNY_EXPLOTA
from ui import musica

PAPELITOS = ((220, 40, 40), (255, 214, 64), (60, 110, 220), (60, 190, 80), (255, 255, 255), (246, 146, 34))
N_PAPELITOS = 70
LADO_X = 160

OSCURECER = (90, 90, 100)


class ResultScene(Scene):
    def __init__(self, game, victory, level_index, background=None, stats=None):
        super().__init__(game)
        self.victory = victory
        self.level_index = level_index
        self.stats = stats or {}
        self.background = background.copy() if background else pygame.Surface((SCREEN_W, SCREEN_H))
        self.background.fill(OSCURECER, special_flags=pygame.BLEND_MULT)
        self.t = 0.0

        acciones = []
        hay_siguiente = level_index + 1 < len(LEVELS)
        if victory and hay_siguiente:
            acciones.append(("SIGUIENTE NIVEL", self.siguiente))
        acciones += [("REINTENTAR", self.retry), ("VOLVER AL MAPA", self.to_map), ("MENÚ PRINCIPAL", self.to_menu)]
        self.panel = tablon("", 120, 128)
        self.panel_rect = self.panel.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 20))
        y0 = self.panel_rect.y + 170
        ancho = max(ancho_tablon(t, 96) for t, _ in acciones)
        self.buttons = [CartelButton(txt, (SCREEN_W // 2, y0 + i * 52), fn, size=(ancho, 15))
                        for i, (txt, fn) in enumerate(acciones)]
        self.ultimo = victory and not hay_siguiente
        self.papelitos = [[random.uniform(0, SCREEN_W), random.uniform(-SCREEN_H // 2, SCREEN_H), random.uniform(70, 130),
                           random.uniform(0, 6.3), random.choice(PAPELITOS), random.choice(((6, 6), (9, 6), (6, 9)))]
                          for _ in range(N_PAPELITOS)] if victory else []
        musica.victoria() if victory else musica.derrota()

    def _jugar(self, idx):
        from scenes.equipo import empezar_nivel
        if LEVELS[idx].get("tutorial"):
            musica.desvanecer(400)
        self.game.change_scene(empezar_nivel(self.game, idx))

    def siguiente(self):
        self._jugar(self.level_index + 1)

    def retry(self):
        self._jugar(self.level_index)

    def to_map(self):
        from scenes.mapa import MapaScene
        self.game.change_scene(MapaScene(self.game))

    def to_menu(self):
        from scenes.menu import MenuScene
        self.game.change_scene(MenuScene(self.game))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.to_map()
            return
        for b in self.buttons:
            if b.handle_event(event):
                break

    def update(self, dt):
        self.t += dt
        for p in self.papelitos:
            p[1] += p[2] * dt
            if p[1] > SCREEN_H:
                p[1] -= SCREEN_H + 20

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        for x, y, _, fase, color, (w, h) in self.papelitos:
            xx = int(x + 6 * math.sin(self.t * 3 + fase)) // 3 * 3
            surface.fill(color, (xx, int(y) // 3 * 3, w, h))
        fondo = tablon("", 76, 56, 3)
        fr = fondo.get_rect(center=(LADO_X, 330))
        surface.blit(fondo, fr)
        if self.victory:
            draw_sprite(surface, "cartman_festejo", (LADO_X, fr.centery - 6), 1.0, self.t)
        else:
            dur = anim_duration("kenny_ratas")
            draw_sprite(surface, "kenny_ratas", (LADO_X, fr.centery - 26), 1.0, self.t % (dur + 1.2) if dur else None)
            draw_pixel_text(surface, FRASE_KENNY_EXPLOTA, (255, 240, 120), 2, outline=(30, 15, 5),
                            center=(LADO_X, fr.bottom - 34))
        surface.blit(self.panel, self.panel_rect)

        caida = max(0, int((0.35 - self.t) * 400))
        if self.victory:
            texto, color = ("¡GANASTE TODO!" if self.ultimo else "¡VICTORIA!"), COLORS["sol"]
        else:
            texto, color = "¡TE COMIERON!", COLORS["rojo"]
        draw_pixel_text(surface, texto, color, 8, outline=(30, 15, 5),
                        center=(SCREEN_W // 2, self.panel_rect.y - 10 - caida))

        cx = SCREEN_W // 2
        nombre = LEVELS[self.level_index]["nombre"]
        draw_pixel_text(surface, nombre, (255, 240, 200), 3, outline=(40, 24, 10), center=(cx, self.panel_rect.y + 50))
        if self.stats:
            draw_pixel_text(surface, f"ZOMBIES ELIMINADOS: {self.stats.get('kills', 0)}", (20, 12, 4), 2,
                            center=(cx, self.panel_rect.y + 90))
            draw_pixel_text(surface, f"TIEMPO: {int(self.stats.get('time', 0))} S", (20, 12, 4), 2,
                            center=(cx, self.panel_rect.y + 114))
        for b in self.buttons:
            b.draw(surface)
