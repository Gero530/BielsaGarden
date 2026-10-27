"""
Carga de sprites (tiras horizontales de frames hechas en LibreSprite).

Para sumar un sprite nuevo, agregá una entrada en SPRITES:
    "clave": {"archivo": "carpeta/archivo.png", "frame_w": 40, "frame_h": 48, "fps": 8}

- frame_w / frame_h: tamaño de UN frame en el PNG (tamaño de dibujo, sin escalar).
- fps: velocidad de la animación.
- "loop": False  -> la animación se reproduce una vez y queda en el último frame
  (se usa para animaciones de acción, como el disparo).
- "seq": orden en que se muestran los frames (ej: [0,0,1,1,0,2] repite el 0 y el 1 para
  que esa parte dure más, y muestra el 2 una sola vez, como un parpadeo). Sin "seq" se
  van mostrando en orden.
- "frames": lista de índices de la tira que forman esta animación (ej: [2,3,4,5,6]).
  Sirve para sacar varias animaciones de un mismo PNG sin cortarlo en archivos.
- "dx": corrimiento horizontal en píxeles de DIBUJO (se escala igual que el sprite). Sirve
  para centrar en la casilla a un personaje que quedó corrido dentro de su frame.
- "mult": multiplica la escala de ESE sprite (1.5 -> x3 en pantalla en vez de x2).
  Agranda el dibujo por un entero exacto, sin deformarlo.
- "dy_px": desplaza el sprite hacia abajo (en píxeles de pantalla) para que los pies
  queden a la altura de los de otros sprites más altos (ej: Cartman vs. lanzaguisantes).
- "icon_dy": igual que dy_px pero para los íconos chicos de las cartas.
- Los sprites se escalan x2 (ESCALA_BASE) con vecino más cercano para que el
  pixel art quede nítido.
- Si el archivo no existe, el juego sigue usando el dibujo con formas.
"""
import os
import pygame

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
ESCALA_BASE = 2   # 1 px dibujado = 2 px en pantalla

SPRITES = {
    # Plantas (frames de 40x48)
    "girasol":                {"archivo": "plantas/cartman_cocinando.png",     "frame_w": 32, "frame_h": 24, "fps": 6, "mult": 1.5, "dy_px": 13},   # Cartman cocinando chili (generador de soles)
    "lanzaguisantes":         {"archivo": "plantas/cartman_idle.png",         "frame_w": 26, "frame_h": 24, "fps": 4, "seq": [0, 0, 1, 1, 0, 0, 1, 1, 0, 2, 1, 1], "mult": 1.5, "dy_px": 13},
    "lanzaguisantes_disparo": {"archivo": "plantas/cartman_disparo.png", "frame_w": 26, "frame_h": 24, "fps": 8, "loop": False, "mult": 1.5, "dy_px": 13},
    # Kyle (catapulta). kyle_completo.png: 0-1 de frente, 2 de perfil quieto, 3-6 patada
    "kyle":                   {"archivo": "plantas/kyle_idle.png",             "frame_w": 38, "frame_h": 38, "fps": 4, "seq": [0, 0, 1, 1, 0, 0, 1, 1, 0, 2, 1, 1], "dx": 6.5, "mult": 1.5, "dy_px": 22, "icon_dy": 6},
    "kyle_perfil":            {"archivo": "plantas/kyle_completo.png",         "frame_w": 38, "frame_h": 38, "fps": 1, "frames": [2], "dx": 6.5, "mult": 1.5, "dy_px": 22},
    "kyle_patada":            {"archivo": "plantas/kyle_completo.png",         "frame_w": 38, "frame_h": 38, "fps": 8, "frames": [2, 3, 4, 5, 6], "dx": 6.5, "loop": False, "mult": 1.5, "dy_px": 22},
    # Kenny (bomba). kenny_explosion.png: 0-4 se infla y explota, 5-29 restos + ratas
    "kenny":                  {"archivo": "plantas/kenny_explosion.png",       "frame_w": 32, "frame_h": 32, "fps": 10, "frames": [0, 1, 2, 3, 4], "loop": False, "mult": 1.5, "dy_px": 19, "icon_dy": 4},
    "kenny_ratas":            {"archivo": "plantas/kenny_explosion.png",       "frame_w": 32, "frame_h": 32, "fps": 12, "frames": list(range(5, 30)), "loop": False, "mult": 1.5, "dy_px": 19},
    # Toallin (hipnoseta)
    "toallin":                {"archivo": "plantas/toallin_idle.png",          "frame_w": 32, "frame_h": 32, "fps": 4, "dx": 2, "mult": 1.5, "dy_px": 7, "icon_dy": -4},
    "nuez":                   {"archivo": "plantas/nuez_idle.png",              "frame_w": 40, "frame_h": 48, "fps": 6},
    "nuez_agrietada":         {"archivo": "plantas/nuez_agrietada.png",         "frame_w": 40, "frame_h": 48, "fps": 6},
    "nuez_mordida":           {"archivo": "plantas/nuez_mordida.png",           "frame_w": 40, "frame_h": 48, "fps": 6},
    # Zombies (frames de 32x48, mirando a la izquierda, pies en el borde inferior)
    "zombie_normal":          {"archivo": "zombies/zombie_normal_caminar.png",  "frame_w": 32, "frame_h": 48, "fps": 6},
    # Unidad de energía: el dedo con resplandor (reemplaza al sol)
    "dedo":                   {"archivo": "soles/dedo_energia.png",            "frame_w": 32, "frame_h": 32, "fps": 4, "mult": 1.5},
    # Proyectiles. ike_volando.png: 0 de frente, 1 salida, 2 inclinado, 3-5 girando, 6 cayendo
    "ike":                    {"archivo": "proyectiles/ike_volando.png",        "frame_w": 38, "frame_h": 38, "fps": 1, "mult": 1.5},
    "guisante":               {"archivo": "proyectiles/guisante.png",           "frame_w": 40, "frame_h": 48, "fps": 1},
}

_cache = {}   # (clave, factor) -> lista de frames escalados


def _load_frames(key):
    """Corta la tira en frames sin escalar. Devuelve None si no hay archivo."""
    cfg = SPRITES.get(key)
    if cfg is None:
        return None
    path = os.path.join(ASSETS_DIR, cfg["archivo"])
    if not os.path.exists(path):
        print(f"[sprites] No se encontró {path}; se usa el dibujo por defecto.")
        SPRITES.pop(key)
        return None
    sheet = pygame.image.load(path).convert_alpha()
    fw, fh = cfg["frame_w"], cfg["frame_h"]
    n = max(1, sheet.get_width() // fw)
    frames = [sheet.subsurface((i * fw, 0, fw, fh)).copy() for i in range(n)]
    if cfg.get("frames"):
        frames = [frames[i] for i in cfg["frames"] if i < len(frames)]
    return frames


def get_frames(key, factor):
    """Frames de `key` escalados por un factor entero (1 = tamaño de dibujo)."""
    if key not in SPRITES:
        return None
    ck = (key, factor)
    if ck not in _cache:
        base = _cache.get((key, 1)) or _load_frames(key)
        if base is None:
            return None
        _cache[(key, 1)] = base
        if factor != 1:
            _cache[ck] = [pygame.transform.scale(f, (f.get_width() * factor, f.get_height() * factor)) for f in base]
    return _cache[ck]


def has_sprite(key):
    return key in SPRITES and get_frames(key, 1) is not None


def anim_duration(key):
    """Duración en segundos de una pasada completa de la animación."""
    frames = get_frames(key, 1)
    if not frames:
        return 0.0
    return len(frames) / SPRITES[key]["fps"]


def frame_index(key, t):
    frames = get_frames(key, 1)
    if not frames or t is None:
        return 0
    i = int(t * SPRITES[key]["fps"])
    seq = SPRITES[key].get("seq")
    if seq:
        return seq[i % len(seq)] % len(frames)
    if SPRITES[key].get("loop", True):
        return i % len(frames)
    return min(i, len(frames) - 1)


_variantes = {}   # (clave, factor, frame, espejo, tinte) -> imagen modificada


def draw_sprite(surface, key, center, scale=1.0, t=None, flash=False, frame=None, flip=False, tint=None):
    """
    Dibuja el sprite centrado en `center`.
    scale=1.0 -> tamaño de juego (x2). Se redondea a un múltiplo entero del
    tamaño de dibujo para que los píxeles no se deformen.
    t: tiempo en segundos para elegir el frame; None = primer frame (íconos).
    frame: número de frame fijo (ignora t). Se usa cuando el código elige la pose.
    flip: espeja el sprite horizontalmente.
    tint: color (r, g, b) que se multiplica sobre el sprite (ej: violeta para hipnotizados).
    flash: aclara el sprite (cuando recibe daño).
    Devuelve False si no hay sprite para esa clave.
    """
    factor = max(1, round(scale * ESCALA_BASE * SPRITES.get(key, {}).get("mult", 1.0)))
    frames = get_frames(key, factor)
    if not frames:
        return False
    idx = frame_index(key, t) if frame is None else min(frame, len(frames) - 1)
    img = frames[idx]
    if flip or tint:
        vk = (key, factor, idx, flip, tint)
        if vk not in _variantes:
            v = pygame.transform.flip(img, True, False) if flip else img.copy()
            if tint:
                v.fill((*tint, 255), special_flags=pygame.BLEND_RGBA_MULT)
            _variantes[vk] = v
        img = _variantes[vk]
    if flash:
        img = img.copy()
        img.fill((90, 90, 90, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # dy_px solo vale al tamaño de juego; en los íconos chicos (cartas) el sprite va centrado
    cfg = SPRITES[key]
    en_juego = factor == round(ESCALA_BASE * cfg.get("mult", 1.0))
    dy = cfg.get("dy_px", 0) if en_juego else cfg.get("icon_dy", 0)
    dx = round(cfg.get("dx", 0) * factor)
    surface.blit(img, img.get_rect(center=(center[0] + dx, center[1] + dy)))
    return True
