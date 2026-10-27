"""
Diálogo con un personaje que habla (estilo Crazy Dave).

Uso:
    dialogo = Dialogo(["Hola", "Chau"])
    dialogo.manejar_evento(evento)   # click / ESPACIO avanza, ESC saltea
    dialogo.actualizar(dt)
    dialogo.dibujar(pantalla)
    if dialogo.terminado: ...

Si falta alguna imagen o la fuente, se dibuja un placeholder en su lugar.
"""
import os
import pygame
from settings import SCREEN_W, SCREEN_H
from ui.sprites import ASSETS_DIR

# === IMÁGENES DEL DIÁLOGO: poné tus archivos acá (rutas relativas a pvz_pygame/assets/) ===
PERSONAJE_IMG  = "dialogo/bielsa1.png"
BURBUJA_IMG    = "dialogo/burbuja.png"
FUENTE_DIALOGO = "fuentes/pixel.ttf"

# === TAMAÑOS Y POSICIONES (en píxeles de pantalla, el juego mide 1000x600) ===
PERSONAJE_TAM = (160, 240)                                  # la imagen se escala a este tamaño
PERSONAJE_POS = (20, SCREEN_H - PERSONAJE_TAM[1])           # esquina sup. izq.: abajo a la izquierda
BURBUJA_TAM   = (432, 176)                                  # 108x44 dibujada x4
# La punta de la colita (x = 0 de la burbuja) queda pegada al borde derecho del personaje
BURBUJA_POS   = (PERSONAJE_POS[0] + PERSONAJE_TAM[0], PERSONAJE_POS[1] - 60)
MARGEN_TEXTO  = (52, 20)                                    # dónde empieza el texto, relativo a la burbuja
AREA_TEXTO    = (360, 136)                                  # ancho y alto del área de texto
TAM_FUENTE    = 28
COLOR_TEXTO   = (20, 20, 20)
INTERLINEADO  = 4                                           # px extra entre líneas

# === COMPORTAMIENTO ===
VELOCIDAD_TEXTO   = 40      # letras por segundo
VELOCIDAD_ENTRADA = 1200    # px/s con que el personaje entra desde la izquierda (0 = sin animación)
OSCURIDAD_FONDO   = 120     # 0 = sin overlay, 255 = negro total
PARPADEO          = 0.5     # segundos entre parpadeos del indicador "seguir"


def _cargar_imagen(ruta, tam):
    """Carga y escala con vecino más cercano (pixel art). None si no existe."""
    path = os.path.join(ASSETS_DIR, ruta)
    if not os.path.exists(path):
        return None
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), tam)


def _placeholder_personaje():
    surf = pygame.Surface(PERSONAJE_TAM, pygame.SRCALPHA)
    surf.fill((140, 140, 140))
    pygame.draw.rect(surf, (50, 50, 50), surf.get_rect(), 4)
    txt = pygame.font.Font(None, 30).render("PERSONAJE", False, (30, 30, 30))
    surf.blit(txt, txt.get_rect(center=surf.get_rect().center))
    return surf


def _placeholder_burbuja():
    """Se dibuja a 1/4 del tamaño y se agranda x4 para que tenga look pixel art."""
    w, h = BURBUJA_TAM[0] // 4, BURBUJA_TAM[1] // 4          # 108x44
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cuerpo = pygame.Rect(8, 0, w - 8, h)                      # el cuerpo empieza en x=32 (8*4)
    pygame.draw.rect(surf, (255, 255, 255), cuerpo, border_radius=4)
    pygame.draw.rect(surf, (0, 0, 0), cuerpo, 1, border_radius=4)
    # Colita: punta en x=0 abajo, base apoyada sobre el borde izquierdo del cuerpo
    colita = [(0, h - 4), (9, h - 14), (9, h - 7)]
    pygame.draw.polygon(surf, (255, 255, 255), colita)
    pygame.draw.lines(surf, (0, 0, 0), False, [colita[1], colita[0], colita[2]], 1)
    return pygame.transform.scale(surf, BURBUJA_TAM)


def _cargar_fuente():
    path = os.path.join(ASSETS_DIR, FUENTE_DIALOGO)
    return pygame.font.Font(path if os.path.exists(path) else None, TAM_FUENTE)


def partir_lineas(texto, fuente, ancho):
    """Word wrap: parte el texto en líneas que entren en `ancho` píxeles."""
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        # shortcut: una palabra sola más ancha que la burbuja se sale; partirla por letras si pasa
        if fuente.size(prueba)[0] <= ancho or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


class Dialogo:
    def __init__(self, mensajes):
        self.mensajes = list(mensajes)
        self.indice = 0
        self.letras = 0.0             # cuántas letras del mensaje actual se ven
        self.tiempo = 0.0             # para el parpadeo del indicador
        self.offset_x = -(PERSONAJE_POS[0] + PERSONAJE_TAM[0] + BURBUJA_TAM[0]) if VELOCIDAD_ENTRADA else 0
        self.terminado = not self.mensajes

        self.fuente = _cargar_fuente()
        self.img_personaje = _cargar_imagen(PERSONAJE_IMG, PERSONAJE_TAM) or _placeholder_personaje()
        self.img_burbuja = _cargar_imagen(BURBUJA_IMG, BURBUJA_TAM) or _placeholder_burbuja()
        self._preparar_mensaje()

    @property
    def activo(self):
        return not self.terminado

    def _preparar_mensaje(self):
        texto = self.mensajes[self.indice] if self.mensajes else ""
        self.lineas = partir_lineas(texto, self.fuente, AREA_TEXTO[0])
        self.total_letras = sum(len(l) for l in self.lineas)
        self.letras = 0.0

    @property
    def escrito(self):
        """True cuando el mensaje actual terminó de escribirse."""
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
            elif evento.key == pygame.K_SPACE:
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
        self.letras = min(self.total_letras, self.letras + VELOCIDAD_TEXTO * dt)

    def dibujar(self, pantalla):
        if self.terminado:
            return
        sombra = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, OSCURIDAD_FONDO))
        pantalla.blit(sombra, (0, 0))

        ox = int(self.offset_x)
        pantalla.blit(self.img_personaje, (PERSONAJE_POS[0] + ox, PERSONAJE_POS[1]))
        bx, by = BURBUJA_POS[0] + ox, BURBUJA_POS[1]
        pantalla.blit(self.img_burbuja, (bx, by))

        # Texto letra por letra, repartido entre las líneas ya partidas
        x, y = bx + MARGEN_TEXTO[0], by + MARGEN_TEXTO[1]
        restantes = int(self.letras)
        for linea in self.lineas:
            if restantes <= 0:
                break
            img = self.fuente.render(linea[:restantes], False, COLOR_TEXTO)
            pantalla.blit(img, (x, y))
            restantes -= len(linea)
            y += self.fuente.get_linesize() + INTERLINEADO

        # Indicador "▼" parpadeando abajo a la derecha del área de texto
        if self.escrito and int(self.tiempo / PARPADEO) % 2 == 0:
            ix = bx + MARGEN_TEXTO[0] + AREA_TEXTO[0] - 16
            iy = by + MARGEN_TEXTO[1] + AREA_TEXTO[1] - 16
            pygame.draw.polygon(pantalla, COLOR_TEXTO, [(ix, iy), (ix + 16, iy), (ix + 8, iy + 10)])
