"""
Pantalla de cuentas (botón con el nombre del jugador, arriba a la derecha del menú).

  - Clic en una cuenta: pasa a jugar con ella (se guarda la actual) y vuelve al menú.
  - EDITAR: cambia el nombre (scenes/nombre.py).
  - BORRAR: pregunta antes; borra la cuenta con su progreso y sus logros. Si era la única,
    se vuelve a pedir un nombre; si era la activa, se pasa a la primera que quede.
  - NUEVA CUENTA: crea otra (hasta cuentas.MAX_CUENTAS).
"""
import pygame
import display
import cuentas
import logros
from settings import SCREEN_W, SCREEN_H
from scenes.base import Scene
from levels import LEVELS
from ui import intro_art as A, button
from ui.button import CartelButton, tablon
from ui.hud import dither
from ui.pixel_font import draw_pixel_text

OSCURO = (30, 18, 6)
CREMA = (255, 240, 200)
DORADO = (255, 214, 64)
LETRA = (44, 24, 8)
FILA_W, FILA_H = 174, 21        # tablón de cada cuenta en píxeles de dibujo (x3)
FILA_X, FILA_Y0, FILA_DY = 60, 92, 72


class CuentasScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.t = 0.0
        self.confirmar = None              # id de la cuenta que se está por borrar
        self.btn_si = CartelButton("SÍ, BORRAR", (SCREEN_W // 2 - 130, 398), self._si, size=(70, 15))
        self.btn_no = CartelButton("NO", (SCREEN_W // 2 + 130, 398), self._no, size=(70, 15))
        self.armar()

    def armar(self):
        self.filas = []                    # (id, datos, rect del tablón, botón editar, botón borrar)
        for i, (cid, datos) in enumerate(cuentas.lista()):
            r = pygame.Rect(FILA_X, FILA_Y0 + i * FILA_DY, FILA_W * 3, FILA_H * 3)
            editar = CartelButton("EDITAR", (r.right + 98, r.centery - 3), lambda c=cid: self.editar(c), size=(56, 14))
            borrar = CartelButton("BORRAR", (r.right + 278, r.centery - 3), lambda c=cid: self.pedir_borrar(c),
                                  size=(56, 14))
            self.filas.append((cid, datos, r, editar, borrar))
        y = SCREEN_H - 56
        self.btn_nueva = CartelButton("NUEVA CUENTA", (SCREEN_W // 2 - 150, y), self.nueva, size=(90, 15))
        self.btn_nueva.enabled = len(self.filas) < cuentas.MAX_CUENTAS
        self.btn_volver = CartelButton("VOLVER", (SCREEN_W // 2 + 170, y), self.volver, size=(70, 15))

    # ------------------------------------------------------------------
    def elegir(self, cid):
        """Pasa a jugar con otra cuenta."""
        if cid != cuentas.id_activa():
            cuentas.guardar_desde(self.game)       # primero se guarda la que estaba
            logros.guardar()
            cuentas.activar(cid)
            logros.recargar()
            cuentas.cargar_en(self.game)
        self.volver()

    def editar(self, cid):
        from scenes.nombre import NombreScene
        self.game.change_scene(NombreScene(self.game, "editar", cid))

    def nueva(self):
        from scenes.nombre import NombreScene
        self.game.change_scene(NombreScene(self.game, "nueva"))

    def pedir_borrar(self, cid):
        self.confirmar = cid

    def _si(self):
        cid, self.confirmar = self.confirmar, None
        era_activa = cid == cuentas.id_activa()
        if era_activa:
            logros.guardar()
        cuentas.borrar(cid)
        if not cuentas.hay_cuentas():              # era la única: se vuelve a pedir un nombre
            logros.recargar()
            cuentas.cargar_en(self.game)
            from scenes.nombre import NombreScene
            self.game.change_scene(NombreScene(self.game, "primera"))
            return
        if era_activa:                             # se juega con la primera que quedó
            logros.recargar()
            cuentas.cargar_en(self.game)
        self.armar()

    def _no(self):
        self.confirmar = None

    def volver(self):
        from scenes.menu import MenuScene
        self.game.change_scene(MenuScene(self.game))

    # ------------------------------------------------------------------
    def handle_event(self, event):
        if self.confirmar is not None:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._no()
            else:
                for b in (self.btn_si, self.btn_no):
                    if b.handle_event(event):
                        break
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.volver()
            return
        for b in [self.btn_nueva, self.btn_volver] + [b for f in self.filas for b in f[3:]]:
            if b.handle_event(event):
                return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not button.ocupado():
            for cid, _, r, _, _ in self.filas:
                if r.collidepoint(event.pos):
                    button.apretar(r, 3, lambda c=cid: self.elegir(c), ("cuenta", cid))
                    return

    def update(self, dt):
        self.t += dt

    # ------------------------------------------------------------------
    def _resumen(self, datos):
        ganados = sum(1 for lv in LEVELS if lv["id"] in datos.get("progreso", []))
        hechos = sum(1 for l in logros.LOGROS if l["id"] in datos.get("logros", {}).get("completados", {}))
        return f"{ganados}/{len(LEVELS)} NIVELES   {hechos}/{len(logros.LOGROS)} LOGROS"

    def draw(self, surface):
        surface.blit(A.fondo_vivo(self.t), (0, 0))
        titulo = A.colgante_escalado("CUENTAS", 96, 16, 1, self.t, cuerda=6)
        surface.blit(titulo, titulo.get_rect(midtop=(SCREEN_W // 2, 0)))

        mouse = display.get_mouse_pos() if self.confirmar is None else (-1, -1)
        activa = cuentas.id_activa()
        for cid, datos, r, editar, borrar in self.filas:
            es_activa = cid == activa
            if button.apretado(("cuenta", cid)):
                estado = "apretado"
            elif r.collidepoint(mouse):
                estado = "hover"
            else:
                estado = "normal"
            dx = -6 if estado == "hover" else 0
            dy = {"hover": -3, "apretado": 3}.get(estado, 0)
            if es_activa:                               # la cuenta con la que se está jugando: marco dorado
                surface.fill(DORADO, r.inflate(8, 2).move(dx, -2))
            surface.blit(tablon(" " * 8, FILA_W, FILA_H, 3, texto_esc=2, estado=estado), r.move(dx, 0))
            draw_pixel_text(surface, datos["nombre"].upper(), LETRA, 2, midleft=(r.x + 22 + dx, r.centery - 12 + dy))
            draw_pixel_text(surface, self._resumen(datos), (92, 56, 22), 2, midleft=(r.x + 22 + dx, r.centery + 12 + dy))
            if es_activa:
                draw_pixel_text(surface, "JUGANDO", (40, 110, 30), 2, midright=(r.right - 22 + dx, r.centery - 12 + dy))
            editar.draw(surface)
            borrar.draw(surface)

        self.btn_nueva.draw(surface)
        self.btn_volver.draw(surface)
        if not self.btn_nueva.enabled:             # no es un control: explica por qué NUEVA CUENTA está bloqueado
            draw_pixel_text(surface, f"MÁXIMO {cuentas.MAX_CUENTAS} CUENTAS: BORRÁ UNA PARA CREAR OTRA", (255, 255, 255), 2,
                            outline=(30, 40, 70), center=(SCREEN_W // 2, SCREEN_H - 14))

        if self.confirmar is not None:
            self._dibujar_confirmacion(surface)

    def _dibujar_confirmacion(self, surface):
        surface.blit(dither((SCREEN_W, SCREEN_H), 2), (0, 0))
        panel = tablon("", 196, 92, 3)
        pr = panel.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
        surface.blit(panel, pr)
        nombre = dict(cuentas.lista()).get(self.confirmar, {}).get("nombre", "").upper()
        lineas = [("¡ATENCIÓN!", (255, 140, 110), 3),
                  ("¿Seguro que querés borrar la cuenta", CREMA, 2),
                  (f"{nombre}?", (255, 214, 64), 3),
                  ("Se pierden su progreso y sus logros.", (255, 220, 160), 2),
                  ("No se puede deshacer.", (255, 220, 160), 2)]
        y = pr.y + 38
        for texto, color, esc in lineas:
            draw_pixel_text(surface, texto, color, esc, outline=OSCURO, center=(SCREEN_W // 2, y))
            y += 30 if esc == 3 else 24
        self.btn_si.draw(surface)
        self.btn_no.draw(surface)
