import pygame
from settings import SCREEN_W, SCREEN_H
from scenes.base import Scene
from ui.pixel_font import draw_pixel_text, text_width

T_TOTAL = 3.6


class LoadingScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        self.cargado = False
        self.listo = False

    def _precargar(self):
        from ui import intro_art as A, musica
        A.build_background()
        A.load_kids()
        A.build_bus()
        A.build_cartel_parada()
        for w in (66, 46, 38):
            A.build_nube(w)
        musica.disponible()
        from ui import sonidos
        sonidos.precargar()
        self.cargado = True

    def handle_event(self, event):
        if self.cargado and event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            self.t = max(self.t, T_TOTAL)

    def update(self, dt):
        self.t += dt
        if not self.cargado and self.t > 0.2:
            self._precargar()
        if self.cargado and self.t >= T_TOTAL and not self.listo:
            self.listo = True
            import cuentas
            if cuentas.hay_cuentas():
                from scenes.menu import MenuScene
                self.game.change_scene(MenuScene(self.game))
            else:
                from scenes.nombre import NombreScene
                self.game.change_scene(NombreScene(self.game, "primera"))

    def draw(self, surface):
        surface.fill((0, 0, 0))
        cx = SCREEN_W // 2
        texto = "PRESENTANDO"
        n = int(max(0.0, self.t - 0.3) * 11)
        visible = texto[:n]
        draw_pixel_text(surface, visible + ("_" if int(self.t * 3) % 2 == 0 and n < len(texto) else ""),
                        (230, 230, 230), 4, midleft=(cx - text_width(texto, 4) // 2, 250))
        if n >= len(texto):
            puntos = "." * (1 + int(self.t * 3) % 3)
            draw_pixel_text(surface, puntos, (230, 230, 230), 4,
                            midleft=(cx + text_width(texto, 4) // 2 + 8, 250))
        if self.t > 1.9:
            draw_pixel_text(surface, "BIELSA GARDEN", (255, 214, 64), 8, center=(cx, 360), outline=(120, 70, 10))
            barra = pygame.Rect(0, 0, 420, 18)
            barra.center = (cx, 450)
            pygame.draw.rect(surface, (90, 90, 90), barra, 2)
            p = min(1.0, (self.t - 1.9) / (T_TOTAL - 2.1))
            pygame.draw.rect(surface, (80, 200, 90), (barra.x + 4, barra.y + 4, int((barra.w - 8) * p), barra.h - 8))
