"""
Genera las tiras de sprites del zombie puerta "Mickey con Winnie the Pooh" a partir de la
imagen fuente assets/zombies/propios/mickey_fuente.png (los dos dibujos de Santi: Mickey parado
y Mickey sosteniendo a Pooh). No se redibuja nada: los frames de caminar y atacar salen de mover
los píxeles originales (rebote, pasos con los zapatos, inclinación, balanceo de Pooh).

    python tools/generar_mickey.py

Salida (assets/zombies/propios/), todos con el zombie mirando a la IZQUIERDA como los demás:
    zombie_mickey_caminar.png        8 frames 56x36  Mickey + Pooh
    zombie_mickey_atacar.png         6 frames 56x36  Mickey + Pooh
    zombie_mickey_sin_caminar.png    8 frames 56x36  Mickey solo
    zombie_mickey_sin_atacar.png     6 frames 56x36  Mickey solo
    pooh.png                         1 frame 16x24   Pooh suelto (lo usa el Imán)
En todos Mickey queda centrado en el frame (x=28) y con los zapatos en la última fila.
"""
import os
from PIL import Image

AQUI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "zombies", "propios")
FW, FH = 56, 36
CX = 28                                     # columna donde queda el centro de Mickey
SHOE_ROWS = 4                               # filas de abajo que son los zapatos
CAMINAR_REBOTE = (0, 1, 1, 0, 0, 1, 1, 0)    # px que sube el cuerpo en cada frame
CAMINAR_PASO = (-1, 0, 1, 1, 1, 0, -1, -1)   # px que se corren los zapatos
CAMINAR_POOH = (0, 0, 1, 1, 0, 0, 1, 1)      # px que baja Pooh (cuelga y se balancea)
ATACAR_ADELANTE = (0, 1, 2, 3, 2, 1)         # px que se tira hacia adelante (izquierda)
ATACAR_BAJA = (0, 0, 1, 1, 1, 0)


def cargar():
    fuente = Image.open(os.path.join(AQUI, "mickey_fuente.png")).convert("RGBA")
    parado = fuente.crop((16, 14, 35, 45))            # 19x31
    con_pooh = fuente.crop((58, 14, 94, 45))          # 36x31
    # Pooh = los píxeles de la izquierda de su dibujo, sin el guante blanco de Mickey
    pooh = Image.new("RGBA", con_pooh.size)
    mickey = con_pooh.copy()
    for y in range(con_pooh.height):
        for x in range(con_pooh.width):
            r, g, b, a = con_pooh.getpixel((x, y))
            if a and x <= 15 and not (r > 230 and g > 230 and b > 230):    # x<=15 -> columnas 58..73
                pooh.putpixel((x, y), (r, g, b, a))
                mickey.putpixel((x, y), (0, 0, 0, 0))
    return parado, mickey, pooh


def espejo(im):
    return im.transpose(Image.FLIP_LEFT_RIGHT)


def centro_mickey(im):
    """Columna del centro de los zapatos (el cuerpo) de una imagen de Mickey."""
    caja = im.crop((0, im.height - 3, im.width, im.height))
    xs = [x for x in range(caja.width) for y in range(caja.height) if caja.getpixel((x, y))[3]]
    return (min(xs) + max(xs)) // 2


def tira(frames):
    t = Image.new("RGBA", (FW * len(frames), FH))
    for i, f in enumerate(frames):
        t.paste(f, (FW * i, 0))
    return t


def main():
    parado, mickey_c, pooh_c = cargar()
    parado, mickey_c, pooh_c = espejo(parado), espejo(mickey_c), espejo(pooh_c)   # mira a la izquierda
    # Mickey de la imagen con Pooh: su lienzo es de 36x31; Pooh queda en la misma posición relativa
    # Los dos "Mickey" tienen que quedar con los zapatos en el mismo lugar: se usa el mismo
    # corrimiento para Mickey y para Pooh (el de Mickey) para no separarlos.
    ox_m = CX - centro_mickey(mickey_c)
    pooh_c_full = Image.new("RGBA", mickey_c.size)
    pooh_c_full.alpha_composite(pooh_c)

    def con_pooh(i, rebote, paso, inclina, baja):
        lienzo = Image.new("RGBA", (FW, FH))
        ox = ox_m
        alto = mickey_c.height
        for y in range(alto):
            if y >= alto - SHOE_ROWS:
                dx = paso
            else:
                dx = -round(inclina * (alto - SHOE_ROWS - y) / (alto - SHOE_ROWS))
            lienzo.alpha_composite(mickey_c.crop((0, y, mickey_c.width, y + 1)), (ox + dx, FH - alto + y - rebote))
        # Pooh: pegado a la mano, un poco más abajo según el balanceo, e inclinado igual que el torso
        lienzo.alpha_composite(pooh_c_full, (ox - round(inclina * 0.6), FH - alto - rebote + baja))
        return lienzo

    def solo(rebote, paso, inclina):
        lienzo = Image.new("RGBA", (FW, FH))
        ox = CX - centro_mickey(parado)
        alto = parado.height
        for y in range(alto):
            if y >= alto - SHOE_ROWS:
                dx = paso
            else:
                dx = -round(inclina * (alto - SHOE_ROWS - y) / (alto - SHOE_ROWS))
            lienzo.alpha_composite(parado.crop((0, y, parado.width, y + 1)), (ox + dx, FH - alto + y - rebote))
        return lienzo

    caminar_p = [con_pooh(i, CAMINAR_REBOTE[i], CAMINAR_PASO[i], 0, CAMINAR_POOH[i]) for i in range(8)]
    atacar_p = [con_pooh(i, 0, 0, ATACAR_ADELANTE[i], ATACAR_BAJA[i]) for i in range(6)]
    caminar_s = [solo(CAMINAR_REBOTE[i], CAMINAR_PASO[i], 0) for i in range(8)]
    atacar_s = [solo(0, 0, ATACAR_ADELANTE[i]) for i in range(6)]
    tira(caminar_p).save(os.path.join(AQUI, "zombie_mickey_caminar.png"))
    tira(atacar_p).save(os.path.join(AQUI, "zombie_mickey_atacar.png"))
    tira(caminar_s).save(os.path.join(AQUI, "zombie_mickey_sin_caminar.png"))
    tira(atacar_s).save(os.path.join(AQUI, "zombie_mickey_sin_atacar.png"))
    caja = pooh_c.getbbox()
    pooh_c.crop(caja).save(os.path.join(AQUI, "pooh.png"))
    print("pooh", pooh_c.crop(caja).size)


if __name__ == "__main__":
    main()
