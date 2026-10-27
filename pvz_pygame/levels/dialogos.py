"""
Textos de los diálogos de cada nivel. Editá acá sin tocar la lógica.

La clave es el número de nivel (1 = primer nivel de levels/__init__.py).
Cada nivel puede tener "intro", "victoria" y "derrota": una lista de mensajes
que se muestran uno por uno. Si un nivel o un tipo no está, se saltea.
"""

DIALOGOS = {
    1: {
        "intro": [
            "¡Hola vecino!",
            "Los zombies vienen por la calle... y tienen MUCHA hambre de cerebros.",
            "Poné a Cartman a cocinar para juntar energía (¡hacé clic en los dedos!) y después ponelo a disparar. ¡Prepará las plantas!",
        ],
        "victoria": ["¡Ganamos! Así se juega."],
        "derrota":  ["Los zombies se comieron tu cerebro...", "¡Probemos de nuevo!"],
    },
}
