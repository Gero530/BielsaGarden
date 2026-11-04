"""
Menú principal con la intro estilo South Park en pixel art.

Al arrancar:  la cabeza de Stan se acerca, caen las calles/cuerpos/cabezas de Cartman,
Kyle, Stan y Kenny en la parada del bus, todo sincronizado con la canción. Cuando
aterriza la cabeza de Cartman aparecen los botones (JUGAR / OPCIONES / SALIR) y la
canción sigue sonando de fondo, con el bus pasando y los chicos cabeceando al ritmo.

Se puede saltear la intro con un clic, Enter, Espacio o Esc. Cuando se vuelve al menú
(desde Opciones o desde una partida) no se repite la intro: queda el menú directo.
"""
import pygame
import display
from settings import SCREEN_W, SCREEN_H, COLORS
from scenes.base import Scene
from ui import intro_art as A, musica
from ui.pixel_font import draw_pixel_text
from settings import MUSICA_DURACION as DURACION

BOTONES = ["JUGAR", "OPCIONES", "SALIR"]
BTN_X = 805
BTN_Y = [225, 310, 395]
BTN_W, BTN_H = 114, 26            # tamaño interno (se agranda x3 en pantalla)
T_BOTON = 0.16                    # retraso entre un botón y el siguiente al aparecer
SALIDA = 0.5                      # fundido a negro al entrar a la partida (s)
EMPIEZA_SIN_INTRO = 3.4           # segundo de la canción desde el que suena si se vuelve al menú


def draw_menu_background(surface):
    """Fondo de franjas de césped (lo usa la pantalla de opciones)."""
    surface.fill(COLORS["cesped_2"])
    for i in range(0, SCREEN_W, 80):
        if (i // 80) % 2 == 0:
            pygame.draw.rect(surface, COLORS["cesped_1"], (i, 0, 80, SCREEN_H))


class MenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.kids = A.load_kids()
        self.world = pygame.Surface((A.W, A.H))
        self.canvas = pygame.Surface((A.W, A.H))
        self.escalado = pygame.Surface((A.W * A.ESCALA, A.H * A.ESCALA))
        self.intro = not getattr(game, "intro_done", False)
        self.shift = 0.0                      # cuánto se adelantó la intro al saltearla
        self.sel = 0
        self.salida = None                    # (acción, tiempo) mientras se hace el fundido
        self._img = {}

        # Música: arranca con la intro; si se vuelve al menú sigue sonando o arranca sin la intro
        if self.intro:
            self.mt = 0.0
            musica.reproducir(0.0)
        elif musica.sonando():
            self.mt = musica.tiempo() or EMPIEZA_SIN_INTRO
        else:
            self.mt = EMPIEZA_SIN_INTRO
            musica.reproducir(EMPIEZA_SIN_INTRO)
        self.vt = self.mt if self.intro else 99.0   # tiempo de la coreografía
        self.t_menu = A.T_MENU if self.intro else -10.0

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------
    def jugar(self):
        if self.salida is None:
            self.salida = ("jugar", 0.0)
            musica.desvanecer(int(SALIDA * 1000))

    def opciones(self):
        from scenes.options import OptionsScene
        self.game.change_scene(OptionsScene(self.game))

    def salir(self):
        self.game.quit()

    def _activar(self, i):
        (self.jugar, self.opciones, self.salir)[i]()

    def _menu_visible(self):
        return self.vt >= self.t_menu + 0.1

    def _saltar(self):
        """Salta al final de la intro (los chicos ya armados y los botones a la vista)."""
        if self.vt < A.T_MENU + 0.5:
            self.shift = A.T_MENU + 0.5 - self.mt

    # ------------------------------------------------------------------
    # Eventos
    # ------------------------------------------------------------------
    def _rect_boton(self, i):
        r = pygame.Rect(0, 0, BTN_W * A.ESCALA, BTN_H * A.ESCALA)
        r.center = (BTN_X, BTN_Y[i])
        return r

    def handle_event(self, event):
        if self.salida is not None:
            return
        if not self._menu_visible():
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE)):
                self._saltar()
            return
        if event.type == pygame.MOUSEMOTION:
            for i in range(len(BOTONES)):
                if self._rect_boton(i).collidepoint(event.pos):
                    self.sel = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(BOTONES)):
                if self._rect_boton(i).collidepoint(event.pos):
                    self.sel = i
                    self._activar(i)
                    return
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(BOTONES)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(BOTONES)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activar(self.sel)

    # ------------------------------------------------------------------
    # Tiempo
    # ------------------------------------------------------------------
    def update(self, dt):
        # Reloj de la canción: avanza con dt y se va corrigiendo con el reloj del audio
        self.mt += dt
        ref = musica.tiempo()
        if ref is not None:
            err = ref - self.mt
            if abs(err) > 0.25:
                self.mt = ref
            else:
                self.mt += err * 0.15
        if self.intro:
            self.vt = max(self.vt, self.mt + self.shift)
        if self.intro and self.vt >= A.T_MENU + 0.8:
            self.game.intro_done = True
        if self.salida is not None:
            acc, t = self.salida
            t += dt
            self.salida = (acc, t)
            if t >= SALIDA:
                from scenes.gameplay import GameplayScene
                self.game.change_scene(GameplayScene(self.game, level_index=0))

    # ------------------------------------------------------------------
    # Dibujo
    # ------------------------------------------------------------------
    def _beat(self):
        """1 durante el primer tramo de cada pulso de la canción (los chicos bajan la cabeza al ritmo)."""
        fase = ((self.mt % DURACION) - A.PULSO_FASE) / A.PULSO % 1.0
        return 1 if fase < 0.28 else 0

    def _extras(self, world):
        t = min(self.vt, 99.0)
        if t >= 1.3:                                         # cartel de la parada del bus
            world.blit(A.build_cartel_parada(), (46, A.FEET - 66))
        if t >= 1.3:                                         # nubes
            for ancho, y, v, x0 in ((66, 12, 5.0, 40), (46, 34, 8.0, 210), (38, 20, 11.0, 330)):
                x = (x0 + v * self.mt) % (A.W + 2 * ancho) - ancho
                world.blit(A.build_nube(ancho), (int(x), y))
        # el bus escolar cruza la calle por detrás de los chicos cada ~16 s (la primera vez, a los 4,8 s)
        tb = self.mt - (A.T_MENU + 1.5)
        if tb >= 0:
            x = A.W + 6 - (tb % 16.0) * 62
            if x > -190:
                world.blit(A.build_bus(), (int(x), A.FEET + 14 - 46))

    def _cartel(self, texto, w, h, esc, hover):
        key = (texto, w, h, esc, hover)
        if key not in self._img:
            s = A.build_cartel(texto, w, h, esc, hover)
            self._img[key] = pygame.transform.scale(s, (w * A.ESCALA, h * A.ESCALA))
        return self._img[key]

    def draw(self, surface):
        vt = self.vt
        A.draw_world(self.world, vt, self.kids, extras=self._extras,
                     beat=self._beat() if vt >= A.T_CARTMAN else None)
        A.render_view(self.canvas, self.world, vt, self.kids)
        pygame.transform.scale(self.canvas, self.escalado.get_size(), self.escalado)
        surface.blit(self.escalado, (0, 0))

        # Título y botones (se deslizan hacia adentro cuando termina de caer la cabeza de Cartman)
        tm = vt - self.t_menu
        if tm > 0:
            u = A.ease_out(tm / 0.5)
            titulo = self._cartel("BIELSA GARDEN", 172, 34, 2, False)
            surface.blit(titulo, titulo.get_rect(center=(385, 104 - int(220 * (1 - u)))))
            for i, txt in enumerate(BOTONES):
                ui = A.ease_out((tm - i * T_BOTON) / 0.5)
                if ui <= 0:
                    continue
                hover = (i == self.sel) and self._menu_visible()
                img = self._cartel(txt, BTN_W, BTN_H, 2, hover)
                r = img.get_rect(center=(BTN_X + int(520 * (1 - ui)) - (14 if hover else 0), BTN_Y[i]))
                surface.blit(img, r)
                if hover:                                          # flechita al lado del tablón elegido
                    draw_pixel_text(surface, ">", (255, 220, 60), 4, center=(r.x - 22, r.centery), outline=(60, 40, 10))
            if tm > 1.2:
                draw_pixel_text(surface, "FLECHAS: ELEGIR    ENTER: ACEPTAR", (255, 255, 255), 2,
                                center=(SCREEN_W // 2, 24), outline=(30, 40, 70))
        elif self.intro and vt < A.T_MENU + 2:
            pass
        if self.intro and vt < A.T_CARTMAN - 0.2:
            draw_pixel_text(surface, "CLIC PARA SALTEAR", (200, 200, 200), 2, center=(SCREEN_W - 120, SCREEN_H - 20))

        if self.salida is not None:                                # fundido a negro al jugar
            veil = pygame.Surface((SCREEN_W, SCREEN_H))
            veil.set_alpha(int(255 * min(1.0, self.salida[1] / SALIDA)))
            surface.blit(veil, (0, 0))
