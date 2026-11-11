"""
Configuración global del juego: pantalla, grilla, colores y estadísticas
de plantas y zombies. Si querés balancear el juego, este es el lugar.
"""

# --- Pantalla ---
SCREEN_W = 1000
SCREEN_H = 600
FPS = 60
TITLE = "Plantas vs Zombies - pygame"

# Música del menú (assets/musica/intro.mp3). La intro está sincronizada con esta canción.
MUSICA_MENU = "musica/intro.mp3"
MUSICA_VOLUMEN = 0.7
# Música de la partida: suenan en este orden, una detrás de otra, y al terminar la última vuelve a la primera.
# (archivo dentro de assets/, volumen de 0.0 a 1.0). Cada tema tiene su volumen porque no vienen igual de fuertes.
MUSICA_PARTIDA = [
    ("musica/uncle_fucka.mp3", 0.7),
    ("musica/kyles_mom.mp3", 0.4),
]
MUSICA_DURACION = 26.28      # segundos que dura la canción (después vuelve a empezar)

# --- Efectos de sonido (assets/sonidos/, ver ui/sonidos.py) ---
SFX_VOLUMEN = 0.8            # volumen general de los efectos (0.0 a 1.0)
SFX_VOLUMENES = {            # ajuste de volumen por efecto (se multiplica por SFX_VOLUMEN)
    "zombie_comiendo": 0.6,
    "explosion": 1.0,
    "hablar": 0.35,          # el sonidito de Bielsa es fuerte y suena muchas veces seguidas
}
SFX_ESPERA = {               # segundos mínimos entre dos reproducciones del mismo efecto
    "zombie_comiendo": 1.5,  # si varios zombies empiezan a comer juntos, suena uno solo
    "impacto": 0.06,
    "hablar": 0.0,           # sin límite: el diálogo ya decide cada cuánto suena
}
# Voces de zombie al azar mientras hay zombies en el campo: (mínimo, máximo) de segundos entre una y otra
BRAINS_INTERVALO = (15.0, 25.0)       # "brains": más o menos cada 20 s
RUIDO_ZOMBIE_INTERVALO = (6.0, 12.0)  # ruido de fondo de los zombies

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

# --- Equipo ---
# Cuántos personajes se pueden llevar a cada nivel (se eligen en la pantalla de equipo)
EQUIPO_MAX = 7

# --- Sol (recurso) ---
SOL_VALOR = 25            # cuánto da cada sol
SOL_VIDA = 9.0            # segundos que un sol queda en el piso antes de desaparecer
SOL_VEL_CAIDA = 70        # px/s

# --- Plantas ---
# costo: soles | vida: puntos de vida | recarga: segundos entre usos de la carta
# (los nombres y descripciones están en data/catalogo.py)
PLANT_DATA = {
    "girasol": {
        "costo": 50,
        "vida": 300,
        "recarga": 7.5,
        "intervalo_sol": 18.0,     # cada cuánto produce un sol
        "primer_sol": 6.0,         # el primero sale antes
    },
    "lanzaguisantes": {
        "costo": 100,
        "vida": 300,
        "recarga": 7.5,
        "cadencia": 1.4,           # segundos entre disparos
        "dano": 20,
    },
    "nuez": {
        "costo": 50,
        "vida": 4000,
        "recarga": 20.0,
    },
    # Kyle: catapulta. Patea a Ike y Ike cae en arco sobre el zombie (mismo daño que el guisante)
    "kyle": {
        "costo": 100,
        "vida": 300,
        "recarga": 7.5,
        "cadencia": 1.4,           # segundos entre patadas
        "dano": 20,
    },
    # Kenny: como la cereza. Explota al plantarlo y daña un área de 3x3 casillas
    "kenny": {
        "costo": 150,
        "vida": 300,
        "recarga": 35.0,
        "dano": 1800,
        "revive": 30.0,            # segundos hasta que revive en la misma casilla (si sigue libre)
    },
    # Toallin: como la hipnoseta. El zombie que lo muerde pasa a pelear de tu lado
    "toallin": {
        "costo": 75,
        "vida": 300,
        "recarga": 30.0,
    },
    # Imán: como el Magnetoseta. Le saca el balde (u otro objeto de metal) al zombie más
    # cercano dentro de su alcance; después se queda con el balde pegado mientras recarga
    "iman": {
        "costo": 100,
        "vida": 300,
        "recarga": 7.5,
        "alcance": 260,            # px desde el centro de su casilla (~3 casillas a la redonda)
        "recarga_iman": 15.0,      # segundos hasta poder volver a atraer
    },
    # Picante: como el Jalapeño pero en CRUZ: quema toda su fila y toda su columna y desaparece.
    # 350 de daño: mata justo al del diario (150 + 200), a la pértiga, la escalera, el bailarín
    # y el excavador; al cono y al balde no.
    "picante": {
        "costo": 125,
        "vida": 300,
        "recarga": 35.0,
        "dano": 350,
    },
    # Aplastadora: como la Calabaza pero reutilizable. Salta a la casilla de enfrente si hay
    # un zombie ahí, mata a TODOS los zombies de esa casilla y se queda ahí.
    "aplastadora": {
        "costo": 150,
        "vida": 300,
        "recarga": 25.0,
        "recarga_salto": 18.0,     # enfriamiento entre un salto y el siguiente
        "preparacion": 0.5,        # cuánto se agacha antes de saltar (s)
        "salto": 0.55,             # cuánto dura el vuelo (s)
    },
}

# --- Zombies ---
# vida: cuerpo | armadura: cono/cubeta (se absorbe primero)
# velocidad: px/s | dps: daño por segundo al comer
# escudo: objeto que lleva adelante (puerta, diario). Se rompe primero.
ZOMBIE_DATA = {
    "normal": {"vida": 200, "armadura": 0,    "velocidad": 18, "dps": 100},
    "cono":   {"vida": 200, "armadura": 370,  "velocidad": 18, "dps": 100},
    "cubeta": {"vida": 200, "armadura": 1100, "velocidad": 16, "dps": 100},
    # Puerta: solo frena lo que viene de frente (Ike cae de arriba y la saltea). El Imán se la saca.
    "puerta":   {"vida": 200, "escudo": 1100, "velocidad": 18, "dps": 100},
    # Diario: el diario absorbe todo; al perderlo se enoja (frenado un momento) y corre
    "diario":   {"vida": 200, "escudo": 150, "velocidad": 18, "dps": 100,
                 "velocidad_enojado": 48, "dps_enojado": 150, "enojo": 1.0},
    # Pértiga (ahora el Murciélago): corre a saltitos, salta la primera planta (se agacha "agacha" s, vuela "salto" s
    # a "altura" px y cae de panza), queda "panzazo" s en el piso, tarda "levantarse" s en pararse y camina lento
    "pertiga":  {"vida": 340, "velocidad": 38, "dps": 100, "velocidad_despues": 18, "salto": 0.9,
                 "agacha": 0.15, "altura": 80, "panzazo": 0.5, "levantarse": 0.4},
    # Escalera: al llegar a la primera planta le apoya la escalera (tarda "apoyar" s) y la pasa por arriba
    "escalera": {"vida": 340, "velocidad": 30, "dps": 100, "velocidad_despues": 18, "apoyar": 1.0},
    # Sr. Garrison (en su rueda): tanque lento que hace mucho daño
    "garrison": {"vida": 1300, "velocidad": 11, "dps": 400},
    # Cae del cielo en una casilla al azar (desde la 3ra columna): "aviso" s de marca antes de caer
    "bungee":   {"vida": 200, "velocidad": 18, "dps": 100, "aviso": 2.5, "caida": 0.5, "col_minima": 2},
    # Cangrejo bailarín (rojo): cada "cada" s frena "baile" s e invoca hasta 4 cangrejos marrones a su alrededor
    "bailarin": {"vida": 340, "velocidad": 18, "dps": 100, "cada": 15.0, "baile": 1.5},
    # Cangrejo invocado (marrón): lo invoca el cangrejo bailarín; mismos números que el zombie normal
    "cangrejo_invocado": {"vida": 200, "armadura": 0, "velocidad": 18, "dps": 100},
    # Excavador: va bajo tierra (no lo tocan los disparos), sale en la 1ra columna y come hacia la derecha
    "excavador": {"vida": 300, "velocidad": 26, "dps": 100, "velocidad_despues": 18, "salir": 0.7},
    # Gigante: aplasta plantas de un golpe; con menos de "lanza_mini" de vida tira al mini zombie
    "gigante":  {"vida": 3000, "velocidad": 10, "dps": 0, "golpe": 1.0, "lanza_mini": 0.5},
    "mini":     {"vida": 150, "velocidad": 24, "dps": 100, "vuelo": 0.9},
    # Alien (de Santi): entra ALIEN_CASILLAS casillas, aprieta el botón y apaga a los Chef hasta que muere.
    # Si en el camino una planta le corta el paso, se la come (dps).
    "alien":    {"vida": 300, "armadura": 0, "velocidad": 22, "dps": 100},
}
ALIEN_CASILLAS = 2     # casillas que entra antes de frenar
CHEF_REACTIVA = 3.0    # segundos hasta el primer sol cuando muere el alien


# --- Proyectiles ---
GUISANTE_VEL = 320
# Bola de nieve de Stan: el zombie golpeado camina y come más lento durante un rato
NIEVE_RALENTIZA = 0.5     # multiplica velocidad, mordida y animación (0.5 = a la mitad)
NIEVE_DURACION = 4.0      # segundos que dura la ralentización (cada golpe la renueva)
IKE_VEL = 360             # px/s horizontales de Ike en el aire (define cuánto dura el vuelo)
