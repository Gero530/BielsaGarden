"""
Música del menú. Si el audio no está disponible (sin placa de sonido, etc.) el juego
sigue andando en silencio: todas las funciones capturan los errores.
"""
import os
import pygame
from settings import MUSICA_MENU, MUSICA_VOLUMEN

RUTA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", MUSICA_MENU)
_ok = None
_desde = 0.0           # desde qué segundo de la canción se arrancó la reproducción


def disponible():
    """True si hay mixer y se pudo cargar la canción."""
    global _ok
    if _ok is None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(RUTA)
            pygame.mixer.music.set_volume(MUSICA_VOLUMEN)
            _ok = True
        except (pygame.error, FileNotFoundError, OSError) as e:
            print(f"[musica] Sin música: {e}")
            _ok = False
    return _ok


def sonando():
    try:
        return disponible() and pygame.mixer.music.get_busy()
    except pygame.error:
        return False


def reproducir(desde=0.0):
    """Arranca la canción (en bucle) desde `desde` segundos. Devuelve True si suena."""
    if not disponible():
        return False
    global _desde
    try:
        pygame.mixer.music.set_volume(MUSICA_VOLUMEN)
        try:
            pygame.mixer.music.play(loops=-1, start=desde)
            _desde = desde
        except pygame.error:
            pygame.mixer.music.play(loops=-1)       # algunos formatos no aceptan 'start'
            _desde = 0.0
        return True
    except pygame.error as e:
        print(f"[musica] No se pudo reproducir: {e}")
        return False


def posicion():
    """Segundos que lleva sonando, o None si no se puede saber."""
    try:
        if disponible() and pygame.mixer.music.get_busy():
            ms = pygame.mixer.music.get_pos()
            if ms >= 0:
                return ms / 1000.0
    except pygame.error:
        pass
    return None


def tiempo():
    """Segundo actual DENTRO de la canción (medido con el reloj del audio), o None si no suena."""
    pos = posicion()
    return None if pos is None else _desde + pos


def desvanecer(ms=700):
    try:
        if disponible():
            pygame.mixer.music.fadeout(ms)
    except pygame.error:
        pass


def parar():
    try:
        if disponible():
            pygame.mixer.music.stop()
    except pygame.error:
        pass
