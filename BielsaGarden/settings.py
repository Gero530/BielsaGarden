SCREEN_W = 1000
SCREEN_H = 600
FPS = 60
TITLE = "Plantas vs Zombies - pygame"

MUSICA_MENU = "musica/intro.mp3"
MUSICA_VOLUMEN = 0.7
MUSICA_PARTIDA = [
    ("musica/uncle_fucka.mp3", 0.7),
    ("musica/kyles_mom.mp3", 0.4),
]
MUSICA_VICTORIA = ("musica/victoria.wav", 0.55)
MUSICA_FINAL = ("musica/victoria.mp3", 0.7)
MUSICA_DERROTA = ("musica/derrota.wav", 0.7)
MUSICA_DURACION = 26.28

SFX_VOLUMEN = 0.8
SFX_VOLUMENES = {
    "zombie_comiendo": 0.6,
    "explosion": 1.0,
    "hablar": 0.35,
    "crab_people": 0.45,
}
SFX_ESPERA = {
    "zombie_comiendo": 1.5,
    "impacto": 0.06,
    "hablar": 0.0,
}
BRAINS_INTERVALO = (15.0, 25.0)
RUIDO_ZOMBIE_INTERVALO = (6.0, 12.0)

GRID_ROWS = 5
GRID_COLS = 9
CELL_W = 80
CELL_H = 96
GRID_X = 180
GRID_Y = 100

HOUSE_X = GRID_X - 35

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

EQUIPO_MAX = 7

SOL_VALOR = 25
SOL_VIDA = 9.0
SOL_VEL_CAIDA = 70

PLANT_DATA = {
    "girasol": {
        "costo": 50,
        "vida": 300,
        "recarga": 7.5,
        "intervalo_sol": 18.0,
        "primer_sol": 6.0,
    },
    "lanzaguisantes": {
        "costo": 100,
        "vida": 300,
        "recarga": 7.5,
        "cadencia": 1.4,
        "dano": 20,
    },
    "nuez": {
        "costo": 50,
        "vida": 4000,
        "recarga": 20.0,
    },
    "kyle": {
        "costo": 100,
        "vida": 300,
        "recarga": 7.5,
        "cadencia": 1.4,
        "dano": 20,
    },
    "kenny": {
        "costo": 150,
        "vida": 300,
        "recarga": 35.0,
        "dano": 1800,
        "revive": 30.0,
    },
    "toallin": {
        "costo": 75,
        "vida": 300,
        "recarga": 30.0,
    },
    "iman": {
        "costo": 100,
        "vida": 300,
        "recarga": 7.5,
        "alcance": 260,
        "recarga_iman": 15.0,
    },
    "picante": {
        "costo": 125,
        "vida": 300,
        "recarga": 35.0,
        "dano": 350,
    },
    "aplastadora": {
        "costo": 150,
        "vida": 300,
        "recarga": 25.0,
        "recarga_salto": 18.0,
        "preparacion": 0.5,
        "salto": 0.55,
    },
}

ZOMBIE_DATA = {
    "normal": {"vida": 200, "armadura": 0,    "velocidad": 18, "dps": 100},
    "cono":   {"vida": 200, "armadura": 370,  "velocidad": 18, "dps": 100},
    "cubeta": {"vida": 200, "armadura": 1100, "velocidad": 16, "dps": 100},
    "puerta":   {"vida": 200, "escudo": 1100, "velocidad": 18, "dps": 100},
    "diario":   {"vida": 200, "escudo": 150, "velocidad": 18, "dps": 100,
                 "velocidad_enojado": 48, "dps_enojado": 150, "enojo": 1.0},
    "pertiga":  {"vida": 340, "velocidad": 38, "dps": 100, "velocidad_despues": 18, "salto": 0.9,
                 "agacha": 0.15, "altura": 80, "panzazo": 0.5, "levantarse": 0.4},
    "escalera": {"vida": 340, "velocidad": 30, "dps": 100, "velocidad_despues": 18, "apoyar": 1.0},
    "garrison": {"vida": 1300, "velocidad": 11, "dps": 400},
    "bungee":   {"vida": 200, "velocidad": 18, "dps": 100, "aviso": 2.5, "caida": 0.5, "col_minima": 2},
    "bailarin": {"vida": 340, "velocidad": 18, "dps": 100, "cada": 15.0, "baile": 1.5},
    "cangrejo_invocado": {"vida": 200, "armadura": 0, "velocidad": 18, "dps": 100},
    "excavador": {"vida": 300, "velocidad": 26, "dps": 100, "velocidad_despues": 18, "salir": 0.7},
    "gigante":  {"vida": 3000, "velocidad": 10, "dps": 0, "golpe": 1.0, "lanza_mini": 0.5},
    "mini":     {"vida": 150, "velocidad": 24, "dps": 100, "vuelo": 0.9},
    "alien":    {"vida": 300, "armadura": 0, "velocidad": 22, "dps": 100},
}
ALIEN_CASILLAS = 2
CHEF_REACTIVA = 3.0


GUISANTE_VEL = 320
NIEVE_RALENTIZA = 0.5
NIEVE_DURACION = 4.0
IKE_VEL = 360
