"""
TEXTOS DEL CATÁLOGO (almanaque). Cambiá acá los nombres y descripciones.

- La clave (ej. "girasol") es la del juego: no la cambies.
- "bielsa": la frase de Bielsa que sale abajo de la ficha en el catálogo.
- El "nombre" de cada personaje es el único: lo usan el catálogo, el HUD y la pantalla de equipo.
- El orden en que aparecen acá es el orden de la grilla.
- Los números (costo, vida, daño, velocidad...) NO van acá: se leen solos de settings.py.
- La fuente pixel tiene mayúsculas, números, tildes, Ñ y los signos . , ! ? ¡ ¿ : - ' ( ) + = %
"""

PERSONAJES = {
    "girasol": {
        "nombre": "Chef Cartman",
        "descripcion": "Cocina chili sin parar y suelta dedos de energía. Dice que es por el bien del jardín, pero se come la mitad.",
        "bielsa": "Sin energía no hay presión. Cartman cocina y el equipo corre. Es así de simple.",
    },
    "lanzaguisantes": {
        "nombre": "Stan",
        "descripcion": "Tira bolas de nieve que dañan y frenan a los zombies. Se pone nervioso cuando ve uno de cerca.",
        "bielsa": "Stan no es el más talentoso, pero es constante. Y la constancia gana partidos.",
    },
    "nuez": {
        "nombre": "Butters",
        "descripcion": "Aguanta mordiscos como nadie. Llora un montón, pero no se mueve de su lugar.",
        "bielsa": "Llora, sí. Pero no abandona su lugar. Eso se llama compromiso.",
    },
    "kyle": {
        "nombre": "Kyle",
        "descripcion": "Patea a Ike por el aire y le cae encima al zombie. Ike no está de acuerdo.",
        "bielsa": "Kyle juega por arriba. Al rival le cuesta defender lo que no ve venir.",
    },
    "kenny": {
        "nombre": "Kenny",
        "descripcion": "Explota apenas lo plantás y se lleva todo lo que tiene alrededor. A los 30 segundos vuelve una vez, como siempre, y espera al próximo zombie.",
        "bielsa": "Se sacrifica por el equipo. Siempre. Después vuelve. No sé cómo, y prefiero no preguntar.",
    },
    "toallin": {
        "nombre": "Toallin",
        "descripcion": "El zombie que lo muerde se marea y pasa a pelear de nuestro lado. ¿Querés fumar?",
        "bielsa": "No apruebo sus métodos. Pero convierte rivales en compañeros, y eso no lo hace cualquiera.",
    },
    "iman": {
        "nombre": "Santi",
        "descripcion": "Les arranca los baldes y las puertas de metal a los zombies. Después tarda en soltarlos.",
        "bielsa": "Le quita la armadura al rival. Y un rival sin defensa es un rival que duda.",
    },
    "picante": {
        "nombre": "Jesús",
        "descripcion": "Se calienta, se calienta... y explota en cruz: quema toda su fila y toda su columna.",
        "bielsa": "Ocupa toda la fila y toda la columna. Eso es ocupar los espacios.",
    },
    "aplastadora": {
        "nombre": "Gero",
        "descripcion": "Salta sobre el zombie que tenga enfrente y lo aplasta. Se queda donde cae y, después de descansar, salta de nuevo.",
        "bielsa": "Presiona arriba y no da respiro. Después descansa. Es lógico, nadie presiona siempre.",
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
        "bielsa": "El zombie común es el más peligroso, porque uno lo subestima.",
    },
    "cono": {
        "nombre": "Zombie con cono",
        "descripcion": "Se puso un cono de tránsito en la cabeza. Le funciona bastante bien.",
        "bielsa": "Un cono en la cabeza. Parece poco, pero aguanta el doble. No se confíe.",
    },
    "cubeta": {
        "nombre": "Zombie con balde",
        "descripcion": "Un balde de metal en la cabeza. " + nombre("iman") + " se lo puede sacar.",
        "bielsa": "Con el balde puesto es otro rival. Hay que sacárselo primero.",
    },
    "puerta": {
        "nombre": "Zombie con puerta",
        "descripcion": "Se cubre con una puerta. Las bolas de nieve rebotan, pero Ike le cae de arriba.",
        "bielsa": "Defiende de frente. Entonces hay que atacarlo por arriba.",
    },
    "diario": {
        "nombre": "Zombie del diario",
        "descripcion": "Lee el diario tranquilo. Si se lo rompés, se enoja y sale corriendo.",
        "bielsa": "Sin el diario se enoja y corre. No se lo rompa cerca de la casa.",
    },
    "pertiga": {
        "nombre": "Zombie con pértiga",
        "descripcion": "Corre rápido y salta por encima de la primera planta. Después se cansa.",
        "bielsa": "Salta la primera línea. La segunda tiene que estar preparada.",
    },
    "escalera": {
        "nombre": "Zombie con escalera",
        "descripcion": "Le apoya una escalera a la primera planta y la pasa por arriba. La escalera queda para los demás.",
        "bielsa": "Apoya la escalera y pasan todos. Hay que cortar la jugada antes.",
    },
    "tractor": {
        "nombre": "Zombie del tractor",
        "descripcion": "Lento, durísimo y muerde fuerte. No para por nada.",
        "bielsa": "Lento, pero muerde fuerte. No le regale tiempo.",
    },
    "bungee": {
        "nombre": "Zombie bungee",
        "descripcion": "Cae del cielo colgado de una cuerda. Mirá la marca roja en el piso.",
        "bielsa": "Cae donde menos lo espera. Hay que cubrir todo el campo.",
    },
    "bailarin": {
        "nombre": "Zombie bailarín",
        "descripcion": "Cada tanto se pone a bailar y aparecen zombies a su alrededor.",
        "bielsa": "Si lo deja bailar, llegan cuatro más. Hay que presionarlo rápido.",
    },
    "excavador": {
        "nombre": "Zombie excavador",
        "descripcion": "Avanza bajo tierra, sale al lado de la casa y come las plantas de atrás para adelante.",
        "bielsa": "Ataca por la espalda. El orden defensivo es de todos, también atrás.",
    },
    "gigante": {
        "nombre": "Gigante",
        "descripcion": "Enorme. Aplasta cualquier planta de un golpe. Cuando está por caer, revolea a un mini zombie.",
        "bielsa": "Es superior físicamente. Eso no nos exime de intentar ganarle.",
    },
    "mini": {
        "nombre": "Mini zombie",
        "descripcion": "Chiquito y rápido. Viaja a caballito del Gigante hasta que lo tiran.",
        "bielsa": "Chico, rápido y molesto. Como un buen enganche.",
    },
    "alien": {
        "nombre": "Alien",
        "descripcion": "Bajó a ver qué pasaba en el pueblo. Entra un poco, aprieta su botón y les corta la luz a los Chef.",
        "bielsa": "Le apaga la luz a Cartman. Sin energía no hay juego. Prioridad absoluta.",
    },
}
