"""
Nivel 1 — corto (~3 minutos) y pasable con las plantas disponibles.

Cada oleada es (segundo, tipo_de_zombie, fila).
fila = None -> fila al azar.
La lista de avisos muestra un cartel en pantalla en ese segundo.
"""

LEVEL = {
    "nombre": "Nivel 1 - El jardín",
    "sol_inicial": 150,
    "intervalo_sol_cielo": 8.0,     # cada cuánto cae un sol del cielo
    "plantas": ["girasol", "lanzaguisantes", "nuez", "kyle", "kenny", "toallin"],

    "oleadas": [
        (20,  "normal", 2),          # el primero va por el medio
        (36,  "normal", None),
        (50,  "normal", None),
        (57,  "normal", None),
        (70,  "cono",   None),
        (83,  "normal", None),
        (89,  "cono",   None),
        (101, "normal", None),
        (105, "normal", None),
        (116, "cubeta", None),
        # Oleada final
        (131, "normal", None),
        (132, "cono",   None),
        (134, "normal", None),
        (136, "cono",   None),
        (138, "normal", None),
        (140, "cubeta", None),
    ],

    "avisos": [
        (17,  "¡Se acercan los zombies!"),
        (128, "¡OLEADA FINAL!"),
    ],
}
