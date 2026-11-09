"""
Zombies. Avanzan por su fila hacia la izquierda; si tienen una planta
delante se frenan y la comen. La armadura (cono/cubeta) absorbe daño antes
que el cuerpo.
Las bolas de nieve de Stan los ralentizan (caminan, comen y se animan más
lento) y se ven celestes mientras dura.
Si muerden a Toallin quedan hipnotizados: se dan vuelta, se ponen violetas y
caminan hacia la derecha mordiendo a los zombies que encuentren.
"""
import math
import random
import pygame
from settings import ZOMBIE_DATA, SCREEN_W, CELL_H, CELL_W, GRID_X, NIEVE_RALENTIZA, ALIEN_CASILLAS
from ui import sonidos
import logros
HIPNO_TINTE = (190, 130, 255)     # color que se multiplica sobre el sprite hipnotizado
HIPNO_ALCANCE = 36                 # a qué distancia (px) muerde a otro zombie
NIEVE_TINTE = (150, 200, 255)      # celeste mientras está ralentizado por la nieve de Stan
CONGELADO_TINTE = (110, 160, 255)  # azul mientras está congelado por la charla de Mr. Mackey
from ui.sprites import draw_sprite, has_sprite, anim_duration, frame_index, SPRITES
# Cuánto se corre la cabeza (adelante, abajo) en cada frame de atacar y de caminar, en píxeles de
# dibujo (igual que ATQ y CAM_CABEZA_DY en tools/zombies_pixel.py): el cono y el balde la siguen.
CABEZA_ATAQUE = ((0, 0), (2, 1), (3, 1), (4, 2), (3, 1), (1, 0))
CABEZA_CAMINAR = (0, 1, 1, 0, 0, 1, 1, 0)


class Zombie:
    key = "normal"
    metal = False              # True: lleva un objeto de metal que el Imán le puede sacar
    # Sprite del cuerpo. Cono y cubeta usan el mismo cuerpo y dibujan el accesorio encima.
    # Si algún día hacés un sprite propio para cada uno, cambiá esta clave en su clase.
    sprite_key = "zombie_normal"
    escudo_total = False       # True: el escudo absorbe todo (diario); False: solo lo de frente (puerta)
    puede_trepar = True        # usa las escaleras que dejó el zombie con escalera
    hipnotizable = True        # False: si muerde a Toallin se lo come sin quedar hipnotizado
    aplasta_pisables = False   # True: rompe a Mr. Hankey al pasarle por encima (tractor, gigante)

    def __init__(self, row, grid):
        data = ZOMBIE_DATA[self.key]
        self.data = data
        self.grid = grid
        self.row = row
        self.x = float(SCREEN_W + random.randint(10, 60))
        self.y_top = grid.row_center_y(row) - CELL_H // 2
        self.hp = data["vida"]
        self.max_hp = data["vida"]
        self.armor = data.get("armadura", 0)
        self.max_armor = self.armor
        self.shield = data.get("escudo", 0)
        self.max_shield = self.shield
        self.speed = data["velocidad"] * random.uniform(0.92, 1.08)
        self.dps = data["dps"]
        self.alive = True
        self.eating = False
        self.hit_flash = 0.0
        self.t = random.random() * 2
        self.hypno = False         # True: pelea de nuestro lado
        self.muerto_por = None     # clave de la planta que lo mató (para los logros)
        self.stun = 0.0            # frenado un instante porque un hipnotizado lo está mordiendo
        self.slow = 0.0            # segundos que le quedan ralentizado (bola de nieve de Stan)
        self.dir = -1              # -1 camina a la izquierda (hacia la casa), 1 a la derecha
        self.underground = False   # bajo tierra: los disparos no lo tocan
        self.airborne = False      # en el aire: nada lo toca (saltando, cayendo del cielo)
        self.lift = 0              # px que se dibuja más arriba (salto, escalera)
        self.congelado = 0.0       # segundos que le quedan congelado (charla de Mr. Mackey)

    @property
    def slow_factor(self):
        return NIEVE_RALENTIZA if self.slow > 0 else 1.0

    @property
    def cur_speed(self):
        """Velocidad real en este momento (con la ralentización aplicada)."""
        return self.speed * self.slow_factor

    @property
    def targetable(self):
        """Lo pueden atacar los disparos (bola de nieve, Ike)."""
        return self.alive and not self.hypno and not self.underground and not self.airborne

    def slow_down(self, duration):
        self.slow = max(self.slow, duration)

    def freeze(self, duration):
        self.congelado = max(self.congelado, duration)

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - 20, self.y_top + 8, 40, CELL_H - 16)

    def take_damage(self, amount, frontal=True, fuente=None):
        """frontal=False: el golpe viene de arriba o es una explosión (no lo frena la puerta).
        fuente: clave de la planta que pega (si lo mata, queda en muerto_por para los logros)."""
        self.hit_flash = 0.08
        if self.shield > 0 and (frontal or self.escudo_total):
            absorbed = min(self.shield, amount)
            self.shield -= absorbed
            amount -= absorbed
            if self.shield <= 0:
                self.on_shield_lost()
        if self.armor > 0:
            absorbed = min(self.armor, amount)
            self.armor -= absorbed
            amount -= absorbed
        self.hp -= amount
        if self.hp <= 0:
            if self.alive:
                self.muerto_por = fuente
            self.alive = False

    def kill(self, fuente=None):
        if self.alive:
            self.muerto_por = fuente
        self.hp = 0
        self.alive = False

    def on_shield_lost(self):
        pass

    def can_lose_metal(self):
        return self.alive and not self.hypno and self.metal and (self.armor > 0 or self.shield > 0)

    def metal_pos(self):
        """Centro del objeto de metal en pantalla (de donde sale volando hacia el Imán)."""
        return (int(self.x) - 4, self.y_top + 4)

    def remove_metal(self):
        """El Imán le arranca el objeto: pierde toda la armadura y sigue como un zombie normal."""
        self.metal = False
        self.armor = 0
        self.max_armor = 0       # la barra de vida pasa a medir solo el cuerpo

    def hypnotize(self):
        self.hypno = True
        self.eating = False
        self.stun = 0.0
        self.dir = 1

    def update_hypno(self, dt, world):
        """Hipnotizado: camina a la derecha y muerde al zombie enemigo que tenga cerca."""
        victim = None
        for z in world.zombies:
            if z is not self and z.alive and not z.hypno and z.row == self.row \
                    and not z.underground and not z.airborne and abs(z.x - self.x) < HIPNO_ALCANCE:
                victim = z
                break
        if victim is not None:
            self.eating = True          # el otro se frena porque le muerde de vuelta (ver rival_hipnotizado)
            victim.take_damage(self.dps * self.slow_factor * dt)
        else:
            self.eating = False
            self.x += self.cur_speed * dt
            if self.x > SCREEN_W + 60:  # salió de la pantalla
                self.alive = False

    def rival_hipnotizado(self, world):
        """El zombie hipnotizado (de nuestro lado) que tiene en la boca, o None."""
        for z in world.zombies:
            if z.hypno and z.alive and z.row == self.row and 0 <= (z.x - self.x) * self.dir < HIPNO_ALCANCE:
                return z
        return None

    def atacar_hipnotizado(self, rival, dt, world):
        """Se frenan y se muerden entre ellos hasta que uno muera (como en el original)."""
        self.eating = True
        rival.take_damage(self.dps * self.slow_factor * dt)

    def plant_ahead(self, world):
        """La planta que tiene en la "boca" (delante, según hacia dónde camina)."""
        col = world.grid.col_at_x(self.x + 22 * self.dir)
        return world.grid.get(self.row, col) if col is not None else None

    def special(self, dt, world):
        """Estados propios de cada zombie (saltar, bailar, caer...). True = ya se movió este frame."""
        return False

    def on_plant(self, target, world):
        """Llegó a una planta. True si hace algo propio en vez de comérsela."""
        return False

    def bite(self, target, dt):
        target.take_damage(self.dps * self.slow_factor * dt)

    def update(self, dt, world):
        if not self.alive:              # lo mataron antes en este mismo frame
            return
        if self.congelado > 0:          # congelado: no se mueve, no come, no se anima
            self.congelado -= dt
            self.eating = False
            if self.hit_flash > 0:
                self.hit_flash -= dt
            return
        self.t += dt * self.slow_factor       # ralentizado: también se anima más lento
        if self.slow > 0:
            self.slow -= dt
        if self.hit_flash > 0:
            self.hit_flash -= dt

        if self.hypno:
            self.update_hypno(dt, world)
            return
        if self.stun > 0:
            self.stun -= dt
            self.eating = False
            return
        if self.special(dt, world):
            return
        rival = self.rival_hipnotizado(world)
        if rival is not None:
            self.lift = 0
            self.atacar_hipnotizado(rival, dt, world)
            return

        target = self.plant_ahead(world)
        if target is not None and not target.alive:
            target = None
        # Mr. Hankey va en el piso: le pasan por encima (el tractor y el gigante lo rompen)
        if target is not None and getattr(target, "pisable", False):
            if self.aplasta_pisables:
                target.alive = False
            target = None
        # Escalera apoyada sobre la planta: la pasa por arriba
        trepa = target is not None and self.puede_trepar and (target.row, target.col) in world.grid.ladders
        self.lift = 26 if trepa else 0
        if trepa:
            target = None

        if target is not None:
            if getattr(target, "hipnotiza", False) and self.hipnotizable:
                # Se comió a Toallin: queda hipnotizado y Toallin desaparece
                target.alive = False
                self.hypnotize()
                sonidos.reproducir("hipnosis")
                logros.agregar("toallin_tipos", self.key)
                return
            if self.on_plant(target, world):
                return
            # El ruido de masticar lo maneja gameplay.py en bucle mientras algún zombie come
            self.eating = True
            self.bite(target, dt)
        else:
            self.eating = False
            self.x += self.dir * self.cur_speed * dt

    # --- Dibujo ---
    def sprite_state(self):
        """(clave_de_sprite, tiempo). Tiempo None = primer frame (quieto mordiendo)."""
        return self.sprite_key, (None if self.eating else self.t)

    def draw(self, surface):
        key, t = self.sprite_state()
        if not has_sprite(key):
            key = self.sprite_key if has_sprite(self.sprite_key) else "zombie_normal"
        # Si hay una animación de ataque para el estado actual, usarla al comer.
        # Los estados especiales (salto, baile, golpe, etc.) conservan su lógica.
        if self.eating and has_sprite(key + "_atacar"):
            key, t = key + "_atacar", self.t
        if has_sprite(key):
            self.draw_with_sprite(surface, key, t)
        else:
            self.draw_shapes(surface)

    def draw_with_sprite(self, surface, key, t):
        # Pies apoyados en el fondo de la fila (el sprite se ve x2: medio alto = frame_h)
        cfg = SPRITES[key]
        factor = max(1, round(2 * cfg.get("mult", 1.0)))
        cx, cy = int(self.x), self.y_top + CELL_H - cfg["frame_h"] * factor // 2 - self.lift
        # Mirando a la derecha (hipnotizado o excavador que ya salió): el sprite se espeja
        flip = self.hypno or self.dir > 0
        lado = 1 if flip else -1
        tint = HIPNO_TINTE if self.hypno else (CONGELADO_TINTE if self.congelado > 0
                                               else (NIEVE_TINTE if self.slow > 0 else None))
        draw_sprite(surface, key, (cx, cy), 1.0, t, flash=self.hit_flash > 0, flip=flip, tint=tint)
        # Cono / balde sobre la cabeza; siguen a la cabeza cuando sube y baja o se estira para morder
        i = frame_index(key, t)
        adel, baja = CABEZA_ATAQUE[i % 6] if key.endswith("_atacar") else (0, CABEZA_CAMINAR[i % 8])
        self.draw_armor(surface, (cx + (9 + adel * 2) * lado, self.y_top + 22 + baja * 2 - self.lift))
        if not self.airborne:
            self.draw_health_bar(surface)

    def draw_icon(self, surface, midbottom, box=None, t=None):
        """Dibujo para el catálogo (sin barra de vida). box=(ancho, alto): si al doble no entra,
        se dibuja a tamaño de dibujo (x1). Siempre por un entero, sin suavizado.
        t: tiempo de la animación (None = quieto, primer frame)."""
        key = self.sprite_key if has_sprite(self.sprite_key) else "zombie_normal"
        cfg = SPRITES[key]
        f = max(1, round(2 * cfg.get("mult", 1.0)))
        if box and (cfg["frame_w"] * f > box[0] or cfg["frame_h"] * f > box[1]):
            f = 1
        self.x, self.y_top = midbottom[0], midbottom[1] - CELL_H
        scale = f / (2 * cfg.get("mult", 1.0))
        draw_sprite(surface, key, (midbottom[0], midbottom[1] - cfg["frame_h"] * f // 2), scale, t)
        if f == 2:
            self.draw_armor(surface, (midbottom[0] - 9, self.y_top + 22))

    def draw_health_bar(self, surface):
        r = self.rect
        total = self.max_hp + self.max_armor + self.max_shield
        cur = max(0, self.hp) + max(0, self.armor) + max(0, self.shield)
        bar = pygame.Rect(r.x, self.y_top + CELL_H - 5, r.w, 4)   # a los pies, no tapa cono/cubeta
        pygame.draw.rect(surface, (60, 0, 0), bar)
        pygame.draw.rect(surface, (220, 60, 60), (bar.x, bar.y, int(bar.w * cur / total), bar.h))

    def draw_shapes(self, surface):
        r = self.rect
        sway = 3 if int(self.t * 3) % 2 == 0 else -3
        if self.eating:
            sway = 4 if int(self.t * 8) % 2 == 0 else 0

        skin = (150, 200, 230) if self.slow > 0 else (150, 180, 130)
        coat = (90, 80, 70)
        if self.hit_flash > 0:
            skin = (230, 240, 220)
            coat = (170, 160, 150)

        # Piernas
        pygame.draw.line(surface, (60, 60, 80), (r.centerx - 6, r.bottom - 22), (r.centerx - 10 - sway, r.bottom), 6)
        pygame.draw.line(surface, (60, 60, 80), (r.centerx + 6, r.bottom - 22), (r.centerx + 8 + sway, r.bottom), 6)
        # Torso
        pygame.draw.rect(surface, coat, (r.x + 6, r.y + 30, r.w - 12, r.h - 52), border_radius=4)
        pygame.draw.polygon(surface, (180, 40, 40), [(r.centerx, r.y + 34), (r.centerx - 4, r.y + 48), (r.centerx + 4, r.y + 48)])
        # Brazos hacia adelante (izquierda)
        arm_y = r.y + 38 + (sway if self.eating else 0)
        pygame.draw.line(surface, skin, (r.x + 8, r.y + 38), (r.x - 16, arm_y), 5)
        # Cabeza
        head = (r.centerx - 2, r.y + 18)
        pygame.draw.circle(surface, skin, head, 15)
        pygame.draw.circle(surface, (255, 255, 255), (head[0] - 6, head[1] - 2), 5)
        pygame.draw.circle(surface, (20, 20, 20), (head[0] - 7, head[1] - 2), 2)
        pygame.draw.line(surface, (60, 30, 30), (head[0] - 10, head[1] + 8), (head[0], head[1] + 8), 2)

        self.draw_armor(surface, head)

        # Barra de vida (cuerpo + armadura)
        total = self.max_hp + self.max_armor
        cur = max(0, self.hp) + max(0, self.armor)
        bar = pygame.Rect(r.x, r.y - 6, r.w, 4)
        pygame.draw.rect(surface, (60, 0, 0), bar)
        pygame.draw.rect(surface, (220, 60, 60), (bar.x, bar.y, int(bar.w * cur / total), bar.h))

    def draw_armor(self, surface, head):
        pass


class NormalZombie(Zombie):
    key = "normal"


class ConeZombie(Zombie):
    key = "cono"

    def draw_armor(self, surface, head):
        if self.armor > 0:
            x, y = head
            color = (240, 140, 40) if self.armor > self.max_armor / 2 else (200, 110, 30)
            pygame.draw.polygon(surface, color, [(x, y - 40), (x - 15, y - 8), (x + 15, y - 8)])
            pygame.draw.line(surface, (255, 230, 200), (x - 8, y - 22), (x + 8, y - 22), 3)


class BucketZombie(Zombie):
    key = "cubeta"
    metal = True

    def draw_armor(self, surface, head):
        if self.armor > 0:
            x, y = head
            draw_bucket(surface, (x, y - 18), 1.0, golpeado=self.armor <= self.max_armor / 2)


class AlienZombie(Zombie):
    key = "alien"
    sprite_key = "alien"
    FRAME_BOTON = 4        # frame de alien_boton en que aprieta el botón

    def __init__(self, row, grid):
        super().__init__(row, grid)
        self.stop_x = grid.rect.right - ALIEN_CASILLAS * CELL_W + CELL_W // 2
        self.state = "camina"      # camina -> boton -> quieto
        self.boton_t = 0.0
        self.zap_done = False      # ya apretó el botón

    def update(self, dt, world):
        self.t += dt * self.slow_factor
        if self.slow > 0:
            self.slow -= dt
        if self.hit_flash > 0:
            self.hit_flash -= dt
        if self.state == "camina":
            planta = self.plant_ahead(world)
            self.eating = planta is not None and planta.alive and not getattr(planta, "pisable", False)
            if self.eating:                 # una planta le corta el paso: se la come
                self.bite(planta, dt)
                return
            self.x -= self.cur_speed * dt
            if self.x <= self.stop_x:
                self.x = self.stop_x
                self.state = "boton"
                self.boton_t = 0.0
        elif self.state == "boton":
            self.boton_t += dt * self.slow_factor
            fps = SPRITES["alien_boton"]["fps"] if has_sprite("alien_boton") else 6
            if not self.zap_done and self.boton_t >= self.FRAME_BOTON / fps:
                self.zap_done = True
                world.alien_zap(self)
            if self.boton_t >= (anim_duration("alien_boton") if has_sprite("alien_boton") else 0.5):
                self.state = "quieto"

    def draw(self, surface):
        if not (has_sprite("alien") and has_sprite("alien_boton")):
            return self.draw_shapes(surface)
        cx, cy = int(self.x), self.y_top + CELL_H - 48
        tint = NIEVE_TINTE if self.slow > 0 else None
        fl = self.hit_flash > 0
        if self.state == "camina":
            key = "alien_atacar" if self.eating and has_sprite("alien_atacar") else "alien"
            draw_sprite(surface, key, (cx, cy), 1.0, self.t, flash=fl, tint=tint)
        elif self.state == "boton":
            draw_sprite(surface, "alien_boton", (cx, cy), 1.0, self.boton_t, flash=fl, tint=tint)
        else:
            draw_sprite(surface, "alien_boton", (cx, cy), 1.0, None, flash=fl, frame=7, tint=tint)
        self.draw_health_bar(surface)


def draw_bucket(surface, center, scale=1.0, golpeado=False):
    """El balde de la cubeta. También lo usa el balde que sale volando hacia el Imán."""
    x, y = center
    w, h = max(4, int(32 * scale)), max(3, int(24 * scale))
    color = (130, 135, 140) if golpeado else (175, 180, 190)
    r = pygame.Rect(0, 0, w, h)
    r.center = (int(x), int(y))
    pygame.draw.rect(surface, color, r, border_radius=3)
    pygame.draw.rect(surface, (90, 95, 100), r, max(1, int(2 * scale)), border_radius=3)
    pygame.draw.line(surface, (90, 95, 100), (r.x - int(2 * scale), r.bottom),
                     (r.right + int(2 * scale), r.bottom), max(1, int(3 * scale)))


def _rand_speed(v):
    return v * random.uniform(0.92, 1.08)


class DoorZombie(Zombie):
    """Lleva una puerta de frente: absorbe los disparos rectos. Ike (desde arriba) y las
    explosiones la saltean. El Imán se la arranca. Sin puerta es un zombie normal."""
    key = "puerta"
    sprite_key = "zombie_puerta"
    metal = True

    def sprite_state(self):
        key = self.sprite_key if self.shield > 0 else "zombie_puerta_sin"
        return key, (None if self.eating else self.t)

    def metal_pos(self):
        return (int(self.x) - 19, self.y_top + 62)

    def remove_metal(self):
        self.metal = False
        self.shield = 0
        self.max_shield = 0


class NewspaperZombie(Zombie):
    """Lee el diario (escudo que absorbe todo). Cuando se lo rompen se queda un momento
    quieto de la bronca y después camina y come mucho más rápido."""
    key = "diario"
    sprite_key = "zombie_diario"
    escudo_total = True

    def __init__(self, row, grid):
        super().__init__(row, grid)
        self.enojado = False

    def on_shield_lost(self):
        self.enojado = True
        self.stun = self.data["enojo"]
        self.speed = _rand_speed(self.data["velocidad_enojado"])
        self.dps = self.data["dps_enojado"]

    def sprite_state(self):
        key = "zombie_diario_enojado" if self.enojado else self.sprite_key
        return key, (None if self.eating else self.t)


class PoleZombie(Zombie):
    """Corre con la pértiga y salta por encima de la primera planta. Después camina normal."""
    key = "pertiga"
    sprite_key = "zombie_pertiga"

    def __init__(self, row, grid):
        super().__init__(row, grid)
        self.pole = True
        self.jump = None            # [tiempo, x_inicial, x_final] mientras salta

    @property
    def puede_trepar(self):
        return not self.pole         # con la pértiga salta la planta aunque tenga escalera

    def on_plant(self, target, world):
        if not self.pole:
            return False
        if getattr(target, "alto", False):     # PC Principal: no lo puede saltar, pierde la pértiga
            self.pole = False
            self.speed = _rand_speed(self.data["velocidad_despues"])
            return False
        land = world.grid.cell_rect(target.row, target.col).left - 14
        self.jump = [0.0, self.x, land]
        self.airborne = True
        self.eating = False
        return True

    def special(self, dt, world):
        if self.jump is None:
            return False
        self.jump[0] += dt
        u = min(1.0, self.jump[0] / self.data["salto"])
        self.x = self.jump[1] + (self.jump[2] - self.jump[1]) * u
        self.lift = int(math.sin(math.pi * u) * 70)
        if u >= 1.0:
            self.jump = None
            self.pole = False
            self.airborne = False
            self.lift = 0
            self.speed = _rand_speed(self.data["velocidad_despues"])
        return True

    def sprite_state(self):
        if self.jump is not None:
            return "zombie_pertiga_salto", self.jump[0]
        key = self.sprite_key if self.pole else "zombie_pertiga_sin"
        return key, (None if self.eating else self.t)


class LadderZombie(Zombie):
    """Al llegar a la primera planta le apoya la escalera encima y la pasa por arriba.
    La escalera queda puesta (world.grid.ladders) y la usan los demás zombies."""
    key = "escalera"
    sprite_key = "zombie_escalera"

    def __init__(self, row, grid):
        super().__init__(row, grid)
        self.ladder = True
        self.placing = None          # [tiempo, (fila, col)] mientras apoya la escalera

    def on_plant(self, target, world):
        if not self.ladder:
            return False
        self.placing = [0.0, (target.row, target.col)]
        self.eating = False
        return True

    def special(self, dt, world):
        if self.placing is None:
            return False
        self.placing[0] += dt
        if self.placing[0] >= self.data["apoyar"]:
            cell = self.placing[1]
            if world.grid.get(*cell) is not None:
                world.grid.ladders.add(cell)
            self.placing = None
            self.ladder = False
            self.speed = _rand_speed(self.data["velocidad_despues"])
        return True

    def sprite_state(self):
        if self.placing is not None:
            return "zombie_escalera_colocar", self.placing[0]
        key = self.sprite_key if self.ladder else "zombie_escalera_sin"
        return key, (None if self.eating else self.t)


class TractorZombie(Zombie):
    """Tanque lento: mucha vida y mucho daño a las plantas. No usa escaleras."""
    key = "tractor"
    sprite_key = "zombie_tractor"
    puede_trepar = False
    hipnotizable = False
    aplasta_pisables = True

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - 40, self.y_top + 8, 80, CELL_H - 16)


class BungeeZombie(Zombie):
    """Cae del cielo colgado de una cuerda en una casilla al azar (desde la 3ra columna).
    Antes se ve una marca en el piso. Al aterrizar camina y come como uno normal."""
    key = "bungee"
    sprite_key = "zombie_bungee"

    def __init__(self, row, grid):
        super().__init__(row, grid)
        # No cae en la casilla de PC Principal
        libres = [c for c in range(self.data["col_minima"], grid.cols) if not self.bloqueada(grid, row, c)]
        self.col = random.choice(libres or list(range(self.data["col_minima"], grid.cols)))
        self.x = float(grid.cell_rect(row, self.col).centerx + 8)
        self.fase = "aviso"          # aviso -> cae -> suelo
        self.ft = 0.0
        self.airborne = True

    def special(self, dt, world):
        if self.fase == "suelo":
            return False
        self.ft += dt
        if self.fase == "aviso" and self.ft >= self.data["aviso"]:
            if self.bloqueada(world.grid, self.row, self.col):
                self.alive = False   # pusieron a PC Principal en la marca: no se anima a caer y se va
                return True
            self.fase, self.ft = "cae", 0.0
        if self.fase == "cae":
            u = min(1.0, self.ft / self.data["caida"])
            self.lift = int((1 - u) * (self.y_top + CELL_H + 20))
            if u >= 1.0:
                self.fase = "suelo"
                self.airborne = False
                self.lift = 0
        return True

    def sprite_state(self):
        if self.fase == "cae":
            return "zombie_bungee_bajar", self.ft
        return super().sprite_state()

    @staticmethod
    def bloqueada(grid, row, col):
        return getattr(grid.get(row, col), "alto", False)

    def draw(self, surface):
        if self.fase != "suelo":
            # Marca en el piso donde va a caer (titila)
            mark = (int(self.x), self.y_top + CELL_H - 12)
            if not draw_sprite(surface, "bungee_marca", mark, 1.0, self.ft):
                pygame.draw.ellipse(surface, (210, 40, 40), (mark[0] - 24, mark[1] - 12, 48, 24), 4)
            if self.fase == "aviso":
                return
            top = self.y_top + CELL_H - 96 - self.lift
            # La cuerda: 1 píxel de dibujo (2 px, como el zombie), alineada a la grilla de x2
            rx = (int(self.x) - 1) // 2 * 2
            pygame.draw.rect(surface, (30, 30, 30), (rx, 0, 2, max(0, (top + 4) // 2 * 2)))
        super().draw(surface)


class DancerZombie(Zombie):
    """Cada tanto frena, baila e invoca zombies normales alrededor suyo: adelante y atrás
    en su fila y en las filas de arriba y abajo (solo repone los que le faltan, máx. 4)."""
    key = "bailarin"
    sprite_key = "zombie_bailarin"

    def __init__(self, row, grid):
        super().__init__(row, grid)
        self.timer = 2.0
        self.dancing = 0.0
        self.backups = [None] * 4

    def summon(self, world):
        spots = [(self.row, -CELL_W), (self.row, CELL_W), (self.row - 1, 0), (self.row + 1, 0)]
        for i, (r, dx) in enumerate(spots):
            b = self.backups[i]
            if b is not None and b.alive:
                continue
            x = self.x + dx
            if not (0 <= r < world.grid.rows and world.grid.rect.left + 20 < x < SCREEN_W):
                continue
            z = create_zombie("normal", r, world.grid)
            z.x = x
            z.stun = 0.6             # sale de la tierra y tarda un momento en arrancar
            world.zombies.append(z)
            self.backups[i] = z

    def special(self, dt, world):
        if self.dancing > 0:
            self.dancing -= dt
            return True
        if self.eating or self.x > world.grid.rect.right - 10:
            return False
        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.data["cada"]
            self.dancing = self.data["baile"]
            self.summon(world)
            return True
        return False

    def sprite_state(self):
        if self.dancing > 0:
            return "zombie_bailarin_baile", self.t
        return self.sprite_key, (None if self.eating else self.t)


class DiggerZombie(Zombie):
    """Avanza bajo tierra (solo lo tocan las explosiones y la podadora), sale en la primera
    columna del lado de la casa y come las plantas de atrás para adelante caminando hacia la
    derecha hasta salir de la pantalla. El pico es de metal: si el Imán se lo saca, sale a la
    superficie donde esté y sigue como un zombie normal (camina hacia la casa)."""
    key = "excavador"
    sprite_key = "zombie_excavador"
    puede_trepar = False
    metal = True               # el pico

    def can_lose_metal(self):
        return self.alive and not self.hypno and self.metal

    def metal_pos(self):
        return (int(self.x) + 8, self.y_top + 56 - self.lift)

    def remove_metal(self):
        self.metal = False
        if self.fase == "tierra":           # sin pico no puede seguir cavando: sale acá
            self.fase, self.ft = "sale", 0.0
        elif self.fase == "camina":
            self.dir = -1

    def __init__(self, row, grid):
        super().__init__(row, grid)
        self.fase = "tierra"         # tierra -> sale -> camina
        self.ft = 0.0
        self.underground = True

    def special(self, dt, world):
        if self.fase == "tierra":
            self.x -= self.cur_speed * dt
            if self.x <= GRID_X + CELL_W // 2:
                self.fase, self.ft = "sale", 0.0
            return True
        if self.fase == "sale":
            self.ft += dt
            self.lift = -int((1 - min(1.0, self.ft / self.data["salir"])) * 40)
            if self.ft >= self.data["salir"]:
                self.fase = "camina"
                self.underground = False
                self.lift = 0
                self.dir = 1 if self.metal else -1   # sin pico: zombie normal
                self.speed = _rand_speed(self.data["velocidad_despues"])
            return True
        if self.dir > 0 and self.x > SCREEN_W + 40:
            self.alive = False       # se comió la fila y se fue por la calle: cuenta como eliminado
            return True
        return False

    def sprite_state(self):
        if self.fase == "tierra":
            return "zombie_excavador_tierra", self.t
        key = self.sprite_key if self.metal else "zombie_excavador_sin"
        if self.fase == "sale":
            return key, None
        return key, (None if self.eating else self.t)


class GiantZombie(Zombie):
    """Muy tanque. Aplasta las plantas de un golpe. Con poca vida tira al mini zombie
    hacia el fondo de la fila (cerca de la casa)."""
    key = "gigante"
    sprite_key = "zombie_gigante"
    puede_trepar = False
    hipnotizable = False
    aplasta_pisables = True

    def __init__(self, row, grid):
        super().__init__(row, grid)
        self.golpe = None            # [tiempo, planta] mientras levanta el poste
        self.tiene_mini = True
        self.lanzando = None         # tiempo de la animación de revolear al enano

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - 28, self.y_top + 8, 56, CELL_H - 16)

    def on_plant(self, target, world):
        if self.golpe is None:
            self.golpe = [0.0, target]
        return True

    def atacar_hipnotizado(self, rival, dt, world):
        self.on_plant(rival, world)      # al hipnotizado también lo aplasta de un golpe

    FRAME_LANZA = 3              # frame de zombie_gigante_lanzar en que suelta al enano

    def special(self, dt, world):
        if self.lanzando is not None:
            self.lanzando += dt * self.slow_factor
            suelta = self.FRAME_LANZA / SPRITES["zombie_gigante_lanzar"]["fps"] if has_sprite("zombie_gigante_lanzar") else 0
            if self.tiene_mini and self.lanzando >= suelta:
                self.tiene_mini = False
                mini = create_zombie("mini", self.row, world.grid)
                mini.lanzar(self.x - 10, random.uniform(GRID_X + 30, GRID_X + CELL_W * 2))
                world.zombies.append(mini)
            if self.lanzando >= max(suelta, anim_duration("zombie_gigante_lanzar")):
                self.lanzando = None
            return True
        if self.tiene_mini and self.golpe is None and self.hp <= self.max_hp * self.data["lanza_mini"] \
                and GRID_X + CELL_W * 3 < self.x < SCREEN_W - 20:
            self.lanzando = 0.0
            return True
        if self.golpe is None:
            return False
        self.golpe[0] += dt * self.slow_factor
        if self.golpe[0] >= self.data["golpe"]:
            plant = self.golpe[1]        # una planta o un zombie hipnotizado
            if plant.alive:
                plant.hp = 0
                plant.alive = False
            self.golpe = None
        return True

    def sprite_state(self):
        suf = "" if self.tiene_mini else "_sin"          # después de lanzar al mini, sin él en la espalda
        if self.lanzando is not None:
            return "zombie_gigante_lanzar", self.lanzando
        if self.golpe is not None:
            return "zombie_gigante_golpe" + suf, self.golpe[0]
        return self.sprite_key + suf, self.t


class MiniZombie(Zombie):
    """El zombie chiquito que tira el gigante."""
    key = "mini"
    sprite_key = "zombie_mini"

    def __init__(self, row, grid):
        super().__init__(row, grid)
        self.vuelo = None

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - 14, self.y_top + 40, 28, CELL_H - 48)

    def lanzar(self, x0, x1):
        self.vuelo = [0.0, x0, x1]
        self.x = x0
        self.airborne = True

    def special(self, dt, world):
        if self.vuelo is None:
            return False
        self.vuelo[0] += dt
        u = min(1.0, self.vuelo[0] / self.data["vuelo"])
        self.x = self.vuelo[1] + (self.vuelo[2] - self.vuelo[1]) * u
        self.lift = int(math.sin(math.pi * u) * 150)
        if u >= 1.0:
            self.vuelo = None
            self.airborne = False
            self.lift = 0
        return True


ZOMBIE_CLASSES = {cls.key: cls for cls in (
    NormalZombie, ConeZombie, BucketZombie, DoorZombie, NewspaperZombie, PoleZombie, LadderZombie,
    TractorZombie, BungeeZombie, DancerZombie, DiggerZombie, GiantZombie, MiniZombie, AlienZombie)}


def create_zombie(key, row, grid):
    return ZOMBIE_CLASSES[key](row, grid)
