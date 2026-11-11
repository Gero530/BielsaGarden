"""
Catálogo (almanaque): pestañas Personajes y Zombies. A la izquierda, una grilla de retratos
animados con su nombre; a la derecha, la ficha del elegido: personaje grande sobre el césped,
datos, descripción y una frase de Bielsa.

Se elige con clic o con las flechas y queda elegido. TAB cambia de pestaña.
Los zombies que todavía no aparecieron en ninguna partida se ven como silueta con "???"
(se guardan en logros.json, conjunto "zombies_vistos"; los anota gameplay.py).

Los textos (nombre, descripción, frase de Bielsa) están en data/catalogo.py; los números
salen solos de settings.py.
"""
import pygame
import display
import logros
from settings import SCREEN_W, SCREEN_H, PLANT_DATA, ZOMBIE_DATA
from scenes.base import Scene
from data.catalogo import PERSONAJES, ZOMBIES
from entities.plants import draw_plant_icon
from entities.zombies import ZOMBIE_CLASSES
from world.grid import Grid
from ui.button import CartelButton, tablon
from ui.pixel_font import draw_pixel_text, draw_pixel_lines, wrap, text_width
from ui.sprites import draw_sprite, has_sprite
from ui.widgets import Tabs, _hueco
from ui import intro_art as A, sonidos

TIP_W = 340               # ancho del pergamino de la pantalla de equipo (draw_tooltip)
_cache = {}


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


PANEL = pygame.Rect(24, 120, 456, 432)        # tablón con la grilla de retratos
PAGINA = pygame.Rect(500, 120, 476, 432)      # pergamino con la ficha
GAP_CELDA = 9
DORADO, CREMA, OSCURO = (255, 214, 64), (255, 240, 200), (30, 18, 6)
FONDO_CELDA, PISO_CELDA = (58, 96, 44), (84, 152, 60)
CIELO, CESPED = (122, 190, 240), ((96, 168, 70), (84, 152, 60))
MARRON = (120, 76, 36)          # etiquetas de los datos en la ficha
CITA = (112, 40, 18)            # la frase de Bielsa
QUIETOS = {"kenny": 0, "picante": 0}   # sus animaciones son la explosión: en el catálogo van quietos
BIELSA = {"id": "_bielsa_catalogo", "icono": ("retrato", "tutorial")}
OCULTO_DESC = "Todavía no se cruzó con este zombie. Cuando aparezca en una partida, acá va a estar su ficha."
OCULTO_CITA = "No hablo de rivales que no estudié. Cuando lo vea, le cuento."


def etiqueta(key, zombie):
    """Nombre corto bajo el retrato: "CARTMAN", "CONO", "PÉRTIGA"..."""
    nombre = (ZOMBIES if zombie else PERSONAJES)[key]["nombre"]
    if zombie:
        for prefijo in ("Zombie con ", "Zombie del ", "Zombie ", "Cangrejo "):
            if nombre.startswith(prefijo) and len(nombre) > len(prefijo):
                nombre = nombre[len(prefijo):]
                break
    else:
        nombre = nombre.split()[-1]
    return nombre.upper()


def datos_ficha(key, zombie):
    """[(etiqueta, valor)] para el costado del escenario de la ficha (hasta 4)."""
    if not zombie:
        d = PLANT_DATA[key]
        filas = [("COSTO", d["costo"])]
        if "dano" in d:
            filas.append(("DAÑO", d["dano"]))
        return filas + [("VIDA", d["vida"]), ("RECARGA", f"{d['recarga']:g} S")]
    d = ZOMBIE_DATA[key]
    filas = [("VIDA", d["vida"])]
    if d.get("armadura"):
        filas.append(("ARMADURA", d["armadura"]))
    if d.get("escudo"):
        filas.append(("ESCUDO", d["escudo"]))
    filas.append(("MORDIDA", f"{d['dps']}/S" if d["dps"] else "UN GOLPE"))
    filas.append(("VELOCIDAD", velocidad_txt(d["velocidad"]).upper()))
    return filas[:4]


def silueta(img):
    """La misma imagen en negro (respeta la transparencia)."""
    s = img.copy()
    s.fill((26, 20, 30, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return s


class CatalogoScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.tab = "PERSONAJES"
        self.tabs = Tabs(["PERSONAJES", "ZOMBIES"], (PANEL.x + 24, PANEL.y - 36), self.cambiar, tab_size=(60, 14))
        self.volver_btn = CartelButton("VOLVER", (96, 40), self.volver, size=(50, 14))
        self.grid = Grid()
        self.zombies = {k: ZOMBIE_CLASSES[k](0, self.grid) for k in ZOMBIES}
        self.vistos = logros.conjunto("zombies_vistos")
        self.sel = {"PERSONAJES": 0, "ZOMBIES": 0}      # cada pestaña recuerda su elegido
        self.hover = None
        self.t = 0.0
        self._zcanvas = pygame.Surface((160, 150), pygame.SRCALPHA)
        self.armar()

    # ------------------------------------------------------------------
    @property
    def es_zombie(self):
        return self.tab == "ZOMBIES"

    def descubierto(self, key):
        return not self.es_zombie or key in self.vistos

    def cambiar(self, tab):
        self.tab = tab
        self.tabs.active = self.tabs.names.index(tab)
        self.armar()

    def armar(self):
        """Grilla centrada en el tablón: 3 columnas para los personajes, 4 para los zombies."""
        self.keys = list(ZOMBIES if self.es_zombie else PERSONAJES)
        n = len(self.keys)
        self.cols = 3 if n <= 9 else 4
        filas = -(-n // self.cols)
        zona = pygame.Rect(PANEL.x + 18, PANEL.y + 18, PANEL.w - 36, PANEL.h - 42)
        cw = (zona.w - (self.cols - 1) * GAP_CELDA) // self.cols // 3 * 3
        ch = min((zona.h - (filas - 1) * GAP_CELDA) // filas, cw) // 3 * 3
        x0 = zona.centerx - (self.cols * cw + (self.cols - 1) * GAP_CELDA) // 2
        y0 = zona.centery - (filas * ch + (filas - 1) * GAP_CELDA) // 2
        self.celdas = []
        for i in range(n):
            f, c = divmod(i, self.cols)
            self.celdas.append(pygame.Rect(x0 + c * (cw + GAP_CELDA), y0 + f * (ch + GAP_CELDA), cw, ch))

    def elegir(self, i):
        if i != self.sel[self.tab]:
            sonidos.reproducir("seleccionar")
        self.sel[self.tab] = i

    def volver(self):
        from scenes.menu import MenuScene
        self.game.change_scene(MenuScene(self.game))

    # ------------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            i, n = self.sel[self.tab], len(self.keys)
            if event.key == pygame.K_ESCAPE:
                self.volver()
            elif event.key == pygame.K_TAB:
                self.cambiar("ZOMBIES" if self.tab == "PERSONAJES" else "PERSONAJES")
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.elegir(min(n - 1, i + 1))
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.elegir(max(0, i - 1))
            elif event.key in (pygame.K_DOWN, pygame.K_s) and i + self.cols < n:
                self.elegir(i + self.cols)
            elif event.key in (pygame.K_UP, pygame.K_w) and i - self.cols >= 0:
                self.elegir(i - self.cols)
            return
        if self.volver_btn.handle_event(event) or self.tabs.handle_event(event):
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.celdas):
                if r.collidepoint(event.pos):
                    self.elegir(i)
                    return

    def update(self, dt):
        self.t += dt
        mouse = display.get_mouse_pos()
        self.hover = next((i for i, r in enumerate(self.celdas) if r.collidepoint(mouse)), None)

    # ------------------------------------------------------------------
    # Dibujo de los personajes
    # ------------------------------------------------------------------
    def _img_zombie(self, key, t):
        """El zombie a tamaño de juego (x2, con cono o balde) en una superficie suelta."""
        lienzo = self._zcanvas
        lienzo.fill((0, 0, 0, 0))
        self.zombies[key].draw_icon(lienzo, (lienzo.get_width() // 2, lienzo.get_height() - 4), None, t)
        caja = lienzo.get_bounding_rect()
        return lienzo.subsurface(caja).copy() if caja.w and caja.h else None

    def dibujar_personaje(self, surface, key, pie, escala, t, oculto=False):
        """Dibuja el personaje o zombie con los pies en `pie` (midbottom). escala: 1 = tamaño de
        juego; para los zombies 0.5 = la mitad exacta (píxeles enteros)."""
        if self.es_zombie:
            img = self._img_zombie(key, t)
            if img is None:
                return
            if escala != 1:
                img = pygame.transform.scale(img, (max(1, int(img.get_width() * escala)),
                                                   max(1, int(img.get_height() * escala))))
        else:
            lienzo = pygame.Surface((180, 180), pygame.SRCALPHA)
            if has_sprite(key):
                draw_sprite(lienzo, key, (90, 90), escala, t, frame=QUIETOS.get(key))
            else:
                draw_plant_icon(lienzo, key, (90, 90), escala)
            caja = lienzo.get_bounding_rect()
            if not caja.w:
                return
            img = lienzo.subsurface(caja)
        if oculto:
            img = silueta(img)
        surface.blit(img, img.get_rect(midbottom=pie))

    # ------------------------------------------------------------------
    def draw(self, surface):
        surface.blit(A.fondo_vivo(self.t), (0, 0))      # el paisaje del menú con nubes y el bus
        titulo = A.colgante_escalado("CATÁLOGO", 96, 16, 1, self.t, cuerda=6)
        surface.blit(titulo, titulo.get_rect(midtop=(SCREEN_W // 2, 0)))
        self.volver_btn.draw(surface)

        surface.blit(tablon("", PANEL.w // 3, PANEL.h // 3, 3), PANEL)
        self.tabs.draw(surface)
        for i, (key, r) in enumerate(zip(self.keys, self.celdas)):
            self.dibujar_celda(surface, i, key, r)
        if self.es_zombie:
            self.dibujar_contador(surface)

        self.dibujar_ficha(surface, self.keys[self.sel[self.tab]])

    def dibujar_celda(self, surface, i, key, r):
        elegida = i == self.sel[self.tab]
        if elegida or i == self.hover:                      # marco: dorado el elegido, claro al pasar
            surface.fill(DORADO if elegida else (232, 186, 112), r.inflate(6, 6))
        surface.blit(_hueco(r.w, r.h), r)
        adentro = r.inflate(-6, -6)
        alto_txt = 14 if self.es_zombie else 18
        surface.fill((74, 122, 56) if elegida else FONDO_CELDA, adentro)
        piso = pygame.Rect(adentro.x, adentro.bottom - alto_txt - 9, adentro.w, 9)
        surface.fill(PISO_CELDA, piso)
        surface.fill((52, 32, 14), (adentro.x, adentro.bottom - alto_txt, adentro.w, alto_txt))
        oculto = not self.descubierto(key)
        old = surface.get_clip()
        surface.set_clip(adentro)
        t = None if oculto else self.t + i * 0.37          # cada uno con su desfase
        escala = 0.5 if self.es_zombie else 0.67
        self.dibujar_personaje(surface, key, (r.centerx, piso.y + 6), escala, t, oculto)
        surface.set_clip(old)
        texto = "???" if oculto else etiqueta(key, self.es_zombie)
        draw_pixel_text(surface, texto, DORADO if elegida else CREMA, 1 if self.es_zombie else 2,
                        center=(r.centerx, adentro.bottom - alto_txt // 2))

    def dibujar_contador(self, surface):
        """Cuántos zombies se descubrieron ("9/15"), en el hueco que deja la última fila de la grilla
        (o abajo del tablón si la grilla está completa). Grande si entra en el hueco."""
        vistos = sum(1 for k in self.keys if k in self.vistos)
        texto = f"{vistos}/{len(self.keys)}"
        ultima = self.celdas[-1]
        libres = self.cols - 1 - (len(self.keys) - 1) % self.cols
        if libres:
            zona = pygame.Rect(ultima.right + GAP_CELDA, ultima.y, PANEL.right - 18 - ultima.right - GAP_CELDA, ultima.h)
            esc = 3 if text_width(texto, 3) + 8 <= zona.w else 2
            draw_pixel_text(surface, texto, DORADO, esc, outline=OSCURO, center=zona.center)
        else:
            draw_pixel_text(surface, texto, DORADO, 2, outline=OSCURO, center=(PANEL.centerx, PANEL.bottom + 24))

    def dibujar_ficha(self, surface, key):
        surface.blit(pergamino(PAGINA.w, PAGINA.h), PAGINA)
        x, ancho = PAGINA.x + 22, PAGINA.w - 48
        oculto = not self.descubierto(key)
        info = (ZOMBIES if self.es_zombie else PERSONAJES)[key]

        nombre = "???" if oculto else info["nombre"].upper()
        esc = 3 if text_width(nombre, 3) <= ancho else 2
        draw_pixel_text(surface, nombre, TINTA_ROJA, esc, topleft=(x, PAGINA.y + 20))

        # Escenario: cielo y césped en un hueco tallado, con el personaje grande y animado
        esc_r = pygame.Rect(x, PAGINA.y + 56, 216, 153)
        surface.blit(_hueco(esc_r.w, esc_r.h), esc_r)
        dentro = esc_r.inflate(-6, -6)
        surface.fill(CIELO, dentro)
        suelo = dentro.bottom - 30
        for j, cx in enumerate(range(dentro.x, dentro.right, 24)):
            surface.fill(CESPED[j % 2], (cx, suelo, min(24, dentro.right - cx), dentro.bottom - suelo))
        surface.fill((70, 130, 50), (dentro.x, suelo, dentro.w, 3))
        old = surface.get_clip()
        surface.set_clip(dentro)
        escala = 1 if self.es_zombie else 1.4             # personajes un poco más grandes que en el juego
        self.dibujar_personaje(surface, key, (dentro.centerx, suelo + 18), escala, None if oculto else self.t, oculto)
        surface.set_clip(old)

        # Datos al costado del escenario: etiqueta a la izquierda, valor a la derecha, centrados en alto
        filas = datos_ficha(key, self.es_zombie)
        dx, derecha = esc_r.right + 16, PAGINA.right - 26
        y = esc_r.centery - (len(filas) * 34 - 14) // 2
        for etiq, valor in filas:
            draw_pixel_text(surface, etiq, MARRON, 2, topleft=(dx, y))
            draw_pixel_text(surface, "???" if oculto else str(valor), TINTA, 2, topright=(derecha, y))
            surface.fill(PAPEL_OSC, (dx, y + 19, derecha - dx, 2))
            y += 34

        # Descripción
        draw_pixel_lines(surface, OCULTO_DESC if oculto else info["descripcion"], TINTA, 2,
                         (x, esc_r.bottom + 14), ancho, gap=20)

        # Frase de Bielsa, abajo de todo, con su cara
        cita = OCULTO_CITA if oculto else info.get("bielsa", "")
        if cita:
            from ui.aviso_logro import icono
            lineas = wrap(f'"{cita}"', 2, ancho - 58)
            alto = max(48, len(lineas) * 20)
            y0 = PAGINA.bottom - 30 - alto
            surface.fill(PAPEL_OSC, (x, y0 - 12, ancho, 2))
            surface.blit(icono(BIELSA, 46), (x, y0 + (alto - 46) // 2))
            y_txt = y0 + (alto - len(lineas) * 20) // 2
            for k, linea in enumerate(lineas):
                draw_pixel_text(surface, linea, CITA, 2, topleft=(x + 58, y_txt + k * 20))


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
