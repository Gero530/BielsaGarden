LEVEL = {
    "id": "nivel4",
    "nombre": "Nivel 4 - El lago",
    "fondo": "fondos/tutorial.png",
    "sol_inicial": 125,
    "intervalo_sol_cielo": 8.0,
    "azar": 0.5,

    "oleadas": [
        {"t": 18, "zombies": {"normal": 1}},
        {"t": 36, "zombies": {"normal": 1, "cono": 1}},
        {"t": 54, "zombies": {"pertiga": 1}},
        {"t": 72, "zombies": {"normal": 2, "diario": 1}},
        {"t": 90, "zombies": {"cono": 1, "cubeta": 1}},
        {"t": 106, "zombies": {"escalera": 1}},
        {"t": 128, "bandera": True, "zombies": {"normal": (4, 5), "cono": 2, "pertiga": 1, "puerta": 1, "escalera": 1}},
        {"t": 156, "zombies": {"pertiga": 1, "cono": (1, 2)}},
        {"t": 172, "zombies": {"escalera": 1, "cubeta": 1, "normal": 1}},
        {"t": 190, "zombies": {"diario": (1, 2), "puerta": 1, "normal": 1}},
        {"t": 214, "bandera": True, "zombies": {"normal": 4, "cono": 2, "pertiga": 2, "cubeta": 1, "escalera": 1}},
        {"t": 244, "final": True, "zombies": {"normal": (5, 7), "cono": 3, "cubeta": 2, "pertiga": 2, "escalera": 2, "puerta": 1, "diario": 1}},
    ],

    "avisos": [
        (14, "¡Se acercan los zombies!", "sirena"),
    ],
}
