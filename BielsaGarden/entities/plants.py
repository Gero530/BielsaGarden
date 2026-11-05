"""
Plantas. Cada tipo hereda de Plant y sobreescribe update() y, si cambia de\nanimación según su estado, sprite_state().
Para agregar una planta nueva:
  1. Agregá sus datos en settings.PLANT_DATA
  2. Creá la clase acá con su `key`
  3. Registrala en PLANT_CLASSES
  4. Aparece sola en la pantalla de equipo (y en data/catalogo.py sumale nombre y descripción)
"""
import math
import random
import pygame
from settings import PLANT_DATA, SCREEN_W, CHEF_REACTIVA
from settings import CELL_W, CELL_H
from entities.projectiles import Snowball, Ike
from entities.effects import SpriteEffect, Flash, FlyingMetal, FloatingText
from data.catalogo import FRASE_KENNY_EXPLOTA, FRASES_AL_PLANTAR
from entities.sun import Sun
from ui.sprites import draw_sprite, has_sprite, anim_duration, SPRITES
from ui import sonidos


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
        self.estado = "normal"     # normal -> golpe (rayo) -> cantando (hasta que muera el alien)
        self.est_t = 0.0

    def sonda(self, delay=0.0):
        """Le cae el rayo: deja de producir y se pone a cantar."""
        if self.estado == "normal":
            self.estado = "golpe"
            self.est_t = -delay        # negativo = el rayo todavía no llegó

    @property
    def deshabilitado(self):
        return self.estado != "normal"

    def sprite_state(self):
        if self.estado == "golpe" and self.est_t >= 0 and has_sprite("girasol_sonda"):
            return "girasol_sonda", self.est_t
        if self.estado == "cantando" and has_sprite("girasol_deshabilitado"):
            return "girasol_deshabilitado", self.est_t
        return self.key, self.t

    def update(self, dt, world):
        super().update(dt, world)
        if self.estado != "normal":
            self.est_t += dt
            if self.estado == "golpe" and self.est_t >= anim_duration("girasol_sonda"):
                self.estado = "cantando"
                self.est_t = 0.0
            if not world.hay_aliens_activos():     # murió el alien: vuelve a cocinar
                self.estado = "normal"
                self.timer = CHEF_REACTIVA
            return                                  # deshabilitado: no produce soles
        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.data["intervalo_sol"]
            x = self.rect.centerx + random.randint(-12, 12)
            world.suns.append(Sun(x, self.rect.top, self.rect.centery + 10))


class Peashooter(Plant):
    """
    Stan. Tira bolas de nieve que hacen daño y ralentizan al zombie (como el
    lanzaguisantes de hielo). Quieto con stan_idle; cuando aparece un zombie en
    su fila se queda en pose de tiro (stan_disparo) y lanza cada `cadencia` s.
    """
    key = "lanzaguisantes"
    ANIM_ALERTA = "lanzaguisantes_alerta"    # primer frame de stan_disparo: bola en la mano
    ANIM_DISPARO = "lanzaguisantes_disparo"  # stan_disparo completo
    FRAME_SALIDA = 3   # frame de la animación en que sale la bola (0 = primero)
    BOCA = (39, 19)    # de dónde sale la bola respecto al centro de la celda (su mano)

    def __init__(self, row, col, grid):
        super().__init__(row, col, grid)
        self.timer = 0.6          # pequeño delay antes del primer disparo
        self.shoot_t = None       # tiempo dentro de la animación de disparo (None = sin tirar)
        self.pea_pending = False  # la bola todavía no salió en este disparo
        self.alert = False        # hay un zombie en la fila

    def sprite_state(self):
        if self.shoot_t is not None:
            return self.ANIM_DISPARO, self.shoot_t
        if self.alert and has_sprite(self.ANIM_ALERTA):
            return self.ANIM_ALERTA, 0.0
        return self.key, self.t

    def spawn_pea(self, world):
        sonidos.reproducir("disparo")
        world.projectiles.append(
            Snowball(self.rect.centerx + self.BOCA[0], self.rect.centery + self.BOCA[1],
                     self.row, self.data["dano"]))

    def has_target(self, world):
        """Solo dispara si hay un zombie en su fila, delante y dentro de la pantalla."""
        for z in world.zombies:
            if z.targetable and z.row == self.row and self.rect.centerx < z.x < SCREEN_W:
                return True
        return False

    def update(self, dt, world):
        super().update(dt, world)
        self.alert = self.has_target(world)

        # Animación de disparo en curso
        if self.shoot_t is not None:
            self.shoot_t += dt
            fps = SPRITES[self.ANIM_DISPARO]["fps"]
            if self.pea_pending and self.shoot_t >= self.FRAME_SALIDA / fps:
                self.pea_pending = False
                self.spawn_pea(world)
            if self.shoot_t >= anim_duration(self.ANIM_DISPARO):
                self.shoot_t = None

        self.timer -= dt
        if self.timer <= 0 and self.alert and self.shoot_t is None:
            self.timer = self.data["cadencia"]
            if has_sprite(self.ANIM_DISPARO):
                self.shoot_t = 0.0  # arranca la animación; la bola sale en FRAME_SALIDA
                self.pea_pending = True
            else:
                self.spawn_pea(world)  # sin sprite: dispara al instante


class WallNut(Plant):
    """
    Butters. Muro con mucha vida: quieto muestra butters_idle y, mientras los
    zombies lo están mordiendo, butters_comido (llorando).
    """
    key = "nuez"
    ANIM_COMIDO = "nuez_comido"
    MARGEN_MORDIDA = 0.2    # segundos sin mordiscos para volver a la pose quieta

    def __init__(self, row, col, grid):
        super().__init__(row, col, grid)
        self.eaten_t = 0.0      # > 0 mientras lo están comiendo

    def take_damage(self, amount):
        super().take_damage(amount)
        self.eaten_t = self.MARGEN_MORDIDA   # los zombies lo dañan en cada frame que muerden

    def update(self, dt, world):
        super().update(dt, world)
        if self.eaten_t > 0:
            self.eaten_t -= dt

    def sprite_state(self):
        if self.eaten_t > 0 and has_sprite(self.ANIM_COMIDO):
            return self.ANIM_COMIDO, self.t
        return self.key, self.t


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
            if z.targetable and z.row == self.row and self.rect.centerx < z.x < SCREEN_W:
                if best is None or z.x < best.x:
                    best = z
        return best

    def kick(self, world):
        target = self.find_target(world)
        if target is None:           # el zombie murió mientras pateaba
            return
        sonidos.reproducir("disparo")
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
    A los "revive" segundos vuelve a aparecer en la misma casilla (si sigue libre). El Kenny
    revivido espera quieto hasta que un zombie entra en su área de 3x3 y recién ahí explota.
    Revive una sola vez: cuando el revivido explota, desaparece para siempre.
    """
    key = "kenny"
    FRAME_EXPLOSION = 4          # frame de la animación en que explota (0 = primero)
    DURACION_EXPLOSION = 0.15    # cuánto se ve el estallido antes de que lleguen las ratas

    def __init__(self, row, col, grid, revivido=False):
        super().__init__(row, col, grid)
        self.age = 0.0
        self.exploded = False
        self.revivido = revivido
        self.esperando = revivido    # revivido: espera a que un zombie se acerque

    def take_damage(self, amount):
        pass                     # explota antes de que lo coman

    def sprite_state(self):
        return self.key, (0.0 if self.esperando else self.age)

    def area(self):
        c = self.rect
        return pygame.Rect(c.x - CELL_W, c.y - CELL_H, CELL_W * 3, CELL_H * 3)

    def en_area(self, z, area):
        return z.alive and not z.hypno and not z.airborne and abs(z.row - self.row) <= 1 \
            and area.left <= z.x <= area.right

    def explode(self, world):
        """Daña a todos los zombies de las 3 filas y 3 columnas alrededor de Kenny."""
        area = self.area()
        sonidos.reproducir("explosion")
        sonidos.reproducir("kenny")
        for z in world.zombies:
            if self.en_area(z, area):
                z.take_damage(self.data["dano"], frontal=False)   # explosión: la puerta no la frena
        world.effects.append(Flash(area.clip(world.grid.rect)))
        world.effects.append(FloatingText(FRASE_KENNY_EXPLOTA, (self.rect.centerx, self.rect.top + 10)))

    def update(self, dt, world):
        super().update(dt, world)
        if self.esperando:
            area = self.area()
            if not any(self.en_area(z, area) for z in world.zombies):
                return
            self.esperando = False
        self.age += dt
        t_boom = self.FRAME_EXPLOSION / SPRITES[self.key]["fps"]
        if not self.exploded and self.age >= t_boom:
            self.exploded = True
            self.explode(world)
        if self.exploded and self.age >= t_boom + self.DURACION_EXPLOSION:
            self.alive = False
            world.effects.append(SpriteEffect("kenny_ratas", self.rect.center))
            if not self.revivido:    # una sola vuelta por planta
                world.effects.append(RevivirKenny(self.row, self.col, self.data["revive"]))


class RevivirKenny:
    """Efecto invisible: cuenta los segundos y, si la casilla sigue libre, vuelve a poner a Kenny."""

    def __init__(self, row, col, segundos):
        self.row, self.col = row, col
        self.t = segundos
        self.alive = True

    def update(self, dt, world):
        self.t -= dt
        if self.t <= 0:
            self.alive = False
            if world.grid.is_free(self.row, self.col):
                world.grid.place(Kenny(self.row, self.col, world.grid, revivido=True))

    def draw(self, surface):
        pass


class Toallin(Plant):
    """
    Como la hipnoseta: se queda fumando. El primer zombie que lo muerde se lo
    come y queda hipnotizado (ver Zombie.update): se da vuelta y ataca a los
    otros zombies.
    """
    key = "toallin"
    hipnotiza = True


class Magnet(Plant):
    """
    Imán (como el Magnetoseta). Cuando un zombie con un objeto de metal (el balde
    de la cubeta) entra en su alcance, levanta el imán, se lo arranca y el balde
    vuela hasta las puntas. Se queda con el balde pegado (que se va deshaciendo)
    mientras recarga; después vuelve a estar listo. El cono no es de metal.
    Estados: "listo" -> "atrae" -> (vuela el balde) -> "cargado" -> "listo"
    """
    key = "iman"
    ANIM_ATRAE = "iman_atrae"
    ANIM_CARGADO = "iman_cargado"
    PUNTAS = (40, 28)    # dónde queda pegado el balde respecto al centro de la celda

    def __init__(self, row, col, grid):
        super().__init__(row, col, grid)
        self.state = "listo"
        self.state_t = 0.0
        self.target = None
        self.recharge = 0.0

    def find_target(self, world):
        """El zombie con metal más cercano dentro del alcance (en cualquier fila)."""
        cx, cy = self.rect.center
        best, best_d = None, self.data["alcance"]
        for z in world.zombies:
            if not z.can_lose_metal() or z.x > SCREEN_W:
                continue
            zy = world.grid.row_center_y(z.row)
            d = math.hypot(z.x - cx, zy - cy)
            if d <= best_d:
                best, best_d = z, d
        return best

    def catch_metal(self):
        """Llamado por FlyingMetal cuando el balde llega a las puntas del imán."""
        self.state = "cargado"
        self.recharge = self.data["recarga_iman"]

    def update(self, dt, world):
        super().update(dt, world)
        self.state_t += dt
        if self.state == "listo":
            self.target = self.find_target(world)
            if self.target is not None:
                self.state, self.state_t = "atrae", 0.0
        elif self.state == "atrae":
            if self.state_t >= anim_duration(self.ANIM_ATRAE) and self.target is not None:
                if self.target.can_lose_metal():
                    start = self.target.metal_pos()
                    self.target.remove_metal()
                    sonidos.reproducir("iman")
                    world.effects.append(FlyingMetal(start, self))
                    self.target = None          # queda esperando a que llegue el balde
                else:                           # murió o lo perdió en el medio: vuelve a buscar
                    self.state, self.target = "listo", None
        elif self.state == "cargado":
            self.recharge -= dt
            if self.recharge <= 0:
                self.state, self.state_t = "listo", 0.0

    def sprite_state(self):
        if self.state == "atrae":
            return self.ANIM_ATRAE, self.state_t
        if self.state == "cargado":
            # 3 etapas del balde (entero, mordido, casi deshecho) según cuánto falta
            u = 1 - self.recharge / self.data["recarga_iman"]
            return self.ANIM_CARGADO, float(min(2, int(u * 3)))
        return self.key, self.t


class Picante(Plant):
    """
    Como el Jalapeño pero en CRUZ: al plantarlo se infla y explota, quemando toda su
    fila y toda su columna. Después desaparece.
    """
    key = "picante"
    ANIM_FUEGO = "picante_fuego"

    def __init__(self, row, col, grid):
        super().__init__(row, col, grid)
        self.age = 0.0

    def take_damage(self, amount):
        pass                     # explota antes de que lo coman

    def sprite_state(self):
        return self.key, self.age

    def explode(self, world):
        g = world.grid
        col_rect = g.cell_rect(0, self.col)
        for z in world.zombies:
            if not z.alive or z.hypno or z.airborne:
                continue
            en_fila = z.row == self.row and g.rect.left - 20 <= z.x <= SCREEN_W
            en_col = col_rect.left - 20 < z.x < col_rect.right + 20     # el cuerpo toca la columna
            if en_fila or en_col:
                z.take_damage(self.data["dano"], frontal=False)
        cells = [(self.row, c) for c in range(g.cols)] + [(r, self.col) for r in range(g.rows) if r != self.row]
        if has_sprite(self.ANIM_FUEGO):
            for r, c in cells:
                world.effects.append(SpriteEffect(self.ANIM_FUEGO, g.cell_rect(r, c).center))
        else:
            row_rect = g.cell_rect(self.row, 0).union(g.cell_rect(self.row, g.cols - 1))
            world.effects.append(Flash(row_rect, (255, 90, 30)))
            world.effects.append(Flash(col_rect.union(g.cell_rect(g.rows - 1, self.col)), (255, 90, 30)))

    def update(self, dt, world):
        super().update(dt, world)
        self.age += dt
        if self.age >= (anim_duration(self.key) or 0.6):
            self.explode(world)
            self.alive = False


class Aplastadora(Plant):
    """
    Como la Calabaza pero reutilizable. Si hay un zombie en la casilla de enfrente (y esa
    casilla no tiene planta), se agacha, salta y cae encima: mata a TODOS los zombies de esa
    casilla, sea cual sea. Se queda en la casilla nueva (la vieja queda libre) y entra en
    enfriamiento; después puede volver a saltar.
    Estados: listo -> prepara -> salto -> aterriza -> listo (con enfriamiento)
    """
    key = "aplastadora"
    ANIM_SALTO = "aplastadora_salto"   # frames: 0-1 prepara, 2 sube, 3 cae, 4 aplasta
    ATERRIZA = 0.35                    # segundos que se ve aplastando

    def __init__(self, row, col, grid):
        super().__init__(row, col, grid)
        self.state = "listo"
        self.st = 0.0
        self.cooldown = 0.5
        self.from_center = self.rect.center
        self.target_col = None

    def take_damage(self, amount):
        if self.state == "listo":       # en el aire no la pueden morder
            super().take_damage(amount)

    ALCANCE_PROPIA = 24     # px a la derecha de su casilla donde se para el zombie que la muerde

    def zombie_in(self, world, c, extra=0):
        r = world.grid.cell_rect(self.row, c)
        return any(z.alive and not z.hypno and not z.underground and not z.airborne
                   and z.row == self.row and r.left <= z.x <= r.right + extra for z in world.zombies)

    def pick_target(self, world):
        """Columna a la que salta: la de enfrente si está libre y tiene un zombie. Si no tiene
        adonde saltar (última columna o planta adelante), aplasta su propia casilla."""
        g = world.grid
        c = self.col + 1
        if c < g.cols and g.is_free(self.row, c):
            return c if self.zombie_in(world, c) else None
        return self.col if self.zombie_in(world, self.col, self.ALCANCE_PROPIA) else None

    def update(self, dt, world):
        super().update(dt, world)
        self.st += dt
        g = world.grid
        if self.state == "listo":
            if self.cooldown > 0:
                self.cooldown -= dt
            else:
                self.target_col = self.pick_target(world)
                if self.target_col is not None:
                    self.state, self.st = "prepara", 0.0
        elif self.state == "prepara" and self.st >= self.data["preparacion"]:
            c = self.target_col
            if c == self.col:                       # salta en el lugar
                self.from_center = self.rect.center
                self.state, self.st = "salto", 0.0
            elif c < g.cols and g.is_free(self.row, c):
                # Se muda ya en la grilla (así nadie planta ahí mientras vuela); la casilla vieja queda libre
                self.from_center = self.rect.center
                g.remove(self.row, self.col)
                self.col = c
                self.rect = g.cell_rect(self.row, c)
                g.place(self)
                self.state, self.st = "salto", 0.0
            else:
                self.state = "listo"
        elif self.state == "salto" and self.st >= self.data["salto"]:
            r = self.rect
            extra = self.ALCANCE_PROPIA if self.from_center == r.center else 10
            for z in world.zombies:
                if z.alive and not z.hypno and not z.underground and not z.airborne \
                        and z.row == self.row and r.left - 10 <= z.x <= r.right + extra:
                    z.kill()
            self.state, self.st = "aterriza", 0.0
        elif self.state == "aterriza" and self.st >= self.ATERRIZA:
            self.state = "listo"
            self.cooldown = self.data["recarga_salto"]

    def draw(self, surface):
        if self.state == "listo":
            return super().draw(surface)
        cx, cy = self.rect.center
        if self.state == "prepara":
            frame = 0 if self.st < self.data["preparacion"] / 2 else 1
        elif self.state == "salto":
            u = min(1.0, self.st / self.data["salto"])
            frame = 2 if u < 0.5 else 3
            cx = int(self.from_center[0] + (cx - self.from_center[0]) * u)
            cy = int(cy - math.sin(math.pi * u) * 90)
        else:
            frame = 4
        if not draw_sprite(surface, self.ANIM_SALTO, (cx, cy), 1.0, frame=frame):
            pygame.draw.ellipse(surface, (70, 170, 60), (cx - 30, cy - 20, 60, 50))


PLANT_CLASSES = {cls.key: cls for cls in (Sunflower, Peashooter, WallNut, Catapult, Kenny, Toallin, Magnet,
                                          Picante, Aplastadora)}


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
