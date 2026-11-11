import copy
import display

CATEGORIAS = [
    ("general", "General"),
    ("musica", "Música"),
    ("efectos", "Efectos"),
    ("personajes", "Personajes"),
    ("enemigos", "Enemigos"),
]

DEFAULT = {
    "volumen": {k: 100 for k, _ in CATEGORIAS},
    "silencio": {k: False for k, _ in CATEGORIAS},
    "silenciar_fondo": True,
}

config = copy.deepcopy(DEFAULT)
_en_foco = True


def cargar():
    config.clear()
    config.update(copy.deepcopy(DEFAULT))
    data = display.leer_config_json().get("sonido")
    if not isinstance(data, dict):
        return
    for k, _ in CATEGORIAS:
        v = data.get("volumen", {}).get(k) if isinstance(data.get("volumen"), dict) else None
        if isinstance(v, (int, float)):
            config["volumen"][k] = max(0, min(100, int(v)))
        s = data.get("silencio", {}).get(k) if isinstance(data.get("silencio"), dict) else None
        if isinstance(s, bool):
            config["silencio"][k] = s
    if isinstance(data.get("silenciar_fondo"), bool):
        config["silenciar_fondo"] = data["silenciar_fondo"]


def guardar():
    display.escribir_config_json({"sonido": config})


def copia():
    return copy.deepcopy(config)


def restaurar(valores):
    config.clear()
    config.update(copy.deepcopy(valores))
    aplicar()


def factor(categoria):
    if not _en_foco and config["silenciar_fondo"]:
        return 0.0
    total = 1.0
    for k in ("general", categoria):
        if config["silencio"].get(k):
            return 0.0
        total *= config["volumen"].get(k, 100) / 100.0
    return total


def set_foco(en_foco):
    global _en_foco
    if en_foco != _en_foco:
        _en_foco = en_foco
        aplicar()


def aplicar():
    from ui import sonidos, musica
    sonidos.aplicar_volumen()
    musica.aplicar_volumen()
