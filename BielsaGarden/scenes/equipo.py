import pygame
import display
from settings import SCREEN_W, SCREEN_H, PLANT_DATA, EQUIPO_MAX
from scenes.base import Scene
from levels import LEVELS
from data.catalogo import PERSONAJES
from entities.zombies import ZOMBIE_CLASSES
from world.grid import Grid
from ui.hud import SeedCard, CARD_W, CARD_H, dither
from ui.button import CartelButton, tablon
from ui.pixel_font import draw_pixel_text
from scenes.catalogo import draw_tooltip, stats_planta
from ui import intro_art as A, musica
from ui.sprites import SPRITES, has_sprite
from ui import sonidos

POR_FILA = 5
ZANCHO = 540
ZY = 206
ZALTO_MAX = 310
ZSEP = 8
ESCALAS = (1.0, 0.875, 0.75, 0.625, 0.5)
_cache = {}


def hueco_carta():
    if "hueco" not in _cache:
        s = A.build_cartel("", 35, 40, 1).copy()
        s.fill((76, 48, 22), (4, 4, 27, 31))
        s.fill((52, 32, 14), (4, 4, 27, 1)); s.fill((52, 32, 14), (4, 4, 1, 31))
        s.fill((164, 116, 60), (4, 34, 27, 1)); s.fill((164, 116, 60), (30, 4, 1, 31))
        cx, cy = 17, 19
        for dx, dy, color in ((1, 1, (52, 32, 14)), (0, 0, (196, 150, 86))):
            s.fill(color, (cx - 3 + dx, cy + dy, 7, 1)); s.fill(color, (cx + dx, cy - 3 + dy, 1, 7))
        _cache["hueco"] = pygame.transform.scale(s, (CARD_W, CARD_H))
    return _cache["hueco"]


def tilde_img():
    if "tilde" not in _cache:
        from ui.widgets import TILDE
        w, h = len(TILDE[0]) + 2, len(TILDE) + 2
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        for capa, color in ((1, (40, 24, 10)), (0, (255, 214, 64))):
            for y, fila in enumerate(TILDE):
                for x, c in enumerate(fila):
                    if c == "#":
                        if capa:
                            for dx in (-1, 0, 1):
                                for dy in (-1, 0, 1):
                                    s.set_at((x + 1 + dx, y + 1 + dy), color)
                        else:
                            s.set_at((x + 1, y + 1), color)
        _cache["tilde"] = pygame.transform.scale(s, (w * 2, h * 2))
    return _cache["tilde"]


def icono_zombie(z):
    lienzo = pygame.Surface((300, 240), pygame.SRCALPHA)
    z.draw_icon(lienzo, (150, 236))
    caja = lienzo.get_bounding_rect()
    return lienzo.subsurface(caja).copy() if caja.w and caja.h else None


def acomodar_zombies(imagenes, ancho_max, alto_max):
    filas = []
    for k in ESCALAS:
        imgs = [im if k == 1 else pygame.transform.scale(
            im, (max(1, round(im.get_width() * k)), max(1, round(im.get_height() * k)))) for im in imagenes]
        filas, fila, usado = [], [], 0
        for im in imgs:
            if fila and usado + im.get_width() > ancho_max:
                filas.append(fila); fila, usado = [], 0
            fila.append(im); usado += im.get_width() + ZSEP
        if fila:
            filas.append(fila)
        filas = [(f, max(im.get_height() for im in f)) for f in filas]
        if sum(h for _, h in filas) + ZSEP * (len(filas) - 1) <= alto_max:
            break
    return filas


def empezar_nivel(game, idx):
    if LEVELS[idx].get("tutorial"):
        from scenes.gameplay import GameplayScene
        return GameplayScene(game, idx)
    return EquipoScene(game, idx)


def zombies_del_nivel(level):
    from world.wave_manager import tipos_de_oleada
    vistos = []
    for w in level["oleadas"]:
        for k in tipos_de_oleada(w):
            if k not in vistos:
                vistos.append(k)
    return vistos


class EquipoScene(Scene):
    def __init__(self, game, level_index):
        super().__init__(game)
        self.idx = level_index
        self.level = LEVELS[level_index]
        self.pool = self.level.get("plantas") or list(PLANT_DATA)
        self.max = min(EQUIPO_MAX, len(self.pool))
        self.equipo = [k for k in getattr(game, "equipo", []) if k in self.pool][:self.max]

        self.t = 0.0

        filas = -(-len(self.pool) // POR_FILA)
        self.panel = tablon("", 136, (44 + filas * (CARD_H + 10) + 12) // 3, 3)
        self.panel_rect = self.panel.get_rect(topleft=(24, 196))
        self.cartas = []
        for i, k in enumerate(self.pool):
            fila, col = divmod(i, POR_FILA)
            x = self.panel_rect.x + 26 + col * (CARD_W + 8)
            y = self.panel_rect.y + 44 + fila * (CARD_H + 10)
            self.cartas.append(SeedCard(k, x, y))
        x0 = SCREEN_W // 2 - (self.max * (CARD_W + 6) - 6) // 2
        self.lugares = [pygame.Rect(x0 + i * (CARD_W + 6), 96, CARD_W, CARD_H) for i in range(self.max)]

        grid = Grid()
        self.zombies = [ZOMBIE_CLASSES[k](0, grid) for k in zombies_del_nivel(self.level)]
        imagenes = [im for im in (icono_zombie(z) for z in self.zombies) if im is not None]
        self.zfilas = acomodar_zombies(imagenes, ZANCHO - 40, ZALTO_MAX - 40 - 18)
        alto = 40 + sum(h for _, h in self.zfilas) + ZSEP * (len(self.zfilas) - 1) + 18
        self.zpanel = tablon("", ZANCHO // 3, (alto + 2) // 3, 3)
        self.zpanel_rect = self.zpanel.get_rect(topright=(SCREEN_W - 12, ZY))

        self.jugar_btn = CartelButton("¡A JUGAR!", (560, 548), self.jugar, size=(70, 15))
        self.volver_btn = CartelButton("VOLVER", (self.panel_rect.x + 106, 548), self.volver, size=(70, 15))
        self.aviso = 0.0

        if not musica.sonando():
            from scenes.menu import EMPIEZA_SIN_INTRO
            musica.reproducir(EMPIEZA_SIN_INTRO)

    def jugar(self):
        if not self.equipo:
            self.aviso = 1.5
            return
        self.game.equipo = list(self.equipo)
        musica.desvanecer(500)
        from scenes.gameplay import GameplayScene
        self.game.change_scene(GameplayScene(self.game, self.idx, plantas=list(self.equipo)))

    def volver(self):
        from scenes.mapa import MapaScene
        self.game.change_scene(MapaScene(self.game))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.volver()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.jugar()
            return
        if self.jugar_btn.handle_event(event) or self.volver_btn.handle_event(event):
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        for i, r in enumerate(self.lugares):
            if r.collidepoint(event.pos) and i < len(self.equipo):
                self.equipo.pop(i)
                sonidos.reproducir("seleccionar")
                return
        for c in self.cartas:
            if c.rect.collidepoint(event.pos) and c.key not in self.equipo and len(self.equipo) < self.max:
                self.equipo.append(c.key)
                sonidos.reproducir("seleccionar")
                return

    def update(self, dt):
        self.t += dt
        self.aviso = max(0.0, self.aviso - dt)
        self.jugar_btn.enabled = bool(self.equipo)

    def draw(self, surface):
        surface.blit(A.fondo_vivo(self.t), (0, 0))
        titulo = tablon("ELEGÍ TU EQUIPO", 100, 18, 3, 1)
        surface.blit(titulo, titulo.get_rect(center=(SCREEN_W // 2, 42)))
        draw_pixel_text(surface, self.level["nombre"], (255, 240, 200), 2, outline=(30, 20, 10),
                        center=(SCREEN_W // 2, 78))

        for i, r in enumerate(self.lugares):
            if i < len(self.equipo):
                SeedCard(self.equipo[i], r.x, r.y).draw(surface, 9999, False)
            else:
                surface.blit(hueco_carta(), r)
        if self.aviso > 0:
            draw_pixel_text(surface, "ELEGÍ AL MENOS UN PERSONAJE", (255, 90, 60), 2, outline=(30, 10, 10),
                            midtop=(SCREEN_W // 2, self.lugares[0].bottom + 8))

        surface.blit(self.panel, self.panel_rect)
        draw_pixel_text(surface, "PERSONAJES", (255, 240, 200), 2, outline=(40, 24, 10),
                        midtop=(self.panel_rect.centerx, self.panel_rect.y + 16))
        for c in self.cartas:
            c.draw(surface, 9999, False)
            if c.key in self.equipo:
                surface.blit(dither(c.rect.size, 2), c.rect)
                tilde = tilde_img()
                surface.blit(tilde, tilde.get_rect(topright=(c.rect.right - 4, c.rect.y + 4)))

        surface.blit(self.zpanel, self.zpanel_rect)
        draw_pixel_text(surface, "VIENEN", (255, 240, 200), 2, outline=(40, 24, 10),
                        midtop=(self.zpanel_rect.centerx, self.zpanel_rect.y + 16))
        y = self.zpanel_rect.y + 40
        for fila, alto in self.zfilas:
            x = self.zpanel_rect.centerx - (sum(im.get_width() for im in fila) + ZSEP * (len(fila) - 1)) // 2
            for im in fila:
                surface.blit(im, im.get_rect(bottomleft=(x, y + alto)))
                x += im.get_width() + ZSEP
            y += alto + ZSEP

        self.jugar_btn.draw(surface)
        self.volver_btn.draw(surface)

        mouse = display.get_mouse_pos()
        hover = next(((c.key, c.rect) for c in self.cartas if c.rect.collidepoint(mouse)), None)
        if hover is None:
            hover = next(((self.equipo[i], r) for i, r in enumerate(self.lugares)
                          if r.collidepoint(mouse) and i < len(self.equipo)), None)
        if hover:
            key, rect = hover
            info = PERSONAJES.get(key, {"nombre": key, "descripcion": ""})
            draw_tooltip(surface, info, stats_planta(key), rect)
