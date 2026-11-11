"""
Volumen del juego (pestaña Sonido de Opciones).

Hay un volumen general y uno por categoría (música, efectos, personajes, enemigos), cada
uno de 0 a 100 y con su casilla de silencio. El volumen real de un sonido es:

    volumen propio (settings.py) x general x categoría

y vale 0 si el general o la categoría están silenciados, o si la ventana está en segundo
plano y está marcada "Silenciar en segundo plano".

La configuración se guarda en config.json (clave "sonido"), junto con la de pantalla.
"""
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
    """Lee la sección "sonido" de config.json (valores inválidos o faltantes: los de fábrica)."""
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
    """Vuelve a unos valores anteriores (Opciones > Volver sin aplicar) y los hace sonar."""
    config.clear()
    config.update(copy.deepcopy(valores))
    aplicar()


def factor(categoria):
    """Multiplicador (0.0 a 1.0) para un sonido de esa categoría."""
    if not _en_foco and config["silenciar_fondo"]:
        return 0.0
    total = 1.0
    for k in ("general", categoria):
        if config["silencio"].get(k):
            return 0.0
        total *= config["volumen"].get(k, 100) / 100.0
    return total


def set_foco(en_foco):
    """Lo llama el bucle principal cuando la ventana gana o pierde el foco."""
    global _en_foco
    if en_foco != _en_foco:
        _en_foco = en_foco
        aplicar()


def aplicar():
    """Actualiza el volumen de lo que está cargado y sonando."""
    from ui import sonidos, musica
    sonidos.aplicar_volumen()
    musica.aplicar_volumen()
