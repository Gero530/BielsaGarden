"""
Registro de niveles, en el orden del mapa (el primero arranca desbloqueado).

  Tutorial  las casas de arriba   normal
  Nivel 1   el jardín             + cono
  Nivel 2   la escuela            + diario
  Nivel 3   la mansión            + balde, puerta
  Nivel 4   el lago               + pértiga, escalera
  Nivel 5   el parque             + bailarín, excavador
  Nivel 6   el centro comercial   + bungee, alien
  Nivel 7   el bosque             + Sr. Garrison, gigante

Para sumar uno: creá levels/level_8.py con su LEVEL (con un "id" nuevo), agregalo acá
y sumá su botón en data/mapa.py.
"""
from levels.tutorial import LEVEL as TUTORIAL
from levels.level_1 import LEVEL as LEVEL_1
from levels.level_2 import LEVEL as LEVEL_2
from levels.level_3 import LEVEL as LEVEL_3
from levels.level_4 import LEVEL as LEVEL_4
from levels.level_5 import LEVEL as LEVEL_5
from levels.level_6 import LEVEL as LEVEL_6
from levels.level_7 import LEVEL as LEVEL_7

LEVELS = [TUTORIAL, LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4, LEVEL_5, LEVEL_6, LEVEL_7]
