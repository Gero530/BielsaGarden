"""
Zombies propios: personajes, animaciones y exportación. Todos usan el cuerpo base de
tools/zombies_pixel.py (el vecino de musculosa) y cambian ropa, pelo y accesorios.

    python tools/zombies_disenos.py            # crea las tiras que faltan en assets/zombies/propios/
    python tools/zombies_disenos.py --forzar   # las vuelve a crear todas (¡pisa tus retoques!)
    python tools/zombies_disenos.py --preview  # además, GIFs x4 en assets/sprites/propuestas/

Cada tira es horizontal, un frame al lado del otro, mirando a la izquierda, pies en la última fila.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zombies_pixel import (pygame, RAIZ, FRAME_W, FRAME_H, CABEZA, TORSO, BRAZO_ADELANTE, BRAZO_ATRAS,
                           PIERNAS, POS, BOB, CAM_CABEZA_DY, CAM_BRAZO_DX, ATQ, ATQ_BOB, ATQ_PIERNAS,
                           cabeza_con, frame, tira, guardar_gif, pasto, espejo_v, rotar_der, mangas)

DEST = os.path.join(RAIZ, "assets", "zombies", "propios")
PREVIEW = os.path.join(RAIZ, "assets", "sprites", "propuestas")
OX = 2      # el cuerpo va corrido 2 px a la derecha: al morder, la cabeza y las manos no se salen


# ------------------------------------------------------------------ herramientas de grilla
def dup_filas(g, filas):
    """Repite filas (alarga una parte sin deformar el contorno)."""
    out = []
    for y, f in enumerate(g):
        out.append(f)
        if y in filas:
            out.append(f)
    return out


def dup_cols(g, cols):
    return ["".join(ch * (2 if x in cols else 1) for x, ch in enumerate(f)) for f in g]


def engordar(g, n=1):
    """Ensancha cada fila n px repitiendo su primer píxel de relleno (sirve en partes en diagonal)."""
    out = []
    for f in g:
        i = next((j for j, ch in enumerate(f) if ch not in ".#"), None)
        if i is None:
            i = f.find("#")
            if i < 0:
                out.append(f)
                continue
        out.append(f[:i] + f[i] * n + f[i:])
    return out


def estampar(g, azulejo, ranuras="12"):
    """Pinta una textura (azulejo repetido) sobre las ranuras de una prenda: cuadros, batik..."""
    h, w = len(azulejo), len(azulejo[0])
    return ["".join(azulejo[y % h][x % w] if ch in ranuras and azulejo[y % h][x % w] != "." else ch
                    for x, ch in enumerate(f)) for y, f in enumerate(g)]


def palo(dx, dy, color="y"):
    """Palo recto de 1 px con contorno (como la herramienta línea de LibreSprite), de (0,0) a (dx,dy)."""
    n = max(abs(dx), abs(dy))
    pts = {(round(dx * i / n), round(dy * i / n)) for i in range(n + 1)}
    x0, y0 = min(p[0] for p in pts) - 1, min(p[1] for p in pts) - 1
    w, h = max(p[0] for p in pts) - x0 + 2, max(p[1] for p in pts) - y0 + 2
    g = [["."] * w for _ in range(h)]
    for x, y in pts:
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if g[y - y0 + ay][x - x0 + ax] == ".":
                    g[y - y0 + ay][x - x0 + ax] = "#"
    for x, y in pts:
        g[y - y0][x - x0] = color
    return ["".join(f) for f in g], -x0, -y0           # grilla y dónde cae el punto (0,0) dentro de ella


# ------------------------------------------------------------------ cuerpo y armado de frames
BASE = {"pos": POS, "piernas": PIERNAS, "bob": BOB, "torso": TORSO, "brazo_adelante": BRAZO_ADELANTE,
        "brazo_atras": BRAZO_ATRAS, "cabeza": lambda boca: cabeza_con(boca, CABEZA)}


def pose(bob=0, cabeza=(0, 0), torso_dx=0, brazo=(0, 0), brazo_atras=(0, 0), piernas=(2, 6), boca="normal", **k):
    p = dict(bob=bob, cabeza=cabeza, torso_dx=torso_dx, brazo=brazo, brazo_atras=brazo_atras,
             piernas=piernas, boca=boca)
    p.update(k)    # ba_grilla / ba_pos / bt_grilla / bt_pos: otra pose de brazo en ese frame; i: n° de frame
    return p


def capas(pj, p, extra=None):
    """Capas de un frame. extra(p) -> dict con capas en "atras", "medio" (detrás de la cabeza),
    "sobre_cabeza" y "adelante"."""
    cu = pj.get("cuerpo", BASE)
    pos, b = cu["pos"], p["bob"]
    ex = extra(p) if extra else {}
    out = list(ex.get("atras", []))
    g = p["bt_grilla"] if "bt_grilla" in p else pj.get("brazo_atras", cu["brazo_atras"])
    if g:
        ax, ay = p.get("bt_pos", pos["brazo_atras"])
        out.append((g, ax + p["brazo_atras"][0], ay + b + p["brazo_atras"][1], True))
    fa, fb = p["piernas"]
    px, py = pos["pierna_atras"]
    if fb is not None:
        out.append((cu["piernas"][fb], px, py + cu["bob"][fb], True))
    tx, ty = pos["torso"]
    out.append((pj.get("torso", cu["torso"]), tx + p["torso_dx"], ty + b))
    for g, dx, dy in pj.get("torso_extra", []):
        out.append((g, tx + p["torso_dx"] + dx, ty + b + dy))
    out += ex.get("medio", [])
    px, py = pos["pierna_adelante"]
    if fa is not None:
        out.append((cu["piernas"][fa], px, py + cu["bob"][fa]))
    hx, hy = pos["cabeza"][0] + p["cabeza"][0], pos["cabeza"][1] + p["cabeza"][1]
    out.append((cu["cabeza"](p["boca"]), hx, hy))
    for g, dx, dy in p.get("sombrero", pj.get("sombrero", [])):
        out.append((g, hx + dx, hy + dy))
    out += ex.get("sobre_cabeza", [])
    g = p["ba_grilla"] if "ba_grilla" in p else pj.get("brazo_adelante", cu["brazo_adelante"])
    if g:
        ax, ay = p.get("ba_pos", pos["brazo_adelante"])
        out.append((g, ax + p["brazo"][0], ay + b + p["brazo"][1]))
    out += ex.get("adelante", [])
    return out


def caminar_poses(bob=BOB):
    """8 frames: contacto, baja, pasa, sube (pierna de adelante) y lo mismo con la de atrás."""
    return [pose(bob=bob[i], cabeza=(0, CAM_CABEZA_DY[i]), brazo=(CAM_BRAZO_DX[i], 0),
                 brazo_atras=(-CAM_BRAZO_DX[i], 0), piernas=(i, (i + 4) % 8), i=i) for i in range(8)]


def atacar_poses():
    return [pose(bob=ATQ_BOB, cabeza=c, torso_dx=t, brazo=a, brazo_atras=a, piernas=ATQ_PIERNAS, boca=m, i=i)
            for i, (t, c, m, a) in enumerate(ATQ)]


def anim(pj, poses, extra=None, w=FRAME_W, h=FRAME_H, ox=OX, oy=0):
    out = []
    for p in poses:
        cs = [(g, x + ox, y + oy) + tuple(r) for g, x, y, *r in capas(pj, p, extra)]
        out.append(frame(cs, pj.get("mapa"), w, h))
    return out


def con_extra(fn, **fijos):
    return lambda p: fn(p, **fijos)


# ------------------------------------------------------------------ brazos extra (dibujados a mano)
# Brazo de atrás levantado (señala para arriba por detrás de la cabeza): bailarín, gigante, garrocha
BRAZO_ARRIBA = mangas([
    "..#...",
    ".#k#..",
    ".#k##.",
    "#kkkK#",
    "#kkKK#",
    ".#kK#.",
    ".#kK#.",
    ".#kK#.",
    ".#kK#.",
    ".#kK#.",
    "..#kK#",
    "..#kK#",
    "..#kK#",
    "..#kK#",
    "..#kK#",
    "..#kK#",
    "..#kK#",
    "..#kK#",
    "..#kkK#",
    ".#kkKK#",
    ".######",
], 99, 99)
BRAZO_ARRIBA = ["".join({"k": "7", "K": "8"}.get(c, c) if y >= 10 else ({"k": "9", "K": "0"}.get(c, c) if y >= 5 else c)
                        for c in f) for y, f in enumerate(BRAZO_ARRIBA)]
POS_ARRIBA = (15, 1)
# Brazo de adelante señalando abajo y adelante (paso de disco)
BRAZO_ABAJO = mangas([
    "...........####.",
    "..........#kkkK#",
    ".........#kkkKK#",
    "........#kkkKK#.",
    ".......#kkkKK#..",
    "......#kkkKK#...",
    ".....#kkkKK#....",
    "....#kkkKK#.....",
    "...#kkkKK#......",
    "..#kkKK##.......",
    ".#kkK#..........",
    "#k#k#...........",
    ".#.#............",
], 9, 6)


# ------------------------------------------------------------------ 1. Normal: el vecino de musculosa
NORMAL = {"mapa": {}}


# ------------------------------------------------------------------ 2. Puerta: vecino con la puerta de su casa
PUERTA_MAPA = {"1": "v", "2": "V", "+": "v", "=": "V", "7": "v", "8": "V", "~": "v", "^": "V", "%": "t",
               "3": "a", "4": "A", "S": "a", "Z": "A", "5": "n", "6": "N", "H": "n"}
PEINADO = [   # raya al costado, un mechón cae sobre la frente
    "....#######....",
    "..##nnnnnnn##..",
    ".#nnnnnnnnnnN#.",
    "#nn#nnnnnnnNNN#",
    "#n#.........NN#",
]
PUERTA_OBJ = [
    "..########",
    ".#nnnnnnN#",
    "#nnnnnnnN#",
    "#n######N#",
    "#n#nnnN#N#",
    "#n#nnnN#N#",
    "#n#nnnN#N#",
    "#n#nnnN#N#",
    "#n#nnnN#N#",
    "#n#NNNN#N#",
    "#n######N#",
    "#nnnnnnnN#",
    "#nn#GG#nN#",
    "#nn#Gg#nN#",
    "#yYnnnnnN#",
    "#nnnnnnnN#",
    "#n######N#",
    "#n#nnnN#N#",
    "#n#nnnN#N#",
    "#n#nnnN#N#",
    "#n#nnnN#N#",
    "#n#nnnN#N#",
    "#n#NNNN#N#",
    "#n######N#",
    "#nnnnnnnN#",
    "#nnnn#nnN#",
    "#nnn#nnnN#",
    "##########",
]
DEDOS_BORDE = [
    "###.",
    "kkK#",
    "###.",
    "kkK#",
    "###.",
]


def puerta_extra(p):
    dx, dy = p["brazo"][0], p["bob"] + p["brazo"][1]
    return {"adelante": [(PUERTA_OBJ, -1 + dx, 18 + dy), (DEDOS_BORDE, 7 + dx, 25 + dy)]}


PUERTA = {"mapa": PUERTA_MAPA, "sombrero": [(PEINADO, 0, 0)]}


# ------------------------------------------------------------------ 3. Diario: jubilado
DIARIO_MAPA = {"1": "o", "2": "O", "+": "o", "=": "O", "7": "o", "8": "O", "9": "o", "0": "O",
               "~": "o", "^": "O", "@": "O", "%": "C", "3": "n", "4": "N", "S": "n", "Z": "N",
               "5": "r", "6": "R", "H": "a"}
CEJAS = [          # cejas canosas y bigote (relativo a la cabeza)
    "...............",
    "...............",
    "...............",
    ".aa..aaaa......",
    "#.aa.#aa.......",
    "...............",
    "...............",
    "...............",
    "...............",
    ".aaaaa.........",
]
CEJAS_ENOJADO = [
    "...............",
    "...............",
    "...............",
    "aa.....aa......",
    "#aa#.aaa.......",
    "...............",
    "...............",
    "...............",
    "...............",
    ".aaaaa.........",
]
BOTONES = [        # cuello de la camisa y botones del saco (relativo al torso)
    "...............",
    "....ww.........",
    "...#ws#........",
    "...............",
    "...y...........",
    "...............",
    "...y...........",
    "...............",
    "...y...........",
]
DIARIO_OBJ = [
    "##############",
    "#w###ws#w###s#",
    "#wwwwws#wwwws#",
    "#wAAAws#wAAAs#",
    "#wwwwws#wwwws#",
    "#wAAwws#wAAws#",
    "#w##wws#wwwws#",
    "#w##AAs#wAAAs#",
    "#wwwwws#wwwws#",
    "#wAAAws#wAAAs#",
    "#wwwwws#wwwws#",
    "##############",
]
DEDOS_IZQ = [
    ".##",
    "#kk",
    ".##",
    "#kk",
    ".##",
]


def diario_extra(p):
    dx, dy = p["brazo"][0], p["bob"] + p["brazo"][1]
    return {"adelante": [(DIARIO_OBJ, 0 + dx, 19 + dy), (DEDOS_IZQ, -1 + dx, 22 + dy),
                         (DEDOS_BORDE, 12 + dx, 21 + dy)]}


DIARIO = {"mapa": DIARIO_MAPA, "sombrero": [(CEJAS, 0, 0)], "torso_extra": [(BOTONES, 0, 0)]}
DIARIO_ENOJADO = {"mapa": DIARIO_MAPA, "sombrero": [(CEJAS_ENOJADO, 0, 0)], "torso_extra": [(BOTONES, 0, 0)]}


# ------------------------------------------------------------------ 4. Escalera: pintor
ESCALERA_MAPA = {"1": "w", "2": "s", "+": "b", "=": "B", "7": "b", "8": "B", "~": "w", "^": "s",
                 "@": "s", "%": "y", "3": "w", "4": "s", "S": "w", "Z": "s", "5": "n", "6": "N", "H": "c"}
GORRA_PINTOR = [
    "......#######....",
    "....##wwwwwww##..",
    "...#wwwwwwwwwss#.",
    "..#wbwwwwwwwwsss#",
    "################.",
]
TIRANTES = [       # tirantes del overol y gotas de pintura (relativo al torso)
    "...............",
    "...w....w......",
    "...w....w......",
    "...w....w......",
    "...............",
    "......b........",
    "..........x....",
    "...............",
    "....y..........",
    "...........b...",
]
ESCALERA_V = [
    "#c#..#c#",
    "#c#..#c#",
    "#c####c#",
    "#cCCCCc#",
    "#c####c#",
    "#c#..#c#",
    "#c#..#c#",
    "#c####c#",
    "#cCCCCc#",
    "#c####c#",
    "#c#..#c#",
    "#c#..#c#",
    "#c####c#",
    "#cCyCCc#",
    "#c####c#",
    "#c#..#c#",
    "#c#..#c#",
    "#c####c#",
    "#cCCCCc#",
    "#c####c#",
    "#c#..#c#",
    "#c#..#c#",
    "#c####c#",
    "#cCCCbc#",
    "#c####c#",
    "#C#..#C#",
    "###..###",
]
ESCALERA_H = rotar_der(ESCALERA_V)


def escalera_extra(p):
    return {"medio": [(ESCALERA_H, -1, 11 + p["bob"])]}


ESCALERA = {"mapa": ESCALERA_MAPA, "sombrero": [(GORRA_PINTOR, -2, -2)], "torso_extra": [(TIRANTES, 0, 0)]}


def escalera_colocar():
    """6 frames: la baja del hombro, la para adelante, la empuja contra la planta y la suelta."""
    ps = []
    for i in range(6):
        ps.append(pose(bob=(1, 2, 1, 1, 2, 1)[i], cabeza=(0, (0, 1, 1, 0, 1, 0)[i]), piernas=(1, 4) if i < 4 else (0, 4),
                       brazo=(0, 0) if i < 3 else (-1, 0), brazo_atras=(0, 0), i=i, torso_dx=-1 if i in (3, 4) else 0))

    def ex(p):
        i = p["i"]
        if i == 0:
            return {"medio": [(ESCALERA_H, -1, 11 + p["bob"])]}
        if i == 1:
            return {"medio": [(ESCALERA_H, -3, 8 + p["bob"])]}
        x = (3, 1, 0, -2)[i - 2]
        return {"adelante": [(ESCALERA_V, x, 20 + (i == 2) * -2)] + ([(DEDOS_BORDE, x + 6, 27)] if i < 5 else [])}
    return ps, ex


# ------------------------------------------------------------------ 5. Pértiga: profe de gimnasia
PERTIGA_MAPA = {"1": "r", "2": "R", "+": "r", "=": "R", "7": "r", "8": "R", "9": "r", "0": "R",
                "~": "r", "^": "R", "@": "R", "%": "R", "3": "r", "4": "R", "S": "r", "Z": "R",
                "5": "w", "6": "s", "H": "N"}
PELO_PROFE = [     # pelo corto parado, vincha y bigote (relativo a la cabeza)
    "...#.#.#.#.....",
    "..#N#N#N#N##...",
    "..#NNNNNNNNN#..",
    ".#yyyyyyyyyyY#.",
    "...............",
    "...............",
    "...............",
    "...............",
    "...............",
    "..............",
    ".NNNN..........",
]
SILBATO = [        # cierre del jogging y silbato (relativo al torso)
    "...............",
    "....w..........",
    "...w.w.........",
    "...w.w.........",
    "....w..........",
    "...#GG#........",
    "...w...........",
    "...w...........",
    "...w...........",
    "...w...........",
]
PERTIGA = {"mapa": PERTIGA_MAPA, "sombrero": [(PELO_PROFE, 0, -1)], "torso_extra": [(SILBATO, 0, 0)]}
PERTIGA_W, PERTIGA_OX = 48, 19       # frame más ancho: la garrocha asoma adelante
GARROCHA, GX, GY = palo(44, 16)      # de la punta (adelante y arriba) hasta atrás, pasando por las manos


def pertiga_extra(p):
    dx, dy = p["brazo"][0], p["bob"] + p["brazo"][1]
    # la garrocha va de adelante-arriba (x negativos: fuera del cuerpo) a atrás-abajo
    return {"medio": [(GARROCHA, -18 - GX + dx, 15 - GY + dy)]}


def pertiga_salto():
    """6 frames 48x48: clava la garrocha, despega, pasa horizontal, arriba de cabeza, cae, aterriza."""
    pj = PERTIGA

    def cuerpo(p, extra=None):
        return anim(pj, [p], extra, 31, 48, OX)[0]

    clavada, cgx, cgy = palo(20, -33)     # punta clavada en el piso adelante, arriba en las manos
    vertical, vgx, vgy = palo(6, -41)
    frames = []
    w = PERTIGA_W
    ancho = dict(w=w, ox=PERTIGA_OX)
    # 0: agachado, la garrocha clavada adelante
    frames += anim(pj, [pose(bob=2, piernas=(1, 5), cabeza=(0, 1), brazo=(-1, 0))],
                   lambda p: {"medio": [(clavada, -16 - cgx, 47 - cgy)]}, **ancho)
    # 1: despega con los brazos arriba
    frames += anim(pj, [pose(bob=0, piernas=(5, 3), bt_grilla=BRAZO_ARRIBA, bt_pos=POS_ARRIBA, boca="abierta")],
                   lambda p: {"medio": [(vertical, -8 - vgx, 47 - vgy)]}, **ancho)
    # 2 y 3: el cuerpo gira por arriba de la garrocha (giros de 90°, sin perder píxeles)
    quieto = cuerpo(pose(bob=0, piernas=(7, 5), bt_grilla=BRAZO_ARRIBA, bt_pos=POS_ARRIBA))
    for ang in (-90, 180):
        s = pygame.Surface((w, 48), pygame.SRCALPHA)
        r = pygame.transform.rotate(quieto, ang)
        s.blit(r, (PERTIGA_OX - OX + 15 - r.get_width() // 2, (48 - r.get_height()) // 2))
        frames.append(s)
    # 4: cae con las piernas adelante, ya sin garrocha
    frames += anim(pj, [pose(bob=0, piernas=(7, 7), bt_grilla=BRAZO_ARRIBA, bt_pos=POS_ARRIBA, boca="abierta")], **ancho)
    # 5: aterriza agachado
    frames += anim(pj, [pose(bob=2, piernas=(1, 5), cabeza=(0, 2))], **ancho)
    return frames


PERTIGA_SIN = PERTIGA


# ------------------------------------------------------------------ 6. Excavador: minero
EXCAVADOR_MAPA = {"1": "b", "2": "B", "+": "o", "=": "O", "7": "o", "8": "O", "~": "b", "^": "B",
                  "@": "N", "%": "t", "3": "b", "4": "B", "S": "b", "Z": "B", "5": "n", "6": "N", "H": "N"}
CASCO = [
    ".....#######....",
    "...##yyyyyyyY##.",
    "..#yyyyyyyyyYYY#",
    "##yyyyyyyyyyYYY#",
    "#w#yyyyyyyyyYYY#",
    "#w##############",
    "##..............",
]
TIZNE = [          # tierra en la ropa y tirantes (relativo al torso)
    "...............",
    "...b....b......",
    "...b....b......",
    "...............",
    "..t............",
    ".........t.....",
    "...............",
    "......t........",
]
PICO = [
    "....######....",
    "..##GGGGGG##..",
    ".#GG##nN##gg#.",
    "#G#..#nN#..#g#",
    "##...#nN#...##",
    ".....#nN#.....",
    "......#nN#....",
    "......#nN#....",
    "......#nN#....",
    ".......#nN#...",
    ".......#nN#...",
    ".......#nN#...",
    "........#nN#..",
    "........#nN#..",
    "........#nN#..",
    ".........#nN#.",
    ".........#nN#.",
    ".........####.",
]


def excavador_extra(p):
    return {"atras": [(PICO, 8 + p["torso_dx"], 3 + p["bob"])]}


EXCAVADOR = {"mapa": EXCAVADOR_MAPA, "sombrero": [(CASCO, -1, -2)], "torso_extra": [(TIZNE, 0, 0)]}


def excavador_tierra():
    """4 frames: el montículo de tierra que avanza (con terrones que saltan y la lamparita que asoma)."""
    mont = [
        "........######........",
        "......##tttttt##......",
        "....##ttttttttTT##....",
        "...#tttTtttttttTTT#...",
        "..#ttttttttTtttTTTT#..",
        ".#ttTttttttttttTTTTT#.",
        "#tttttttTttttttTTTTTT#",
        "######################",
    ]
    asoma = [".#####.", "#yyyyY#", "#w#yYY#"]
    terron = ["##", "#t"]
    out = []
    for i in range(4):
        cs = [(mont, 4, 40 - (i % 2))]
        if i in (1, 3):
            cs.append((asoma, 11, 37 - (i % 2)))
        cs.append((terron, (2, 24, 3, 25)[i], (36, 34, 33, 37)[i]))
        cs.append((terron, (25, 4, 26, 2)[i], (34, 36, 38, 33)[i]))
        out.append(frame(cs, EXCAVADOR_MAPA))
    return out


# ------------------------------------------------------------------ 7. Bailarín: hippie
BAILARIN_MAPA = {"1": "f", "2": "F", "+": "f", "=": "F", "7": "f", "8": "F", "%": "y", "~": "k", "^": "K",
                 "@": "n", "3": "p", "4": "P", "S": "p", "Z": "P", "5": "p", "6": "P", "H": "n"}
PELO_LARGO = [
    ".....#######.....",
    "...##nnnnnnn##...",
    "..#nnnnnnnnnnN#..",
    ".#xxxxxxxxxxxxx#.",
    ".#n.........nnN#.",
    "............nnN#.",
    "............nnNN#",
    "............nnNN#",
    "............nnNN#",
    "............nnNN#",
    "...........#nnNN#",
    "...........#nnNN#",
    "...........#nNNN#",
    "...........#nNN#.",
    "...........#nNN#.",
    "............#N#..",
    ".............#...",
]
BATIK = [          # textura de la remera teñida (se estampa sobre la prenda)
    "fyff",
    "bffy",
    "fffb",
    "ybff",
]
COLLAR = [
    "...............",
    "...............",
    "..G...G........",
    "...G.G.........",
    "....#..........",
    "...#w#.........",
    "....#..........",
]
BAILARIN = {"mapa": BAILARIN_MAPA, "sombrero": [(PELO_LARGO, -1, -1)],
            "torso": estampar(TORSO, BATIK), "torso_extra": [(COLLAR, 0, 0)]}


def bailarin_baile():
    """8 frames: paso de disco (señala arriba y abajo), mueve la cadera y llama a los compañeros."""
    ps = []
    for i in range(8):
        arriba = i in (1, 2, 5, 6)
        ps.append(pose(bob=(1, 0, 0, 1, 1, 0, 0, 1)[i], cabeza=(0, (0, 0, 0, 1, 0, 0, 0, 1)[i]),
                       torso_dx=(0, -1, -1, 0, 0, 1, 1, 0)[i] if i < 4 else 0,
                       piernas=((2, 6), (0, 4), (0, 4), (2, 6), (6, 2), (4, 0), (4, 0), (6, 2))[i],
                       ba_grilla=BRAZO_ABAJO if arriba else BRAZO_ADELANTE,
                       bt_grilla=BRAZO_ARRIBA if arriba else BRAZO_ATRAS,
                       bt_pos=POS_ARRIBA if arriba else POS["brazo_atras"], i=i,
                       boca="abierta" if i in (2, 6) else "normal"))
    return ps


# ------------------------------------------------------------------ 8. Bungee
BUNGEE_MAPA = {"1": "b", "2": "B", "3": "o", "4": "O", "5": "w", "6": "s", "@": "y", "%": "B", "H": "N"}
CASCO_BUNGEE = [
    "....#######....",
    "..##rrrrrrr##..",
    ".#rrwwwwrrrRR#.",
    "#rrrrrrrrrRRRR#",
    "#rrrrrrrrrRRRR#",
    "###############",
]
ARNES = [
    "...............",
    "...............",
    "...............",
    "..y.....y......",
    "..y.....y......",
    "...y...y.......",
    "...yyyyy.......",
    "...y...y.......",
    "..y.....y......",
    "..y.....y......",
    "..y.....y......",
]
BUNGEE = {"mapa": BUNGEE_MAPA, "sombrero": [(CASCO_BUNGEE, 0, -1)], "torso_extra": [(ARNES, 0, 0)]}


def bungee_bajar():
    """4 frames: colgado cabeza abajo de la soga, pataleando y manoteando (el dibujo dado vuelta)."""
    out = []
    for i in range(4):
        p = pose(bob=0, piernas=((2, 6), (7, 3), (6, 2), (3, 7))[i], brazo=(0, (0, 2, 0, -1)[i]),
                 brazo_atras=(0, (2, 0, -1, 0)[i]), boca="abierta" if i % 2 else "normal")
        f = anim(BUNGEE, [p])[0]
        out.append(pygame.transform.flip(f, False, True))
    return out


# ------------------------------------------------------------------ 9. Mini zombie: enano de jardín
MINI_W, MINI_H = 20, 32
MINI_MAPA = {"3": "c", "4": "C"}
MINI_GORRO = [
    "..##.......",
    ".#rr#......",
    "..#rr#.....",
    "..#rrR#....",
    "..#rrRR#...",
    ".#rrrrRR#..",
    ".#rrrrrRR#.",
    "#rrrrrrRRR#",
    "#rrrrrrRRR#",
]
MINI_CABEZA = [
    "###########",
    "#kkkkkkkKK#",
    "#heekeehKK#",
    "#eeekeeeKK#",
    "#kkkkkkkKK#",
    "#wwwwwkKKK#",
    "#wewwwwsKK#",
    ".#wwwwwss#.",
    "..#wwwss#..",
    "...#wss#...",
    "....##.....",
]
MINI_BOCAS = {"normal": ("#wewwwwsKK#", ".#wwwwwss#."), "abierta": ("#eeewwwsKK#", ".#eewwwss#."),
              "muerde": ("#w#wwwwsKK#", ".#wwwwwss#."), "mastica": ("#weewwwsKK#", ".#wwwwwss#.")}
MINI_TORSO = [
    "..######..",
    ".#bbbbbB#.",
    "#bbbbbbBB#",
    "#bbbbbbBB#",
    "#NNNyNNNN#",
    "#bbbbbbBB#",
    ".#cccccC#.",
    "..######..",
]
MINI_BRAZO = [
    "....###.",
    ".###bbB#",
    "#kk#BB#.",
    "#k#k##..",
    ".#.#....",
]
MINI_PIERNAS = [
    ["...#cC#.", "..#cC#..", ".#cC#...", ".#nN#...", "#nnnN#..", "######.."],
    ["...#cC#.", "..#cCC#.", "..#cC#..", "..#nN#..", ".#nnnN#.", ".######."],
    ["...#cC#.", "...#cC#.", "...#cC#.", "..#nnN#.", ".#nnnN#.", ".######."],
    ["...#cC#.", "....#cC#", "....#cC#", "....#nN#", "...#nnN#", "...#####"],
    ["...#cC#..", "....#cC#.", ".....#cC#", "....#nnN#", "....####.", "........."],
    ["...#cC#.", "...#cCC#", "....#cC#", "...#nnN#", "....###..", "........"],
    ["...#cC#.", "...#cC#.", "..#cC#..", ".#nnN#..", "#nnnN#..", "######.."],
    ["...#cC#.", "..#cC#..", ".#cC#...", "#nnN#...", "######..", "........"],
]


def mini_capas(i=0, boca="normal", cdx=0, cdy=0, bdx=0, bob=0, piernas=None, ox=0, oy=0):
    """Capas del enano (frame 20x32, pies en la fila 31)."""
    a, b = piernas if piernas else (i % 8, (i + 4) % 8)
    m1, m2 = MINI_BOCAS[boca]
    cab = MINI_CABEZA[:6] + [m1, m2] + MINI_CABEZA[8:]
    return [
        (MINI_BRAZO, 5 + bdx + ox, 20 + bob + oy, True),
        (MINI_PIERNAS[b], 8 + ox, 26 + oy, True),
        (MINI_TORSO, 6 + ox, 19 + bob + oy),
        (MINI_PIERNAS[a], 5 + ox, 26 + oy),
        (MINI_GORRO, 4 + cdx + ox, 0 + cdy + bob + oy),
        (cab, 4 + cdx + ox, 9 + cdy + bob + oy),
        (MINI_BRAZO, 2 + bdx + ox, 21 + bob + oy),
    ]


def mini_caminar():
    return [frame(mini_capas(i, bob=(0, 1, 1, 0, 0, 1, 1, 0)[i], cdy=(0, 0, 1, 0, 0, 0, 1, 0)[i] * 0,
                             bdx=CAM_BRAZO_DX[i] // 1 if False else 0), MINI_MAPA, MINI_W, MINI_H) for i in range(8)]


def mini_atacar():
    seq = [("normal", 0, 0), ("abierta", -1, 0), ("abierta", -2, 1), ("muerde", -2, 1), ("mastica", -1, 0), ("normal", 0, 0)]
    return [frame(mini_capas(boca=m, cdx=dx, cdy=dy, bdx=dx, piernas=(0, 4)), MINI_MAPA, MINI_W, MINI_H)
            for m, dx, dy in seq]


# ------------------------------------------------------------------ 10. Gigante: leñador (frame 44x64)
GIG_W, GIG_H, GIG_OX = 44, 64, 4
CUADROS = ["1R1", "RNR", "1R1"]          # textura de la camisa escocesa
_g_cabeza = lambda boca: dup_filas(dup_cols(cabeza_con(boca, CABEZA), {10}), {3, 8})
GIG_CUERPO = {
    "pos": {"cabeza": (3, 10), "torso": (9, 25), "brazo_adelante": (0, 27), "brazo_atras": (5, 31),
            "pierna_adelante": (2, 43), "pierna_atras": (7, 43)},
    "piernas": [engordar(dup_filas(pp, {1, 6, 8, 10}), 2) for pp in PIERNAS],
    "bob": BOB,
    "torso": estampar(dup_filas(dup_cols(TORSO, {5, 6, 7}), {5, 6, 7, 8}), CUADROS, "12+=~^"),
    "brazo_adelante": dup_filas(dup_cols(BRAZO_ADELANTE, {10, 11}), {4}),
    "brazo_atras": dup_filas(dup_cols(BRAZO_ATRAS, {9, 10}), {3}),
    "cabeza": _g_cabeza,
}
GIG_MAPA = {"1": "r", "2": "R", "+": "r", "=": "R", "7": "r", "8": "R", "9": "k", "0": "K", "~": "r", "^": "R",
            "@": "N", "%": "R", "3": "b", "4": "B", "S": "b", "Z": "B", "5": "N", "6": "N", "H": "n"}
GORRO_LANA = [
    "......####.......",
    ".....#vvVV#......",
    "...##vvvvvVV##...",
    "..#vvvvvvvvvVV#..",
    ".#vvvvvvvvvvvVV#.",
    "#VvVvVvVvVvVvVVV#",
    "#################",
]
BARBA = [           # relativo a la cabeza del gigante (deja ver la boca)
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "...........nn...",
    "#nnnnnnnnnnnN#..",
    "#n.....nnnnNN#..",
    "#n.....nnnnNN#..",
    "#nn...nnnnnNN#..",
    ".#nnnnnnnnNN#...",
    "..#nnnnnnNN#....",
    "...##nnnN##.....",
    ".....###........",
]
TRONCO_V = [
    ".#####.",
    "#nnnnN#",
    "#nNnnN#",
    "#nnnNN#",
    "#nnnnN#",
    "#NnnnN#",
    "#nnnNN#",
    "#nnnnN#",
    "#nNnnN#",
    "#nnnnN#",
    "#nnnNN#",
    "#nnnnN#",
    "#nnNnN#",
    "#nnnnN#",
    "#nnnNN#",
    "#ccccC#",
    "#cCccC#",
    ".#####.",
]
TRONCO_H = rotar_der(TRONCO_V)
GIGANTE = {"cuerpo": GIG_CUERPO, "mapa": GIG_MAPA, "sombrero": [(GORRO_LANA, -1, -4), (BARBA, 0, 0)]}
GIG_ARRIBA = dup_filas(engordar(BRAZO_ARRIBA, 1), {12, 13, 14})


def gig_mini(x, y):
    """El enano a caballito (quieto)."""
    return [(g, gx + x, gy + y) + tuple(r) for g, gx, gy, *r in mini_capas(0, piernas=(2, 6))]


def gigante_extra(p, mini=True, tronco="mano", mx=18, my=8):
    dx, dy = p["brazo"][0], p["bob"] + p["brazo"][1]
    ex = {"atras": gig_mini(mx, my + p["bob"]) if mini else []}
    if tronco == "mano":
        ex["adelante"] = [(TRONCO_V, -2 + dx, 33 + dy)]
    return ex


def gig_caminar_poses():
    return caminar_poses()


def gigante_golpe(mini=True):
    """6 frames: levanta el tronco por encima de la cabeza y aplasta la planta."""
    ps, exs = [], []
    datos = [  # bob, brazo de adelante, tronco
        (1, None, ("v", -2, 33)),
        (0, "arriba", ("h", 6, 1)),
        (0, "arriba", ("h", 8, 0)),
        (2, None, ("h", -6, 46)),
        (2, None, ("h", -6, 46)),
        (1, None, ("v", -2, 33)),
    ]
    for i, (bob, brazo, tr) in enumerate(datos):
        kw = dict(bt_grilla=GIG_ARRIBA, bt_pos=(15, 3)) if brazo else {}
        ps.append(pose(bob=bob, piernas=(1, 5) if bob == 2 else (2, 6), cabeza=(0, 1 if i in (3, 4) else 0),
                       boca="abierta" if i in (1, 2) else ("muerde" if i in (3, 4) else "normal"), i=i, **kw))
        exs.append(tr)

    def ex(p):
        i = p["i"]
        kind, x, y = exs[i]
        out = {"atras": gig_mini(18, 8 + p["bob"]) if mini else []}
        g = TRONCO_V if kind == "v" else TRONCO_H
        capa = (g, x, y + (p["bob"] if kind == "v" else 0))
        if kind == "h" and y < 10:
            out["atras"] = out["atras"] + [capa]
        else:
            out["adelante"] = [capa]
        if i == 4:
            out.setdefault("adelante", []).append((["a.a..a", ".a.aa."], -4, 58))
        return out
    return ps, ex


def gigante_lanzar():
    """6 frames: agarra al enano de la espalda, lo levanta por arriba de la cabeza y lo revolea."""
    ps = []
    for i in range(6):
        kw = dict(bt_grilla=GIG_ARRIBA, bt_pos=(15, 3)) if i in (1, 2, 3) else {}
        ps.append(pose(bob=(1, 0, 0, 2, 1, 1)[i], piernas=(2, 6) if i < 3 else (0, 4), i=i,
                       boca="abierta" if i in (2, 3) else "normal", cabeza=(0, 1 if i == 3 else 0), **kw))
    mini_pos = [(18, 8), (18, -2), (8, -9), (-16, 4), None, None]

    def ex(p):
        i = p["i"]
        out = {"adelante": [(TRONCO_V, -2 + p["brazo"][0], 33 + p["bob"])]}
        if mini_pos[i]:
            x, y = mini_pos[i]
            capas_mini = gig_mini(x, y + p["bob"])
            out["atras" if i < 2 else "sobre_cabeza"] = capas_mini
        return out
    return ps, ex


# ------------------------------------------------------------------ 11. Tractor: granjero (frame 56x48)
TRAC_W = 56
TRACTOR_MAPA = {"1": "b", "2": "B", "+": "r", "=": "R", "7": "r", "8": "R", "~": "b", "^": "B", "@": "B",
                "%": "t", "H": "n"}
SOMBRERO_PAJA = [
    "......#########.....",
    ".....#ccccccccC#....",
    ".....#ccccccCCC#....",
    ".....#rrrrrrRRR#....",
    "#####################",
    "#ccccccccccccccccCCC#",
    "#####################",
]
RUEDA_GRANDE = [
    ".......######.......",
    ".....##hhhhhh##.....",
    "....#hhhhhhhhhh#....",
    "...#hhh######hhh#...",
    "..#hh##yyyyyy##hh#..",
    ".#hh#yyyyyyyyyY#hh#.",
    ".#h#yyyyyyyyyyYY#h#.",
    "#hh#yyyyy##yyyYY#hh#",
    "#h#yyyyy#GG#yyyYY#h#",
    "#h#yyyy#GGgg#yyYY#h#",
    "#h#yyyy#Gggg#yyYY#h#",
    "#h#yyyyy#gg#yyYYY#h#",
    "#hh#yyyyy##yyYYY#hh#",
    ".#h#yyyyyyyyYYYY#h#.",
    ".#hh#YyyyyyYYYY#hh#.",
    "..#hh##YYYYYY##hh#..",
    "...#hhh######hhh#...",
    "....#hhhhhhhhhh#....",
    ".....##hhhhhh##.....",
    ".......######.......",
]
# Tacos de la cubierta y tuercas de la llanta: 4 posiciones que van girando
TACOS = [
    [(9, 1), (10, 1), (1, 9), (1, 10), (18, 9), (18, 10), (9, 18), (10, 18), (9, 5), (14, 9), (10, 14), (5, 10)],
    [(13, 1), (1, 6), (18, 13), (6, 18), (2, 13), (6, 1), (17, 6), (13, 18), (12, 6), (13, 12), (7, 13), (6, 7)],
    [(15, 3), (3, 4), (16, 15), (4, 16), (15, 4), (4, 3), (16, 16), (3, 15), (13, 7), (12, 13), (6, 12), (7, 6)],
    [(17, 6), (6, 1), (13, 18), (2, 13), (17, 13), (13, 1), (6, 18), (1, 6), (13, 9), (10, 13), (6, 10), (9, 6)],
]
RUEDA_CHICA = [
    "....####....",
    "..##hhhh##..",
    ".#hh####hh#.",
    ".#h#yyyy#h#.",
    "#h#yy##yY#h#",
    "#h#y#GG#Y#h#",
    "#h#y#Gg#Y#h#",
    "#h#yY##YY#h#",
    ".#h#YYYY#h#.",
    ".#hh####hh#.",
    "..##hhhh##..",
    "....####....",
]
TACOS_CHICA = [[(5, 1), (1, 6), (10, 5), (6, 10)], [(8, 2), (2, 3), (9, 8), (3, 9)],
               [(9, 4), (3, 2), (8, 9), (2, 8)], [(9, 6), (5, 1), (2, 5), (6, 10)]]
CAPOT = [
    "...########################.....",
    "..#vvvvvvvvvvvvvvvvvvvvvvvvV#...",
    ".#yvvvvvvvvvvvvvvvvvvvvvvvvVV#..",
    "#yyvvvvvvvvvvvvvvvvvvvvvvvvVVV#.",
    "#g#vVvVvVvVvVvvvvvvvvvvvvvvVVV#.",
    "#g#vVvVvVvVvVvvvvvvvvvvvvvvVVV#.",
    "#g#vvvvvvvvvvvvvvvvvvvvvvvVVVV#.",
    "#g#VVVVVVVVVVVVVVVVVVVVVVVVVVV#.",
    "#g############################..",
    ".##.......................#VV#..",
    "..........................#V#...",
    "..........................###...",
]
GUARDABARRO = [
    "....################....",
    "..##vvvvvvvvvvvvvvvV##..",
    ".#vvvvvvvvvvvvvvvvvVVV#.",
    "#vvvvVVVVVVVVVVVVVVVVVV#",
    "#vV##################VV#",
    "#V#..................#V#",
    "##....................##",
]
ASIENTO = ["..#####.", ".#nnnnN#", ".#nnnnN#", ".#nnnnN#", "#nnnnnN#", "#NNNNNN#", "########"]
VOLANTE = [".#.", "#G#", "#G#", "#g#", ".#g#", "..#g#", "...#g#", "....#g#"]
CANO = ["###", "#g#", "#g#", "#g#", "#g#", "#g#", "#g#", "#g#", "#g#", "#g#"]
HUMO = [[".##.", "#aa#", "#aA#", ".##."], ["..##..", ".#aa#.", "#aaaA#", ".#AA#."]]


def rueda(g, tacos):
    g = [list(f) for f in g]
    for x, y in tacos:
        g[y][x] = "#" if g[y][x] == "h" else ("Y" if g[y][x] == "y" else g[y][x])
    return ["".join(f) for f in g]


def tractor_frame(i, sacude=0, bob=0, boca="normal", tierra=False, cabeza=(0, 0)):
    torso_g = TORSO[:11]
    cab = cabeza_con(boca, CABEZA)
    hx, hy = 28 + cabeza[0] + sacude, 1 + bob + cabeza[1]
    cs = [
        (rueda(RUEDA_GRANDE, TACOS[i % 4]), 34, 28),
        (GUARDABARRO, 31 + sacude, 23 + bob),
        (ASIENTO, 42 + sacude, 16 + bob),
        (torso_g, 34 + sacude, 13 + bob),
        (cab, hx, hy),
        (SOMBRERO_PAJA, hx - 3, hy - 4),
        (CANO, 12 + sacude, 16 + bob),
        (HUMO[i % 2], (11, 10, 12, 9)[i % 4], (11, 7, 4, 1)[i % 4]),
        (CAPOT, 1 + sacude, 26 + bob),
        (VOLANTE, 25 + sacude, 18 + bob),
        (BRAZO_ADELANTE, 23 + sacude, 16 + bob),
        (rueda(RUEDA_CHICA, TACOS_CHICA[i % 4]), 5, 36),
    ]
    if tierra:
        cs.append((["t.t..", ".t..t", "t..t."][i % 3:] + ["..t.t"], 0, 38 - (i % 3)))
    return frame(cs, TRACTOR_MAPA, TRAC_W, FRAME_H)


def tractor_caminar():
    return [tractor_frame(i, bob=i % 2) for i in range(8)]


def tractor_atacar():
    datos = [(0, "normal", (0, 0)), (-1, "abierta", (-1, 1)), (0, "abierta", (-2, 1)),
             (-1, "muerde", (-2, 2)), (0, "mastica", (-1, 1)), (-1, "normal", (0, 0))]
    return [tractor_frame(i * 2, sacude=s, bob=i % 2, boca=m, tierra=True, cabeza=c) for i, (s, m, c) in enumerate(datos)]


# ------------------------------------------------------------------ 12. Alien (dibujo de Santi): atacar
def alien_atacar():
    """6 frames a partir del primer frame de alien_caminar.png: se inclina, abre la boca, muerde,
    mastica y vuelve. El cuerpo no cambia; la cabeza baja y se corre hacia la planta."""
    hoja = pygame.image.load(os.path.join(RAIZ, "assets", "zombies", "alien_caminar.png")).convert_alpha()
    base = hoja.subsurface((0, 0, 31, 48)).copy()
    cabeza = base.subsurface((0, 0, 31, 17)).copy()
    cuerpo = base.copy()
    cuerpo.fill((0, 0, 0, 0), (0, 0, 31, 17))
    negro, ojo, blanco = (0, 0, 0), (24, 24, 28), (232, 232, 236)
    bocas = {
        "normal": [],
        "abierta": [(14, 11, negro), (15, 11, ojo), (16, 11, negro), (15, 12, negro)],
        "muerde": [(14, 11, negro), (15, 11, negro), (16, 11, negro)],
        "mastica": [(15, 11, ojo), (14, 11, negro)],
    }
    seq = [("normal", 0, 0, 0), ("abierta", -1, 1, -1), ("abierta", -2, 1, -2), ("muerde", -2, 2, -2),
           ("mastica", -1, 1, -1), ("normal", 0, 0, 0)]
    out = []
    for boca, dx, dy, brazo in seq:
        f = pygame.Surface((31, 48), pygame.SRCALPHA)
        c = cuerpo.copy()
        if brazo:   # levanta el brazo izquierdo (columnas 8-11) hacia la planta
            br = cuerpo.subsurface((8, 18, 4, 13)).copy()
            c.fill((0, 0, 0, 0), (8, 18, 3, 13))
            c.blit(br, (8 + brazo // 2, 18 + brazo))
        f.blit(c, (0, 0))
        h = cabeza.copy()
        for x, y, col in bocas[boca]:
            h.set_at((x, y), col)
        if boca != "normal":
            h.set_at((15, 11), bocas[boca][1][2] if boca == "abierta" else h.get_at((15, 11)))
        f.blit(h, (dx, dy))
        if dy:     # el cuello se estira: rellena el hueco entre la cabeza y el cuerpo
            for y in range(17, 17 + dy):
                for x, col in ((13, negro), (14, blanco), (15, blanco), (16, blanco), (17, negro)):
                    if f.get_at((x + dx // 2, y))[3] == 0:
                        f.set_at((x + dx // 2, y), col)
        out.append(f)
    return out


# ------------------------------------------------------------------ escalera apoyada (objeto del juego)
def escalera_puesta():
    larga = ESCALERA_V[:24] + ESCALERA_V[12:]
    return [frame([(larga, 6, 40 - len(larga))], ESCALERA_MAPA, 20, 40)]


# ------------------------------------------------------------------ todas las animaciones
def animaciones():
    """nombre de archivo -> (frames, fps)."""
    A = {}
    cam, atq = caminar_poses(), atacar_poses()

    def par(nombre, pj, extra=None, fps=(8, 10), **kw):
        A[nombre + "_caminar"] = (anim(pj, cam, extra, **kw), fps[0])
        A[nombre + "_atacar"] = (anim(pj, atq, extra, **kw), fps[1])

    par("zombie_normal", NORMAL)
    par("zombie_puerta", PUERTA, puerta_extra)
    par("zombie_puerta_sin", PUERTA)
    par("zombie_diario", DIARIO, diario_extra)
    par("zombie_diario_enojado", DIARIO_ENOJADO, fps=(12, 12))
    par("zombie_escalera", ESCALERA, escalera_extra)
    par("zombie_escalera_sin", ESCALERA)
    ps, ex = escalera_colocar()
    A["zombie_escalera_colocar"] = (anim(ESCALERA, ps, ex), 6)
    par("zombie_pertiga", PERTIGA, pertiga_extra, fps=(10, 10), w=PERTIGA_W, ox=PERTIGA_OX)
    par("zombie_pertiga_sin", PERTIGA_SIN)
    A["zombie_pertiga_salto"] = (pertiga_salto(), 7)
    par("zombie_excavador", EXCAVADOR, excavador_extra)
    par("zombie_excavador_sin", EXCAVADOR)
    A["zombie_excavador_tierra"] = (excavador_tierra(), 8)
    par("zombie_bailarin", BAILARIN)
    A["zombie_bailarin_baile"] = (anim(BAILARIN, bailarin_baile()), 8)
    par("zombie_bungee", BUNGEE)
    A["zombie_bungee_bajar"] = (bungee_bajar(), 8)
    A["zombie_mini_caminar"] = (mini_caminar(), 10)
    A["zombie_mini_atacar"] = (mini_atacar(), 12)
    g = dict(w=GIG_W, h=GIG_H, ox=GIG_OX)
    A["zombie_gigante_caminar"] = (anim(GIGANTE, cam, gigante_extra, **g), 6)
    A["zombie_gigante_sin_caminar"] = (anim(GIGANTE, cam, con_extra(gigante_extra, mini=False), **g), 6)
    ps, ex = gigante_golpe(True)
    A["zombie_gigante_golpe"] = (anim(GIGANTE, ps, ex, **g), 6)
    ps, ex = gigante_golpe(False)
    A["zombie_gigante_golpe_sin"] = (anim(GIGANTE, ps, ex, **g), 6)
    ps, ex = gigante_lanzar()
    A["zombie_gigante_lanzar"] = (anim(GIGANTE, ps, ex, **g), 8)
    A["zombie_tractor_caminar"] = (tractor_caminar(), 10)
    A["zombie_tractor_atacar"] = (tractor_atacar(), 12)
    A["alien_atacar"] = (alien_atacar(), 10)
    A["escalera_puesta"] = (escalera_puesta(), 1)
    return A


# ------------------------------------------------------------------ exportación y vistas previas
def preview_gif(nombre, frames, fps, escala=4):
    w, h = frames[0].get_size()
    W, H = w * escala + 16 * escala, h * escala + 8 * escala
    fondo = pasto(W, H, escala)
    out = []
    for f in frames:
        s = fondo.copy()
        s.blit(pygame.transform.scale(f, (w * escala, h * escala)), ((W - w * escala) // 2, H - h * escala - 4 * escala))
        out.append(s)
    guardar_gif(os.path.join(PREVIEW, nombre + ".gif"), out, int(1000 / fps))


def hoja_frames(A, salida, escala=3):
    """Todas las tiras, una abajo de la otra, sobre el pasto (para revisarlas pose por pose)."""
    filas = [(n, fr) for n, (fr, _) in A.items()]
    W = max(sum(f.get_width() + 4 for f in fr) for _, fr in filas) * escala
    H = sum(fr[0].get_height() + 4 for _, fr in filas) * escala
    hoja = pasto(W, H, escala)
    y = 0
    for _, fr in filas:
        x = 0
        for f in fr:
            hoja.blit(pygame.transform.scale(f, (f.get_width() * escala, f.get_height() * escala)), (x, y + 2 * escala))
            x += (f.get_width() + 4) * escala
        y += (fr[0].get_height() + 4) * escala
    pygame.image.save(hoja, salida)


def hoja_quietos(A, salida, escala=4):
    """Todos quietos (primer frame de caminar) junto al alien."""
    claves = [k for k in A if k.endswith("_caminar") and "_sin" not in k] + ["alien"]
    imgs = []
    for k in claves:
        if k == "alien":
            hoja = pygame.image.load(os.path.join(RAIZ, "assets", "zombies", "alien_caminar.png")).convert_alpha()
            imgs.append(hoja.subsurface((0, 0, 31, 48)).copy())
        else:
            imgs.append(A[k][0][0])
    W = sum(i.get_width() + 6 for i in imgs) * escala
    H = (max(i.get_height() for i in imgs) + 8) * escala
    s = pasto(W, H, escala)
    x = 0
    for i in imgs:
        s.blit(pygame.transform.scale(i, (i.get_width() * escala, i.get_height() * escala)),
               (x + 3 * escala, H - (i.get_height() + 4) * escala))
        x += (i.get_width() + 6) * escala
    pygame.image.save(s, salida)


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    forzar = "--forzar" in sys.argv
    os.makedirs(DEST, exist_ok=True)
    A = animaciones()
    for nombre, (frames, fps) in A.items():
        path = os.path.join(DEST, nombre + ".png")
        if forzar or not os.path.exists(path):
            pygame.image.save(tira(frames), path)
            print("creado:", os.path.relpath(path, RAIZ), "%dx%d, %d frames" % (*frames[0].get_size(), len(frames)))
    if "--preview" in sys.argv:
        os.makedirs(PREVIEW, exist_ok=True)
        for nombre, (frames, fps) in A.items():
            preview_gif(nombre, frames, fps)
        hoja_frames(A, os.path.join(PREVIEW, "todos_los_frames.png"))
        hoja_quietos(A, os.path.join(PREVIEW, "todos_quietos.png"))


if __name__ == "__main__":
    main()
