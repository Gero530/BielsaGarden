"""
Nivel 2 — La calle (~4,5 min).
Presenta de a uno: diario -> pértiga -> escalera -> excavador.
"""

LEVEL = {
    "id": "nivel2",
    "nombre": "Nivel 2 - La calle",
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
        {"t": 124, "bandera": True, "zombies": ["normal", "normal", "cono", "pertiga", "normal", "diario"]},
        {"t": 140, "zombies": ["excavador"]},                        # nuevo: excavador (tramo tranquilo)
        {"t": 150, "zombies": ["escalera", "normal"]},               # nuevo: escalera
        {"t": 166, "zombies": ["cubeta", "pertiga"]},
        {"t": 182, "zombies": ["normal"]},
        {"t": 198, "zombies": ["escalera", "cono", "diario"]},
        {"t": 222, "bandera": True, "zombies": ["normal", "cono", "normal", "cubeta", "escalera", "cono", "puerta", "normal"]},
        {"t": 250, "zombies": ["excavador", "pertiga", "cono"]},
        {"t": 278, "final": True, "zombies": [
            "normal", "cono", "pertiga", "normal", "diario", "cubeta", "escalera", "cono",
            "normal", "excavador", "pertiga", "cono", "diario", "cubeta", "normal"]},
    ],
}
