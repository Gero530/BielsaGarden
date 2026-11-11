"""
Efectos visuales que no interactúan con nada: una animación que se reproduce
una vez en un lugar (ej: las ratas de Kenny) y un destello que se desvanece
(ej: el área de la explosión), y el balde que el Imán le arranca a un zombie.
"""
import math
import pygame
from ui.sprites import draw_sprite, anim_duration, get_frames
from entities.zombies import draw_bucket
from ui.pixel_font import draw_pixel_text, text_width
from settings import SCREEN_W


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


class FloatingText:
    """Frase en pixel art que aparece sobre un personaje, sube un poco y desaparece."""
    ESCALA = 2

    def __init__(self, text, pos, color=(255, 240, 120), life=1.8):
        self.text = text
        half = text_width(text, self.ESCALA) // 2 + 6
        self.x = min(max(pos[0], half), SCREEN_W - half)     # que no se salga de la pantalla
        self.y = max(pos[1], 118)                            # que no la tape el HUD
        self.color = color
        self.life = life
        self.t = 0.0
        self.alive = True

    def update(self, dt, world):
        self.t += dt
        if self.t >= self.life:
            self.alive = False

    def draw(self, surface):
        y = self.y - int(self.t * 12) // 2 * 2               # sube de a 2 px (1 píxel de dibujo)
        draw_pixel_text(surface, self.text, self.color, self.ESCALA, outline=(30, 15, 5), midbottom=(self.x, y))


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
    El objeto de metal que el Imán le saca a un zombie (el balde, o Winnie the Pooh en el zombie
    puerta): vuela en un arco corto desde el zombie hasta las puntas del imán, achicándose y
    girando. Al llegar avisa al Imán, que pasa a mostrarlo pegado en su sprite.
    """
    DURACION = 0.4

    def __init__(self, start, magnet, objeto="balde"):
        self.start = start
        self.magnet = magnet
        self.objeto = objeto
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
                self.magnet.catch_metal(self.objeto)

    def draw(self, surface):
        u = min(1.0, self.t / self.DURACION)
        e = 1 - (1 - u) ** 2                      # sale rápido y frena al pegarse
        (x0, y0), (x1, y1) = self.start, self.target()
        x = x0 + (x1 - x0) * e
        y = y0 + (y1 - y0) * e - math.sin(math.pi * u) * 40
        if self.objeto == "pooh" and get_frames("pooh", 2):
            # Pooh (dibujo x2) gira y se achica hasta el tamaño que tiene pegado en el imán (x1)
            img = pygame.transform.rotozoom(get_frames("pooh", 2)[0], u * 360, 1.0 - 0.5 * e)
            surface.blit(img, img.get_rect(center=(int(x), int(y))))
            return
        scale = 1.0 + (0.56 - 1.0) * e          # termina del tamaño del balde del sprite
        img = pygame.Surface((48, 40), pygame.SRCALPHA)
        if self.objeto == "armadura":           # la armadura de Chef (Darth Vader): negra
            draw_bucket(img, (24, 18), scale, color=(40, 40, 46), borde=(20, 20, 24))
        else:
            draw_bucket(img, (24, 18), scale)
        img = pygame.transform.rotate(img, u * 360)
        surface.blit(img, img.get_rect(center=(int(x), int(y))))


class ConoCae:
    """El cono de Philip: salta de la cabeza, cae al piso dando vueltas, queda un rato y se desvanece."""
    GRAVEDAD = 700.0
    VIDA_EN_PISO = 0.8

    def __init__(self, pos, piso_y, direccion=-1):
        self.x, self.y = float(pos[0]), float(pos[1])
        self.piso_y = piso_y
        self.vx = 40.0 * direccion
        self.vy = -170.0
        self.giro = 0.0
        self.t_piso = 0.0
        self.alive = True

    def update(self, dt, world):
        if self.y < self.piso_y:
            self.vy += self.GRAVEDAD * dt
            self.x += self.vx * dt
            self.y += self.vy * dt
            self.giro += 540 * dt
            if self.y >= self.piso_y:
                self.y = self.piso_y
                self.giro = 90.0 * (1 if self.vx >= 0 else -1)      # queda tumbado
        else:
            self.t_piso += dt
            if self.t_piso >= self.VIDA_EN_PISO:
                self.alive = False

    def draw(self, surface):
        frames = get_frames("cono_caido", 3)
        if not frames:
            return
        img = frames[0]
        en_aire = self.y < self.piso_y
        if en_aire:
            img = pygame.transform.rotate(img, self.giro)
        else:
            img = pygame.transform.rotate(img, self.giro)
            img = img.copy()
            img.set_alpha(max(0, int(255 * (1 - self.t_piso / self.VIDA_EN_PISO))))
        surface.blit(img, img.get_rect(center=(int(self.x), int(self.y))))


class PoohSeVa:
    """Winnie the Pooh se rompió a tiros: se levanta, titila y se desvanece, y Mickey sigue solo."""
    DURACION = 0.7

    def __init__(self, center):
        self.x, self.y = center
        self.t = 0.0
        self.alive = True

    def update(self, dt, world):
        self.t += dt
        if self.t >= self.DURACION:
            self.alive = False

    def draw(self, surface):
        frames = get_frames("pooh", 2)
        if not frames:
            return
        u = min(1.0, self.t / self.DURACION)
        img = frames[0].copy()
        img.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)        # brilla blanco al romperse
        img.fill((255, 255, 255, int(255 * (1 - u))), special_flags=pygame.BLEND_RGBA_MULT)
        if int(self.t * 20) % 2:                                                  # titila
            img.set_alpha(120)
        surface.blit(img, img.get_rect(center=(int(self.x), int(self.y - 46 * u))))
        for k in range(5):                                                        # nubecita de humo
            a = k * 1.26 + 0.4
            r = 6 + 22 * u
            pygame.draw.circle(surface, (235, 235, 235), (int(self.x + math.cos(a) * r), int(self.y + math.sin(a) * r * 0.7)),
                               max(1, int(7 * (1 - u))))
