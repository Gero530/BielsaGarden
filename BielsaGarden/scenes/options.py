"""
Pantalla de opciones con pestañas, con la estética del menú (fondo con nubes y bus,
tablones, fuente pixel, flechas y casilla dibujadas en pixel art).

Pestañas:
  - Pantalla: resolución y pantalla completa.
  - Sonido: volumen general, música, efectos, personajes y enemigos (slider + casilla de
    silencio cada uno) y "Silenciar en segundo plano" (ui/audio.py).

Para agregar una pestaña nueva:
  1. Sumá el nombre a TABS.
  2. Creá un método _build_<nombre>() que devuelva la lista de controles.
  3. Registralo en self.builders dentro de __init__.

Los cambios quedan "pendientes" hasta tocar Aplicar. Volver (o Esc) los descarta. Los de
sonido se escuchan al momento (para probar el volumen), pero Volver también los deshace.

Se abre desde el menú principal o desde la pausa de una partida: `volver_a` es la escena a
la que se vuelve (si no se pasa, el menú principal).
"""
import pygame
import display
from settings import SCREEN_W, SCREEN_H, COLORS
from scenes.base import Scene
from ui import intro_art as A, audio
from ui.button import CartelButton, tablon
from ui.pixel_font import draw_pixel_text
from ui.widgets import Tabs, Selector, Checkbox, Slider

TABS = ["Pantalla", "Sonido"]
OSCURO = (30, 18, 6)


class OptionsScene(Scene):
    def __init__(self, game, volver_a=None):
        super().__init__(game)
        self.volver_a = volver_a
        self.pending = {
            "resolucion": list(display.config["resolucion"]),
            "pantalla_completa": display.config["pantalla_completa"],
        }
        self.audio_guardado = audio.copia()      # lo último aplicado (Volver vuelve a esto)
        self.panel_img = tablon("", 233, 110, 3)
        self.panel = self.panel_img.get_rect(topleft=(150, 140))
        self.tabs = Tabs(TABS, (self.panel.x + 30, self.panel.y - 36), self.change_tab)

        self.builders = {
            "Pantalla": self._build_pantalla,
            "Sonido": self._build_sonido,
        }
        self.current_tab = TABS[0]
        self.widgets = self.builders[self.current_tab]()

        cy = self.panel.bottom + 62
        self.btn_apply = CartelButton("APLICAR", (SCREEN_W // 2 - 140, cy), self.apply, size=(70, 15))
        self.btn_back = CartelButton("VOLVER", (SCREEN_W // 2 + 140, cy), self.back, size=(70, 15))
        self.message = None      # [texto, segundos]
        self.t = 0.0
        self._refresh()

    # ------------------------------------------------------------------
    # Pestañas
    # ------------------------------------------------------------------
    def change_tab(self, name):
        self.current_tab = name
        self.widgets = self.builders[name]()
        self._refresh()

    def _build_pantalla(self):
        x = self.panel.x + 50
        res_options = [(list(r), f"{r[0]} x {r[1]}" + ("  (nativa)" if i == 0 else ""))
                       for i, r in enumerate(display.available_resolutions())]
        self.sel_res = Selector("Resolución", res_options, 0, (x, self.panel.y + 55), self._on_res)
        self.sel_res.set_value(self.pending["resolucion"])
        self.sel_res.note = "En pantalla completa se usa la resolución del monitor"
        self.chk_full = Checkbox("Pantalla completa", self.pending["pantalla_completa"],
                                 (x, self.panel.y + 160), self._on_full)
        return [self.sel_res, self.chk_full]

    def _on_res(self, value):
        self.pending["resolucion"] = list(value)
        self._refresh()

    def _on_full(self, value):
        self.pending["pantalla_completa"] = value
        self._refresh()

    def _build_sonido(self):
        x = self.panel.x + 50
        y = self.panel.y + 46
        widgets = []
        for i, (clave, nombre) in enumerate(audio.CATEGORIAS):
            widgets.append(Slider(nombre, audio.config["volumen"][clave], audio.config["silencio"][clave],
                                  (x, y + i * 46), lambda v, s, c=clave: self._on_volumen(c, v, s)))
        self.silencio_x = widgets[0].box.centerx           # para el título de la columna de casillas
        widgets.append(Checkbox("Silenciar en segundo plano", audio.config["silenciar_fondo"],
                                (x, y + 5 * 46 + 6), self._on_fondo, escala=2))
        return widgets

    def _on_volumen(self, clave, valor, silenciado):
        audio.config["volumen"][clave] = valor
        audio.config["silencio"][clave] = silenciado
        audio.aplicar()                  # se escucha al momento
        self._refresh()

    def _on_fondo(self, value):
        audio.config["silenciar_fondo"] = value
        audio.aplicar()
        self._refresh()

    # ------------------------------------------------------------------
    # Aplicar / volver
    # ------------------------------------------------------------------
    def _cambios_pantalla(self):
        return (self.pending["resolucion"] != list(display.config["resolucion"]) or
                self.pending["pantalla_completa"] != display.config["pantalla_completa"])

    def _cambios_sonido(self):
        return audio.config != self.audio_guardado

    def has_changes(self):
        return self._cambios_pantalla() or self._cambios_sonido()

    def _refresh(self):
        self.btn_apply.enabled = self.has_changes()      # sin cambios: bloqueado (tablas cruzadas)
        if self.current_tab == "Pantalla":
            self.sel_res.enabled = not self.pending["pantalla_completa"]

    def apply(self):
        if self._cambios_pantalla():
            display.config["resolucion"] = list(self.pending["resolucion"])
            display.config["pantalla_completa"] = self.pending["pantalla_completa"]
            self.game.apply_display()
        if self._cambios_sonido():
            audio.guardar()
            self.audio_guardado = audio.copia()
        self.message = ["Cambios aplicados", 2.0]
        self._refresh()

    def back(self):
        if self._cambios_sonido():
            audio.restaurar(self.audio_guardado)     # descarta lo que se probó sin aplicar
        if self.volver_a is not None:
            self.game.change_scene(self.volver_a)
        else:
            from scenes.menu import MenuScene
            self.game.change_scene(MenuScene(self.game))

    # ------------------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.back()
            return
        if self.tabs.handle_event(event):
            return
        for w in self.widgets:
            if w.handle_event(event):
                return
        for b in (self.btn_apply, self.btn_back):
            if b.handle_event(event):
                return

    def update(self, dt):
        self.t += dt
        if self.message:
            self.message[1] -= dt
            if self.message[1] <= 0:
                self.message = None

    def draw(self, surface):
        surface.blit(A.fondo_vivo(self.t), (0, 0))
        titulo = A.colgante_escalado("OPCIONES", 80, 22, 2, self.t)
        surface.blit(titulo, titulo.get_rect(midtop=(SCREEN_W // 2, 0)))

        surface.blit(self.panel_img, self.panel)
        self.tabs.draw(surface)
        if self.current_tab == "Sonido":
            draw_pixel_text(surface, "SILENCIO", (255, 230, 140), 2, outline=OSCURO,
                            midbottom=(self.silencio_x, self.panel.y + 44))
        for w in self.widgets:
            w.draw(surface)

        aviso_y = self.panel.bottom + 18
        if self.has_changes():
            draw_pixel_text(surface, "Hay cambios sin aplicar", (255, 230, 140), 2, outline=OSCURO,
                            center=(SCREEN_W // 2, aviso_y))
        elif self.message:
            draw_pixel_text(surface, self.message[0], (140, 240, 110), 2, outline=OSCURO,
                            center=(SCREEN_W // 2, aviso_y))

        self.btn_apply.draw(surface)
        self.btn_back.draw(surface)
        draw_pixel_text(surface, "ESC: VOLVER", (255, 255, 255), 2, outline=(30, 40, 70),
                        center=(SCREEN_W // 2, SCREEN_H - 20))
