"""
Efectos de sonido. Los archivos están en assets/sonidos/.

Uso:  from ui import sonidos
      sonidos.reproducir("disparo")

Igual que la música: si no hay placa de sonido o falta un archivo, el juego sigue en silencio
(los errores se capturan). Cada efecto se carga una sola vez y se guarda en memoria.
"""
import os
import time
import pygame
from settings import SFX_VOLUMEN, SFX_VOLUMENES, SFX_ESPERA

CARPETA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sonidos")

# nombre del efecto -> archivo
ARCHIVOS = {
    "carne": "carne.mp3",                  # juntar un dedo de energía
    "disparo": "disparo.mp3",              # Stan tira la bola / Kyle patea a Ike
    "impacto": "impacto.mp3",              # un proyectil golpea a un zombie
    "explosion": "explosion.mp3",          # Kenny explota
    "kenny": "kenny.mp3",                  # grito de Kenny (suena junto con la explosión)
    "hipnosis": "hipnosis.mp3",            # un zombie se come a Toallin
    "iman": "iman.mp3",                    # el Imán le roba el balde al zombie
    "timmy": "timmy.mp3",                  # Timmy sale disparado
    "zombie_comiendo": "zombie_comiendo.mp3",   # un zombie empieza a comerse una planta
    "canto": "cartman_singa.ogg",          #Cartman
    "brains": "brains.mp3",                # un zombie dice "brains" cada tanto
    "ruido_zombie": "ruido_zombie.mp3",    # ruido de zombies de fondo, al azar
    "plantar": "plantar.mp3",              # plantar algo / sacar una planta con la pala
    "seleccionar": "seleccionar_personaje.mp3",   # clic en una carta de personaje
    "oleada": "oleada.mp3",                # cartel de oleada final
    "sirena": "sirena.mp3",                # llegan los zombies / después de oleada
    "hablar": "sans.mp3",                  # sonidito de cada letra cuando habla Bielsa (estilo Sans)
}

_cache = {}          # nombre -> pygame.mixer.Sound (o None si no se pudo cargar)
_ultimo = {}         # nombre -> última vez que sonó (para no apilar el mismo sonido)
_mixer_ok = None


def _mixer():
    global _mixer_ok
    if _mixer_ok is None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(24)       # muchos sonidos a la vez sin cortarse
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
                sonido.set_volume(SFX_VOLUMEN * SFX_VOLUMENES.get(nombre, 1.0))
            except (pygame.error, FileNotFoundError, OSError) as e:
                print(f"[sonidos] No se pudo cargar '{archivo}': {e}")
        _cache[nombre] = sonido
    return _cache[nombre]


def precargar():
    """Carga todos los efectos de una vez (se llama en la pantalla de carga)."""
    for nombre in ARCHIVOS:
        _cargar(nombre)


def reproducir(nombre):
    """Suena el efecto `nombre` una vez. No hace nada si no hay audio o el archivo falta."""
    try:
        sonido = _cargar(nombre)
        if sonido is None:
            return
        ahora = time.monotonic()
        # Evita que el mismo efecto se apile muchas veces en el mismo instante
        if ahora - _ultimo.get(nombre, -1e9) < SFX_ESPERA.get(nombre, 0.05):
            return
        _ultimo[nombre] = ahora
        sonido.play()
    except pygame.error:
        pass


def encadenar(primero, segundo):
    """Suena `primero` y, apenas termina, `segundo` (ej: oleada y después sirena)."""
    try:
        s1, s2 = _cargar(primero), _cargar(segundo)
        if s1 is None:
            reproducir(segundo)
            return
        canal = s1.play()
        if canal is not None and s2 is not None:
            canal.queue(s2)          # arranca solo cuando el primero termina
    except pygame.error:
        pass


_canal_canto = None

def canto(activo):
    """True enciende la canción en bucle; False la apaga."""
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
    """True enciende el ruido de masticar en bucle (si no está sonando); False lo apaga."""
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


def pausar(pausado):
    try:
        for canal in (_canal_canto, _canal_mastica):
            if canal is not None:
                canal.pause() if pausado else canal.unpause()
    except pygame.error:
        pass