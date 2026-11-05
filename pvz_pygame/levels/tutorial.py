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

LEVEL = {
    "id": "tutorial",
    "nombre": "Tutorial",
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
        {"texto": ["¡Hola vecino! Te enseño a defender el jardín de los zombies.",
                   "Primero hace falta energía. Cartman la genera cocinando chili.",
                   "Hacé clic en la carta de Chef (arriba) y después en el césped."],
         "espera": ("planta", "girasol"),
         "pista": "Clic en la carta de Chef y después en el césped"},
        {"texto": ["¡Bien! Cada tanto Cartman suelta un dedo brillante: esa es la energía.",
                   "También caen dedos del cielo. Hacé clic en uno para juntarlo."],
         "espera": ("juntar", 1),
         "pista": "Hacé clic en un dedo brillante"},
        {"texto": ["Con la energía se compran defensores. Stan tira bolas de nieve que frenan a los zombies.",
                   "Juntá 100 de energía y poné a Stan en la fila del medio."],
         "espera": ("planta", "lanzaguisantes"),
         "pista": "Juntá 100 de energía y plantá a Stan"},
        {"texto": ["¡Ahí viene un zombie! Stan le va a tirar solo."],
         "oleadas": True,
         "espera": ("muertes", 1),
         "pista": "Seguí juntando energía y poné más Stan"},
        {"texto": ["¡Bien hecho! Si un zombie llega al final del césped, Timmy sale disparado y limpia la fila.",
                   "Pero ojo: cada Timmy sirve una sola vez por nivel. Si un zombie llega a la casa, perdés.",
                   "Para ganar, aguantá todas las oleadas. ¡Vamos que quedan pocos!"]},
    ],
}
