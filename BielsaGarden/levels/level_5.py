LEVEL = {
    "id": "nivel5",
    "nombre": "Nivel 5 - El parque",
    "fondo": "fondos/tutorial.png",
    "sol_inicial": 150,
    "intervalo_sol_cielo": 8.0,
    "azar": 0.65,

    "oleadas": [
        {"t": 18, "zombies": {"normal": 2}},
        {"t": 36, "zombies": {"cono": 1, "normal": 1}},
        {"t": 56, "zombies": {"bailarin": 1}},
        {"t": 76, "zombies": {"pertiga": 1, "diario": 1}},
        {"t": 94, "zombies": {"cubeta": 1, "normal": (1, 2)}},
        {"t": 110, "zombies": {"excavador": 1}},
        {"t": 132, "bandera": True, "zombies": {"normal": (4, 6), "cono": 2, "bailarin": 1, "pertiga": 1, "puerta": 1}},
        {"t": 160, "zombies": {"excavador": 1, "cono": 1, "escalera": 1}},
        {"t": 178, "zombies": {"bailarin": 1, "cubeta": 1}},
        {"t": 196, "zombies": {"pertiga": (1, 2), "diario": 1, "normal": 1}},
        {"t": 220, "bandera": True, "zombies": {"normal": 4, "cono": (2, 3), "cubeta": 1, "escalera": 1, "excavador": 1, "bailarin": 1}},
        {"t": 250, "zombies": {"puerta": 1, "excavador": 1, "cono": 1}},
        {"t": 274, "final": True, "zombies": {"normal": (6, 8), "cono": 3, "cubeta": 2, "bailarin": 2, "excavador": 1, "pertiga": 2, "escalera": 1, "puerta": 1}},
    ],

    "avisos": [
        (14, "¡Se acercan los zombies!", "sirena"),
    ],
}
