import os
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTE = os.path.join(RAIZ, "assets", "zombies", "randy_fuente", "randy.png")
SALIDA = os.path.join(RAIZ, "assets", "zombies", "propios")

FW, FH = 21, 38
Y0, Y1 = 14, 50
POSES = {
    "frente_normal": (5, 21),   "perfil_normal": (29, 43),
    "frente_mascara": (55, 71), "perfil_mascara": (79, 93),
    "frente_spider": (105, 121), "perfil_spider": (129, 143),
}
CAMINAR = [(0, 0), (0, -1), (0, -1), (0, 0)]
ATACAR = [(0, 0), (-1, 0), (-2, 0), (-2, -1), (-1, 0), (0, 0)]


def recortar(hoja, nombre):
    x0, x1 = POSES[nombre]
    return hoja.crop((x0, Y0, x1 + 1, Y1))


def frame(pose, dx=0, dy=0):
    f = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    f.alpha_composite(pose, ((FW - pose.width) // 2 + dx, FH - pose.height + dy))
    return f


def tira(frames, nombre):
    img = Image.new("RGBA", (FW * len(frames), FH), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        img.paste(f, (i * FW, 0))
    img.save(os.path.join(SALIDA, nombre))


def main():
    hoja = Image.open(FUENTE).convert("RGBA")
    tira([frame(recortar(hoja, "frente_" + e)) for e in ("normal", "mascara", "spider")], "randy_frente.png")
    for e in ("spider", "mascara", "normal"):
        p = recortar(hoja, "perfil_" + e)
        tira([frame(p, dx, dy) for dx, dy in CAMINAR], "randy_%s_caminar.png" % e)
        tira([frame(p, dx, dy) for dx, dy in ATACAR], "randy_%s_atacar.png" % e)
    print("Sprites de Randy generados en", SALIDA)


if __name__ == "__main__":
    main()
