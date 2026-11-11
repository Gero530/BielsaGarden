"""Proyectiles: el guisante (recto), la bola de nieve de Stan (recta, ralentiza) e Ike (en arco, lo patea Kyle)."""
import pygame
from ui.sprites import draw_sprite
from ui import sonidos
from settings import GUISANTE_VEL, IKE_VEL, SCREEN_W, NIEVE_DURACION

IKE_PX = 3          # Ike se ve x3: la sombra usa el mismo tamaño de píxel
_sombras = {}


def _sombra(w):
    """Sombra ovalada de 2w x 4 píxeles de dibujo, agrandada xIKE_PX sin suavizado."""
    if w not in _sombras:
        s = pygame.Surface((w * 2, 4), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 70), s.get_rect())
        _sombras[w] = pygame.transform.scale(s, (w * 2 * IKE_PX, 4 * IKE_PX))
    return _sombras[w]


class Pea:
    def __init__(self, x, y, row, damage):
        self.x = x
        self.y = y
        self.row = row
        self.damage = damage
        self.alive = True
        self.fuente = "lanzaguisantes"     # quién la tiró (logros: muertes de Stan)

    def update(self, dt, world):
        self.x += GUISANTE_VEL * dt
        if self.x > SCREEN_W + 20:
            self.alive = False
            return
        # Golpea al primer zombie vivo de su fila que toque
        for z in world.zombies:
            if z.targetable and z.row == self.row and z.rect.left <= self.x <= z.rect.right:
                sonidos.reproducir("impacto")
                self.hit(z)
                self.alive = False
                return

    def hit(self, zombie):
        zombie.take_damage(self.damage, fuente=self.fuente)

    def draw(self, surface):
        c = (int(self.x), int(self.y))
        if draw_sprite(surface, "guisante", c):
            return
        pygame.draw.circle(surface, (40, 120, 30), c, 9)
        pygame.draw.circle(surface, (120, 220, 80), c, 7)


class Snowball(Pea):
    """Bola de nieve de Stan: va recta como el guisante y además ralentiza al zombie."""

    def hit(self, zombie):
        en_la_puerta = zombie.shield > 0 and not zombie.escudo_total   # rebota en la puerta: no lo frena
        zombie.take_damage(self.damage, fuente=self.fuente)
        if not en_la_puerta:
            zombie.slow_down(NIEVE_DURACION)

    def draw(self, surface):
        c = (int(self.x), int(self.y))
        if draw_sprite(surface, "bola_nieve", c):
            return
        pygame.draw.circle(surface, (255, 255, 255), c, 7)


class Ike:
    """
    Proyectil en arco (como las catapultas del original). Sale del pie de Kyle,
    vuela por encima de lo que haya en el camino y cae sobre el zombie al que
    apuntó, apuntando a donde va a estar cuando aterrice.
    Elige el frame según la fase del vuelo: salida, inclinado, girando, cayendo.
    """
    # Frames de ike_volando.png
    F_SALIDA, F_INCLINADO, F_GIRO, F_CAIDA = 1, 2, (3, 4, 5), 6

    def __init__(self, x, y, target, damage, grid):
        self.row = target.row
        self.damage = damage
        self.alive = True
        self.t = 0.0
        self.x0, self.y0 = x, y
        dist = abs(target.x - x)
        self.T = min(1.6, max(0.5, dist / IKE_VEL + 0.15))      # duración del vuelo
        # Los zombies caminan: apunta a donde van a estar al aterrizar
        avance = 0.0 if (target.eating or target.hypno) else target.cur_speed * self.T
        self.x1 = max(x + 30, target.x - avance)
        self.y1 = grid.row_center_y(self.row) - 6                # altura del torso
        self.ground = grid.row_center_y(self.row) + 40           # donde se dibuja la sombra
        self.peak = 70 + min(60, dist / 6)                       # altura máxima del arco
        self.pos = (x, y)
        self.arc = 0.0

    def update(self, dt, world):
        self.t += dt
        u = self.t / self.T
        if u >= 1.0:
            self.land(world)
            return
        self.arc = 4 * self.peak * u * (1 - u)
        x = self.x0 + (self.x1 - self.x0) * u
        y = self.y0 + (self.y1 - self.y0) * u - self.arc
        self.pos = (x, y)

    def land(self, world):
        """Daña al zombie (vivo y no hipnotizado) más cercano al punto de caída."""
        best = None
        for z in world.zombies:
            if z.targetable and z.row == self.row and abs(z.x - self.x1) <= 45:
                if best is None or abs(z.x - self.x1) < abs(best.x - self.x1):
                    best = z
        if best is not None:
            sonidos.reproducir("impacto")
            best.take_damage(self.damage, frontal=False, fuente="kyle")   # cae de arriba: la puerta no lo frena
        self.alive = False

    def frame(self):
        u = self.t / self.T
        if u < 0.12:
            return self.F_SALIDA
        if u < 0.25:
            return self.F_INCLINADO
        if u > 0.88:
            return self.F_CAIDA
        return self.F_GIRO[int(self.t * 12) % len(self.F_GIRO)]

    def draw(self, surface):
        x, y = self.pos
        # Sombra en el piso: más chica y clara cuanto más alto está
        w = max(3, int(34 - self.arc / 5) // IKE_PX)        # medio ancho en píxeles de dibujo
        sh = _sombra(w)
        surface.blit(sh, ((int(x) - w * IKE_PX) // IKE_PX * IKE_PX,
                          (int(self.ground) - 2 * IKE_PX) // IKE_PX * IKE_PX))
        if not draw_sprite(surface, "ike", (int(x), int(y)), 1.0, None, frame=self.frame()):
            pygame.draw.circle(surface, (110, 190, 255), (int(x), int(y)), 12)
