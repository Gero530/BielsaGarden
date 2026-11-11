"""
Configuración del mapa de niveles.

Hay tres mapas configurados; MAPA elige cuál se usa:
  "pueblo_pixel": el pueblo nevado en pixel art (tools/mapa_pueblo.py lo genera).
  "pueblo":       el dibujo original del pueblo (1920x960, achicado: se ve algo borroso).
  "original":     el mapa anterior con el camino de tierra.
Los dos últimos tienen botones solo para el tutorial y los niveles 1 a 3.
Los tres archivos están en assets/mapa/.

Cada mapa:
  "fondo":   el dibujo (ruta dentro de assets/). Puede tener cualquier tamaño: el juego lo
             agranda o achica para que entre ENTERO en 1000x600 sin deformarlo. Si sobra lugar
             (otra proporción), las franjas se pintan con "relleno".
  "relleno": color de esas franjas (el de los bordes del dibujo, así no se notan).
  "niveles": un botón por nivel, en el MISMO orden que levels/__init__.py (el id tiene que
             coincidir con el "id" de cada nivel). "pos" es el CENTRO del botón en píxeles de
             TU dibujo: abrí el PNG en un editor, poné el mouse donde va el botón y copiá la x, y.

Si el archivo del mapa elegido no existe, se usa "original"; y si tampoco está su PNG, un mapa
simple dibujado por código (scenes/mapa.py, fondo_simple) de ANCHO x ALTO.
"""

MAPAS = {
    # Pueblo nevado en pixel art, hecho por código (tools/mapa_pueblo.py) a partir del dibujo de
    # abajo: 1000x600 (la pantalla entera), se ve tal cual, sin achicar: por eso queda nítido
    "pueblo_pixel": {
        "fondo": "mapa/pueblo_pixel.png",
        "relleno": (234, 240, 247),
        "niveles": [
            {"id": "tutorial", "pos": (808, 348)},     # las casas de arriba (a la derecha del parque)
            {"id": "nivel1",   "pos": (808, 568)},     # el jardín: las casas de abajo a la derecha
            {"id": "nivel2",   "pos": (132, 568)},     # la escuela
            {"id": "nivel3",   "pos": (174, 348)},     # la mansión (en la calle de abajo)
            {"id": "nivel4",   "pos": (138, 54)},      # el lago
            {"id": "nivel5",   "pos": (484, 286)},     # el parque (sobre la fuente)
            {"id": "nivel6",   "pos": (482, 104)},     # el centro comercial (estacionamiento)
            {"id": "nivel7",   "pos": (860, 40)},      # el bosque
        ],
    },
    # Pueblo nevado (1920x960, el dibujo original: se achica y se ve algo borroso): lago, mall, negocios, parque, mansión, escuela y casas
    "pueblo": {
        "fondo": "mapa/pueblo.png",
        "relleno": (234, 240, 247),
        "niveles": [
            {"id": "tutorial", "pos": (247, 905)},     # la escuela (en la calle de enfrente)
            {"id": "nivel1",   "pos": (888, 470)},     # el parque (al lado de la fuente)
            {"id": "nivel2",   "pos": (952, 398)},     # la calle de los negocios
            {"id": "nivel3",   "pos": (1320, 398)},    # frente al restaurante Dragón
        ],
    },
    # Mapa anterior (500x300, se ve x2)
    "original": {
        "fondo": "mapa/fondo_mapa.png",
        "relleno": (0, 0, 0),
        "niveles": [
            {"id": "tutorial", "pos": (62, 236)},
            {"id": "nivel1",   "pos": (148, 160)},
            {"id": "nivel2",   "pos": (262, 214)},
            {"id": "nivel3",   "pos": (420, 150)},
        ],
    },
}
MAPA = "pueblo_pixel"

ESCALA = 2                  # tamaño en pantalla de los botones y la flechita (pixel art x2)
ANCHO, ALTO = 500, 300      # tamaño del mapa simple dibujado por código (si no hay ningún PNG)
