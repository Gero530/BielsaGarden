"""
Mapa de niveles en pixel art (250x150, el juego lo ve x4): cordillera nevada, el pueblo, el camino
de tierra que une los niveles y, al lado de cada botón, el lugar de ese nivel (iguales a sus fondos):
  Tutorial -> la parada del bus     Nivel 1 -> la casa del jardín
  Nivel 2  -> la escuela            Nivel 3 -> el centro (City Wok)

    python tools/mapa.py            # crea assets/mapa/fondo_mapa.png si no existe
    python tools/mapa.py --forzar   # lo vuelve a crear (¡pisa tus retoques!)

Los botones de los niveles los dibuja el juego encima, en las posiciones de data/mapa.py.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fondos import pygame, RAIZ, PAL, estampar, mosaico, texto, PINO, CARTEL_BUS, BANCO, EDIFICIOS, FAROLITO

sys.path.insert(0, RAIZ)
from data import mapa as M

W, H = M.ANCHO, M.ALTO
SALIDA = os.path.join(RAIZ, "assets", M.FONDO)
PAL.update({
    "1": (106, 176, 76), "2": (90, 154, 64), "3": (128, 186, 87),      # pasto (los verdes del jardín)
    "4": (196, 150, 90), "5": (154, 107, 62), "6": (224, 176, 122),    # camino de tierra
    "7": (95, 174, 227), "8": (125, 192, 236), "9": (163, 214, 243),   # cielo (de arriba a abajo)
})

PASTO = ["1111", "1121", "1111", "2111", "1111", "1113"]

MONTANA = [
    "..............NN..............",
    ".............NNnN.............",
    "............NNNnnN............",
    "...........NNnNnnnn...........",
    "..........NNNNnnnnnn..........",
    ".........NnPNnPnnnPnn.........",
    "........PPPPPNPPnpPpPp........",
    ".......PPPPPPPPPPpppppp.......",
    "......PPPPPPPPPPPPppppppp.....",
    ".....PPPPPPPPPPPPPpppppppp....",
    "....PPPPPPPPPPPPPPPppppppppp..",
    "...PPPPPPPPPPPPPPPPpppppppppp.",
    "..PPPPPPPPPPPPPPPPPPpppppppppp",
    ".PPPPPPPPPPPPPPPPPPPpppppppppp",
    "PPPPPPPPPPPPPPPPPPPPpppppppppp",
]
LOMA = [   # lomas verdes delante de las montañas
    "........EEEEEEE.........",
    ".....EEEEEEEEEEEEe......",
    "...EEEEEEEEEEEEEEEEee...",
    ".EEEEEEEEEEEEEEEEEEEeee.",
    "EEEEEEEEEEEEEEEEEEEEEeee",
]
NIEVE = [".NNN.", "NNnNN", ".nnn."]
NIEVE_CHICA = ["NN.", ".Nn"]
CASA = [
    ".......ooo.......",
    "......oTTTo......",
    ".....oTTUTTo.....",
    "....oTTTTTTTo....",
    "...oTTTTTUTTTo...",
    "..oTTUTTTTTTTTo..",
    ".ottttttttttttto.",
    "..o11111111111o..",
    "..o1ooo111ooo1o..",
    "..o1oGo111oGo1o..",
    "..o1ooo1oo1ooo1o.",
    "..o1111oDo11111o.",
    "..o1111oDo11111o.",
    "..o1111oYo11111o.",
    "..ooooooooooooo..",
]
CERQUITA = ["o.o.o.o.o.o.o.o.o.o", "6o6o6o6o6o6o6o6o6o6", "ooooooooooooooooooo", "6o6o6o6o6o6o6o6o6o6"]
LAGO = [
    "........NNNNNNNNNNNNNNN.........",
    "....NNNNnnLLLLLLLLLLLnnNNNN.....",
    "..NNnLLLLGGGGGGGGGGGGLLLLnNNN...",
    ".NnLLGGGGGGGGgGGGGGGGGGGGLLnNN..",
    "NnLGGGGGgGGGGGGGGGGGGgGGGGGLnNN.",
    "NnLGGGGGGGGGGGGGGGgGGGGGGGGLLnN.",
    ".NnLLGGGGGGGgGGGGGGGGGGGLLLnNN..",
    "..NNnnLLLLGGGGGGGGGGLLLLnnNN....",
    "....NNNNnnnnnnnnnnnnnnNNNN......",
]
ESCUELA = [
    "...............oooo.............",
    "...............oBBo.............",
    "...............oxxo.............",
    "...............H................",
    "oooooooooooooooHoooooooooooooooo",
    "oSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSo",
    "oWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWo",
    "oWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWo",
    "oWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWo",
    "oWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWo",
    "oWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWo",
    "oRRRRRRRMRRRRRRRMRRRRRRRMRRRRRRo",
    "oRoooRRRMRoooRRRMRRRoooRMRRoooRo",
    "oRoGoRRRMRoGoRRRMRRRoGoRMRRoGoRo",
    "oRoooRRRMRoooRRRMRRRoooRMRRoooRo",
    "orrrrrrrMrrrrrooooorrrrrMrrrrrro",
    "oRRRRRRRMRRRRoDDoDDoRRRRMRRRRRRo",
    "oRoooRRRMRRRRoDDoDDoRRRRMRoooRRo",
    "oRoGoRRRMRRRRoDDoDDoRRRRMRoGoRRo",
    "oRoooRRRMRRRRoDYoYDoRRRRMRoooRRo",
    "oRRRRRRRMRRRRoDDoDDoRRRRMRRRRRRo",
    "oooooooooooooooooooooooooooooooo",
    "..SSSSSSSSSSSSSSSSSSSSSSSSSSSS..",
]
WOK = [
    "oooooooooooooooooooooooooooooo",
    "oYYYYYYYYYYYYYYYYYYYYYYYYYYYYo",
    "oYQQQQQQQQQQQQQQQQQQQQQQQQQQYo",
    "oYQQQQQQQQQQQQQQQQQQQQQQQQQQYo",
    "oYQQQQQQQQQQQQQQQQQQQQQQQQQQYo",
    "oYQQQQQQQQQQQQQQQQQQQQQQQQQQYo",
    "oYQQQQQQQQQQQQQQQQQQQQQQQQQQYo",
    "oYYYYYYYYYYYYYYYYYYYYYYYYYYYYo",
    "oooooooooooooooooooooooooooooo",
    ".oQQQQQQQQQQQQQQQQQQQQQQQQQqo.",
    ".oQooooooooQQQQQQQooooooooqo.",
    ".oQoLGGGGGoQQoooQQoGGGGGgoqo.",
    ".oQoGGGGGgoQQoQoQQoGGGGggoqo.",
    ".oQoGGGGggoQQoQoQQoGGGgggoqo.",
    ".oQooooooooQQoQoQQooooooooqo.",
    ".oQQQQQQQQQQQoYoQQQQQQQQQQqo.",
    ".oQQQQQQQQQQQoQoQQQQQQQQQQqo.",
    ".oooooooooooooooooooooooooooo.",
    "..SSSSSSSSSSSSSSSSSSSSSSSSSS..",
]
PINO_GRANDE = [
    "....e....",
    "...eEe...",
    "...NEe...",
    "..eENEe..",
    "..EEEEe..",
    ".eENEEEe.",
    ".EEEEEEe.",
    "eENEEEEEe",
    "EEEEEEEEe",
    "....o....",
    "....o....",
]
PIEDRA = [".ss.", "sSSs", ".ss."]


def camino(s, pts):
    """Camino de tierra con borde, siguiendo los botones de los niveles (pincel redondo dibujado a mano)."""
    borde = [".555.", "55555", "55555", "55555", ".555."]
    relleno = ["444", "464", "444"]
    for pincel, off in ((borde, 2), (relleno, 1)):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            n = max(abs(x1 - x0), abs(y1 - y0))
            for i in range(n + 1):
                x, y = round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)
                estampar(s, pincel, x - off, y - off)


def lejos(x, y, pts, botones, d=10):
    """True si (x, y) no pisa el camino ni un botón."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(0, n + 1, 2):
            if abs(x - (x0 + (x1 - x0) * i / n)) < d and abs(y - (y0 + (y1 - y0) * i / n)) < d:
                return False
    return all(abs(x - bx) > 16 or abs(y - by) > 16 for bx, by in botones)


def generar():
    s = pygame.Surface((W, H))
    # Cielo en tres franjas y la cordillera
    for y0, y1, c in ((0, 12, "7"), (12, 22, "8"), (22, 40, "9")):
        s.fill(PAL[c], (0, y0, W, y1 - y0))
    for x, y in ((-12, 14), (16, 10), (46, 16), (78, 8), (108, 14), (140, 9), (170, 15), (200, 7), (230, 13)):
        estampar(s, MONTANA, x, y)
    for x in range(-10, W, 22):
        estampar(s, LOMA, x, 30 + (x // 22) % 2)
    mosaico(s, PASTO, (0, 35, W, H - 35))
    rnd = random.Random(7)
    pts = [n["pos"] for n in M.NIVELES]
    botones = list(pts)
    for _ in range(70):                                        # manchones de nieve
        x, y = rnd.randrange(0, W - 5), rnd.randrange(38, H - 3)
        estampar(s, NIEVE if rnd.random() < 0.4 else NIEVE_CHICA, x, y)
    camino(s, pts)
    for x, y in ((pts[0][0] - 9, pts[0][1] + 6), (pts[-1][0] + 4, pts[-1][1] - 14)):   # el camino sigue
        estampar(s, PIEDRA, x, y)

    # Tutorial: la parada del bus y la casita celeste
    estampar(s, [f.replace("1", "F") for f in CASA], 4, 126)
    estampar(s, CARTEL_BUS, 12, 88)
    texto(s, "BUS", "W", (19, 92))
    s.fill(PAL["o"], (18, 97, 3, 22)); s.fill(PAL["H"], (19, 97, 1, 22))
    estampar(s, BANCO, 2, 116)
    # Nivel 1: la casa del jardín con su cerquita, y el lago congelado de adorno
    estampar(s, [f.replace("1", "A") for f in CASA], 62, 54)
    estampar(s, CERQUITA, 58, 68)
    estampar(s, LAGO, 104, 44)
    texto(s, "LAGO", "x", (120, 49))
    # Nivel 2: la escuela con su bandera
    estampar(s, ESCUELA, 168, 112)
    texto(s, "ESCUELA", "O", (184, 120))
    # Nivel 3: el centro, con el City Wok adelante de los edificios
    estampar(s, EDIFICIOS[1], 222, 50)
    estampar(s, EDIFICIOS[0], 230, 58)
    estampar(s, WOK, 218, 80)
    texto(s, "WOK", "Y", (233, 84))
    for x in (222, 238):
        estampar(s, FAROLITO, x, 89)

    # Pinos donde no estorban
    lugares = [pygame.Rect(0, 84, 34, 66), pygame.Rect(56, 50, 24, 26), pygame.Rect(102, 42, 34, 12),
               pygame.Rect(166, 106, 34, 30), pygame.Rect(216, 48, 34, 52)]
    for _ in range(400):
        x, y = rnd.randrange(0, W - 9), rnd.randrange(34, H - 11)
        r = pygame.Rect(x, y, 9, 11)
        if lejos(x + 4, y + 9, pts, botones) and not any(r.colliderect(l) for l in lugares):
            estampar(s, PINO_GRANDE if rnd.random() < 0.6 else PINO, x, y)
            lugares.append(r.inflate(4, 2))
        if len(lugares) > 34:
            break
    return s


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    if "--forzar" in sys.argv or not os.path.exists(SALIDA):
        os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
        pygame.image.save(generar(), SALIDA)
        print("creado:", os.path.relpath(SALIDA, RAIZ))


if __name__ == "__main__":
    main()
