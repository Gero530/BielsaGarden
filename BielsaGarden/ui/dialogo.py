"""
Diálogo con Bielsa (estilo Crazy Dave): retrato grande abajo a la izquierda, burbuja en pixel art
con la colita apuntando a su boca, el tablón con su nombre y la flechita de "seguir".

Uso:
    dialogo = Dialogo(["Hola", "Chau"], retrato="victoria")
    dialogo.manejar_evento(evento)   # clic o cualquier tecla avanza (completa el texto si se está
                                     # escribiendo); ESC saltea todo
    dialogo.actualizar(dt)
    dialogo.dibujar(pantalla)
    if dialogo.terminado: ...
"""
import os
import pygame
from settings import SCREEN_W, SCREEN_H
from ui.sprites import ASSETS_DIR
from ui.pixel_font import wrap, draw_pixel_text, ALTO
from ui import sonidos

# === RETRATOS (assets/dialogo/). "boca": dónde está la boca, en píxeles del retrato ya escalado ===
# Los PNG están dibujados con bloques de 6x6: se muestran a la mitad exacta (3 px por bloque),
# sin suavizado, para que ocupen buena parte del alto de la pantalla.
RETRATOS = {
    "tutorial": {"img": "dialogo/bielsa1.png", "boca": (270, 250)},
    "antes":    {"img": "dialogo/bielsa2.png", "boca": (156, 214)},
    "victoria": {"img": "dialogo/bielsa_victoria.png", "boca": (216, 180)},
    "derrota":  {"img": "dialogo/bielsa_derrota.png", "boca": (192, 256)},
}
BLOQUE_PNG, BLOQUE_PANTALLA = 6, 3

# === BURBUJA (se dibuja en una grilla de PIXEL px de pantalla, como los tablones del menú) ===
PIXEL = 3
BURBUJA_W, BURBUJA_H = 192, 80           # en píxeles de la grilla (x3 = 576x240 en pantalla)
BURBUJA_X_MAX = 400                       # la burbuja empieza acá, o más a la izquierda si la boca lo pide
COLITA_W = 30                             # largo de la colita (grilla)
ESCALA_TEXTO = 3                          # fuente pixel x3
MARGEN = (12, 10)                         # margen interno (grilla)
COLOR_TEXTO = (44, 30, 16)
BORDE = (44, 30, 16)
FONDO = (250, 243, 224)
LUZ = (255, 252, 242)
SOMBRA_INT = (222, 208, 176)
SOMBRA = (70, 48, 26)
NOMBRE_PERSONAJE = "BIELSA"

# === COMPORTAMIENTO ===
VELOCIDAD_TEXTO = 45        # letras por segundo
VELOCIDAD_ENTRADA = 1600    # px/s con que entra desde la izquierda (0 = sin animación)
OSCURIDAD_FONDO = 120       # 0 = sin overlay, 255 = negro total
SONIDO_CADA = 2             # suena un sonidito cada N letras

FLECHA = [                  # flechita de "seguir" (grilla x3), rebota de a 1 píxel de grilla
    "#######",
    "#YYYYY#",
    ".#YYY#.",
    "..#Y#..",
    "...#...",
]
REBOTE = (0, 1, 2, 1)

_cache = {}


def retrato_img(clave):
    """El retrato a 3 px por bloque (vecino más cercano: los bloques de 6 quedan de 3 exactos)."""
    if clave not in _cache:
        path = os.path.join(ASSETS_DIR, RETRATOS[clave]["img"])
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            f = BLOQUE_PANTALLA / BLOQUE_PNG
            _cache[clave] = pygame.transform.scale(img, (int(img.get_width() * f), int(img.get_height() * f)))
        else:
            s = pygame.Surface((300, 400), pygame.SRCALPHA)
            s.fill((140, 140, 140))
            _cache[clave] = s
    return _cache[clave]


def _rect_redondeado(w, h):
    """Máscara (lista de filas) de un rectángulo con esquinas escalonadas, dibujada a mano."""
    esquina = ["...", ".", ""]          # cuántos píxeles faltan en las 3 primeras filas: 3, 1, 0
    filas = []
    for y in range(h):
        k = len(esquina[y]) if y < 3 else (len(esquina[h - 1 - y]) if y >= h - 3 else 0)
        filas.append((k, w - k))
    return filas


def burbuja_img(w, h, colita_y):
    """La burbuja en la grilla chica: borde de 2, bisel claro arriba-izquierda y oscuro abajo-derecha,
    colita a la izquierda (punta en (0, colita_y + 10)) y sombra apoyada abajo a la derecha."""
    key = ("burbuja", w, h, colita_y)
    if key in _cache:
        return _cache[key]
    W, H = COLITA_W + w + 3, max(h, colita_y + 13) + 3
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    x0 = COLITA_W
    filas = _rect_redondeado(w, h)
    for y, (a, b) in enumerate(filas):                 # borde (todo el rectángulo)
        s.fill(BORDE, (x0 + a, y, b - a, 1))
    for y in range(2, h - 2):                          # relleno, 2 px adentro
        a, b = filas[y]
        a2 = max(a, 2) + (1 if y in (2, h - 3) else 0)
        b2 = min(b, w - 2) - (1 if y in (2, h - 3) else 0)
        s.fill(FONDO, (x0 + a2, y, b2 - a2, 1))
        if y == 2:
            s.fill(LUZ, (x0 + a2, y, b2 - a2, 1))
        if y == h - 3:
            s.fill(SOMBRA_INT, (x0 + a2, y, b2 - a2, 1))
        s.set_at((x0 + a2, y), LUZ)                     # bisel izquierdo
        s.set_at((x0 + b2 - 1, y), SOMBRA_INT)          # bisel derecho
    # Colita: de la punta (abajo a la izquierda) al costado de la burbuja, en escalones
    tip_y = colita_y + 10
    for x in range(COLITA_W + 3):
        t = x / (COLITA_W + 2)
        arriba = round(tip_y + (colita_y - tip_y) * t)
        abajo = round(tip_y + (colita_y + 8 - tip_y) * t)
        for y in range(arriba - 2, abajo + 3):
            borde = y < arriba or y > abajo or x < 2
            s.set_at((x, y), BORDE if borde else FONDO)
    # Sombra apoyada: la misma silueta corrida 3 abajo y 3 a la derecha, detrás
    sombra = pygame.mask.from_surface(s).to_surface(setcolor=SOMBRA, unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface((W, H), pygame.SRCALPHA)
    out.blit(sombra, (3, 3))
    out.blit(s, (0, 0))
    _cache[key] = pygame.transform.scale(out, (W * PIXEL, H * PIXEL))
    return _cache[key]


def flecha_img():
    if "flecha" not in _cache:
        s = pygame.Surface((len(FLECHA[0]), len(FLECHA)), pygame.SRCALPHA)
        for y, fila in enumerate(FLECHA):
            for x, ch in enumerate(fila):
                if ch != ".":
                    s.set_at((x, y), BORDE if ch == "#" else (240, 196, 60))
        _cache["flecha"] = pygame.transform.scale(s, (s.get_width() * PIXEL, s.get_height() * PIXEL))
    return _cache["flecha"]


class Dialogo:
    def __init__(self, mensajes, retrato="tutorial"):
        self.mensajes = list(mensajes)
        self.retrato = retrato if retrato in RETRATOS else "tutorial"
        self.indice = 0
        self.letras = 0.0
        self.tiempo = 0.0
        self.contador_letras = 0
        self.terminado = not self.mensajes
        self.img = retrato_img(self.retrato)
        # Dónde va cada cosa: el retrato abajo a la izquierda; la burbuja a su derecha, con la
        # punta de la colita junto a la boca
        self.retrato_pos = (0, SCREEN_H - self.img.get_height())
        bx, by = RETRATOS[self.retrato]["boca"]
        boca = (self.retrato_pos[0] + bx, self.retrato_pos[1] + by)
        punta = (boca[0] + 40, boca[1])
        self.burbuja_x = min(BURBUJA_X_MAX, punta[0] + COLITA_W * PIXEL)          # borde izquierdo del cuerpo
        colita_y = BURBUJA_H - 22                                                 # dónde sale la colita (grilla)
        self.burbuja_y = punta[1] - (colita_y + 10) * PIXEL
        self.burbuja_y = max(96, min(self.burbuja_y, SCREEN_H - BURBUJA_H * PIXEL - 12))
        tip_y = (punta[1] - self.burbuja_y) // PIXEL - 10
        self.img_burbuja = burbuja_img(BURBUJA_W, BURBUJA_H, max(4, min(BURBUJA_H - 12, tip_y)))
        self.offset_x = -(self.burbuja_x + BURBUJA_W * PIXEL) if VELOCIDAD_ENTRADA else 0
        self.ancho_texto = (BURBUJA_W - 2 * MARGEN[0]) * PIXEL
        self._preparar_mensaje()

    @property
    def activo(self):
        return not self.terminado

    def _preparar_mensaje(self):
        texto = self.mensajes[self.indice] if self.mensajes else ""
        self.lineas = wrap(texto, ESCALA_TEXTO, self.ancho_texto)      # parte por palabras, nunca a la mitad
        self.total_letras = sum(len(l) for l in self.lineas)
        self.plano = "".join(self.lineas)
        self.letras = 0.0

    @property
    def escrito(self):
        return self.letras >= self.total_letras

    def avanzar(self):
        if not self.escrito:
            self.letras = self.total_letras       # completa el texto de golpe
        elif self.indice + 1 < len(self.mensajes):
            self.indice += 1
            self._preparar_mensaje()
        else:
            self.terminado = True

    # ------------------------------------------------------------------
    def manejar_evento(self, evento):
        if self.terminado:
            return
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                self.terminado = True
            else:
                self.avanzar()
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self.avanzar()

    def actualizar(self, dt):
        if self.terminado:
            return
        self.tiempo += dt
        if self.offset_x < 0:                     # todavía entrando: el texto espera
            self.offset_x = min(0, self.offset_x + VELOCIDAD_ENTRADA * dt)
            return
        antes = int(self.letras)
        self.letras = min(self.total_letras, self.letras + VELOCIDAD_TEXTO * dt)
        suena = False
        for c in self.plano[antes:int(self.letras)]:
            if c.isalnum():
                self.contador_letras += 1
                if self.contador_letras % SONIDO_CADA == 0:
                    suena = True
        if suena:
            sonidos.reproducir("hablar")

    def dibujar(self, pantalla):
        if self.terminado:
            return
        sombra = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, OSCURIDAD_FONDO))
        pantalla.blit(sombra, (0, 0))

        ox = int(self.offset_x) // PIXEL * PIXEL
        pantalla.blit(self.img, (self.retrato_pos[0] + ox, self.retrato_pos[1]))
        bx, by = self.burbuja_x + ox, self.burbuja_y
        pantalla.blit(self.img_burbuja, (bx - COLITA_W * PIXEL, by))
        if NOMBRE_PERSONAJE:
            from ui.button import tablon
            placa = tablon(NOMBRE_PERSONAJE, 0, 14, PIXEL)
            pantalla.blit(placa, placa.get_rect(bottomleft=(bx + 8 * PIXEL, by + 4 * PIXEL)))

        # Texto letra por letra
        x, y = bx + MARGEN[0] * PIXEL, by + MARGEN[1] * PIXEL
        restantes = int(self.letras)
        for linea in self.lineas:
            if restantes <= 0:
                break
            draw_pixel_text(pantalla, linea[:restantes], COLOR_TEXTO, ESCALA_TEXTO, topleft=(x, y))
            y += (ALTO + 4) * ESCALA_TEXTO
            restantes -= len(linea)

        # Flechita de "seguir" con rebote, abajo a la derecha de la burbuja
        if self.escrito and self.offset_x >= 0:
            f = flecha_img()
            rebote = REBOTE[int(self.tiempo * 6) % len(REBOTE)] * PIXEL
            pantalla.blit(f, (bx + (BURBUJA_W - 14) * PIXEL, by + (BURBUJA_H - 11) * PIXEL + rebote))


def entra_en_burbuja(texto):
    """True si el texto entra en la burbuja (para revisar las frases)."""
    lineas = wrap(texto, ESCALA_TEXTO, (BURBUJA_W - 2 * MARGEN[0]) * PIXEL)
    alto = len(lineas) * (ALTO + 4) * ESCALA_TEXTO
    return alto <= (BURBUJA_H - MARGEN[1] - 14) * PIXEL and all(
        len(l) * 6 * ESCALA_TEXTO <= (BURBUJA_W - 2 * MARGEN[0]) * PIXEL + ESCALA_TEXTO for l in lineas)
