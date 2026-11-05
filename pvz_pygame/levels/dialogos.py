"""
Textos de los diálogos de cada nivel. Editá acá sin tocar la lógica.

La clave es el "id" del nivel (el que tiene cada LEVEL en levels/).
Cada nivel puede tener "intro", "victoria" y "derrota": una lista de mensajes
que se muestran uno por uno. Si un nivel o un tipo no está, se saltea.
"""

DIALOGOS = {
    "tutorial": {
        "victoria": ["¡Excelente! Ya sabés lo básico. En el mapa se desbloqueó el Nivel 1."],
        "derrota":  ["Uy, se colaron. ¡Probemos otra vez, que es fácil!"],
    },
    "nivel1": {
        "intro": [
            "¡Hola vecino!",
            "Los zombies vienen por la calle... y tienen MUCHA hambre de cerebros.",
            "Poné a Cartman a cocinar para juntar energía (¡hacé clic en los dedos!) y después ponelo a disparar. ¡Prepará las plantas!",
        ],
        "victoria": ["¡Ganamos! Así se juega."],
        "derrota":  ["Los zombies se comieron tu cerebro...", "¡Probemos de nuevo!"],
    },
    "nivel2": {
        "intro": ["Ojo con los nuevos: unos leen el diario, otros saltan con pértiga y otros cavan por abajo.",
                  "Probá el Picante: quema toda su fila y su columna de una.",
                  "Y si un excavador se te mete, el Imán le saca el pico."],
        "victoria": ["¡Qué crack! Se viene lo más difícil."],
        "derrota":  ["Esos excavadores son traicioneros... ¡otra vez!"],
    },
    "nivel3": {
        "intro": ["Este es el último. Vienen bailarines, bungees, tractores... y un GIGANTE.",
                  "Usá a la Aplastadora: salta encima de lo que tenga enfrente y lo hace puré."],
        "victoria": ["¡GANASTE TODO! El jardín está a salvo."],
        "derrota":  ["El gigante nos pasó por arriba. ¡Revancha!"],
    },
}
