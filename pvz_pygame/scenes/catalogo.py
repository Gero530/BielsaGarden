"""
Catálogo (almanaque): pestañas Personajes y Zombies, grilla con sus sprites y un cuadro
con nombre, descripción y stats al pasar el mouse.

Los textos están en data/catalogo.py; los números salen solos de settings.py.
"""
import pygame
import display
from settings import SCREEN_W, SCREEN_H, PLANT_DATA, ZOMBIE_DATA
from scenes.base import Scene
from data.catalogo import PERSONAJES, ZOMBIES
from entities.plants import draw_plant_icon
from entities.zombies import ZOMBIE_CLASSES
from world.grid import Grid
from ui.button import CartelButton, tablon, apretado
from ui.pixel_font import draw_pixel_text, draw_pixel_lines, wrap, text_width
from ui import intro_art as A

CELDA_W, CELDA_H = 104, 140      # el gigante (48x64 al doble) entra entero
GAP = 10
TIP_W = 340               # ancho del pergamino de descripción (px de pantalla)
TXT = (20, 12, 4)

_cache = {}


def celda_img(hover):
    """Marquito de papel de cada personaje (CELDA / 2 de dibujo, x2)."""
    key = ("celda", hover)
    if key not in _cache:
        w, h = CELDA_W // 2, CELDA_H // 2
        s = pygame.Surface((w, h))
        s.fill((255, 230, 60) if hover else (60, 40, 24))
        s.fill((225, 210, 160), (1, 1, w - 2, h - 2))
        s.fill((60, 40, 24), (3, 3, w - 6, h - 6))
        s.fill((150, 190, 120) if hover else (120, 170, 90), (4, 4, w - 8, h - 8))
        s.fill((170, 210, 140) if hover else (140, 190, 110), (4, 4, w - 8, 2))
        _cache[key] = pygame.transform.scale(s, (CELDA_W, CELDA_H))
    return _cache[key]


def velocidad_txt(v):
    return "lenta" if v < 14 else ("normal" if v <= 20 else "rápida")


def stats_planta(key):
    d = PLANT_DATA[key]
    lineas = [f"Costo: {d['costo']}", f"Vida: {d['vida']}", f"Recarga: {d['recarga']:g} s"]
    if "dano" in d:
        lineas.insert(1, f"Daño: {d['dano']}")
    return lineas


def stats_zombie(key):
    d = ZOMBIE_DATA[key]
    vida = d["vida"] + d.get("armadura", 0) + d.get("escudo", 0)
    mordida = f"{d['dps']} por segundo" if d["dps"] else "aplasta de un golpe"
    return [f"Vida: {vida}", f"Daño: {mordida}", f"Velocidad: {velocidad_txt(d['velocidad'])}"]


class CatalogoScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.tab = "PERSONAJES"
        self.tabs = [CartelButton(name, (SCREEN_W // 2 + dx, 128), lambda n=name: self.cambiar(n), size=(80, 14))
                     for name, dx in (("PERSONAJES", -130), ("ZOMBIES", 130))]
        self.volver_btn = CartelButton("VOLVER", (96, 40), self.volver, size=(50, 14))
        self.grid = Grid()
        self.zombies = {k: ZOMBIE_CLASSES[k](0, self.grid) for k in ZOMBIES}
        self.hover = None
        self.t = 0.0
        self.armar()

    def cambiar(self, tab):
        self.tab = tab
        self.armar()

    def armar(self):
        """Ubica las celdas de la pestaña actual (centradas, hasta 7 por fila)."""
        keys = list(PERSONAJES if self.tab == "PERSONAJES" else ZOMBIES)
        por_fila = 6 if self.tab == "PERSONAJES" else 7
        self.celdas = []
        for i, k in enumerate(keys):
            fila, col = divmod(i, por_fila)
            n = min(por_fila, len(keys) - fila * por_fila)
            x0 = SCREEN_W // 2 - (n * CELDA_W + (n - 1) * GAP) // 2
            r = pygame.Rect(x0 + col * (CELDA_W + GAP), 170 + fila * (CELDA_H + GAP), CELDA_W, CELDA_H)
            self.celdas.append((k, r))

    def volver(self):
        from scenes.menu import MenuScene
        self.game.change_scene(MenuScene(self.game))

    # ------------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.volver()
            return
        if self.volver_btn.handle_event(event):
            return
        for b in self.tabs:
            if b.handle_event(event):
                return

    def update(self, dt):
        self.t += dt
        mouse = display.get_mouse_pos()
        self.hover = next((k for k, r in self.celdas if r.collidepoint(mouse)), None)

    def draw(self, surface):
        surface.blit(A.fondo_vivo(self.t), (0, 0))      # el paisaje del menú con nubes y el bus
        titulo = A.colgante_escalado("CATÁLOGO", 80, 18, 2, self.t)
        surface.blit(titulo, titulo.get_rect(midtop=(SCREEN_W // 2, 0)))
        self.volver_btn.draw(surface)
        for b in self.tabs:
            activa = b.text == self.tab
            img = tablon(b.text, *b.size, b.esc, b.texto_esc,
                         estado="apretado" if apretado(b) else ("hover" if activa else "normal"))
            surface.blit(img, b.rect.move(0, -6 if activa else 0))

        for k, r in self.celdas:
            surface.blit(celda_img(k == self.hover), r)
            old = surface.get_clip()
            surface.set_clip(r.inflate(-8, -8))
            if self.tab == "PERSONAJES":
                draw_plant_icon(surface, k, (r.centerx, r.centery + 2), 0.67)
            else:
                self.zombies[k].draw_icon(surface, (r.centerx, r.bottom - 8), (r.w - 8, r.h - 12))
            surface.set_clip(old)

        if self.hover:
            self.draw_tooltip(surface, self.hover)

        quien = "UN PERSONAJE" if self.tab == "PERSONAJES" else "UN ZOMBIE"
        draw_pixel_text(surface, f"PASÁ EL MOUSE POR {quien} PARA VER SU DESCRIPCIÓN", (255, 255, 255), 2,
                        outline=(30, 40, 70), center=(SCREEN_W // 2, SCREEN_H - 20))

    def draw_tooltip(self, surface, key):
        planta = self.tab == "PERSONAJES"
        info = (PERSONAJES if planta else ZOMBIES)[key]
        celda = next(r for k, r in self.celdas if k == key)
        draw_tooltip(surface, info, stats_planta(key) if planta else stats_zombie(key), celda)


PAPEL, PAPEL_OSC, BORDE_PAPEL = (238, 224, 184), (212, 192, 142), (58, 34, 14)
TINTA, TINTA_ROJA = (36, 22, 10), (150, 36, 18)
MARGEN_TIP = 22


def pergamino(w, h):
    """Pergamino opaco (x2): borde oscuro, papel claro, sombra abajo, esquinas gastadas y fibras."""
    key = ("pergamino", w, h)
    if key not in _cache:
        a, b = w // 2, h // 2
        s = pygame.Surface((a, b), pygame.SRCALPHA)
        s.fill((0, 0, 0, 90), (2, 2, a - 2, b - 2))
        s.fill(BORDE_PAPEL, (0, 0, a - 2, b - 2))
        s.fill(PAPEL, (1, 1, a - 4, b - 4))
        s.fill(PAPEL_OSC, (1, b - 5, a - 4, 2))
        for x, y in ((0, 0), (a - 3, 0), (0, b - 3), (a - 3, b - 3)):
            s.set_at((x, y), (0, 0, 0, 0))
        for x in range(6, a - 8, 9):
            s.set_at((x, 3 + x % 5), PAPEL_OSC)
        _cache[key] = pygame.transform.scale(s, (a * 2, b * 2))
    return _cache[key]


def draw_tooltip(surface, info, stats, ancla):
    """Pergamino con nombre (rojo), descripción y datos, AL COSTADO de `ancla` (el cuadro o la
    carta que estás mirando): a la derecha, o a la izquierda si no entra. Nunca lo tapa y nunca
    queda cortado en los bordes de la pantalla."""
    ancho_txt = TIP_W - 2 * MARGEN_TIP
    lineas = wrap(info["descripcion"], 2, ancho_txt)
    esc_nombre = 3 if text_width(info["nombre"], 3) <= ancho_txt else 2
    alto = MARGEN_TIP + 8 * esc_nombre + 12 + len(lineas) * 20 + 12 + len(stats) * 20 + MARGEN_TIP
    r = pygame.Rect(0, 0, TIP_W, alto // 2 * 2)
    r.top = ancla.top
    if ancla.right + 10 + TIP_W <= SCREEN_W - 8:
        r.left = ancla.right + 10
    elif ancla.left - 10 - TIP_W >= 8:
        r.right = ancla.left - 10
    else:                                                    # ni a la derecha ni a la izquierda: abajo
        r.centerx, r.top = ancla.centerx, ancla.bottom + 10
    r.clamp_ip(pygame.Rect(8, 8, SCREEN_W - 16, SCREEN_H - 16))
    surface.blit(pergamino(r.w, r.h), r)
    x, y = r.x + MARGEN_TIP, r.y + MARGEN_TIP
    draw_pixel_text(surface, info["nombre"], TINTA_ROJA, esc_nombre, topleft=(x, y))
    y = draw_pixel_lines(surface, info["descripcion"], TINTA, 2, (x, y + 8 * esc_nombre + 12), ancho_txt, gap=20) + 4
    surface.fill(PAPEL_OSC, (x, y, ancho_txt, 2))           # raya que separa los datos
    y += 10
    for linea in stats:
        draw_pixel_text(surface, linea, TINTA, 2, topleft=(x, y))
        y += 20
