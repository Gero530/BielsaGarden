"""
Plantas. Cada tipo hereda de Plant y sobreescribe update() y, si cambia de\nanimación según su estado, sprite_state().
Para agregar una planta nueva:
  1. Agregá sus datos en settings.PLANT_DATA
  2. Creá la clase acá con su `key`
  3. Registrala en PLANT_CLASSES
  4. Agregá la key en la lista "plantas" del nivel
"""
import math
import random
import pygame
from settings import PLANT_DATA, SCREEN_W
from settings import CELL_W, CELL_H
from entities.projectiles import Pea, Ike
from entities.effects import SpriteEffect, Flash
from entities.sun import Sun
from ui.sprites import draw_sprite, has_sprite, anim_duration, SPRITES


class Plant:
    key = None
    hipnotiza = False      # True: el zombie que la muerde queda hipnotizado (Toallin)

    def __init__(self, row, col, grid):
        data = PLANT_DATA[self.key]
        self.data = data
        self.row = row
        self.col = col
        self.max_hp = data["vida"]
        self.hp = self.max_hp
        self.rect = grid.cell_rect(row, col)
        self.alive = True
        self.hit_flash = 0.0
        self.flash_cd = 0.0        # evita que el destello quede fijo mientras la muerden
        self.t = random.random()   # desfase de animación

    def take_damage(self, amount):
        self.hp -= amount
        if self.flash_cd <= 0:          # un destello por "mordisco", no en cada frame
            self.hit_flash = 0.08
            self.flash_cd = 0.35
        if self.hp <= 0:
            self.alive = False

    def update(self, dt, world):
        self.t += dt
        if self.hit_flash > 0:
            self.hit_flash -= dt
        if self.flash_cd > 0:
            self.flash_cd -= dt

    def sprite_state(self):
        """(clave_de_sprite, tiempo) a mostrar ahora. Las subclases lo cambian."""
        return self.key, self.t

    def draw(self, surface):
        key, t = self.sprite_state()
        if draw_sprite(surface, key, self.rect.center, 1.0, t, flash=self.hit_flash > 0):
            return
        # Sin sprite: dibujo con formas + destello circular
        draw_plant_icon(surface, self.key, self.rect.center, 1.0, self)
        if self.hit_flash > 0:
            flash = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            pygame.draw.circle(flash, (255, 255, 255, 90), (self.rect.w // 2, self.rect.h // 2), 32)
            surface.blit(flash, self.rect.topleft)


class Sunflower(Plant):
    key = "girasol"

    def __init__(self, row, col, grid):
        super().__init__(row, col, grid)
        self.timer = self.data["primer_sol"]

    def update(self, dt, world):
        super().update(dt, world)
        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.data["intervalo_sol"]
            # El dedo cae al costado de Cartman (si cayera encima lo taparía)
            x = self.rect.centerx + random.randint(50, 62)
            y = self.rect.centery
            world.suns.append(Sun(x, y - 40, y + 5))


class Peashooter(Plant):
  key = 'lanzaguisantes'
  # Clave en ui/sprites.py (SPRITES) -> apunta a plantas/cartman_disparo.png
  ANIM_DISPARO = 'lanzaguisantes_disparo'
  FRAME_SALIDA = 2  # frame de la animación en que sale el guisante (0 = primero)
  BOCA = (
      30,
      -15,
  )  # posición de la boca del cañón respecto al centro de la celda

  def __init__(self, row, col, grid):
    super().__init__(row, col, grid)
    self.timer = 0.6  # pequeño delay antes del primer disparo
    self.shoot_t = None  # tiempo dentro de la animación de disparo (None = en reposo)
    self.pea_pending = False  # el guisante todavía no salió en este disparo

  def sprite_state(self):
    if self.shoot_t is not None:
      return self.ANIM_DISPARO, self.shoot_t
    return self.key, self.t

  def spawn_pea(self, world):
    world.projectiles.append(
        Pea(
            self.rect.centerx + self.BOCA[0],
            self.rect.centery + self.BOCA[1],
            self.row,
            self.data['dano'],
        )
    )

  def has_target(self, world):
    """Solo dispara si hay un zombie en su fila, delante y dentro de la pantalla."""
    for z in world.zombies:
      if z.alive and not z.hypno and z.row == self.row and self.rect.centerx < z.x < SCREEN_W:
        return True
    return False

  def update(self, dt, world):
    super().update(dt, world)

    # Animación de disparo en curso
    if self.shoot_t is not None:
      self.shoot_t += dt
      fps = SPRITES[self.ANIM_DISPARO]['fps']
      if self.pea_pending and self.shoot_t >= self.FRAME_SALIDA / fps:
        self.pea_pending = False
        self.spawn_pea(world)
      if self.shoot_t >= anim_duration(self.ANIM_DISPARO):
        self.shoot_t = None

    self.timer -= dt
    if self.timer <= 0 and self.has_target(world):
      self.timer = self.data['cadencia']
      if has_sprite(self.ANIM_DISPARO):
        self.shoot_t = 0.0  # arranca la animación; el guisante sale en FRAME_SALIDA
        self.pea_pending = True
      else:
        self.spawn_pea(world)  # sin sprite: dispara al instante


class WallNut(Plant):
    key = "nuez"

    def sprite_state(self):
        frac = self.hp / self.max_hp
        if frac > 2 / 3:
            return "nuez", self.t
        if frac > 1 / 3:
            return "nuez_agrietada", self.t
        return "nuez_mordida", self.t


class Catapult(Plant):
    """
    Kyle. Parado de frente mientras no hay enemigos. Cuando aparece un zombie en su
    fila se da vuelta a la derecha y patea a Ike, que sale volando en arco y cae
    sobre el zombie. Hace el mismo daño que el guisante.
    """
    key = "kyle"
    ANIM_PERFIL = "kyle_perfil"      # de perfil, listo para patear
    ANIM_PATADA = "kyle_patada"      # gira, patea, sigue la patada y vuelve
    FRAME_SALIDA = 2                 # frame de la patada en que sale Ike (0 = primero)
    BOCA = (47, 20)                  # de dónde sale Ike respecto al centro de la celda (el pie)

    def __init__(self, row, col, grid):
        super().__init__(row, col, grid)
        self.grid = grid
        self.timer = 0.6
        self.shoot_t = None          # tiempo dentro de la patada (None = sin patear)
        self.ike_pending = False
        self.alert = False           # hay un zombie en la fila: se queda de perfil

    def sprite_state(self):
        if self.shoot_t is not None:
            return self.ANIM_PATADA, self.shoot_t
        if self.alert:
            return self.ANIM_PERFIL, 0.0
        return self.key, self.t

    def find_target(self, world):
        """El zombie enemigo más cercano en su fila (delante y dentro de la pantalla)."""
        best = None
        for z in world.zombies:
            if z.alive and not z.hypno and z.row == self.row and self.rect.centerx < z.x < SCREEN_W:
                if best is None or z.x < best.x:
                    best = z
        return best

    def kick(self, world):
        target = self.find_target(world)
        if target is None:           # el zombie murió mientras pateaba
            return
        world.projectiles.append(
            Ike(self.rect.centerx + self.BOCA[0], self.rect.centery + self.BOCA[1],
                target, self.data["dano"], self.grid))

    def update(self, dt, world):
        super().update(dt, world)
        self.alert = self.find_target(world) is not None

        if self.shoot_t is not None:
            self.shoot_t += dt
            fps = SPRITES[self.ANIM_PATADA]["fps"]
            if self.ike_pending and self.shoot_t >= self.FRAME_SALIDA / fps:
                self.ike_pending = False
                self.kick(world)
            if self.shoot_t >= anim_duration(self.ANIM_PATADA):
                self.shoot_t = None

        self.timer -= dt
        if self.timer <= 0 and self.alert and self.shoot_t is None:
            self.timer = self.data["cadencia"]
            if has_sprite(self.ANIM_PATADA):
                self.shoot_t = 0.0
                self.ike_pending = True
            else:
                self.kick(world)


class Kenny(Plant):
    """
    Como la cereza explosiva: al plantarlo se infla y explota enseguida, dañando
    un área de 3x3 casillas centrada en él. Después aparecen las ratas y se
    llevan lo que quedó (solo decoración, la casilla queda libre).
    """
    key = "kenny"
    FRAME_EXPLOSION = 4          # frame de la animación en que explota (0 = primero)
    DURACION_EXPLOSION = 0.15    # cuánto se ve el estallido antes de que lleguen las ratas

    def __init__(self, row, col, grid):
        super().__init__(row, col, grid)
        self.age = 0.0
        self.exploded = False

    def take_damage(self, amount):
        pass                     # explota antes de que lo coman

    def sprite_state(self):
        return self.key, self.age

    def explode(self, world):
        """Daña a todos los zombies de las 3 filas y 3 columnas alrededor de Kenny."""
        c = self.rect
        area = pygame.Rect(c.x - CELL_W, c.y - CELL_H, CELL_W * 3, CELL_H * 3)
        for z in world.zombies:
            if z.alive and abs(z.row - self.row) <= 1 and area.left <= z.x <= area.right:
                z.take_damage(self.data["dano"])
        world.effects.append(Flash(area.clip(world.grid.rect)))

    def update(self, dt, world):
        super().update(dt, world)
        self.age += dt
        t_boom = self.FRAME_EXPLOSION / SPRITES[self.key]["fps"]
        if not self.exploded and self.age >= t_boom:
            self.exploded = True
            self.explode(world)
        if self.exploded and self.age >= t_boom + self.DURACION_EXPLOSION:
            self.alive = False
            world.effects.append(SpriteEffect("kenny_ratas", self.rect.center))


class Toallin(Plant):
    """
    Como la hipnoseta: se queda fumando. El primer zombie que lo muerde se lo
    come y queda hipnotizado (ver Zombie.update): se da vuelta y ataca a los
    otros zombies.
    """
    key = "toallin"
    hipnotiza = True


PLANT_CLASSES = {cls.key: cls for cls in (Sunflower, Peashooter, WallNut, Catapult, Kenny, Toallin)}


def create_plant(key, row, col, grid):
    return PLANT_CLASSES[key](row, col, grid)


# ----------------------------------------------------------------------
# Dibujo con formas simples (reemplazable por sprites más adelante).
# Se usa tanto en el tablero como en las cartas del HUD.
# ----------------------------------------------------------------------
def draw_plant_icon(surface, key, center, scale=1.0, plant=None):
    # Si hay sprite en assets/ se usa ese; si no, el dibujo con formas de abajo
    if draw_sprite(surface, key, center, scale, None if plant is None else plant.t):
        return

    x, y = center
    s = scale
    bob = 0
    if plant is not None:
        bob = 2 if int(plant.t * 2) % 2 == 0 else 0

    def P(dx, dy):
        return int(x + dx * s), int(y + (dy + bob) * s)

    if key == "girasol":
        pygame.draw.line(surface, (50, 130, 40), P(0, 5), P(0, 38), max(1, int(6 * s)))
        pygame.draw.ellipse(surface, (60, 150, 50), (*P(-22, 22), int(20 * s), int(10 * s)))
        for i in range(10):
            a = i * math.pi / 5
            pygame.draw.circle(surface, (255, 200, 30), P(math.cos(a) * 20, -8 + math.sin(a) * 20), int(9 * s))
        pygame.draw.circle(surface, (130, 80, 30), P(0, -8), int(14 * s))
        pygame.draw.circle(surface, (20, 20, 20), P(-5, -11), max(1, int(2 * s)))
        pygame.draw.circle(surface, (20, 20, 20), P(5, -11), max(1, int(2 * s)))

    elif key == "lanzaguisantes":
        pygame.draw.line(surface, (50, 130, 40), P(-4, 5), P(-4, 38), max(1, int(6 * s)))
        pygame.draw.ellipse(surface, (60, 150, 50), (*P(-24, 26), int(22 * s), int(10 * s)))
        pygame.draw.circle(surface, (70, 170, 50), P(-4, -10), int(20 * s))
        pygame.draw.rect(surface, (70, 170, 50), (*P(10, -20), int(18 * s), int(16 * s)))
        pygame.draw.circle(surface, (30, 90, 25), P(28, -12), int(7 * s))
        pygame.draw.circle(surface, (20, 20, 20), P(2, -16), max(1, int(4 * s)))

    elif key == "nuez":
        frac = 1.0 if plant is None else plant.hp / plant.max_hp
        body = pygame.Rect(0, 0, int(52 * s), int(66 * s))
        body.center = P(0, 0)
        pygame.draw.ellipse(surface, (110, 70, 30), body)
        pygame.draw.ellipse(surface, (165, 110, 55), body.inflate(-int(8 * s), -int(8 * s)))
        pygame.draw.circle(surface, (255, 255, 255), P(-8, -8), int(7 * s))
        pygame.draw.circle(surface, (255, 255, 255), P(10, -8), int(7 * s))
        pygame.draw.circle(surface, (20, 20, 20), P(-7, -7), max(1, int(3 * s)))
        pygame.draw.circle(surface, (20, 20, 20), P(11, -7), max(1, int(3 * s)))
        # Grietas según el daño recibido
        if frac < 0.66:
            pygame.draw.lines(surface, (70, 40, 15), False, [P(-14, -24), P(-8, -14), P(-14, -4)], 2)
        if frac < 0.33:
            pygame.draw.lines(surface, (70, 40, 15), False, [P(14, 6), P(6, 14), P(14, 24)], 2)
