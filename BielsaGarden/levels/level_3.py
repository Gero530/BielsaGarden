"""
Nivel 3 — El centro (~5 min).
Presenta de a uno: bailarín -> bungee -> tractor -> gigante.
"""

LEVEL = {
    "id": "nivel3",
    "nombre": "Nivel 3 - El centro",
    "fondo": "fondos/nivel3.png",          # lo genera tools/fondos.py a partir de fondos/jardin.png
    "sol_inicial": 250,
    "intervalo_sol_cielo": 8.0,

    "oleadas": [
        {"t": 20,  "zombies": ["normal"]},
        {"t": 38,  "zombies": ["normal", "cono"]},
        {"t": 58,  "zombies": [("bailarin", 2)]},                    # nuevo: bailarín
        {"t": 80,  "zombies": ["pertiga", "normal"]},
        {"t": 96,  "zombies": ["bungee"]},                           # nuevo: bungee
        {"t": 112, "zombies": ["cono", "diario", "alien"]},
        {"t": 132, "bandera": True, "zombies": ["normal", "normal", "cono", "bailarin", "pertiga", "normal", "puerta", "bungee"]},
        {"t": 160, "zombies": [("tractor", 2), "normal"]},            # nuevo: tractor
        {"t": 176, "zombies": ["bungee", "escalera", "cono"]},
        {"t": 192, "zombies": ["cubeta", "diario", "excavador"]},
        {"t": 212, "zombies": ["gigante"]},                          # nuevo: gigante
        {"t": 236, "bandera": True, "zombies": [
            "normal", "cono", "normal", "tractor", "cono", "bailarin", "bungee", "normal", "escalera"]},
        {"t": 266, "zombies": ["excavador", "cubeta", "puerta", "alien"]},
        {"t": 294, "final": True, "zombies": [
            "normal", "cono", "gigante", "normal", "bailarin", "cono", "tractor", "pertiga", "bungee",
            "diario", "normal", "cubeta", "escalera", "bungee", "cono", "normal"]},
    ],
}
