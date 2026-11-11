from levels.dialogos import TUTORIAL as T

LEVEL = {
    "id": "tutorial",
    "nombre": "Tutorial",
    "fondo": "fondos/tutorial.png",
    "sol_inicial": 50,
    "intervalo_sol_cielo": 5.0,
    "plantas": ["girasol", "lanzaguisantes"],

    "oleadas": [
        {"t": 3,  "zombies": [("normal", 2)]},
        {"t": 35, "zombies": ["normal"]},
        {"t": 55, "zombies": ["normal"]},
        {"t": 75, "final": True, "zombies": ["normal", "normal"]},
    ],

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
