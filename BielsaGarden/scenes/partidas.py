"""
Panel de partidas guardadas (las 10 ranuras de guardado.py, en dos columnas de tablones).

  modo "cargar"  (menú > Continuar): clic en una partida para seguirla (va al mapa).
                 Las ranuras vacías están bloqueadas.
  modo "guardar" (pausa > Guardar):  clic en una ranura vacía guarda ahí; en una ocupada
                 pregunta antes "¿De verdad quieres sobreescribir esta partida?" (SÍ / NO).
                 La ranura de la partida actual se guarda sin preguntar.

`volver_a`: escena a la que se vuelve (la partida en pausa); si no hay, el menú principal.
`fondo`: imagen de fondo (la partida congelada); si no hay, el paisaje del menú.
"""
import pygame
import display
import guardado
from settings import SCREEN_W, SCREEN_H
from scenes.base import Scene
from levels import LEVELS
from ui import intro_art as A, button
from ui.button import CartelButton, tablon
from ui.hud import dither
from ui.pixel_font import draw_pixel_text

OSCURO = (30, 18, 6)
LETRA = (44, 24, 8)              # letras "talladas" sobre el tablón
RANURA_W, RANURA_H = 136, 20     # tamaño de cada tablón en píxeles de dibujo (x3 en pantalla)
COL_X = (SCREEN_W // 2 - 216, SCREEN_W // 2 + 216)
FILA_Y0, FILA_DY = 150, 70
VUELTA = 1.0                     # segundos que se ve "Partida guardada" antes de volver al juego


class PartidasScene(Scene):
    def __init__(self, game, modo="cargar", volver_a=None, fondo=None):
        super().__init__(game)
        self.modo = modo
        self.volver_a = volver_a
        self.fondo = None
        if fondo is not None:
            self.fondo = fondo.copy()
            self.fondo.fill((90, 90, 100), special_flags=pygame.BLEND_MULT)
        self.t = 0.0
        self.partidas = guardado.cargar_todas()
        self.rects = {}
        for n in range(1, guardado.MAX_RANURAS + 1):
            col, fila = (n - 1) // 5, (n - 1) % 5
            r = pygame.Rect(0, 0, RANURA_W * 3, RANURA_H * 3)
            r.center = (COL_X[col], FILA_Y0 + fila * FILA_DY)
            self.rects[n] = r
        self.btn_volver = CartelButton("VOLVER", (SCREEN_W // 2, 545), self.volver, size=(70, 15))
        self.confirmar = None              # ranura que se está por sobreescribir
        self.btn_si = CartelButton("SÍ", (SCREEN_W // 2 - 110, 356), self._si, size=(50, 15))
        self.btn_no = CartelButton("NO", (SCREEN_W // 2 + 110, 356), self._no, size=(50, 15))
        self.mensaje = None                # [texto, segundos]
        self.saliendo = None               # segundos que faltan para volver solo (después de guardar)

    # ------------------------------------------------------------------
    def _habilitada(self, n):
        return n in self.partidas if self.modo == "cargar" else True

    def volver(self):
        if self.volver_a is not None:
            self.game.change_scene(self.volver_a)
        else:
            from scenes.menu import MenuScene
            self.game.change_scene(MenuScene(self.game))

    def elegir(self, n):
        if self.modo == "cargar":
            if guardado.continuar(self.game, n):
                from scenes.mapa import MapaScene
                self.game.change_scene(MapaScene(self.game))
            return
        if n in self.partidas and n != self.game.ranura:
            self.confirmar = n                   # ocupada por otra partida: preguntar antes
        else:
            self._guardar(n)

    def _guardar(self, n):
        if guardado.guardar(self.game, n):
            self.partidas = guardado.cargar_todas()
            self.mensaje = [f"Guardada en {guardado.nombre(n)}", VUELTA + 0.5]
            self.saliendo = VUELTA
        else:
            self.mensaje = ["No se pudo guardar", 2.5]

    def _si(self):
        n, self.confirmar = self.confirmar, None
        self._guardar(n)

    def _no(self):
        self.confirmar = None

    # ------------------------------------------------------------------
    def handle_event(self, event):
        if self.saliendo is not None:
            return
        if self.confirmar is not None:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._no()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._si()
            else:
                for b in (self.btn_si, self.btn_no):
                    if b.handle_event(event):
                        return
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.volver()
            return
        if self.btn_volver.handle_event(event):
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not button.ocupado():
            for n, r in self.rects.items():
                if r.collidepoint(event.pos) and self._habilitada(n):
                    button.apretar(r, 3, lambda n=n: self.elegir(n), ("ranura", n))
                    return

    def update(self, dt):
        self.t += dt
        if self.mensaje:
            self.mensaje[1] -= dt
            if self.mensaje[1] <= 0:
                self.mensaje = None
        if self.saliendo is not None:
            self.saliendo -= dt
            if self.saliendo <= 0:
                self.saliendo = None
                self.volver()

    # ------------------------------------------------------------------
    def _dibujar_ranura(self, surface, n, mouse):
        r = self.rects[n]
        datos = self.partidas.get(n)
        if not self._habilitada(n):
            estado = "bloqueado"
        elif button.apretado(("ranura", n)):
            estado = "apretado"
        elif r.collidepoint(mouse) and self.confirmar is None and self.saliendo is None:
            estado = "hover"
        else:
            estado = "normal"
        dx = -6 if estado == "hover" else 0
        dy = {"hover": -3, "apretado": 3}.get(estado, 0)
        if datos is None:
            surface.blit(tablon("RANURA VACÍA", RANURA_W, RANURA_H, 3, estado=estado), r.move(dx, 0))
            return
        # Texto en blanco de escala 2: el tablón deja la franja del medio sin vetas (no tachan las letras)
        surface.blit(tablon(" " * 8, RANURA_W, RANURA_H, 3, texto_esc=2, estado=estado), r.move(dx, 0))
        titulo = guardado.nombre(n).upper() + ("  (ACTUAL)" if n == self.game.ranura and self.game.en_partida else "")
        ganados = sum(1 for lv in LEVELS if lv["id"] in datos["progreso"])
        fecha = datos.get("fecha", "")
        if len(fecha) == 16:                     # "07/11/2026 14:32" -> "07/11/26 14:32"
            fecha = fecha[:6] + fecha[8:]
        detalle = f"{ganados}/{len(LEVELS)} NIVELES   {fecha}"
        cx = r.centerx + dx
        draw_pixel_text(surface, titulo, LETRA, 2, center=(cx, r.centery - 10 + dy))
        draw_pixel_text(surface, detalle, (92, 56, 22), 2, center=(cx, r.centery + 10 + dy))

    def _dibujar_confirmacion(self, surface):
        surface.blit(dither((SCREEN_W, SCREEN_H), 2), (0, 0))
        panel = tablon("", 180, 70, 3)
        pr = panel.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
        surface.blit(panel, pr)
        draw_pixel_text(surface, "¿De verdad quieres sobreescribir", (255, 240, 200), 2, outline=OSCURO,
                        center=(SCREEN_W // 2, pr.y + 42))
        draw_pixel_text(surface, "esta partida?", (255, 240, 200), 2, outline=OSCURO,
                        center=(SCREEN_W // 2, pr.y + 66))
        datos = self.partidas.get(self.confirmar, {})
        ganados = sum(1 for lv in LEVELS if lv["id"] in datos.get("progreso", []))
        draw_pixel_text(surface, f"Se pierde {guardado.nombre(self.confirmar)} ({ganados}/{len(LEVELS)} niveles)",
                        (255, 200, 120), 2, outline=OSCURO, center=(SCREEN_W // 2, pr.y + 102))
        self.btn_si.draw(surface)
        self.btn_no.draw(surface)

    def draw(self, surface):
        if self.fondo is not None:
            surface.blit(self.fondo, (0, 0))
        else:
            surface.blit(A.fondo_vivo(self.t), (0, 0))
        texto = "CONTINUAR" if self.modo == "cargar" else "GUARDAR PARTIDA"
        titulo = A.colgante_escalado(texto, 96, 16, 1, self.t, cuerda=6)
        surface.blit(titulo, titulo.get_rect(midtop=(SCREEN_W // 2, 0)))

        mouse = (-1, -1) if self.confirmar is not None else display.get_mouse_pos()
        for n in self.rects:
            self._dibujar_ranura(surface, n, mouse)

        if self.mensaje:
            draw_pixel_text(surface, self.mensaje[0], (140, 240, 110), 2, outline=OSCURO,
                            center=(SCREEN_W // 2, 498))
        elif self.modo == "guardar" and guardado.ranura_libre(self.partidas) is None:
            draw_pixel_text(surface, "Sin ranuras libres: elegí una partida para pisarla",
                            (255, 230, 140), 2, outline=OSCURO, center=(SCREEN_W // 2, 498))
        self.btn_volver.draw(surface)
        draw_pixel_text(surface, "ESC: VOLVER", (255, 255, 255), 2, outline=(30, 40, 70),
                        center=(SCREEN_W // 2, SCREEN_H - 14))

        if self.confirmar is not None:
            self._dibujar_confirmacion(surface)
