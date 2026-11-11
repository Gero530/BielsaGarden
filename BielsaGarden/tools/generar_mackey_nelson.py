"""
Genera los frames del Sr. Mackey (reemplaza al zombie gigante) y del Sr. Nelson (reemplaza al
mini zombie) a partir de los dibujos de assets/zombies/mackey_nelson_fuente/:

  mackey_caminando.png   2 frames de 20x38 (de frente / de perfil mirando a la izquierda)
  mrmackey_idle.png      2 frames de 20x38 (de frente, respira)
  srnelson_idle.png      3 frames de 24x27 (2 de frente + 1 de perfil mirando a la derecha)

Salida en assets/zombies/propios/ (los pies quedan en la última fila de cada frame):

  zombie_mackey_caminar.png        8 frames 36x64  Mackey caminando con Nelson sobre la cabeza
  zombie_mackey_sin_caminar.png    8 frames 36x64  Mackey caminando solo
  zombie_mackey_golpe.png          6 frames 36x64  pisotón con Nelson arriba (aplasta la planta)
  zombie_mackey_golpe_sin.png      6 frames 36x64  pisotón solo
  zombie_mackey_lanzar.png         6 frames 36x64  agarra a Nelson y lo revolea (lo suelta en el frame 3)
  zombie_nelson_caminar.png        8 frames 20x28  Nelson caminando (mirando a la izquierda)
  zombie_nelson_atacar.png         6 frames 20x28  Nelson mordiendo

Los dos miran a la izquierda. Los frames se ven x2 en el juego.

Uso:  python tools/generar_mackey_nelson.py
"""
import math
import os
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(AQUI), "assets", "zombies")
FUENTE = os.path.join(ASSETS, "mackey_nelson_fuente")
SALIDA = os.path.join(ASSETS, "propios")

NEGRO = (0, 0, 0, 255)
VERDE = (73, 185, 13, 255)
PIEL = (255, 222, 184, 255)
AZUL_PANT = (63, 63, 116, 255)
ZAPATO = (34, 32, 52, 255)
POLVO = (200, 190, 170, 255)

MW, MH = 36, 64          # frame de Mackey
CX = 18                  # columna del cuerpo de Mackey dentro del frame
PIES = MH - 1            # fila de los pies
M_OX = CX - 10           # el dibujo de Mackey tiene el cuerpo en la columna 10
M_OY = PIES - 37         # y los pies en la fila 37
NW, NH = 20, 28          # frame de Nelson (mini)


def cargar(nombre):
    return Image.open(os.path.join(FUENTE, nombre)).convert("RGBA")


def tira(frames):
    w, h = frames[0].size
    hoja = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        hoja.paste(f, (i * w, 0))
    return hoja


def pegar(dst, src, ox, oy):
    """Pega src sobre dst respetando la transparencia (todo o nada: es pixel art)."""
    ps, pd = src.load(), dst.load()
    for y in range(src.height):
        for x in range(src.width):
            if ps[x, y][3] > 0:
                X, Y = x + ox, y + oy
                if 0 <= X < dst.width and 0 <= Y < dst.height:
                    pd[X, Y] = (*ps[x, y][:3], 255)


def punto(img, x, y, color, solo_vacio=False):
    if 0 <= x < img.width and 0 <= y < img.height:
        if not solo_vacio or img.getpixel((x, y))[3] == 0:
            img.putpixel((x, y), color)


def linea(p0, p1):
    (x0, y0), (x1, y1) = p0, p1
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    return [(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)]


def miembro(img, puntos, color, punta=None, punta_n=0):
    """Dibuja un brazo o una pierna: línea de 1 px con contorno negro. Las últimas punta_n celdas
    van de color `punta` (mano o zapato)."""
    celdas = []
    for a, b in zip(puntos, puntos[1:]):
        for c in linea(a, b):
            if c not in celdas:
                celdas.append(c)
    for (x, y) in celdas:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            if (x + dx, y + dy) not in celdas:
                punto(img, x + dx, y + dy, NEGRO)
    for i, (x, y) in enumerate(celdas):
        c = punta if punta is not None and i >= len(celdas) - punta_n else color
        punto(img, x, y, c)


# ------------------------------------------------------------------ Mackey
def mackey_cuerpo():
    """Cabeza y torso de perfil (filas 0-25 del dibujo), sin la mano que traía dibujada."""
    src = cargar("mackey_caminando.png").crop((20, 0, 40, 38))
    cuerpo = src.crop((0, 0, 20, 26))
    for x in range(20):
        if cuerpo.getpixel((x, 24)) == PIEL:
            cuerpo.putpixel((x, 24), VERDE)
    return cuerpo


def nelson_perfil():
    """Nelson de perfil mirando a la IZQUIERDA (el dibujo original mira a la derecha)."""
    p = cargar("srnelson_idle.png").crop((48, 0, 72, 27))
    return p.transpose(Image.FLIP_LEFT_RIGHT)


def pierna(img, hx, hy, dx_pie, largo, color=AZUL_PANT, rodilla=None):
    """Pierna desde la cadera (hx, hy) hasta el piso; el pie se corre dx_pie. Con `rodilla`
    (x, y) la pierna se dobla (pisotón)."""
    pie = (hx + dx_pie, hy + largo)
    pts = [(hx, hy), rodilla, pie] if rodilla else [(hx, hy), pie]
    miembro(img, pts, color)
    # zapato: apunta hacia adelante (izquierda)
    for dx in (-2, -1, 0):
        punto(img, pie[0] + dx, pie[1], ZAPATO)
    punto(img, pie[0] - 3, pie[1], NEGRO)
    punto(img, pie[0] + 1, pie[1], NEGRO)
    for dx in (-2, -1, 0):
        punto(img, pie[0] + dx, pie[1] + 1, NEGRO)


def mackey_frame(dy=0, dx=0, pierna_f=0, pierna_t=0, brazos=None, nelson=None, extra=None,
                 rodilla_f=None, alzar_f=0):
    """Un frame completo de Mackey (36x64).
    dy/dx: corrimiento del torso y la cabeza (rebote / inclinación). pierna_f/pierna_t: cuánto
    se adelanta el pie de adelante y se atrasa el de atrás. brazos: lista de brazos; cada uno es una
    polilínea [hombro, (codo), mano] en coordenadas del dibujo de Mackey. nelson: (img, ox, oy) en coordenadas del frame.
    rodilla_f: rodilla de la pierna de adelante (la dobla). alzar_f: sube el pie de adelante."""
    f = Image.new("RGBA", (MW, MH), (0, 0, 0, 0))
    cadera = (10 + M_OX, 26 + M_OY + dy)
    largo = PIES - 1 - cadera[1]
    # pierna de atrás, pierna de adelante
    pierna(f, cadera[0] + 0, cadera[1], -pierna_t, largo)
    pierna(f, cadera[0] + 0, cadera[1], pierna_f, largo - alzar_f, rodilla=rodilla_f)
    pegar(f, mackey_cuerpo(), M_OX + dx, M_OY + dy)
    # Nelson (encima o en las manos)
    if nelson is not None:
        pegar(f, *nelson)
    for brazo in (brazos or []):
        pts = [(x + M_OX + dx, y + M_OY + dy) for x, y in brazo]
        miembro(f, pts, VERDE, punta=PIEL, punta_n=2)
    if extra:
        extra(f)
    return f


def nelson_sobre_cabeza(dy=0, dx=0, subir=0):
    """Nelson parado sobre la cabeza de Mackey (sigue su rebote)."""
    n = nelson_perfil()
    ox = CX - 11 + 1 + dx          # el cuerpo de Nelson (de perfil) queda sobre el centro de la cabeza
    oy = M_OY + 2 + dy - 23 - subir  # su fila 23 (pies) apoya sobre la fila 1-2 de la cabeza
    return (n, ox, oy)


SW = [0, 2, 3, 2, 0, -2, -3, -2]       # cuánto se abren las piernas en cada frame de caminar
REBOTE = [-1, 0, 0, 0, -1, 0, 0, 0]    # sube un pixel cuando las piernas se cruzan


def mackey_caminar(con_nelson):
    frames = []
    for i in range(8):
        s, dy = SW[i], REBOTE[i]
        brazo = [(10, 21), (10 - round(s * 0.7), 25)]     # el brazo se balancea al revés que las piernas
        nel = nelson_sobre_cabeza(dy) if con_nelson else None
        frames.append(mackey_frame(dy=dy, pierna_f=-s, pierna_t=-s, brazos=[brazo], nelson=nel))
    return tira(frames)


def mackey_golpe(con_nelson):
    """Pisotón: levanta la pierna de adelante, se inclina atrás y la clava (la planta muere al final)."""
    # (dy, dx, alzar, rodilla, dx_pie)
    poses = [
        (0, 0, 0, None, 0),
        (0, 0, 2, (7 + M_OX, 29 + M_OY), -2),
        (-1, 1, 5, (6 + M_OX, 29 + M_OY), -3),
        (-1, 1, 6, (5 + M_OX, 28 + M_OY), -4),
        (1, -1, 0, None, -5),
        (1, -1, 0, None, -5),
    ]
    frames = []
    for i, (dy, dx, alzar, rod, dxp) in enumerate(poses):
        nel = nelson_sobre_cabeza(dy, dx) if con_nelson else None
        brazo = [(10, 21), (10 + (1 if i in (2, 3) else -2 if i >= 4 else 0), 25 - (2 if i in (2, 3) else 0))]

        def polvo(img, i=i):
            if i == 5:
                for (x, y) in ((CX - 9, PIES - 1), (CX - 11, PIES), (CX - 7, PIES), (CX - 13, PIES - 1)):
                    punto(img, x, y, POLVO)

        pf = dxp
        f = mackey_frame(dy=dy, dx=dx, pierna_f=pf, pierna_t=1, brazos=[brazo], nelson=nel,
                         rodilla_f=rod, alzar_f=alzar, extra=polvo)
        frames.append(f)
    return tira(frames)


def mackey_lanzar():
    """Agarra a Nelson de la cabeza y lo revolea hacia adelante (izquierda). Frames 0-2 con
    Nelson, 3-5 sin él (el código lo suelta al empezar el frame 3)."""
    n = nelson_perfil()
    base_y = M_OY + 2 - 23          # oy de Nelson parado sobre la cabeza

    def nel(cx, subir):             # Nelson con su centro en la columna cx del dibujo de Mackey
        return (n, cx + M_OX - 11, base_y - subir)

    frames = [
        # 0: sube el brazo por delante de la cara y lo agarra de los pies
        mackey_frame(brazos=[[(9, 19), (0, 17), (1, 3)]], nelson=nel(7, 1)),
        # 1: lo levanta
        mackey_frame(dy=-1, brazos=[[(9, 19), (0, 16), (1, -3)]], nelson=nel(5, 7)),
        # 2: toma envión: se echa para atrás y lo lleva detrás de la cabeza
        mackey_frame(dy=-1, dx=1, pierna_t=2, pierna_f=-1,
                     brazos=[[(10, 19), (21, 16), (20, 0)]], nelson=nel(19, 4)),
        # 3: lo suelta: el brazo sale disparado hacia adelante
        mackey_frame(dx=-1, pierna_f=-3, pierna_t=2, brazos=[[(10, 19), (3, 14), (-5, 9)]]),
        # 4: sigue el movimiento
        mackey_frame(dy=1, dx=-1, pierna_f=-3, pierna_t=2, brazos=[[(10, 19), (2, 19), (-6, 20)]]),
        # 5: se endereza
        mackey_frame(pierna_f=-1, pierna_t=1, brazos=[[(10, 21), (9, 25)]]),
    ]
    return tira(frames)


# ------------------------------------------------------------------ Nelson
def nelson_frame(dy=0, dx_pie=0, empuje=0, dx_cab=0):
    """Nelson de perfil mirando a la izquierda en un frame de 20x28. empuje: lo que se tira
    hacia adelante al morder (la cabeza más que el torso)."""
    p = nelson_perfil()                      # 24x27; filas 4-23 tienen dibujo, pies en la 23
    f = Image.new("RGBA", (NW, NH), (0, 0, 0, 0))
    ox, oy = 10 - 12, NH - 1 - 23            # el centro de su cuerpo (columna 12) va a la columna 10
    cab = p.crop((0, 0, 24, 18))             # cabeza (filas 0-17)
    tor = p.crop((0, 18, 24, 22))            # torso con la mano (filas 18-21)
    pegar(f, tor, ox - empuje // 2, oy + 18 + dy)
    pegar(f, cab, ox - empuje + dx_cab, oy + dy)
    # piernas: dos patitas que se abren y se cierran
    hx, hy = 10, oy + 22 + dy
    for lado, c in ((1, -dx_pie), (0, dx_pie)):
        x = hx + c + (0 if lado else 0)
        for X in (x - 2, x - 1, x, x + 1):
            punto(f, X, hy, (179, 171, 149, 255) if X in (x - 1, x) else NEGRO)
            punto(f, X, hy + 1, (68, 64, 77, 255) if X in (x - 2, x - 1, x) else NEGRO)
    return f


def nelson_caminar():
    frames = []
    for i in range(8):
        s = SW[i] // 2 if SW[i] % 2 == 0 else SW[i] // 2 + (1 if SW[i] > 0 else -1)
        frames.append(nelson_frame(dy=-1 if i in (0, 4) else 0, dx_pie=s))
    return tira(frames)


def nelson_atacar():
    lung = [0, 2, 4, 6, 4, 1]
    return tira([nelson_frame(dy=0, dx_pie=0, empuje=l) for l in lung])


# ------------------------------------------------------------------ main
def main():
    os.makedirs(SALIDA, exist_ok=True)
    salidas = {
        "zombie_mackey_caminar.png": lambda: mackey_caminar(True),
        "zombie_mackey_sin_caminar.png": lambda: mackey_caminar(False),
        "zombie_mackey_golpe.png": lambda: mackey_golpe(True),
        "zombie_mackey_golpe_sin.png": lambda: mackey_golpe(False),
        "zombie_mackey_lanzar.png": mackey_lanzar,
        "zombie_nelson_caminar.png": nelson_caminar,
        "zombie_nelson_atacar.png": nelson_atacar,
    }
    for nombre, fn in salidas.items():
        hoja = fn()
        hoja.save(os.path.join(SALIDA, nombre))
        print(f"{nombre}: {hoja.width}x{hoja.height}")


if __name__ == "__main__":
    main()
