"""
Nivel 2 — La calle (~4,5 min).
Presenta de a uno: diario -> pértiga -> alien -> excavador -> escalera.
"""

LEVEL = {
    "id": "nivel2",
    "nombre": "Nivel 2 - La calle",
    "fondo": "fondos/nivel2.png",          # lo genera tools/fondos.py a partir de fondos/jardin.png
    "sol_inicial": 100,
    "intervalo_sol_cielo": 8.0,

    "oleadas": [
        {"t": 18,  "zombies": ["normal"]},
        {"t": 38,  "zombies": ["normal"]},
        {"t": 48,  "zombies": ["cono"]},
        {"t": 62,  "zombies": [("diario", 2)]},                      # nuevo: diario
        {"t": 76,  "zombies": ["normal", "normal"]},
        {"t": 90,  "zombies": ["pertiga"]},                          # nuevo: pértiga
        {"t": 104, "zombies": ["cono", "diario"]},
        {"t": 112, "zombies": ["alien"]},                           # nuevo: alien (apaga a los Chef)
        {"t": 124, "bandera": True, "zombies": ["normal", "normal", "cono", "pertiga", "normal", "diario"]},
        {"t": 140, "zombies": ["excavador"]},                        # nuevo: excavador (tramo tranquilo)
        {"t": 150, "zombies": ["escalera", "normal"]},               # nuevo: escalera
        {"t": 166, "zombies": ["cubeta", "pertiga"]},
        {"t": 182, "zombies": ["normal"]},
        {"t": 198, "zombies": ["escalera", "cono", "diario"]},
        {"t": 222, "bandera": True, "zombies": ["normal", "cono", "normal", "cubeta", "escalera", "cono", "puerta", "normal", "alien"]},
        {"t": 250, "zombies": ["excavador", "pertiga", "cono"]},
        {"t": 278, "final": True, "zombies": [
            "normal", "cono", "pertiga", "normal", "diario", "cubeta", "escalera", "cono",
            "normal", "excavador", "pertiga", "cono", "diario", "cubeta", "normal"]},
    ],
}
