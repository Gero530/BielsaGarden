"""
Tutorial guiado. Mismo formato que los niveles, más la lista "tutorial": pasos que se
muestran en orden. Cada paso:
    "texto":   mensajes del diálogo (uno por cuadro)
    "espera":  qué tiene que hacer el jugador para pasar al siguiente paso:
               ("planta", clave)  -> tener esa planta en el césped
               ("juntar", n)      -> haber juntado n unidades de energía con clic
               ("muertes", n)     -> haber eliminado n zombies
               None (o sin poner) -> sigue apenas se cierra el diálogo
    "pista":   texto chico que queda abajo mientras se espera
    "oleadas": True -> desde este paso empiezan a venir los zombies (el reloj de las
               oleadas arranca en ese momento)
"""

from levels.dialogos import TUTORIAL as T

LEVEL = {
    "id": "tutorial",
    "nombre": "Tutorial",
    "fondo": "fondos/tutorial.png",          # lo genera tools/fondos.py a partir de fondos/jardin.png
    "sol_inicial": 50,
    "intervalo_sol_cielo": 5.0,
    "plantas": ["girasol", "lanzaguisantes"],

    "oleadas": [
        {"t": 3,  "zombies": [("normal", 2)]},
        {"t": 35, "zombies": ["normal"]},
        {"t": 55, "zombies": ["normal"]},
        {"t": 75, "final": True, "zombies": ["normal", "normal"]},
    ],

    # Una frase de Bielsa por paso (levels/dialogos.py, TUTORIAL). El paso no termina hasta que
    # el jugador hace lo que dice "espera".
    "tutorial": [
        {"texto": [T[0]]},
        {"texto": [T[1]]},
        {"texto": [T[2]], "espera": ("planta", "girasol"),
         "pista": "Clic en la carta de Cartman y después en el césped"},
        {"texto": [T[3]], "espera": ("juntar", 1),
         "pista": "Hacé clic en un dedo brillante para juntarlo"},
        {"texto": [T[4]]},
        {"texto": [T[5]]},
        {"texto": [T[6]], "espera": ("planta", "lanzaguisantes"),
         "pista": "Juntá 100 y plantá a Stan en la fila del zombie"},
        {"texto": [T[7]]},
        {"texto": [T[8]], "oleadas": True, "espera": ("muertes", 1),
         "pista": "Aguantá: Stan le dispara solo al zombie"},
        {"texto": [T[9]]},
        {"texto": [T[10]]},
        {"texto": [T[11]]},
    ],
}
