import sys, os
from PIL import Image

FW, FH = 17, 31
ROJO, TEAL = (208, 2, 27), (29, 189, 169)
PELO_NEGRO, RUBIO = (33, 31, 29), (225, 219, 10)
CONO = {(212, 85, 0), (242, 155, 24), (255, 102, 0), (255, 255, 255), (0, 0, 0)}


def frames(im):
    return [im.crop((i * FW, 0, (i + 1) * FW, FH)) for i in range(im.width // FW)]


def tira(fr):
    out = Image.new("RGBA", (FW * len(fr), FH), (0, 0, 0, 0))
    for i, f in enumerate(fr):
        out.paste(f, (i * FW, 0))
    return out


def fila_camisa(f, color):
    for y in range(FH):
        if any(f.getpixel((x, y))[:3] == color for x in range(FW)):
            return y


def pelo_rubio(f):
    y0 = next(y for y in range(FH) if any(f.getpixel((x, y))[3] for x in range(FW)))
    for y in (y0, y0 + 1):
        for x in range(FW):
            if f.getpixel((x, y))[:3] == PELO_NEGRO and f.getpixel((x, y))[3]:
                f.putpixel((x, y), (*RUBIO, 255))
    return f


def philip_sin_cono(ph, te):
    y_p, y_t = fila_camisa(ph, TEAL), fila_camisa(te, ROJO)
    out = ph.copy()
    for y in range(y_p):
        for x in range(FW):
            out.putpixel((x, y), (0, 0, 0, 0))
    for y in range(y_t):
        yy = y - y_t + y_p
        if yy < 0:
            continue
        for x in range(FW):
            p = te.getpixel((x, y))
            if p[3]:
                out.putpixel((x, yy), p)
    return pelo_rubio(out)


def main(src, dst):
    os.makedirs(dst, exist_ok=True)
    cargar = lambda n: Image.open(os.path.join(src, n)).convert("RGBA")
    te_i, te_c = cargar("terrance_idle.png"), cargar("terrance_caminar.png")
    ph_i, ph_c = cargar("philip_idle.png"), cargar("philip_caminar.png")
    for n, im in (("terrance_idle", te_i), ("terrance_caminar", te_c), ("philip_idle", ph_i), ("philip_caminar", ph_c)):
        im.save(os.path.join(dst, n + ".png"))
    for nombre, ph, te in (("philip_sin_idle", ph_i, te_i), ("philip_sin_caminar", ph_c, te_c)):
        tira([philip_sin_cono(p, t) for p, t in zip(frames(ph), frames(te))]).save(os.path.join(dst, nombre + ".png"))
    f = frames(ph_i)[0]
    y_p = fila_camisa(f, TEAL)
    cono = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    for y in range(y_p):
        for x in range(FW):
            p = f.getpixel((x, y))
            if p[:3] in CONO and p[3]:
                cono.putpixel((x, y), p)
    cono.crop(cono.getbbox()).save(os.path.join(dst, "cono_caido.png"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
