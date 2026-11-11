import os
import sys
from PIL import Image

FW, FH = 44, 40
CX = 22
SKIN, BLK, PUR = (255, 222, 184, 255), (0, 0, 0, 255), (113, 35, 144, 255)
POLVO = (235, 235, 235, 255)
POLVO2 = (190, 190, 190, 255)


def vacio(w=FW, h=FH):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def pegar(dst, src, x, y):
    dst.alpha_composite(src, (x, y)) if x >= 0 and y >= 0 and x + src.width <= dst.width and y + src.height <= dst.height \
        else _pegar_recortado(dst, src, x, y)


def _pegar_recortado(dst, src, x, y):
    for j in range(src.height):
        for i in range(src.width):
            p = src.getpixel((i, j))
            if p[3] and 0 <= x + i < dst.width and 0 <= y + j < dst.height:
                dst.putpixel((x + i, y + j), p)


def tira(frames):
    out = vacio(frames[0].width * len(frames), frames[0].height)
    for i, f in enumerate(frames):
        out.paste(f, (i * f.width, 0))
    return out


def cargar_piezas(src):
    pf = Image.open(os.path.join(src, "perfil_y_frente.png")).convert("RGBA")
    perfil = pf.crop((0, 0, 52, 50))
    perfil = perfil.crop(perfil.getbbox())
    cabeza = perfil.crop((0, 0, perfil.width, 15))
    cuerpo = perfil.crop((0, 15, perfil.width, perfil.height))
    idle = Image.open(os.path.join(src, "frente_idle.png")).convert("RGBA")
    return perfil, cabeza, cuerpo, idle


def figura(cabeza, cuerpo, aplastar=0, estirar=0, cab_dx=0, cab_dy=0):
    filas = [cuerpo.crop((0, y, cuerpo.width, y + 1)) for y in range(cuerpo.height)]
    for _ in range(aplastar):
        del filas[4]
    for _ in range(estirar):
        filas.insert(4, filas[4])
    c = vacio(cuerpo.width, len(filas))
    for y, f in enumerate(filas):
        c.paste(f, (0, y))
    m = 4
    out = vacio(cuerpo.width + 2 * m, cabeza.height + c.height + 4)
    top = 2
    pegar(out, c, m, top + cabeza.height + max(0, cab_dy))
    pegar(out, cabeza, m + cab_dx, top + max(0, -cab_dy))
    return out.crop(out.getbbox()), out.getbbox()[0] - m


def inclinar_h(img, k):
    h = img.height
    tope = max(abs(round(k * (h - 1))), 0)
    out = vacio(img.width + tope, h)
    for y in range(h):
        s = round(k * (h - 1 - y))
        out.paste(img.crop((0, y, img.width, y + 1)), (tope - s if k >= 0 else -s, y))
    return out, (tope if k >= 0 else 0)


def inclinar_v(img, k):
    w = img.width
    tope = abs(round(k * (w - 1)))
    out = vacio(w, img.height + tope)
    for x in range(w):
        s = round(k * (w - 1 - x))
        out.paste(img.crop((x, 0, x + 1, img.height)), (x, (tope - 0 if k < 0 else 0) + s if k >= 0 else tope + s))
    return out


def en_frame(fig, x_centro, y_pie):
    f = vacio()
    pegar(f, fig, x_centro - fig.width // 2, y_pie - fig.height + 1)
    return f


def parado(cabeza, cuerpo, aplastar=0, estirar=0, cab_dx=0, cab_dy=0, inclinacion=0.0, alto=0, dx=0):
    fig, _ = figura(cabeza, cuerpo, aplastar, estirar, cab_dx, cab_dy)
    if inclinacion:
        fig, _ = inclinar_h(fig, inclinacion)
    return en_frame(fig, CX + dx, FH - 1 - alto)


def brazo(largo):
    a = vacio(largo, 4)
    for x in range(largo):
        a.putpixel((x, 0), BLK)
        a.putpixel((x, 3), BLK)
        a.putpixel((x, 1), SKIN)
        a.putpixel((x, 2), SKIN)
    for y in range(4):
        a.putpixel((0, y), BLK)
    for y in (1, 2):
        a.putpixel((1, y), PUR)
        a.putpixel((2, y), PUR)
    return a


def acostado(perfil, largo_brazo=14, brazos=True):
    rot = perfil.rotate(90, expand=True)
    out = vacio(rot.width + largo_brazo - 6, rot.height)
    if brazos:
        pegar(out, brazo(largo_brazo), 0, 11)
    pegar(out, rot, largo_brazo - 6, 0)
    return out


def polvo(frame, fuerte=True):
    pts = [(6, 38), (5, 36), (7, 36), (4, 38), (38, 38), (40, 36), (39, 35), (41, 38)] if fuerte \
        else [(5, 38), (40, 38), (6, 37), (39, 37)]
    for i, (x, y) in enumerate(pts):
        frame.putpixel((x, y), POLVO if i % 2 == 0 else POLVO2)
    return frame


def correr(cabeza, cuerpo):
    return [
        parado(cabeza, cuerpo, aplastar=2, cab_dx=-1),
        parado(cabeza, cuerpo, estirar=1, cab_dx=-1, inclinacion=0.06, alto=4),
        parado(cabeza, cuerpo, estirar=1, cab_dx=-2, inclinacion=0.08, alto=8),
        parado(cabeza, cuerpo, cab_dx=-1, inclinacion=0.04, alto=4),
    ]


def caminar(cabeza, cuerpo):
    return [
        parado(cabeza, cuerpo),
        parado(cabeza, cuerpo, cab_dx=-1, alto=1, inclinacion=0.02),
        parado(cabeza, cuerpo),
        parado(cabeza, cuerpo, cab_dx=1, alto=1, inclinacion=-0.02),
    ]


def atacar(cabeza, cuerpo):
    out = []
    for adel, bajar, inc in ((0, 0, 0.0), (1, 0, 0.04), (3, 1, 0.08), (4, 1, 0.1), (3, 1, 0.08), (1, 0, 0.04)):
        out.append(parado(cabeza, cuerpo, cab_dx=-adel, cab_dy=bajar, inclinacion=inc, dx=-(1 if adel > 2 else 0)))
    return out


def salto(perfil, cabeza, cuerpo):
    f = [parado(cabeza, cuerpo, aplastar=3, cab_dx=-1),
         parado(cabeza, cuerpo, estirar=2, cab_dx=-2, inclinacion=0.14)]
    vuelo = acostado(perfil, 14)
    f.append(en_frame(vuelo, CX + 1, 33))
    f.append(en_frame(inclinar_v(vuelo, 0.14), CX + 1, 36))
    f.append(en_frame(inclinar_v(acostado(perfil, 16), 0.34), CX, 39))
    return f


def panzazo(perfil):
    plano = acostado(perfil, 14)
    f = [polvo(en_frame(plano, CX + 1, 39)), polvo(en_frame(plano, CX + 1, 39), fuerte=False)]
    f.append(en_frame(inclinar_v(acostado(perfil, 8, brazos=True), -0.22), CX + 1, 39))
    f.append(en_frame(inclinar_v(acostado(perfil, 4, brazos=False), -0.5), CX + 2, 39))
    return f


def main(src, dst):
    os.makedirs(dst, exist_ok=True)
    perfil, cabeza, cuerpo, idle = cargar_piezas(src)
    p = panzazo(perfil)
    p.append(parado(cabeza, cuerpo, aplastar=3, cab_dx=-1))
    tiras = {
        "murcielago_correr": correr(cabeza, cuerpo),
        "murcielago_atacar": atacar(cabeza, cuerpo),
        "murcielago_salto": salto(perfil, cabeza, cuerpo),
        "murcielago_panzazo": p,
        "murcielago_caminar": caminar(cabeza, cuerpo),
    }
    for nombre, frames in tiras.items():
        tira(frames).save(os.path.join(dst, nombre + ".png"))
    fr = [idle.crop((i * 52 + 4, 18, i * 52 + 34, 50)) for i in range(2)]
    tira(fr).save(os.path.join(dst, "murcielago_idle.png"))


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(base, "assets", "zombies", "murcielago_fuente"),
         sys.argv[2] if len(sys.argv) > 2 else os.path.join(base, "assets", "zombies"))
