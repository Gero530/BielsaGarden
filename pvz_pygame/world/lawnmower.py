"""
Cortacéspedes: última defensa de cada fila. Se activa cuando un zombie
llega al borde del césped, barre la fila entera y se consume.
"""
import pygame
from settings import GRID_X, SCREEN_W

VELOCIDAD = 420


class LawnMower:
    def __init__(self, row, grid):
        self.row = row
        self.x = float(GRID_X - 32)
        self.y = grid.row_center_y(row) + 18
        self.active = False      # en movimiento
        self.used = False        # ya se gastó

    def update(self, dt, world):
        if not self.active and not self.used:
            for z in world.zombies:
                if z.row == self.row and z.alive and z.x < GRID_X + 5:
                    self.active = True
                    break
        if self.active:
            self.x += VELOCIDAD * dt
            for z in world.zombies:
                if z.row == self.row and z.alive and abs(z.x - self.x) < 30:
                    z.alive = False
            if self.x > SCREEN_W + 40:
                self.active = False
                self.used = True

    def draw(self, surface):
        if self.used:
            return
        x, y = int(self.x), int(self.y)
        pygame.draw.rect(surface, (200, 40, 40), (x - 20, y - 14, 40, 20), border_radius=4)
        pygame.draw.line(surface, (60, 60, 60), (x - 18, y - 12), (x - 30, y - 34), 3)
        pygame.draw.circle(surface, (30, 30, 30), (x - 12, y + 8), 7)
        pygame.draw.circle(surface, (30, 30, 30), (x + 12, y + 8), 7)
