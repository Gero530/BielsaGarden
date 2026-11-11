"""
Genera los sprites PLACEHOLDER de las plantas y zombies nuevos en assets/sprites/nuevos/.

    python tools/generar_placeholders.py            # crea solo los que faltan
    python tools/generar_placeholders.py --forzar   # los vuelve a crear todos (¡pisa tus dibujos!)

Cada PNG es una tira horizontal de frames (igual que el resto del juego). Abrilos en
LibreSprite, redibujalos respetando el tamaño de frame y la cantidad de frames, y guardalos
con el mismo nombre: el juego los toma sin tocar código. Tamaños y frames: ver la tabla en
ui/sprites.py (sección "NUEVOS").
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "assets")
DEST = os.path.join(ASSETS, "sprites", "nuevos")

# Paleta (colores planos, estilo recorte de papel)
NEGRO = (20, 20, 20)
BLANCO = (255, 255, 255)
PIEL_Z = (150, 180, 130)
PIEL_Z_OSC = (110, 140, 95)
ROJO = (210, 40, 40)
ROJO_OSC = (150, 20, 20)
NARANJA = (245, 140, 30)
AMARILLO = (255, 214, 64)
VERDE = (70, 170, 60)
VERDE_OSC = (40, 110, 40)
VERDE_CL = (130, 210, 90)
MARRON = (120, 80, 40)
MARRON_CL = (170, 120, 66)
GRIS = (150, 150, 160)
GRIS_CL = (205, 205, 210)
GRIS_OSC = (90, 90, 100)
AZUL = (60, 70, 160)
CELESTE = (150, 200, 240)
PAPEL = (235, 232, 220)
PIEL = (250, 212, 172)
PELO_RUBIO = (240, 210, 110)
ROSA = (225, 120, 145)
CAQUI = (190, 160, 110)
CAFE = (120, 72, 30)
CAFE_CL = (156, 100, 46)


def contorno(s, color=NEGRO):
    """Agrega un contorno de 1 píxel alrededor de todo lo dibujado (look de recorte de papel)."""
    w, h = s.get_size()
    src = s.copy()
    for y in range(h):
        for x in range(w):
            if src.get_at((x, y)).a:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and src.get_at((nx, ny)).a and src.get_at((nx, ny))[:3] != color:
                    s.set_at((x, y), color)
                    break
    return s


def tira(frames):
    w, h = frames[0].get_size()
    out = pygame.Surface((w * len(frames), h), pygame.SRCALPHA)
    for i, f in enumerate(frames):
        out.blit(f, (i * w, 0))
    return out


def nuevo(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def ojos(s, x, y, enojado=True):
    """Dos ojos estilo South Park (óvalos blancos con pupila) en (x, y) = esquina sup. izq."""
    for ox in (0, 6):
        pygame.draw.ellipse(s, BLANCO, (x + ox, y, 6, 6))
        s.fill(NEGRO, (x + ox + 2, y + 2, 2, 2))
    if enojado:
        pygame.draw.line(s, NEGRO, (x, y - 2), (x + 5, y), 1)
        pygame.draw.line(s, NEGRO, (x + 12, y - 2), (x + 7, y), 1)


# ----------------------------------------------------------------------
# Plantas (frames de 40x40, se ven x3 como Stan/Butters)
# ----------------------------------------------------------------------
def picante():
    """6 frames: se sacude y se infla hasta explotar (explota al terminar el frame 5)."""
    frames = []
    for i in range(6):
        s = nuevo(40, 40)
        g = i * 2                     # cuánto se infla
        dx = (-1, 1)[i % 2] if i >= 2 else 0
        body = pygame.Rect(0, 0, 14 + g, 26 + g // 2)
        body.midbottom = (20 + dx, 37)
        color = ROJO if i < 4 else (240, 70, 40)
        pygame.draw.ellipse(s, color, body)
        pygame.draw.ellipse(s, ROJO_OSC, body.inflate(-body.w + 4, -6).move(body.w // 2 - 4, 2))
        s.fill(VERDE, (body.centerx - 2, body.y - 4, 4, 5))         # cabito
        s.fill(VERDE_OSC, (body.centerx - 5, body.y, 10, 2))         # hojitas
        ojos(s, body.centerx - 6, body.y + 7)
        s.fill(NEGRO, (body.centerx - 3, body.y + 17, 6, 1))         # boca
        frames.append(contorno(s))
    return tira(frames)


def picante_fuego():
    """6 frames de 26x32 (una casilla a x3): la llamarada que cubre cada casilla de la cruz."""
    # Colores de la explosión de assets/plantas/picante.png (rojo, naranja, amarillo y centro blanco)
    rojo, naranja, amarillo, blanco, oscuro = (220, 30, 10), (255, 140, 0), (255, 220, 0), (255, 255, 255), (90, 20, 10)
    frames = []
    alturas = (8, 18, 28, 30, 22, 10)
    for i, alto in enumerate(alturas):
        s = nuevo(26, 32)
        for k, (col, enc) in enumerate(((rojo, 0), (naranja, 4), (amarillo, 9), (blanco, 13))):
            a = max(0, alto - enc * 2)
            if a <= 0:
                continue
            for j in range(3):
                x = 2 + enc // 2 + j * (7 - enc // 4)
                h = max(2, a - ((j + i) % 2) * 5)
                pygame.draw.ellipse(s, col, (x, 31 - h, 9 - enc // 3, h))
        frames.append(contorno(s, oscuro))
    return tira(frames)


def _calabaza(ancho, alto, cara=True):
    s = nuevo(40, 40)
    r = pygame.Rect(0, 0, ancho, alto)
    r.midbottom = (20, 37)
    pygame.draw.ellipse(s, VERDE, r)
    pygame.draw.ellipse(s, VERDE_CL, (r.x + 3, r.y + 2, max(2, r.w // 3), max(2, r.h // 3)))
    s.fill(VERDE_OSC, (r.centerx - 1, r.y - 3, 3, 4))
    if cara:
        ojos(s, r.centerx - 6, r.y + max(3, r.h // 3))
        s.fill(NEGRO, (r.centerx - 4, r.y + max(10, r.h * 2 // 3), 8, 2))
    return contorno(s)


def aplastadora():
    """2 frames de reposo (respira)."""
    return tira([_calabaza(26, 24), _calabaza(27, 23)])


def aplastadora_salto():
    """5 frames: 0-1 se agacha (prepara), 2 estirada subiendo, 3 cayendo, 4 aplastando."""
    return tira([_calabaza(28, 21), _calabaza(30, 18), _calabaza(20, 32), _calabaza(22, 30), _calabaza(36, 14)])


def cartman_festejo():
    """8 frames de 40x46: tu Cartman (plantas/cartman_idle.png, el frame 0 entero) saltando con los
    brazos arriba, con su sombra en el piso. Hay lugar de sobra a los costados y arriba, así los
    guantes y la cabeza no se cortan contra el borde del frame."""
    hoja = pygame.image.load(os.path.join(ASSETS, "plantas", "cartman_idle.png")).convert_alpha()
    cartman = hoja.subsurface((0, 0, 26, 24)).copy()
    W, H, PISO = 40, 46, 44
    # (altura del salto, cuánto suben los brazos): agachado, sube, arriba de todo, baja
    pasos = [(0, 0), (3, 2), (7, 3), (10, 4), (11, 4), (10, 4), (7, 3), (3, 2)]
    out = []
    for alto, brazos in pasos:
        s = nuevo(W, H)
        x, y = (W - 26) // 2, PISO - 24 - alto
        for hombro, mano in (((x + 4, y + 16), (x - 3, y + 7 - brazos)),
                             ((x + 21, y + 16), (x + 28, y + 7 - brazos))):
            pygame.draw.line(s, (200, 40, 40), hombro, mano, 2)
            s.fill(AMARILLO, (mano[0] - 1, mano[1] - 2, 3, 3))                   # guantes
        s.blit(cartman, (x, y))
        s = contorno(s)
        sombra = max(10, 22 - alto)                                              # más chica cuanto más alto
        pygame.draw.ellipse(s, (0, 0, 0, 70), (W // 2 - sombra // 2, PISO - 1, sombra, 3))
        out.append(s)
    return tira(out)


# ----------------------------------------------------------------------
# Zombies (frames de 32x48, mirando a la izquierda, pies abajo; se ven x2)
# Se arman encima del zombie normal para que tengan el mismo estilo.
# ----------------------------------------------------------------------
def base_zombie():
    sheet = pygame.image.load(os.path.join(ASSETS, "zombies", "zombie_normal_caminar.png"))
    return [sheet.subsurface((i * 32, 0, 32, 48)).copy() for i in range(sheet.get_width() // 32)]


def con(frames, dibujar):
    out = []
    for i, f in enumerate(frames):
        f = f.copy()
        dibujar(f, i)
        out.append(f)
    return tira(out)


def puerta(f, i):
    r = pygame.Rect(0, 12 + (i % 2), 12, 33)
    f.fill(NEGRO, r)
    f.fill(GRIS_CL, r.inflate(-2, -2))
    f.fill(CELESTE, (r.x + 3, r.y + 3, 6, 9))
    f.fill(GRIS_OSC, (r.x + 3, r.y + 16, 6, 1))
    f.fill(AMARILLO, (r.right - 3, r.y + 18, 1, 2))          # picaporte


def diario(f, i):
    r = pygame.Rect(0, 11 + (i % 2), 15, 17)
    f.fill(NEGRO, r)
    f.fill(PAPEL, r.inflate(-2, -2))
    for y in range(r.y + 3, r.bottom - 2, 3):
        f.fill(GRIS_OSC, (r.x + 2, y, 9 if y % 2 else 11, 1))


def enojado(f, i):
    sub = f.subsurface((0, 0, 32, 22))                      # cabeza colorada de bronca
    sub.fill((255, 150, 140, 255), special_flags=pygame.BLEND_RGBA_MULT)
    f.fill(NEGRO, (6, 5, 5, 1))                              # cejas fruncidas
    f.fill(NEGRO, (13, 5, 4, 1))


def pertiga(f, i):
    pygame.draw.line(f, MARRON, (0, 25 + (i % 2)), (31, 22 + (i % 2)), 1)


def vincha(f, i):
    f.fill(ROJO, (6, 6, 18, 2))


def pertiga_salto():
    f0 = base_zombie()[0]
    frames = []
    for i in range(3):
        f = f0.copy()
        pygame.draw.line(f, MARRON, (3 + i * 2, 0), (8 - i, 47), 2)
        vincha(f, i)
        frames.append(f)
    return tira(frames)


def escalera(f, i):
    y0 = 2 + (i % 2)
    f.fill(MARRON_CL, (1, y0, 1, 42))
    f.fill(MARRON_CL, (8, y0, 1, 42))
    for y in range(y0 + 3, y0 + 42, 5):
        f.fill(MARRON, (2, y, 6, 1))


def casco(f, i):
    f.fill(AMARILLO, (5, 2, 20, 4))
    f.fill(NEGRO, (5, 6, 20, 1))


def escalera_puesta():
    """Escalera apoyada sobre una planta: 1 frame de 20x40 (se ve x2)."""
    s = nuevo(20, 40)
    for k in range(40):
        x = 3 + k * 10 // 40
        s.fill(MARRON_CL, (x, k, 2, 1))
        s.fill(MARRON_CL, (x + 11, k, 2, 1))
    for y in range(3, 40, 5):
        s.fill(MARRON, (4 + y * 10 // 40, y, 11, 1))
    return contorno(s)


def tractor():
    """4 frames de 48x48 (se ve x2): tractor rojo con el zombie manejando."""
    cabeza = base_zombie()[0].subsurface((2, 0, 22, 22)).copy()
    frames = []
    for i in range(4):
        s = nuevo(48, 48)
        s.blit(cabeza, (18, 4 + (i % 2)))
        s.fill(ROJO, (8, 24, 36, 12))                         # carrocería
        s.fill(ROJO_OSC, (8, 34, 36, 2))
        s.fill(GRIS_OSC, (4, 18, 3, 10))                      # caño de escape
        s.fill(ROJO, (2, 28, 10, 8))                           # trompa
        for cx, cy, r in ((34, 38, 9), (10, 41, 6)):
            pygame.draw.circle(s, NEGRO, (cx, cy), r)
            pygame.draw.circle(s, GRIS, (cx, cy), r - 3)
            a = i * 0.785
            pygame.draw.line(s, NEGRO, (cx, cy), (cx + round(math.cos(a) * (r - 3)), cy + round(math.sin(a) * (r - 3))))
        frames.append(contorno(s))
    return tira(frames)


def bungee():
    fr = base_zombie()
    out = []
    for i in (0, 2):
        f = fr[i].copy()
        f.fill(NARANJA, (8, 26, 16, 2))                        # arnés
        f.fill(NARANJA, (15, 0, 2, 26))                        # cuerda hasta el arnés
        out.append(f)
    return tira(out)


def bungee_marca():
    """2 frames de 24x12 (se ve x2): la marca roja en el piso donde va a caer."""
    out = []
    for i in range(2):
        s = nuevo(24, 12)
        c = ROJO if i == 0 else NARANJA
        pygame.draw.ellipse(s, c, (0, 0, 24, 12), 2)
        s.fill(c, (11, 2, 2, 8))
        s.fill(c, (4, 5, 16, 2))
        out.append(s)
    return tira(out)


def afro(f, i):
    pygame.draw.ellipse(f, NEGRO, (3, -2 + (i % 2), 24, 12))
    f.fill(AMARILLO, (10, 27, 8, 1))                          # cadena dorada


def baile():
    fr = base_zombie()
    out = []
    for i in range(4):
        f = fr[0].copy()
        afro(f, i)
        lado = 26 if i % 2 else 2
        f.fill(PIEL_Z, (lado, 6 + (i // 2) * 3, 3, 16))         # brazo arriba
        f.fill(NEGRO, (lado, 6 + (i // 2) * 3, 3, 1))
        out.append(f)
    return tira(out)


def minero(f, i):
    f.fill(AMARILLO, (5, 1, 20, 5))
    f.fill(BLANCO, (4, 3, 3, 2))                               # linterna
    pygame.draw.line(f, MARRON, (22, 14), (29, 34), 1)          # pico
    f.fill(GRIS_OSC, (19, 12, 8, 2))


def minero_sin(f, i):
    """El casco sin el pico (se lo sacó el Imán)."""
    f.fill(AMARILLO, (5, 1, 20, 5))
    f.fill(BLANCO, (4, 3, 3, 2))


def tierra():
    """4 frames de 32x48: el montículo de tierra que avanza (el zombie va abajo)."""
    out = []
    for i in range(4):
        s = nuevo(32, 48)
        pygame.draw.ellipse(s, MARRON, (2, 38, 28, 12))
        for k in range(3):
            x = 5 + ((k * 9 + i * 3) % 22)
            s.fill(MARRON_CL, (x, 39 + (k + i) % 3, 3, 2))
        s.fill(GRIS_OSC, (8 + i % 2, 36, 3, 3))                    # piedritas que saltan
        out.append(contorno(s))
    return tira(out)


def _gigante(frame, golpe=None):
    """Gigante de 48x64 dibujado con formas. golpe: 0..3 = posición del poste (arriba -> abajo)."""
    s = nuevo(48, 64)
    paso = (-2, 0, 2, 0)[frame % 4]
    s.fill((70, 70, 90), (14 + paso, 46, 8, 18))               # piernas
    s.fill((70, 70, 90), (28 - paso, 46, 8, 18))
    s.fill((150, 110, 70), (10, 24, 30, 24))                   # torso (remera rota)
    s.fill(PIEL_Z, (16, 30, 6, 6))
    pygame.draw.ellipse(s, PIEL_Z, (12, 4, 24, 22))            # cabeza
    ojos(s, 15, 11)
    s.fill(ROJO_OSC, (16, 20, 10, 2))
    if golpe is None:
        s.fill(MARRON, (2, 12 + paso, 4, 40))                   # poste de luz
        s.fill(PIEL_Z, (4, 30, 8, 5))                           # brazo
    else:
        ang = math.radians((-70, -20, 30, 80)[golpe])
        x0, y0 = 10, 28
        x1, y1 = x0 - math.cos(ang) * 30, y0 + math.sin(ang) * 30
        pygame.draw.line(s, MARRON, (x0, y0), (x1, y1), 4)
        s.fill(PIEL_Z, (6, 27, 8, 5))
    return contorno(s)


def gigante():
    return tira([_gigante(i) for i in range(4)])


def gigante_golpe():
    return tira([_gigante(0, g) for g in range(4)])


def mini():
    """4 frames de 24x32 (se ve x2): el zombie chiquito que tira el gigante."""
    out = []
    for i in range(4):
        s = nuevo(24, 32)
        paso = (-1, 0, 1, 0)[i]
        s.fill((60, 60, 80), (8 + paso, 24, 3, 8))
        s.fill((60, 60, 80), (13 - paso, 24, 3, 8))
        s.fill((130, 90, 50), (6, 14, 12, 11))
        pygame.draw.ellipse(s, PIEL_Z, (4, 1, 16, 15))
        ojos(s, 5, 5, enojado=False)
        s.fill(PIEL_Z, (2, 16, 5, 2))                          # brazo adelante
        out.append(contorno(s))
    return tira(out)


GENERADORES = {
    # Plantas
    "picante.png": picante,
    "picante_fuego.png": picante_fuego,
    "aplastadora.png": aplastadora,
    "aplastadora_salto.png": aplastadora_salto,
    "cartman_festejo.png": cartman_festejo,
    # Zombies
    "zombie_puerta.png": lambda: con(base_zombie(), puerta),
    "zombie_diario.png": lambda: con(base_zombie(), diario),
    "zombie_diario_enojado.png": lambda: con(base_zombie(), enojado),
    "zombie_pertiga.png": lambda: con(base_zombie(), lambda f, i: (vincha(f, i), pertiga(f, i))),
    "zombie_pertiga_salto.png": pertiga_salto,
    "zombie_pertiga_sin.png": lambda: con(base_zombie(), vincha),
    "zombie_escalera.png": lambda: con(base_zombie(), lambda f, i: (casco(f, i), escalera(f, i))),
    "zombie_escalera_sin.png": lambda: con(base_zombie(), casco),
    "escalera.png": escalera_puesta,
    "zombie_tractor.png": tractor,
    "zombie_bungee.png": bungee,
    "bungee_marca.png": bungee_marca,
    "zombie_bailarin.png": lambda: con(base_zombie(), afro),
    "zombie_bailarin_baile.png": baile,
    "zombie_excavador.png": lambda: con(base_zombie(), minero),
    "zombie_excavador_sin.png": lambda: con(base_zombie(), minero_sin),
    "zombie_excavador_tierra.png": tierra,
    "zombie_gigante.png": gigante,
    "zombie_gigante_golpe.png": gigante_golpe,
    "zombie_mini.png": mini,
}


def main():
    forzar = "--forzar" in sys.argv
    pygame.init()
    pygame.display.set_mode((1, 1))
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
