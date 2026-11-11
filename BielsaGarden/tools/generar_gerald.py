import os
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(AQUI), "assets", "zombies")
FUENTE = os.path.join(ASSETS, "gerald_fuente", "gerald_caminando.png")
SALIDA = os.path.join(ASSETS, "propios")

FW, FH = 32, 40
Y0 = 3
CORTE = 26


def cargar():
    src = Image.open(FUENTE).convert("RGBA")
    enojado = src.crop((0, 0, 32, 47))
    bastón = src.crop((32, 0, 64, 47))
    pb, pe = bastón.load(), enojado.load()
    solo_bastón = Image.new("RGBA", (32, 47), (0, 0, 0, 0))
    cuerpo = bastón.copy()
    ps, pc = solo_bastón.load(), cuerpo.load()
    for y in range(47):
        for x in range(32):
            if pb[x, y][3] and pb[x, y] != pe[x, y] and x <= 14 and y >= 28:
                ps[x, y] = pb[x, y]
                pc[x, y] = (0, 0, 0, 0)
    return enojado, cuerpo, solo_bastón


def pegar(dst, img, dx, dy, y_desde=0, y_hasta=47):
    parte = img.crop((0, y_desde, 32, y_hasta))
    dst.alpha_composite(parte, (0, 0)) if False else None
    dst.paste(parte, (dx, y_desde - Y0 + dy), parte)


def frame(base, sup_dx=0, inf_dx=0, dy=0, baston=None, b_dx=0, b_dy=0):
    out = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    pegar(out, base, sup_dx, dy, 0, CORTE)
    pegar(out, base, inf_dx, dy, CORTE, 47)
    if baston is not None:
        pegar(out, baston, b_dx, b_dy, 0, 47)
    return out


def tira(frames, nombre):
    img = Image.new("RGBA", (FW * len(frames), FH), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        img.paste(f, (i * FW, 0))
    img.save(os.path.join(SALIDA, nombre))
    print("ok", nombre, img.size)


def main():
    enojado, cuerpo, baston = cargar()

    caminar = [
        frame(cuerpo, 0, 0, 0, baston, -2, 0),
        frame(cuerpo, -1, 0, -1, baston, -1, -1),
        frame(cuerpo, 0, 0, 0, baston, 0, 0),
        frame(cuerpo, 0, 1, -1, baston, -2, -2),
    ]
    tira(caminar, "zombie_diario_caminar.png")

    atacar = [
        frame(cuerpo, 0, 0, 0, baston, 0, 0),
        frame(cuerpo, -1, 0, 0, baston, 0, 0),
        frame(cuerpo, -2, 0, 0, baston, 0, 0),
        frame(cuerpo, -1, 0, -1, baston, 0, 0),
    ]
    tira(atacar, "zombie_diario_atacar.png")

    corre = [
        frame(enojado, -2, 0, 0),
        frame(enojado, -3, 1, -2),
        frame(enojado, -2, -1, 0),
        frame(enojado, -3, 0, -2),
    ]
    tira(corre, "zombie_diario_enojado_caminar.png")

    muerde = [
        frame(enojado, -1, 0, 0),
        frame(enojado, -3, 0, -1),
        frame(enojado, -4, 0, 0),
        frame(enojado, -2, 0, -1),
    ]
    tira(muerde, "zombie_diario_enojado_atacar.png")


if __name__ == "__main__":
    main()
