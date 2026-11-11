import os
import pygame
from settings import MUSICA_MENU, MUSICA_VOLUMEN, MUSICA_PARTIDA, MUSICA_VICTORIA, MUSICA_DERROTA, MUSICA_FINAL
from ui import audio

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
RUTA = os.path.join(ASSETS, MUSICA_MENU)
_ok = None
_desde = 0.0
_base = MUSICA_VOLUMEN
_actual = None


def _volumen(base):
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
        return disponible() and _actual == "menu" and pygame.mixer.music.get_busy()
    except pygame.error:
        return False


def reproducir(desde=0.0):
    if not disponible():
        return False
    global _desde, _actual
    try:
        pygame.mixer.music.load(RUTA)
        _actual = "menu"
        _volumen(MUSICA_VOLUMEN)
        try:
            pygame.mixer.music.play(loops=-1, start=desde)
            _desde = desde
        except pygame.error:
            pygame.mixer.music.play(loops=-1)
            _desde = 0.0
        return True
    except pygame.error as e:
        print(f"[musica] No se pudo reproducir: {e}")
        return False


def posicion():
    try:
        if disponible() and pygame.mixer.music.get_busy():
            ms = pygame.mixer.music.get_pos()
            if ms >= 0:
                return ms / 1000.0
    except pygame.error:
        pass
    return None


def tiempo():
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


_partida = False
_pista = 0
_pausada = False


def _tocar_pista():
    global _partida, _actual
    archivo, volumen = MUSICA_PARTIDA[_pista % len(MUSICA_PARTIDA)]
    _actual = "partida"
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(os.path.join(ASSETS, archivo))
        _volumen(volumen)
        pygame.mixer.music.play()
    except (pygame.error, FileNotFoundError, OSError) as e:
        print(f"[musica] No se pudo reproducir '{archivo}': {e}")
        _partida = False


def partida_iniciar():
    global _partida, _pista, _pausada
    if not MUSICA_PARTIDA:
        return
    _partida, _pista, _pausada = True, 0, False
    _tocar_pista()


def partida_actualizar():
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
    global _pausada
    if not _partida or pausado == _pausada:
        return
    _pausada = pausado
    try:
        pygame.mixer.music.pause() if pausado else pygame.mixer.music.unpause()
    except pygame.error:
        pass


def partida_parar(ms=800):
    global _partida, _pausada
    if not _partida:
        return
    _partida, _pausada = False, False
    try:
        pygame.mixer.music.fadeout(ms)
    except pygame.error:
        pass


def _jingle(tema, bucle):
    global _partida, _pausada, _actual
    archivo, volumen = tema
    _partida, _pausada = False, False
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(os.path.join(ASSETS, archivo))
        _volumen(volumen)
        pygame.mixer.music.play(loops=-1 if bucle else 0)
        _actual = "jingle"
    except (pygame.error, FileNotFoundError, OSError) as e:
        print(f"[musica] No se pudo reproducir '{archivo}': {e}")


def victoria():
    _jingle(MUSICA_VICTORIA, True)


def final():
    _jingle(MUSICA_FINAL, True)


def derrota():
    _jingle(MUSICA_DERROTA, False)
