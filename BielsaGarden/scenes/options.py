import pygame
import display
import ajustes
from settings import SCREEN_W, SCREEN_H, COLORS
from scenes.base import Scene
from ui import intro_art as A, audio
from ui.button import CartelButton, tablon
from ui.pixel_font import draw_pixel_text
from ui.widgets import Tabs, Selector, Checkbox, Slider
from data.catalogo import PERSONAJES
from entities.plants import draw_plant_icon

TABS = ["Pantalla", "Sonido", "Juego"]
OSCURO = (30, 18, 6)


class OptionsScene(Scene):
    def __init__(self, game, volver_a=None):
        super().__init__(game)
        self.volver_a = volver_a
        self.pending = {
            "resolucion": list(display.config["resolucion"]),
            "pantalla_completa": display.config["pantalla_completa"],
        }
        self.audio_guardado = audio.copia()
        self.juego_pending = ajustes.copia()
        self.juego_pj = 0
        self.panel_img = tablon("", 233, 110, 3)
        self.panel = self.panel_img.get_rect(topleft=(150, 140))
        self.tabs = Tabs(TABS, (self.panel.x + 30, self.panel.y - 36), self.change_tab)

        self.builders = {
            "Pantalla": self._build_pantalla,
            "Sonido": self._build_sonido,
            "Juego": self._build_juego,
        }
        self.current_tab = TABS[0]
        self.widgets = self.builders[self.current_tab]()

        cy = self.panel.bottom + 62
        self.btn_apply = CartelButton("APLICAR", (SCREEN_W // 2 - 140, cy), self.apply, size=(70, 15))
        self.btn_back = CartelButton("VOLVER", (SCREEN_W // 2 + 140, cy), self.back, size=(70, 15))
        self.message = None
        self.t = 0.0
        self._refresh()

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
        self.silencio_x = widgets[0].box.centerx
        widgets.append(Checkbox("Silenciar en segundo plano", audio.config["silenciar_fondo"],
                                (x, y + 5 * 46 + 6), self._on_fondo, escala=2))
        return widgets

    def _on_volumen(self, clave, valor, silenciado):
        audio.config["volumen"][clave] = valor
        audio.config["silencio"][clave] = silenciado
        audio.aplicar()
        self._refresh()

    def _on_fondo(self, value):
        audio.config["silenciar_fondo"] = value
        audio.aplicar()
        self._refresh()

    def _build_juego(self):
        x, y = self.panel.x + 40, self.panel.y + 22
        claves = list(PERSONAJES)
        clave = claves[self.juego_pj]
        pj = Selector("Personaje", [(i, PERSONAJES[k]["nombre"]) for i, k in enumerate(claves)], self.juego_pj,
                      (x, y), self._on_pj, x_valor=200, ancho_valor=60)
        widgets = [pj]
        for i, (stat, nombre) in enumerate(ajustes.STATS):
            pos = (x, y + 56 + i * 44)
            if ajustes.tiene(clave, stat):
                opciones = [(p, f"{p}%  ({self._fmt(stat, ajustes.valor(clave, stat, p))})")
                            for p in ajustes.PORCENTAJES]
                sel = Selector(nombre, opciones, 0, pos, lambda v, s=stat: self._on_stat(s, v),
                               x_valor=200, ancho_valor=60)
                sel.set_value(ajustes.porcentaje(clave, stat, self.juego_pending))
            else:
                sel = Selector(nombre, [(100, "NO TIENE")], 0, pos, lambda v: None, x_valor=200, ancho_valor=60)
                sel.enabled = False
            widgets.append(sel)
        cy = self.panel.bottom - 40
        widgets.append(CartelButton("RESTABLECER", (self.panel.x + 170, cy), self._reset_todos, size=(80, 15)))
        parejo = self._porcentaje_parejo()
        opciones = [(p, f"{p}%") for p in ajustes.PORCENTAJES]
        if parejo is None:
            opciones.insert(0, (None, "VARIOS"))
        todos = Selector("Todos al", opciones, 0, (self.panel.x + 315, cy - 21), self._on_todos,
                         x_valor=160, ancho_valor=40)
        todos.set_value(parejo)
        widgets.append(todos)
        return widgets

    def _porcentaje_parejo(self):
        valores = {ajustes.porcentaje(k, s, self.juego_pending)
                   for k in PERSONAJES for s, _ in ajustes.STATS if ajustes.tiene(k, s)}
        return valores.pop() if len(valores) == 1 else None

    def _on_todos(self, pct):
        if pct is None:
            return
        self.juego_pending = {k: {s: pct for s, _ in ajustes.STATS if ajustes.tiene(k, s)} for k in PERSONAJES}
        self.change_tab("Juego")

    @staticmethod
    def _fmt(stat, v):
        return f"{v:g} S" if stat == "recarga" else str(v)

    def _clave_pj(self):
        return list(PERSONAJES)[self.juego_pj]

    def _on_pj(self, i):
        self.juego_pj = i
        self.change_tab("Juego")

    def _on_stat(self, stat, pct):
        self.juego_pending.setdefault(self._clave_pj(), {})[stat] = pct
        self._refresh()

    def _reset_todos(self):
        self.juego_pending = {}
        self.change_tab("Juego")

    def _cambios_pantalla(self):
        return (self.pending["resolucion"] != list(display.config["resolucion"]) or
                self.pending["pantalla_completa"] != display.config["pantalla_completa"])

    def _cambios_sonido(self):
        return audio.config != self.audio_guardado

    def _cambios_juego(self):
        return ajustes._limpio(self.juego_pending) != ajustes.config

    def has_changes(self):
        return self._cambios_pantalla() or self._cambios_sonido() or self._cambios_juego()

    def _refresh(self):
        self.btn_apply.enabled = self.has_changes()
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
        if self._cambios_juego():
            ajustes.establecer(self.juego_pending)
            self.juego_pending = ajustes.copia()
        self.message = ["Cambios aplicados", 2.0]
        self._refresh()

    def back(self):
        if self._cambios_sonido():
            audio.restaurar(self.audio_guardado)
        if self.volver_a is not None:
            self.game.change_scene(self.volver_a)
        else:
            from scenes.menu import MenuScene
            self.game.change_scene(MenuScene(self.game))

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
        if self.current_tab == "Juego":
            draw_plant_icon(surface, self._clave_pj(), (self.panel.right - 92, self.panel.y + 150), 1.0)

        aviso_y = self.panel.bottom + 18
        if self.has_changes():
            draw_pixel_text(surface, "Hay cambios sin aplicar", (255, 230, 140), 2, outline=OSCURO,
                            center=(SCREEN_W // 2, aviso_y))
        elif self.message:
            draw_pixel_text(surface, self.message[0], (140, 240, 110), 2, outline=OSCURO,
                            center=(SCREEN_W // 2, aviso_y))

        self.btn_apply.draw(surface)
        self.btn_back.draw(surface)
