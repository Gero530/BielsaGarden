"""
Nivel 7 — El bosque (~5.5 min). Zombies nuevos: Sr. Garrison y gigante.

Cada oleada dice cuántos zombies de cada tipo vienen; salen mezclados y por filas al azar,
distinto en cada partida. (mín, máx) = la cantidad también se sortea. Formato completo y qué
hace "azar": world/wave_manager.py.
"""

LEVEL = {
    "id": "nivel7",
    "nombre": "Nivel 7 - El bosque",
    "fondo": "fondos/tutorial.png",          # por ahora todos usan el fondo nevado del tutorial
    "sol_inicial": 250,
    "intervalo_sol_cielo": 8.0,     # cada cuánto cae un sol del cielo
    "azar": 1.0,                     # 0 = siempre parecido, 1 = muy distinto en cada partida

    "oleadas": [
        {"t": 20, "zombies": {"normal": 2}},
        {"t": 38, "zombies": {"cono": 1, "normal": 1}},
        {"t": 58, "zombies": {"garrison": 1}},   # nuevo: Sr. Garrison
        {"t": 78, "zombies": {"pertiga": 1, "diario": 1, "normal": 1}},
        {"t": 96, "zombies": {"bungee": 1, "cubeta": 1}},
        {"t": 114, "zombies": {"alien": 1, "cono": 1}},
        {"t": 136, "bandera": True, "zombies": {"normal": (5, 6), "cono": 2, "bailarin": 1, "garrison": 1, "escalera": 1}},   # horda
        {"t": 166, "zombies": {"gigante": 1}},   # nuevo: gigante (con el mini en la espalda)
        {"t": 190, "zombies": {"excavador": 1, "cubeta": 1, "puerta": 1}},
        {"t": 208, "zombies": {"bungee": (1, 2), "pertiga": 1, "cono": 1}},
        {"t": 230, "bandera": True, "zombies": {"normal": (4, 5), "cono": 3, "garrison": 1, "bailarin": 1, "alien": 1, "cubeta": 1}},   # horda
        {"t": 262, "zombies": {"escalera": 1, "diario": 1, "excavador": 1}},
        {"t": 280, "zombies": {"cubeta": (1, 2), "cono": 2}},
        {"t": 306, "final": True, "zombies": {"normal": (8, 10), "cono": 4, "cubeta": 2, "gigante": 1, "garrison": 1, "bailarin": 1, "bungee": 2, "pertiga": 1, "escalera": 1, "alien": 1, "excavador": 1}},   # oleada final
    ],

    "avisos": [
        # (segundo, texto, sonido). Los carteles de horda y oleada final salen solos (ver wave_manager).
        (14, "¡Se acercan los zombies!", "sirena"),
    ],
}
