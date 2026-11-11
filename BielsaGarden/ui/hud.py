import pygame
import display
from settings import PLANT_DATA, SCREEN_W, SCREEN_H
from entities.plants import draw_plant_icon
from ui.sprites import draw_sprite
from ui.pixel_font import draw_pixel_text, text_width
from ui.button import tablon
from data.catalogo import PERSONAJES

PX = 2
CARD_W, CARD_H = 35 * PX, 40 * PX
HUD_H = 92

BORDE = (60, 40, 24)
PAPEL = (225, 210, 160)
PAPEL_OSC = (190, 168, 112)
VENTANA = (96, 152, 60)
VENTANA_CL = (120, 178, 80)
SEL = (255, 230, 60)
TXT = (30, 20, 10)

_cache = {}


def dither(size, densidad):
    key = ("dither", size, densidad)
    if key not in _cache:
        w, h = size
        s = pygame.Surface(size, pygame.SRCALPHA)
        for y in range(0, h, PX):
            for x in range(0, w, PX):
                i, j = x // PX % 2, y // PX % 2
                tapa = {1: i == 0 and j == 0, 2: (i + j) % 2 == 0, 3: not (i == 1 and j == 1)}[densidad]
                if tapa:
                    s.fill((0, 0, 0, 255), (x, y, PX, PX))
        _cache[key] = s
    return _cache[key]


def _card_bg(selected, gris=False):
    key = ("card", selected, gris)
    if key not in _cache:
        s = pygame.Surface((35, 40))
        s.fill(SEL if selected else BORDE)
        s.fill(PAPEL if not gris else (180, 175, 170), (1, 1, 33, 38))
        win = (100, 100, 105) if gris else VENTANA
        s.fill(BORDE, (2, 2, 31, 26))
        s.fill(win, (3, 3, 29, 24))
        s.fill(VENTANA_CL if not gris else (130, 130, 135), (3, 3, 29, 2))
        s.fill(PAPEL_OSC if not gris else (150, 145, 140), (2, 29, 31, 9))
        if selected:
            s.fill(SEL, (0, 0, 35, 1)); s.fill(SEL, (0, 39, 35, 1))
            s.fill(SEL, (0, 0, 1, 40)); s.fill(SEL, (34, 0, 1, 40))
        _cache[key] = pygame.transform.scale(s, (CARD_W, CARD_H))
    return _cache[key]


class SeedCard:
    def __init__(self, key, x, y):
        self.key = key
        self.data = PLANT_DATA[key]
        self.rect = pygame.Rect(x, y, CARD_W, CARD_H)
        self.cooldown = 0.0

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
        r = self.rect.move(0, -2 * PX) if selected else self.rect
        surface.blit(_card_bg(selected), r)
        win = pygame.Rect(r.x + 3 * PX, r.y + 3 * PX, 29 * PX, 24 * PX)
        old = surface.get_clip()
        surface.set_clip(win)
        draw_plant_icon(surface, self.key, (win.centerx, win.centery + 4), 0.55)
        surface.set_clip(old)

        if self.cooldown > 0 or sun < self.cost:
            surface.blit(dither(win.size, 2), win)
        if self.cooldown > 0:
            barra = pygame.Rect(win.x + PX, win.bottom - 3 * PX, win.width - 2 * PX, 2 * PX)
            surface.fill(BORDE, barra.inflate(2 * PX, 2 * PX).clip(win))
            lleno = int(barra.width * self.cooldown / self.data["recarga"]) // PX * PX
            if lleno > 0:
                surface.fill(SEL, (barra.x, barra.y, lleno, barra.height))
        color = TXT if sun >= self.cost else (150, 30, 20)
        draw_pixel_text(surface, str(self.cost), color, PX, center=(r.centerx, r.bottom - 6 * PX))


class HUD:
    def __init__(self, plant_keys):
        self.sun_rect = pygame.Rect(8, 6, 45 * PX, 40 * PX)
        x0 = self.sun_rect.right + 8
        self.cards = [SeedCard(k, x0 + i * (CARD_W + 4), 6) for i, k in enumerate(plant_keys)]
        x_pala = x0 + len(self.cards) * (CARD_W + 4) + 10
        self.shovel_rect = pygame.Rect(x_pala, 6, CARD_W, CARD_H)
        self.speed_rect = pygame.Rect(self.shovel_rect.right + 10, 8, 32 * PX, 18 * PX)
        self.bar = pygame.Rect(SCREEN_W - 172, 22, 80 * PX, 8 * PX)
        self.barra_abajo = self.speed_rect.right + 8 > self.bar.left
        if self.barra_abajo:
            self.bar.y = SCREEN_H - 9 * PX

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

    def draw(self, surface, sun, selected, progress, level_name, flags=(), velocidad=1):
        surface.blit(tablon("", 45, 40, PX), self.sun_rect)
        c = (self.sun_rect.centerx, self.sun_rect.y + 30)
        if not draw_sprite(surface, "dedo", c, 0.55, pygame.time.get_ticks() / 1000):
            pygame.draw.circle(surface, (255, 214, 50), c, 16)
        draw_pixel_text(surface, str(sun), (255, 240, 200), 3, outline=(40, 24, 10),
                        center=(self.sun_rect.centerx, self.sun_rect.bottom - 16))
        etiqueta = _etiqueta_cheesy()
        surface.blit(etiqueta, etiqueta.get_rect(midtop=(self.sun_rect.centerx, self.sun_rect.bottom - 2 * PX)))

        for card in self.cards:
            card.draw(surface, sun, selected == card.key)

        surface.blit(_card_bg(selected == "pala", gris=True), self.shovel_rect)
        draw_shovel(surface, (self.shovel_rect.centerx - 2, self.shovel_rect.y + 26))
        draw_pixel_text(surface, "PALA", TXT, PX, center=(self.shovel_rect.centerx, self.shovel_rect.bottom - 6 * PX))

        self.draw_speed(surface, velocidad)

        card = self.card_at(display.get_mouse_pos())
        if card:
            nombre = PERSONAJES.get(card.key, {}).get("nombre", card.key)
            draw_pixel_text(surface, f"{nombre} ({card.cost})", (255, 255, 255), PX,
                            outline=(30, 20, 10), midtop=(card.rect.centerx, card.rect.bottom + 4))

        self.draw_progress(surface, progress, level_name, flags)

    def draw_speed(self, surface, velocidad):
        hover = self.speed_rect.collidepoint(display.get_mouse_pos())
        surface.blit(tablon("", 32, 18, PX, hover=hover), self.speed_rect)
        color = (255, 240, 200) if velocidad == 1 else SEL
        icono = _avance_img(color)
        texto = f"X{velocidad}"
        total = icono.get_width() + 2 * PX + text_width(texto, PX)
        x = self.speed_rect.centerx - total // 2 // PX * PX
        cy = self.speed_rect.centery + PX
        surface.blit(icono, icono.get_rect(midleft=(x, cy)))
        draw_pixel_text(surface, texto, color, PX, outline=(40, 24, 10),
                        midleft=(x + icono.get_width() + 2 * PX, cy))
        if hover:
            draw_pixel_text(surface, "VELOCIDAD (F)", (255, 255, 255), PX, outline=(30, 20, 10),
                            midtop=(self.speed_rect.centerx, 90))

    def draw_progress(self, surface, progress, level_name, flags):
        bar = self.bar
        if self.barra_abajo:
            draw_pixel_text(surface, level_name, (255, 255, 255), PX, outline=(30, 20, 10),
                            midright=(bar.left - 8, bar.centery))
        else:
            draw_pixel_text(surface, level_name, (255, 255, 255), PX, outline=(30, 20, 10),
                            topright=(bar.right, bar.bottom + 8))
        surface.fill(BORDE, bar)
        inner = bar.inflate(-2 * PX, -2 * PX)
        surface.fill((50, 35, 20), inner)
        w = int(inner.width * progress) // PX * PX
        if w:
            surface.fill((90, 200, 70), (inner.right - w, inner.y, w, inner.height))
            surface.fill((140, 230, 110), (inner.right - w, inner.y, w, PX))
        for f in flags:
            x = inner.right - int(inner.width * f) // PX * PX
            up = progress >= f
            top = bar.y - ((8 if up else 4) if not self.barra_abajo else 1) * PX
            surface.fill((40, 30, 20), (x, top, PX, bar.bottom - top))
            surface.fill((220, 40, 40) if up else (150, 60, 60), (x + PX, top, 4 * PX, 3 * PX))
        hx = inner.right - w
        head = pygame.Rect(0, 0, 7 * PX, 7 * PX)
        head.center = (hx, bar.centery)
        surface.fill((20, 20, 20), head)
        surface.fill((150, 180, 130), head.inflate(-2 * PX, -2 * PX))
        surface.fill((255, 255, 255), (head.x + 2 * PX, head.y + 2 * PX, PX, PX))
        surface.fill((255, 255, 255), (head.x + 4 * PX, head.y + 2 * PX, PX, PX))
        surface.fill((150, 20, 20), (head.x + 2 * PX, head.y + 4 * PX, 3 * PX, PX))


PALA = [
    "..........HH",
    ".........HHH",
    "........HH..",
    ".......HH...",
    "......HH....",
    ".....HH.....",
    "..MMMH......",
    ".MMMMM......",
    "MMMMMM......",
    "MMMMM.......",
    "MMMM........",
    ".MM.........",
]


def _pala_img(p):
    key = ("pala", p)
    if key not in _cache:
        colores = {"H": (130, 86, 42), "M": (200, 200, 210)}
        n = len(PALA)
        s = pygame.Surface((n + 2, n + 2), pygame.SRCALPHA)
        for y, fila in enumerate(PALA):
            for x, ch in enumerate(fila):
                if ch != ".":
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            if s.get_at((x + 1 + dx, y + 1 + dy)).a == 0:
                                s.set_at((x + 1 + dx, y + 1 + dy), (40, 30, 30))
        for y, fila in enumerate(PALA):
            for x, ch in enumerate(fila):
                if ch != ".":
                    s.set_at((x + 1, y + 1), colores[ch])
        _cache[key] = pygame.transform.scale(s, ((n + 2) * p, (n + 2) * p))
    return _cache[key]


AVANCE_RAPIDO = [
    "OO..OO..",
    "O#O.O#O.",
    "O##OO##O",
    "O#O.O#O.",
    "OO..OO..",
]


def _avance_img(color):
    key = ("avance", color)
    if key not in _cache:
        s = pygame.Surface((len(AVANCE_RAPIDO[0]), len(AVANCE_RAPIDO)), pygame.SRCALPHA)
        for y, fila in enumerate(AVANCE_RAPIDO):
            for x, ch in enumerate(fila):
                if ch != ".":
                    s.set_at((x, y), (40, 24, 10) if ch == "O" else color)
        _cache[key] = pygame.transform.scale(s, (s.get_width() * PX, s.get_height() * PX))
    return _cache[key]


MICRO = {
    "C": ["###", "#..", "#..", "#..", "###"], "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "E": ["###", "#..", "##.", "#..", "###"], "S": ["###", "#..", "###", "..#", "###"],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."], "P": ["##.", "#.#", "##.", "#..", "#.."],
    "O": ["###", "#.#", "#.#", "#.#", "###"], "F": ["###", "#..", "##.", "#..", "#.."],
    " ": ["...", "...", "...", "...", "..."],
}


def _etiqueta_cheesy():
    if "cheesy" not in _cache:
        texto = "CHEESY POOFS"
        w, h = len(texto) * 4 + 3, 9
        s = pygame.Surface((w, h + 2), pygame.SRCALPHA)
        s.fill((40, 24, 10), (w // 4, 0, 1, 2)); s.fill((40, 24, 10), (w * 3 // 4, 0, 1, 2))
        s.fill((40, 24, 10), (0, 2, w, h))
        s.fill((246, 146, 34), (1, 3, w - 2, h - 2))
        s.fill((255, 204, 64), (1, 3, w - 2, 1))
        for i, ch in enumerate(texto):
            for y, fila in enumerate(MICRO[ch]):
                for x, c in enumerate(fila):
                    if c == "#":
                        s.set_at((2 + i * 4 + x, 4 + y), (30, 40, 120))
        _cache["cheesy"] = pygame.transform.scale(s, (s.get_width() * PX, s.get_height() * PX))
    return _cache["cheesy"]


def draw_shovel(surface, center, scale=1.0):
    img = _pala_img(max(1, round(PX * scale)))
    surface.blit(img, img.get_rect(center=(int(center[0]), int(center[1]))))
