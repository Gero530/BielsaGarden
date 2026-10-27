"""Caché de fuentes para no crearlas en cada frame."""
import pygame

_cache = {}


def get_font(size, bold=False):
    key = (size, bold)
    if key not in _cache:
        _cache[key] = pygame.font.SysFont(None, size, bold=bold)
    return _cache[key]


def draw_text(surface, text, size, color, center=None, topleft=None, bold=False):
    img = get_font(size, bold).render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = center
    elif topleft:
        rect.topleft = topleft
    surface.blit(img, rect)
    return rect
