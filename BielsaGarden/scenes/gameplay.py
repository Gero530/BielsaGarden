"""
Escena de juego: une la grilla, las entidades, el HUD, los recursos
y las condiciones de victoria/derrota.
"""
import random
import pygame
import display
from settings import SCREEN_W, SCREEN_H, COLORS, GRID_X, HOUSE_X, PLANT_DATA
from settings import BRAINS_INTERVALO, RUIDO_ZOMBIE_INTERVALO
from scenes.base import Scene
from world.grid import Grid
from world.wave_manager import WaveManager
from world.lawnmower import LawnMower
from entities.plants import create_plant, draw_plant_icon
from entities.zombies import create_zombie
from entities.sun import Sun
from ui.hud import HUD, draw_shovel
from ui.fonts import draw_text
from levels import LEVELS
from levels.dialogos import DIALOGOS
from ui.dialogo import Dialogo
from ui import sonidos, musica
from entities.effects import Rayo, DestelloPantalla


class GameplayScene(Scene):
    def __init__(self, game, level_index=0):
        super().__init__(game)
        self.level_index = level_index
        self.level = LEVELS[level_index]

        self.grid = Grid()
        self.zombies = []
        self.projectiles = []
        self.effects = []             # animaciones sueltas (ratas de Kenny, destellos)
        self.suns = []
        self.mowers = [LawnMower(r, self.grid) for r in range(self.grid.rows)]

        self.sun = self.level["sol_inicial"]
        self.hud = HUD(self.level["plantas"])
        self.waves = WaveManager(self.level)

        self.sky_timer = 4.0
        self.selected = None          # key de planta, "pala" o None
        self.paused = False
        self.banner = None            # (texto, segundos_restantes)
        self.kills = 0
        self.time = 0.0
        self.end_delay = None         # pequeña pausa antes de mostrar victoria
        self.mastica_t = 0.0          # >0 mientras suena el ruido de masticar
        self.musica_iniciada = False  # ya arrancó la música de la partida
        self.brains_timer = random.uniform(*BRAINS_INTERVALO)       # cuenta regresiva hasta el próximo "brains"
        self.ruido_timer = random.uniform(*RUIDO_ZOMBIE_INTERVALO)   # ... y hasta el próximo ruido de zombie

        # Diálogo activo (congela la partida) y qué hacer cuando se cierra
        self.dialogo = self.crear_dialogo("intro")
        self.al_cerrar_dialogo = None

    def crear_dialogo(self, tipo):
        """tipo: "intro", "victoria" o "derrota". None si el nivel no tiene ese diálogo."""
        mensajes = DIALOGOS.get(self.level_index + 1, {}).get(tipo)
        return Dialogo(mensajes) if mensajes else None

    # ------------------------------------------------------------------
    # Acciones del jugador (también las usa el test automático)
    # ------------------------------------------------------------------
    def can_place(self, key, row, col):
        card = self.hud.get_card(key)
        return card is not None and card.ready(self.sun) and self.grid.is_free(row, col)

    def try_place(self, key, row, col):
        if not self.can_place(key, row, col):
            return False
        self.grid.place(create_plant(key, row, col, self.grid))
        self.sun -= PLANT_DATA[key]["costo"]
        self.hud.get_card(key).start_cooldown()
        sonidos.reproducir("plantar")
        return True

    def dig(self, row, col):
        if not self.grid.is_free(row, col):
            self.grid.remove(row, col)
            sonidos.reproducir("plantar")
            return True
        return False

    def collect_sun_at(self, pos):
        for s in reversed(self.suns):
            if s.alive and s.clicked(pos):
                s.alive = False
                self.sun += s.value
                sonidos.reproducir("carne")
                return True
        return False

    def hay_aliens_activos(self):
        """True si hay un alien vivo que ya apretó el botón."""
        return any(z.alive and getattr(z, "zap_done", False) for z in self.zombies)

    def alien_zap(self, alien):
        """El alien apretó el botón: cae un rayo sobre cada Chef del mapa."""
        self.effects.append(DestelloPantalla())
        for p in self.grid.plants():
            if p.key == "girasol" and p.alive and not p.deshabilitado:
                delay = random.uniform(0.0, 0.3)
                p.sonda(delay)
                self.effects.append(Rayo(p.rect.center, delay))

    def actualizar_canto(self):
        cantando = any(p.key == "girasol" and p.deshabilitado for p in self.grid.plants())
        sonidos.canto(cantando)

    def actualizar_mastica(self, dt):
        """El ruido de masticar suena en bucle mientras algún zombie vivo esté comiendo."""
        if any(z.alive and z.eating for z in self.zombies):
            self.mastica_t = 0.25          # margen para que no corte entre una planta y la siguiente
        elif self.mastica_t > 0:
            self.mastica_t -= dt
        sonidos.masticar(self.mastica_t > 0)
    # ------------------------------------------------------------------
    def handle_event(self, event):
        if self.dialogo:
            self.dialogo.manejar_evento(event)
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_p, pygame.K_ESCAPE):
                self.paused = not self.paused
            # Atajos 1..3 para cartas, S para pala
            elif pygame.K_1 <= event.key <= pygame.K_9:
                i = event.key - pygame.K_1
                if i < len(self.hud.cards):
                    self.toggle_select(self.hud.cards[i].key)
            elif event.key == pygame.K_s:
                self.toggle_select("pala")
            return

        if self.paused or event.type != pygame.MOUSEBUTTONDOWN:
            return

        if event.button == 3:
            self.selected = None
            return
        if event.button != 1:
            return

        pos = event.pos
        # 1) Soles tienen prioridad
        if self.collect_sun_at(pos):
            return
        # 2) Cartas / pala
        card = self.hud.card_at(pos)
        if card:
            if card.ready(self.sun):
                self.toggle_select(card.key)
            return
        if self.hud.shovel_rect.collidepoint(pos):
            self.toggle_select("pala")
            return
        # 3) Grilla
        cell = self.grid.cell_at(pos)
        if cell and self.selected:
            if self.selected == "pala":
                self.dig(*cell)
                self.selected = None
            elif self.try_place(self.selected, *cell):
                self.selected = None

    def toggle_select(self, key):
        if key != "pala":
            card = self.hud.get_card(key)
            if not card.ready(self.sun):
                return
            if self.selected != key:
                sonidos.reproducir("seleccionar")     # clic en un personaje (no al soltarlo)
        self.selected = None if self.selected == key else key

    # ------------------------------------------------------------------
    def update(self, dt):
        # Mientras hay diálogo el nivel no avanza (ni zombies, ni soles, ni oleadas)
        if self.dialogo:
            self.dialogo.actualizar(dt)
            if self.dialogo.terminado:
                self.dialogo = None
                if self.al_cerrar_dialogo:
                    self.al_cerrar_dialogo()
            return
        if self.paused:
            sonidos.pausar(True)
            musica.partida_pausar(True)
            return
        sonidos.pausar(False)
        musica.partida_pausar(False)
        if not self.musica_iniciada:           # la música arranca cuando termina el diálogo y empieza la partida
            self.musica_iniciada = True
            musica.partida_iniciar()
        musica.partida_actualizar()            # cuando termina un tema, sigue el próximo
        self.time += dt

        # Oleadas
        new_zombies, notices = self.waves.update(dt)
        for kind, row in new_zombies:
            self.zombies.append(create_zombie(kind, row, self.grid))
        for text, sonido in notices:
            self.banner = [text, 3.0]
            if isinstance(sonido, (tuple, list)):
                sonidos.encadenar(*sonido)            # ej: oleada y, al terminar, sirena
            elif sonido:
                sonidos.reproducir(sonido)
        if self.banner:
            self.banner[1] -= dt
            if self.banner[1] <= 0:
                self.banner = None

        # Voces de zombie al azar (solo mientras haya zombies enemigos en el campo)
        if any(z.alive and not z.hypno for z in self.zombies):
            self.brains_timer -= dt
            self.ruido_timer -= dt
            if self.brains_timer <= 0:
                sonidos.reproducir("brains")
                self.brains_timer = random.uniform(*BRAINS_INTERVALO)
                self.ruido_timer = max(self.ruido_timer, 3.0)   # que no se pisen
            if self.ruido_timer <= 0:
                sonidos.reproducir("ruido_zombie")
                self.ruido_timer = random.uniform(*RUIDO_ZOMBIE_INTERVALO)

        # Sol del cielo
        self.sky_timer -= dt
        if self.sky_timer <= 0:
            self.sky_timer = self.level["intervalo_sol_cielo"]
            x = random.randint(GRID_X + 30, self.grid.rect.right - 30)
            target = random.randint(self.grid.rect.top + 40, self.grid.rect.bottom - 40)
            self.suns.append(Sun(x, 70, target))

        # Entidades
        self.hud.update(dt)
        for p in list(self.grid.plants()):
            p.update(dt, self)
        for z in self.zombies:
            z.update(dt, self)
        for pr in self.projectiles:
            pr.update(dt, self)
        for e in self.effects:
            e.update(dt, self)
        for m in self.mowers:
            m.update(dt, self)
        for s in self.suns:
            s.update(dt)

        # Limpieza
        self.grid.cleanup()
        self.actualizar_canto()
        self.actualizar_mastica(dt)
        before = len(self.zombies)
        self.zombies = [z for z in self.zombies if z.alive]
        self.kills += before - len(self.zombies)
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.effects = [e for e in self.effects if e.alive]
        self.suns = [s for s in self.suns if s.alive]

        # Si la carta seleccionada dejó de estar disponible, deseleccionar
        if self.selected and self.selected != "pala" and not self.hud.get_card(self.selected).ready(self.sun):
            self.selected = None

        self.check_end(dt)

    def check_end(self, dt):
        # Derrota: un zombie llegó a la casa (su fila ya no tenía cortacésped)
        if any(z.x < HOUSE_X for z in self.zombies if not z.hypno):
            self.finish(victory=False)
            return
        # Victoria: no quedan oleadas ni zombies enemigos (los hipnotizados no cuentan)
        if self.waves.finished and not any(not z.hypno for z in self.zombies):
            if self.end_delay is None:
                self.end_delay = 1.2
                self.banner = ["¡Nivel completado!", 2.0]
            self.end_delay -= dt
            if self.end_delay <= 0:
                self.finish(victory=True)

    @property
    def result(self):
        """None mientras se juega; True/False al terminar (útil para tests)."""
        return getattr(self, "_result", None)

    def finish(self, victory):
        self._result = victory
        sonidos.canto(False)
        sonidos.masticar(False)
        musica.partida_parar(500)
        from scenes.result import ResultScene
        self.banner = None
        self.selected = None
        snapshot = pygame.Surface((SCREEN_W, SCREEN_H))
        self.draw(snapshot, show_cursor=False)
        stats = {"kills": self.kills, "time": self.time}
        # Primero el diálogo de victoria/derrota (si hay) y al cerrarlo, la pantalla de resultado
        self.al_cerrar_dialogo = lambda: self.game.change_scene(
            ResultScene(self.game, victory, self.level_index, snapshot, stats))
        self.dialogo = self.crear_dialogo("victoria" if victory else "derrota")
        if not self.dialogo:
            self.al_cerrar_dialogo()

    # ------------------------------------------------------------------
    def draw(self, surface, show_cursor=True):
        surface.fill(COLORS["bg"])
        self.grid.draw(surface)
        for m in self.mowers:
            m.draw(surface)

        mouse = display.get_mouse_pos()
        if show_cursor and self.selected and not self.paused:
            if self.selected == "pala":
                self.grid.draw_hover(surface, mouse, lambda c: not self.grid.is_free(*c))
            else:
                self.grid.draw_hover(surface, mouse, lambda c: self.grid.is_free(*c))

        for p in self.grid.plants():
            p.draw(surface)
        # Zombies ordenados por fila para que se superpongan bien
        for z in sorted(self.zombies, key=lambda z: z.row):
            z.draw(surface)
        for pr in self.projectiles:
            pr.draw(surface)
        for e in self.effects:
            e.draw(surface)
        # Timmy cuando sale disparado (y su grito) va por encima de plantas y zombies
        for m in self.mowers:
            m.draw_overlay(surface)

        self.hud.draw(surface, self.sun, self.selected, self.waves.progress, self.level["nombre"])

        for s in self.suns:
            s.draw(surface)

        # Planta / pala "fantasma" siguiendo al mouse
        if show_cursor and self.selected and not self.paused:
            if self.selected == "pala":
                draw_shovel(surface, mouse)
            else:
                ghost = pygame.Surface((140, 140), pygame.SRCALPHA)
                draw_plant_icon(ghost, self.selected, (70, 70), 0.9)
                ghost.set_alpha(150)
                surface.blit(ghost, (mouse[0] - 70, mouse[1] - 70))

        if self.banner:
            draw_text(surface, self.banner[0], 64, (0, 0, 0), center=(SCREEN_W // 2 + 3, SCREEN_H // 2 + 3), bold=True)
            draw_text(surface, self.banner[0], 64, COLORS["rojo"], center=(SCREEN_W // 2, SCREEN_H // 2), bold=True)

        if self.paused:
            shade = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 140))
            surface.blit(shade, (0, 0))
            draw_text(surface, "PAUSA", 80, COLORS["texto"], center=(SCREEN_W // 2, SCREEN_H // 2 - 20), bold=True)
            draw_text(surface, "P / Esc para continuar", 30, COLORS["texto"], center=(SCREEN_W // 2, SCREEN_H // 2 + 40))

        if self.dialogo:
            self.dialogo.dibujar(surface)
