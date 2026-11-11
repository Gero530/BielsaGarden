import os
import struct
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import pygame

FRAME_W, FRAME_H = 31, 48

PALETA = {
    "#": (0, 0, 0),
    "w": (232, 232, 236), "s": (198, 200, 210),
    "e": (24, 24, 28), "h": (70, 70, 80),
    "g": (96, 102, 118), "G": (150, 156, 172),
    "y": (255, 236, 60), "q": (255, 170, 170), "x": (255, 40, 40), "u": (130, 255, 130),
    "k": (160, 188, 124), "K": (122, 150, 100),
    "n": (110, 80, 58), "N": (72, 52, 40),
    "c": (184, 160, 112), "C": (146, 124, 86),
    "z": (168, 150, 106),
    "b": (88, 112, 156), "B": (62, 80, 118),
    "r": (180, 66, 60), "R": (128, 44, 42),
    "p": (132, 108, 152), "P": (96, 78, 114),
    "f": (224, 150, 170), "F": (180, 112, 134),
    "Y": (204, 180, 40),
    "o": (226, 140, 60), "O": (172, 98, 40),
    "v": (110, 160, 80), "V": (74, 116, 56),
    "a": (170, 170, 172), "A": (124, 124, 128),
    "t": (120, 84, 50), "T": (88, 60, 36),
}
OSCURO = {"w": "s", "k": "K", "n": "N", "c": "C", "b": "B", "r": "R", "p": "P", "f": "F", "y": "Y",
          "o": "O", "v": "V", "a": "A", "G": "g", "t": "T", "z": "C", "q": "F"}

MAPA_BASE = {
    "1": "w", "2": "s",
    "3": "c", "4": "C",
    "S": "k", "Z": "K",
    "5": "p", "6": "P",
    "7": "k", "8": "K",
    "9": "k", "0": "K",
    "+": "k", "=": "K",
    "~": "k", "^": "K",
    "@": "N",
    "%": "z",
    "H": "N",
}

CABEZA = [
    "....#######.#..",
    "..##kkkkkkk##H#",
    ".#kkkkkkkkkKHH#",
    "#kkkkkkkkkKHHH#",
    "#kKKkkKKKkkKHH#",
    "#heekkeeehkkKH#",
    "#eeekkeeeekK#H#",
    "#keekkkeekKk#K#",
    "#kkkkkkkkkK##K#",
    "#kkkkkkkkkkKKK#",
    "#kkewekkkkkKKK#",
    ".#keeekkkkKKK#.",
    "..##kkkkKKK##..",
    "....#######....",
]


def con_boca(cabeza, filas):
    return cabeza[:9] + filas + cabeza[13:]


BOCAS = {
    "normal": None,
    "abierta": [
        "#kwewkkkkkkKKK#",
        "#keeeekkkkkKKK#",
        ".#eeeekkkkKKK#.",
        "..##eekkKKK##..",
    ],
    "muerde": [
        "#kkkkkkkkkkKKK#",
        "#kwwwkkkkkkKKK#",
        ".#k#kkkkkKKKK#.",
        "..##kkkkKKK##..",
    ],
    "mastica": [
        "#kkkkkkkkkkKKK#",
        "#kkeekkkkkKKKK#",
        ".#kweekkkKKKK#.",
        "..##kkkkKKK##..",
    ],
    "grita": [
        "#kwwwwkkkkkKKK#",
        "#keeeekkkkkKKK#",
        ".#keeekkkKKKK#.",
        "..##kkkkKKK##..",
    ],
}


def cabeza_con(boca="normal", cabeza=CABEZA):
    return cabeza if BOCAS.get(boca) is None else con_boca(cabeza, BOCAS[boca])


_TORSO_A = [
    "....#####......",
    "..##kkkkK##....",
    ".#kkkkkkkKK#...",
    ".#wkkkkkkKKK#..",
    "#wwwkkkwwsKKK#.",
    "#wwwwwwwwwsKK#.",
    "#wwzwwwwwwwsK#.",
    "#wzzwwwwwwwss#.",
    ".#wwwwwwwwwss#.",
    ".#swwwwwwwss#..",
    ".#s#ws#ss#s#...",
    ".#kkkkkkkKK#...",
    ".#NNNNNNNNN#...",
    ".#cccccccCC#...",
]
_A_RANURA = {"w": "1", "s": "2", "z": "%", "N": "@", "c": "3", "C": "4"}
TORSO = ["".join({"k": "~" if y == 11 else "+", "K": "^" if y == 11 else "="}.get(ch, _A_RANURA.get(ch, ch))
                 for ch in fila) for y, fila in enumerate(_TORSO_A)]


def mangas(grilla, codo, mano):
    out = []
    for fila in grilla:
        f = ""
        for x, ch in enumerate(fila):
            if ch in "kK" and x >= codo:
                ch = "7" if ch == "k" else "8"
            elif ch in "kK" and x >= mano:
                ch = "9" if ch == "k" else "0"
            f += ch
        out.append(f)
    return out


BRAZO_ADELANTE = mangas([
    "...........####.",
    ".........##kkkK#",
    ".......##kkkkKK#",
    "..#####kkkkKKK#.",
    ".#kkkkkkkKK###..",
    "#kkkkKKKK##.....",
    "#k#k#k###.......",
    ".#.#.#..........",
], 9, 5)
BRAZO_ATRAS = mangas([
    "...........###",
    "........###kkK#",
    "..######kkkkK#.",
    ".#kkkkkkkK###..",
    "#kkkkkK##......",
    "#k#k#k#........",
    ".#.#.#.........",
], 8, 4)

BOB = (1, 2, 1, 0, 1, 2, 1, 0)
PIERNAS = [
    [
        ".......#33334#",
        "......#333344#",
        "......#33344#.",
        ".....#333344#.",
        ".....#4#4#44#.",
        ".....#SSZ#....",
        "....#SSZ#.....",
        "....#SSZ#.....",
        "....#SSZ#.....",
        "...#SSZ#......",
        "...#SSZ#......",
        "...#SSZ#......",
        "..#SSZ#.......",
        "##5SSZ#.......",
        "#555556#......",
        ".######.......",
    ],
    [
        ".......#33334#",
        "......#333344#",
        ".....#333344#.",
        ".....#33344#..",
        "....#4#4#44#..",
        "....#SSZ#.....",
        "....#SSZ#.....",
        "....#SSZ#.....",
        ".....#SSZ#....",
        ".....#SSZ#....",
        ".....#SSZ#....",
        ".....#SSZ#....",
        "...##SSSZ#....",
        "..#5555556#...",
        "...########...",
    ],
    [
        ".......#33334#.",
        ".......#333344#",
        ".......#33334#.",
        "......#333344#.",
        "......#4#4#4#..",
        ".......#SSZ#...",
        ".......#SSZ#...",
        ".......#SSZ#...",
        "......#SSZ#....",
        "......#SSZ#....",
        "......#SSZ#....",
        "......#SSZ#....",
        "......#SSZ#....",
        "....##SSSZ#....",
        "...#5555556#...",
        "....########...",
    ],
    [
        ".......#33334#..",
        ".......#333344#.",
        "........#33344#.",
        "........#333344#",
        "........#4#4#4#.",
        ".........#SSZ#..",
        ".........#SSZ#..",
        "..........#SSZ#.",
        "..........#SSZ#.",
        "..........#SSZ#.",
        "..........#SSZ#.",
        "...........#SSZ#",
        "...........#SSZ#",
        "..........##SSZ#",
        ".........#55556#",
        "........#555566#",
        ".........######.",
    ],
    [
        ".......#33334#...",
        ".......#333344#..",
        "........#333344#.",
        "........#333344#.",
        ".........#4#4#4#.",
        "..........#SSZ#..",
        "..........#SSZ#..",
        "...........#SSZ#.",
        "...........#SSZ#.",
        "............#SSZ#",
        "............#SSZ#",
        "............#SSZ#",
        "............#SSZ#",
        "...........##SZ6#",
        "..........#5556#.",
        "...........####..",
    ],
    [
        ".......#33334#.",
        ".......#333344#",
        ".......#33334#.",
        ".......#333344#",
        ".......#4#4#4#.",
        "........#SSZ#..",
        "........#SSZZ#.",
        ".........#SSZ#.",
        "..........#SSZ#",
        "..........#SSZ#",
        "..........#SSZ#",
        ".........##SZ6#",
        "........#5556#.",
        ".........####..",
        "...............",
    ],
    [
        ".......#33334#.",
        ".......#333344#",
        "......#333344#.",
        "......#33344#..",
        "......#4#4#4#..",
        ".......#SSZ#...",
        ".......#SSZZ#..",
        "........#SSZ#..",
        "........#SSZ#..",
        ".......#SSZ#...",
        ".......#SSZ#...",
        "......#SSZ#....",
        "......#SSZ#....",
        "....##SSZ#.....",
        "...#55556#.....",
        "....######.....",
    ],
    [
        ".......#33334#",
        "......#333344#",
        ".....#333344#.",
        "....#333344#..",
        "....#4#4#44#..",
        "....#SSZ#.....",
        "....#SSZ#.....",
        "....#SSZ#.....",
        "...#SSZ#......",
        "...#SSZ#......",
        "...#SSZ#......",
        "..#SSZ#.......",
        "..#SSZ#.......",
        "##5SZ#........",
        "#55556#.......",
        ".#####........",
        "..............",
    ],
]

POS = {"cabeza": (2, 4), "torso": (8, 17), "brazo_adelante": (0, 19), "brazo_atras": (4, 23),
       "pierna_adelante": (0, 31), "pierna_atras": (4, 31)}

CAM_CABEZA_DY = (0, 1, 1, 0, 0, 1, 1, 0)
CAM_BRAZO_DX = (1, 1, 0, -1, -1, -1, 0, 1)
ATQ = [
    (0, (0, 0), "normal", (0, 0)),
    (-1, (-2, 1), "abierta", (-1, 0)),
    (-1, (-3, 1), "abierta", (-2, 0)),
    (-2, (-4, 2), "muerde", (-2, 1)),
    (-1, (-3, 1), "mastica", (-1, 1)),
    (0, (-1, 0), "normal", (0, 0)),
]
ATQ_BOB = 1
ATQ_PIERNAS = (0, 4)


def pintar(sup, capas, mapa=None, ox=0, oy=0):
    m = dict(MAPA_BASE)
    m.update(mapa or {})
    for capa in capas:
        grilla, px, py = capa[:3]
        osc = len(capa) > 3 and capa[3]
        for y, fila in enumerate(grilla):
            for x, ch in enumerate(fila):
                if ch == ".":
                    continue
                ch = m.get(ch, ch)
                if osc:
                    ch = OSCURO.get(ch, ch)
                X, Y = ox + px + x, oy + py + y
                if 0 <= X < sup.get_width() and 0 <= Y < sup.get_height():
                    sup.set_at((X, Y), PALETA[ch])


def frame(capas, mapa=None, w=FRAME_W, h=FRAME_H):
    sup = pygame.Surface((w, h), pygame.SRCALPHA)
    pintar(sup, capas, mapa)
    return sup


def tira(frames):
    w, h = frames[0].get_size()
    sup = pygame.Surface((w * len(frames), h), pygame.SRCALPHA)
    for i, f in enumerate(frames):
        sup.blit(f, (i * w, 0))
    return sup


def espejo_v(grilla):
    return list(reversed(grilla))


def rotar_der(grilla):
    w = max(len(f) for f in grilla)
    g = [f.ljust(w, ".") for f in grilla]
    return ["".join(g[len(g) - 1 - y][x] for y in range(len(g))) for x in range(w)]


def guardar_gif(path, frames, ms=100):
    colores, idx_frames = {}, []
    w, h = frames[0].get_size()
    for f in frames:
        idx = bytearray()
        for y in range(h):
            for x in range(w):
                c = tuple(f.get_at((x, y)))[:3]
                if c not in colores:
                    colores[c] = len(colores)
                idx.append(colores[c])
        idx_frames.append(idx)
    assert len(colores) <= 256, "demasiados colores para el GIF"
    bits = max(2, (len(colores) - 1).bit_length())
    pal = b"".join(bytes(c) for c in colores) + b"\0" * (3 * (2 ** bits - len(colores)))
    out = bytearray(b"GIF89a" + struct.pack("<HHBBB", w, h, 0xF0 | (bits - 1), 0, 0) + pal)
    out += b"!\xff\x0bNETSCAPE2.0\x03\x01\0\0\0"
    for idx in idx_frames:
        out += b"!\xf9\x04\x00" + struct.pack("<H", ms // 10) + b"\0\0"
        out += b"," + struct.pack("<HHHHB", 0, 0, w, h, 0) + bytes([bits])
        out += _sub_bloques(_lzw(idx, bits))
    out += b";"
    with open(path, "wb") as fh:
        fh.write(out)


def _lzw(datos, min_bits):
    clear, fin = 1 << min_bits, (1 << min_bits) + 1
    tabla = {bytes([i]): i for i in range(clear)}
    sig, ancho = fin + 1, min_bits + 1
    salida, acum, nbits = bytearray(), 0, 0

    def emitir(cod):
        nonlocal acum, nbits
        acum |= cod << nbits
        nbits += ancho
        while nbits >= 8:
            salida.append(acum & 255)
            acum >>= 8
            nbits -= 8

    emitir(clear)
    w = b""
    for b in datos:
        wc = w + bytes([b])
        if wc in tabla:
            w = wc
            continue
        emitir(tabla[w])
        if sig < 4095:
            tabla[wc] = sig
            sig += 1
            if sig > (1 << ancho) and ancho < 12:
                ancho += 1
        else:
            emitir(clear)
            tabla = {bytes([i]): i for i in range(clear)}
            sig, ancho = fin + 1, min_bits + 1
        w = bytes([b])
    if w:
        emitir(tabla[w])
    emitir(fin)
    if nbits:
        salida.append(acum & 255)
    return bytes(salida)


def _sub_bloques(datos):
    out = bytearray()
    for i in range(0, len(datos), 255):
        out += bytes([len(datos[i:i + 255])]) + datos[i:i + 255]
    return bytes(out) + b"\0"


_fondo = None


def pasto(w, h, escala):
    global _fondo
    if _fondo is None:
        _fondo = pygame.image.load(os.path.join(RAIZ, "assets", "fondos", "jardin.png")).convert()
    big = pygame.transform.scale(_fondo.subsurface((45, 49, 80, 40)), (80 * escala * 2, 40 * escala * 2))
    out = pygame.Surface((w, h))
    for x in range(0, w, big.get_width()):
        for y in range(0, h, big.get_height()):
            out.blit(big, (x, y))
    return out
