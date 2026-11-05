"""
TEXTOS DEL CATÁLOGO (almanaque). Cambiá acá los nombres y descripciones.

- La clave (ej. "girasol") es la del juego: no la cambies.
- El "nombre" de cada personaje es el único: lo usan el catálogo, el HUD y la pantalla de equipo.
- El orden en que aparecen acá es el orden de la grilla.
- Los números (costo, vida, daño, velocidad...) NO van acá: se leen solos de settings.py.
- La fuente pixel tiene mayúsculas, números, tildes, Ñ y los signos . , ! ? ¡ ¿ : - ' ( ) + = %
"""

PERSONAJES = {
    "girasol": {
        "nombre": "Chef Cartman",
        "descripcion": "Cocina chili sin parar y suelta dedos de energía. Dice que es por el bien del jardín, pero se come la mitad.",
    },
    "lanzaguisantes": {
        "nombre": "Stan",
        "descripcion": "Tira bolas de nieve que dañan y frenan a los zombies. Se pone nervioso cuando ve uno de cerca.",
    },
    "nuez": {
        "nombre": "Butters",
        "descripcion": "Aguanta mordiscos como nadie. Llora un montón, pero no se mueve de su lugar.",
    },
    "kyle": {
        "nombre": "Kyle",
        "descripcion": "Patea a Ike por el aire y le cae encima al zombie. Ike no está de acuerdo.",
    },
    "kenny": {
        "nombre": "Kenny",
        "descripcion": "Explota apenas lo plantás y se lleva todo lo que tiene alrededor. A los 30 segundos vuelve una vez, como siempre, y espera al próximo zombie.",
    },
    "toallin": {
        "nombre": "Toallin",
        "descripcion": "El zombie que lo muerde se marea y pasa a pelear de nuestro lado. ¿Querés fumar?",
    },
    "iman": {
        "nombre": "Santi",
        "descripcion": "Les arranca los baldes y las puertas de metal a los zombies. Después tarda en soltarlos.",
    },
    "picante": {
        "nombre": "Jesús",
        "descripcion": "Se calienta, se calienta... y explota en cruz: quema toda su fila y toda su columna.",
    },
    "aplastadora": {
        "nombre": "Gero",
        "descripcion": "Salta sobre el zombie que tenga enfrente y lo aplasta. Se queda donde cae y, después de descansar, salta de nuevo.",
    },
}



def nombre(key):
    """Nombre que se ve en el juego (HUD, catálogo, equipo, diálogos). Usalo en vez de escribirlo."""
    return PERSONAJES[key]["nombre"]


# Frases en pixel art que aparecen un momento sobre el personaje
FRASES_AL_PLANTAR = {
    "girasol": "¡Respeten mi autoridad!",
}
FRASES_SOLO_LA_PRIMERA_VEZ = {"girasol"}      # estas salen solo la primera vez que lo plantás en el nivel
FRASE_KENNY_EXPLOTA = "¡Mataron a Kenny!"

ZOMBIES = {
    "normal": {
        "nombre": "Zombie",
        "descripcion": "Camina, tiene hambre y no piensa mucho. El de siempre.",
    },
    "cono": {
        "nombre": "Zombie con cono",
        "descripcion": "Se puso un cono de tránsito en la cabeza. Le funciona bastante bien.",
    },
    "cubeta": {
        "nombre": "Zombie con balde",
        "descripcion": "Un balde de metal en la cabeza. " + nombre("iman") + " se lo puede sacar.",
    },
    "puerta": {
        "nombre": "Zombie con puerta",
        "descripcion": "Se cubre con una puerta. Las bolas de nieve rebotan, pero Ike le cae de arriba.",
    },
    "diario": {
        "nombre": "Zombie del diario",
        "descripcion": "Lee el diario tranquilo. Si se lo rompés, se enoja y sale corriendo.",
    },
    "pertiga": {
        "nombre": "Zombie con pértiga",
        "descripcion": "Corre rápido y salta por encima de la primera planta. Después se cansa.",
    },
    "escalera": {
        "nombre": "Zombie con escalera",
        "descripcion": "Le apoya una escalera a la primera planta y la pasa por arriba. La escalera queda para los demás.",
    },
    "tractor": {
        "nombre": "Zombie del tractor",
        "descripcion": "Lento, durísimo y muerde fuerte. No para por nada.",
    },
    "bungee": {
        "nombre": "Zombie bungee",
        "descripcion": "Cae del cielo colgado de una cuerda. Mirá la marca roja en el piso.",
    },
    "bailarin": {
        "nombre": "Zombie bailarín",
        "descripcion": "Cada tanto se pone a bailar y aparecen zombies a su alrededor.",
    },
    "excavador": {
        "nombre": "Zombie excavador",
        "descripcion": "Avanza bajo tierra, sale al lado de la casa y come las plantas de atrás para adelante.",
    },
    "gigante": {
        "nombre": "Gigante",
        "descripcion": "Enorme. Aplasta cualquier planta de un golpe. Cuando está por caer, revolea a un mini zombie.",
    },
    "mini": {
        "nombre": "Mini zombie",
        "descripcion": "Chiquito y rápido. Viaja a caballito del Gigante hasta que lo tiran.",
    },
    "alien": {
        "nombre": "Alien",
        "descripcion": "Bajó a ver qué pasaba en el pueblo. Entra un poco, aprieta su botón y les corta la luz a los Chef.",
    },
}
