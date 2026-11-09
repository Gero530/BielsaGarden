"""
Pantalla de logros (menú principal > LOGROS). Lista con scroll: cada logro es un tablón con el
ícono del personaje a la izquierda, el nombre al lado y abajo la descripción con el progreso.
Los pendientes se ven en gris; los completados, a color y con la fecha.

Los logros no dependen de la partida (ver logros.py). Rueda del mouse, flechas o arrastrar la
barra de la derecha para recorrer la lista.
"""
import pygame
import display
import logros
from settings import SCREEN_W, SCREEN_H
from scenes.base import Scene
from ui import intro_art as A
from ui.aviso_logro import icono
from ui.button import CartelButton, tablon
from ui.pixel_font import draw_pixel_text, wrap
from ui.widgets import _hueco

OSCURO = (30, 18, 6)
CREMA = (255, 240, 200)
DORADO = (255, 214, 64)
VISTA = pygame.Rect(56, 100, 866, 412)       # zona visible de la lista
TARJETA_W = 828                              # ancho de cada tablón (múltiplo de 3)
ICONO = 84
TEXTO_X = 24 + ICONO + 22                    # dónde empieza el texto dentro del tablón
TEXTO_W = TARJETA_W - TEXTO_X - 24
SEPARACION = 12
PASO_RUEDA = 60


def _texto_progreso(logro):
    actual, meta = logros.progreso(logro)
    if logro["clave"] == "toallin_tipos":
        return f"{actual}/{meta} tipos"
    if logro["clave"] == "niveles" and meta > 1:
        return f"{actual}/{meta} niveles"
    if logro["tipo"] == "maximo":
        return f"Mejor: {actual}/{meta}"
    if meta == 1:
        return "Pendiente"
    return f"{actual}/{meta}"


def _tarjeta(logro):
    """El tablón de un logro ya dibujado (a color o en gris)."""
    hecho = logros.completado(logro["id"])
    nombre = wrap(logro["nombre"].upper(), 2, TEXTO_W)
    desc = wrap(logro["descripcion"], 2, TEXTO_W)
    alto_texto = len(nombre) * 20 + 8 + len(desc) * 20 + 10 + 18
    alto = max(ICONO + 36, alto_texto + 36)
    alto += -alto % 3
    s = pygame.Surface((TARJETA_W, alto), pygame.SRCALPHA)
    s.blit(tablon("", TARJETA_W // 3, alto // 3, 3), (0, 0))
    # Ícono en un hueco tallado
    caja = pygame.Rect(18, (alto - ICONO - 12) // 2, ICONO + 12, ICONO + 12)
    s.blit(_hueco(caja.w, caja.h), caja)
    s.blit(icono(logro, ICONO), (caja.x + 6, caja.y + 6))
    # Nombre y descripción
    y = 18
    for linea in nombre:
        draw_pixel_text(s, linea, DORADO, 2, outline=OSCURO, topleft=(TEXTO_X, y))
        y += 20
    y += 8
    for linea in desc:
        draw_pixel_text(s, linea, CREMA, 2, outline=OSCURO, topleft=(TEXTO_X, y))
        y += 20
    y += 6
    # Progreso: barra tallada + texto (o la fecha si ya está)
    actual, meta = logros.progreso(logro)
    if hecho:
        draw_pixel_text(s, f"¡COMPLETADO!  {logros.fecha(logro['id']) or ''}", (140, 240, 110), 2,
                        outline=OSCURO, topleft=(TEXTO_X, y))
    else:
        if meta > 1:
            barra = pygame.Rect(TEXTO_X, y, 300, 18)
            s.blit(_hueco(barra.w, barra.h), barra)
            lleno = (barra.w - 6) * actual // meta // 3 * 3
            if lleno > 0:
                s.fill((226, 170, 40), (barra.x + 3, barra.y + 3, lleno, barra.h - 6))
                s.fill((255, 222, 96), (barra.x + 3, barra.y + 3, lleno, 3))
            draw_pixel_text(s, _texto_progreso(logro), CREMA, 2, outline=OSCURO,
                            midleft=(barra.right + 14, barra.centery))
        else:
            draw_pixel_text(s, _texto_progreso(logro), CREMA, 2, outline=OSCURO, topleft=(TEXTO_X, y))
    if not hecho:                                       # pendiente: todo en gris
        s = pygame.transform.grayscale(s)
        s.fill((170, 170, 170, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return s


class LogrosScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        # Toda la lista se dibuja una vez en una superficie alta; después solo se corre
        tarjetas = [_tarjeta(l) for l in logros.LOGROS]
        alto = sum(t.get_height() for t in tarjetas) + SEPARACION * (len(tarjetas) - 1)
        self.lista = pygame.Surface((TARJETA_W, alto), pygame.SRCALPHA)
        y = 0
        for t in tarjetas:
            self.lista.blit(t, (0, y))
            y += t.get_height() + SEPARACION
        self.scroll = 0.0
        self.max_scroll = max(0, alto - VISTA.h)
        self.barra = pygame.Rect(VISTA.right - 24, VISTA.y, 24, VISTA.h)
        self.arrastrando = None           # desde dónde se agarró la perilla (y del mouse, scroll)
        self.btn_volver = CartelButton("VOLVER", (SCREEN_W // 2, 552), self.volver, size=(70, 15))

    def volver(self):
        from scenes.menu import MenuScene
        self.game.change_scene(MenuScene(self.game))

    def _mover(self, cuanto):
        self.scroll = max(0.0, min(self.max_scroll, self.scroll + cuanto))

    def _perilla_rect(self):
        alto = max(42, self.barra.h * VISTA.h // max(1, self.lista.get_height()))
        recorrido = self.barra.h - alto
        y = self.barra.y + (recorrido * self.scroll / self.max_scroll if self.max_scroll else 0)
        return pygame.Rect(self.barra.x, int(y), self.barra.w, alto), recorrido

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.volver()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._mover(PASO_RUEDA)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self._mover(-PASO_RUEDA)
            elif event.key == pygame.K_PAGEDOWN:
                self._mover(VISTA.h - 40)
            elif event.key == pygame.K_PAGEUP:
                self._mover(-(VISTA.h - 40))
            return
        if event.type == pygame.MOUSEWHEEL:
            self._mover(-event.y * PASO_RUEDA)
            return
        if self.btn_volver.handle_event(event):
            return
        if self.max_scroll:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.barra.collidepoint(event.pos):
                perilla, recorrido = self._perilla_rect()
                if not perilla.collidepoint(event.pos):          # clic en la barra: salta ahí
                    u = (event.pos[1] - self.barra.y - perilla.h / 2) / max(1, recorrido)
                    self.scroll = max(0.0, min(1.0, u)) * self.max_scroll
                self.arrastrando = (event.pos[1], self.scroll)
            elif event.type == pygame.MOUSEMOTION and self.arrastrando:
                _, recorrido = self._perilla_rect()
                y0, s0 = self.arrastrando
                self.scroll = s0
                self._mover((event.pos[1] - y0) * self.max_scroll / max(1, recorrido))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.arrastrando = None

    def update(self, dt):
        self.t += dt

    def draw(self, surface):
        surface.blit(A.fondo_vivo(self.t), (0, 0))
        titulo = A.colgante_escalado("LOGROS", 96, 16, 1, self.t, cuerda=6)
        surface.blit(titulo, titulo.get_rect(midtop=(SCREEN_W // 2, 0)))
        hechos = logros.cantidad_completados()
        draw_pixel_text(surface, f"{hechos}/{len(logros.LOGROS)} COMPLETADOS", DORADO if hechos else CREMA, 2,
                        outline=OSCURO, midleft=(VISTA.x, 82))

        viejo = surface.get_clip()
        surface.set_clip(VISTA)
        surface.blit(self.lista, (VISTA.x, VISTA.y - int(self.scroll)))
        surface.set_clip(viejo)

        if self.max_scroll:
            surface.blit(_hueco(self.barra.w, self.barra.h), self.barra)
            perilla, _ = self._perilla_rect()
            estado = "hover" if self.arrastrando or perilla.collidepoint(display.get_mouse_pos()) else "normal"
            surface.blit(tablon("", perilla.w // 3, perilla.h // 3, 3, estado=estado), perilla)

        self.btn_volver.draw(surface)
        draw_pixel_text(surface, "RUEDA / FLECHAS: MOVER    ESC: VOLVER", (255, 255, 255), 2,
                        outline=(30, 40, 70), center=(SCREEN_W // 2, SCREEN_H - 12))
