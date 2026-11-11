LEVEL = {
    "id": "nivel3",
    "nombre": "Nivel 3 - La mansión",
    "fondo": "fondos/tutorial.png",
    "sol_inicial": 100,
    "intervalo_sol_cielo": 8.0,
    "azar": 0.35,

    "oleadas": [
        {"t": 18, "zombies": {"normal": 1}},
        {"t": 36, "zombies": {"normal": 1, "cono": 1}},
        {"t": 54, "zombies": {"diario": 1, "normal": 1}},
        {"t": 72, "zombies": {"cubeta": 1}},
        {"t": 90, "zombies": {"normal": 2, "cono": 1}},
        {"t": 106, "zombies": {"puerta": 1}},
        {"t": 128, "bandera": True, "zombies": {"normal": 4, "cono": 2, "cubeta": 1, "puerta": 1}},
        {"t": 154, "zombies": {"cono": (1, 2), "diario": 1}},
        {"t": 170, "zombies": {"cubeta": 1, "normal": (1, 2)}},
        {"t": 186, "zombies": {"puerta": 1, "cono": 1, "diario": 1}},
        {"t": 210, "final": True, "zombies": {"normal": (5, 6), "cono": 3, "cubeta": 2, "puerta": 1, "diario": 2}},
    ],

    "avisos": [
        (14, "¡Se acercan los zombies!", "sirena"),
    ],
}
