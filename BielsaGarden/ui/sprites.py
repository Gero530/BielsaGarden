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
- "icono": qué frame usar como imagen fija en la carta del HUD y en el catálogo (por defecto el 0).
- Los sprites se escalan x2 (ESCALA_BASE) con vecino más cercano para que el
  pixel art quede nítido.
- Si el archivo no existe, el juego sigue usando el dibujo con formas.
"""
from operator import ge
import os
import pygame

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
ESCALA_BASE = 2   # 1 px dibujado = 2 px en pantalla

SPRITES = {
    # Plantas (frames de 40x48)
    "girasol":                {"archivo": "plantas/cartman_cocinando.png",     "frame_w": 32, "frame_h": 24, "fps": 6, "mult": 1.5, "dy_px": 13},   # Cartman cocinando chili (generador de soles)
    # Stan (lanzaguisantes de nieve). stan_disparo.png: 0-1 prepara la bola, 2 gira, 3 la tira.
    # En el frame 3 se borró la bola (la dibuja el proyectil); la original está en stan_disparo_original.png
    "lanzaguisantes":         {"archivo": "plantas/stan_idle.png",             "frame_w": 40, "frame_h": 40, "fps": 4, "seq": [0, 0, 1, 1, 0, 0, 1, 1, 0, 2, 1, 1], "mult": 1.5, "dy_px": 4, "icon_dy": -4},
    "lanzaguisantes_alerta":  {"archivo": "plantas/stan_disparo.png",          "frame_w": 40, "frame_h": 40, "fps": 1, "frames": [0], "mult": 1.5, "dy_px": 7},
    "lanzaguisantes_disparo": {"archivo": "plantas/stan_disparo.png",          "frame_w": 40, "frame_h": 40, "fps": 8, "loop": False, "mult": 1.5, "dy_px": 7},
    # Kyle (catapulta). kyle_completo.png: 0-1 de frente, 2 de perfil quieto, 3-6 patada
    "kyle":                   {"archivo": "plantas/kyle_idle.png",             "frame_w": 38, "frame_h": 38, "fps": 4, "seq": [0, 0, 1, 1, 0, 0, 1, 1, 0, 2, 1, 1], "dx": 6.5, "mult": 1.5, "dy_px": 22, "icon_dy": 6},
    "kyle_perfil":            {"archivo": "plantas/kyle_completo.png",         "frame_w": 38, "frame_h": 38, "fps": 1, "frames": [2], "dx": 6.5, "mult": 1.5, "dy_px": 22},
    "kyle_patada":            {"archivo": "plantas/kyle_completo.png",         "frame_w": 38, "frame_h": 38, "fps": 8, "frames": [2, 3, 4, 5, 6], "dx": 6.5, "loop": False, "mult": 1.5, "dy_px": 22},
    # Kenny (bomba). kenny_explosion.png: 0-4 se infla y explota, 5-29 restos + ratas
    "kenny":                  {"archivo": "plantas/kenny_explosion.png",       "frame_w": 32, "frame_h": 32, "fps": 10, "frames": [0, 1, 2, 3, 4], "loop": False, "mult": 1.5, "dy_px": 19, "icon_dy": 4},
    "kenny_ratas":            {"archivo": "plantas/kenny_explosion.png",       "frame_w": 32, "frame_h": 32, "fps": 12, "frames": list(range(5, 30)), "loop": False, "mult": 1.5, "dy_px": 19},
    # Toallin (hipnoseta)
    "toallin":                {"archivo": "plantas/toallin_idle.png",          "frame_w": 32, "frame_h": 32, "fps": 4, "dx": 2, "mult": 1.5, "dy_px": 7, "icon_dy": -4},
    # Butters (nuez). Quieto mientras nadie lo toca; llora cuando lo están mordiendo
    "nuez":                   {"archivo": "plantas/butters_idle.png",          "frame_w": 40, "frame_h": 40, "fps": 2, "seq": [0, 0, 0, 1], "mult": 1.5, "dy_px": 7, "icon_dy": -3},
    "nuez_comido":            {"archivo": "plantas/butters_comido.png",        "frame_w": 40, "frame_h": 40, "fps": 8, "dx": 2, "mult": 1.5, "dy_px": -5},
    # Zombies propios (assets/zombies/propios/), dibujados a mano en el estilo del alien.
    # Los genera tools/zombies_disenos.py (no pisa tus retoques salvo con --forzar).
    # Respaldo: los vecinos anteriores siguen en assets/sprites/vecinos/ y assets/zombies/zombie_normal_*.png.
    # Caminar: 8 frames; atacar: 6 frames (se tira adelante, abre la boca, muerde, mastica, vuelve).
    # "dx": la pértiga usa un frame más ancho (la garrocha asoma adelante); dx deja el cuerpo
    # en el mismo lugar que el de los demás.
    "zombie_normal":               {"archivo": "zombies/propios/zombie_normal_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_normal_atacar":        {"archivo": "zombies/propios/zombie_normal_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "zombie_puerta":               {"archivo": "zombies/propios/zombie_puerta_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_puerta_atacar":        {"archivo": "zombies/propios/zombie_puerta_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "zombie_puerta_sin":           {"archivo": "zombies/propios/zombie_puerta_sin_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_puerta_sin_atacar":    {"archivo": "zombies/propios/zombie_puerta_sin_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "zombie_diario":               {"archivo": "zombies/propios/zombie_diario_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_diario_atacar":        {"archivo": "zombies/propios/zombie_diario_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "zombie_diario_enojado":       {"archivo": "zombies/propios/zombie_diario_enojado_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 12},
    "zombie_diario_enojado_atacar": {"archivo": "zombies/propios/zombie_diario_enojado_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 12},
    "zombie_escalera":             {"archivo": "zombies/propios/zombie_escalera_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_escalera_atacar":      {"archivo": "zombies/propios/zombie_escalera_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "zombie_escalera_colocar":     {"archivo": "zombies/propios/zombie_escalera_colocar.png", "frame_w": 31, "frame_h": 48, "fps": 6, "loop": False},
    "zombie_escalera_sin":         {"archivo": "zombies/propios/zombie_escalera_sin_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_escalera_sin_atacar":  {"archivo": "zombies/propios/zombie_escalera_sin_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "zombie_pertiga":              {"archivo": "zombies/propios/zombie_pertiga_caminar.png", "frame_w": 48, "frame_h": 48, "fps": 10, "dx": -8.5},
    "zombie_pertiga_atacar":       {"archivo": "zombies/propios/zombie_pertiga_atacar.png", "frame_w": 48, "frame_h": 48, "fps": 10, "dx": -8.5},
    "zombie_pertiga_salto":        {"archivo": "zombies/propios/zombie_pertiga_salto.png", "frame_w": 48, "frame_h": 48, "fps": 7, "dx": -8.5, "loop": False},
    "zombie_pertiga_sin":          {"archivo": "zombies/propios/zombie_pertiga_sin_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_pertiga_sin_atacar":   {"archivo": "zombies/propios/zombie_pertiga_sin_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "zombie_excavador":            {"archivo": "zombies/propios/zombie_excavador_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_excavador_atacar":     {"archivo": "zombies/propios/zombie_excavador_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "zombie_excavador_sin":        {"archivo": "zombies/propios/zombie_excavador_sin_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_excavador_sin_atacar": {"archivo": "zombies/propios/zombie_excavador_sin_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "zombie_excavador_tierra":     {"archivo": "zombies/propios/zombie_excavador_tierra.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_bailarin":             {"archivo": "zombies/propios/zombie_bailarin_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_bailarin_atacar":      {"archivo": "zombies/propios/zombie_bailarin_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "zombie_bailarin_baile":       {"archivo": "zombies/propios/zombie_bailarin_baile.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_bungee":               {"archivo": "zombies/propios/zombie_bungee_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_bungee_atacar":        {"archivo": "zombies/propios/zombie_bungee_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "zombie_bungee_bajar":         {"archivo": "zombies/propios/zombie_bungee_bajar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_mini":                 {"archivo": "zombies/propios/zombie_mini_caminar.png", "frame_w": 20, "frame_h": 32, "fps": 10},
    "zombie_mini_atacar":          {"archivo": "zombies/propios/zombie_mini_atacar.png", "frame_w": 20, "frame_h": 32, "fps": 12},
    "zombie_gigante":              {"archivo": "zombies/propios/zombie_gigante_caminar.png", "frame_w": 44, "frame_h": 64, "fps": 6},
    "zombie_gigante_sin":          {"archivo": "zombies/propios/zombie_gigante_sin_caminar.png", "frame_w": 44, "frame_h": 64, "fps": 6},
    "zombie_gigante_golpe":        {"archivo": "zombies/propios/zombie_gigante_golpe.png", "frame_w": 44, "frame_h": 64, "fps": 6, "loop": False},
    "zombie_gigante_golpe_sin":    {"archivo": "zombies/propios/zombie_gigante_golpe_sin.png", "frame_w": 44, "frame_h": 64, "fps": 6, "loop": False},
    "zombie_gigante_lanzar":       {"archivo": "zombies/propios/zombie_gigante_lanzar.png", "frame_w": 44, "frame_h": 64, "fps": 8, "loop": False},
    "zombie_tractor":              {"archivo": "zombies/propios/zombie_tractor_caminar.png", "frame_w": 56, "frame_h": 48, "fps": 10},
    "zombie_tractor_atacar":       {"archivo": "zombies/propios/zombie_tractor_atacar.png", "frame_w": 56, "frame_h": 48, "fps": 12},
    # Alien y Cartman con la sonda (de Santi)
    "alien":                 {"archivo": "zombies/alien_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 6},
    "alien_boton":           {"archivo": "zombies/alien_boton.png",   "frame_w": 31, "frame_h": 48, "fps": 6, "loop": False},
    "alien_atacar":          {"archivo": "zombies/propios/alien_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},   # hecho a partir del dibujo de Santi
    "girasol_sonda":         {"archivo": "plantas/cartman_sonda.png", "frame_w": 32, "frame_h": 24, "fps": 10, "loop": False, "mult": 1.5, "dy_px": 13},
    "girasol_deshabilitado": {"archivo": "plantas/cartman_deshabilitado.png", "frame_w": 32, "frame_h": 24, "fps": 6, "mult": 1.5, "dy_px": 13},
    "cartman_baile":         {"archivo": "plantas/cartman_baile.png", "frame_w": 32, "frame_h": 32, "fps": 6, "mult": 1.5},
    # Imán (como el Magnetoseta). iman_completo.png: 0-2 reposo (2 = brillito, 1 = parpadeo),
    # 3-5 atrae (sale el campo magnético), 6-8 con el balde pegado, cada vez más deshecho
    "iman":                   {"archivo": "plantas/iman_completo.png",         "frame_w": 40, "frame_h": 40, "fps": 4, "frames": [0, 1, 2], "seq": [0, 0, 0, 0, 0, 2, 0, 0, 0, 1], "dx": -3, "mult": 1.5, "dy_px": 4, "icon_dy": -4},
    "iman_atrae":             {"archivo": "plantas/iman_completo.png",         "frame_w": 40, "frame_h": 40, "fps": 10, "frames": [3, 4, 5], "loop": False, "dx": -3, "mult": 1.5, "dy_px": 4},
    "iman_cargado":           {"archivo": "plantas/iman_completo.png",         "frame_w": 40, "frame_h": 40, "fps": 1, "frames": [6, 7, 8], "loop": False, "dx": -3, "mult": 1.5, "dy_px": 4},
    # Timmy (podadora). Por ahora un solo frame; el movimiento lo agrega world/lawnmower.py.
    # Si dibujás tiras animadas, cambiá "archivo" (y "fps") de estas dos claves.
    "podadora":               {"archivo": "podadora/timmy_idle.png",           "frame_w": 40, "frame_h": 40, "fps": 4, "mult": 1.5, "dy_px": 4},
    "podadora_activa":        {"archivo": "podadora/timmy_correr.png", "frame_w": 40, "frame_h": 40, "fps": 10, "mult": 1.5, "dy_px": 4},
    "podadora_grito":         {"archivo": "podadora/timmy_grito.png", "frame_w": 40, "frame_h": 40, "fps": 8, "loop": False, "mult": 1.5, "dy_px": 4},
    # Unidad de energía: el dedo con resplandor (reemplaza al sol)
    "dedo":                   {"archivo": "soles/dedo_energia.png",            "frame_w": 32, "frame_h": 32, "fps": 4, "mult": 1.5},
    # Proyectiles. ike_volando.png: 0 de frente, 1 salida, 2 inclinado, 3-5 girando, 6 cayendo
    "ike":                    {"archivo": "proyectiles/ike_volando.png",        "frame_w": 38, "frame_h": 38, "fps": 1, "mult": 1.5},
    "guisante":               {"archivo": "proyectiles/guisante.png",           "frame_w": 40, "frame_h": 48, "fps": 1},
    "bola_nieve":             {"archivo": "proyectiles/bola_nieve.png",         "frame_w": 6, "frame_h": 6, "fps": 1, "mult": 1.5},

    # ------------------------------------------------------------------
    # NUEVOS (placeholders de tools/generar_placeholders.py en assets/sprites/nuevos/).
    # Redibujalos en LibreSprite con el MISMO tamaño de frame y cantidad de frames.
    # Plantas: frames 40x40 que se ven x3 (mult 1.5). Zombies: frames 32x48 que se ven x2.
    # ------------------------------------------------------------------
    # Picante (Jesús): plantas/picante.png, 20 frames 40x40. 1-14 se enciende (~1 s), 15 aro,
    # 16-19 explosión (el daño en cruz sale en el 16), 20 humo.
    "picante":                {"archivo": "plantas/picante.png", "frame_w": 40, "frame_h": 40, "fps": 14, "frames": list(range(14)), "loop": False, "mult": 1.5, "dy_px": 4, "icon_dy": -4},
    "picante_explota":        {"archivo": "plantas/picante.png", "frame_w": 40, "frame_h": 40, "fps": 18, "frames": list(range(14, 20)), "loop": False, "mult": 1.5, "dy_px": 4},
    # Llamarada que se ve en cada casilla de la cruz: 6 frames 26x32 (x3 = una casilla)
    "picante_fuego":          {"archivo": "sprites/nuevos/picante_fuego.png",     "frame_w": 26, "frame_h": 32, "fps": 12, "loop": False, "mult": 1.5},
    # Aplastadora (Gero): quieta 4 frames en loop; salto 8 frames (1 quieto, 2-3 se agacha,
    # 4 salta, 5 en el aire, 6 cae, 7 aplasta, 8 se recupera; los elige el código); cansada 2 frames.
    "aplastadora":            {"archivo": "plantas/aplastadora_quieta.png",  "frame_w": 40, "frame_h": 40, "fps": 4, "mult": 1.5, "dy_px": 4, "icon_dy": -4},
    "aplastadora_salto":      {"archivo": "plantas/aplastadora_salto.png",   "frame_w": 40, "frame_h": 40, "fps": 1, "mult": 1.5, "dy_px": 4},
    "aplastadora_cansada":    {"archivo": "plantas/aplastadora_cansada.png", "frame_w": 40, "frame_h": 40, "fps": 2, "mult": 1.5, "dy_px": 4},
    # Cartman festejando en la pantalla de victoria: 4 frames 32x40 (salta con los brazos arriba)
    "cartman_festejo":        {"archivo": "sprites/nuevos/cartman_festejo.png",   "frame_w": 32, "frame_h": 40, "fps": 6, "mult": 1.5},
    # PC Principal: 2 frames 40x40 (respira)
    "principal":              {"archivo": "sprites/nuevos/principal.png",         "frame_w": 40, "frame_h": 40, "fps": 2, "mult": 1.5, "dy_px": 4, "icon_dy": -2},
    # Mr. Hankey: 2 frames 40x40, dibujado abajo del frame (va en el piso)
    "hankey":                 {"archivo": "sprites/nuevos/hankey.png",            "frame_w": 40, "frame_h": 40, "fps": 2, "mult": 1.5, "dy_px": 4, "icon_dy": -12},
    # Mr. Mackey: 6 frames 40x40 de charla (una sola vez); al terminar congela a los zombies
    "mackey":                 {"archivo": "sprites/nuevos/mackey.png",            "frame_w": 40, "frame_h": 40, "fps": 6, "loop": False, "mult": 1.5, "dy_px": 4, "icon_dy": -2},
    # Objetos y estados de zombies que siguen con el placeholder (assets/sprites/nuevos)
    "escalera":               {"archivo": "zombies/propios/escalera_puesta.png",      "frame_w": 20, "frame_h": 40, "fps": 1},   # 1 frame, apoyada sobre la planta
    "bungee_marca":           {"archivo": "sprites/nuevos/bungee_marca.png",          "frame_w": 24, "frame_h": 12, "fps": 4},   # 2 frames, aviso en el piso
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