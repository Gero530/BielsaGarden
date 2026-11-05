"""
Zombies. Avanzan por su fila hacia la izquierda; si tienen una planta
delante se frenan y la comen. La armadura (cono/cubeta) absorbe daño antes
que el cuerpo.
Las bolas de nieve de Stan los ralentizan (caminan, comen y se animan más
lento) y se ven celestes mientras dura.
Si muerden a Toallin quedan hipnotizados: se dan vuelta, se ponen violetas y
caminan hacia la derecha mordiendo a los zombies que encuentren.
"""
import random
import pygame
from settings import ZOMBIE_DATA, SCREEN_W, CELL_H, CELL_W, NIEVE_RALENTIZA, ALIEN_CASILLAS
from ui.sprites import draw_sprite, has_sprite, anim_duration, SPRITES
from ui import sonidos

HIPNO_TINTE = (190, 130, 255)     # color que se multiplica sobre el sprite hipnotizado
HIPNO_ALCANCE = 36                 # a qué distancia (px) muerde a otro zombie
NIEVE_TINTE = (150, 200, 255)      # celeste mientras está ralentizado por la nieve de Stan


class Zombie:
    key = "normal"
    metal = False              # True: lleva un objeto de metal que el Imán le puede sacar
    # Sprite del cuerpo. Cono y cubeta usan el mismo cuerpo y dibujan el accesorio encima.
    # Si algún día hacés un sprite propio para cada uno, cambiá esta clave en su clase.
    sprite_key = "zombie_normal"

    def __init__(self, row, grid):
        data = ZOMBIE_DATA[self.key]
        self.row = row
        self.x = float(SCREEN_W + random.randint(10, 60))
        self.y_top = grid.row_center_y(row) - CELL_H // 2
        self.hp = data["vida"]
        self.max_hp = data["vida"]
        self.armor = data["armadura"]
        self.max_armor = data["armadura"]
        self.speed = data["velocidad"] * random.uniform(0.92, 1.08)
        self.dps = data["dps"]
        self.alive = True
        self.eating = False
        self.hit_flash = 0.0
        self.t = random.random() * 2
        self.hypno = False         # True: pelea de nuestro lado
        self.stun = 0.0            # frenado un instante porque un hipnotizado lo está mordiendo
        self.slow = 0.0            # segundos que le quedan ralentizado (bola de nieve de Stan)

    @property
    def slow_factor(self):
        return NIEVE_RALENTIZA if self.slow > 0 else 1.0

    @property
    def cur_speed(self):
        """Velocidad real en este momento (con la ralentización aplicada)."""
        return self.speed * self.slow_factor

    def slow_down(self, duration):
        self.slow = max(self.slow, duration)

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - 20, self.y_top + 8, 40, CELL_H - 16)

    def take_damage(self, amount):
        self.hit_flash = 0.08
        if self.armor > 0:
            absorbed = min(self.armor, amount)
            self.armor -= absorbed
            amount -= absorbed
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

    def can_lose_metal(self):
        return self.alive and not self.hypno and self.metal and self.armor > 0

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

    def update_hypno(self, dt, world):
        """Hipnotizado: camina a la derecha y muerde al zombie enemigo que tenga cerca."""
        victim = None
        for z in world.zombies:
            if z is not self and z.alive and not z.hypno and z.row == self.row \
                    and abs(z.x - self.x) < HIPNO_ALCANCE:
                victim = z
                break
        if victim is not None:
            self.eating = True
            victim.take_damage(self.dps * self.slow_factor * dt)
            # El mordido se defiende: el hipnotizado también pierde vida (y puede morir)
            self.take_damage(victim.dps * victim.slow_factor * dt)
            victim.stun = 0.15          # el mordido se queda quieto mientras lo comen
        else:
            self.eating = False
            self.x += self.cur_speed * dt
            if self.x > SCREEN_W + 60:  # salió de la pantalla
                self.alive = False

    def update(self, dt, world):
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

        # ¿Hay una planta justo delante (en la "boca" del zombie)?
        col = world.grid.col_at_x(self.x - 22)
        target = world.grid.get(self.row, col) if col is not None else None

        if target is not None and target.alive:
            if getattr(target, "hipnotiza", False):
                # Se comió a Toallin: queda hipnotizado y Toallin desaparece
                target.alive = False
                self.hypnotize()
                sonidos.reproducir("hipnosis")
                return
            # El ruido de masticar lo maneja gameplay.py en bucle mientras algún zombie come
            self.eating = True
            target.take_damage(self.dps * self.slow_factor * dt)
        else:
            self.eating = False
            self.x -= self.cur_speed * dt

    # --- Dibujo ---
    def draw(self, surface):
        if has_sprite(self.sprite_key):
            self.draw_with_sprite(surface)
        else:
            self.draw_shapes(surface)

    def draw_with_sprite(self, surface):
        # Pies apoyados en el fondo de la fila; el sprite (x2) mide 64x96
        cx, cy = int(self.x), self.y_top + CELL_H - 48
        # Hipnotizado: el sprite se espeja (mira a la derecha) y se tiñe de violeta
        lado = 1 if self.hypno else -1
        flip = self.hypno
        tint = HIPNO_TINTE if self.hypno else (NIEVE_TINTE if self.slow > 0 else None)
        if self.eating:
            # Mordiendo: frame quieto y un pequeño cabeceo hacia adelante
            dx = 3 * lado if int(self.t * 8) % 2 == 0 else 0
            draw_sprite(surface, self.sprite_key, (cx + dx, cy), 1.0, None,
                        flash=self.hit_flash > 0, flip=flip, tint=tint)
            head = (cx + 4 * lado + dx, self.y_top + 22)
        else:
            draw_sprite(surface, self.sprite_key, (cx, cy), 1.0, self.t,
                        flash=self.hit_flash > 0, flip=flip, tint=tint)
            head = (cx + 4 * lado, self.y_top + 22)
        self.draw_armor(surface, head)
        self.draw_health_bar(surface)

    def draw_health_bar(self, surface):
        r = self.rect
        total = self.max_hp + self.max_armor
        cur = max(0, self.hp) + max(0, self.armor)
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
            draw_sprite(surface, "alien", (cx, cy), 1.0, self.t, flash=fl, tint=tint)
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


ZOMBIE_CLASSES = {cls.key: cls for cls in (NormalZombie, ConeZombie, BucketZombie, AlienZombie)}


def create_zombie(key, row, grid):
    return ZOMBIE_CLASSES[key](row, grid)
