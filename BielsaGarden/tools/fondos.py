"""
Fondos de cada nivel, hechos a partir de assets/fondos/A_vereda.png (250x150, el juego lo ve x4).
Sin edificios ni estructuras: cada nivel cambia la época y la hora (lo de detrás de la cerca), los
detalles del pasto y lo que hay tirado en las veredas. Todo dibujado a mano como mapas de píxeles
(cada letra es un color de PAL). La cuadrícula del pasto (x 45..224, y 25..144) queda donde está.
  Tutorial: invierno     Nivel 1: día de sol     Nivel 2: otoño     Nivel 3: atardecer
La cerca de abajo es una cerquita baja en y 145..149, debajo de los pies de la última fila.

También guarda piezas que usa tools/mapa.py (montaña, pino, cartel del bus, banco, edificios...).

    python tools/fondos.py            # crea los que faltan en assets/fondos/
    python tools/fondos.py --forzar   # los vuelve a crear (¡pisa tus retoques!)
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import pygame

FONDOS = os.path.join(RAIZ, "assets", "fondos")
W, H = 250, 150
PASTO_X0, PASTO_X1 = 45, 225      # el pasto va de x 45 a 224
CERCA_Y0, PASTO_Y0 = 15, 25       # la cerca de arriba ocupa y 15..24

# Paleta: los colores del jardín + los nuevos de cada nivel
PAL = {
    "o": (94, 70, 48),                                       # contorno marrón (el del jardín)
    "O": (60, 44, 32),                                       # contorno más oscuro
    "A": (217, 201, 163), "a": (184, 165, 126), "b": (200, 184, 146),   # tablas beige
    "W": (240, 234, 214), "w": (206, 198, 176),              # marco blanco
    "G": (125, 192, 236), "g": (90, 148, 200), "L": (206, 234, 250),   # vidrio
    "c": (200, 90, 80), "C": (160, 64, 60),                  # cortina / flor roja
    "D": (176, 112, 70), "d": (138, 86, 54),                 # madera de puerta
    "Y": (232, 197, 71), "y": (190, 150, 40),                # amarillo (picaporte, cartel)
    "R": (174, 74, 56), "r": (146, 58, 44), "M": (196, 170, 150),       # ladrillo rojo y junta
    "T": (169, 71, 58), "t": (126, 50, 41), "U": (201, 97, 79),         # tejas del jardín
    "S": (181, 178, 168), "s": (154, 151, 142), "Z": (236, 236, 236),   # vereda / pintura blanca
    "K": (90, 90, 96), "k": (72, 72, 78),                    # asfalto
    "N": (244, 248, 252), "n": (206, 222, 236),              # nieve
    "P": (140, 160, 184), "p": (112, 132, 158),              # montaña lejana
    "E": (44, 104, 62), "e": (30, 76, 46),                   # pino / arbusto
    "m": (120, 84, 56),                                      # tierra del cantero
    "h": (150, 156, 160), "H": (110, 114, 120),              # alambre / metal
    "I": (52, 52, 60), "i": (96, 96, 108),                   # hierro
    "Q": (196, 52, 40), "q": (148, 34, 28),                  # rojo del restaurante
    "B": (60, 110, 200), "x": (36, 70, 150),                 # azul (cartel del bus, casa celeste)
    "F": (150, 186, 226), "f": (120, 156, 200),              # tablas celestes
    "V": (110, 160, 90), "v": (82, 128, 66),                 # verde edificio
    "J": (226, 186, 120), "j": (196, 150, 90),               # beige edificio
}


# ------------------------------------------------------------------ herramientas
def estampar(s, grilla, x, y):
    for j, fila in enumerate(grilla):
        for i, ch in enumerate(fila):
            if ch != "." and 0 <= x + i < W and 0 <= y + j < H:
                s.set_at((x + i, y + j), PAL[ch])


def mosaico(s, azulejo, rect):
    """Repite un azulejo dibujado a mano dentro de rect (ladrillos, tablas, alambre...)."""
    x0, y0, w, h = rect
    th, tw = len(azulejo), len(azulejo[0])
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            ch = azulejo[(y - y0) % th][(x - x0) % tw]
            if ch != ".":
                s.set_at((x, y), PAL[ch])


# Letras chicas de 3x5 para los carteles (la fuente del juego no entra en un edificio de 45 px)
LETRAS = {
    "A": ["###", "#.#", "###", "#.#", "#.#"], "B": ["##.", "#.#", "##.", "#.#", "##."],
    "C": ["###", "#..", "#..", "#..", "###"], "E": ["###", "#..", "##.", "#..", "###"], "G": ["###", "#..", "#.#", "#.#", "###"],
    "I": ["###", ".#.", ".#.", ".#.", "###"], "K": ["#.#", "#.#", "##.", "#.#", "#.#"],
    "L": ["#..", "#..", "#..", "#..", "###"], "O": ["###", "#.#", "#.#", "#.#", "###"],
    "S": ["###", "#..", "###", "..#", "###"], "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "U": ["#.#", "#.#", "#.#", "#.#", "###"], "W": ["#...#", "#...#", "#.#.#", "#.#.#", ".#.#."],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."], " ": ["..", "..", "..", "..", ".."],
}


def texto(s, txt, color, centro):
    ancho = sum(len(LETRAS[ch][0]) + 1 for ch in txt) - 1
    x, y = centro[0] - ancho // 2, centro[1] - 2
    for ch in txt:
        estampar(s, [f.replace("#", color) for f in LETRAS[ch]], x, y)
        x += len(LETRAS[ch][0]) + 1


# ------------------------------------------------------------------ piezas (también las usa tools/mapa.py)
def cerca_nevada(s):
    """Nieve sobre las puntas de la cerca de madera (la de arriba y la de abajo)."""
    for x in range(PASTO_X0, PASTO_X1):
        for y0, y1 in ((CERCA_Y0 - 1, PASTO_Y0), (139, H)):
            for y in range(y0, y1):
                if s.get_at((x, y))[:3] == PAL["o"]:
                    s.set_at((x, y - 1), PAL["N"])
                    if y - 2 >= 0 and x % 3:
                        s.set_at((x, y - 2), PAL["n"])
                    break


MONTANA = [   # montaña nevada de South Park (se repite a lo ancho, detrás de la cerca)
    "............NN............",
    "..........NNnnN...........",
    "........NNNnNnNN..........",
    ".......NnNPNnPNNn.........",
    ".....NNPPPPPPPPpnN........",
    "....nPPPPPPPPPPPppn.......",
    "...PPPPPPPPPPPPPpppp......",
    "..PPPPPPPPPPPPPPPpppp.....",
    ".PPPPPPPPPPPPPPPPPpppp....",
    "PPPPPPPPPPPPPPPPPPPpppp...",
]
PINO = [
    "...e...",
    "..eEe..",
    "..EEe..",
    ".eENEe.",
    ".EEEEe.",
    "eENEEEe",
    "EEEEEEe",
    "...o...",
]
CARTEL_BUS = [
    "oooooooooooooo",
    "oBBBBBBBBBBBBo",
    "oBBBBBBBBBBBBo",
    "oBBBBBBBBBBBBo",
    "oBBBBBBBBBBBBo",
    "oBBBBBBBBBBBBo",
    "oxxxxxxxxxxxxo",
    "oooooooooooooo",
    "......oHo.....",
]
BANCO = [
    "ooooooooooo",
    "oDDDDDDDDDo",
    "oddddddddd o".replace(" ", ""),
    "ooooooooooo",
    ".oHo...oHo.",
    ".oHo...oHo.",
    ".oHo...oHo.",
]


EDIFICIOS = [   # fachadas del centro detrás de la baranda (cada una dibujada a mano)
    [
        "oooooooooooooooooooo",
        "oJJJJJJJJJJJJJJJJJJo",
        "ojjjjjjjjjjjjjjjjjjo",
        "oJooooJJooooJJooooJo",
        "oJoGGoJJoGGoJJoGGoJo",
        "oJogGoJJogGoJJogGoJo",
        "oJooooJJooooJJooooJo",
        "oJJJJJJJJJJJJJJJJJJo",
        "oJooooJJooooJJooooJo",
        "oJoGGoJJoLGoJJoGGoJo",
        "oJogGoJJogGoJJogGoJo",
        "oJooooJJooooJJooooJo",
        "oJJJJJJJJJJJJJJJJJJo",
        "ojjjjjjjjjjjjjjjjjjo",
        "oJJJJJJJJJJJJJJJJJJo",
        "oJJJJJJJJJJJJJJJJJJo",
    ],
    [
        "..oooooooooooooo..",
        "..oVVVVVVVVVVVVo..",
        "oooooooooooooooooo",
        "oVVVVVVVVVVVVVVVVo",
        "oVooooVVooooVVoooo",
        "oVoGGoVVoGGoVVoGGo",
        "oVogGoVVogGoVVogGo",
        "oVooooVVooooVVoooo",
        "ovvvvvvvvvvvvvvvvo",
        "oVooooVVooooVVoooo",
        "oVoLGoVVoGGoVVoGGo",
        "oVogGoVVogGoVVogGo",
        "oVooooVVooooVVoooo",
        "oVVVVVVVVVVVVVVVVo",
        "oVVVVVVVVVVVVVVVVo",
        "oVVVVVVVVVVVVVVVVo",
    ],
    [
        "......................",
        "......................",
        "......................",
        "oooooooooooooooooooooo",
        "oRRRRRRRMRRRRRRRMRRRRo",
        "oRooooRRMRooooRRMRoooo",
        "oRoGGoRRMRoGGoRRMRoGGo",
        "oRogGoRRMRogGoRRMRogGo",
        "oRooooRRMRooooRRMRoooo",
        "orrrrrrrMrrrrrrrMrrrro",
        "oRooooRRMRooooRRMRoooo",
        "oRoGGoRRMRoLGoRRMRoGGo",
        "oRogGoRRMRogGoRRMRogGo",
        "oRooooRRMRooooRRMRoooo",
        "oRRRRRRRMRRRRRRRMRRRRo",
        "oRRRRRRRMRRRRRRRMRRRRo",
    ],
]
FAROLITO = [   # farolito chino rojo con franjas amarillas
    "..o..",
    ".ooo.",
    "oyyyo",
    "oQQQo",
    "oQqQo",
    "oQQqo",
    "oyyyo",
    ".ooo.",
    "..Y..",
]


# ------------------------------------------------------------------ fondos de los niveles (sobre A_vereda)
PAL.update({
    "!": (66, 122, 48), "?": (140, 203, 94),                    # matas de pasto (oscuro / claro)
    "&": (230, 130, 50), "*": (196, 96, 40),                    # hojas de otoño
    "(": (224, 176, 122), ")": (200, 149, 92), "[": (154, 107, 62),   # madera de la cerca
})
FILA_PIES = 145          # los pies de plantas y zombies de la última fila caen en y 144: nada los tapa

# Detalles del pasto: piezas chicas, planas (sin perspectiva), dibujadas a mano
MATA = ["?..?", "!?!!", ".!!."]
MATA_CHICA = ["!.?", ".!!"]
FLOR_BLANCA = [".Z.", "ZYZ", ".!."]
FLOR_AMARILLA = [".Y.", "YyY", ".!."]
FLOR_ROJA = [".C.", "CYC", ".!."]
TREBOL = ["?.?", ".!.", "?!?"]
PIEDRITA = [".SS.", "SSSs", ".ss."]
HOJA_1 = ["&&", "&*"]
HOJA_2 = [".&", "&*", "*."]
HOJA_3 = ["QQ", "Qq"]
COPO = [".NN.", "NNnN", ".nn."]
COPO_CHICO = ["NN", "nN"]

DETALLES = {
    "tutorial": [MATA, MATA_CHICA, COPO, COPO, COPO_CHICO, PIEDRITA],
    "nivel1":   [MATA, MATA_CHICA, FLOR_BLANCA, FLOR_AMARILLA, FLOR_ROJA, TREBOL, PIEDRITA],
    "nivel2":   [MATA, MATA_CHICA, HOJA_1, HOJA_2, HOJA_3, HOJA_1, PIEDRITA],
    "nivel3":   [MATA, MATA_CHICA, FLOR_ROJA, FLOR_AMARILLA, TREBOL, MATA],
}

# Cerquita baja de abajo (y 145..149): queda debajo de los pies de la última fila
CERQUITA = [
    ".oo.",
    "o()o",
    "o()o",
    "o)[o",
    "oooo",
]
CERQUITA_NEVADA = [
    ".NN.",
    "o()o",
    "o()o",
    "o)[o",
    "oooo",
]

# Recoloreos de lo que se ve detrás de la cerca (cielo, árboles, sol, nubes)
OTONO = {(156, 195, 180): (214, 140, 70), (180, 212, 198): (236, 176, 96),
         (106, 154, 122): (170, 96, 60), (128, 174, 140): (196, 120, 70), (88, 135, 106): (140, 76, 50)}
ATARDECER = {(95, 174, 227): (236, 136, 102), (125, 192, 236): (246, 164, 112), (163, 214, 243): (252, 198, 136),
             (211, 230, 244): (255, 214, 170), (255, 255, 255): (255, 226, 206),
             (156, 195, 180): (122, 104, 150), (180, 212, 198): (150, 128, 172),
             (106, 154, 122): (90, 82, 122), (128, 174, 140): (110, 96, 138), (88, 135, 106): (70, 64, 100),
             (255, 224, 102): (255, 170, 70), (242, 179, 61): (240, 120, 50)}


def recolorear(s, rect, mapa):
    x0, y0, w, h = rect
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            c = tuple(s.get_at((x, y)))[:3]
            if c in mapa:
                s.set_at((x, y), mapa[c])


def pasto_completo(s, base):
    """La última fila de pasto llega entera hasta y 144 (antes la cerca la pisaba desde y 140) y la
    vereda de la izquierda sigue hasta abajo."""
    s.blit(base, (PASTO_X0, 140), (PASTO_X0, 116, PASTO_X1 - PASTO_X0, 5))     # una casilla más arriba: mismo dibujo
    s.blit(base, (0, 140), (0, 120, PASTO_X0, 10))                             # baldosas de la vereda


def cerca_baja(s, pieza=CERQUITA):
    mosaico(s, ["!", "!", "!", "!", "!"], (0, FILA_PIES, PASTO_X1, H - FILA_PIES))   # sombra del pasto detrás
    mosaico(s, pieza, (0, FILA_PIES, PASTO_X1, H - FILA_PIES))


def detalles_pasto(s, nombre, rnd):
    """2 o 3 detalles por casilla, lejos de los bordes de la casilla y sin pisarse."""
    piezas = DETALLES[nombre]
    for fila in range(5):
        for col in range(9):
            x0, y0 = PASTO_X0 + col * 20, PASTO_Y0 + fila * 24
            puestos = []
            for _ in range(rnd.choice((2, 3, 3))):
                p = rnd.choice(piezas)
                for _intento in range(10):
                    x, y = x0 + rnd.randint(2, 20 - len(p[0]) - 2), y0 + rnd.randint(3, 24 - len(p) - 3)
                    r = pygame.Rect(x - 1, y - 1, len(p[0]) + 2, len(p) + 2)
                    if not any(r.colliderect(q) for q in puestos):
                        estampar(s, p, x, y)
                        puestos.append(r)
                        break


def en_veredas(s, piezas, rnd, n=26):
    """Cosas tiradas en las veredas (nieve, hojas): planas, sin perspectiva."""
    for _ in range(n):
        p = rnd.choice(piezas)
        x = rnd.choice((rnd.randint(1, 38), rnd.randint(226, 234)))
        estampar(s, p, x, rnd.randint(PASTO_Y0 + 2, 140))


def tutorial(s, base, rnd):
    """Invierno: montañas nevadas y pinos detrás de la cerca, nieve en la cerca y en el piso."""
    s.fill((95, 174, 227), (0, 0, W, CERCA_Y0 + 2))
    s.fill((125, 192, 236), (0, 8, W, CERCA_Y0 - 6))
    for x in range(-6, W, 22):
        estampar(s, MONTANA, x, 7)
    for x in range(-2, W, 13):
        estampar(s, PINO, x, 10 + (x // 13) % 2)
    s.blit(base, (PASTO_X0, CERCA_Y0), (PASTO_X0, CERCA_Y0, PASTO_X1 - PASTO_X0, 10))   # la cerca de madera
    s.blit(base, (PASTO_X1, CERCA_Y0 + 2), (PASTO_X1, CERCA_Y0 + 2, W - PASTO_X1, 8))
    recolorear(s, (PASTO_X1, CERCA_Y0, W - PASTO_X1, 10), {(106, 154, 122): PAL["N"], (128, 174, 140): PAL["n"],
                                                            (88, 135, 106): PAL["n"]})
    cerca_nevada(s)
    cerca_baja(s, CERQUITA_NEVADA)
    en_veredas(s, [COPO, COPO_CHICO], rnd, 34)


def nivel1(s, base, rnd):
    """Día de sol: el de A_vereda, con flores."""
    cerca_baja(s)


def nivel2(s, base, rnd):
    """Otoño: árboles naranjas y hojas caídas en el pasto y en las veredas."""
    recolorear(s, (0, 0, W, PASTO_Y0), OTONO)
    cerca_baja(s)
    en_veredas(s, [HOJA_1, HOJA_2, HOJA_3], rnd, 30)


def nivel3(s, base, rnd):
    """Atardecer: cielo naranja, árboles en silueta violeta y el sol bajando."""
    recolorear(s, (0, 0, W, PASTO_Y0), ATARDECER)
    cerca_baja(s)
    # luz cálida de la tarde sobre todo el piso (la barra de cartas tapa casi todo el cielo)
    s.fill((255, 226, 196), (0, PASTO_Y0 - 10, W, H - PASTO_Y0 + 10), special_flags=pygame.BLEND_MULT)


# ------------------------------------------------------------------ armado
NIVELES = {"tutorial": tutorial, "nivel1": nivel1, "nivel2": nivel2, "nivel3": nivel3}


def generar(nombre, base):
    import random
    rnd = random.Random(nombre)
    s = base.copy()
    pasto_completo(s, base)
    detalles_pasto(s, nombre, rnd)
    NIVELES[nombre](s, base, rnd)
    return s


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    base = pygame.image.load(os.path.join(FONDOS, "A_vereda.png")).convert()
    forzar = "--forzar" in sys.argv
    for nombre in NIVELES:
        path = os.path.join(FONDOS, nombre + ".png")
        s = generar(nombre, base)
        # nada por debajo de los pies de la última fila: el pasto llega entero hasta y 144
        assert all(s.get_at((x, 143))[:3] != PAL["o"] for x in range(PASTO_X0, PASTO_X1)), nombre
        if forzar or not os.path.exists(path):
            pygame.image.save(s, path)
            print("creado:", os.path.relpath(path, RAIZ))


if __name__ == "__main__":
    main()
