"""
Arma los sprites del zombie Chef (el que reemplaza al zombie con balde) a partir de los 3 dibujos
originales de tools/chef_fuente/ (cada uno trae 2 poses de Chef una al lado de la otra):
    chef_vader.png      Chef con la armadura y el casco de Darth Vader (estado inicial, catálogo)
    chef_sin_casco.png  Chef con la armadura pero sin casco (cuando pierde 1/3 de la armadura)
    chef_zombie.png     Chef zombie herido, sin armadura (sin armadura, o si lo toca el Imán)
Uso: python3 generar_chef.py [carpeta_fuente] [carpeta_de_salida]
Genera en assets/zombies/ (tiras horizontales, todos los frames del mismo tamaño y con los pies abajo):
    <estado>_idle.png      2 frames (las 2 poses), para el catálogo y la pantalla de equipo
    <estado>_caminar.png   4 frames de saltito (siempre de frente): se usa al avanzar y al comer
y assets/plantas/iman_cargado_vader.png (las 3 etapas del imán con la armadura pegada, en negro).
"""
import os
import sys
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
ESTADOS = ("chef_vader", "chef_sin_casco", "chef_zombie")
# Alturas del saltito (px de dibujo) en cada uno de los 4 frames, y qué pose se usa en cada uno.
SALTO_DY = (0, 5, 8, 3)
SALTO_POSE = (0, 1, 0, 1)
MARGEN_ARRIBA = max(SALTO_DY)


def partir(im):
    """Divide la imagen en sus 2 poses, cortando por la columna vacía más cercana al medio."""
    a = im.getchannel("A")
    vacias = [x for x in range(im.width) if a.crop((x, 0, x + 1, im.height)).getbbox() is None]
    medio = im.width / 2
    corte = min((x for x in vacias if 0.3 * im.width < x < 0.7 * im.width), key=lambda x: abs(x - medio))
    izq, der = im.crop((0, 0, corte, im.height)), im.crop((corte, 0, im.width, im.height))
    return [f.crop(f.getbbox()) for f in (izq, der)]


def lienzo(poses, w, h, dy=0):
    """Pega la pose centrada y con los pies en el fondo de un frame de w x h (dy = cuánto sube)."""
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(poses, ((w - poses.width) // 2, h - poses.height - dy), poses)
    return out


def tira(frames):
    out = Image.new("RGBA", (frames[0].width * len(frames), frames[0].height), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        out.paste(f, (i * f.width, 0))
    return out


def oscurecer_iman(src, dst):
    """El imán con la armadura pegada: el bloque gris del balde pasa a negro/gris oscuro de Vader."""
    im = Image.open(src).convert("RGBA")
    cargado = im.crop((6 * 40, 0, 9 * 40, 40))
    mapa = {(175, 180, 190): (40, 40, 46), (200, 205, 215): (70, 70, 78), (225, 228, 235): (96, 96, 106),
            (110, 115, 125): (22, 22, 26)}
    px = cargado.load()
    for y in range(cargado.height):
        for x in range(cargado.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in mapa:
                px[x, y] = (*mapa[(r, g, b)], a)
    cargado.save(dst)


def main(src, assets):
    dst = os.path.join(assets, "zombies")
    estados = {}
    for n in ESTADOS:
        estados[n] = partir(Image.open(os.path.join(src, n + ".png")).convert("RGBA"))
    w = max(p.width for ps in estados.values() for p in ps)
    h = max(p.height for ps in estados.values() for p in ps)
    for n, poses in estados.items():
        tira([lienzo(p, w, h + MARGEN_ARRIBA) for p in poses]).save(os.path.join(dst, n + "_idle.png"))
        tira([lienzo(poses[SALTO_POSE[i]], w, h + MARGEN_ARRIBA, SALTO_DY[i]) for i in range(4)]).save(
            os.path.join(dst, n + "_caminar.png"))
    print("frame:", w, "x", h + MARGEN_ARRIBA)
    oscurecer_iman(os.path.join(assets, "plantas", "iman_completo.png"),
                   os.path.join(assets, "plantas", "iman_cargado_vader.png"))


if __name__ == "__main__":
    base = os.path.dirname(AQUI)
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "chef_fuente"),
         sys.argv[2] if len(sys.argv) > 2 else os.path.join(base, "assets"))
