"""
Nivel 2 — La escuela (~3.8 min). Zombie nuevo: diario (el cono ya apareció en el jardín).

Cada oleada dice cuántos zombies de cada tipo vienen; salen mezclados y por filas al azar,
distinto en cada partida. (mín, máx) = la cantidad también se sortea. Formato completo y qué
hace "azar": world/wave_manager.py.
"""

LEVEL = {
    "id": "nivel2",
    "nombre": "Nivel 2 - La escuela",
    "fondo": "fondos/tutorial.png",          # por ahora todos usan el fondo nevado del tutorial
    "sol_inicial": 100,
    "intervalo_sol_cielo": 8.0,     # cada cuánto cae un sol del cielo
    "azar": 0.2,                     # 0 = siempre parecido, 1 = muy distinto en cada partida

    "oleadas": [
        {"t": 18, "zombies": {"normal": 1}},
        {"t": 38, "zombies": {"normal": 1}},
        {"t": 54, "zombies": {"normal": 2}},
        {"t": 70, "zombies": {"cono": 1}},
        {"t": 86, "zombies": {"normal": 1, "cono": 1}},
        {"t": 102, "zombies": {"diario": 1}},   # nuevo: diario
        {"t": 124, "bandera": True, "zombies": {"normal": 4, "cono": 2, "diario": 1}},   # horda
        {"t": 150, "zombies": {"normal": 2, "cono": 1}},
        {"t": 166, "zombies": {"diario": 1, "cono": 1}},
        {"t": 182, "zombies": {"normal": 2, "diario": 1}},
        {"t": 206, "final": True, "zombies": {"normal": 5, "cono": 3, "diario": 2}},   # oleada final
    ],

    "avisos": [
        # (segundo, texto, sonido). Los carteles de horda y oleada final salen solos (ver wave_manager).
        (14, "¡Se acercan los zombies!", "sirena"),
    ],
}
