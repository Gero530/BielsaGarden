import math
import os
from collections import deque
from PIL import Image

AQUI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "zombies", "propios")
FW, FH = 56, 48
OX, OY = 5, 4
CENTRO = (23.0, 22.5)
GOMA = (89, 86, 82)
TACO_A = (66, 64, 62)
TACO_B = (146, 143, 133)
PERIODO = 60.0
POLVO = [(176, 146, 104, 255), (140, 112, 78, 255)]

CAMINAR_PASO = 7.5
CAMINAR_REBOTE = (0, 0, 1, 1, 0, 0, 1, 1)
ATACAR_PASO = 10.0
ATACAR_ADELANTE = (0, 1, 2, 3, 2, 1)
ATACAR_GARRISON = (0, 0, 1, 2, 1, 0)
ATACAR_REBOTE = (0, 1, 1, 0, 1, 0)


def separar(img):
    w, h = img.size
    px = img.load()
    fuera = set()
    cola = deque((x, y) for x in range(w) for y in range(h) if (x in (0, w - 1) or y in (0, h - 1)) and px[x, y][3] == 0)
    fuera.update(cola)
    while cola:
        x, y = cola.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in fuera and px[nx, ny][3] == 0:
                fuera.add((nx, ny))
                cola.append((nx, ny))
    rueda, garrison = [], []
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            if c[3] == 0:
                continue
            toca_fuera = any((x + dx, y + dy) in fuera or not (0 <= x + dx < w and 0 <= y + dy < h)
                             for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            if c[:3] == GOMA or (c[:3] == (0, 0, 0) and toca_fuera):
                rueda.append((x, y, c))
            else:
                garrison.append((x, y, c))
    return rueda, garrison


def tono(x, y, giro):
    ang = math.degrees(math.atan2(-(y + 0.5 - CENTRO[1]), x + 0.5 - CENTRO[0]))
    return TACO_A if ((ang - giro) % PERIODO) < PERIODO / 2 else TACO_B


def frame(rueda, garrison, giro, sube=0, dx_rueda=0, dx_garr=0, polvo=()):
    f = Image.new("RGBA", (FW, FH))
    p = f.load()

    def poner(x, y, c):
        if 0 <= x < FW and 0 <= y < FH:
            p[x, y] = c

    for x, y, c in rueda:
        if c[:3] == GOMA:
            c = tono(x, y, giro) + (255,)
        poner(x + OX + dx_rueda, y + OY, c)
    ocupado = {(x, y) for x, y, _ in rueda}
    for x, y, c in garrison:
        if y >= 36 and sube and (x, y) not in ocupado:
            poner(x + OX + dx_rueda, y + OY, tono(x, y, giro) + (255,))
    for x, y, c in garrison:
        poner(x + OX + dx_rueda + dx_garr, y + OY - sube, c)
    for x, y, c in polvo:
        poner(x, y, c)
    return f


def tira(frames):
    t = Image.new("RGBA", (FW * len(frames), FH))
    for i, f in enumerate(frames):
        t.paste(f, (i * FW, 0))
    return t


def polvo_ataque(i):
    base = {0: [], 1: [(0, 0)], 2: [(0, 0), (-2, -1)], 3: [(0, 0), (-2, -1), (-3, 1)], 4: [(-2, -1), (-3, 0)], 5: [(-3, 1)]}[i]
    return [(1 + dx - ATACAR_ADELANTE[i] // 2 + (k % 2) * 2, 46 + dy, POLVO[k % 2]) for k, (dx, dy) in enumerate(base)]


def main():
    fuente = Image.open(os.path.join(AQUI, "garrison_fuente.png")).convert("RGBA")
    rueda, garrison = separar(fuente)
    caminar = [frame(rueda, garrison, giro=i * CAMINAR_PASO, sube=CAMINAR_REBOTE[i]) for i in range(8)]
    atacar = [frame(rueda, garrison, giro=i * ATACAR_PASO, sube=ATACAR_REBOTE[i], dx_rueda=-ATACAR_ADELANTE[i],
                    dx_garr=-ATACAR_GARRISON[i], polvo=polvo_ataque(i)) for i in range(6)]
    tira(caminar).save(os.path.join(AQUI, "zombie_garrison_caminar.png"))
    tira(atacar).save(os.path.join(AQUI, "zombie_garrison_atacar.png"))
    print("listo: zombie_garrison_caminar.png (8 frames) y zombie_garrison_atacar.png (6 frames), %dx%d" % (FW, FH))


if __name__ == "__main__":
    main()
