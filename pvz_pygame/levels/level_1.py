"""
Nivel 1 — El jardín (~3,5 min). Presenta al zombie con puerta.

Los personajes se eligen antes de jugar (pantalla de equipo, entre todos). Si querés
limitar los que se pueden elegir en un nivel, agregá "plantas": ["girasol", ...].

Formato de oleadas: ver world/wave_manager.py. Resumen:
    {"t": segundo, "zombies": [tipo, (tipo, fila), ...], "bandera": True, "final": True, "cada": s}
"""

LEVEL = {
    "id": "nivel1",
    "nombre": "Nivel 1 - El jardín",
    "sol_inicial": 100,
    "intervalo_sol_cielo": 8.0,     # cada cuánto cae un sol del cielo

    "oleadas": [
        # Arranque: de a uno, para armar la economía con Cartman
        {"t": 18,  "zombies": [("normal", 2)]},
        {"t": 38,  "zombies": ["normal"]},
        {"t": 54,  "zombies": ["normal", "normal"]},
        {"t": 68,  "zombies": ["cono"]},
        {"t": 82,  "zombies": ["normal", "cono"]},
        {"t": 98,  "zombies": ["puerta"]},                           # nuevo: puerta
        # Horda intermedia
        {"t": 120, "bandera": True, "zombies": ["normal", "normal", "cono", "normal", "cono", "puerta", "normal", "cubeta"]},
        # Se pone más pesado
        {"t": 146, "zombies": ["cono", "normal", "cono"]},
        {"t": 160, "zombies": ["cubeta", "normal", "normal"]},
        {"t": 175, "zombies": ["puerta", "cono"]},
        {"t": 188, "zombies": ["cono", "normal"]},
        # Oleada final
        {"t": 208, "final": True, "zombies": [
            "normal", "cono", "normal", "puerta", "cono", "cubeta",
            "normal", "cono", "normal", "puerta", "cubeta", "normal"]},
    ],
}
