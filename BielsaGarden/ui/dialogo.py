import os
import pygame
from settings import SCREEN_W, SCREEN_H
from ui.sprites import ASSETS_DIR
from ui.pixel_font import wrap, draw_pixel_text, ALTO
from ui import sonidos

RETRATOS = {
    "tutorial": {"img": "dialogo/bielsa1.png", "boca": (270, 250)},
    "antes":    {"img": "dialogo/bielsa2.png", "boca": (156, 214)},
    "victoria": {"img": "dialogo/bielsa_victoria.png", "boca": (216, 180)},
    "derrota":  {"img": "dialogo/bielsa_derrota.png", "boca": (192, 256)},
}
BLOQUE_PNG, BLOQUE_PANTALLA = 6, 3

PIXEL = 3
BURBUJA_W, BURBUJA_H = 192, 80
BURBUJA_X_MAX = 400
COLITA_W = 30
ESCALA_TEXTO = 3
MARGEN = (12, 10)
COLOR_TEXTO = (44, 30, 16)
BORDE = (44, 30, 16)
FONDO = (250, 243, 224)
LUZ = (255, 252, 242)
SOMBRA_INT = (222, 208, 176)
SOMBRA = (70, 48, 26)
NOMBRE_PERSONAJE = "BIELSA"

VELOCIDAD_TEXTO = 45
VELOCIDAD_ENTRADA = 1600
OSCURIDAD_FONDO = 120
SONIDO_CADA = 2

FLECHA = [
    "#######",
    "#YYYYY#",
    ".#YYY#.",
    "..#Y#..",
    "...#...",
]
REBOTE = (0, 1, 2, 1)

_cache = {}


def retrato_img(clave):
    if clave not in _cache:
        path = os.path.join(ASSETS_DIR, RETRATOS[clave]["img"])
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            f = BLOQUE_PANTALLA / BLOQUE_PNG
            _cache[clave] = pygame.transform.scale(img, (int(img.get_width() * f), int(img.get_height() * f)))
        else:
            s = pygame.Surface((300, 400), pygame.SRCALPHA)
            s.fill((140, 140, 140))
            _cache[clave] = s
    return _cache[clave]


def _rect_redondeado(w, h):
    esquina = ["...", ".", ""]
    filas = []
    for y in range(h):
        k = len(esquina[y]) if y < 3 else (len(esquina[h - 1 - y]) if y >= h - 3 else 0)
        filas.append((k, w - k))
    return filas


def burbuja_img(w, h, colita_y):
    key = ("burbuja", w, h, colita_y)
    if key in _cache:
        return _cache[key]
    W, H = COLITA_W + w + 3, max(h, colita_y + 13) + 3
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    x0 = COLITA_W
    filas = _rect_redondeado(w, h)
    for y, (a, b) in enumerate(filas):
        s.fill(BORDE, (x0 + a, y, b - a, 1))
    for y in range(2, h - 2):
        a, b = filas[y]
        a2 = max(a, 2) + (1 if y in (2, h - 3) else 0)
        b2 = min(b, w - 2) - (1 if y in (2, h - 3) else 0)
        s.fill(FONDO, (x0 + a2, y, b2 - a2, 1))
        if y == 2:
            s.fill(LUZ, (x0 + a2, y, b2 - a2, 1))
        if y == h - 3:
            s.fill(SOMBRA_INT, (x0 + a2, y, b2 - a2, 1))
        s.set_at((x0 + a2, y), LUZ)
        s.set_at((x0 + b2 - 1, y), SOMBRA_INT)
    tip_y = colita_y + 10
    for x in range(COLITA_W + 3):
        t = x / (COLITA_W + 2)
        arriba = round(tip_y + (colita_y - tip_y) * t)
        abajo = round(tip_y + (colita_y + 8 - tip_y) * t)
        for y in range(arriba - 2, abajo + 3):
            borde = y < arriba or y > abajo or x < 2
            s.set_at((x, y), BORDE if borde else FONDO)
    sombra = pygame.mask.from_surface(s).to_surface(setcolor=SOMBRA, unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface((W, H), pygame.SRCALPHA)
    out.blit(sombra, (3, 3))
    out.blit(s, (0, 0))
    _cache[key] = pygame.transform.scale(out, (W * PIXEL, H * PIXEL))
    return _cache[key]


def flecha_img():
    if "flecha" not in _cache:
        s = pygame.Surface((len(FLECHA[0]), len(FLECHA)), pygame.SRCALPHA)
        for y, fila in enumerate(FLECHA):
            for x, ch in enumerate(fila):
                if ch != ".":
                    s.set_at((x, y), BORDE if ch == "#" else (240, 196, 60))
        _cache["flecha"] = pygame.transform.scale(s, (s.get_width() * PIXEL, s.get_height() * PIXEL))
    return _cache["flecha"]


class Dialogo:
    def __init__(self, mensajes, retrato="tutorial"):
        self.mensajes = list(mensajes)
        self.retrato = retrato if retrato in RETRATOS else "tutorial"
        self.indice = 0
        self.letras = 0.0
        self.tiempo = 0.0
        self.contador_letras = 0
        self.terminado = not self.mensajes
        self.img = retrato_img(self.retrato)
        self.retrato_pos = (0, SCREEN_H - self.img.get_height())
        bx, by = RETRATOS[self.retrato]["boca"]
        boca = (self.retrato_pos[0] + bx, self.retrato_pos[1] + by)
        punta = (boca[0] + 40, boca[1])
        self.burbuja_x = min(BURBUJA_X_MAX, punta[0] + COLITA_W * PIXEL)
        colita_y = BURBUJA_H - 22
        self.burbuja_y = punta[1] - (colita_y + 10) * PIXEL
        self.burbuja_y = max(96, min(self.burbuja_y, SCREEN_H - BURBUJA_H * PIXEL - 12))
        tip_y = (punta[1] - self.burbuja_y) // PIXEL - 10
        self.img_burbuja = burbuja_img(BURBUJA_W, BURBUJA_H, max(4, min(BURBUJA_H - 12, tip_y)))
        self.offset_x = -(self.burbuja_x + BURBUJA_W * PIXEL) if VELOCIDAD_ENTRADA else 0
        self.ancho_texto = (BURBUJA_W - 2 * MARGEN[0]) * PIXEL
        self._preparar_mensaje()

    @property
    def activo(self):
        return not self.terminado

    def _preparar_mensaje(self):
        texto = self.mensajes[self.indice] if self.mensajes else ""
        self.lineas = wrap(texto, ESCALA_TEXTO, self.ancho_texto)
        self.total_letras = sum(len(l) for l in self.lineas)
        self.plano = "".join(self.lineas)
        self.letras = 0.0

    @property
    def escrito(self):
        return self.letras >= self.total_letras

    def avanzar(self):
        if not self.escrito:
            self.letras = self.total_letras
        elif self.indice + 1 < len(self.mensajes):
            self.indice += 1
            self._preparar_mensaje()
        else:
            self.terminado = True

    def manejar_evento(self, evento):
        if self.terminado:
            return
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                self.terminado = True
            else:
                self.avanzar()
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self.avanzar()

    def actualizar(self, dt):
        if self.terminado:
            return
        self.tiempo += dt
        if self.offset_x < 0:
            self.offset_x = min(0, self.offset_x + VELOCIDAD_ENTRADA * dt)
            return
        antes = int(self.letras)
        self.letras = min(self.total_letras, self.letras + VELOCIDAD_TEXTO * dt)
        suena = False
        for c in self.plano[antes:int(self.letras)]:
            if c.isalnum():
                self.contador_letras += 1
                if self.contador_letras % SONIDO_CADA == 0:
                    suena = True
        if suena:
            sonidos.reproducir("hablar")

    def dibujar(self, pantalla):
        if self.terminado:
            return
        sombra = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, OSCURIDAD_FONDO))
        pantalla.blit(sombra, (0, 0))

        ox = int(self.offset_x) // PIXEL * PIXEL
        pantalla.blit(self.img, (self.retrato_pos[0] + ox, self.retrato_pos[1]))
        bx, by = self.burbuja_x + ox, self.burbuja_y
        pantalla.blit(self.img_burbuja, (bx - COLITA_W * PIXEL, by))
        if NOMBRE_PERSONAJE:
            from ui.button import tablon
            placa = tablon(NOMBRE_PERSONAJE, 0, 14, PIXEL)
            pantalla.blit(placa, placa.get_rect(bottomleft=(bx + 8 * PIXEL, by + 4 * PIXEL)))

        x, y = bx + MARGEN[0] * PIXEL, by + MARGEN[1] * PIXEL
        restantes = int(self.letras)
        for linea in self.lineas:
            if restantes <= 0:
                break
            draw_pixel_text(pantalla, linea[:restantes], COLOR_TEXTO, ESCALA_TEXTO, topleft=(x, y))
            y += (ALTO + 4) * ESCALA_TEXTO
            restantes -= len(linea)

        if self.escrito and self.offset_x >= 0:
            f = flecha_img()
            rebote = REBOTE[int(self.tiempo * 6) % len(REBOTE)] * PIXEL
            pantalla.blit(f, (bx + (BURBUJA_W - 14) * PIXEL, by + (BURBUJA_H - 11) * PIXEL + rebote))


def entra_en_burbuja(texto):
    lineas = wrap(texto, ESCALA_TEXTO, (BURBUJA_W - 2 * MARGEN[0]) * PIXEL)
    alto = len(lineas) * (ALTO + 4) * ESCALA_TEXTO
    return alto <= (BURBUJA_H - MARGEN[1] - 14) * PIXEL and all(
        len(l) * 6 * ESCALA_TEXTO <= (BURBUJA_W - 2 * MARGEN[0]) * PIXEL + ESCALA_TEXTO for l in lineas)
