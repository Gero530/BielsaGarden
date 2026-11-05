"""
Efectos visuales que no interactúan con nada: una animación que se reproduce
una vez en un lugar (ej: las ratas de Kenny) y un destello que se desvanece
(ej: el área de la explosión), y el balde que el Imán le arranca a un zombie.
"""
import math
import pygame
from ui.sprites import draw_sprite, anim_duration
from entities.zombies import draw_bucket


class SpriteEffect:
    """Reproduce una animación de SPRITES una sola vez y desaparece."""

    def __init__(self, key, center):
        self.key = key
        self.center = center
        self.t = 0.0
        self.duration = anim_duration(key)
        self.alive = True

    def update(self, dt, world):
        self.t += dt
        if self.t >= self.duration:
            self.alive = False

    def draw(self, surface):
        draw_sprite(surface, self.key, self.center, 1.0, self.t)


class Flash:
    """Rectángulo de color que se desvanece (muestra el área de una explosión)."""

    def __init__(self, rect, color=(255, 170, 40), life=0.3, alpha=120):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.life = life
        self.max_life = life
        self.alpha = alpha
        self.alive = True

    def update(self, dt, world):
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def draw(self, surface):
        a = int(self.alpha * max(0.0, self.life) / self.max_life)
        overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(overlay, (*self.color, a), overlay.get_rect(), border_radius=14)
        surface.blit(overlay, self.rect.topleft)


class Rayo:
    """Rayo que cae del cielo sobre un punto (un Chef)."""
    def __init__(self, target, delay=0.0, life=0.5):
        self.target, self.delay, self.life = target, delay, life
        self.alive = True
        self.seed_t = 0.0
        self.pts = self._make()

    def _make(self):
        import random
        x, y = self.target
        pts = [(x + random.randint(-6, 6), 0)]
        for i in range(1, 7):
            pts.append((x + random.randint(-26, 26), int(y * i / 7)))
        pts.append((x, y - 10))
        return pts

    def update(self, dt, world):
        if self.delay > 0:
            self.delay -= dt
            return
        self.life -= dt
        self.seed_t += dt
        if self.seed_t > 0.07:           # titila cambiando de forma
            self.seed_t = 0.0
            self.pts = self._make()
        if self.life <= 0:
            self.alive = False

    def draw(self, surface):
        if self.delay > 0:
            return
        pygame.draw.lines(surface, (255, 236, 60), False, self.pts, 9)
        pygame.draw.lines(surface, (255, 255, 255), False, self.pts, 4)
        pygame.draw.circle(surface, (255, 255, 200), self.pts[-1], 14)
        pygame.draw.circle(surface, (255, 236, 60), self.pts[-1], 14, 3)


class DestelloPantalla:
    """Pantallazo blanco que se desvanece."""
    def __init__(self, life=0.3, alpha=140):
        self.life = self.max_life = life
        self.alpha = alpha
        self.alive = True

    def update(self, dt, world):
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def draw(self, surface):
        a = int(self.alpha * max(0.0, self.life) / self.max_life)
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, a))
        surface.blit(overlay, (0, 0))

class FlyingMetal:
    """
    El balde que el Imán le saca a un zombie: vuela en un arco corto desde la
    cabeza del zombie hasta las puntas del imán, achicándose y girando. Al llegar
    avisa al Imán, que pasa a mostrarlo pegado en su sprite.
    """
    DURACION = 0.4

    def __init__(self, start, magnet):
        self.start = start
        self.magnet = magnet
        self.t = 0.0
        self.alive = True

    def target(self):
        cx, cy = self.magnet.rect.center
        return (cx + self.magnet.PUNTAS[0], cy + self.magnet.PUNTAS[1])

    def update(self, dt, world):
        self.t += dt
        if self.t >= self.DURACION:
            self.alive = False
            if self.magnet.alive:
                self.magnet.catch_metal()

    def draw(self, surface):
        u = min(1.0, self.t / self.DURACION)
        e = 1 - (1 - u) ** 2                      # sale rápido y frena al pegarse
        (x0, y0), (x1, y1) = self.start, self.target()
        x = x0 + (x1 - x0) * e
        y = y0 + (y1 - y0) * e - math.sin(math.pi * u) * 40
        scale = 1.0 + (0.56 - 1.0) * e          # termina del tamaño del balde del sprite
        img = pygame.Surface((48, 40), pygame.SRCALPHA)
        draw_bucket(img, (24, 18), scale)
        img = pygame.transform.rotate(img, u * 360)
        surface.blit(img, img.get_rect(center=(int(x), int(y))))
