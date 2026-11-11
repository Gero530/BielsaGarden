import math
import os
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTE = os.path.join(RAIZ, "assets", "zombies", "trent_fuente")
PROPIOS = os.path.join(RAIZ, "assets", "zombies", "propios")
ZOMBIES = os.path.join(RAIZ, "assets", "zombies")

W, H = 56, 44
CX = 28
G = H - 1

NEGRO = (0, 0, 0, 255)
PIEL = (255, 222, 184, 255)
MANGA = (198, 50, 50, 255)
MANGA_OSC = (150, 24, 28, 255)
PANT = (80, 64, 75, 255)
MAD_CLARA = (184, 160, 112, 255)
MAD_OSC = (146, 124, 86, 255)


def capa():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def poner(img, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        img.putpixel((x, y), c)


def linea(img, x0, y0, x1, y1, c, grosor=1):
    n = max(abs(x1 - x0), abs(y1 - y0), 1) * 2
    for k in range(n + 1):
        x = round(x0 + (x1 - x0) * k / n)
        y = round(y0 + (y1 - y0) * k / n)
        for dx in range(grosor):
            for dy in range(grosor):
                poner(img, x + dx, y + dy, c)


def contorno(img, c=NEGRO):
    out = img.copy()
    px = img.load()
    for y in range(H):
        for x in range(W):
            if px[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and px[nx, ny][3]:
                    out.putpixel((x, y), c)
                    break
    return out


def pegar(base, otra):
    base.alpha_composite(otra)


_perfil = Image.open(os.path.join(FUENTE, "trent_caminando.png")).convert("RGBA").crop((50, 0, 100, 50))
CABEZA = _perfil.crop((4, 24, 23, 41))
TORSO = _perfil.crop((4, 41, 23, 48))
ARRIBA_X = CX - 9


def pierna(img, x, y, alzada=0):
    y -= alzada
    for j in range(3):
        poner(img, x, y + j, NEGRO)
        poner(img, x + 4, y + j, NEGRO)
        for i in range(1, 4):
            poner(img, x + i, y + j, PANT)
    for i in range(5):
        poner(img, x + i, y + 3, NEGRO)
    poner(img, x - 1, y + 3, NEGRO)


def cuerpo(bob=0, dx=0, piernas=(0, 0), alzadas=(0, 0), lado="izq"):
    abajo = capa()
    y_hem = G - 4 - bob
    pierna(abajo, CX - 4 + dx + piernas[1] - 0, G - 3, alzadas[1])
    pierna(abajo, CX - 4 + dx + piernas[0], G - 3, alzadas[0])
    abajo.alpha_composite(TORSO, (ARRIBA_X + dx, y_hem - 6))
    cab = capa()
    cab.alpha_composite(CABEZA, (ARRIBA_X + dx, y_hem - 6 - CABEZA.height))
    return abajo, cab


def hombro(bob=0, dx=0):
    return CX - 1 + dx, G - 4 - bob - 5


def brazo(img, hombro_xy, mano_xy, c=MANGA):
    sx, sy = hombro_xy
    mx, my = mano_xy
    linea(img, sx, sy, mx, my, c, grosor=2)
    for i in range(2):
        for j in range(2):
            poner(img, mx + i, my + j, PIEL)


def mano_con_borde(img, mx, my):
    mano = capa()
    for i in range(2):
        for j in range(2):
            poner(mano, mx + i, my + j, PIEL)
    pegar(img, contorno(mano))


def escalera(p0, p1, ancho=6, paso=4.0):
    c = capa()
    x0, y0 = p0
    x1, y1 = p1
    largo = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / largo, (y1 - y0) / largo
    nx, ny = -uy, ux
    hw = (ancho - 1) / 2
    pasos = int(largo * 3)
    for k in range(pasos + 1):
        t = k / pasos * largo
        bx, by = x0 + ux * t, y0 + uy * t
        for s in (-hw, hw):
            poner(c, round(bx + nx * s), round(by + ny * s), MAD_CLARA)
    k = paso / 2
    while k < largo:
        bx, by = x0 + ux * k, y0 + uy * k
        n = int(hw * 2 * 2)
        for q in range(n + 1):
            s = -hw + 2 * hw * q / n
            poner(c, round(bx + nx * s), round(by + ny * s), MAD_OSC)
        k += paso
    px = c.load()
    for y in range(H - 1):
        for x in range(W):
            if px[x, y] == MAD_CLARA and px[x, y + 1][3] == 0:
                c.putpixel((x, y), (160, 134, 90, 255))
    return contorno(c)


CICLO = [round(3 * math.cos(2 * math.pi * i / 8)) for i in range(8)]


def paso(i):
    a = CICLO[i]
    bob = 1 if i in (2, 6) else 0
    alz0 = 1 if i in (1, 2, 3) else 0
    alz1 = 1 if i in (5, 6, 7) else 0
    return a, bob, (alz0, alz1)


def escalera_horizontal(x0, y, largo=28, ancho=5):
    c = capa()
    for x in range(x0, x0 + largo):
        poner(c, x, y, MAD_CLARA)
        poner(c, x, y + ancho - 1, MAD_CLARA)
    for x in range(x0 + 2, x0 + largo, 4):
        for yy in range(y + 1, y + ancho - 1):
            poner(c, x, yy, MAD_OSC)
    return contorno(c)


def frame_caminar_con_escalera(i):
    a, bob, alz = paso(i)
    f = capa()
    abajo, cab = cuerpo(bob, 0, (a, -a), alz)
    pegar(f, abajo)
    sx, sy = hombro(bob)
    rebote = (0, 1, 1, 0, 0, 1, 1, 0)[i]
    mano = (CX - 9, sy + 1 - bob)
    esc = escalera_horizontal(CX - 16, sy - 2 - bob + rebote // 1)
    pegar(f, esc)
    pegar(f, cab)
    brazo(f, (sx, sy + 1 - bob), mano)
    mano_con_borde(f, *mano)
    return f


def frame_caminar_sin(i):
    a, bob, alz = paso(i)
    f = capa()
    sx, sy = hombro(bob)
    atras = capa()
    brazo(atras, (sx + 1, sy + 1 - bob), (sx + 1 + round(-a * 0.7), sy + 6 - bob + (abs(a) == 3)), MANGA_OSC)
    abajo, cab = cuerpo(bob, 0, (a, -a), alz)
    pegar(f, contorno(atras))
    pegar(f, abajo)
    pegar(f, cab)
    delante = capa()
    brazo(delante, (sx - 1, sy + 1 - bob), (sx - 1 + round(a * 0.7), sy + 6 - bob + (abs(a) == 3)))
    pegar(f, contorno(delante))
    return f


def frame_atacar(i, con_escalera=False):
    adelanta = (0, -1, -2, -3, -2, -1)[i]
    bob = (0, 0, 1, 0, 0, 1)[i]
    f = capa()
    abajo, cab = cuerpo(bob, adelanta, (-1, 2), (0, 0))
    sx, sy = hombro(bob, adelanta)
    puno = (-2, -4, -7, -9, -6, -3)[i]
    altura = (6, 3, 1, 1, 2, 4)[i]
    if con_escalera:
        pegar(f, abajo)
        esc = escalera_horizontal(CX - 16 + adelanta, sy - 2 - bob)
        pegar(f, esc)
        pegar(f, cab)
        mano = (CX - 9 + adelanta, sy + 1 - bob)
        brazo(f, (sx, sy + 1 - bob), mano)
        mano_con_borde(f, *mano)
        return f
    atras = capa()
    brazo(atras, (sx + 1, sy + 1 - bob), (sx + 4, sy + 5 - bob), MANGA_OSC)
    pegar(f, contorno(atras))
    pegar(f, abajo)
    pegar(f, cab)
    delante = capa()
    brazo(delante, (sx - 1, sy + 1 - bob), (sx - 1 + puno, sy + altura - bob))
    pegar(f, contorno(delante))
    return f


def frame_colocar(i):
    f = capa()
    bob = (0, 1, 0, 0, 1, 0)[i]
    avance = (0, -1, -2, -3, -3, -3)[i]
    piernas = ((1, -1), (-1, 3), (-2, 3), (-3, 3), (-3, 2), (-2, 1))[i]
    alz = ((0, 0), (1, 0), (0, 0), (0, 0), (0, 0), (0, 0))[i]
    abajo, cab = cuerpo(bob, avance, piernas, alz)
    sx, sy = hombro(bob, avance)
    sy = sy - bob
    ejes = [
        None,
        ((CX - 17, G - 25), (CX + 1, G - 7)),
        ((CX - 14, G - 31), (CX - 12, G - 3)),
        ((CX - 18, G - 32), (CX - 14, G - 1)),
        ((CX - 21, G - 32), (CX - 15, G)),
        ((CX - 21, G - 32), (CX - 15, G)),
    ]
    if ejes[i] is None:
        esc = escalera_horizontal(CX - 16, sy - 2)
    else:
        p0, p1 = ejes[i]
        esc = escalera(p0, p1, ancho=7 if i >= 2 else 6)
    manos = [
        (CX - 9, sy + 1), (CX - 10, sy - 1), (CX - 12, sy - 3), (CX - 17, sy - 6), (CX - 18, sy - 8),
        (CX - 11, sy + 4),
    ][i]
    if i <= 1:
        pegar(f, abajo)
        pegar(f, esc)
        pegar(f, cab)
    else:
        pegar(f, esc)
        pegar(f, abajo)
        pegar(f, cab)
    if i <= 4:
        brazo(f, (sx, sy + 1), manos)
        if i >= 2:
            mano_con_borde(f, *manos)
        else:
            mano_con_borde(f, *manos)
    else:
        brazo(f, (sx, sy + 1), manos)
    return f


def tira(frames):
    out = Image.new("RGBA", (W * len(frames), H), (0, 0, 0, 0))
    for k, fr in enumerate(frames):
        out.alpha_composite(fr, (W * k, 0))
    return out


def idle():
    src = Image.open(os.path.join(FUENTE, "trent_idle.png")).convert("RGBA")
    frames = [src.crop((50 * k + 2, 23, 50 * k + 26, 50)) for k in range(2)]
    out = Image.new("RGBA", (24 * 2, frames[0].height), (0, 0, 0, 0))
    for k, fr in enumerate(frames):
        out.alpha_composite(fr, (24 * k, 0))
    return out


def escalera_puesta():
    img = escalera((CX - 21, G - 32), (CX - 15, G), ancho=7)
    return img.crop(img.getbbox())


def main():
    salidas = {
        os.path.join(PROPIOS, "escalera_puesta.png"): escalera_puesta(),
        os.path.join(PROPIOS, "zombie_escalera_caminar.png"): tira([frame_caminar_con_escalera(i) for i in range(8)]),
        os.path.join(PROPIOS, "zombie_escalera_atacar.png"): tira([frame_atacar(i, True) for i in range(6)]),
        os.path.join(PROPIOS, "zombie_escalera_colocar.png"): tira([frame_colocar(i) for i in range(6)]),
        os.path.join(PROPIOS, "zombie_escalera_sin_caminar.png"): tira([frame_caminar_sin(i) for i in range(8)]),
        os.path.join(PROPIOS, "zombie_escalera_sin_atacar.png"): tira([frame_atacar(i) for i in range(6)]),
        os.path.join(ZOMBIES, "trent_idle.png"): idle(),
    }
    for ruta, img in salidas.items():
        img.save(ruta)
        print("listo:", os.path.relpath(ruta, RAIZ), img.size)


if __name__ == "__main__":
    main()
