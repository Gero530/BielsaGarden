import math
import random
import pygame
from settings import SCREEN_W, SCREEN_H, COLORS
from scenes.base import Scene
from data.catalogo import PERSONAJES
from entities.plants import draw_plant_icon
from ui import intro_art as A, musica
from ui.button import CartelButton, ancho_tablon
from ui.pixel_font import draw_pixel_text
from ui.sprites import draw_sprite, has_sprite

PAPELITOS = ((220, 40, 40), (255, 214, 64), (60, 110, 220), (60, 190, 80), (255, 255, 255), (246, 146, 34))
ELENCO = [("girasol", "cartman_festejo", None), ("lanzaguisantes", "lanzaguisantes", None), ("nuez", "nuez", None),
          ("kyle", "kyle", None), ("kenny", "kenny", 0), ("toallin", "toallin", None), ("iman", "iman", None),
          ("picante", "picante", 0), ("aplastadora", "aplastadora", None)]
PISO = 488
SALTO = 18
FRASE = '"Lo logramos. Y no fue suerte: fue trabajo, orden y sacrificio." - Bielsa'


class FinalScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        musica.final()
        acciones = [("VOLVER AL MAPA", self.to_map), ("MENÚ PRINCIPAL", self.to_menu)]
        ancho = max(ancho_tablon(t, 80) for t, _ in acciones)
        self.buttons = [CartelButton(txt, (SCREEN_W // 2 + (i * 2 - 1) * 180, SCREEN_H - 38), fn, size=(ancho, 15))
                        for i, (txt, fn) in enumerate(acciones)]
        self.papelitos = [[random.uniform(0, SCREEN_W), random.uniform(-SCREEN_H, SCREEN_H), random.uniform(60, 120),
                           random.uniform(0, 6.3), random.choice(PAPELITOS), random.choice(((6, 6), (9, 6), (6, 9)))]
                          for _ in range(90)]
        self._lienzo = pygame.Surface((180, 180), pygame.SRCALPHA)

    def to_map(self):
        from scenes.mapa import MapaScene
        self.game.change_scene(MapaScene(self.game))

    def to_menu(self):
        from scenes.menu import MenuScene
        self.game.change_scene(MenuScene(self.game))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.to_menu()
            return
        for b in self.buttons:
            if b.handle_event(event):
                return

    def update(self, dt):
        self.t += dt
        for p in self.papelitos:
            p[1] += p[2] * dt
            if p[1] > SCREEN_H:
                p[1] -= SCREEN_H + 20

    def _personaje(self, clave, sprite, frame, t):
        lienzo = self._lienzo
        lienzo.fill((0, 0, 0, 0))
        if has_sprite(sprite):
            draw_sprite(lienzo, sprite, (90, 90), 1.0, None if frame is not None else t, frame=frame)
        else:
            draw_plant_icon(lienzo, clave, (90, 90), 1.0)
        caja = lienzo.get_bounding_rect()
        return lienzo.subsurface(caja) if caja.w else None

    def draw(self, surface):
        surface.blit(A.fondo_vivo(self.t, bus=False), (0, 0))
        for x, y, _, fase, color, (w, h) in self.papelitos:
            xx = int(x + 6 * math.sin(self.t * 3 + fase)) // 3 * 3
            surface.fill(color, (xx, int(y) // 3 * 3, w, h))

        caida = max(0, int((0.5 - self.t) * 500))
        titulo = A.colgante_escalado("¡FELICIDADES!", 0, 22, 2, self.t, cuerda=10)
        surface.blit(titulo, titulo.get_rect(midtop=(SCREEN_W // 2, -caida)))
        if self.t > 0.5:
            sacude = 3 if int(self.t * 8) % 2 and self.t < 1.0 else 0
            draw_pixel_text(surface, "JUEGO COMPLETADO", COLORS["sol"], 6, outline=(30, 15, 5),
                            center=(SCREEN_W // 2 + sacude, 200))
            draw_pixel_text(surface, FRASE, (255, 255, 255), 2, outline=(30, 40, 70), center=(SCREEN_W // 2, 246))

        n = len(ELENCO)
        paso = (SCREEN_W - 120) / (n - 1)
        for i, (clave, sprite, frame) in enumerate(ELENCO):
            img = self._personaje(clave, sprite, frame, self.t + i * 0.2)
            if img is None:
                continue
            x = round(60 + i * paso)
            fase = (self.t / A.PULSO - i * 0.18) % 2.0
            salto = int(SALTO * max(0.0, math.sin(math.pi * min(1.0, fase))))
            pygame.draw.ellipse(surface, (150, 160, 176), (x - 24, PISO - 5, 48, 10))
            surface.blit(img, img.get_rect(midbottom=(x, PISO - salto)))
            draw_pixel_text(surface, PERSONAJES[clave]["nombre"].split()[-1].upper(), (255, 255, 255), 2,
                            outline=(30, 40, 70), midtop=(x, PISO + 8))

        for b in self.buttons:
            b.draw(surface)
