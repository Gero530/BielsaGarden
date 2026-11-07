"""
Partidas guardadas: hasta MAX_RANURAS ranuras ("Partida 1" ... "Partida 10") en partidas.json,
al lado de main.py.

Una partida guarda el progreso de la campaña: los niveles ganados (game.progreso) y la
velocidad elegida. No guarda un nivel a medio jugar: al continuar se vuelve al mapa.

Estado en memoria (atributos de Game):
  game.en_partida   True desde que se toca Nueva partida o Continuar.
  game.ranura       Ranura de la partida actual (1..10) o None si todavía no tiene.

Guardado automático (autoguardar): al volver al menú principal, al ganar un nivel y al cerrar
el juego. Si la partida ya tiene ranura se guarda ahí; si es nueva, en la primera ranura
libre; si no hay ninguna libre, no se guarda (hay que guardarla a mano sobre otra).
"""
import json
import os
import time

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "partidas.json")
MAX_RANURAS = 10


def nombre(ranura):
    return f"Partida {ranura}"


def cargar_todas():
    """{ranura: datos} con las ranuras ocupadas. Si el archivo no existe o está roto: {}."""
    try:
        with open(RUTA, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    partidas = {}
    for k, v in (data.get("partidas", {}) if isinstance(data, dict) else {}).items():
        try:
            n = int(k)
        except ValueError:
            continue
        if 1 <= n <= MAX_RANURAS and isinstance(v, dict) and isinstance(v.get("progreso"), list):
            partidas[n] = v
    return partidas


def _escribir(partidas):
    """Escribe en un archivo temporal y lo reemplaza: si se corta a la mitad no se rompe el anterior."""
    data = {"partidas": {str(n): partidas[n] for n in sorted(partidas)}}
    tmp = RUTA + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, RUTA)
        return True
    except OSError as e:
        print(f"[guardado] No se pudo guardar: {e}")
        return False


def hay_partidas():
    return bool(cargar_todas())


def ranura_libre(partidas=None):
    partidas = cargar_todas() if partidas is None else partidas
    return next((n for n in range(1, MAX_RANURAS + 1) if n not in partidas), None)


def guardar(game, ranura):
    """Guarda la partida actual en `ranura` (pisa lo que hubiera) y la deja como su ranura."""
    partidas = cargar_todas()
    partidas[ranura] = {
        "progreso": sorted(game.progreso),
        "velocidad": getattr(game, "velocidad", 1),
        "fecha": time.strftime("%d/%m/%Y %H:%M"),
    }
    if _escribir(partidas):
        game.ranura = ranura
        return True
    return False


def autoguardar(game):
    """Guarda la partida en curso donde corresponde. Devuelve "ok", "sin_lugar" o None (no había partida)."""
    if not getattr(game, "en_partida", False):
        return None
    ranura = game.ranura or ranura_libre()
    if ranura is None:
        return "sin_lugar"
    return "ok" if guardar(game, ranura) else None


def nueva(game):
    game.progreso = set()
    game.ranura = None
    game.en_partida = True


def continuar(game, ranura):
    """Carga la partida de `ranura` como partida actual. Devuelve False si ya no existe."""
    datos = cargar_todas().get(ranura)
    if datos is None:
        return False
    game.progreso = set(datos["progreso"])
    if datos.get("velocidad") in (1, 2, 3):
        game.velocidad = datos["velocidad"]
    game.ranura = ranura
    game.en_partida = True
    return True
