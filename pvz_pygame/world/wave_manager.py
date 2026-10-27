"""
Lee la lista de oleadas del nivel y va soltando zombies según el tiempo.
"""
import random
from settings import GRID_ROWS


class WaveManager:
    def __init__(self, level):
        self.pending = sorted(level["oleadas"], key=lambda w: w[0])
        self.notices = sorted(level.get("avisos", []), key=lambda n: n[0])
        self.total = len(self.pending)
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
        return self.spawned / self.total if self.total else 1.0
