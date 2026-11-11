"""
Menú principal con la intro estilo South Park en pixel art.

Al arrancar:  la cabeza de Stan se acerca, caen las calles/cuerpos/cabezas de Cartman,
Kyle, Stan y Kenny en la parada del bus, todo sincronizado con la canción. Cuando
aterriza la cabeza de Cartman aparecen los botones (JUGAR / CATÁLOGO / OPCIONES / SALIR) y la
canción sigue sonando de fondo, con el bus pasando y los chicos cabeceando al ritmo.
Además, dos tablones chicos: LOGROS (abajo a la izquierda) y el nombre del jugador (arriba a la
derecha), que abre la pantalla de cuentas (cambiar, crear, editar o borrar).

Al volver al menú se guarda solo el progreso en la cuenta activa (cuentas.guardar_desde).

Se puede saltear la intro con un clic, Enter, Espacio o Esc. Cuando se vuelve al menú
(desde Opciones o desde una partida) no se repite la intro: queda el menú directo.
"""
import pygame
import display
import cuentas
from settings import SCREEN_W, SCREEN_H, COLORS
from scenes.base import Scene
from ui import intro_art as A, musica
from ui.pixel_font import draw_pixel_text
from ui import button
from ui.button import ancho_tablon
from settings import MUSICA_DURACION as DURACION

BTN_X = 805
BTN_Y = [192, 270, 348, 426]
BTN_W, BTN_H = 114, 24            # tamaño interno (se agranda xBTN_ESC en pantalla)
BTN_ESC = 3
CHICO_W, CHICO_H = BTN_W // 2, 14    # LOGROS y el del jugador: la mitad de ancho (14 de alto para que el texto respire)
T_BOTON = 0.16                    # retraso entre un botón y el siguiente al aparecer
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
        self._img = {}
        cuentas.guardar_desde(game)           # al volver al menú se guarda el progreso de la cuenta
        self.botones = [("JUGAR", self.jugar), ("CATÁLOGO", self.catalogo),
                        ("OPCIONES", self.opciones), ("SALIR", self.salir)]
        self.n_grandes = len(self.botones)    # los de la columna; después van los dos chicos
        self.i_logros = len(self.botones)
        self.botones.append(("LOGROS", self.logros))
        self.i_cuenta = len(self.botones)
        self.botones.append((cuentas.nombre_activa().upper() or "JUGADOR", self.abrir_cuentas))
        self._destellos = [button.Destello() for _ in self.botones]

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
        # La música sigue en el mapa; se apaga recién al entrar a un nivel
        from scenes.mapa import MapaScene
        self.game.change_scene(MapaScene(self.game))

    def abrir_cuentas(self):
        from scenes.cuentas import CuentasScene
        self.game.change_scene(CuentasScene(self.game))

    def catalogo(self):
        from scenes.catalogo import CatalogoScene
        self.game.change_scene(CatalogoScene(self.game))

    def opciones(self):
        from scenes.options import OptionsScene
        self.game.change_scene(OptionsScene(self.game))

    def logros(self):
        from scenes.logros import LogrosScene
        self.game.change_scene(LogrosScene(self.game))

    def salir(self):
        self.game.quit()

    def _activar(self, i):
        self.botones[i][1]()

    def _apretar(self, i):
        """El tablón se hunde, saltan astillas y a los 0,1 s se hace la acción."""
        if not button.ocupado():
            button.apretar(self._rect_boton(i), BTN_ESC, lambda: self._activar(i), ("menu", i))

    def _menu_visible(self):
        return self.vt >= self.t_menu + 0.1

    def _saltar(self):
        """Salta al final de la intro (los chicos ya armados y los botones a la vista)."""
        if self.vt < A.T_MENU + 0.5:
            self.shift = A.T_MENU + 0.5 - self.mt

    # ------------------------------------------------------------------
    # Eventos
    # ------------------------------------------------------------------
    def _chico(self, i):
        return i >= self.n_grandes

    def _rect_boton(self, i):
        if self._chico(i):
            w = ancho_tablon(self.botones[i][0], CHICO_W)
            r = pygame.Rect(0, 0, w * BTN_ESC, CHICO_H * BTN_ESC)
            if i == self.i_logros:
                r.bottomleft = (14, SCREEN_H - 12)
            else:
                r.topright = (SCREEN_W - 14, 14)
            return r
        r = pygame.Rect(0, 0, BTN_W * BTN_ESC, BTN_H * BTN_ESC)
        r.center = (BTN_X, self._y(i))
        return r

    def _y(self, i):
        return BTN_Y[i]

    def handle_event(self, event):
        if not self._menu_visible():
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE)):
                self._saltar()
            return
        if event.type == pygame.MOUSEMOTION:
            for i in range(len(self.botones)):
                if self._rect_boton(i).collidepoint(event.pos):
                    self.sel = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self.botones)):
                if self._rect_boton(i).collidepoint(event.pos):
                    self.sel = i
                    self._apretar(i)
                    return
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(self.botones)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(self.botones)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._apretar(self.sel)

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

    def _bus(self, world):
        """El bus escolar cruza la calle POR DELANTE de los chicos (y del cartel de la parada) cada
        ~16 s; la primera vez, a los 4,8 s. Se dibuja después de los chicos para taparlos."""
        tb = self.mt - (A.T_MENU + 1.5)
        if tb >= 0:
            x = A.W + 6 - (tb % 16.0) * 62
            if x > -190:
                world.blit(A.build_bus(), (int(x), A.FEET + 14 - 46))

    def _cartel(self, texto, w, h, esc, estado, destello=None):
        if destello is not None:
            s = A.con_destello(A.build_cartel(texto, w, h, esc, estado=estado), destello)
            return pygame.transform.scale(s, (w * BTN_ESC, h * BTN_ESC))
        key = (texto, w, h, esc, estado)
        if key not in self._img:
            s = A.build_cartel(texto, w, h, esc, estado=estado)
            self._img[key] = pygame.transform.scale(s, (w * BTN_ESC, h * BTN_ESC))
        return self._img[key]

    def draw(self, surface):
        vt = self.vt
        A.draw_world(self.world, vt, self.kids, extras=self._extras, delante=self._bus,
                     beat=self._beat() if vt >= A.T_CARTMAN else None)
        A.render_view(self.canvas, self.world, vt, self.kids)
        pygame.transform.scale(self.canvas, self.escalado.get_size(), self.escalado)
        surface.blit(self.escalado, (0, 0))

        # Título y botones (se deslizan hacia adentro cuando termina de caer la cabeza de Cartman)
        tm = vt - self.t_menu
        if tm > 0:
            u = A.ease_out(tm / 0.5)
            # Cartel colgante: las sogas llegan hasta arriba de la pantalla
            titulo = A.colgante_escalado("BIELSA GARDEN", 172, 34, 2, self.mt, cuerda=18)
            surface.blit(titulo, titulo.get_rect(midbottom=(385, 104 + 51 - int(220 * (1 - u)))))
            for i, (txt, _) in enumerate(self.botones):
                ui = A.ease_out((tm - i * T_BOTON) / 0.5)
                if ui <= 0:
                    continue
                hover = (i == self.sel) and self._menu_visible()
                estado = "apretado" if button.apretado(("menu", i)) else ("hover" if hover else "normal")
                if self._chico(i):
                    self._dibujar_chico(surface, i, txt, estado, hover, ui)
                    continue
                img = self._cartel(txt, BTN_W, BTN_H, 2, estado,
                                   self._destellos[i].fase(estado == "hover"))
                r = img.get_rect(center=(BTN_X + int(520 * (1 - ui)) - (10 if hover else 0), self._y(i)))
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

    def _dibujar_chico(self, surface, i, txt, estado, hover, ui):
        """LOGROS entra desde la izquierda; el del jugador, desde la derecha (con "JUGADOR" abajo)."""
        r0 = self._rect_boton(i)
        img = self._cartel(txt, r0.w // BTN_ESC, CHICO_H, 1, estado, self._destellos[i].fase(estado == "hover"))
        if i == self.i_logros:
            r = r0.move(-int(300 * (1 - ui)) + (6 if hover else 0), 0)
            surface.blit(img, r)
            if hover:
                draw_pixel_text(surface, "<", (255, 220, 60), 3, center=(r.right + 16, r.centery), outline=(60, 40, 10))
        else:
            r = r0.move(int(400 * (1 - ui)) - (6 if hover else 0), 0)
            surface.blit(img, r)
            draw_pixel_text(surface, "JUGADOR", (255, 255, 255), 1, outline=(30, 40, 70),
                            midtop=(r.centerx, r.bottom + 2))
            if hover:
                draw_pixel_text(surface, ">", (255, 220, 60), 3, center=(r.x - 16, r.centery), outline=(60, 40, 10))
