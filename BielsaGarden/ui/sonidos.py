import os
import time
import pygame
from settings import SFX_VOLUMEN, SFX_VOLUMENES, SFX_ESPERA
from ui import audio

CARPETA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sonidos")

ARCHIVOS = {
    "carne": "carne.mp3",
    "disparo": "disparo.mp3",
    "impacto": "impacto.mp3",
    "explosion": "explosion.mp3",
    "kenny": "kenny.mp3",
    "hipnosis": "hipnosis.mp3",
    "iman": "iman.mp3",
    "timmy": "timmy.mp3",
    "zombie_comiendo": "zombie_comiendo.mp3",
    "canto": "cartman_singa.ogg",
    "brains": "brains.mp3",
    "ruido_zombie": "ruido_zombie.mp3",
    "plantar": "plantar.mp3",
    "seleccionar": "seleccionar_personaje.mp3",
    "oleada": "oleada.mp3",
    "sirena": "sirena.mp3",
    "delfin": "delfin.mp3",
    "crab_people": "crab_people.mp3",
    "gero_hmm": "hmm.mp3",
    "gero_impacto": "impacto_fuerte.mp3",
    "murcielago_impacto": "impacto_fuerte.mp3",
    "srnelson": "srnelson.mp3",
    "randy_cae": "yeehaw.mp3",
    "minando": "minando.mp3",
    "pip_sale": "saliendo_de_la_tierra.mp3",
    "hablar": "sans.mp3",
}

CATEGORIA = {
    "disparo": "personajes", "kenny": "personajes", "hipnosis": "personajes", "iman": "personajes",
    "timmy": "personajes", "canto": "personajes", "hablar": "personajes",
    "gero_hmm": "personajes", "gero_impacto": "personajes",
    "crab_people": "enemigos", "murcielago_impacto": "enemigos", "srnelson": "enemigos",
    "randy_cae": "enemigos", "minando": "enemigos", "pip_sale": "enemigos",
    "delfin": "enemigos", "zombie_comiendo": "enemigos", "brains": "enemigos", "ruido_zombie": "enemigos",
}

_cache = {}
_ultimo = {}
_mixer_ok = None


def _mixer():
    global _mixer_ok
    if _mixer_ok is None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(24)
            _mixer_ok = True
        except pygame.error as e:
            print(f"[sonidos] Sin audio: {e}")
            _mixer_ok = False
    return _mixer_ok


def _cargar(nombre):
    if nombre not in _cache:
        sonido = None
        archivo = ARCHIVOS.get(nombre)
        if archivo and _mixer():
            try:
                sonido = pygame.mixer.Sound(os.path.join(CARPETA, archivo))
                sonido.set_volume(_volumen(nombre))
            except (pygame.error, FileNotFoundError, OSError) as e:
                print(f"[sonidos] No se pudo cargar '{archivo}': {e}")
        _cache[nombre] = sonido
    return _cache[nombre]


def _volumen(nombre):
    return SFX_VOLUMEN * SFX_VOLUMENES.get(nombre, 1.0) * audio.factor(CATEGORIA.get(nombre, "efectos"))


def aplicar_volumen():
    for nombre, sonido in _cache.items():
        if sonido is not None:
            try:
                sonido.set_volume(_volumen(nombre))
            except pygame.error:
                pass


def precargar():
    for nombre in ARCHIVOS:
        _cargar(nombre)


def reproducir(nombre):
    try:
        sonido = _cargar(nombre)
        if sonido is None:
            return
        ahora = time.monotonic()
        if ahora - _ultimo.get(nombre, -1e9) < SFX_ESPERA.get(nombre, 0.05):
            return
        _ultimo[nombre] = ahora
        sonido.play()
    except pygame.error:
        pass


def encadenar(primero, segundo):
    try:
        s1, s2 = _cargar(primero), _cargar(segundo)
        if s1 is None:
            reproducir(segundo)
            return
        canal = s1.play()
        if canal is not None and s2 is not None:
            canal.queue(s2)
    except pygame.error:
        pass


_canal_canto = None

def canto(activo):
    global _canal_canto
    try:
        if activo:
            if _canal_canto is None or not _canal_canto.get_busy():
                s = _cargar("canto")
                if s is not None:
                    _canal_canto = s.play(loops=-1)
        elif _canal_canto is not None:
            if _canal_canto.get_busy():
                _canal_canto.fadeout(300)
            _canal_canto = None
    except pygame.error:
        _canal_canto = None

_canal_mastica = None


def masticar(activo):
    global _canal_mastica
    try:
        if activo:
            if _canal_mastica is None or not _canal_mastica.get_busy():
                s = _cargar("zombie_comiendo")
                if s is not None:
                    _canal_mastica = s.play(loops=-1)
        elif _canal_mastica is not None:
            if _canal_mastica.get_busy():
                _canal_mastica.fadeout(250)
            _canal_mastica = None
    except pygame.error:
        _canal_mastica = None


_canal_minando = None


def minando(activo):
    global _canal_minando
    try:
        if activo:
            if _canal_minando is None or not _canal_minando.get_busy():
                s = _cargar("minando")
                if s is not None:
                    _canal_minando = s.play(loops=-1)
        elif _canal_minando is not None:
            if _canal_minando.get_busy():
                _canal_minando.fadeout(150)
            _canal_minando = None
    except pygame.error:
        _canal_minando = None


def pausar(pausado):
    try:
        for canal in (_canal_canto, _canal_mastica, _canal_minando):
            if canal is not None:
                canal.pause() if pausado else canal.unpause()
    except pygame.error:
        pass
