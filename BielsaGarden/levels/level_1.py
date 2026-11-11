LEVEL = {
    "id": "nivel1",
    "nombre": "Nivel 1 - El jardín",
    "fondo": "fondos/tutorial.png",
    "sol_inicial": 100,
    "intervalo_sol_cielo": 8.0,
    "azar": 0.1,

    "oleadas": [
        {"t": 18, "zombies": {"normal": 1}},
        {"t": 36, "zombies": {"normal": 1}},
        {"t": 52, "zombies": {"normal": 2}},
        {"t": 68, "zombies": {"cono": 1}},
        {"t": 84, "zombies": {"normal": 1, "cono": 1}},
        {"t": 100, "zombies": {"normal": 2}},
        {"t": 120, "bandera": True, "zombies": {"normal": 4, "cono": 2}},
        {"t": 146, "zombies": {"normal": 2, "cono": 1}},
        {"t": 162, "zombies": {"cono": 1, "normal": 1}},
        {"t": 186, "final": True, "zombies": {"normal": 5, "cono": 3}},
    ],

    "avisos": [
        (14, "¡Se acercan los zombies!", "sirena"),
    ],
}
