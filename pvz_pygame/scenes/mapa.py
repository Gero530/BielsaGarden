"""
Mapa de niveles: Tutorial -> Nivel 1 -> Nivel 2 -> Nivel 3.

Los niveles se desbloquean de a uno (game.progreso, solo en memoria). Los ganados se
pueden volver a jugar. Fondo y posiciones de los botones: data/mapa.py.
"""
import os
import pygame
import display
from settings import SCREEN_W, SCREEN_H
from scenes.base import Scene
from levels import LEVELS
from data import mapa as M
from ui.sprites import ASSETS_DIR
from ui.button import CartelButton, tablon
from ui.pixel_font import pixel_text, text_width, draw_pixel_text
from ui import intro_art as A, musica

SALIDA = 0.5            # fundido a negro al entrar a un nivel (s)
RADIO = 10              # radio del botón de nivel en píxeles de dibujo

CANDADO = [
    "..###..",
    ".#...#.",
    ".#...#.",
    "#######",
    "###.###",
    "###.###",
    "#######",
]

# Flechita sobre el próximo nivel: # = borde, Y = amarillo (píxeles de dibujo, x ESCALA)
FLECHA = [
    "#########",
    ".#YYYYY#.",
    "..#YYY#..",
    "...#Y#...",
    "....#....",
]

_cache = {}


def flecha_img():
    if "flecha" not in _cache:
        s = pygame.Surface((len(FLECHA[0]), len(FLECHA)), pygame.SRCALPHA)
        for y, fila in enumerate(FLECHA):
            for x, ch in enumerate(fila):
                if ch != ".":
                    s.set_at((x, y), (40, 28, 14) if ch == "#" else (255, 230, 60))
        _cache["flecha"] = pygame.transform.scale(s, (s.get_width() * M.ESCALA, s.get_height() * M.ESCALA))
    return _cache["flecha"]


def fondo():
    """Tu dibujo (assets/mapa/fondo_mapa.png) o, si no está, el mapa simple de abajo."""
    if "fondo" not in _cache:
        path = os.path.join(ASSETS_DIR, M.FONDO)
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
        else:
            img = fondo_simple()
        # scale (vecino más cercano), nunca smoothscale: el pixel art queda nítido
        _cache["fondo"] = pygame.transform.scale(img, (M.ANCHO * M.ESCALA, M.ALTO * M.ESCALA))
    return _cache["fondo"]


# Lugares de South Park, uno por nivel (en píxeles del dibujo de 250x150). Ninguno toca el camino
# ni los botones de los niveles. Si dibujás tu propio mapa, ponelos en tu dibujo.
LUGARES = {
    "parada":   pygame.Rect(4, 117, 22, 29),     # Tutorial: la parada del bus
    "lago":     pygame.Rect(50, 40, 63, 26),     # Nivel 1 (El jardín): el lago Stark
    "escuela":  pygame.Rect(133, 117, 46, 30),   # Nivel 2 (La calle): la escuela
    "city_wok": pygame.Rect(193, 81, 56, 31),    # Nivel 3 (El centro): el City Wok
}


def _cartelito(s, rect, texto, color_texto, fondo=(236, 232, 220)):
    """Cartel con borde oscuro y el texto centrado (para los lugares del mapa)."""
    s.fill((30, 20, 10), rect)
    s.fill(fondo, rect.inflate(-2, -2))
    txt = pixel_text(texto, color_texto, 1)
    s.blit(txt, txt.get_rect(center=(rect.centerx, rect.centery)))


def fondo_simple():
    """Mapa placeholder en 250x150: montañas, pasto, el camino, casitas y un lugar de South Park
    al lado de cada nivel (parada del bus, lago Stark, escuela y City Wok)."""
    s = pygame.Surface((M.ANCHO, M.ALTO))
    s.fill(A.SKY)
    for cx, alto in ((20, 24), (70, 30), (125, 26), (180, 32), (235, 25)):
        A._montana(s, cx, 40, alto, A.VERDE_OSC, nieve=A.GRIS_MONTE)
    s.fill(A.VERDE, (0, 38, M.ANCHO, M.ALTO - 38))
    for i in range(0, M.ANCHO, 9):                            # manchones de nieve
        s.fill(A.NIEVE, (i * 7 % M.ANCHO, 44 + i * 13 % 100, 6, 2))
    # Camino de tierra uniendo los niveles
    pts = [n["pos"] for n in M.NIVELES]
    for a, b in zip(pts, pts[1:]):
        pygame.draw.line(s, (90, 60, 30), a, b, 9)
    for p in pts:
        pygame.draw.circle(s, (90, 60, 30), p, 4)
    for a, b in zip(pts, pts[1:]):
        pygame.draw.line(s, (196, 150, 90), a, b, 6)
    for p in pts:
        pygame.draw.circle(s, (196, 150, 90), p, 3)
    # Pinos
    for x, y in ((14, 70), (24, 84), (14, 100), (120, 60), (118, 142), (200, 138), (240, 126), (172, 52), (40, 52)):
        pygame.draw.polygon(s, (20, 40, 20), [(x, y - 11), (x - 6, y + 1), (x + 6, y + 1)])
        pygame.draw.polygon(s, (30, 110, 50), [(x, y - 9), (x - 4, y), (x + 4, y)])
        s.fill((90, 60, 30), (x - 1, y + 1, 2, 3))
    # Casitas (fuera del camino)
    for x, y, color in ((98, 116, (200, 80, 70)), (60, 128, (90, 120, 200))):
        s.fill((30, 20, 10), (x - 1, y - 1, 16, 12))
        s.fill(color, (x, y, 14, 10))
        pygame.draw.polygon(s, (30, 20, 10), [(x - 2, y), (x + 7, y - 7), (x + 16, y)])
        pygame.draw.polygon(s, (120, 60, 40), [(x, y - 1), (x + 7, y - 6), (x + 14, y - 1)])
        s.fill((80, 50, 30), (x + 5, y + 4, 4, 6))
    # Nivel 1: el lago Stark congelado, con su cartel
    lx, ly = LUGARES["lago"].topleft
    _cartelito(s, pygame.Rect(lx, ly, 63, 9), "LAGO STARK", (30, 50, 110))
    pygame.draw.ellipse(s, (255, 255, 255), (lx + 10, ly + 10, 42, 16))      # orilla nevada
    pygame.draw.ellipse(s, (170, 214, 240), (lx + 12, ly + 12, 38, 12))      # hielo
    for x, y in ((lx + 18, ly + 15), (lx + 19, ly + 16), (lx + 34, ly + 19), (lx + 35, ly + 18), (lx + 26, ly + 21)):
        s.set_at((x, y), (130, 180, 220))                                     # rajaduras del hielo
    # Nivel 2: la escuela (ladrillos, ventanas y puerta doble) con su cartel
    ex, ey = LUGARES["escuela"].topleft
    _cartelito(s, pygame.Rect(ex, ey, 46, 9), "ESCUELA", (40, 40, 40))
    s.fill((30, 20, 10), (ex + 1, ey + 9, 44, 21))
    s.fill((174, 74, 56), (ex + 2, ey + 10, 42, 19))
    for y in range(ey + 12, ey + 29, 3):                                       # filas de ladrillos
        s.fill((150, 60, 44), (ex + 2, y, 42, 1))
    for x in (ex + 5, ex + 13, ex + 29, ex + 37):                              # ventanas
        s.fill((30, 20, 10), (x - 1, ey + 13, 6, 6)); s.fill((140, 210, 230), (x, ey + 14, 4, 4))
    s.fill((30, 20, 10), (ex + 19, ey + 20, 8, 10)); s.fill((110, 60, 30), (ex + 20, ey + 21, 6, 9))
    s.fill((30, 20, 10), (ex + 23, ey + 21, 1, 9))                             # puerta doble
    # Nivel 3: el City Wok, local rojo con su cartel amarillo
    cx_, cy_ = LUGARES["city_wok"].topleft
    _cartelito(s, pygame.Rect(cx_, cy_, 56, 11), "CITY WOK", (170, 30, 20), (246, 206, 60))
    s.fill((30, 20, 10), (cx_ + 5, cy_ + 11, 46, 20)); s.fill((196, 52, 40), (cx_ + 6, cy_ + 12, 44, 18))
    s.fill((30, 20, 10), (cx_ + 11, cy_ + 16, 8, 6)); s.fill((140, 210, 230), (cx_ + 12, cy_ + 17, 6, 4))
    s.fill((30, 20, 10), (cx_ + 37, cy_ + 17, 6, 14)); s.fill((90, 40, 20), (cx_ + 38, cy_ + 18, 4, 13))
    # Tutorial: la parada del bus
    s.fill((60, 60, 66), (14, 126, 2, 20))
    s.fill((10, 40, 90), (4, 117, 22, 11)); s.fill((30, 90, 190), (5, 118, 20, 9))
    txt = pixel_text("BUS", (255, 255, 255), 1)
    s.blit(txt, txt.get_rect(center=(15, 123)))
    return s


def boton_img(etiqueta, estado, hover):
    """Botón redondo de nivel (22x22 de dibujo, agrandado x ESCALA).
    estado: "bloqueado", "disponible" o "ganado"."""
    key = (etiqueta, estado, hover)
    if key not in _cache:
        d = RADIO * 2 + 2
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        c = (d // 2, d // 2)
        relleno = {"bloqueado": (120, 120, 128), "disponible": (166, 122, 68), "ganado": (232, 190, 60)}[estado]
        pygame.draw.circle(s, (255, 230, 60) if hover else (40, 28, 14), c, RADIO + 1)
        pygame.draw.circle(s, (40, 28, 14), c, RADIO)
        pygame.draw.circle(s, relleno, c, RADIO - 1)
        pygame.draw.circle(s, tuple(min(255, v + 30) for v in relleno), (c[0] - 2, c[1] - 3), 3)
        if estado == "bloqueado":
            for y, fila in enumerate(CANDADO):
                for x, ch in enumerate(fila):
                    if ch == "#":
                        s.set_at((c[0] - 3 + x, c[1] - 3 + y), (40, 40, 48))
        else:
            txt = pixel_text(etiqueta, (20, 12, 4), 1)
            s.blit(txt, txt.get_rect(center=(c[0] + 1, c[1])))
        _cache[key] = pygame.transform.scale(s, (d * M.ESCALA, d * M.ESCALA))
    return _cache[key]


class MapaScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        self.hover = None
        self.salida = None            # (indice_nivel, tiempo) mientras se hace el fundido
        self.botones = []             # (indice_nivel, rect en pantalla, etiqueta)
        ids = [lv["id"] for lv in LEVELS]
        for n in M.NIVELES:
            if n["id"] not in ids:
                raise ValueError(f'data/mapa.py: el nivel "{n["id"]}" no existe. '
                                 f'Los ids válidos (levels/__init__.py) son: {", ".join(ids)}')
            idx = ids.index(n["id"])
            etiqueta = "T" if idx == 0 else str(idx)
            r = pygame.Rect(0, 0, (RADIO * 2 + 2) * M.ESCALA, (RADIO * 2 + 2) * M.ESCALA)
            r.center = (n["pos"][0] * M.ESCALA, n["pos"][1] * M.ESCALA)
            self.botones.append((idx, r, etiqueta))
        self.volver_btn = CartelButton("VOLVER", (96, 40), self.volver, size=(50, 14))
        if not musica.sonando():
            from scenes.menu import EMPIEZA_SIN_INTRO
            musica.reproducir(EMPIEZA_SIN_INTRO)

    # ------------------------------------------------------------------
    def desbloqueado(self, idx):
        return idx == 0 or LEVELS[idx - 1]["id"] in self.game.progreso

    def estado(self, idx):
        if LEVELS[idx]["id"] in self.game.progreso:
            return "ganado"
        return "disponible" if self.desbloqueado(idx) else "bloqueado"

    def volver(self):
        from scenes.menu import MenuScene
        self.game.change_scene(MenuScene(self.game))

    def jugar(self, idx):
        if self.salida is None:
            self.salida = (idx, 0.0)
            musica.desvanecer(int(SALIDA * 1000))

    # ------------------------------------------------------------------
    def handle_event(self, event):
        if self.salida is not None:
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.volver()
            return
        if self.volver_btn.handle_event(event):
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, r, _ in self.botones:
                if r.collidepoint(event.pos) and self.desbloqueado(idx):
                    self.jugar(idx)
                    return

    def update(self, dt):
        self.t += dt
        mouse = display.get_mouse_pos()
        self.hover = next((idx for idx, r, _ in self.botones if r.collidepoint(mouse)), None)
        if self.salida is not None:
            idx, t = self.salida
            self.salida = (idx, t + dt)
            if t + dt >= SALIDA:
                from scenes.equipo import empezar_nivel
                self.game.change_scene(empezar_nivel(self.game, idx))

    def draw(self, surface):
        surface.blit(fondo(), (0, 0))
        titulo = A.colgante_escalado("ELEGÍ UN NIVEL", 96, 16, 1, self.t, cuerda=6)
        surface.blit(titulo, titulo.get_rect(midtop=(SCREEN_W // 2, 0)))
        self.volver_btn.draw(surface)

        for idx, r, etiqueta in self.botones:
            est = self.estado(idx)
            hover = idx == self.hover
            surface.blit(boton_img(etiqueta, est, hover), r.move(0, -M.ESCALA if hover else 0))
            # Flechita que salta sobre el próximo nivel para jugar
            if est == "disponible" and int(self.t * 3) % 2 == 0:
                img = flecha_img()
                x = (r.centerx - img.get_width() // 2) // M.ESCALA * M.ESCALA
                surface.blit(img, (x, r.top - 7 * M.ESCALA))

        # Nombre del nivel bajo el mouse
        if self.hover is not None:
            idx = self.hover
            r = next(r for i, r, _ in self.botones if i == idx)
            nombre = LEVELS[idx]["nombre"] + ("" if self.desbloqueado(idx) else " (BLOQUEADO)")
            cartel = tablon(nombre, text_width(nombre, 1) + 12, 14)
            pos = cartel.get_rect(midbottom=(r.centerx, r.top - 8))
            pos.clamp_ip(surface.get_rect())
            surface.blit(cartel, pos)

        draw_pixel_text(surface, "ESC: VOLVER AL MENÚ", (255, 255, 255), 2, outline=(30, 20, 10),
                        bottomright=(SCREEN_W - 12, SCREEN_H - 10))

        if self.salida is not None:
            veil = pygame.Surface((SCREEN_W, SCREEN_H))
            veil.set_alpha(int(255 * min(1.0, self.salida[1] / SALIDA)))
            surface.blit(veil, (0, 0))
