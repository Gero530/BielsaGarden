"""
Lee las oleadas del nivel y va soltando zombies según el tiempo.

Formato de cada oleada (ver levels/level_1.py):
    {"t": 120, "zombies": ["normal", "cono", ("cubeta", 2)], "bandera": True}
  - t: segundo en que empieza.
  - zombies: tipo, o (tipo, fila) para fijar la fila (0 = arriba). Sin fila = al azar.
  - cada: segundos entre un zombie y el siguiente de la misma oleada (por defecto 1.5;
    las hordas con bandera o final usan 0.8).
  - bandera: True -> horda grande: cartel "¡SE VIENE UNA HORDA!" y banderita en la barra.
  - final: True -> oleada final: cartel "¡OLEADA FINAL!".
"avisos" del nivel: lista de (segundo, texto) para carteles extra.
"""
import random
from settings import GRID_ROWS

AVISO_ANTES = 3.0            # segundos antes de la horda en que aparece el cartel
TXT_HORDA = "¡Se viene una horda!"
TXT_FINAL = "¡Oleada final!"


class WaveManager:
    def __init__(self, level):
        self.pending = []            # (segundo, tipo, fila)
        notices = list(level.get("avisos", []))
        self.flags = []              # segundos de las hordas con bandera (y la final)
        for w in level["oleadas"]:
            horda = w.get("bandera") or w.get("final")
            cada = w.get("cada", 0.8 if horda else 1.5)
            for i, z in enumerate(w["zombies"]):
                kind, row = (z, None) if isinstance(z, str) else z
                self.pending.append((w["t"] + i * cada, kind, row))
            if horda:
                self.flags.append(w["t"])
                notices.append((max(0.0, w["t"] - AVISO_ANTES), TXT_FINAL if w.get("final") else TXT_HORDA))
        self.pending.sort(key=lambda w: w[0])
        self.notices = sorted(notices, key=lambda n: n[0])
        self.total = len(self.pending)
        self.end_t = self.pending[-1][0] if self.pending else 1.0
        self.spawned = 0
        self.elapsed = 0.0
        self.last_row = None

    def _pick_row(self, row):
        if row is not None:
            return row
        # Fila al azar, evitando repetir la anterior para repartir la presión
        options = [r for r in range(GRID_ROWS) if r != self.last_row]
        return random.choice(options)

    def update(self, dt):
        """Avanza el tiempo. Devuelve (zombies_a_crear, avisos_nuevos)."""
        self.elapsed += dt
        to_spawn = []
        while self.pending and self.pending[0][0] <= self.elapsed:
            _, kind, row = self.pending.pop(0)
            row = self._pick_row(row)
            self.last_row = row
            to_spawn.append((kind, row))
            self.spawned += 1

        notices = []
        while self.notices and self.notices[0][0] <= self.elapsed:
            notices.append(self.notices.pop(0)[1])
        return to_spawn, notices

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
