import os
from PIL import Image

AQUI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "zombies", "propios")
FW, FH = 56, 36
CX = 28
SHOE_ROWS = 4
CAMINAR_REBOTE = (0, 1, 1, 0, 0, 1, 1, 0)
CAMINAR_PASO = (-1, 0, 1, 1, 1, 0, -1, -1)
CAMINAR_POOH = (0, 0, 1, 1, 0, 0, 1, 1)
ATACAR_ADELANTE = (0, 1, 2, 3, 2, 1)
ATACAR_BAJA = (0, 0, 1, 1, 1, 0)


def cargar():
    fuente = Image.open(os.path.join(AQUI, "mickey_fuente.png")).convert("RGBA")
    parado = fuente.crop((16, 14, 35, 45))
    con_pooh = fuente.crop((58, 14, 94, 45))
    pooh = Image.new("RGBA", con_pooh.size)
    mickey = con_pooh.copy()
    for y in range(con_pooh.height):
        for x in range(con_pooh.width):
            r, g, b, a = con_pooh.getpixel((x, y))
            if a and x <= 15 and not (r > 230 and g > 230 and b > 230):
                pooh.putpixel((x, y), (r, g, b, a))
                mickey.putpixel((x, y), (0, 0, 0, 0))
    return parado, mickey, pooh


def espejo(im):
    return im.transpose(Image.FLIP_LEFT_RIGHT)


def centro_mickey(im):
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
    parado, mickey_c, pooh_c = espejo(parado), espejo(mickey_c), espejo(pooh_c)
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
