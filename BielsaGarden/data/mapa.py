"""
Configuración del mapa de niveles.

FONDO: tu dibujo del mapa (ruta dentro de assets/). Dibujalo en LibreSprite a ANCHO x ALTO
píxeles (500x300). El juego lo agranda x ESCALA (2) sin suavizado y
queda en 1000x600. Si el archivo no existe, se usa un mapa simple dibujado por código.

NIVELES: un botón por nivel, en el MISMO orden que levels/__init__.py (el id tiene que
coincidir con el "id" de cada nivel). "pos" es el CENTRO del botón en coordenadas de TU
dibujo (0..499, 0..299): abrí el PNG en LibreSprite, poné el mouse donde va el botón y
copiá la x, y que muestra abajo.
"""

FONDO = "mapa/fondo_mapa.png"
ANCHO, ALTO = 500, 300
ESCALA = 2

NIVELES = [
    {"id": "tutorial", "pos": (62, 236)},
    {"id": "nivel1",   "pos": (148, 160)},
    {"id": "nivel2",   "pos": (262, 214)},
    {"id": "nivel3",   "pos": (420, 150)},
]
