"""
Grilla del jardín: convierte posiciones del mouse en celdas, guarda qué
planta hay en cada celda y dibuja el césped.
"""
import os
import pygame
from settings import GRID_ROWS, GRID_COLS, CELL_W, CELL_H, GRID_X, GRID_Y, COLORS, SCREEN_W, SCREEN_H
from ui.sprites import ASSETS_DIR

# Imagen de fondo del jardín. Se escala para llenar la pantalla (250x150 -> x4 = 1000x600).
# El césped tiene que coincidir con la grilla: en la imagen de 250x150 empieza en (45, 25)
# y cada celda mide 20x24. Si el archivo no existe, se dibuja el fondo con colores planos.
FONDO = "fondos/jardin.png"

_fondo_cache = None


def load_background():
    """Carga el fondo una sola vez (se reutiliza al reintentar el nivel)."""
    global _fondo_cache
    if _fondo_cache is None:
        path = os.path.join(ASSETS_DIR, FONDO)
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            # scale (vecino más cercano) y no smoothscale, para que el pixel art quede nítido
            _fondo_cache = pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
        else:
            print(f"[fondo] No se encontró {path}; se usa el fondo con colores planos.")
            _fondo_cache = False
    return _fondo_cache or None


class Grid:
    def __init__(self):
        self.rows = GRID_ROWS
        self.cols = GRID_COLS
        self.rect = pygame.Rect(GRID_X, GRID_Y, GRID_COLS * CELL_W, GRID_ROWS * CELL_H)
        self.cells = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    # --- Conversión de coordenadas ---
    def cell_at(self, pos):
        """Devuelve (fila, col) para una posición de pantalla, o None."""
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

    # --- Plantas ---
    def get(self, row, col):
        return self.cells[row][col]

    def is_free(self, row, col):
        return self.cells[row][col] is None

    def place(self, plant):
        self.cells[plant.row][plant.col] = plant

    def remove(self, row, col):
        self.cells[row][col] = None

    def plants(self):
        for row in self.cells:
            for p in row:
                if p is not None:
                    yield p

    def cleanup(self):
        """Saca de la grilla las plantas muertas."""
        for r in range(self.rows):
            for c in range(self.cols):
                p = self.cells[r][c]
                if p is not None and not p.alive:
                    self.cells[r][c] = None

    # --- Dibujo ---
    def draw(self, surface):
        fondo = load_background()
        if fondo is not None:
            surface.blit(fondo, (0, 0))
            return

        # Sin imagen: casa (izquierda), calle (derecha) y césped a cuadros
        pygame.draw.rect(surface, COLORS["casa"], (0, GRID_Y, GRID_X, SCREEN_H - GRID_Y))
        pygame.draw.rect(surface, COLORS["calle"], (self.rect.right, GRID_Y, SCREEN_W - self.rect.right, SCREEN_H - GRID_Y))
        for r in range(self.rows):
            for c in range(self.cols):
                color = COLORS["cesped_1"] if (r + c) % 2 == 0 else COLORS["cesped_2"]
                pygame.draw.rect(surface, color, self.cell_rect(r, c))
        # Puerta de la casa
        pygame.draw.rect(surface, (100, 70, 45), (30, GRID_Y + 2 * CELL_H + 10, 40, CELL_H - 10))

    def draw_hover(self, surface, pos, valid):
        cell = self.cell_at(pos)
        if cell is None:
            return
        rect = self.cell_rect(*cell)
        overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
        overlay.fill(COLORS["hover_celda"] if valid(cell) else COLORS["hover_invalido"])
        surface.blit(overlay, rect.topleft)
