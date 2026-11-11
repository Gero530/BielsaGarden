"""
Ajustes de dificultad (Opciones > Juego): daño, vida, costo y recarga de cada personaje, como
porcentaje de su valor original (100 % = como viene en settings.PLANT_DATA).

Los valores originales se copian al importar este módulo; aplicar() reescribe PLANT_DATA a partir
de ellos y de los porcentajes, así todo el juego (cartas, plantas, catálogo) usa los ajustados sin
cambiar nada más. Se guardan en config.json (clave "juego"), junto con pantalla y sonido.
"""
import copy
import display
from settings import PLANT_DATA

BASE = copy.deepcopy(PLANT_DATA)                 # los valores originales, para recalcular siempre desde acá
STATS = [("dano", "Daño"), ("vida", "Vida"), ("costo", "Costo"), ("recarga", "Recarga")]
PORCENTAJES = [25, 50, 75, 100, 125, 150, 200, 300]

config = {}            # {clave del personaje: {stat: porcentaje}} (solo lo que no es 100 %)


def tiene(key, stat):
    """Si el personaje tiene esa estadística (no todos hacen daño)."""
    return stat in BASE[key]


def porcentaje(key, stat, ajustes=None):
    return (config if ajustes is None else ajustes).get(key, {}).get(stat, 100)


def valor(key, stat, pct):
    """El valor ajustado, redondeado para que tenga sentido en el juego."""
    v = BASE[key][stat] * pct / 100
    if stat == "costo":
        return max(5, int(round(v / 5)) * 5)       # de a 5 de energía
    if stat == "recarga":
        return max(0.5, round(v * 2) / 2)          # de a medio segundo
    return max(1, int(round(v)))                   # vida y daño: enteros


def aplicar():
    """Reescribe PLANT_DATA con los porcentajes actuales (en el lugar: las plantas y las cartas
    guardan una referencia a su dict y ven el cambio)."""
    for key, base in BASE.items():
        for stat, _ in STATS:
            if stat in base:
                PLANT_DATA[key][stat] = valor(key, stat, porcentaje(key, stat))


def _limpio(ajustes):
    """Sin los 100 % ni personajes/estadísticas que no existen."""
    out = {}
    for key, stats in (ajustes or {}).items():
        if key not in BASE or not isinstance(stats, dict):
            continue
        buenos = {s: int(p) for s, p in stats.items()
                  if s in BASE[key] and s in dict(STATS) and int(p) in PORCENTAJES and int(p) != 100}
        if buenos:
            out[key] = buenos
    return out


def cargar():
    data = display.leer_config_json().get("juego")
    config.clear()
    try:
        config.update(_limpio(data if isinstance(data, dict) else {}))
    except (TypeError, ValueError):
        pass
    aplicar()


def establecer(ajustes):
    """Pone estos porcentajes, los aplica al juego y los guarda."""
    config.clear()
    config.update(_limpio(ajustes))
    aplicar()
    display.escribir_config_json({"juego": config})


def copia():
    return copy.deepcopy(config)
