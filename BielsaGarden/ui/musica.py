"""
Música del menú. Si el audio no está disponible (sin placa de sonido, etc.) el juego
sigue andando en silencio: todas las funciones capturan los errores.
"""
import os
import pygame
from settings import MUSICA_MENU, MUSICA_VOLUMEN, MUSICA_PARTIDA
from ui import audio

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
RUTA = os.path.join(ASSETS, MUSICA_MENU)
_ok = None
_desde = 0.0           # desde qué segundo de la canción se arrancó la reproducción
_base = MUSICA_VOLUMEN   # volumen propio del tema cargado (antes de Opciones > Sonido)


def _volumen(base):
    """Pone el volumen del tema: el suyo x el de Opciones > Sonido (general y música)."""
    global _base
    _base = base
    pygame.mixer.music.set_volume(base * audio.factor("musica"))


def aplicar_volumen():
    try:
        if pygame.mixer.get_init():
            _volumen(_base)
    except pygame.error:
        pass


def disponible():
    """True si hay mixer y se pudo cargar la canción."""
    global _ok
    if _ok is None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(RUTA)
            _volumen(MUSICA_VOLUMEN)
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
        pygame.mixer.music.load(RUTA)       # puede haber quedado cargado un tema de la partida
        _volumen(MUSICA_VOLUMEN)
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


# ----------------------------------------------------------------------
# Música de la partida: lista de temas que suenan uno detrás de otro (settings.MUSICA_PARTIDA)
# ----------------------------------------------------------------------
_partida = False       # True mientras la lista está sonando
_pista = 0             # índice del tema actual
_pausada = False


def _tocar_pista():
    """Carga y reproduce (una sola vez) el tema `_pista` de la lista."""
    global _partida
    archivo, volumen = MUSICA_PARTIDA[_pista % len(MUSICA_PARTIDA)]
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(os.path.join(ASSETS, archivo))
        _volumen(volumen)
        pygame.mixer.music.play()
    except (pygame.error, FileNotFoundError, OSError) as e:
        print(f"[musica] No se pudo reproducir '{archivo}': {e}")
        _partida = False               # sin música (y no reintenta en cada cuadro)


def partida_iniciar():
    """Arranca la lista desde el primer tema."""
    global _partida, _pista, _pausada
    if not MUSICA_PARTIDA:
        return
    _partida, _pista, _pausada = True, 0, False
    _tocar_pista()


def partida_actualizar():
    """Llamar en cada cuadro: cuando un tema termina, arranca el siguiente (y vuelve al primero al final)."""
    global _pista
    if not _partida or _pausada:
        return
    try:
        if not pygame.mixer.music.get_busy():
            _pista += 1
            _tocar_pista()
    except pygame.error:
        pass


def partida_pausar(pausado):
    """Pausa o reanuda el tema que está sonando."""
    global _pausada
    if not _partida or pausado == _pausada:
        return
    _pausada = pausado
    try:
        pygame.mixer.music.pause() if pausado else pygame.mixer.music.unpause()
    except pygame.error:
        pass


def partida_parar(ms=800):
    """Termina la música de la partida con un fundido."""
    global _partida, _pausada
    if not _partida:
        return
    _partida, _pausada = False, False
    try:
        pygame.mixer.music.fadeout(ms)
    except pygame.error:
        pass
