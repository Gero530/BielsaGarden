import json
import os
import time

CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA = os.path.join(CARPETA, "cuentas.json")
MAX_CUENTAS = 6
MAX_NOMBRE = 12

_estado = None


def _vacio():
    return {"activa": None, "siguiente": 1, "cuentas": {}}


def _cargar():
    global _estado
    if _estado is None:
        _estado = _vacio()
        try:
            with open(RUTA, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("cuentas"), dict):
                _estado["cuentas"] = {k: v for k, v in data["cuentas"].items()
                                      if isinstance(v, dict) and isinstance(v.get("nombre"), str)}
                _estado["siguiente"] = max([int(data.get("siguiente", 1))] +
                                           [int(k) + 1 for k in _estado["cuentas"] if k.isdigit()])
                if data.get("activa") in _estado["cuentas"]:
                    _estado["activa"] = data["activa"]
        except (OSError, ValueError, TypeError):
            pass
        if _estado["activa"] is None and _estado["cuentas"]:
            _estado["activa"] = lista()[0][0]
    return _estado


def recargar():
    global _estado
    _estado = None
    _cargar()


def guardar():
    estado = _cargar()
    tmp = RUTA + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(estado, f, indent=2, ensure_ascii=False)
        os.replace(tmp, RUTA)
        return True
    except OSError as e:
        print(f"[cuentas] No se pudo guardar: {e}")
        return False


def lista():
    cuentas = _cargar()["cuentas"]
    return sorted(cuentas.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0)


def hay_cuentas():
    return bool(_cargar()["cuentas"])


def id_activa():
    return _cargar()["activa"]


def activa():
    estado = _cargar()
    return estado["cuentas"].get(estado["activa"])


def nombre_activa():
    datos = activa()
    return datos["nombre"] if datos else ""


def logros_activa():
    datos = activa()
    if datos is None:
        return None
    return datos.setdefault("logros", {"contadores": {}, "conjuntos": {}, "maximos": {}, "completados": {}})


def validar_nombre(nombre, excepto=None):
    nombre = nombre.strip()
    if not nombre:
        return "Escribí un nombre"
    if len(nombre) > MAX_NOMBRE:
        return f"Máximo {MAX_NOMBRE} letras"
    for cid, datos in lista():
        if cid != excepto and datos["nombre"].strip().upper() == nombre.upper():
            return "Ya hay una cuenta con ese nombre"
    return None


def crear(nombre):
    estado = _cargar()
    primera_vez = not os.path.exists(RUTA) and not estado["cuentas"]
    cid = str(estado["siguiente"])
    estado["siguiente"] += 1
    estado["cuentas"][cid] = {"nombre": nombre.strip(), "creada": time.strftime("%d/%m/%Y"),
                              "progreso": [], "velocidad": 1}
    if primera_vez:
        _migrar(estado["cuentas"][cid])
    estado["activa"] = cid
    guardar()
    return cid


def renombrar(cid, nombre):
    estado = _cargar()
    if cid in estado["cuentas"]:
        estado["cuentas"][cid]["nombre"] = nombre.strip()
        guardar()


def activar(cid):
    estado = _cargar()
    if cid in estado["cuentas"]:
        estado["activa"] = cid
        guardar()


def borrar(cid):
    estado = _cargar()
    estado["cuentas"].pop(cid, None)
    if estado["activa"] == cid or estado["activa"] not in estado["cuentas"]:
        quedan = lista()
        estado["activa"] = quedan[0][0] if quedan else None
    guardar()


def cargar_en(game):
    datos = activa() or {}
    game.progreso = set(datos.get("progreso", []))
    if datos.get("velocidad") in (1, 2, 3):
        game.velocidad = datos["velocidad"]


def guardar_desde(game):
    datos = activa()
    if datos is None:
        return False
    datos["progreso"] = sorted(game.progreso)
    datos["velocidad"] = getattr(game, "velocidad", 1)
    return guardar()


def _migrar(cuenta):
    try:
        with open(os.path.join(CARPETA, "logros.json"), encoding="utf-8") as f:
            viejos = json.load(f)
        if isinstance(viejos, dict):
            cuenta["logros"] = {k: viejos.get(k, {}) if isinstance(viejos.get(k), dict) else {}
                                for k in ("contadores", "conjuntos", "maximos", "completados")}
    except (OSError, ValueError):
        pass
    try:
        with open(os.path.join(CARPETA, "partidas.json"), encoding="utf-8") as f:
            partidas = json.load(f).get("partidas", {})
        mejor = max(partidas.values(), key=lambda p: len(p.get("progreso", [])), default=None)
        if mejor:
            cuenta["progreso"] = list(mejor.get("progreso", []))
            cuenta["velocidad"] = mejor.get("velocidad", 1)
    except (OSError, ValueError, AttributeError):
        pass
