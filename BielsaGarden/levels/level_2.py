LEVEL = {
    "id": "nivel2",
    "nombre": "Nivel 2 - La escuela",
    "fondo": "fondos/tutorial.png",
    "sol_inicial": 100,
    "intervalo_sol_cielo": 8.0,
    "azar": 0.2,

    "oleadas": [
        {"t": 18, "zombies": {"normal": 1}},
        {"t": 38, "zombies": {"normal": 1}},
        {"t": 54, "zombies": {"normal": 2}},
        {"t": 70, "zombies": {"cono": 1}},
        {"t": 86, "zombies": {"normal": 1, "cono": 1}},
        {"t": 102, "zombies": {"diario": 1}},
        {"t": 124, "bandera": True, "zombies": {"normal": 4, "cono": 2, "diario": 1}},
        {"t": 150, "zombies": {"normal": 2, "cono": 1}},
        {"t": 166, "zombies": {"diario": 1, "cono": 1}},
        {"t": 182, "zombies": {"normal": 2, "diario": 1}},
        {"t": 206, "final": True, "zombies": {"normal": 5, "cono": 3, "diario": 2}},
    ],

    "avisos": [
        (14, "¡Se acercan los zombies!", "sirena"),
    ],
}
