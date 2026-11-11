"""
Escena de juego: une la grilla, las entidades, el HUD, los recursos
y las condiciones de victoria/derrota.
"""
import random
import pygame
import display
import cuentas
import logros
from settings import SCREEN_W, SCREEN_H, COLORS, GRID_X, HOUSE_X, PLANT_DATA
from settings import BRAINS_INTERVALO, RUIDO_ZOMBIE_INTERVALO
from scenes.base import Scene
from world.grid import Grid
from world.wave_manager import WaveManager
from world.lawnmower import LawnMower
from entities.plants import create_plant, draw_plant_icon
from entities.zombies import create_zombie
from entities.sun import Sun
from ui.hud import HUD, draw_shovel, dither
from ui.pixel_font import draw_pixel_text
from world.wave_manager import TXT_HORDA, TXT_FINAL
from levels import LEVELS
from levels.dialogos import ANTES_DEL_NIVEL, AL_GANAR, AL_PERDER
from ui.dialogo import Dialogo
from ui.sprites import draw_sprite
from ui.button import CartelButton, ancho_tablon, tablon
from ui import intro_art as A
from ui.hud import HUD_H

CAIDA_CARTEL = 0.35           # segundos que tarda en caer el cartel de horda
DURACION_AVISO = 2.0          # segundos que se ve un aviso (horda, oleada final)
ROJO_PINTURA = (178, 28, 20)  # letras pintadas del cartel de horda
from entities.effects import FloatingText
from data.catalogo import FRASES_AL_PLANTAR, FRASES_SOLO_LA_PRIMERA_VEZ
from ui import sonidos, musica
from entities.effects import Rayo, DestelloPantalla


class GameplayScene(Scene):
    def __init__(self, game, level_index=0, plantas=None):
        super().__init__(game)
        self.level_index = level_index
        self.level = LEVELS[level_index]

        self.grid = Grid(self.level.get("fondo", "fondos/jardin.png"))
        self.zombies = []
        self.projectiles = []
        self.effects = []             # animaciones sueltas (ratas de Kenny, destellos)
        self.suns = []
        self.mowers = [LawnMower(r, self.grid) for r in range(self.grid.rows)]

        self.sun = self.level["sol_inicial"]
        # plantas: el equipo elegido; si no hay, las del nivel; si el nivel no dice, todas
        self.plantas = plantas or self.level.get("plantas") or list(PLANT_DATA)
        self.hud = HUD(self.plantas)
        self.waves = WaveManager(self.level)

        self.sky_timer = 4.0
        self.selected = None          # key de planta, "pala" o None
        self.paused = False
        self.velocidad = getattr(game, "velocidad", 1)    # x1 / x2 / x3, se recuerda entre niveles
        acciones = (("CONTINUAR", self.toggle_pausa), ("OPCIONES", self.ir_opciones),
                    ("VOLVER AL MAPA", self.ir_mapa), ("MENÚ PRINCIPAL", self.ir_menu))
        ancho = max(ancho_tablon(t, 96) for t, _ in acciones)
        self.pausa_btns = [CartelButton(t, (SCREEN_W // 2, 316 + i * 58), fn, size=(ancho, 15))
                           for i, (t, fn) in enumerate(acciones)]
        self.banner = None            # (texto, segundos_restantes)
        self.kills = 0
        self.timmy_en_final = False   # Timmy salió durante la oleada final (logro)
        self.vistos = logros.conjunto("zombies_vistos")   # zombies ya descubiertos (catálogo)
        self.frases_dichas = set()    # frases que salen una sola vez por nivel (ej. Cartman)
        self.time = 0.0
        self.end_delay = None         # pequeña pausa antes de mostrar victoria
        self.mastica_t = 0.0          # >0 mientras suena el ruido de masticar
        self.musica_iniciada = False  # ya arrancó la música de la partida
        self.brains_timer = random.uniform(*BRAINS_INTERVALO)       # cuenta regresiva hasta el próximo "brains"
        self.ruido_timer = random.uniform(*RUIDO_ZOMBIE_INTERVALO)   # ... y hasta el próximo ruido de zombie

        # Diálogo activo (congela la partida) y qué hacer cuando se cierra
        self.dialogo = self.crear_dialogo("intro")
        self.al_cerrar_dialogo = None

        # Tutorial guiado (levels/tutorial.py): pasos con diálogo + algo que hacer.
        # Mientras haya tutorial, las oleadas no arrancan hasta el paso que lo indique.
        self.tuto = list(self.level.get("tutorial", []))
        self.tuto_paso = None
        self.juntados = 0             # energía juntada con clic (para el paso "juntar")
        self.waves_on = not self.tuto
        if self.tuto:
            self.siguiente_paso()

    def crear_dialogo(self, tipo):
        """tipo: "intro", "victoria" o "derrota": Bielsa dice una frase al azar (levels/dialogos.py).
        El tutorial no tiene "intro": arranca con sus propios pasos."""
        if tipo == "intro":
            return None if self.level.get("tutorial") else Dialogo([random.choice(ANTES_DEL_NIVEL)], "antes")
        frases = AL_GANAR if tipo == "victoria" else AL_PERDER
        return Dialogo([random.choice(frases)], tipo)

    def siguiente_paso(self):
        self.tuto_paso = self.tuto.pop(0) if self.tuto else None
        if self.tuto_paso is None:
            return
        # Los pasos seguidos que no esperan nada van en un mismo diálogo (Bielsa entra una sola vez)
        textos = list(self.tuto_paso["texto"])
        while self.tuto and not self.tuto_paso.get("espera") and not self.tuto_paso.get("oleadas"):
            self.tuto_paso = self.tuto.pop(0)
            textos += self.tuto_paso["texto"]
        if self.tuto_paso.get("oleadas"):
            self.waves_on = True
        self.dialogo = Dialogo(textos, "tutorial")

    def paso_cumplido(self):
        espera = self.tuto_paso.get("espera")
        if not espera:
            return True
        tipo, valor = espera
        if tipo == "planta":
            return any(p.key == valor for p in self.grid.plants())
        if tipo == "juntar":
            return self.juntados >= valor
        if tipo == "muertes":
            return self.kills >= valor
        return True

    # ------------------------------------------------------------------
    # Acciones del jugador (también las usa el test automático)
    # ------------------------------------------------------------------
    def can_place(self, key, row, col):
        card = self.hud.get_card(key)
        return card is not None and card.ready(self.sun) and self.grid.is_free(row, col)

    def try_place(self, key, row, col):
        if not self.can_place(key, row, col):
            return False
        plant = create_plant(key, row, col, self.grid)
        self.grid.place(plant)
        frase = FRASES_AL_PLANTAR.get(key)
        if key in FRASES_SOLO_LA_PRIMERA_VEZ:
            frase = frase if key not in self.frases_dichas else None
            self.frases_dichas.add(key)
        if frase:
            self.effects.append(FloatingText(frase, (plant.rect.centerx, plant.rect.top + 10)))
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
                self.juntados += 1
                logros.sumar("energia", s.value)
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

    def actualizar_minando(self):
        """El ruido de cavar suena en bucle mientras algún Pip siga bajo tierra (hasta que sale, le sacan el pico o explota)."""
        sonidos.minando(any(z.alive and z.key == "excavador" and z.fase == "tierra" for z in self.zombies))

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
                self.toggle_pausa()
            elif event.key == pygame.K_f:
                self.cambiar_velocidad()
            elif self.paused:
                pass
            # Atajos 1..9 para cartas, S para pala
            elif pygame.K_1 <= event.key <= pygame.K_9:
                i = event.key - pygame.K_1
                if i < len(self.hud.cards):
                    self.toggle_select(self.hud.cards[i].key)
            elif event.key == pygame.K_s:
                self.toggle_select("pala")
            return

        if self.paused:
            for b in self.pausa_btns:
                if b.handle_event(event):
                    return
            return
        if event.type != pygame.MOUSEBUTTONDOWN:
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
        if self.hud.speed_rect.collidepoint(pos):
            self.cambiar_velocidad()
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

    def toggle_pausa(self):
        self.paused = not self.paused

    def cambiar_velocidad(self):
        self.velocidad = self.velocidad % 3 + 1          # x1 -> x2 -> x3 -> x1
        self.game.velocidad = self.velocidad

    def ir_mapa(self):
        from scenes.mapa import MapaScene
        self.game.change_scene(MapaScene(self.game))

    def ir_menu(self):
        from scenes.menu import MenuScene
        self.game.change_scene(MenuScene(self.game))         # el menú guarda el progreso de la cuenta

    def ir_opciones(self):
        from scenes.options import OptionsScene
        self.game.change_scene(OptionsScene(self.game, volver_a=self))

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
        # Los carteles se leen a velocidad normal aunque el juego vaya x2 o x3
        if self.banner:
            self.banner[1] -= dt
            if self.banner[1] <= 0:
                self.banner = None
        # x2 / x3: 2 o 3 pasos normales por cuadro (mismo dt que a x1), así disparos y choques se
        # calculan igual y el balance no cambia. Un diálogo del tutorial o la pausa cortan en seco.
        for _ in range(self.velocidad):
            self.paso(dt)
            if self.dialogo or self.paused or self.result is not None:
                break

    def paso(self, dt):
        """Un paso de la lógica del juego."""
        self.time += dt
        if self.tuto_paso is not None and self.paso_cumplido():
            self.siguiente_paso()
            return

        # Oleadas
        new_zombies, notices = self.waves.update(dt) if self.waves_on else ([], [])
        for kind, row in new_zombies:
            self.zombies.append(create_zombie(kind, row, self.grid))
        for text, sonido in notices:
            self.banner = [text, DURACION_AVISO]
            if isinstance(sonido, (tuple, list)):
                sonidos.encadenar(*sonido)            # ej: oleada y, al terminar, sirena
            elif sonido:
                sonidos.reproducir(sonido)

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

        # Zombies que aparecen por primera vez: se descubren en el catálogo (también los que
        # invocan el bailarín o tira el gigante)
        for z in self.zombies:
            if z.key not in self.vistos:
                self.vistos.add(z.key)
                logros.agregar("zombies_vistos", z.key)

        # Limpieza
        self.grid.cleanup()
        self.actualizar_canto()
        self.actualizar_mastica(dt)
        self.actualizar_minando()
        before = len(self.zombies)
        for z in self.zombies:
            if not z.alive and not z.hypno and z.muerto_por:
                logros.sumar("muertes_" + z.muerto_por)        # muertes por personaje (logros)
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
        if self.result is not None:          # ya terminó: no volver a contar la victoria (logros, cuenta)
            return
        self._result = victory
        if victory:
            self.game.progreso.add(self.level["id"])     # desbloquea el siguiente en el mapa
            cuentas.guardar_desde(self.game)            # el nivel ganado queda en la cuenta
            logros.agregar("niveles", self.level["id"])
            if self.timmy_en_final:
                logros.sumar("timmy_final")
            if any(p.key == "nuez" and p.alive for p in self.grid.plants()):
                logros.sumar("butters_sobrevive")
        sonidos.canto(False)
        sonidos.masticar(False)
        sonidos.minando(False)
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

    def draw_cartel_horda(self, surface):
        """Aviso de horda: cartel con letras rojas pintadas que cae colgado de sogas (desde el borde
        del HUD) y después se balancea por cuadros."""
        visto = DURACION_AVISO - self.banner[1]            # segundos desde que apareció (tiempo real)
        caida = max(0.0, 1 - visto / CAIDA_CARTEL)
        dy = int(-300 * caida * caida) // 3 * 3              # cae rápido y frena
        cartel = A.colgante_escalado(self.banner[0], 0, 22, 2, visto, cuerda=58, color_texto=ROJO_PINTURA)
        r = cartel.get_rect(midbottom=(SCREEN_W // 2, SCREEN_H // 2 + 33 + dy))
        old = surface.get_clip()
        surface.set_clip(pygame.Rect(0, HUD_H, SCREEN_W, SCREEN_H - HUD_H))   # las sogas salen del HUD
        surface.blit(cartel, r)
        surface.set_clip(old)

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
        # Escaleras que dejó el zombie con escalera (apoyadas del lado de la calle)
        for r, c in self.grid.ladders:
            cell = self.grid.cell_rect(r, c)
            if not draw_sprite(surface, "escalera", (cell.centerx + 18, cell.bottom - 48)):
                pygame.draw.line(surface, (170, 120, 66), (cell.centerx + 4, cell.bottom - 8), (cell.centerx + 24, cell.y + 10), 4)
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

        self.hud.draw(surface, self.sun, self.selected, self.waves.progress, self.level["nombre"], self.waves.flag_marks,
                      self.velocidad)

        for s in self.suns:
            s.draw(surface)

        # Planta / pala "fantasma" siguiendo al mouse (no sobre el HUD: taparía las cartas)
        if show_cursor and self.selected and not self.paused and mouse[1] >= HUD_H:
            if self.selected == "pala":
                draw_shovel(surface, mouse)
            else:
                ghost = pygame.Surface((140, 140), pygame.SRCALPHA)
                draw_plant_icon(ghost, self.selected, (70, 70), 0.9)
                ghost.set_alpha(150)
                surface.blit(ghost, (mouse[0] - 70, mouse[1] - 70))

        if self.banner and self.banner[0] in (TXT_HORDA, TXT_FINAL):
            self.draw_cartel_horda(surface)
        elif self.banner:
            # Cartel grande con la fuente pixel; tiembla un poco al aparecer
            sacude = 4 if self.banner[1] > DURACION_AVISO - 0.4 and int(self.banner[1] * 30) % 2 else 0
            draw_pixel_text(surface, self.banner[0], (255, 214, 64), 5, outline=(30, 10, 10),
                            center=(SCREEN_W // 2 + sacude, SCREEN_H // 2))

        if self.paused:
            surface.blit(dither((SCREEN_W, SCREEN_H), 2), (0, 0))
            # Cartel colgante (las sogas bajan desde arriba de la pantalla)
            cartel = A.colgante_escalado("PAUSA", 0, 24, 3, pygame.time.get_ticks() / 1000, cuerda=44)
            surface.blit(cartel, cartel.get_rect(midtop=(SCREEN_W // 2, 0)))
            draw_pixel_text(surface, "P / ESC PARA CONTINUAR", (255, 255, 255), 3, outline=(30, 20, 10), center=(SCREEN_W // 2, 236))
            for b in self.pausa_btns:
                b.draw(surface)

        # Tutorial: pista abajo y flechita titilando bajo la carta que hay que usar
        if self.tuto_paso is not None and not self.dialogo and self.tuto_paso.get("pista"):
            pista = tablon(self.tuto_paso["pista"], 0, 14, 3)        # sobre un tablón: se lee sobre el pasto
            surface.blit(pista, pista.get_rect(center=(SCREEN_W // 2, SCREEN_H - 62)))
            espera = self.tuto_paso.get("espera") or (None, None)
            card = self.hud.get_card(espera[1]) if espera[0] == "planta" else None
            if card and int(self.time * 3) % 2 == 0:
                draw_pixel_text(surface, "^", (255, 240, 120), 5, outline=(30, 20, 10),
                                midtop=(card.rect.centerx, card.rect.bottom + 22))

        if self.dialogo:
            self.dialogo.dibujar(surface)
