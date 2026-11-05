"""
Pantalla de opciones con pestañas.

Para agregar una pestaña nueva (por ejemplo "Sonido"):
  1. Sumá el nombre a TABS.
  2. Creá un método _build_sonido() que devuelva la lista de controles.
  3. Registralo en self.builders dentro de __init__.

Los cambios quedan "pendientes" hasta tocar Aplicar. Volver (o Esc) los descarta.
"""
import pygame
import display
from settings import SCREEN_W, SCREEN_H, COLORS
from scenes.base import Scene
from ui.button import Button
from ui.fonts import draw_text
from ui.widgets import Tabs, Selector, Checkbox, PANEL, PANEL_BORDE

TABS = ["Pantalla"]


class OptionsScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.pending = {
            "resolucion": list(display.config["resolucion"]),
            "pantalla_completa": display.config["pantalla_completa"],
        }
        self.panel = pygame.Rect(150, 150, SCREEN_W - 300, 300)
        self.tabs = Tabs(TABS, (self.panel.x + 16, self.panel.y - 40), self.change_tab)

        self.builders = {
            "Pantalla": self._build_pantalla,
        }
        self.current_tab = TABS[0]
        self.widgets = self.builders[self.current_tab]()

        cy = self.panel.bottom + 60
        self.btn_apply = Button("Aplicar", (SCREEN_W // 2 - 130, cy), self.apply, size=(220, 52), font_size=32)
        self.btn_back = Button("Volver", (SCREEN_W // 2 + 130, cy), self.back, size=(220, 52), font_size=32)
        self.message = None      # [texto, segundos]
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
        self.sel_res = Selector("Resolución", res_options, 0, (x, self.panel.y + 50), self._on_res)
        self.sel_res.set_value(self.pending["resolucion"])
        self.sel_res.note = "En pantalla completa se usa la resolución del monitor"
        self.chk_full = Checkbox("Pantalla completa", self.pending["pantalla_completa"],
                                 (x, self.panel.y + 150), self._on_full)
        return [self.sel_res, self.chk_full]

    def _on_res(self, value):
        self.pending["resolucion"] = list(value)
        self._refresh()

    def _on_full(self, value):
        self.pending["pantalla_completa"] = value
        self._refresh()

    # ------------------------------------------------------------------
    # Aplicar / volver
    # ------------------------------------------------------------------
    def has_changes(self):
        return (self.pending["resolucion"] != list(display.config["resolucion"]) or
                self.pending["pantalla_completa"] != display.config["pantalla_completa"])

    def _refresh(self):
        self.btn_apply.enabled = self.has_changes()
        if self.current_tab == "Pantalla":
            self.sel_res.enabled = not self.pending["pantalla_completa"]

    def apply(self):
        display.config["resolucion"] = list(self.pending["resolucion"])
        display.config["pantalla_completa"] = self.pending["pantalla_completa"]
        self.game.apply_display()
        self.message = ["Cambios aplicados", 2.0]
        self._refresh()

    def back(self):
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
        if self.message:
            self.message[1] -= dt
            if self.message[1] <= 0:
                self.message = None

    def draw(self, surface):
        from scenes.menu import draw_menu_background
        draw_menu_background(surface)

        draw_text(surface, "OPCIONES", 64, COLORS["sol"], center=(SCREEN_W // 2, 70), bold=True)

        self.tabs.draw(surface)
        pygame.draw.rect(surface, PANEL, self.panel, border_radius=10)
        pygame.draw.rect(surface, PANEL_BORDE, self.panel, 3, border_radius=10)
        # Re-dibujar la pestaña activa encima del borde del panel para que queden unidos
        self.tabs.draw(surface)

        for w in self.widgets:
            w.draw(surface)

        if self.has_changes():
            draw_text(surface, "Hay cambios sin aplicar", 22, (255, 230, 140),
                      center=(SCREEN_W // 2, self.panel.bottom - 22))
        elif self.message:
            draw_text(surface, self.message[0], 22, COLORS["verde"],
                      center=(SCREEN_W // 2, self.panel.bottom - 22))

        self.btn_apply.draw(surface)
        self.btn_back.draw(surface)
        draw_text(surface, "Esc: volver", 20, COLORS["texto"], center=(SCREEN_W // 2, SCREEN_H - 20))
