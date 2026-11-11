"""
Arte y coreografía de la intro (pixel art dibujado por código, salvo los chicos, que son
los sprites de tu juego).

Todo se dibuja en un lienzo chico de 334x200 que después se agranda x3 a 1000x600, así el
tamaño de píxel coincide con el de tus personajes en la partida (que también van x3). Los chicos se usan tal cual los dibujaste.

La coreografía (assembly_view) es una función del TIEMPO DE LA CANCIÓN: dado t, calcula
dónde está cada pieza. Por eso queda sincronizada con la música aunque el juego vaya
más lento o más rápido. Los momentos clave caen sobre los pulsos de la canción
(145 BPM = un pulso cada 0,414 s):
  pulso 5 (2,09 s) aterriza la cabeza de Kenny
  pulso 6 (2,50 s) aterriza la cabeza de Stan
  pulso 7 (2,91 s) aterriza la cabeza de Cartman (en la pausa de la canción) -> aparece el menú
"""
import math
import os
import random
import pygame
from ui.pixel_font import pixel_text, text_width

W, H = 334, 200
ESCALA = 3
FEET = 178                     # altura donde apoyan los pies de los chicos
ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

# Pulso de la canción (se midió sobre el mp3)
PULSO = 0.414
PULSO_FASE = 0.016
T_CARTMAN = 2.914              # aterriza la cabeza de Cartman = termina el armado
T_MENU = 3.328                 # pulso 8: aparecen los botones

SKY = (118, 178, 240)
VERDE = (12, 198, 83)
VERDE_OSC = (8, 160, 74)
GRIS_MONTE = (200, 205, 210)
NIEVE = (255, 255, 255)
NIEVE_SOMBRA = (226, 234, 242)
CALLE = (74, 74, 78)
LINEA = (236, 200, 40)

# Chicos: (archivo, ancho frame, alto frame, recorte x,y,ancho,alto del personaje en el frame 0,
#          fila donde se separa cabeza/cuerpo, x final, aterriza cuerpo, aterriza cabeza)
KIDS = [
    dict(name="cartman", file="plantas/cartman_idle.png", fw=26, fh=24, crop=(1, 0, 25, 23), split=16,
         x=84, body_t=2.20, head_t=T_CARTMAN),
    dict(name="stan", file="personajes/stan_idle.png", fw=40, fh=40, crop=(13, 10, 15, 24), split=16,
         x=114, body_t=1.90, head_t=2.50),
    dict(name="kenny", file="plantas/kenny_explosion.png", fw=32, fh=32, crop=(8, 4, 15, 21), split=12,
         x=142, body_t=1.50, head_t=2.086),
    dict(name="kyle", file="plantas/kyle_idle.png", fw=38, fh=38, crop=(3, 6, 19, 21), split=14,
         x=170, body_t=1.70, head_t=2.30),
]

_cache = {}


# ----------------------------------------------------------------------
# Utilidades de animación
# ----------------------------------------------------------------------
def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def smooth(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def rebote(t, t_land, alto=7.0, dur=0.38):
    """Salto chiquito después de aterrizar (en píxeles hacia arriba)."""
    v = (t - t_land) / dur
    if v < 0 or v >= 1:
        return 0.0
    return alto * abs(math.sin(math.pi * 2 * v)) * (1 - v) ** 1.5


# ----------------------------------------------------------------------
# Fondo
# ----------------------------------------------------------------------
def _montana(surf, cx, base, alto, color, nieve=NIEVE, cap=0.30, pendiente=0.95):
    top = base - alto
    for y in range(top, base):
        d = y - top
        half = int(d * pendiente)
        col = nieve if d < alto * cap else color
        pygame.draw.line(surf, col, (cx - half, y), (cx + half, y))
    # borde irregular de la nieve (dientes de sierra como en la intro original)
    capy = top + int(alto * cap)
    for k in range(0, 6):
        y = capy + k
        half = int((y - top) * pendiente)
        for x in range(cx - half, cx + half + 1):
            if ((x // 5) + k) % 2 == 0 and k < 3:
                surf.set_at((x, y), nieve)


def build_background():
    if "bg" in _cache:
        return _cache["bg"]
    bg = pygame.Surface((W, H))
    bg.fill(SKY)
    # montañas del fondo (más oscuras, nieve gris) y del frente
    for cx, alto in ((20, 54), (93, 66), (170, 58), (247, 72), (320, 56)):
        _montana(bg, cx, 157, alto, VERDE_OSC, nieve=GRIS_MONTE)
    for cx, alto in ((50, 62), (137, 76), (213, 64), (293, 78)):
        _montana(bg, cx, 159, alto, VERDE)
    # nieve
    bg.fill(NIEVE, (0, 155, W, H - 155))
    for x in range(0, W, 12):                               # unas sombras para que no sea plana
        bg.fill(NIEVE_SOMBRA, (x + (x // 12 % 3) * 3, 164 + (x // 12 % 3) * 4, 7, 2))
    _cache["bg"] = bg
    return bg


def draw_road(world, t_road):
    """La calle: cae inclinada y se acomoda. t_road: 0 = al principio, 1 = en su lugar."""
    ang = math.radians(15 * (1 - ease_out(t_road)))
    yc = 190 + (87 - 190) * (1 - ease_out(t_road))

    def xf(px, py):
        return (W / 2 + px * math.cos(ang) - py * math.sin(ang), yc + px * math.sin(ang) + py * math.cos(ang))
    pts = [xf(-470, -10), xf(470, -10), xf(470, 10), xf(-470, 10)]
    pygame.draw.polygon(world, CALLE, pts)
    for i in range(-10, 11):                                # rayas amarillas
        a = xf(i * 26 - 6, 5)
        b = xf(i * 26 + 6, 5)
        pygame.draw.line(world, LINEA, a, b, 2)


# ----------------------------------------------------------------------
# Chicos (sprites tuyos, partidos en cabeza y cuerpo)
# ----------------------------------------------------------------------
def load_kids():
    if "kids" in _cache:
        return _cache["kids"]
    kids = []
    for k in KIDS:
        sheet = pygame.image.load(os.path.join(ASSETS, k["file"])).convert_alpha()
        x, y, w, h = k["crop"]
        full = sheet.subsurface((0, 0, k["fw"], k["fh"])).subsurface((x, y, w, h)).copy()
        s = k["split"]
        d = dict(k)
        d.update(w=w, h=h, full=full, head=full.subsurface((0, 0, w, s)).copy(),
                 body=full.subsurface((0, s, w, h - s)).copy())
        d["sx"] = k["x"] - w // 2
        d["sy"] = FEET - h
        kids.append(d)
    _cache["kids"] = kids
    return kids


# ----------------------------------------------------------------------
# Bus escolar y cartel de la parada
# ----------------------------------------------------------------------
def build_bus():
    if "bus" in _cache:
        return _cache["bus"]
    bw, bh = 176, 46
    s = pygame.Surface((bw, bh), pygame.SRCALPHA)
    AMAR, AMAR_S, NEG = (226, 164, 16), (178, 124, 8), (20, 14, 6)
    s.fill(NEG, (4, 2, bw - 8, 34))                         # contorno
    s.fill(AMAR, (5, 3, bw - 10, 32))
    s.fill(AMAR_S, (5, 3, bw - 10, 2))                      # borde de arriba
    s.fill(NEG, (5, 24, bw - 10, 2))                        # franjas negras
    s.fill(NEG, (5, 29, bw - 10, 1))
    for i in range(6):                                      # ventanillas
        x = 34 + i * 23
        s.fill(NEG, (x - 1, 7, 20, 14))
        s.fill((40, 196, 112), (x, 8, 18, 12))
        s.fill((20, 150, 80), (x, 8, 18, 3))
    s.fill(NEG, (5, 7, 24, 22)); s.fill((226, 164, 16), (6, 8, 22, 20))   # puerta
    s.fill(NEG, (9, 10, 14, 14)); s.fill((40, 196, 112), (10, 11, 12, 12))
    # cartel rojo STOP (octógono simple) en el costado de adelante
    pygame.draw.polygon(s, (170, 20, 20), [(0, 12), (4, 9), (10, 9), (14, 12), (14, 18), (10, 21), (4, 21), (0, 18)])
    pygame.draw.polygon(s, (230, 40, 40), [(1, 12), (4, 10), (10, 10), (13, 12), (13, 18), (10, 20), (4, 20), (1, 18)])
    s.fill((255, 255, 255), (3, 14, 8, 2))
    txt = pixel_text("SOUTH PARK ELEMENTARY", (20, 14, 6), 1)
    s.blit(txt, (32, 26))
    for cx in (34, 138):                                    # ruedas
        pygame.draw.circle(s, NEG, (cx, 37), 9)
        pygame.draw.circle(s, (70, 70, 74), (cx, 37), 5)
        pygame.draw.circle(s, (150, 150, 156), (cx, 37), 2)
    _cache["bus"] = s
    return s


def build_cartel_parada():
    if "parada" in _cache:
        return _cache["parada"]
    s = pygame.Surface((34, 70), pygame.SRCALPHA)
    s.fill((60, 60, 66), (16, 20, 3, 50))                   # poste
    s.fill((10, 40, 90), (2, 4, 30, 20))                    # cartel azul
    s.fill((30, 90, 190), (3, 5, 28, 18))
    s.blit(pixel_text("BUS", (255, 255, 255), 1), (9, 11))
    _cache["parada"] = s
    return s


def build_nube(ancho):
    key = ("nube", ancho)
    if key in _cache:
        return _cache[key]
    s = pygame.Surface((ancho, ancho // 3 + 6), pygame.SRCALPHA)
    h = s.get_height()
    for i, (dx, r) in enumerate(((0.22, 0.22), (0.45, 0.30), (0.70, 0.24))):
        pygame.draw.circle(s, (255, 255, 255), (int(ancho * dx + 6), h - 6 - int(ancho * 0.12)), int(ancho * r))
    s.fill((255, 255, 255), (4, h - 14, ancho - 4, 8))
    _cache[key] = s
    return s


# ----------------------------------------------------------------------
# Cartel de madera (botones y título)
# ----------------------------------------------------------------------
# Paletas del tablón por estado: contorno, luz, medio, sombra, veta, letra, luz del tallado
TABLON_PAL = {
    "normal":    ((58, 34, 14), (200, 150, 86), (164, 116, 60), (116, 78, 38), (132, 92, 46), (40, 22, 6), (222, 180, 116)),
    "hover":     ((58, 34, 14), (232, 186, 112), (194, 144, 80), (138, 96, 48), (160, 114, 60), (30, 14, 2), (250, 214, 150)),
    "apretado":  ((50, 30, 12), (150, 104, 54), (128, 88, 44), (92, 60, 28), (108, 72, 36), (36, 20, 6), (170, 126, 72)),
    "bloqueado": ((62, 60, 58), (172, 168, 160), (140, 136, 130), (102, 100, 96), (120, 116, 110), (44, 42, 40), (190, 186, 180)),
}
TABLON_SOMBRA = (0, 0, 0, 90)


def _lugar_texto(img, ancho, top, ph, esc):
    """Dónde va el texto en el tablón. Se centra en la cara de la madera (sin el borde) lo que
    se ve: las letras (7 filas) más la luz tallada de abajo (1 fila más). La fila de la tilde
    (Á, É...) no cuenta: sube al margen de arriba en vez de empujar las letras contra el borde
    de abajo. Si sobra una fila impar, va abajo."""
    cara_y, cara_h = top + 1, ph - 2                 # filas entre el borde de arriba y el de abajo
    bloque = 8 * esc                                 # 7 de letra + 1 de luz
    tilde = img.get_height() - 7 * esc               # fila de más arriba si hay tildes
    r = img.get_rect()
    r.centerx = ancho // 2
    r.top = cara_y + max(0, cara_h - bloque) // 2 - tilde
    return r


def build_cartel(texto, ancho, alto, escala_texto, hover=False, estado=None, color_texto=None):
    """Tablón de madera de 3 tonos con letras talladas (en píxeles de dibujo; se agranda afuera).
    estado: "normal" (apoyado, con sombra abajo), "hover" (más claro y levantado 1 píxel),
    "apretado" (más oscuro y hundido 1 píxel, sin sombra) o "bloqueado" (gris con dos tablas
    cruzadas clavadas). Las 2 filas de abajo quedan para la sombra / el movimiento."""
    estado = estado or ("hover" if hover else "normal")
    key = ("cartel", texto, ancho, alto, escala_texto, estado, color_texto)
    if key in _cache:
        return _cache[key]
    out, luz, mid, osc, veta, letra, brillo = TABLON_PAL[estado]
    s = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    top = {"normal": 1, "hover": 0, "apretado": 2, "bloqueado": 1}[estado]
    ph = alto - 2
    if estado != "apretado":                                    # sombra apoyada
        s.fill(TABLON_SOMBRA, (2, top + ph, ancho - 3, alto - top - ph))
    body = pygame.Rect(0, top, ancho, ph)
    s.fill(out, body)
    inner = body.inflate(-2, -2)
    s.fill(mid, inner)
    s.fill(luz, (inner.x, inner.y, inner.w, 1)); s.fill(luz, (inner.x, inner.y, 1, inner.h))         # luz arriba
    s.fill(osc, (inner.x, inner.bottom - 1, inner.w, 1)); s.fill(osc, (inner.right - 1, inner.y, 1, inner.h))
    # Franja del texto: las vetas no pasan por ahí (no tachan las letras)
    img = pixel_text(texto, color_texto or letra, escala_texto) if texto else None
    tr = _lugar_texto(img, ancho, top, ph, escala_texto) if img else pygame.Rect(0, 0, 0, 0)
    franja = range(tr.top - 1, tr.bottom + escala_texto + 1) if img else range(0)
    rnd = random.Random(ancho * 31 + alto * 7)
    for y in range(inner.y + 3, inner.bottom - 2, 3):           # vetas cortas
        if y in franja:
            continue
        x0 = inner.x + 2 + rnd.randint(0, max(1, ancho // 3))
        largo = min(rnd.randint(max(2, ancho // 5), max(3, ancho // 2)), inner.right - 3 - x0)
        if largo > 0:
            s.fill(veta, (x0, y, largo, 1))
    if ancho > 34 and ph > 12:                                  # un nudo, lejos del texto
        kx = inner.x + rnd.randint(4, max(5, inner.w - 8))
        for ky in (inner.y + 2, inner.bottom - 5):
            if all(yy not in franja for yy in range(ky, ky + 3)):
                s.fill(veta, (kx, ky, 3, 1)); s.fill(veta, (kx, ky + 2, 3, 1))
                s.fill(veta, (kx - 1, ky + 1, 1, 1)); s.fill(veta, (kx + 3, ky + 1, 1, 1))
                s.fill(osc, (kx + 1, ky + 1, 1, 1))
                break
    # Esquinas gastadas y una astilla
    for x, y in ((0, top), (ancho - 1, top), (0, top + ph - 1), (ancho - 1, top + ph - 1)):
        s.set_at((x, y), (0, 0, 0, 0))
    if ancho > 20:
        s.fill((0, 0, 0, 0), (3, top + ph - 1, 3, 1)); s.fill(out, (3, top + ph - 2, 3, 1))
        s.fill((0, 0, 0, 0), (ancho - 9, top, 2, 1)); s.fill(out, (ancho - 9, top + 1, 2, 1))
    if ph >= 12 and ancho >= 24:                                # tornillos con un píxel de brillo
        for x, y in ((inner.x + 2, inner.y + 2), (inner.right - 4, inner.y + 2),
                     (inner.x + 2, inner.bottom - 4), (inner.right - 4, inner.bottom - 4)):
            s.fill((46, 34, 24), (x, y, 2, 2)); s.set_at((x, y), (200, 190, 170))
    if estado == "bloqueado":                                   # dos tablas cruzadas clavadas
        # Se cortan en la franja del texto (pasan por detrás de las letras), así se sigue leyendo
        zonas = [pygame.Rect(0, 0, tr.left - 2, alto), pygame.Rect(tr.right + 2, 0, ancho, alto)] if img             else [s.get_rect()]
        for zona in zonas:
            s.set_clip(zona)
            for a, b in (((2, top + 2), (ancho - 3, top + ph - 3)), ((2, top + ph - 3), (ancho - 3, top + 2))):
                pygame.draw.line(s, (70, 52, 34), a, b, 3)
                pygame.draw.line(s, (150, 112, 70), a, b, 1)
        s.set_clip(None)
    if img:                                                     # letras talladas: luz de 1 píxel debajo
        s.blit(pixel_text(texto, brillo, escala_texto), tr.move(0, escala_texto))   # luz del grosor del trazo
        s.blit(img, tr)
    _cache[key] = s
    return s


BALANCEO = (0, 1, 0, -1)         # corrimiento (píxeles de dibujo) de la punta de abajo en cada cuadro


def cuadro_balanceo(t, fps=3):
    return BALANCEO[int(t * fps) % len(BALANCEO)]


def build_colgante(texto, ancho, alto, escala_texto, cuadro=0, cuerda=8, color_texto=None):
    """Tablón colgando de dos sogas. cuadro (-1, 0, 1): balanceo dibujado en pixel art: cada fila
    se corre un número entero de píxeles (la de arriba nada, la de abajo `cuadro`), sin rotar."""
    ancho = max(ancho, text_width(texto, escala_texto) + 20)
    key = ("colgante", texto, ancho, alto, escala_texto, cuadro, cuerda, color_texto)
    if key in _cache:
        return _cache[key]
    s = pygame.Surface((ancho + 2, alto + cuerda), pygame.SRCALPHA)
    for x in (ancho // 4, ancho * 3 // 4):
        for y in range(cuerda + 2):
            s.set_at((x + 1, y), (196, 160, 104) if y % 2 else (124, 92, 54))      # soga trenzada
    s.blit(build_cartel(texto, ancho, alto, escala_texto, color_texto=color_texto), (1, cuerda))
    if cuadro:
        out = pygame.Surface(s.get_size(), pygame.SRCALPHA)
        h = s.get_height()
        for y in range(h):
            out.blit(s, (round(cuadro * y / (h - 1)), y), (0, y, s.get_width(), 1))
        s = out
    _cache[key] = s
    return s


def colgante_escalado(texto, ancho, alto, escala_texto, t, esc=ESCALA, cuerda=8, color_texto=None, cuadro=None):
    """build_colgante agrandado x`esc`, en el cuadro de balanceo que toca en el instante t."""
    c = cuadro_balanceo(t) if cuadro is None else cuadro
    key = ("colgante_esc", texto, ancho, alto, escala_texto, c, cuerda, esc, color_texto)
    if key not in _cache:
        s = build_colgante(texto, ancho, alto, escala_texto, c, cuerda, color_texto)
        _cache[key] = pygame.transform.scale(s, (s.get_width() * esc, s.get_height() * esc))
    return _cache[key]


_vivo = {}


def fondo_vivo(t):
    """El paisaje del menú (montañas, nieve y la calle) con nubes que pasan y el bus que cruza
    cada ~16 s (sin la parada: asomaba detrás de los paneles). Devuelve la imagen agrandada x ESCALA."""
    if not _vivo:
        _vivo["mundo"] = pygame.Surface((W, H))
        _vivo["pantalla"] = pygame.Surface((W * ESCALA, H * ESCALA))
    m = _vivo["mundo"]
    m.blit(build_background(), (0, 0))
    draw_road(m, 1.0)
    for ancho, y, v, x0 in ((66, 12, 5.0, 40), (46, 34, 8.0, 210), (38, 20, 11.0, 330)):
        x = (x0 + v * t) % (W + 2 * ancho) - ancho
        m.blit(build_nube(ancho), (int(x), y))
    tb = t - 2.0
    if tb >= 0:
        x = W + 6 - (tb % 16.0) * 62
        if x > -190:
            m.blit(build_bus(), (int(x), FEET + 14 - 46))
    pygame.transform.scale(m, _vivo["pantalla"].get_size(), _vivo["pantalla"])
    return _vivo["pantalla"]


CORTINA_ESC = 3


def build_cortina():
    """Hoja de cartulina con los bordes rotos (para la transición entre pantallas), agrandada x3."""
    if "cortina" in _cache:
        return _cache["cortina"]
    a, b = 120, 200
    s = pygame.Surface((a, b), pygame.SRCALPHA)
    rnd = random.Random(7)
    papel, borde, fibra = (214, 158, 92), (150, 100, 50), (232, 184, 120)
    for y in range(b):
        izq, der = rnd.randint(0, 3), a - rnd.randint(1, 4)       # bordes rotos
        s.fill(borde, (izq, y, der - izq, 1))
        s.fill(papel, (izq + 1, y, der - izq - 2, 1))
    for _ in range(140):                                          # fibras de la cartulina
        s.set_at((rnd.randint(6, a - 8), rnd.randint(0, b - 1)), fibra)
    _cache["cortina"] = pygame.transform.scale(s, (a * CORTINA_ESC, b * CORTINA_ESC))
    return _cache["cortina"]


def con_destello(img, fase):
    """Copia del tablón con un brillo diagonal de 2 píxeles que lo cruza (fase 0..1).
    Solo aclara los píxeles de madera que ya están (no pinta afuera del tablón)."""
    s = img.copy()
    w, h = s.get_size()
    x0 = int(-h + fase * (w + h))
    for y in range(h):
        for k in range(2):
            x = x0 + (h - y) + k
            if 0 <= x < w:
                c = s.get_at((x, y))
                if c.a == 255 and sum(c[:3]) > 200:             # madera (no el contorno ni las letras)
                    s.set_at((x, y), (min(255, c.r + 50), min(255, c.g + 46), min(255, c.b + 36)))
    return s


# ----------------------------------------------------------------------
# Coreografía del armado (tiempo de la canción -> vista de la cámara)
# ----------------------------------------------------------------------
Z0 = 12.0
T_ZOOM0, T_ZOOM1 = 0.20, T_CARTMAN        # el zoom arranca con Stan y termina cuando cae Cartman


def camara(t, stan_head_center):
    """Devuelve (zoom, centro_mundo, desplazamiento_en_pantalla)."""
    u = clamp((t - T_ZOOM0) / (T_ZOOM1 - T_ZOOM0))
    z = math.exp(math.log(Z0) * (1 - u ** 1.5))
    w = smooth((t - 1.3) / 1.5)
    cx = stan_head_center[0] + (W / 2 - stan_head_center[0]) * w
    cy = stan_head_center[1] + (H / 2 - stan_head_center[1]) * w
    e = ease_out((t - 0.2) / 0.8)
    return z, (cx, cy), (165 * (1 - e), 80 * (1 - e))


def pieza_pos(k, t, parte):
    """Esquina superior izquierda de la cabeza/cuerpo de un chico en el instante t (o None si no se ve)."""
    sx, sy = k["sx"], k["sy"]
    if parte == "body":
        top = sy + k["split"]
        t_land, dur = k["body_t"], 0.7
        if t < t_land - dur:
            return None
        u = clamp((t - (t_land - dur)) / dur)
        return (sx + 20 * (1 - u), -45 + (top + 45) * u * u - rebote(t, t_land, 3))
    # cabeza
    t_land = k["head_t"]
    if k["name"] == "stan":
        # Stan: arranca en el centro de la pantalla (es el protagonista del acercamiento) y baja a su cuerpo
        start = (W / 2 - k["w"] / 2, H / 2 - k["split"] / 2)
        if t < 0.2:
            return None
        u = clamp((t - 1.0) / (t_land - 1.0))
        return (start[0] + (sx - start[0]) * ease_out(u),
                start[1] + (sy - start[1]) * u * u - rebote(t, t_land, 4))
    dur = 0.95
    if t < t_land - dur:
        return None
    u = clamp((t - (t_land - dur)) / dur)
    return (sx + 36 * (1 - u), -50 + (sy + 50) * u * u - rebote(t, t_land, 5))


def draw_world(world, t, kids, extras=None, beat=None, delante=None):
    """Dibuja el mundo (500x300) en el instante t. `extras(world)` dibuja cosas entre el fondo y los
    chicos; `delante(world)`, cosas que pasan por delante de los chicos (el bus)."""
    world.fill((0, 0, 0))
    # el fondo se revela como un rectángulo que crece desde el centro (como en la intro)
    r = smooth((t - 0.8) / 0.6)
    if r > 0:
        hw, hh = 27 + (W / 2 - 27) * r, 16 + (H / 2 - 16) * r
        rect = pygame.Rect(int(W / 2 - hw), int(H / 2 - hh), int(hw * 2), int(hh * 2))
        world.blit(build_background(), rect.topleft, rect)
        if r >= 1.0:
            world.blit(build_background(), (0, 0))
    if t >= 0.8:
        draw_road(world, clamp((t - 1.4) / 1.2))
    if extras:
        extras(world)
    # cuerpos primero, cabezas arriba
    for k in kids:
        p = pieza_pos(k, t, "body")
        if p is not None:
            world.blit(k["body"], (round(p[0]), round(p[1])))
    for k in kids:
        p = pieza_pos(k, t, "head")
        if p is not None:
            dy = 0
            if beat is not None and t >= T_CARTMAN:
                dy = beat                                      # el cabeceo al ritmo, solo después del armado
            world.blit(k["head"], (round(p[0]), round(p[1]) + dy))
    if delante:
        delante(world)


def render_view(canvas, world, t, kids):
    """Pasa el mundo por la cámara (zoom/desplazamiento) y lo deja en `canvas` (500x300)."""
    stan = next(k for k in kids if k["name"] == "stan")
    sp = pieza_pos(stan, t, "head") or (W / 2 - stan["w"] / 2, H / 2 - stan["split"] / 2)
    sc = (sp[0] + stan["w"] / 2, sp[1] + stan["split"] / 2)
    z, cam, off = camara(t, sc)
    canvas.fill((0, 0, 0))
    if t < T_ZOOM0:
        return
    if z <= 1.001 and abs(off[0]) < 0.5:
        canvas.blit(world, (0, 0))
        return
    vw, vh = W / z, H / z
    vx = clamp(cam[0] - vw / 2, 0, W - vw)
    vy = clamp(cam[1] - vh / 2, 0, H - vh)
    x0, y0 = int(vx), int(vy)
    w = min(W - x0, int(math.ceil(vw)) + 2)
    h = min(H - y0, int(math.ceil(vh)) + 2)
    sub = world.subsurface((x0, y0, w, h))
    big = pygame.transform.scale(sub, (max(1, round(w * z)), max(1, round(h * z))))
    canvas.blit(big, (round((x0 - vx) * z + off[0]), round((y0 - vy) * z + off[1])))
