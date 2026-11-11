import copy
import display
from settings import PLANT_DATA

BASE = copy.deepcopy(PLANT_DATA)
STATS = [("dano", "Daño"), ("vida", "Vida"), ("costo", "Costo"), ("recarga", "Recarga")]
PORCENTAJES = [25, 50, 75, 100, 125, 150, 200, 300]

config = {}


def tiene(key, stat):
    return stat in BASE[key]


def porcentaje(key, stat, ajustes=None):
    return (config if ajustes is None else ajustes).get(key, {}).get(stat, 100)


def valor(key, stat, pct):
    v = BASE[key][stat] * pct / 100
    if stat == "costo":
        return max(5, int(round(v / 5)) * 5)
    if stat == "recarga":
        return max(0.5, round(v * 2) / 2)
    return max(1, int(round(v)))


def aplicar():
    for key, base in BASE.items():
        for stat, _ in STATS:
            if stat in base:
                PLANT_DATA[key][stat] = valor(key, stat, porcentaje(key, stat))


def _limpio(ajustes):
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
    config.clear()
    config.update(_limpio(ajustes))
    aplicar()
    display.escribir_config_json({"juego": config})


def copia():
    return copy.deepcopy(config)
