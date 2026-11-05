"""
Cortacéspedes: última defensa de cada fila. Es Timmy en su silla de ruedas:
espera al borde del césped y, cuando un zombie llega hasta ahí, grita
"¡TIMMY!", sale disparado por la fila llevándose a todos los zombies y se
consume (como en el original, uno por fila).

El movimiento se hace por código sobre el sprite (sirve aunque tenga un solo frame):
  - quieto: se mece despacio, de a 1 píxel de dibujo
  - activado: traquetea arriba/abajo y va dejando polvo atrás
Si más adelante dibujás tiras con más frames (ej: moviendo los brazos), alcanza
con apuntar las claves "podadora" y "podadora_activa" de ui/sprites.py al PNG nuevo.
"""
import random
import pygame
from settings import GRID_X, SCREEN_W
from ui.sprites import draw_sprite, has_sprite
from ui.pixel_font import draw_pixel_text
from ui import sonidos

VELOCIDAD = 420
PIXEL = 3                  # tamaño en pantalla de un píxel del dibujo (el sprite va x3)
PIES_DY = 46               # pies a la misma altura que los chicos del tablero (centro de fila + 46)
DURACION_GRITO = 1.0       # segundos que se ve el "¡TIMMY!"

_nubes = {}


def _nube(n, alfa):
    """Nubecita de polvo de radio n (píxeles de dibujo), agrandada xPIXEL sin suavizado."""
    if (n, alfa) not in _nubes:
        s = pygame.Surface((n * 2, n * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (210, 200, 180, alfa), (n, n), n)
        _nubes[(n, alfa)] = pygame.transform.scale(s, (n * 2 * PIXEL, n * 2 * PIXEL))
    return _nubes[(n, alfa)]


class LawnMower:
    def __init__(self, row, grid):
        self.row = row
        self.x = float(GRID_X - 32)
        self.y = grid.row_center_y(row) + 18           # se usa en el dibujo con formas
        self.feet_y = grid.row_center_y(row) + PIES_DY
        self.active = False      # en movimiento
        self.used = False        # ya se gastó
        self.t = random.random() * 3     # desfase para que no se mezan todos a la vez
        self.shout = 0.0         # tiempo restante del grito
        self.dust = []           # nubecitas de polvo: [x, y, edad]

    def update(self, dt, world):
        self.t += dt
        if self.shout > 0:
            self.shout -= dt
        if not self.active and not self.used:
            for z in world.zombies:
                if z.row == self.row and z.alive and not z.airborne and not z.hypno and z.x < GRID_X + 5:
                    self.active = True
                    self.shout = DURACION_GRITO
                    sonidos.reproducir("timmy")
                    break
        if self.active:
            self.x += VELOCIDAD * dt
            for z in world.zombies:
                if z.row == self.row and z.alive and not z.airborne and not z.hypno and abs(z.x - self.x) < 30:
                    z.alive = False
            # polvo que levantan las ruedas
            if random.random() < 0.6:
                self.dust.append([self.x - 22, self.feet_y - random.randint(2, 10), 0.0])
            if self.x > SCREEN_W + 40:
                self.active = False
                self.used = True
        for d in self.dust:
            d[2] += dt
        self.dust = [d for d in self.dust if d[2] < 0.4]

    # --- Dibujo ---
    def draw(self, surface):
        """Capa de abajo: Timmy esperando al borde del césped."""
        if not self.used and not self.active:
            self.draw_body(surface)

    def draw_overlay(self, surface):
        """Capa de arriba (después de plantas y zombies): Timmy en marcha, el polvo y el grito."""
        self.draw_dust(surface)
        if self.active:
            self.draw_body(surface)
        if self.shout > 0 and has_sprite("podadora"):
            self.draw_shout(surface, int(self.x))

    def draw_body(self, surface):
        if has_sprite("podadora"):
            self.draw_with_sprite(surface)
        else:
            self.draw_shapes(surface)

    def draw_with_sprite(self, surface):
        x = int(self.x)
        if self.active:
            key, t = "podadora_activa", self.t
            bob = 0
                  # traqueteo rápido
        else:
            key, t = "podadora", self.t
            bob = -PIXEL if int(self.t * 1.5) % 2 == 0 else 0     # se mece despacio
        # ui/sprites.py ya ubica los pies con dy_px; acá solo se suma el bamboleo
        draw_sprite(surface, key, (x, self.feet_y - PIES_DY + bob), 1.0, t)

    def draw_shout(self, surface, x):
        # Sube un poco y tiembla mientras dura
        u = 1 - self.shout / DURACION_GRITO
        dx = random.choice((-2, 0, 2))
        y = self.feet_y - 100 - int(u * 14)
        draw_pixel_text(surface, "TIMMY!", (255, 230, 60), scale=2,
                        center=(x + 10 + dx, y), outline=(40, 20, 10))

    def draw_dust(self, surface):
        for x, y, edad in self.dust:
            n = max(1, round((4 + edad * 18) / PIXEL))          # radio en píxeles de dibujo
            a = int(150 * (1 - edad / 0.4)) // 30 * 30          # pocos niveles de transparencia
            img = _nube(n, a)
            px = (int(x - edad * 40) - n * PIXEL) // PIXEL * PIXEL
            py = (int(y) - n * PIXEL) // PIXEL * PIXEL
            surface.blit(img, (px, py))

    def draw_shapes(self, surface):
        """Sin sprite: la podadora roja de antes."""
        x, y = int(self.x), int(self.y)
        pygame.draw.rect(surface, (200, 40, 40), (x - 20, y - 14, 40, 20), border_radius=4)
        pygame.draw.line(surface, (60, 60, 60), (x - 18, y - 12), (x - 30, y - 34), 3)
        pygame.draw.circle(surface, (30, 30, 30), (x - 12, y + 8), 7)
        pygame.draw.circle(surface, (30, 30, 30), (x + 12, y + 8), 7)
