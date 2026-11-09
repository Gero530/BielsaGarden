"""
Mapa de niveles: Tutorial -> Nivel 1 -> Nivel 2 -> Nivel 3.

Los niveles se desbloquean de a uno (game.progreso, de la cuenta activa). Los ganados se
pueden volver a jugar. Qué mapa se usa, su fondo y dónde va cada botón: data/mapa.py.
"""
import os
import pygame
import display
from settings import SCREEN_W, SCREEN_H
from scenes.base import Scene
from levels import LEVELS
from data import mapa as M
from ui.sprites import ASSETS_DIR
from ui.button import tablon
from ui import button
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

# Botón de volver: tablón chico con una flecha tallada hacia la izquierda (píxeles de dibujo, x3)
VOLVER_W, VOLVER_H, VOLVER_ESC = 18, 14, 3
FLECHA_VOLVER = [
    "...#.......",
    "..##.......",
    ".##########",
    "###########",
    ".##########",
    "..##.......",
    "...#.......",
]


def volver_img(estado):
    key = ("volver", estado)
    if key not in _cache:
        s = A.build_cartel("", VOLVER_W, VOLVER_H, 1, estado=estado).copy()
        top = {"normal": 1, "hover": 0, "apretado": 2}[estado]
        x0 = (VOLVER_W - len(FLECHA_VOLVER[0])) // 2
        y0 = top + (VOLVER_H - 2 - len(FLECHA_VOLVER)) // 2
        for capa, color, dy in ((1, (236, 200, 140), 1), (0, (40, 22, 6), 0)):   # luz tallada abajo y la flecha
            for y, fila in enumerate(FLECHA_VOLVER):
                for x, ch in enumerate(fila):
                    if ch == "#":
                        s.set_at((x0 + x, y0 + y + dy), color)
        _cache[key] = pygame.transform.scale(s, (VOLVER_W * VOLVER_ESC, VOLVER_H * VOLVER_ESC))
    return _cache[key]


def flecha_img():
    if "flecha" not in _cache:
        s = pygame.Surface((len(FLECHA[0]), len(FLECHA)), pygame.SRCALPHA)
        for y, fila in enumerate(FLECHA):
            for x, ch in enumerate(fila):
                if ch != ".":
                    s.set_at((x, y), (40, 28, 14) if ch == "#" else (255, 230, 60))
        _cache["flecha"] = pygame.transform.scale(s, (s.get_width() * M.ESCALA, s.get_height() * M.ESCALA))
    return _cache["flecha"]


def mapa_elegido():
    """(config, imagen) del mapa de data/mapa.py. Si falta su PNG se usa el "original", y si
    tampoco está, el mapa simple dibujado por código (con los botones del original)."""
    for nombre in (M.MAPA, "original"):
        cfg = M.MAPAS[nombre]
        path = os.path.join(ASSETS_DIR, cfg["fondo"])
        if os.path.exists(path):
            return cfg, pygame.image.load(path).convert()
    return M.MAPAS["original"], fondo_simple()


def _armar_fondo():
    """El dibujo agrandado/achicado para que entre ENTERO en 1000x600 sin deformarse, centrado,
    con franjas del color de relleno si sobra lugar. Guarda la escala y el corrimiento para
    pasar las posiciones de los botones (píxeles del dibujo) a la pantalla."""
    cfg, img = mapa_elegido()
    w, h = img.get_size()
    k = min(SCREEN_W / w, SCREEN_H / h)
    tam = (round(w * k), round(h * k))
    if k == int(k):
        img = pygame.transform.scale(img, tam)          # pixel art agrandado x entero: nítido
    else:
        img = pygame.transform.smoothscale(img, tam)    # ilustración achicada: suave, sin perder líneas
    pantalla = pygame.Surface((SCREEN_W, SCREEN_H))
    pantalla.fill(cfg["relleno"])
    off = ((SCREEN_W - tam[0]) // 2, (SCREEN_H - tam[1]) // 2)
    pantalla.blit(img, off)
    _cache["fondo"] = pantalla
    _cache["mapa"] = (cfg, k, off)


def fondo():
    if "fondo" not in _cache:
        _armar_fondo()
    return _cache["fondo"]


def niveles_en_pantalla():
    """[(id, (x, y) en pantalla)] de los botones del mapa elegido."""
    if "mapa" not in _cache:
        _armar_fondo()
    cfg, k, (ox, oy) = _cache["mapa"]
    return [(n["id"], (round(ox + n["pos"][0] * k), round(oy + n["pos"][1] * k))) for n in cfg["niveles"]]


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
    pts = [n["pos"] for n in M.MAPAS["original"]["niveles"]]
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
        for nid, centro in niveles_en_pantalla():
            if nid not in ids:
                raise ValueError(f'data/mapa.py: el nivel "{nid}" no existe. '
                                 f'Los ids válidos (levels/__init__.py) son: {", ".join(ids)}')
            idx = ids.index(nid)
            etiqueta = "T" if idx == 0 else str(idx)
            r = pygame.Rect(0, 0, (RADIO * 2 + 2) * M.ESCALA, (RADIO * 2 + 2) * M.ESCALA)
            r.center = centro
            self.botones.append((idx, r, etiqueta))
        self.volver_rect = pygame.Rect(12, 12, VOLVER_W * VOLVER_ESC, VOLVER_H * VOLVER_ESC)
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
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.volver_rect.collidepoint(event.pos):
            if not button.ocupado():
                button.apretar(self.volver_rect, VOLVER_ESC, self.volver, "mapa_volver")
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
        if button.apretado("mapa_volver"):
            estado = "apretado"
        elif self.volver_rect.collidepoint(display.get_mouse_pos()):
            estado = "hover"
        else:
            estado = "normal"
        surface.blit(volver_img(estado), self.volver_rect.move(-VOLVER_ESC * 2 if estado == "hover" else 0, 0))

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
            # Cartelito chico al costado del nivel (a la derecha, o a la izquierda si no entra)
            cartel = tablon(nombre, 0, 14, 2)
            pos = cartel.get_rect(midleft=(r.right + 6, r.centery))
            if pos.right > SCREEN_W - 8:
                pos.midright = (r.left - 6, r.centery)
            pos.clamp_ip(surface.get_rect())
            surface.blit(cartel, pos)


        if self.salida is not None:
            veil = pygame.Surface((SCREEN_W, SCREEN_H))
            veil.set_alpha(int(255 * min(1.0, self.salida[1] / SALIDA)))
            surface.blit(veil, (0, 0))
