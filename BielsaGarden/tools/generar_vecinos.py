import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_placeholders as gp
import pygame

DEST = os.path.join(gp.ASSETS, "sprites", "vecinos")
NEGRO, BLANCO = gp.NEGRO, gp.BLANCO
PIEL = (166, 190, 146)
PIEL_ENOJADA = (204, 150, 126)
BOCA, DIENTE = (70, 20, 24), (240, 236, 210)

TALLAS = {
    "normal":  dict(r=10, bw=14, bh=12, lh=7, brazo=7),
    "mini":    dict(r=7, bw=9, bh=7, lh=5, brazo=4),
    "gigante": dict(r=10, bw=28, bh=24, lh=11, brazo=10),
}

CAMINAR = [dict(bob=b, paso=p, bdy=a) for b, p, a in
           zip((0, 1, 1, 0, 0, 1, 1, 0), (-2, -1, 0, 1, 2, 1, 0, -1), (0, 0, 1, 1, 0, 0, 1, 1))]
CORRER = [dict(bob=b, paso=p, bdy=a) for b, p, a in
          zip((0, 1, 2, 1, 0, 1, 2, 1), (-3, -2, 0, 2, 3, 2, 0, -2), (0, 1, 1, 0, 0, 1, 1, 0))]
ATACAR = [dict(bdy=d, adelante=f, boca=m) for d, f, m in
          zip((0, 1, 2, 2, 1, 0, 0, 0), (0, 1, 2, 3, 3, 2, 1, 0), (0, 0, 1, 1, 1, 1, 0, 0))]


def oscuro(c, k=38):
    return tuple(max(0, v - k) for v in c)


def persona(s, talla, ropa, pose, cx, pies, piel=PIEL, arriba=False):
    t = TALLAS[talla]
    camisa, pantalon = ropa
    bob, paso, adel = pose.get("bob", 0), pose.get("paso", 0), pose.get("adelante", 0)
    ly = pies - 2 - t["lh"]
    for dx, signo in ((-t["bw"] // 4 - 2, 1), (t["bw"] // 4, -1)):
        x = cx + dx + signo * paso
        s.fill(pantalon, (x, ly, 3, t["lh"]))
        pygame.draw.ellipse(s, NEGRO, (x - 2, pies - 3, 6, 3))
    by = ly - t["bh"] - bob
    bx = cx - t["bw"] // 2
    brazo_y = by + 2 + pose.get("bdy", 0)
    if arriba:
        s.fill(oscuro(camisa), (bx + t["bw"] - 2, by - 6, 3, 8)); s.fill(oscuro(piel), (bx + t["bw"] - 2, by - 9, 3, 3))
    else:
        s.fill(oscuro(camisa), (bx - t["brazo"] + 2 - adel, brazo_y - 1, t["brazo"], 3))
        s.fill(oscuro(piel), (bx - t["brazo"] - adel, brazo_y - 1, 3, 3))
    s.fill(camisa, (bx, by + 2, t["bw"], t["bh"] - 1))
    pygame.draw.ellipse(s, camisa, (bx, by, t["bw"], 5))
    s.fill(oscuro(camisa), (bx + t["bw"] // 2, by + t["bh"] - 3, 2, 2))
    s.set_at((bx + 2, by + t["bh"] - 1), oscuro(camisa))
    r = t["r"]
    hx, hy = cx - 1 - adel, by - r + 4
    pygame.draw.ellipse(s, piel, (hx - r - 1, hy - r, 2 * r + 2, 2 * r))
    ew = max(4, r // 2 + 1)
    ex, ey = hx - r + 1, hy - r // 3 - 1
    for i in (0, 1):
        pygame.draw.ellipse(s, BLANCO, (ex + i * (ew - 1), ey, ew, ew))
    s.fill(NEGRO, (ex + 1, ey + ew // 2, 2, 2))
    s.set_at((ex + ew, ey + ew // 2), NEGRO)
    s.fill(oscuro(piel), (ex, ey + ew, ew * 2 - 1, 1))
    mx, my = hx - r + 2, hy + r // 2
    if pose.get("boca"):
        pygame.draw.ellipse(s, BOCA, (mx, my - 1, r, r // 2 + 2))
        s.set_at((mx + 2, my - 1), DIENTE); s.set_at((mx + 5, my - 1), DIENTE)
    else:
        for i in range(r - 2):
            s.set_at((mx + i, my + i % 2), BOCA)
    ax = bx - t["brazo"] - adel
    if arriba:
        s.fill(camisa, (bx - 1, by - 6, 3, 8)); s.fill(piel, (bx - 1, by - 9, 3, 3))
        ax, ay = bx - 1, by - 9
    else:
        ay = brazo_y + 1
        s.fill(camisa, (ax + 2, ay, t["brazo"], 3)); s.fill(piel, (ax, ay, 3, 3))
    return dict(hx=hx, hy=hy, r=r, bx=bx, by=by, bw=t["bw"], bh=t["bh"], mano=(ax, ay), pies=pies, cx=cx, ly=ly)


def strip(w, h, poses, dibujar):
    out = []
    for i, pose in enumerate(poses):
        s = gp.nuevo(w, h)
        dibujar(s, pose, i)
        out.append(gp.contorno(s))
    return gp.tira(out)


def pelo_despeinado(s, p):
    hx, hy, r = p["hx"], p["hy"], p["r"]
    for dx, alto in ((-4, 2), (-1, 3), (2, 2), (5, 1)):
        s.fill((84, 80, 88), (hx + dx, hy - r - alto + 1, 2, alto))


def gorra(s, p, color, visera=True):
    hx, hy, r = p["hx"], p["hy"], p["r"]
    pygame.draw.ellipse(s, color, (hx - r, hy - r - 2, 2 * r + 1, 8))
    s.fill(color, (hx - r, hy - r + 2, 2 * r + 1, 2))
    if visera:
        s.fill(oscuro(color), (hx - r - 4, hy - r + 3, 6, 2))


def gorro_pompon(s, p, color, pompon):
    hx, hy, r = p["hx"], p["hy"], p["r"]
    pygame.draw.ellipse(s, color, (hx - r, hy - r - 2, 2 * r + 1, r + 2))
    s.fill(oscuro(color), (hx - r, hy - r + r // 2, 2 * r + 1, 2))
    s.fill(pompon, (hx - 1, hy - r - 4, 3, 3))


def casco_obra(s, p):
    hx, hy, r = p["hx"], p["hy"], p["r"]
    pygame.draw.ellipse(s, (250, 210, 50), (hx - r, hy - r - 2, 2 * r + 1, 9))
    s.fill((250, 210, 50), (hx - r - 2, hy - r + 4, 2 * r + 5, 2))
    s.fill(BLANCO, (hx - r, hy - r + 1, 2, 2))


PARKA = ((92, 120, 170), (80, 66, 52))


def normal(poses):
    def d(s, pose, i):
        p = persona(s, "normal", PARKA, pose, 16, 47)
        pelo_despeinado(s, p)
    return strip(32, 48, poses, d)


def puerta(poses):
    def d(s, pose, i):
        p = persona(s, "normal", ((90, 140, 80), (60, 60, 70)), pose, 17, 47)
        pelo_despeinado(s, p)
        top = p["by"] - 1
        s.fill((120, 86, 56), (0, top, 11, 46 - top))
        s.fill((236, 232, 220), (1, top + 1, 9, 44 - top))
        s.fill((150, 200, 230), (3, top + 3, 5, 6))
        s.fill((230, 190, 60), (7, top + 15, 2, 2))
    return strip(32, 48, poses, d)


def diario(poses, enojado=False):
    def d(s, pose, i):
        p = persona(s, "normal", ((150, 110, 170), (150, 110, 170)), pose, 17, 47,
                    piel=PIEL_ENOJADA if enojado else PIEL)
        hx, hy, r = p["hx"], p["hy"], p["r"]
        s.fill((200, 200, 205), (hx + 1, hy - r, 7, 2))
        ex, ey = hx - r + 1, hy - r // 3 - 1
        pygame.draw.rect(s, NEGRO, (ex - 1, ey - 1, 13, 8), 1)
        if enojado:
            s.fill(NEGRO, (ex, ey - 3, 4, 1)); s.fill(NEGRO, (ex + 7, ey - 3, 4, 1))
            if i % 2:
                s.fill(BLANCO, (hx + 4, hy - r - 5, 2, 2)); s.fill(BLANCO, (hx - 3, hy - r - 6, 2, 2))
        else:
            mx, my = p["mano"]
            baja = 3 if pose.get("boca") else 0
            s.fill((232, 228, 214), (0, my - 6 + baja, 13, 11))
            for yy in range(my - 4 + baja, my + 4 + baja, 2):
                s.fill((150, 150, 156), (2, yy, 9, 1))
            s.fill(NEGRO, (2, my - 5 + baja, 9, 1))
    return strip(32, 48, poses, d)


ATLETA = ((230, 200, 60), (60, 90, 170))


def pertiga(poses, con_pertiga=True):
    def d(s, pose, i):
        p = persona(s, "normal", ATLETA, pose, 17, 47)
        hx, hy, r = p["hx"], p["hy"], p["r"]
        for dx in (-5, -2, 1, 4):
            s.fill((120, 70, 40), (hx + dx, hy - r - 1, 2, 2))
        s.fill(NEGRO, (p["bx"] + 6, p["by"] + 4, 2, 1)); s.fill(NEGRO, (p["bx"] + 7, p["by"] + 5, 1, 4))
        if con_pertiga:
            mx, my = p["mano"]
            pygame.draw.line(s, (160, 116, 60), (0, my + 3), (31, my - 2), 1)
    return strip(32, 48, poses, d)


def pertiga_salto():
    def d(s, pose, i):
        pies = (47, 36, 47)[i]
        p = persona(s, "normal", ATLETA, CORRER[2 * i], 17 if i < 2 else 12, pies)
        hx, hy, r = p["hx"], p["hy"], p["r"]
        for dx in (-5, -2, 1, 4):
            s.fill((120, 70, 40), (hx + dx, hy - r - 1, 2, 2))
        if i == 0:
            pygame.draw.line(s, (160, 116, 60), (1, 47), (24, p["by"] - 2), 1)
        elif i == 1:
            pygame.draw.line(s, (160, 116, 60), (6, 47), (9, 14), 1)
    return strip(32, 48, CORRER[:3], d)


def escalera(poses, con_escalera=True):
    def d(s, pose, i):
        bob = pose.get("bob", 0)
        if con_escalera:
            for x in (21, 27):
                s.fill((176, 128, 70), (x, 3 - bob, 2, 40))
            for y in range(6 - bob, 42 - bob, 5):
                s.fill((150, 106, 56), (21, y, 8, 1))
        p = persona(s, "normal", ((186, 52, 48), (60, 80, 130)), pose, 15, 47)
        for x in range(p["bx"] + 1, p["bx"] + p["bw"], 3):
            s.fill((112, 28, 30), (x, p["by"] + 2, 1, p["bh"] - 1))
        gorra(s, p, (66, 66, 72))
    return strip(32, 48, poses, d)


def tractor(poses, atacando=False):
    def d(s, pose, i):
        vib = i % 2
        sube = (0, -2, -3, -2, 0, 1, 0, 0)[i] if atacando else 0
        s.fill((80, 80, 86), (40, 12 - vib, 2, 10))
        if i % 4 < 2:
            pygame.draw.ellipse(s, (220, 220, 220), (38, 6 - vib - i % 4, 5, 4))
        s.fill((230, 120, 30), (14, 22 - vib, 30, 16))
        s.fill((150, 200, 230), (26, 12 - vib, 14, 10))
        pygame.draw.ellipse(s, PIEL, (27, 10 - vib, 12, 12))
        s.fill(BLANCO, (28, 13 - vib, 3, 3)); s.fill(BLANCO, (31, 13 - vib, 3, 3)); s.set_at((29, 14 - vib), NEGRO)
        if atacando and pose.get("boca"):
            s.fill(BOCA, (29, 18 - vib, 4, 2))
        else:
            s.fill(BOCA, (29, 18 - vib, 4, 1))
        pygame.draw.ellipse(s, (60, 120, 200), (27, 7 - vib, 12, 6))
        s.fill((255, 255, 255), (32, 5 - vib, 2, 2))
        pygame.draw.rect(s, (40, 40, 44), (10, 38, 36, 9), border_radius=4)
        for k, x in enumerate((15, 23, 31, 39)):
            pygame.draw.circle(s, (130, 130, 136), (x, 42), 3)
            ang = (i + k) % 4
            s.set_at((x + (1, 0, -1, 0)[ang], 42 + (0, 1, 0, -1)[ang]), NEGRO)
        pts = [(1, 26 + sube), (11, 30 + sube), (11, 44), (2, 46)]
        pygame.draw.polygon(s, (110, 110, 120), pts)
        pygame.draw.line(s, (250, 210, 50), (2, 46), (1, 26 + sube), 1)
        s.fill((80, 80, 86), (11, 34, 4, 3))
    return strip(48, 48, poses, d)


def bungee(poses):
    def d(s, pose, i):
        p = persona(s, "normal", ((60, 170, 170), (60, 170, 170)), pose, 17, 47)
        hx, hy, r, bx, by = p["hx"], p["hy"], p["r"], p["bx"], p["by"]
        pygame.draw.line(s, NEGRO, (bx, by + 2), (bx + p["bw"] - 1, by + p["bh"] - 2), 1)
        pygame.draw.line(s, NEGRO, (bx + p["bw"] - 1, by + 2), (bx, by + p["bh"] - 2), 1)
        s.fill((90, 90, 96), (hx - r + 1, hy - r + 2, 2 * r - 1, 3))
        s.fill((120, 200, 250), (hx - r + 2, hy - r + 2, 3, 2)); s.fill((120, 200, 250), (hx - r + 7, hy - r + 2, 3, 2))
    return strip(32, 48, poses, d)


def bailarin(poses, baile=False):
    def d(s, pose, i):
        p = persona(s, "normal", ((130, 70, 170), (130, 70, 170)), pose, 16, 47, arriba=baile and i % 2 == 0)
        hx, hy, r = p["hx"], p["hy"], p["r"]
        s.fill(BLANCO, (p["bx"] + 2, p["by"] + 2, 1, p["bh"] - 2))
        gorra(s, p, (200, 40, 40), visera=False)
        s.fill((150, 30, 30), (hx + r - 2, hy - r + 3, 5, 2))
        if baile:
            s.fill((70, 70, 76), (0, 39, 11, 7))
            pygame.draw.circle(s, (150, 150, 160), (3, 42), 2); pygame.draw.circle(s, (150, 150, 160), (8, 42), 2)
        else:
            bx, by = p["bx"] + p["bw"] - 4, p["by"] - 6
            s.fill((70, 70, 76), (bx, by, 11, 7))
            pygame.draw.circle(s, (150, 150, 160), (bx + 3, by + 3), 2)
            pygame.draw.circle(s, (150, 150, 160), (bx + 8, by + 3), 2)
    if baile:
        poses = [dict(bob=b, paso=p) for b, p in ((0, -2), (2, 0), (0, 2), (2, 0))]
    return strip(32, 48, poses, d)


def excavador(poses, con_pico=True):
    def d(s, pose, i):
        p = persona(s, "normal", ((236, 130, 40), (90, 90, 96)), pose, 17, 47)
        s.fill((250, 230, 90), (p["bx"] + 2, p["by"] + 5, p["bw"] - 4, 1))
        casco_obra(s, p)
        if con_pico:
            bx, by = p["bx"], p["by"]
            pygame.draw.line(s, (150, 106, 56), (bx + 2, by + 6), (bx + 12, by - 8), 1)
            s.fill((170, 170, 180), (bx + 7, by - 11, 10, 2))
            s.set_at((bx + 6, by - 10), (170, 170, 180)); s.set_at((bx + 17, by - 10), (170, 170, 180))
    return strip(32, 48, poses, d)


def gigante(poses, con_mini=True, golpe=False):
    def d(s, pose, i):
        cx = 26
        if con_mini:
            pygame.draw.ellipse(s, PIEL, (35, 10, 11, 10))
            pygame.draw.ellipse(s, (70, 150, 70), (35, 8, 11, 6)); s.fill(BLANCO, (39, 6, 2, 2))
            s.fill(BLANCO, (36, 13, 3, 3)); s.set_at((36, 14), NEGRO)
            s.fill(PIEL, (44, 20, 3, 3))
        p = persona(s, "gigante", ((206, 200, 180), (110, 80, 54)), pose, cx, 63)
        hx, hy, r = p["hx"], p["hy"], p["r"]
        s.fill((84, 80, 88), (hx - 3, hy - r - 1, 6, 2))
        s.fill(oscuro((206, 200, 180), 60), (p["bx"] + 8, p["by"] + 10, 5, 4))
        mx, my = p["mano"]
        if golpe:
            fase = (0, 1, 2, 3, 4, 4, 2, 1)[i]
            if fase <= 3:
                tip = (mx - 2 + fase, my - 10 - fase * 4)
            else:
                tip = (1, 58)
        else:
            tip = (mx + 2, my - 22 + pose.get("bob", 0))
        tip = (max(6, tip[0]), max(6, min(58, tip[1])))
        pygame.draw.line(s, (150, 150, 160), (mx + 1, my + 1), tip, 2)
        pygame.draw.circle(s, (200, 30, 30), tip, 5)
        s.fill(BLANCO, (tip[0] - 3, tip[1], 7, 1))
    if golpe:
        poses = [dict(bob=0, paso=0, bdy=(0, -1, -2, -3, 2, 3, 1, 0)[k]) for k in range(8)]
    return strip(48, 64, poses, d)


def mini(poses):
    def d(s, pose, i):
        p = persona(s, "mini", ((236, 140, 50), (70, 70, 110)), pose, 12, 31)
        gorro_pompon(s, p, (70, 150, 70), BLANCO)
    return strip(24, 32, poses, d)


GENERADORES = {
    "zombie_normal_caminar.png": lambda: normal(CAMINAR),
    "zombie_normal_atacar.png": lambda: normal(ATACAR),
    "zombie_puerta_caminar.png": lambda: puerta(CAMINAR),
    "zombie_puerta_atacar.png": lambda: puerta(ATACAR),
    "zombie_diario_caminar.png": lambda: diario(CAMINAR),
    "zombie_diario_atacar.png": lambda: diario(ATACAR),
    "zombie_diario_enojado_caminar.png": lambda: diario(CORRER, enojado=True),
    "zombie_diario_enojado_atacar.png": lambda: diario(ATACAR, enojado=True),
    "zombie_pertiga_caminar.png": lambda: pertiga(CORRER),
    "zombie_pertiga_salto.png": pertiga_salto,
    "zombie_pertiga_sin_caminar.png": lambda: pertiga(CAMINAR, con_pertiga=False),
    "zombie_pertiga_sin_atacar.png": lambda: pertiga(ATACAR, con_pertiga=False),
    "zombie_escalera_caminar.png": lambda: escalera(CAMINAR),
    "zombie_escalera_sin_caminar.png": lambda: escalera(CAMINAR, con_escalera=False),
    "zombie_escalera_sin_atacar.png": lambda: escalera(ATACAR, con_escalera=False),
    "zombie_tractor_caminar.png": lambda: tractor(CAMINAR),
    "zombie_tractor_atacar.png": lambda: tractor(ATACAR, atacando=True),
    "zombie_bungee_caminar.png": lambda: bungee(CAMINAR),
    "zombie_bungee_atacar.png": lambda: bungee(ATACAR),
    "zombie_bailarin_caminar.png": lambda: bailarin(CAMINAR),
    "zombie_bailarin_atacar.png": lambda: bailarin(ATACAR),
    "zombie_bailarin_baile.png": lambda: bailarin(None, baile=True),
    "zombie_excavador_caminar.png": lambda: excavador(CAMINAR),
    "zombie_excavador_atacar.png": lambda: excavador(ATACAR),
    "zombie_excavador_sin_caminar.png": lambda: excavador(CAMINAR, con_pico=False),
    "zombie_excavador_sin_atacar.png": lambda: excavador(ATACAR, con_pico=False),
    "zombie_gigante_caminar.png": lambda: gigante(CAMINAR),
    "zombie_gigante_sin_caminar.png": lambda: gigante(CAMINAR, con_mini=False),
    "zombie_gigante_golpe.png": lambda: gigante(None, golpe=True),
    "zombie_gigante_golpe_sin.png": lambda: gigante(None, con_mini=False, golpe=True),
    "zombie_mini_caminar.png": lambda: mini(CAMINAR),
    "zombie_mini_atacar.png": lambda: mini(ATACAR),
}


def main():
    forzar = "--forzar" in sys.argv
    os.makedirs(DEST, exist_ok=True)
    for nombre, gen in GENERADORES.items():
        path = os.path.join(DEST, nombre)
        if os.path.exists(path) and not forzar:
            print("ya existe (no se toca):", nombre)
            continue
        pygame.image.save(gen(), path)
        print("creado:", nombre)


if __name__ == "__main__":
    main()
