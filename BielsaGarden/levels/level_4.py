"""
Nivel 4 — El lago (~4.5 min). Zombies nuevos: pértiga y escalera.

Cada oleada dice cuántos zombies de cada tipo vienen; salen mezclados y por filas al azar,
distinto en cada partida. (mín, máx) = la cantidad también se sortea. Formato completo y qué
hace "azar": world/wave_manager.py.
"""

LEVEL = {
    "id": "nivel4",
    "nombre": "Nivel 4 - El lago",
    "fondo": "fondos/tutorial.png",          # por ahora todos usan el fondo nevado del tutorial
    "sol_inicial": 125,
    "intervalo_sol_cielo": 8.0,     # cada cuánto cae un sol del cielo
    "azar": 0.5,                     # 0 = siempre parecido, 1 = muy distinto en cada partida

    "oleadas": [
        {"t": 18, "zombies": {"normal": 1}},
        {"t": 36, "zombies": {"normal": 1, "cono": 1}},
        {"t": 54, "zombies": {"pertiga": 1}},   # nuevo: pértiga
        {"t": 72, "zombies": {"normal": 2, "diario": 1}},
        {"t": 90, "zombies": {"cono": 1, "cubeta": 1}},
        {"t": 106, "zombies": {"escalera": 1}},   # nuevo: escalera
        {"t": 128, "bandera": True, "zombies": {"normal": (4, 5), "cono": 2, "pertiga": 1, "puerta": 1, "escalera": 1}},   # horda
        {"t": 156, "zombies": {"pertiga": 1, "cono": (1, 2)}},
        {"t": 172, "zombies": {"escalera": 1, "cubeta": 1, "normal": 1}},
        {"t": 190, "zombies": {"diario": (1, 2), "puerta": 1, "normal": 1}},
        {"t": 214, "bandera": True, "zombies": {"normal": 4, "cono": 2, "pertiga": 2, "cubeta": 1, "escalera": 1}},   # horda
        {"t": 244, "final": True, "zombies": {"normal": (5, 7), "cono": 3, "cubeta": 2, "pertiga": 2, "escalera": 2, "puerta": 1, "diario": 1}},   # oleada final
    ],

    "avisos": [
        # (segundo, texto, sonido). Los carteles de horda y oleada final salen solos (ver wave_manager).
        (14, "¡Se acercan los zombies!", "sirena"),
    ],
}
