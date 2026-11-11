"""
Nivel 3 — La mansión (~3.9 min). Zombies nuevos: balde y puerta.

Cada oleada dice cuántos zombies de cada tipo vienen; salen mezclados y por filas al azar,
distinto en cada partida. (mín, máx) = la cantidad también se sortea. Formato completo y qué
hace "azar": world/wave_manager.py.
"""

LEVEL = {
    "id": "nivel3",
    "nombre": "Nivel 3 - La mansión",
    "fondo": "fondos/tutorial.png",          # por ahora todos usan el fondo nevado del tutorial
    "sol_inicial": 100,
    "intervalo_sol_cielo": 8.0,     # cada cuánto cae un sol del cielo
    "azar": 0.35,                     # 0 = siempre parecido, 1 = muy distinto en cada partida

    "oleadas": [
        {"t": 18, "zombies": {"normal": 1}},
        {"t": 36, "zombies": {"normal": 1, "cono": 1}},
        {"t": 54, "zombies": {"diario": 1, "normal": 1}},
        {"t": 72, "zombies": {"cubeta": 1}},   # nuevo: balde
        {"t": 90, "zombies": {"normal": 2, "cono": 1}},
        {"t": 106, "zombies": {"puerta": 1}},   # nuevo: puerta
        {"t": 128, "bandera": True, "zombies": {"normal": 4, "cono": 2, "cubeta": 1, "puerta": 1}},   # horda
        {"t": 154, "zombies": {"cono": (1, 2), "diario": 1}},
        {"t": 170, "zombies": {"cubeta": 1, "normal": (1, 2)}},
        {"t": 186, "zombies": {"puerta": 1, "cono": 1, "diario": 1}},
        {"t": 210, "final": True, "zombies": {"normal": (5, 6), "cono": 3, "cubeta": 2, "puerta": 1, "diario": 2}},   # oleada final
    ],

    "avisos": [
        # (segundo, texto, sonido). Los carteles de horda y oleada final salen solos (ver wave_manager).
        (14, "¡Se acercan los zombies!", "sirena"),
    ],
}
