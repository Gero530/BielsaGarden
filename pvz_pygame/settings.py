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
MUSICA_DURACION = 26.28      # segundos que dura la canción (después vuelve a empezar)

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
    # PC Principal: como la Nuez Alta. Muro con muchísima vida; la pértiga no lo puede saltar
    # (se le cae la pértiga y lo muerde) y el bungee no puede caer en su casilla.
    "principal": {
        "costo": 125,
        "vida": 8000,
        "recarga": 30.0,
    },
    # Mr. Hankey: como la Pinchohierba. Va en el piso: los zombies le pasan por encima y les hace
    # "dano" cada "cadencia" s mientras lo pisan. No se lo pueden comer; tractor y gigante lo rompen.
    "hankey": {
        "costo": 100,
        "vida": 300,
        "recarga": 7.5,
        "dano": 20,
        "cadencia": 1.0,
    },
    # Mr. Mackey: como la Seta Helada. Da su charla y congela a todos los zombies de la pantalla
    # durante "congela" s. Se usa una vez.
    "mackey": {
        "costo": 75,
        "vida": 300,
        "recarga": 50.0,
        "congela": 4.0,
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
    # Pértiga: corre, salta la primera planta y después camina normal
    "pertiga":  {"vida": 340, "velocidad": 38, "dps": 100, "velocidad_despues": 18, "salto": 0.9},
    # Escalera: al llegar a la primera planta le apoya la escalera (tarda "apoyar" s) y la pasa por arriba
    "escalera": {"vida": 340, "velocidad": 30, "dps": 100, "velocidad_despues": 18, "apoyar": 1.0},
    # Tractor: tanque lento que hace mucho daño
    "tractor":  {"vida": 1300, "velocidad": 11, "dps": 400},
    # Cae del cielo en una casilla al azar (desde la 3ra columna): "aviso" s de marca antes de caer
    "bungee":   {"vida": 200, "velocidad": 18, "dps": 100, "aviso": 2.5, "caida": 0.5, "col_minima": 2},
    # Bailarín: cada "cada" s frena "baile" s e invoca hasta 4 zombies normales a su alrededor
    "bailarin": {"vida": 340, "velocidad": 18, "dps": 100, "cada": 15.0, "baile": 1.5},
    # Excavador: va bajo tierra (no lo tocan los disparos), sale en la 1ra columna y come hacia la derecha
    "excavador": {"vida": 300, "velocidad": 26, "dps": 100, "velocidad_despues": 18, "salir": 0.7},
    # Gigante: aplasta plantas de un golpe; con menos de "lanza_mini" de vida tira al mini zombie
    "gigante":  {"vida": 3000, "velocidad": 10, "dps": 0, "golpe": 1.0, "lanza_mini": 0.5},
    "mini":     {"vida": 150, "velocidad": 24, "dps": 100, "vuelo": 0.9},
}

# --- Proyectiles ---
GUISANTE_VEL = 320
# Bola de nieve de Stan: el zombie golpeado camina y come más lento durante un rato
NIEVE_RALENTIZA = 0.5     # multiplica velocidad, mordida y animación (0.5 = a la mitad)
NIEVE_DURACION = 4.0      # segundos que dura la ralentización (cada golpe la renueva)
IKE_VEL = 360             # px/s horizontales de Ike en el aire (define cuánto dura el vuelo)
