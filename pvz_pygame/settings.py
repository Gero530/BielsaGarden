"""
Configuración global del juego: pantalla, grilla, colores y estadísticas
de plantas y zombies. Si querés balancear el juego, este es el lugar.
"""

# --- Pantalla ---
SCREEN_W = 1000
SCREEN_H = 600
FPS = 60
TITLE = "Plantas vs Zombies - pygame"

# --- Grilla (5 filas x 9 columnas, como el original) ---
GRID_ROWS = 5
GRID_COLS = 9
CELL_W = 80
CELL_H = 96
GRID_X = 180          # borde izquierdo del césped
GRID_Y = 100          # borde superior del césped (debajo del HUD)

# Si un zombie cruza esta x, llegó a la casa -> derrota
HOUSE_X = GRID_X - 35

# --- Colores ---
COLORS = {
    "bg": (30, 34, 40),
    "hud": (92, 64, 40),
    "hud_borde": (60, 40, 24),
    "cesped_1": (96, 168, 70),
    "cesped_2": (84, 152, 60),
    "casa": (150, 120, 90),
    "calle": (110, 110, 115),
    "texto": (250, 250, 240),
    "texto_osc": (30, 30, 30),
    "sol": (255, 214, 50),
    "sol_borde": (230, 160, 20),
    "carta": (225, 210, 160),
    "carta_borde": (120, 90, 50),
    "carta_sel": (255, 245, 120),
    "deshabilitado": (0, 0, 0, 140),
    "boton": (70, 130, 60),
    "boton_hover": (95, 165, 80),
    "rojo": (200, 50, 50),
    "verde": (60, 200, 80),
    "hover_celda": (255, 255, 255, 60),
    "hover_invalido": (255, 60, 60, 70),
}

# --- Sol (recurso) ---
SOL_VALOR = 25            # cuánto da cada sol
SOL_VIDA = 9.0            # segundos que un sol queda en el piso antes de desaparecer
SOL_VEL_CAIDA = 70        # px/s

# --- Plantas ---
# costo: soles | vida: puntos de vida | recarga: segundos entre usos de la carta
PLANT_DATA = {
    "girasol": {
        "nombre": "Chef",
        "costo": 50,
        "vida": 300,
        "recarga": 7.5,
        "intervalo_sol": 18.0,     # cada cuánto produce un sol
        "primer_sol": 6.0,         # el primero sale antes
    },
    "lanzaguisantes": {
        "nombre": "Lanzaguis.",
        "costo": 100,
        "vida": 300,
        "recarga": 7.5,
        "cadencia": 1.4,           # segundos entre disparos
        "dano": 20,
    },
    "nuez": {
        "nombre": "Nuez",
        "costo": 50,
        "vida": 4000,
        "recarga": 20.0,
    },
    # Kyle: catapulta. Patea a Ike y Ike cae en arco sobre el zombie (mismo daño que el guisante)
    "kyle": {
        "nombre": "Kyle",
        "costo": 100,
        "vida": 300,
        "recarga": 7.5,
        "cadencia": 1.4,           # segundos entre patadas
        "dano": 20,
    },
    # Kenny: como la cereza. Explota al plantarlo y daña un área de 3x3 casillas
    "kenny": {
        "nombre": "Kenny",
        "costo": 150,
        "vida": 300,
        "recarga": 35.0,
        "dano": 1800,
    },
    # Toallin: como la hipnoseta. El zombie que lo muerde pasa a pelear de tu lado
    "toallin": {
        "nombre": "Toallin",
        "costo": 75,
        "vida": 300,
        "recarga": 30.0,
    },
}

# --- Zombies ---
# vida: cuerpo | armadura: cono/cubeta (se absorbe primero)
# velocidad: px/s | dps: daño por segundo al comer
ZOMBIE_DATA = {
    "normal": {"vida": 200, "armadura": 0,    "velocidad": 18, "dps": 100},
    "cono":   {"vida": 200, "armadura": 370,  "velocidad": 18, "dps": 100},
    "cubeta": {"vida": 200, "armadura": 1100, "velocidad": 16, "dps": 100},
}

# --- Proyectiles ---
GUISANTE_VEL = 320
IKE_VEL = 360             # px/s horizontales de Ike en el aire (define cuánto dura el vuelo)
