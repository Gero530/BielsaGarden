"""
Oleadas: lee las del nivel, arma el cronograma de la partida (distinto cada vez) y va
soltando zombies según el tiempo.

Formato de cada oleada (ver levels/level_*.py):
    {"t": 120, "zombies": {"normal": 3, "cono": (1, 2)}, "bandera": True}
  - t: segundo en que empieza.
  - zombies: cuántos de cada tipo. Un número fijo, o (mínimo, máximo) para que varíe en cada
    partida. Salen MEZCLADOS (orden al azar) y cada uno por una fila al azar (repartidos: no
    repite la fila del anterior y prefiere las filas por las que vinieron menos en esa oleada).
    También vale una lista ["normal", ("cono", 2)] (orden fijo; ("tipo", fila) fija la fila):
    la usa el tutorial, que necesita que el primer zombie venga siempre por el medio.
  - duracion: segundos en los que se reparten los zombies de la oleada (por defecto, según
    cuántos son: 1,5 s por zombie, 0,8 s en hordas).
  - bandera: True -> horda grande: cartel "¡Se viene una horda!" y banderita en la barra.
  - final: True -> oleada final: cartel "¡Oleada final!".

"azar" del nivel (0 a 1, por defecto 0): cuánto cambia cada partida. Con más azar:
  - los tiempos entre zombies son más irregulares y la oleada arranca unos segundos antes o después,
  - algunos llegan en ráfaga (casi juntos, por filas distintas),
  - en las oleadas comunes puede colarse un zombie "sorpresa" de los que ya aparecen en el nivel.

"avisos" del nivel: lista de (segundo, texto) o (segundo, texto, sonido) para carteles extra.
  El sonido es un nombre de ui/sonidos.py o un par ("primero", "segundo") que suenan seguidos.
"""
import random
from settings import GRID_ROWS

AVISO_ANTES = 3.0            # segundos antes de la horda en que aparece el cartel
TXT_HORDA = "¡Se viene una horda!"
TXT_FINAL = "¡Oleada final!"
NO_SORPRESA = {"gigante", "tractor", "mini"}     # demasiado fuertes para colarse de sorpresa


def tipos_de_oleada(oleada):
    """Los tipos de zombie de una oleada (sin repetir, en el orden en que están escritos)."""
    z = oleada["zombies"]
    if isinstance(z, dict):
        return list(z)
    vistos = []
    for item in z:
        k = item if isinstance(item, str) else item[0]
        if k not in vistos:
            vistos.append(k)
    return vistos


def armar_oleada(oleada, rnd, azar=0.0, sorpresas=()):
    """[(tipo, fila o None)] de la oleada, ya mezclada. Los rangos se sortean acá."""
    z = oleada["zombies"]
    if not isinstance(z, dict):                       # lista: orden fijo (tutorial)
        return [(item, None) if isinstance(item, str) else (item[0], item[1]) for item in z]
    lista = []
    for tipo, cant in z.items():
        n = rnd.randint(cant[0], cant[1]) if isinstance(cant, (tuple, list)) else cant
        lista += [tipo] * n
    horda = oleada.get("bandera") or oleada.get("final")
    if sorpresas and not horda and rnd.random() < 0.3 * azar:
        lista.append(rnd.choice(sorpresas))
    rnd.shuffle(lista)
    return [(tipo, None) for tipo in lista]


class WaveManager:
    def __init__(self, level, seed=None):
        rnd = random.Random(seed)
        self.rnd = rnd
        azar = level.get("azar", 0.0)
        todos = []
        for w in level["oleadas"]:
            todos += tipos_de_oleada(w)
        sorpresas = sorted({t for t in todos if t not in NO_SORPRESA})

        self.pending = []            # (segundo, tipo, fila o None, n.º de oleada)
        notices = list(level.get("avisos", []))
        self.flags = []              # segundos de las hordas con bandera (y la final)
        self.final_t = None          # segundo en que arranca la oleada final (None: no tiene)
        for n_oleada, w in enumerate(level["oleadas"]):
            horda = w.get("bandera") or w.get("final")
            zombies = armar_oleada(w, rnd, azar, sorpresas)
            t0 = w["t"]
            if not horda and azar and n_oleada:            # las comunes arrancan un poco corridas
                t0 = max(1.0, t0 + rnd.uniform(-2.5, 2.5) * azar)
            for t, (kind, row) in zip(self._tiempos(w, len(zombies), rnd, azar, horda), zombies):
                self.pending.append((t0 + t, kind, row, n_oleada))
            if horda:
                self.flags.append(w["t"])
                if w.get("final"):
                    self.final_t = w["t"] if self.final_t is None else min(self.final_t, w["t"])
                    notices.append((max(0.0, w["t"] - AVISO_ANTES), TXT_FINAL, ("oleada", "sirena")))
                else:
                    notices.append((max(0.0, w["t"] - AVISO_ANTES), TXT_HORDA, "sirena"))
        self.pending.sort(key=lambda p: p[0])
        self.notices = sorted(notices, key=lambda n: n[0])
        self.total = len(self.pending)
        self.end_t = self.pending[-1][0] if self.pending else 1.0
        self.spawned = 0
        self.elapsed = 0.0
        self.last_row = None
        self.filas_oleada = {}       # n.º de oleada -> [cuántos vinieron por cada fila]

    @staticmethod
    def _tiempos(oleada, n, rnd, azar, horda):
        """Segundos (desde que arranca la oleada) en que sale cada zombie."""
        if n == 0:
            return []
        base = oleada.get("cada", 0.8 if horda else 1.5)
        if "duracion" in oleada and n > 1:
            base = oleada["duracion"] / (n - 1)
        tiempos, t = [], 0.0
        for i in range(n):
            tiempos.append(t)
            if azar and rnd.random() < 0.35 * azar:
                t += rnd.uniform(0.05, 0.3)                  # ráfaga: el siguiente sale casi junto
            else:
                t += base * rnd.uniform(1 - 0.6 * azar, 1 + 0.6 * azar)
        return tiempos

    def _pick_row(self, row, n_oleada):
        if row is not None:
            return row
        # Fila al azar, sin repetir la anterior y prefiriendo las menos usadas en esta oleada
        usadas = self.filas_oleada.setdefault(n_oleada, [0] * GRID_ROWS)
        opciones = [r for r in range(GRID_ROWS) if r != self.last_row]
        pesos = [1.0 / (1 + usadas[r]) ** 2 for r in opciones]
        return self.rnd.choices(opciones, weights=pesos)[0]

    def update(self, dt):
        """Avanza el tiempo. Devuelve (zombies_a_crear, avisos_nuevos)."""
        self.elapsed += dt
        to_spawn = []
        while self.pending and self.pending[0][0] <= self.elapsed:
            _, kind, row, n_oleada = self.pending.pop(0)
            row = self._pick_row(row, n_oleada)
            self.filas_oleada.setdefault(n_oleada, [0] * GRID_ROWS)[row] += 1
            self.last_row = row
            to_spawn.append((kind, row))
            self.spawned += 1

        notices = []
        while self.notices and self.notices[0][0] <= self.elapsed:
            aviso = self.notices.pop(0)
            # (texto, sonido): el sonido es opcional (3er dato del aviso en el nivel)
            notices.append((aviso[1], aviso[2] if len(aviso) > 2 else None))
        return to_spawn, notices

    @property
    def en_final(self):
        """True desde que arrancó la oleada final."""
        return self.final_t is not None and self.elapsed >= self.final_t

    @property
    def finished(self):
        return not self.pending

    @property
    def progress(self):
        return min(1.0, self.elapsed / self.end_t)

    @property
    def flag_marks(self):
        """Posición (0..1) de cada bandera en la barra de progreso."""
        return [min(1.0, t / self.end_t) for t in self.flags]
