"""
Nivel 1 — El jardín (~3.3 min). Zombie nuevo: cono. El más tranquilo después del tutorial.

Cada oleada dice cuántos zombies de cada tipo vienen; salen mezclados y por filas al azar,
distinto en cada partida. (mín, máx) = la cantidad también se sortea. Formato completo y qué
hace "azar": world/wave_manager.py.
"""

LEVEL = {
    "id": "nivel1",
    "nombre": "Nivel 1 - El jardín",
    "fondo": "fondos/tutorial.png",          # por ahora todos usan el fondo nevado del tutorial
    "sol_inicial": 100,
    "intervalo_sol_cielo": 8.0,     # cada cuánto cae un sol del cielo
    "azar": 0.1,                     # 0 = siempre parecido, 1 = muy distinto en cada partida

    "oleadas": [
        {"t": 18, "zombies": {"normal": 1}},
        {"t": 36, "zombies": {"normal": 1}},
        {"t": 52, "zombies": {"normal": 2}},
        {"t": 68, "zombies": {"cono": 1}},   # nuevo: cono
        {"t": 84, "zombies": {"normal": 1, "cono": 1}},
        {"t": 100, "zombies": {"normal": 2}},
        {"t": 120, "bandera": True, "zombies": {"normal": 4, "cono": 2}},   # horda
        {"t": 146, "zombies": {"normal": 2, "cono": 1}},
        {"t": 162, "zombies": {"cono": 1, "normal": 1}},
        {"t": 186, "final": True, "zombies": {"normal": 5, "cono": 3}},   # oleada final
    ],

    "avisos": [
        # (segundo, texto, sonido). Los carteles de horda y oleada final salen solos (ver wave_manager).
        (14, "¡Se acercan los zombies!", "sirena"),
    ],
}
