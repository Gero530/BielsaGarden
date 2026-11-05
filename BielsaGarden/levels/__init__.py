"""
Registro de niveles, en el orden del mapa (el primero arranca desbloqueado).
Para sumar uno: creá levels/level_4.py con su LEVEL (con un "id" nuevo), agregalo acá
y sumá su botón en data/mapa.py.
"""
from levels.tutorial import LEVEL as TUTORIAL
from levels.level_1 import LEVEL as LEVEL_1
from levels.level_2 import LEVEL as LEVEL_2
from levels.level_3 import LEVEL as LEVEL_3

LEVELS = [TUTORIAL, LEVEL_1, LEVEL_2, LEVEL_3]
