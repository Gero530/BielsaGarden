"""
Arma los sprites de Pip (Philip Pirrup) a partir de los dibujos originales (2 frames de 50x50 cada uno).
Uso: python3 generar_pip.py <carpeta_con_pip_idle.png_y_pip_caminando.png> <carpeta_assets_zombies>
  (normalmente: python3 tools/generar_pip.py assets/zombies/pip_fuente assets/zombies)
Genera:
  zombies/pip_idle.png            2 frames 24x25, de frente (catálogo y pantalla de equipo)
  zombies/propios/pip_caminar.png 4 frames 28x26, de perfil mirando a la DERECHA (caminando)
  zombies/propios/pip_atacar.png  6 frames 28x26, de perfil mirando a la DERECHA (comiendo plantas)
El perfil sale del 2do frame de pip_caminando.png: solo se mueve (rebote, pasos y cabezazo hacia adelante).
"""
import sys, os
from PIL import Image

SRC = 50                      # tamaño de cada frame original
PW, PH = 28, 26               # tamaño de cada frame de perfil
PERFIL = (24, 24, 43, 46)     # recuadro del perfil dentro de su frame original (x0, y0, x1, y1)
Y_PIES = 44                   # filas de pantalón y zapatos (relativas al frame original)
Y_CUELLO = 39                 # desde acá para abajo: remera y piernas; arriba: gorro y cabeza


def frame(im, i):
    return im.crop((i * SRC, 0, (i + 1) * SRC, SRC))


def fila(im, y):
    return im.crop((0, y, im.width, y + 1))


def componer(base, tramos, relleno=()):
    """base: perfil recortado (19x22). tramos: [(y0, y1, dx, dy)] filas de la base y cuánto se corren.
    relleno: filas (de la base) que se duplican para tapar los huecos que deja el rebote."""
    lienzo = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    ox, oy = 4, PH - base.height          # pies apoyados en la última fila
    for y0, y1, dx, dy in tramos:
        for y in range(y0, y1):
            lienzo.alpha_composite(fila(base, y), (ox + dx, oy + y + dy))
    for y, dx, dy in relleno:
        lienzo.alpha_composite(fila(base, y), (ox + dx, oy + y + dy))
    return lienzo


def mitades(base, y0, y1, dx_atras, dx_adelante):
    """Piernas: la mitad de atrás (izquierda) y la de adelante (derecha) se corren distinto."""
    m = base.width // 2 + 1
    out = []
    for y in range(y0, y1):
        izq = base.crop((0, y, m, y + 1))
        der = base.crop((m, y, base.width, y + 1))
        out.append((y, izq, der))
    return out


def con_pasos(base, y_cuerpo, dx_atras, dx_adelante, dy_cuerpo, dx_cuerpo=0):
    lienzo = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    ox, oy = 4, PH - base.height
    h = base.height
    y_pies = Y_PIES - PERFIL[1]
    # cuerpo (todo lo de arriba de los pies)
    for y in range(0, y_pies):
        lienzo.alpha_composite(fila(base, y), (ox + dx_cuerpo, oy + y + dy_cuerpo))
    if dy_cuerpo < 0:                      # el cuerpo sube: se estira la fila de abajo para no dejar hueco
        for k in range(-dy_cuerpo):
            lienzo.alpha_composite(fila(base, y_pies - 1), (ox + dx_cuerpo, oy + y_pies - 1 + k + 1 + dy_cuerpo))
    # pies
    for y, izq, der in mitades(base, y_pies, h, dx_atras, dx_adelante):
        lienzo.alpha_composite(izq, (ox + dx_atras, oy + y))
        lienzo.alpha_composite(der, (ox + base.width // 2 + 1 + dx_adelante, oy + y))
    return lienzo


def caminar(base):
    return [
        con_pasos(base, 0, -1, 1, 0, 0),      # paso: piernas abiertas
        con_pasos(base, 0, 0, 0, -1, 0),      # pasa una pierna: el cuerpo sube
        con_pasos(base, 0, 1, -1, 0, 0),      # paso con la otra pierna
        con_pasos(base, 0, 0, 0, -1, 0),      # el cuerpo vuelve a subir
    ]


def atacar(base):
    """Cabezazo hacia adelante (como el mordisco del zombie normal): la cabeza se estira y vuelve."""
    y_cuello = Y_CUELLO - PERFIL[1]
    y_pies = Y_PIES - PERFIL[1]
    cabeza = (0, 1, 2, 3, 2, 1)
    baja = (0, 0, 1, 1, 1, 0)
    out = []
    for dx, dy in zip(cabeza, baja):
        out.append(componer(base, [
            (0, y_cuello, dx, dy),                 # gorro y cabeza
            (y_cuello, y_pies, dx // 2, 0),         # remera
            (y_pies, base.height, 0, 0),            # pies quietos
        ]))
    return out


def tira(frames, w, h):
    out = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        out.paste(f, (i * w, 0))
    return out


def main(src, dst):
    prop = os.path.join(dst, "propios")
    os.makedirs(prop, exist_ok=True)
    idle = Image.open(os.path.join(src, "pip_idle.png")).convert("RGBA")
    cam = Image.open(os.path.join(src, "pip_caminando.png")).convert("RGBA")
    # catálogo: Pip de frente, 2 frames recortados al dibujo (los pies en la última fila)
    tira([frame(idle, i).crop((12, 22, 36, 47)) for i in range(2)], 24, 25).save(os.path.join(dst, "pip_idle.png"))
    base = frame(cam, 1).crop(PERFIL)
    tira(caminar(base), PW, PH).save(os.path.join(prop, "pip_caminar.png"))
    tira(atacar(base), PW, PH).save(os.path.join(prop, "pip_atacar.png"))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
