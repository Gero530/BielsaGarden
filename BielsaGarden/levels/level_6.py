"""
Nivel 6 — El centro comercial (~5.2 min). Zombies nuevos: bungee y alien.

Cada oleada dice cuántos zombies de cada tipo vienen; salen mezclados y por filas al azar,
distinto en cada partida. (mín, máx) = la cantidad también se sortea. Formato completo y qué
hace "azar": world/wave_manager.py.
"""

LEVEL = {
    "id": "nivel6",
    "nombre": "Nivel 6 - El centro comercial",
    "fondo": "fondos/tutorial.png",          # por ahora todos usan el fondo nevado del tutorial
    "sol_inicial": 150,
    "intervalo_sol_cielo": 8.0,     # cada cuánto cae un sol del cielo
    "azar": 0.8,                     # 0 = siempre parecido, 1 = muy distinto en cada partida

    "oleadas": [
        {"t": 18, "zombies": {"normal": 2}},
        {"t": 36, "zombies": {"cono": 1, "diario": 1}},
        {"t": 56, "zombies": {"bungee": 1}},   # nuevo: bungee
        {"t": 74, "zombies": {"normal": 2, "pertiga": 1}},
        {"t": 92, "zombies": {"cubeta": 1, "escalera": 1}},
        {"t": 108, "zombies": {"alien": 1}},   # nuevo: alien (apaga a los Chef)
        {"t": 130, "bandera": True, "zombies": {"normal": (5, 6), "cono": 2, "bungee": 1, "bailarin": 1, "puerta": 1}},   # horda
        {"t": 158, "zombies": {"alien": 1, "excavador": 1, "cono": 1}},
        {"t": 176, "zombies": {"bungee": (1, 2), "cubeta": 1}},
        {"t": 194, "zombies": {"pertiga": 1, "diario": 1, "normal": (1, 2)}},
        {"t": 218, "bandera": True, "zombies": {"normal": 4, "cono": 3, "cubeta": 1, "bungee": 1, "alien": 1, "escalera": 1, "bailarin": 1}},   # horda
        {"t": 248, "zombies": {"excavador": 1, "puerta": 1, "bungee": 1}},
        {"t": 266, "zombies": {"cono": (2, 3), "pertiga": 1}},
        {"t": 290, "final": True, "zombies": {"normal": (7, 9), "cono": 3, "cubeta": 2, "bungee": 2, "alien": 1, "bailarin": 1, "escalera": 1, "excavador": 1, "puerta": 1, "diario": 1}},   # oleada final
    ],

    "avisos": [
        # (segundo, texto, sonido). Los carteles de horda y oleada final salen solos (ver wave_manager).
        (14, "¡Se acercan los zombies!", "sirena"),
    ],
}
