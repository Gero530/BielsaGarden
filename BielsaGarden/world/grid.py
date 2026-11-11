import os
import pygame
from settings import GRID_ROWS, GRID_COLS, CELL_W, CELL_H, GRID_X, GRID_Y, COLORS, SCREEN_W, SCREEN_H
from ui.sprites import ASSETS_DIR

FONDO = "fondos/jardin.png"

_fondo_cache = {}


def load_background(fondo=FONDO):
    if fondo not in _fondo_cache:
        path = os.path.join(ASSETS_DIR, fondo)
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            _fondo_cache[fondo] = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
        else:
            print(f"[fondo] No se encontró {path}; se usa el fondo con colores planos.")
            _fondo_cache[fondo] = False
    return _fondo_cache[fondo] or None


class Grid:
    def __init__(self, fondo=FONDO):
        self.fondo = fondo
        self.rows = GRID_ROWS
        self.cols = GRID_COLS
        self.rect = pygame.Rect(GRID_X, GRID_Y, GRID_COLS * CELL_W, GRID_ROWS * CELL_H)
        self.cells = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.ladders = set()

    def cell_at(self, pos):
        if not self.rect.collidepoint(pos):
            return None
        col = (pos[0] - GRID_X) // CELL_W
        row = (pos[1] - GRID_Y) // CELL_H
        return int(row), int(col)

    def col_at_x(self, x):
        if x < GRID_X or x >= self.rect.right:
            return None
        return int((x - GRID_X) // CELL_W)

    def cell_rect(self, row, col):
        return pygame.Rect(GRID_X + col * CELL_W, GRID_Y + row * CELL_H, CELL_W, CELL_H)

    def row_center_y(self, row):
        return GRID_Y + row * CELL_H + CELL_H // 2

    def get(self, row, col):
        return self.cells[row][col]

    def is_free(self, row, col):
        return self.cells[row][col] is None

    def place(self, plant):
        self.cells[plant.row][plant.col] = plant

    def remove(self, row, col):
        self.cells[row][col] = None
        self.ladders.discard((row, col))

    def plants(self):
        for row in self.cells:
            for p in row:
                if p is not None:
                    yield p

    def cleanup(self):
        for r in range(self.rows):
            for c in range(self.cols):
                p = self.cells[r][c]
                if p is not None and not p.alive:
                    self.remove(r, c)

    def draw(self, surface):
        fondo = load_background(self.fondo)
        if fondo is not None:
            surface.blit(fondo, (0, 0))
            return

        pygame.draw.rect(surface, COLORS["casa"], (0, GRID_Y, GRID_X, SCREEN_H - GRID_Y))
        pygame.draw.rect(surface, COLORS["calle"], (self.rect.right, GRID_Y, SCREEN_W - self.rect.right, SCREEN_H - GRID_Y))
        for r in range(self.rows):
            for c in range(self.cols):
                color = COLORS["cesped_1"] if (r + c) % 2 == 0 else COLORS["cesped_2"]
                pygame.draw.rect(surface, color, self.cell_rect(r, c))
        pygame.draw.rect(surface, (100, 70, 45), (30, GRID_Y + 2 * CELL_H + 10, 40, CELL_H - 10))

    def draw_hover(self, surface, pos, valid):
        cell = self.cell_at(pos)
        if cell is None:
            return
        rect = self.cell_rect(*cell)
        overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
        overlay.fill(COLORS["hover_celda"] if valid(cell) else COLORS["hover_invalido"])
        surface.blit(overlay, rect.topleft)
