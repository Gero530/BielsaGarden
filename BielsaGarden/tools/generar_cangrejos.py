import math
import os
from PIL import Image

AQUI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "zombies", "propios")
FW, FH = 31, 48
CW, CH = 22, 36
GARRAS_FIN, CUERPO_FIN = 11, 22


def cargar():
    fuente = Image.open(os.path.join(AQUI, "cangrejos_fuente.png")).convert("RGBA")
    alfa = fuente.split()[3]
    cols = [x for x in range(fuente.width) if any(alfa.getpixel((x, y)) > 0 for y in range(fuente.height))]
    grupos, ini = [], cols[0]
    for a, b in zip(cols, cols[1:] + [None]):
        if b is None or b - a > 1:
            grupos.append((ini, a)); ini = b
    res = []
    for x0, x1 in grupos[:2]:
        caja = fuente.crop((x0, 0, x1 + 1, fuente.height)).getbbox()
        c = fuente.crop((x0, 0, x1 + 1, fuente.height))
        c = c.crop(c.getbbox())
        lienzo = Image.new("RGBA", (CW, CH))
        lienzo.alpha_composite(c, ((CW - c.width) // 2, CH - c.height))
        res.append(lienzo)
    return res


def mover(im, f):
    out = Image.new("RGBA", (CW, CH))
    src = im.load()
    dst = out.load()
    for y in range(CH):
        for x in range(CW):
            dx, dy = f(x, y)
            sx, sy = x - int(round(dx)), y - int(round(dy))
            if 0 <= sx < CW and 0 <= sy < CH and src[sx, sy][3] > 0:
                dst[x, y] = src[sx, sy]
    return out


def w_garra(y):
    return max(0.0, 1 - y / GARRAS_FIN) ** 1.0


def frame(im, ox=0, oy=0):
    lienzo = Image.new("RGBA", (FW, FH))
    lienzo.alpha_composite(im, ((FW - CW) // 2 + ox, FH - CH + oy))
    return lienzo


def tira(frames):
    out = Image.new("RGBA", (FW * len(frames), FH))
    for i, f in enumerate(frames):
        out.paste(f, (i * FW, 0))
    return out


def caminar(im, n=8):
    frames = []
    for i in range(n):
        fase = 2 * math.pi * i / n
        rebote = -1 if i % 4 in (1, 2) else 0

        def f(x, y, fase=fase):
            dx = dy = 0.0
            if y < GARRAS_FIN:
                lado = -1 if x < CW / 2 else 1
                dy = round(-w_garra(y) * (1 if math.sin(fase * lado) > 0.2 else 0))
                dx = round(lado * w_garra(y) * (1 if math.cos(fase) > 0.3 else 0))
            elif y >= CUERPO_FIN:
                lado = -1 if x < CW / 2 else 1
                prof = (y - CUERPO_FIN) / (CH - CUERPO_FIN)
                dx = round(math.sin(fase * lado) * 1.4 * prof)
            return dx, dy
        frames.append(frame(mover(im, f), 0, rebote))
    return frames


def atacar(im):
    pasos = ((0, 0, 0), (2, 1, 1), (3, 1, 2), (4, 2, 3), (3, 1, 2), (1, 0, 0))
    frames = []
    for adel, baja, abre in pasos:
        def f(x, y, adel=adel, abre=abre):
            if y < GARRAS_FIN:
                lado = -1 if x < CW / 2 else 1
                return -adel + lado * abre * w_garra(y), 0
            if y < CUERPO_FIN:
                return -adel, 0
            prof = (y - CUERPO_FIN) / (CH - CUERPO_FIN)
            return -adel * (1 - prof), 0
        frames.append(frame(mover(im, f), 0, baja))
    return frames


def bailar(im, n=8):
    frames = []
    for i in range(n):
        fase = 2 * math.pi * i / n
        sube = -2 if i % 4 == 1 else (-1 if i % 4 in (0, 2) else 0)

        def f(x, y, fase=fase):
            lado = -1 if x < CW / 2 else 1
            mece = math.sin(fase)
            if y < GARRAS_FIN:
                w = w_garra(y)
                return mece + mece * 1.5 * w, -math.sin(fase + (0 if lado < 0 else math.pi)) * 2 * w
            if y < CUERPO_FIN:
                return mece, 0
            prof = (y - CUERPO_FIN) / (CH - CUERPO_FIN)
            return mece * (1 - prof) + math.sin(fase * 2 * lado) * 1.2 * prof, 0
        frames.append(frame(mover(im, f), 0, sube))
    return frames


def main():
    rojo, marron = cargar()
    tira(caminar(rojo)).save(os.path.join(AQUI, "cangrejo_rojo_caminar.png"))
    tira(atacar(rojo)).save(os.path.join(AQUI, "cangrejo_rojo_atacar.png"))
    tira(bailar(rojo)).save(os.path.join(AQUI, "cangrejo_rojo_baile.png"))
    tira(caminar(marron)).save(os.path.join(AQUI, "cangrejo_marron_caminar.png"))
    tira(atacar(marron)).save(os.path.join(AQUI, "cangrejo_marron_atacar.png"))
    print("Listo: 5 tiras de cangrejos en", os.path.normpath(AQUI))


if __name__ == "__main__":
    main()
