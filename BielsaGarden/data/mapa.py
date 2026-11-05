"""
Configuración del mapa de niveles.

FONDO: tu dibujo del mapa (ruta dentro de assets/). Dibujalo en LibreSprite a ANCHO x ALTO
píxeles (250x150, igual que el jardín). El juego lo agranda x ESCALA (4) sin suavizado y
queda en 1000x600. Si el archivo no existe, se usa un mapa simple dibujado por código.

NIVELES: un botón por nivel, en el MISMO orden que levels/__init__.py (el id tiene que
coincidir con el "id" de cada nivel). "pos" es el CENTRO del botón en coordenadas de TU
dibujo (0..249, 0..149): abrí el PNG en LibreSprite, poné el mouse donde va el botón y
copiá la x, y que muestra abajo.
"""

FONDO = "mapa/fondo_mapa.png"
ANCHO, ALTO = 250, 150
ESCALA = 4

NIVELES = [
    {"id": "tutorial", "pos": (38, 112)},
    {"id": "nivel1",   "pos": (92, 84)},
    {"id": "nivel2",   "pos": (152, 104)},
    {"id": "nivel3",   "pos": (208, 66)},
]
