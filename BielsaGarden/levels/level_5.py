"""
Nivel 5 — El parque (~5 min). Zombies nuevos: bailarín y excavador.

Cada oleada dice cuántos zombies de cada tipo vienen; salen mezclados y por filas al azar,
distinto en cada partida. (mín, máx) = la cantidad también se sortea. Formato completo y qué
hace "azar": world/wave_manager.py.
"""

LEVEL = {
    "id": "nivel5",
    "nombre": "Nivel 5 - El parque",
    "fondo": "fondos/tutorial.png",          # por ahora todos usan el fondo nevado del tutorial
    "sol_inicial": 150,
    "intervalo_sol_cielo": 8.0,     # cada cuánto cae un sol del cielo
    "azar": 0.65,                     # 0 = siempre parecido, 1 = muy distinto en cada partida

    "oleadas": [
        {"t": 18, "zombies": {"normal": 2}},
        {"t": 36, "zombies": {"cono": 1, "normal": 1}},
        {"t": 56, "zombies": {"bailarin": 1}},   # nuevo: bailarín
        {"t": 76, "zombies": {"pertiga": 1, "diario": 1}},
        {"t": 94, "zombies": {"cubeta": 1, "normal": (1, 2)}},
        {"t": 110, "zombies": {"excavador": 1}},   # nuevo: excavador
        {"t": 132, "bandera": True, "zombies": {"normal": (4, 6), "cono": 2, "bailarin": 1, "pertiga": 1, "puerta": 1}},   # horda
        {"t": 160, "zombies": {"excavador": 1, "cono": 1, "escalera": 1}},
        {"t": 178, "zombies": {"bailarin": 1, "cubeta": 1}},
        {"t": 196, "zombies": {"pertiga": (1, 2), "diario": 1, "normal": 1}},
        {"t": 220, "bandera": True, "zombies": {"normal": 4, "cono": (2, 3), "cubeta": 1, "escalera": 1, "excavador": 1, "bailarin": 1}},   # horda
        {"t": 250, "zombies": {"puerta": 1, "excavador": 1, "cono": 1}},
        {"t": 274, "final": True, "zombies": {"normal": (6, 8), "cono": 3, "cubeta": 2, "bailarin": 2, "excavador": 1, "pertiga": 2, "escalera": 1, "puerta": 1}},   # oleada final
    ],

    "avisos": [
        # (segundo, texto, sonido). Los carteles de horda y oleada final salen solos (ver wave_manager).
        (14, "¡Se acercan los zombies!", "sirena"),
    ],
}
