import json
import os
import sys
import pygame
from settings import SCREEN_W, SCREEN_H

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

RESOLUCIONES = [
    (1000, 600),
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
    (2560, 1440),
]

DEFAULT_CONFIG = {"resolucion": [SCREEN_W, SCREEN_H], "pantalla_completa": False}

config = dict(DEFAULT_CONFIG)

_window = None
_view = pygame.Rect(0, 0, SCREEN_W, SCREEN_H)


def load_config():
    config.clear()
    config.update(DEFAULT_CONFIG)
    data = leer_config_json()
    res = data.get("resolucion")
    if isinstance(res, list) and len(res) == 2 and tuple(res) in RESOLUCIONES:
        config["resolucion"] = list(res)
    config["pantalla_completa"] = bool(data.get("pantalla_completa", False))
    return config


def save_config():
    escribir_config_json(config)


def leer_config_json():
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def escribir_config_json(cambios):
    data = leer_config_json()
    data.update(cambios)
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"[display] No se pudo guardar la configuración: {e}")


def available_resolutions():
    try:
        dw, dh = pygame.display.get_desktop_sizes()[0]
    except (pygame.error, IndexError):
        return list(RESOLUCIONES)
    ok = [r for r in RESOLUCIONES if r[0] < dw and r[1] < dh]
    return ok if RESOLUCIONES[0] in ok else [RESOLUCIONES[0]] + ok


def enable_dpi_awareness():
    if sys.platform != "win32":
        return
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def apply():
    global _window, _view
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    if config["pantalla_completa"]:
        _window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        res = tuple(config["resolucion"])
        if res not in available_resolutions():
            res = RESOLUCIONES[0]
            config["resolucion"] = list(res)
        _window = pygame.display.set_mode(res)

    ww, wh = _window.get_size()
    scale = min(ww / SCREEN_W, wh / SCREEN_H)
    w, h = int(SCREEN_W * scale), int(SCREEN_H * scale)
    _view = pygame.Rect((ww - w) // 2, (wh - h) // 2, w, h)
    return _window


def present(screen):
    if _view.size == (SCREEN_W, SCREEN_H) and _view.topleft == (0, 0):
        _window.blit(screen, (0, 0))
    else:
        _window.fill((0, 0, 0))
        _window.blit(pygame.transform.scale(screen, _view.size), _view.topleft)
    pygame.display.flip()


def to_logical(pos):
    x = (pos[0] - _view.x) * SCREEN_W / _view.w
    y = (pos[1] - _view.y) * SCREEN_H / _view.h
    return int(x), int(y)


def get_mouse_pos():
    return to_logical(pygame.mouse.get_pos())


def convert_event(event):
    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
        data = dict(event.dict)
        data["pos"] = to_logical(event.pos)
        return pygame.event.Event(event.type, data)
    return event
