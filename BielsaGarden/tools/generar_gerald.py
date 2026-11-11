"""
Genera los frames de Gerald Broflovski (el padre de Kyle, versión delfín) que reemplazan
al zombie del diario. Parte de assets/zombies/gerald_fuente/gerald_caminando.png
(2 frames de 32x47: izquierda = enojado sin bastón, derecha = caminando con bastón)
y arma tiras de 4 frames de 32x40 (los pies quedan en la última fila del frame):

  zombie_diario_caminar.png          caminar con bastón (suave)
  zombie_diario_atacar.png           comiendo con bastón
  zombie_diario_enojado_caminar.png  enojado: inclinado hacia adelante, saltitos más grandes
  zombie_diario_enojado_atacar.png   enojado comiendo

Uso:  python tools/generar_gerald.py
"""
import os
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(AQUI), "assets", "zombies")
FUENTE = os.path.join(ASSETS, "gerald_fuente", "gerald_caminando.png")
SALIDA = os.path.join(ASSETS, "propios")

FW, FH = 32, 40          # tamaño de cada frame final
Y0 = 3                   # fila de la fuente que pasa a ser la fila 0 (se recorta el aire de arriba)
CORTE = 26               # filas de la fuente por encima de esto = cabeza y torso; debajo = piernas


def cargar():
    src = Image.open(FUENTE).convert("RGBA")
    enojado = src.crop((0, 0, 32, 47))
    bastón = src.crop((32, 0, 64, 47))
    # el bastón = lo que tiene el frame con bastón y no el enojado
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
    """Pega las filas [y_desde, y_hasta) de img en dst, corridas (dx, dy), recortando el aire de arriba."""
    parte = img.crop((0, y_desde, 32, y_hasta))
    dst.alpha_composite(parte, (0, 0)) if False else None
    dst.paste(parte, (dx, y_desde - Y0 + dy), parte)


def frame(base, sup_dx=0, inf_dx=0, dy=0, baston=None, b_dx=0, b_dy=0):
    """base: imagen 32x47 del cuerpo. sup_dx: corrimiento de cabeza+torso; inf_dx: de las piernas;
    dy: salto de todo el cuerpo (negativo = sube). baston: imagen sólo del bastón."""
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

    # Caminar con bastón: el bastón se apoya adelante, el cuerpo se balancea hasta él, lo levanta y repite
    caminar = [
        frame(cuerpo, 0, 0, 0, baston, -2, 0),
        frame(cuerpo, -1, 0, -1, baston, -1, -1),
        frame(cuerpo, 0, 0, 0, baston, 0, 0),
        frame(cuerpo, 0, 1, -1, baston, -2, -2),
    ]
    tira(caminar, "zombie_diario_caminar.png")

    # Comiendo con bastón: se inclina hacia adelante y muerde en el lugar (el bastón queda apoyado)
    atacar = [
        frame(cuerpo, 0, 0, 0, baston, 0, 0),
        frame(cuerpo, -1, 0, 0, baston, 0, 0),
        frame(cuerpo, -2, 0, 0, baston, 0, 0),
        frame(cuerpo, -1, 0, -1, baston, 0, 0),
    ]
    tira(atacar, "zombie_diario_atacar.png")

    # Enojado: se tira hacia adelante y va a saltos más grandes (sin bastón)
    corre = [
        frame(enojado, -2, 0, 0),
        frame(enojado, -3, 1, -2),
        frame(enojado, -2, -1, 0),
        frame(enojado, -3, 0, -2),
    ]
    tira(corre, "zombie_diario_enojado_caminar.png")

    # Enojado comiendo: muerde con ganas (más movimiento que el de bastón)
    muerde = [
        frame(enojado, -1, 0, 0),
        frame(enojado, -3, 0, -1),
        frame(enojado, -4, 0, 0),
        frame(enojado, -2, 0, -1),
    ]
    tira(muerde, "zombie_diario_enojado_atacar.png")


if __name__ == "__main__":
    main()
