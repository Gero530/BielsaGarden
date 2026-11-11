import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import pygame
from ui.pixel_font import pixel_text, text_width

SALIDA = os.path.join(RAIZ, "assets", "mapa", "pueblo_pixel.png")
W, H = 500, 300
X2 = 2

NIEVE = (234, 240, 247)
NIEVE_SOMBRA = (214, 222, 234)
BLANCO = (250, 252, 255)
ASFALTO = (74, 76, 86)
ASFALTO_BORDE = (58, 60, 70)
LINEA = (238, 196, 60)
CEBRA = (220, 224, 230)
PINO, PINO_LUZ, PINO_OSC, TRONCO = (36, 104, 66), (58, 132, 84), (24, 74, 48), (104, 72, 46)
CONTORNO = (40, 34, 40)
VIDRIO = (255, 232, 150)
PUERTA = (92, 56, 34)

NEGOCIO_COLORES = {
    "JUEGOS": ((110, 70, 150), (70, 40, 104)), "HOTEL": ((206, 176, 120), (40, 96, 60)),
    "HELADOS": ((236, 150, 180), (196, 70, 120)), "BAR": ((150, 50, 46), (40, 30, 34)),
    "CAFE": ((150, 96, 60), (90, 54, 30)), "PIZZA": ((200, 54, 44), (140, 28, 24)),
    "LIBROS": ((60, 126, 76), (30, 80, 46)), "FARMACIA": ((230, 236, 230), (40, 150, 90)),
    "BANCO": ((130, 140, 170), (60, 70, 110)), "FLORES": ((240, 160, 190), (200, 80, 130)),
    "PAN": ((214, 150, 70), (150, 92, 36)), "CINE": ((44, 48, 80), (190, 40, 50)),
    "ROPA": ((70, 110, 190), (40, 64, 140)), "BURGER": ((220, 120, 40), (150, 60, 24)),
    "TIENDA": ((160, 160, 168), (90, 90, 104)), "MUSICA": ((130, 70, 150), (80, 36, 100)),
    "TALLER": ((70, 70, 76), (220, 180, 40)), "JOYAS": ((226, 190, 80), (150, 110, 30)),
    "DULCES": ((240, 170, 200), (210, 70, 130)), "GYM": ((236, 140, 40), (170, 80, 20)),
    "VIDEO": ((60, 150, 140), (30, 96, 90)), "ZAPATOS": ((150, 100, 60), (96, 60, 34)),
    "MASCOTAS": ((140, 200, 110), (60, 130, 60)),
}
CASA_PAREDES = [(200, 70, 60), (90, 160, 90), (90, 190, 190), (220, 190, 90), (150, 110, 80),
                (230, 140, 70), (90, 130, 210), (170, 120, 200), (236, 230, 210), (120, 160, 90)]
CASA_TECHOS = [(60, 40, 34), (40, 46, 60), (90, 40, 36), (50, 70, 50), (70, 54, 40)]

ANCHO_CALLE = 6
CALLES_H = [(66, 11, 489), (112, 11, 489), (174, 11, 489), (222, 11, 489), (284, 11, 489)]
CALLES_V = [(14, 63, 287), (160, 63, 287), (322, 63, 287), (486, 63, 287)]
CUADRAS_X = [(17, 157), (163, 319), (325, 483)]

FILA_NEGOCIOS = 82
NEGOCIOS_IZQ = (21, 154, ["JUEGOS", "HOTEL", "HELADOS", "BAR", "PAN", "CINE"])
NEGOCIOS_MEDIO = (167, 316, ["CAFE", "PIZZA", "LIBROS", "FARMACIA", "BANCO", "FLORES"])
NEGOCIOS_DER = (371, 481, ["ROPA", "BURGER", "TIENDA", "MUSICA", "TALLER"])
DRAGON = pygame.Rect(329, 78, 38, 28)
NEGOCIOS_ARRIBA_1 = (330, 392, ["JOYAS", "DULCES", "GYM"])
NEGOCIOS_ARRIBA_2 = (408, 487, ["VIDEO", "ZAPATOS", "MASCOTAS"])
FILA_ARRIBA = 40
SENDERO_X = 399

LAGO = pygame.Rect(18, 5, 102, 44)
MALL = pygame.Rect(178, 3, 127, 59)
MANSION = pygame.Rect(20, 117, 134, 52)
PARQUE = pygame.Rect(166, 117, 153, 52)
ESCUELA = pygame.Rect(24, 245, 84, 30)
CANCHA = pygame.Rect(117, 240, 36, 34)

CASAS_FILAS = [
    (150, CUADRAS_X[2], 6),
    (191, CUADRAS_X[0], 5), (191, CUADRAS_X[1], 6), (191, CUADRAS_X[2], 6),
    (245, CUADRAS_X[1], 6), (245, CUADRAS_X[2], 6),
]
CERCAS = [(141, 327, 481), (182, 19, 155), (182, 165, 317), (182, 327, 481), (233, 165, 317), (233, 327, 481)]

textos = []
ocupado = []


def rect(s, color, r):
    s.fill(color, pygame.Rect(r))


def punto(s, color, x, y):
    if 0 <= x < W and 0 <= y < H:
        s.set_at((int(x), int(y)), color)


def oscuro(c, f=0.75):
    return tuple(int(v * f) for v in c)


def claro(c, f=0.35):
    return tuple(int(v + (255 - v) * f) for v in c)


PINO_GRANDE = [
    "...N...",
    "..NoN..",
    "..oeo..",
    ".NeEeN.",
    ".oeEeo.",
    "NeeEeeN",
    "oeeEeeo",
    "ooeEeoo",
    "...t...",
]
PINO_CHICO = [
    "..N..",
    ".NoN.",
    ".oeo.",
    "NeEeN",
    "oeEeo",
    "..t..",
]
COLORES_PINO = {"N": BLANCO, "e": PINO, "E": PINO_LUZ, "o": PINO_OSC, "t": TRONCO}


def pino(s, x, y, grande=True):
    for j, fila in enumerate(PINO_GRANDE if grande else PINO_CHICO):
        for i, ch in enumerate(fila):
            if ch != ".":
                punto(s, COLORES_PINO[ch], x + i, y + j)


def calles(s):
    for y, x0, x1 in CALLES_H:
        r = pygame.Rect(x0, y - ANCHO_CALLE // 2, x1 - x0, ANCHO_CALLE)
        rect(s, ASFALTO, r)
        rect(s, ASFALTO_BORDE, (r.x, r.y, r.w, 1)); rect(s, ASFALTO_BORDE, (r.x, r.bottom - 1, r.w, 1))
        ocupado.append(r.inflate(2, 4))
    for x, y0, y1 in CALLES_V:
        r = pygame.Rect(x - ANCHO_CALLE // 2, y0, ANCHO_CALLE, y1 - y0)
        rect(s, ASFALTO, r)
        rect(s, ASFALTO_BORDE, (r.x, r.y, 1, r.h)); rect(s, ASFALTO_BORDE, (r.right - 1, r.y, 1, r.h))
        ocupado.append(r.inflate(4, 2))
    cruces_x = [x for x, _, _ in CALLES_V]
    cruces_y = [y for y, _, _ in CALLES_H]
    for y, x0, x1 in CALLES_H:
        for x in range(x0 + 2, x1 - 2, 6):
            if all(abs(x - cx) > 6 and abs(x + 2 - cx) > 6 for cx in cruces_x):
                rect(s, LINEA, (x, y - 1, 3, 1))
    for x, y0, y1 in CALLES_V:
        for y in range(y0 + 2, y1 - 2, 6):
            if all(abs(y - cy) > 6 and abs(y + 2 - cy) > 6 for cy in cruces_y):
                rect(s, LINEA, (x - 1, y, 1, 3))
    for x, y0, y1 in CALLES_V:
        for y, x0, x1 in CALLES_H:
            if y0 - 4 <= y <= y1 + 4 and x0 - 4 <= x <= x1 + 4:
                rect(s, ASFALTO, (x - 3, y - 3, 6, 6))
                for k in range(-2, 3, 2):
                    if x0 <= x - 6 and y0 <= y + k <= y1:
                        rect(s, CEBRA, (x - 6, y + k, 2, 1))
                    if x + 4 <= x1:
                        rect(s, CEBRA, (x + 4, y + k, 2, 1))


def anchos_por_nombre(x0, x1, nombres):
    minimos = [max(14, (text_width(n, 1) + 7) // X2 + 1) for n in nombres]
    sobra = (x1 - x0) - sum(minimos)
    extra = [sobra // len(nombres) + (1 if i < sobra % len(nombres) else 0) for i in range(len(nombres))]
    return [m + e for m, e in zip(minimos, extra)]


def negocio(s, x, y, w, h, nombre):
    frente, cartel = NEGOCIO_COLORES[nombre]
    r = pygame.Rect(x, y, w, h)
    rect(s, CONTORNO, r)
    rect(s, frente, r.inflate(-2, -2))
    rect(s, BLANCO, (x - 1, y - 2, w + 2, 2)); rect(s, NIEVE_SOMBRA, (x, y, w, 1))
    rect(s, cartel, (x + 1, y + 2, w - 2, 5))
    textos.append((nombre, (255, 248, 228), (x + w / 2, y + 4.5)))
    for i in range(x + 1, x + w - 1):
        punto(s, BLANCO if (i - x) % 2 else cartel, i, y + 8)
        punto(s, BLANCO if (i - x) % 2 else cartel, i, y + 9)
    rect(s, CONTORNO, (x + 2, y + 11, w - 9, h - 13))
    rect(s, VIDRIO, (x + 3, y + 12, w - 11, h - 15))
    rect(s, claro(VIDRIO, 0.5), (x + 3, y + 12, w - 11, 1))
    rect(s, CONTORNO, (x + w - 6, y + 11, 4, h - 12))
    rect(s, PUERTA, (x + w - 5, y + 12, 2, h - 13))
    ocupado.append(r.inflate(4, 6))


def fila_negocios(s, x0, x1, nombres, y, h=24):
    x = x0
    for nombre, w in zip(nombres, anchos_por_nombre(x0, x1, nombres)):
        negocio(s, x, y, w - 1, h, nombre)
        x += w


def dragon(s):
    r = DRAGON
    rojo, rojo_osc, oro, verde = (196, 40, 36), (140, 24, 24), (236, 190, 60), (40, 120, 70)
    rect(s, CONTORNO, r)
    rect(s, rojo, r.inflate(-2, -2))
    rect(s, BLANCO, (r.x - 3, r.y - 3, r.w + 6, 2))
    rect(s, verde, (r.x - 3, r.y - 1, r.w + 6, 3))
    rect(s, oscuro(verde), (r.x - 3, r.y + 1, r.w + 6, 1))
    for dx in (-4, r.w + 3):
        punto(s, verde, r.x + dx, r.y - 2); punto(s, verde, r.x + dx, r.y - 3)
    rect(s, oro, (r.x + 7, r.y + 4, r.w - 14, 6)); rect(s, CONTORNO, (r.x + 8, r.y + 5, r.w - 16, 4))
    textos.append(("DRAGON", oro, (r.centerx, r.y + 7)))
    for cx in (r.x + 3, r.right - 5):
        rect(s, rojo_osc, (cx, r.y + 4, 2, r.h - 5))
    for wx in (r.x + 6, r.right - 12):
        rect(s, oro, (wx, r.y + 13, 6, 6)); rect(s, (255, 214, 110), (wx + 1, r.y + 14, 4, 4))
        rect(s, oro, (wx + 2, r.y + 14, 1, 4)); rect(s, oro, (wx + 1, r.y + 15, 4, 1))
    rect(s, CONTORNO, (r.centerx - 3, r.y + 14, 6, r.h - 15))
    rect(s, (60, 20, 18), (r.centerx - 2, r.y + 15, 4, r.h - 16))
    for fx in (r.x - 2, r.right + 1):
        punto(s, CONTORNO, fx, r.y + 3); rect(s, (220, 50, 40), (fx - 1, r.y + 4, 3, 3)); punto(s, oro, fx, r.y + 5)
    ocupado.append(r.inflate(8, 8))


def mall(s):
    r = MALL
    rect(s, CONTORNO, (r.x, r.y, r.w, 10))
    rect(s, BLANCO, (r.x + 1, r.y + 1, r.w - 2, 8))
    for x in range(r.x + 5, r.right - 6, 9):
        rect(s, (110, 150, 200), (x, r.y + 3, 4, 3))
    f = pygame.Rect(r.x + 1, r.y + 10, r.w - 2, 25)
    rect(s, (128, 142, 164), f)
    rect(s, (150, 164, 186), (f.x, f.y, f.w, 1))
    rect(s, (226, 108, 50), (f.x, f.y + 3, f.w, 1))
    for x in range(f.x + 3, f.right - 4, 7):
        if not (r.centerx - 14 <= x <= r.centerx + 10):
            rect(s, (176, 214, 226), (x, f.y + 6, 4, 15)); rect(s, (210, 236, 244), (x, f.y + 6, 4, 2))
    e = pygame.Rect(r.centerx - 12, f.y + 4, 24, f.h - 4)
    rect(s, (60, 110, 180), e)
    for x in range(e.x + 2, e.right, 4):
        rect(s, (110, 170, 230), (x, e.y + 2, 2, e.h - 2))
    rect(s, (40, 50, 70), (e.centerx - 3, e.bottom - 6, 6, 6))
    rect(s, (232, 110, 46), (e.centerx - 9, f.y - 1, 18, 6))
    textos.append(("MALL", (255, 248, 228), (e.centerx, f.y + 2)))
    p = pygame.Rect(r.x + 1, f.bottom, r.w - 2, r.bottom - f.bottom)
    rect(s, (84, 86, 96), p)
    for x in range(p.x + 4, p.right - 2, 7):
        if abs(x - r.centerx) > 7:
            rect(s, (220, 224, 230), (x, p.y + 2, 1, 7))
    rect(s, (116, 118, 128), (r.centerx - 5, p.y, 10, p.h + 3))
    rnd = random.Random(3)
    for x in range(p.x + 6, p.right - 4, 7):
        if abs(x - r.centerx) > 9 and rnd.random() < 0.45:
            c = rnd.choice([(60, 100, 200), (200, 50, 50), (60, 150, 90), (236, 236, 236)])
            rect(s, c, (x, p.y + 3, 4, 6)); rect(s, (160, 210, 240), (x + 1, p.y + 4, 2, 2))
    ocupado.append(r.inflate(6, 4))


def lago(s):
    r = LAGO
    capas = [((156, 140, 120), 0), ((196, 222, 242), 2), ((120, 176, 222), 5), ((84, 140, 200), 10)]
    for color, borde in capas:
        q = r.inflate(-2 * borde, -2 * borde)
        pygame.draw.ellipse(s, color, q)
    pygame.draw.ellipse(s, (84, 140, 200), (r.x + 30, r.y + 12, 44, 18))
    rnd = random.Random(11)
    for _ in range(70):
        x, y = rnd.randrange(r.x + 8, r.right - 8), rnd.randrange(r.y + 6, r.bottom - 6)
        if s.get_at((x, y))[:3] in ((120, 176, 222), (84, 140, 200)):
            punto(s, (196, 222, 242), x, y)
    rect(s, (130, 92, 60), (r.x + 48, r.bottom - 3, 3, 14))
    for y in range(r.bottom - 2, r.bottom + 11, 3):
        rect(s, (96, 64, 40), (r.x + 48, y, 3, 1))
    ocupado.append(r.inflate(6, 6))
    ocupado.append(pygame.Rect(r.x + 44, r.bottom, 10, 14))


def mansion(s):
    m = MANSION
    reja, reja_osc = (150, 150, 160), (110, 110, 120)
    rect(s, reja, (m.x, m.y, m.w, 1)); rect(s, reja, (m.x, m.y, 1, m.h)); rect(s, reja, (m.right - 1, m.y, 1, m.h))
    for x in range(m.x, m.right):
        if abs(x - m.centerx) > 5:
            punto(s, reja_osc, x, m.bottom - 1)
            if x % 2 == 0:
                punto(s, reja, x, m.bottom - 2)
    for x in (m.centerx - 6, m.centerx + 5):
        rect(s, reja_osc, (x, m.bottom - 4, 2, 4))
    crema, crema_osc, techo, techo_osc = (236, 224, 192), (204, 190, 154), (96, 108, 130), (70, 80, 100)
    ventana = (244, 212, 110)

    def cuerpo(r, filas):
        rect(s, CONTORNO, r); rect(s, crema, r.inflate(-2, -2))
        rect(s, crema_osc, (r.x + 1, r.bottom - 2, r.w - 2, 1))
        for x in range(r.x + 3, r.right - 4, 6):
            for y in filas:
                rect(s, CONTORNO, (x, y, 4, 5)); rect(s, ventana, (x + 1, y + 1, 2, 3))

    def techo_plano(r):
        rect(s, BLANCO, (r.x - 2, r.y - 4, r.w + 4, 2))
        rect(s, techo, (r.x - 2, r.y - 2, r.w + 4, 2))
        rect(s, techo_osc, (r.x - 2, r.y - 1, r.w + 4, 1))

    alas = [pygame.Rect(m.x + 14, m.y + 12, 38, 23), pygame.Rect(m.right - 52, m.y + 12, 38, 23)]
    for a in alas:
        techo_plano(a)
        cuerpo(a, (a.y + 4, a.y + 12))
        rect(s, (150, 64, 54), (a.x + 5, a.y - 8, 3, 4)); rect(s, BLANCO, (a.x + 5, a.y - 9, 3, 1))
    c = pygame.Rect(m.centerx - 18, m.y + 9, 36, 26)
    cuerpo(c, (c.y + 4,))
    for k in range(9):
        rect(s, BLANCO if k < 2 else crema, (c.centerx - 2 * k - 2, c.y - 9 + k, 4 * k + 4, 1))
    rect(s, techo_osc, (c.x - 1, c.y - 1, c.w + 2, 1))
    punto(s, (230, 190, 70), c.centerx, c.y - 4); punto(s, (230, 190, 70), c.centerx - 1, c.y - 4)
    for x in range(c.x + 4, c.right - 3, 6):
        rect(s, BLANCO, (x, c.y + 11, 2, c.h - 12))
    rect(s, CONTORNO, (c.centerx - 3, c.bottom - 9, 6, 8)); rect(s, (110, 64, 40), (c.centerx - 2, c.bottom - 8, 4, 7))
    rect(s, (196, 196, 204), (c.x - 2, c.bottom, c.w + 4, 2))
    rect(s, (200, 200, 206), (m.centerx - 3, c.bottom + 2, 6, m.bottom - c.bottom - 4))
    pygame.draw.ellipse(s, (200, 200, 206), (m.centerx - 22, m.bottom - 16, 44, 12))
    pygame.draw.ellipse(s, NIEVE, (m.centerx - 16, m.bottom - 14, 32, 8))
    pygame.draw.ellipse(s, (180, 186, 196), (m.centerx - 7, m.bottom - 13, 14, 6))
    pygame.draw.ellipse(s, (120, 176, 222), (m.centerx - 5, m.bottom - 12, 10, 4))
    punto(s, BLANCO, m.centerx, m.bottom - 11)
    for hx in (m.x + 6, m.right - 30):
        for hy in (m.bottom - 14, m.bottom - 8):
            rect(s, (34, 96, 56), (hx, hy, 24, 4)); rect(s, (52, 122, 70), (hx, hy + 1, 24, 1))
            for k in range(hx + 1, hx + 24, 3):
                punto(s, BLANCO, k, hy)
    for px, py in ((m.x + 4, m.y + 3), (m.right - 11, m.y + 3)):
        pino(s, px, py, True)
    ocupado.append(m.inflate(6, 6))


def parque(s):
    p = PARQUE
    rect(s, (60, 120, 60), p)
    rect(s, (100, 168, 84), p.inflate(-2, -2))
    rnd = random.Random(5)
    for _ in range(260):
        punto(s, (116, 182, 96), rnd.randrange(p.x + 1, p.right - 1), rnd.randrange(p.y + 1, p.bottom - 1))
    c = (p.centerx, p.centery)
    tierra = (214, 196, 150)
    for dst in (p.topleft, p.topright, p.bottomleft, (p.right - 1, p.bottom - 1),
                (p.x, c[1]), (p.right - 1, c[1]), (c[0], p.y), (c[0], p.bottom - 1)):
        pygame.draw.line(s, tierra, c, dst, 2)
    rect(s, (180, 182, 186), (c[0] - 1, CALLES_H[1][0] + 3, 3, p.y - CALLES_H[1][0] - 3))
    rect(s, (180, 182, 186), (c[0] - 1, p.bottom, 3, CALLES_H[2][0] - 3 - p.bottom))
    pygame.draw.circle(s, (190, 196, 204), c, 6)
    pygame.draw.circle(s, (120, 176, 222), c, 4)
    punto(s, BLANCO, c[0], c[1] - 1)
    g = (p.right - 36, p.y + 6)
    rect(s, (200, 60, 50), (g[0] - 6, g[1], 13, 3)); rect(s, BLANCO, (g[0] - 5, g[1] - 1, 11, 1))
    for gx in (g[0] - 5, g[0] + 5):
        rect(s, BLANCO, (gx, g[1] + 3, 1, 5))
    rect(s, (230, 226, 216), (g[0] - 6, g[1] + 8, 13, 2))
    j = (p.x + 38, p.bottom - 14)
    rect(s, (236, 196, 120), (j[0] - 3, j[1] - 1, 18, 9))
    rect(s, (60, 100, 200), (j[0], j[1], 1, 6)); rect(s, (60, 100, 200), (j[0] + 5, j[1], 1, 6))
    rect(s, (60, 100, 200), (j[0], j[1], 6, 1))
    pygame.draw.line(s, (220, 60, 50), (j[0] + 8, j[1]), (j[0] + 13, j[1] + 6))
    lugares = [pygame.Rect(c[0] - 8, c[1] - 8, 16, 16), pygame.Rect(g[0] - 8, g[1] - 2, 17, 13),
               pygame.Rect(j[0] - 5, j[1] - 3, 22, 13)]
    for _ in range(400):
        x, y = rnd.randrange(p.x + 3, p.right - 5), rnd.randrange(p.y + 3, p.bottom - 5)
        r = pygame.Rect(x - 1, y - 1, 5, 5)
        if s.get_at((x + 1, y + 1))[:3] == tierra or s.get_at((x + 1, y + 3))[:3] == tierra:
            continue
        if any(r.colliderect(l) for l in lugares):
            continue
        lugares.append(r.inflate(2, 2))
        rect(s, (40, 104, 56), (x, y, 3, 3)); punto(s, (60, 130, 70), x + 1, y)
        punto(s, BLANCO, x + 1, y - 1) if rnd.random() < 0.5 else None
        punto(s, (90, 64, 40), x + 1, y + 3)
        if len(lugares) > 70:
            break
    ocupado.append(p.inflate(4, 4))


def escuela(s):
    e = ESCUELA
    ladrillo, ladrillo_osc = (176, 64, 48), (140, 48, 36)
    rect(s, CONTORNO, e); rect(s, ladrillo, e.inflate(-2, -2))
    for y in range(e.y + 3, e.bottom - 1, 3):
        rect(s, ladrillo_osc, (e.x + 1, y, e.w - 2, 1))
    rect(s, BLANCO, (e.x - 1, e.y - 2, e.w + 2, 2)); rect(s, (236, 236, 240), (e.x + 1, e.y + 1, e.w - 2, 4))
    for x in range(e.x + 4, e.right - 4, 6):
        if abs(x + 1 - e.centerx) > 8:
            rect(s, (40, 50, 80), (x, e.y + 9, 4, 4)); rect(s, (150, 190, 230), (x + 1, e.y + 10, 2, 2))
            rect(s, (40, 50, 80), (x, e.y + 16, 4, 4)); rect(s, (150, 190, 230), (x + 1, e.y + 17, 2, 2))
    t = pygame.Rect(e.centerx - 4, e.y - 12, 8, 14)
    rect(s, CONTORNO, t); rect(s, ladrillo, t.inflate(-2, -2))
    rect(s, BLANCO, (t.x - 1, t.y - 2, t.w + 2, 2))
    pygame.draw.circle(s, BLANCO, (t.centerx, t.y + 5), 2); punto(s, CONTORNO, t.centerx, t.y + 5)
    rect(s, (40, 70, 140), (e.centerx - 10, e.y + 7, 20, 4))
    textos.append(("ESCUELA", (255, 248, 228), (e.centerx, e.y + 9)))
    rect(s, CONTORNO, (e.centerx - 3, e.bottom - 9, 6, 8)); rect(s, (150, 190, 230), (e.centerx - 2, e.bottom - 8, 4, 7))
    ocupado.append(pygame.Rect(e.x - 2, t.y - 3, e.w + 4, e.bottom - t.y + 5))
    c = CANCHA
    rect(s, (196, 110, 70), c); rect(s, BLANCO, (c.x, c.y, c.w, 1)); rect(s, BLANCO, (c.x, c.bottom - 1, c.w, 1))
    rect(s, BLANCO, (c.x, c.y, 1, c.h)); rect(s, BLANCO, (c.right - 1, c.y, 1, c.h))
    rect(s, BLANCO, (c.centerx, c.y, 1, c.h))
    pygame.draw.circle(s, BLANCO, c.center, 4, 1)
    for ax in (c.x, c.right - 4):
        rect(s, BLANCO, (ax, c.centery - 4, 4, 1)); rect(s, BLANCO, (ax, c.centery + 4, 4, 1))
        rect(s, BLANCO, (ax + (3 if ax == c.x else 0), c.centery - 4, 1, 9))
    ocupado.append(c.inflate(4, 4))


def casa(s, x, y, rnd):
    pared = rnd.choice(CASA_PAREDES)
    techo = rnd.choice(CASA_TECHOS)
    rect(s, BLANCO, (x - 1, y, 17, 2))
    rect(s, techo, (x - 1, y + 2, 17, 3))
    punto(s, BLANCO, x + 2, y + 2); punto(s, BLANCO, x + 8, y + 2); punto(s, BLANCO, x + 12, y + 2)
    rect(s, CONTORNO, (x, y + 5, 15, 10)); rect(s, pared, (x + 1, y + 5, 13, 9))
    rect(s, oscuro(pared, 0.85), (x + 1, y + 5, 13, 1))
    for wx in (x + 2, x + 10):
        rect(s, VIDRIO, (wx, y + 7, 3, 3)); punto(s, claro(VIDRIO, 0.6), wx, y + 7)
    rect(s, PUERTA, (x + 6, y + 8, 3, 6))
    rect(s, (196, 198, 204), (x + 6, y + 15, 3, 2))
    ocupado.append(pygame.Rect(x - 3, y - 2, 21, 20))


def cerca(s, y, x0, x1):
    for x in range(x0, x1):
        punto(s, (150, 120, 96), x, y)
        if x % 3 == 0:
            punto(s, (120, 92, 70), x, y - 1)
    ocupado.append(pygame.Rect(x0, y - 2, x1 - x0, 4))


def sendero(s):
    rnd = random.Random(2)
    x = SENDERO_X
    for y in range(0, FILA_ARRIBA + 21):
        x += rnd.choice((0, 0, 0, 1, -1)) if y % 3 == 0 else 0
        rect(s, (150, 110, 74), (x, y, 3, 1)); punto(s, (176, 136, 96), x + 1, y)
        ocupado.append(pygame.Rect(x - 3, y, 9, 1))
    rect(s, (150, 110, 74), (x, FILA_ARRIBA + 21, 3, CALLES_H[0][0] - 3 - FILA_ARRIBA - 21))


def bosque(s, rnd):
    zonas_tupidas = [pygame.Rect(306, -4, 196, 42), pygame.Rect(-3, -4, 14, 306), pygame.Rect(490, -4, 14, 306),
                     pygame.Rect(306, 36, 24, 26), pygame.Rect(-3, 288, 506, 14)]
    puestos = []
    for zona in zonas_tupidas:
        for fila, y in enumerate(range(zona.y, zona.bottom - 4, 5)):
            for x in range(zona.x + (3 if fila % 2 else 0), zona.right - 3, 6):
                px, py = x + rnd.randrange(-1, 2), y + rnd.randrange(-1, 2)
                if not any(pygame.Rect(px + 1, py + 2, 5, 7).colliderect(o) for o in ocupado):
                    puestos.append((py, px, True))
    sueltos = []
    for _ in range(3000):
        grande = rnd.random() < 0.45
        px, py = rnd.randrange(0, W - 7), rnd.randrange(0, H - 9)
        r = pygame.Rect(px, py, 7 if grande else 5, 9 if grande else 6)
        if any(r.inflate(2, 2).colliderect(o) for o in ocupado):
            continue
        if any(abs(px - x) < 9 and abs(py - y) < 9 for y, x, _ in sueltos):
            continue
        sueltos.append((py, px, grande))
        if len(sueltos) >= 150:
            break
    for py, px, grande in sorted(puestos + sueltos):
        pino(s, px, py, grande)


def generar():
    textos.clear(); ocupado.clear()
    s = pygame.Surface((W, H))
    s.fill(NIEVE)
    rnd = random.Random(1)
    for _ in range(500):
        punto(s, NIEVE_SOMBRA, rnd.randrange(W), rnd.randrange(H))
    calles(s)
    lago(s)
    mall(s)
    sendero(s)
    fila_negocios(s, *NEGOCIOS_ARRIBA_1, FILA_ARRIBA, h=21)
    fila_negocios(s, *NEGOCIOS_ARRIBA_2, FILA_ARRIBA, h=21)
    fila_negocios(s, *NEGOCIOS_IZQ, FILA_NEGOCIOS)
    fila_negocios(s, *NEGOCIOS_MEDIO, FILA_NEGOCIOS)
    fila_negocios(s, *NEGOCIOS_DER, FILA_NEGOCIOS)
    dragon(s)
    mansion(s)
    parque(s)
    escuela(s)
    for y, x0, x1 in CERCAS:
        cerca(s, y, x0, x1)
    rnd_casas = random.Random(4)
    for y, (x0, x1), n in CASAS_FILAS:
        paso = (x1 - x0 - 15) / n
        for k in range(n):
            casa(s, round(x0 + paso * (k + 0.5)), y, rnd_casas)
    bosque(s, random.Random(9))

    grande = pygame.transform.scale(s, (W * X2, H * X2))
    for texto, color, (cx, cy) in textos:
        img = pixel_text(texto, color, 1)
        r = img.get_rect(center=(round(cx * X2), round(cy * X2)))
        if img.get_height() > 7:
            r.y -= 1
        grande.blit(img, r)
    return grande


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    pygame.image.save(generar(), SALIDA)
    print("creado:", os.path.relpath(SALIDA, RAIZ))


if __name__ == "__main__":
    main()
