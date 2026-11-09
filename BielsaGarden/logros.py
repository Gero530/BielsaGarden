"""
Logros del juego. Son de la CUENTA del jugador (cuentas.py): se guardan dentro de su cuenta en
cuentas.json y valen para todo lo que juegue con ella. Una vez completado, queda completado.
Sin cuenta activa (solo en las pruebas) se cuentan en memoria y no se guardan.

El juego avisa lo que pasa con cuatro funciones (las llaman las entidades y gameplay.py):
    sumar("muertes_kyle")              contador += 1   (o sumar(clave, n))
    agregar("toallin_tipos", "cono")   conjunto: agrega un valor (sin repetir)
    maximo("kenny_simultaneas", 4)     se queda con el mejor valor
Después de cada aviso se revisan los logros; los que se completan aparecen en un cartel
(ui/aviso_logro.py) y se guardan al momento. El resto del progreso se guarda al cambiar
de pantalla y al cerrar el juego (guardar()).

Para agregar un logro: sumá un dict a LOGROS (id, nombre, descripcion, icono, tipo, clave,
meta) y llamá a sumar/agregar/maximo con su clave donde pase la acción.
  tipo "contador": progreso = valor del contador         (meta = número)
  tipo "conjunto": progreso = cuántos de `meta` hay en el conjunto (meta = lista de valores)
  tipo "maximo":   progreso = mejor valor alcanzado       (meta = número)
  icono: (clave de sprite de ui/sprites.py, n.º de frame) o ("retrato", clave de ui/dialogo.py)
"""
import time
import cuentas
from levels import LEVELS


def _tipos_hipnotizables():
    """Tipos de zombie que aparecen en los niveles y que Toallin puede hipnotizar."""
    from entities.zombies import ZOMBIE_CLASSES
    from world.wave_manager import tipos_de_oleada
    tipos = {"normal"}                      # el bailarín invoca normales
    for lv in LEVELS:
        for w in lv.get("oleadas", []):
            tipos.update(tipos_de_oleada(w))
    if "gigante" in tipos:
        tipos.add("mini")                   # el gigante tira al mini
    orden = list(ZOMBIE_CLASSES)
    return sorted((t for t in tipos if t in ZOMBIE_CLASSES and ZOMBIE_CLASSES[t].hipnotizable),
                  key=orden.index)


LOGROS = [
    {"id": "autoridad", "nombre": "¡Respetad mi autoridad!",
     "descripcion": "Completa todos los niveles.",
     "icono": ("cartman_festejo", 0), "tipo": "conjunto", "clave": "niveles",
     "meta": [lv["id"] for lv in LEVELS if lv["id"] != "tutorial"]},
    {"id": "huesos_grandes", "nombre": "No soy gordo, soy de huesos grandes",
     "descripcion": "Consigue 10000 de energía (sumando todo lo que juegues).",
     "icono": ("girasol", 2), "tipo": "contador", "clave": "energia", "meta": 10000},
    {"id": "mataron_a_kenny", "nombre": "¡Oh, Dios mío! Mataron a Kenny",
     "descripcion": "Utiliza a Kenny para matar a 6 zombies al mismo tiempo.",
     "icono": ("kenny", 0), "tipo": "maximo", "clave": "kenny_simultaneas", "meta": 6},
    {"id": "toallin", "nombre": "Hoy aprendí algo, no debería drogarme para tener ideas, debería tener "
                                "ideas y drogarme para premiarme a mí mismo",
     "descripcion": "Usa la habilidad de Toallin y toma control de todos los tipos de zombies al menos una vez.",
     "icono": ("toallin", 0), "tipo": "conjunto", "clave": "toallin_tipos", "meta": None},   # ver meta()
    {"id": "patea_al_bebe", "nombre": "¿Listo, Ike? ¡Patea al bebé!",
     "descripcion": "Mata 100 zombies usando a Kyle.",
     "icono": ("ike", 2), "tipo": "contador", "clave": "muertes_kyle", "meta": 100},
    {"id": "timmy", "nombre": "¡TIMMAEH!",
     "descripcion": "Gana un nivel en el que Timmy haya salido durante la oleada final.",
     "icono": ("podadora_activa", 0), "tipo": "contador", "clave": "timmy_final", "meta": 1},
    {"id": "woo_hoo", "nombre": "¡WOO-HOO!",
     "descripcion": "Mata a 100 zombies con Kenny.",
     "icono": ("kenny", 3), "tipo": "contador", "clave": "muertes_kenny", "meta": 100},
    {"id": "aprendi_algo", "nombre": "Sabes, hoy he aprendido algo...",
     "descripcion": "Mata a 100 zombies usando a Stan.",
     "icono": ("lanzaguisantes", 0), "tipo": "contador", "clave": "muertes_lanzaguisantes", "meta": 100},
    {"id": "butters", "nombre": "No eres malo en el fútbol, Butters. Eres malo en todos los deportes",
     "descripcion": "Haz que Butters sobreviva a un nivel 10 veces (ganarlo con Butters en el césped).",
     "icono": ("nuez", 0), "tipo": "contador", "clave": "butters_sobrevive", "meta": 10},
    {"id": "jesus", "nombre": "Soy judío. Tengo ciertos complejos respecto a matar a Jesús",
     "descripcion": "Utiliza a Jesús para matar a 6 zombies al mismo tiempo.",
     "icono": ("picante", 0), "tipo": "maximo", "clave": "picante_simultaneas", "meta": 6},
    {"id": "santi", "nombre": "Pero ya sabes, hoy he aprendido algo. He aprendido que las personas que "
                              "quieren poder, mucho poder, siempre acaban muertas",
     "descripcion": "Utiliza a Santi para quitar defensas a los zombies 20 veces.",
     "icono": ("iman_cargado", 0), "tipo": "contador", "clave": "santi_defensas", "meta": 20},
    {"id": "gero", "nombre": "Que les den, chicos, me voy a casa",
     "descripcion": "Utiliza a Gero para aplastar a 50 zombies.",
     "icono": ("aplastadora_salto", 0), "tipo": "contador", "clave": "muertes_aplastadora", "meta": 50},
    {"id": "tutorial", "nombre": "Acá no se improvisa",
     "descripcion": "Completa el tutorial.",
     "icono": ("retrato", "tutorial"), "tipo": "conjunto", "clave": "niveles", "meta": ["tutorial"]},
]
_sin_cuenta = None     # logros en memoria cuando no hay cuenta activa (pruebas)
_sucio = False         # hay progreso sin guardar
_nuevos = []           # logros recién completados, para el cartel de aviso


def _vacio():
    return {"contadores": {}, "conjuntos": {}, "maximos": {}, "completados": {}}


def _cargar():
    """Los logros de la cuenta activa (o los de memoria si no hay cuenta)."""
    global _sin_cuenta
    d = cuentas.logros_activa()
    if d is None:
        if _sin_cuenta is None:
            _sin_cuenta = _vacio()
        d = _sin_cuenta
    for k, v in _vacio().items():               # cuentas viejas o datos incompletos
        d.setdefault(k, v)
    return d


def recargar():
    """Olvida lo pendiente (al cambiar de cuenta y en las pruebas)."""
    global _sin_cuenta, _sucio
    _sin_cuenta, _sucio = None, False
    _nuevos.clear()


def guardar():
    """Guarda la cuenta si hay progreso de logros nuevo."""
    global _sucio
    if _sucio and cuentas.activa() is not None and cuentas.guardar():
        _sucio = False


# ----------------------------------------------------------------------
# Avisos del juego
# ----------------------------------------------------------------------
def sumar(clave, n=1):
    global _sucio
    d = _cargar()
    d["contadores"][clave] = d["contadores"].get(clave, 0) + n
    _sucio = True
    revisar()


def agregar(clave, valor):
    global _sucio
    d = _cargar()
    conjunto = d["conjuntos"].setdefault(clave, [])
    if valor not in conjunto:
        conjunto.append(valor)
        _sucio = True
        revisar()


def maximo(clave, valor):
    global _sucio
    d = _cargar()
    if valor > d["maximos"].get(clave, 0):
        d["maximos"][clave] = valor
        _sucio = True
        revisar()


# ----------------------------------------------------------------------
# Consultas
# ----------------------------------------------------------------------
def meta(logro):
    """La meta del logro. La de Toallin (tipos de zombie) se calcula la primera vez: no se puede
    al importar porque entities/zombies.py importa este módulo."""
    if logro["meta"] is None:
        logro["meta"] = _tipos_hipnotizables()
    return logro["meta"]


def progreso(logro):
    """(actual, meta) del logro, con actual <= meta."""
    d = _cargar()
    tipo, clave, objetivo = logro["tipo"], logro["clave"], meta(logro)
    if tipo == "conjunto":
        tiene = set(d["conjuntos"].get(clave, []))
        return sum(1 for v in objetivo if v in tiene), len(objetivo)
    valor = d["contadores" if tipo == "contador" else "maximos"].get(clave, 0)
    return min(valor, objetivo), objetivo


def conjunto(clave):
    """Los valores guardados en un conjunto (ej. "zombies_vistos", que usa el catálogo)."""
    return set(_cargar()["conjuntos"].get(clave, []))


def completado(logro_id):
    return logro_id in _cargar()["completados"]


def fecha(logro_id):
    return _cargar()["completados"].get(logro_id)


def cantidad_completados():
    return sum(1 for l in LOGROS if completado(l["id"]))


def revisar():
    """Marca como completados los logros que llegaron a la meta (y los anota para el aviso)."""
    d = _cargar()
    nuevos = False
    for l in LOGROS:
        if l["id"] in d["completados"]:
            continue
        actual, total = progreso(l)
        if actual >= total:
            d["completados"][l["id"]] = time.strftime("%d/%m/%Y")
            _nuevos.append(l)
            nuevos = True
    if nuevos:
        global _sucio
        _sucio = True
        guardar()


def tomar_nuevos():
    """Devuelve (y vacía) la lista de logros recién completados."""
    nuevos = list(_nuevos)
    _nuevos.clear()
    return nuevos
