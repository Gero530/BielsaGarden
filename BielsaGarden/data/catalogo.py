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
        "descripcion": "Les arranca los baldes a los zombies y se lleva a Winnie the Pooh de los brazos de Mickey. Después tarda en soltarlos.",
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
    return PERSONAJES[key]["nombre"]


FRASES_AL_PLANTAR = {
    "girasol": "¡Respeten mi autoridad!",
}
FRASES_SOLO_LA_PRIMERA_VEZ = {"girasol"}
FRASE_KENNY_EXPLOTA = "¡Mataron a Kenny!"

ZOMBIES = {
    "normal": {
        "nombre": "Terrance",
        "descripcion": "Camina a saltitos, tiene hambre y no piensa mucho. Se come las plantas saltando.",
        "bielsa": "Terrance es el más peligroso, porque uno lo subestima.",
    },
    "cono": {
        "nombre": "Phillip",
        "descripcion": "Salta como Terrance pero con un cono de tránsito en la cabeza. Le funciona bastante bien.",
        "bielsa": "Phillip y su cono. Parece poco, pero aguanta el doble. No se confíe.",
    },
    "cubeta": {
        "nombre": "Chef",
        "descripcion": "Chef resucitado como Darth Vader. Salta con su armadura; al golpearlo pierde el casco y luego todo el traje. " + nombre("iman") + " se lo saca de una.",
        "bielsa": "Con la armadura puesta es otro rival. Hay que sacársela primero.",
    },
    "puerta": {
        "nombre": "Mickey con Pooh",
        "descripcion": "Camina con Winnie the Pooh en el brazo como escudo. Las bolas de nieve rebotan en Pooh, pero Ike le cae de arriba. Sin Pooh es un Mickey cualquiera.",
        "bielsa": "Pooh lo defiende de frente. Atáquelo por arriba o sáquele a Pooh con el imán.",
    },
    "diario": {
        "nombre": "Gerald",
        "descripcion": "El papá de Kyle, en su fase delfín. Camina tranquilo con los bastones. Si se los rompés, se enoja y sale corriendo.",
        "bielsa": "Sin los bastones se enoja y corre. No se los rompa cerca de la casa.",
    },
    "pertiga": {
        "nombre": "El murciélago",
        "descripcion": "Corre a saltitos y, al llegar a la primera planta, la salta volando de panza como en la lucha libre. Cae al piso, se levanta y sigue caminando lento.",
        "bielsa": "Salta la primera línea. La segunda tiene que estar preparada.",
    },
    "escalera": {
        "nombre": "Trent Boyett",
        "descripcion": "Camina con una escalera al hombro. Al llegar a la primera planta la apoya y la pasa por arriba. La escalera queda para los demás.",
        "bielsa": "Apoya la escalera y pasan todos. Hay que cortar la jugada antes.",
    },
    "garrison": {
        "nombre": "Sr. Garrison",
        "descripcion": "Lento, durísimo y muerde fuerte. Rueda en su rueda gigante y no para por nada.",
        "bielsa": "Lento, pero muerde fuerte. No le regale tiempo.",
    },
    "bungee": {
        "nombre": "Randy",
        "descripcion": "Cae del cielo colgado de una cuerda con su raro traje de Spider-Man. Mirá la marca roja en el piso. Con los golpes pierde el traje, después la máscara.",
        "bielsa": "Cae donde menos lo espera. Hay que cubrir todo el campo.",
    },
    "bailarin": {
        "nombre": "Crab king",
        "descripcion": "Cada tanto se pone a bailar y aparecen cangrejos a su alrededor.",
        "bielsa": "Si lo deja bailar, llegan cuatro más. Hay que presionarlo rápido.",
    },
    "cangrejo_invocado": {
        "nombre": "Crab people",
        "descripcion": "Lo llama el Crab king cuando se pone a bailar. Camina y muerde como cualquier zombie.",
        "bielsa": "Llegan de a cuatro, por todos los costados. Hay que achicar espacios.",
    },
    "excavador": {
        "nombre": "Pip",
        "descripcion": "Philip Pirrup, el de los viejos tiempos. Cava bajo tierra, sale al lado de la casa y come las plantas de atrás para adelante.",
        "bielsa": "Ataca por la espalda. El orden defensivo es de todos, también atrás.",
    },
    "gigante": {
        "nombre": "Sr. Mackey",
        "descripcion": "Altísimo y durísimo. Aplasta cualquier planta de un pisotón. Camina con el Sr. Nelson sobre la cabeza y, cuando está por caer, lo revolea.",
        "bielsa": "Es superior físicamente. Eso no nos exime de intentar ganarle.",
    },
    "mini": {
        "nombre": "Sr. Nelson",
        "descripcion": "Chiquito y rápido. Viaja sobre la cabeza del Sr. Mackey hasta que lo revolea. Y recuerden, las palabras son como las balas.",
        "bielsa": "Chico, rápido y molesto. Como un buen enganche.",
    },
    "alien": {
        "nombre": "Alien",
        "descripcion": "Bajó a ver qué pasaba en el pueblo. Entra un poco, aprieta su botón y les corta la luz a los Chef.",
        "bielsa": "Le apaga la luz a Cartman. Sin energía no hay juego. Prioridad absoluta.",
    },
}
