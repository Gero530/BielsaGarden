"""
Pantalla para escribir el nombre de una cuenta (cuentas.py). Tres usos:

  "primera": no hay ninguna cuenta (primera vez, o se borró la última). Bielsa pide el
             nombre; no se puede volver atrás. Al aceptar se crea la cuenta y se va al menú.
  "nueva":   desde Cuentas > NUEVA CUENTA. Al aceptar se crea, queda activa y se va al menú.
  "editar":  desde Cuentas > EDITAR. Al aceptar se renombra y se vuelve a Cuentas.
"""
import pygame
import cuentas
import logros
from settings import SCREEN_W, SCREEN_H
from scenes.base import Scene
from ui import intro_art as A
from ui.aviso_logro import icono
from ui.button import CartelButton, tablon
from ui.pixel_font import draw_pixel_text, wrap
from ui.widgets import CampoTexto

OSCURO = (30, 18, 6)
CREMA = (255, 240, 200)
BIELSA = {"id": "_bielsa_nombre", "icono": ("retrato", "tutorial")}
TEXTOS = {
    "primera": ("¡BIENVENIDO!", "Buenas tardes. Antes de empezar, una formalidad: ¿cómo se llama usted?"),
    "nueva": ("NUEVA CUENTA", "Muy bien. ¿Cómo se llama el nuevo jugador?"),
    "editar": ("EDITAR NOMBRE", "¿Cómo quiere que lo llamemos de ahora en más?"),
}


class NombreScene(Scene):
    def __init__(self, game, modo="primera", cid=None):
        super().__init__(game)
        self.modo = modo
        self.cid = cid
        actual = ""
        if modo == "editar":
            actual = dict(cuentas.lista()).get(cid, {}).get("nombre", "")
        self.titulo, self.pregunta = TEXTOS[modo]
        self.panel_img = tablon("", 210, 104, 3)
        self.panel = self.panel_img.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 20))
        self.campo = CampoTexto(actual, (SCREEN_W // 2, self.panel.y + 190), cuentas.MAX_NOMBRE, self.aceptar)
        cy = self.panel.bottom + 34
        if modo == "primera":
            self.botones = [CartelButton("ACEPTAR", (SCREEN_W // 2, cy), self.aceptar, size=(70, 15))]
        else:
            self.botones = [CartelButton("ACEPTAR", (SCREEN_W // 2 - 130, cy), self.aceptar, size=(70, 15)),
                            CartelButton("VOLVER", (SCREEN_W // 2 + 130, cy), self.volver, size=(70, 15))]
        self.error = None
        self.t = 0.0

    def aceptar(self):
        nombre = self.campo.texto.strip()
        self.error = cuentas.validar_nombre(nombre, excepto=self.cid)
        if self.error:
            return
        if self.modo == "editar":
            cuentas.renombrar(self.cid, nombre)
            from scenes.cuentas import CuentasScene
            self.game.change_scene(CuentasScene(self.game))
            return
        cuentas.guardar_desde(self.game)          # lo de la cuenta anterior (si había) queda guardado
        logros.guardar()
        cuentas.crear(nombre)
        logros.recargar()
        cuentas.cargar_en(self.game)
        from scenes.menu import MenuScene
        self.game.change_scene(MenuScene(self.game))

    def volver(self):
        if self.modo == "primera":
            return
        from scenes.cuentas import CuentasScene
        self.game.change_scene(CuentasScene(self.game))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.volver()
            return
        if self.campo.handle_event(event):
            if event.type == pygame.TEXTINPUT or event.key == pygame.K_BACKSPACE:
                self.error = None                 # al escribir se borra el error anterior
            return
        for b in self.botones:
            if b.handle_event(event):
                return

    def update(self, dt):
        self.t += dt
        self.campo.update(dt)

    def draw(self, surface):
        surface.blit(A.fondo_vivo(self.t), (0, 0))
        titulo = A.colgante_escalado(self.titulo, 96, 16, 1, self.t, cuerda=6)
        surface.blit(titulo, titulo.get_rect(midtop=(SCREEN_W // 2, 0)))
        surface.blit(self.panel_img, self.panel)

        # Bielsa pregunta (su cara y la frase al lado)
        x = self.panel.x + 30
        surface.blit(icono(BIELSA, 96), (x, self.panel.y + 28))
        lineas = wrap(self.pregunta, 2, self.panel.w - 190)
        y = self.panel.y + 76 - len(lineas) * 10
        for linea in lineas:
            draw_pixel_text(surface, linea, CREMA, 2, outline=OSCURO, topleft=(x + 120, y))
            y += 20

        self.campo.draw(surface)
        if self.error:
            draw_pixel_text(surface, self.error, (255, 140, 110), 2, outline=OSCURO,
                            center=(SCREEN_W // 2, self.campo.rect.bottom + 22))
        else:
            draw_pixel_text(surface, f"Hasta {cuentas.MAX_NOMBRE} letras", (220, 200, 160), 2, outline=OSCURO,
                            center=(SCREEN_W // 2, self.campo.rect.bottom + 22))
        for b in self.botones:
            b.draw(surface)
