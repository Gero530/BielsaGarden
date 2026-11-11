from operator import ge
import os
import pygame

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
ESCALA_BASE = 2

SPRITES = {
    "girasol":                {"archivo": "plantas/cartman_cocinando.png",     "frame_w": 32, "frame_h": 24, "fps": 6, "mult": 1.5, "dy_px": 13},
    "lanzaguisantes":         {"archivo": "plantas/stan_idle.png",             "frame_w": 40, "frame_h": 40, "fps": 4, "seq": [0, 0, 1, 1, 0, 0, 1, 1, 0, 2, 1, 1], "mult": 1.5, "dy_px": 4, "icon_dy": -4},
    "lanzaguisantes_alerta":  {"archivo": "plantas/stan_disparo.png",          "frame_w": 40, "frame_h": 40, "fps": 1, "frames": [0], "mult": 1.5, "dy_px": 7},
    "lanzaguisantes_disparo": {"archivo": "plantas/stan_disparo.png",          "frame_w": 40, "frame_h": 40, "fps": 8, "loop": False, "mult": 1.5, "dy_px": 7},
    "kyle":                   {"archivo": "plantas/kyle_idle.png",             "frame_w": 38, "frame_h": 38, "fps": 4, "seq": [0, 0, 1, 1, 0, 0, 1, 1, 0, 2, 1, 1], "dx": 6.5, "mult": 1.5, "dy_px": 22, "icon_dy": 6},
    "kyle_perfil":            {"archivo": "plantas/kyle_completo.png",         "frame_w": 38, "frame_h": 38, "fps": 1, "frames": [2], "dx": 6.5, "mult": 1.5, "dy_px": 22},
    "kyle_patada":            {"archivo": "plantas/kyle_completo.png",         "frame_w": 38, "frame_h": 38, "fps": 8, "frames": [2, 3, 4, 5, 6], "dx": 6.5, "loop": False, "mult": 1.5, "dy_px": 22},
    "kenny":                  {"archivo": "plantas/kenny_explosion.png",       "frame_w": 32, "frame_h": 32, "fps": 10, "frames": [0, 1, 2, 3, 4], "loop": False, "mult": 1.5, "dy_px": 19, "icon_dy": 4},
    "kenny_ratas":            {"archivo": "plantas/kenny_explosion.png",       "frame_w": 32, "frame_h": 32, "fps": 12, "frames": list(range(5, 30)), "loop": False, "mult": 1.5, "dy_px": 19},
    "toallin":                {"archivo": "plantas/toallin_idle.png",          "frame_w": 32, "frame_h": 32, "fps": 4, "dx": 2, "mult": 1.5, "dy_px": 7, "icon_dy": -4},
    "nuez":                   {"archivo": "plantas/butters_idle.png",          "frame_w": 40, "frame_h": 40, "fps": 2, "seq": [0, 0, 0, 1], "mult": 1.5, "dy_px": 7, "icon_dy": -3},
    "nuez_comido":            {"archivo": "plantas/butters_comido.png",        "frame_w": 40, "frame_h": 40, "fps": 8, "dx": 2, "mult": 1.5, "dy_px": -5},
    "zombie_normal":               {"archivo": "zombies/propios/zombie_normal_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_normal_atacar":        {"archivo": "zombies/propios/zombie_normal_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "terrance":                    {"archivo": "zombies/terrance_caminar.png", "frame_w": 17, "frame_h": 31, "fps": 6, "mult": 2.0},
    "terrance_atacar":             {"archivo": "zombies/terrance_caminar.png", "frame_w": 17, "frame_h": 31, "fps": 6, "mult": 2.0},
    "terrance_idle":               {"archivo": "zombies/terrance_idle.png",    "frame_w": 17, "frame_h": 31, "fps": 3, "mult": 2.0},
    "philip":                      {"archivo": "zombies/philip_caminar.png",   "frame_w": 17, "frame_h": 31, "fps": 6, "mult": 2.0},
    "philip_atacar":               {"archivo": "zombies/philip_caminar.png",   "frame_w": 17, "frame_h": 31, "fps": 6, "mult": 2.0},
    "philip_idle":                 {"archivo": "zombies/philip_idle.png",      "frame_w": 17, "frame_h": 31, "fps": 3, "mult": 2.0},
    "philip_sin":                  {"archivo": "zombies/philip_sin_caminar.png", "frame_w": 17, "frame_h": 31, "fps": 6, "mult": 2.0},
    "philip_sin_atacar":           {"archivo": "zombies/philip_sin_caminar.png", "frame_w": 17, "frame_h": 31, "fps": 6, "mult": 2.0},
    "philip_sin_idle":             {"archivo": "zombies/philip_sin_idle.png",  "frame_w": 17, "frame_h": 31, "fps": 3, "mult": 2.0},
    "chef_vader":              {"archivo": "zombies/chef_vader_caminar.png", "frame_w": 30, "frame_h": 46, "fps": 6, "mult": 1.5},
    "chef_vader_atacar":       {"archivo": "zombies/chef_vader_caminar.png", "frame_w": 30, "frame_h": 46, "fps": 6, "mult": 1.5},
    "chef_vader_idle":         {"archivo": "zombies/chef_vader_idle.png",    "frame_w": 30, "frame_h": 46, "fps": 3, "mult": 1.5},
    "chef_sin_casco":          {"archivo": "zombies/chef_sin_casco_caminar.png", "frame_w": 30, "frame_h": 46, "fps": 6, "mult": 1.5},
    "chef_sin_casco_atacar":   {"archivo": "zombies/chef_sin_casco_caminar.png", "frame_w": 30, "frame_h": 46, "fps": 6, "mult": 1.5},
    "chef_sin_casco_idle":     {"archivo": "zombies/chef_sin_casco_idle.png",    "frame_w": 30, "frame_h": 46, "fps": 3, "mult": 1.5},
    "chef_zombie":             {"archivo": "zombies/chef_zombie_caminar.png", "frame_w": 30, "frame_h": 46, "fps": 6, "mult": 1.5},
    "chef_zombie_atacar":      {"archivo": "zombies/chef_zombie_caminar.png", "frame_w": 30, "frame_h": 46, "fps": 6, "mult": 1.5},
    "chef_zombie_idle":        {"archivo": "zombies/chef_zombie_idle.png",    "frame_w": 30, "frame_h": 46, "fps": 3, "mult": 1.5},
    "cono_caido":                  {"archivo": "zombies/cono_caido.png", "frame_w": 8, "frame_h": 8, "fps": 1, "mult": 1.5},
    "zombie_puerta":               {"archivo": "zombies/propios/zombie_mickey_caminar.png", "frame_w": 56, "frame_h": 36, "fps": 8, "mult": 1.5},
    "zombie_puerta_atacar":        {"archivo": "zombies/propios/zombie_mickey_atacar.png", "frame_w": 56, "frame_h": 36, "fps": 10, "mult": 1.5},
    "zombie_puerta_sin":           {"archivo": "zombies/propios/zombie_mickey_sin_caminar.png", "frame_w": 56, "frame_h": 36, "fps": 8, "mult": 1.5},
    "zombie_puerta_sin_atacar":    {"archivo": "zombies/propios/zombie_mickey_sin_atacar.png", "frame_w": 56, "frame_h": 36, "fps": 10, "mult": 1.5},
    "pooh":                        {"archivo": "zombies/propios/pooh.png", "frame_w": 16, "frame_h": 24, "fps": 1},
    "gerald_idle":                 {"archivo": "zombies/gerald_idle.png", "frame_w": 40, "frame_h": 40, "fps": 2, "mult": 1.5},
    "zombie_diario":               {"archivo": "zombies/propios/zombie_diario_caminar.png", "frame_w": 32, "frame_h": 40, "fps": 6, "mult": 1.5},
    "zombie_diario_atacar":        {"archivo": "zombies/propios/zombie_diario_atacar.png", "frame_w": 32, "frame_h": 40, "fps": 8, "mult": 1.5},
    "zombie_diario_enojado":       {"archivo": "zombies/propios/zombie_diario_enojado_caminar.png", "frame_w": 32, "frame_h": 40, "fps": 12, "mult": 1.5},
    "zombie_diario_enojado_atacar": {"archivo": "zombies/propios/zombie_diario_enojado_atacar.png", "frame_w": 32, "frame_h": 40, "fps": 12, "mult": 1.5},
    "trent_idle":                  {"archivo": "zombies/trent_idle.png", "frame_w": 24, "frame_h": 27, "fps": 2, "mult": 2.0, "ajuste": 5 / 8},
    "zombie_escalera":             {"archivo": "zombies/propios/zombie_escalera_caminar.png", "frame_w": 56, "frame_h": 44, "mult": 1.5, "fps": 8, "ajuste": 5 / 6},
    "zombie_escalera_atacar":      {"archivo": "zombies/propios/zombie_escalera_atacar.png", "frame_w": 56, "frame_h": 44, "mult": 1.5, "fps": 10, "ajuste": 5 / 6},
    "zombie_escalera_colocar":     {"archivo": "zombies/propios/zombie_escalera_colocar.png", "frame_w": 56, "frame_h": 44, "mult": 1.5, "fps": 6, "loop": False, "ajuste": 5 / 6},
    "zombie_escalera_sin":         {"archivo": "zombies/propios/zombie_escalera_sin_caminar.png", "frame_w": 56, "frame_h": 44, "mult": 1.5, "fps": 8, "ajuste": 5 / 6},
    "zombie_escalera_sin_atacar":  {"archivo": "zombies/propios/zombie_escalera_sin_atacar.png", "frame_w": 56, "frame_h": 44, "mult": 1.5, "fps": 10, "ajuste": 5 / 6},
    "murcielago":                  {"archivo": "zombies/murcielago_correr.png", "frame_w": 44, "frame_h": 40, "fps": 8, "mult": 1.5, "ajuste": 7 / 6},
    "murcielago_atacar":           {"archivo": "zombies/murcielago_atacar.png", "frame_w": 44, "frame_h": 40, "fps": 10, "mult": 1.5, "ajuste": 7 / 6},
    "murcielago_salto":            {"archivo": "zombies/murcielago_salto.png", "frame_w": 44, "frame_h": 40, "fps": 1, "loop": False, "mult": 1.5, "ajuste": 7 / 6},
    "murcielago_panzazo":          {"archivo": "zombies/murcielago_panzazo.png", "frame_w": 44, "frame_h": 40, "fps": 1, "loop": False, "mult": 1.5, "ajuste": 7 / 6},
    "murcielago_sin":              {"archivo": "zombies/murcielago_caminar.png", "frame_w": 44, "frame_h": 40, "fps": 5, "mult": 1.5, "ajuste": 7 / 6},
    "murcielago_sin_atacar":       {"archivo": "zombies/murcielago_atacar.png", "frame_w": 44, "frame_h": 40, "fps": 10, "mult": 1.5, "ajuste": 7 / 6},
    "murcielago_idle":             {"archivo": "zombies/murcielago_idle.png", "frame_w": 30, "frame_h": 32, "fps": 2, "mult": 1.5, "ajuste": 7 / 6},
    "zombie_pertiga":              {"archivo": "zombies/propios/zombie_pertiga_caminar.png", "frame_w": 48, "frame_h": 48, "fps": 10, "dx": -8.5},
    "zombie_pertiga_atacar":       {"archivo": "zombies/propios/zombie_pertiga_atacar.png", "frame_w": 48, "frame_h": 48, "fps": 10, "dx": -8.5},
    "zombie_pertiga_salto":        {"archivo": "zombies/propios/zombie_pertiga_salto.png", "frame_w": 48, "frame_h": 48, "fps": 7, "dx": -8.5, "loop": False},
    "zombie_pertiga_sin":          {"archivo": "zombies/propios/zombie_pertiga_sin_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_pertiga_sin_atacar":   {"archivo": "zombies/propios/zombie_pertiga_sin_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "pip_idle":                    {"archivo": "zombies/pip_idle.png", "frame_w": 24, "frame_h": 25, "fps": 2, "mult": 1.5},
    "zombie_excavador":            {"archivo": "zombies/propios/pip_caminar.png", "frame_w": 28, "frame_h": 26, "fps": 5, "mult": 1.5},
    "zombie_excavador_atacar":     {"archivo": "zombies/propios/pip_atacar.png", "frame_w": 28, "frame_h": 26, "fps": 10, "mult": 1.5},
    "zombie_excavador_sin":        {"archivo": "zombies/propios/pip_caminar.png", "frame_w": 28, "frame_h": 26, "fps": 5, "mult": 1.5},
    "zombie_excavador_sin_atacar": {"archivo": "zombies/propios/pip_atacar.png", "frame_w": 28, "frame_h": 26, "fps": 10, "mult": 1.5},
    "zombie_excavador_tierra":     {"archivo": "zombies/propios/zombie_excavador_tierra.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "cangrejo_bailarin":           {"archivo": "zombies/propios/cangrejo_rojo_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8, "mult": 1.5},
    "cangrejo_bailarin_atacar":    {"archivo": "zombies/propios/cangrejo_rojo_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10, "mult": 1.5},
    "cangrejo_bailarin_baile":     {"archivo": "zombies/propios/cangrejo_rojo_baile.png", "frame_w": 31, "frame_h": 48, "fps": 8, "mult": 1.5},
    "cangrejo_invocado":           {"archivo": "zombies/propios/cangrejo_marron_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8, "mult": 1.5},
    "cangrejo_invocado_atacar":    {"archivo": "zombies/propios/cangrejo_marron_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10, "mult": 1.5},
    "zombie_bungee":               {"archivo": "zombies/propios/zombie_bungee_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "zombie_bungee_atacar":        {"archivo": "zombies/propios/zombie_bungee_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "zombie_bungee_bajar":         {"archivo": "zombies/propios/zombie_bungee_bajar.png", "frame_w": 31, "frame_h": 48, "fps": 8},
    "randy_spider":           {"archivo": "zombies/propios/randy_spider_caminar.png",  "frame_w": 21, "frame_h": 38, "fps": 8, "mult": 1.5},
    "randy_spider_atacar":    {"archivo": "zombies/propios/randy_spider_atacar.png",   "frame_w": 21, "frame_h": 38, "fps": 10, "mult": 1.5},
    "randy_mascara":          {"archivo": "zombies/propios/randy_mascara_caminar.png", "frame_w": 21, "frame_h": 38, "fps": 8, "mult": 1.5},
    "randy_mascara_atacar":   {"archivo": "zombies/propios/randy_mascara_atacar.png",  "frame_w": 21, "frame_h": 38, "fps": 10, "mult": 1.5},
    "randy_normal":           {"archivo": "zombies/propios/randy_normal_caminar.png",  "frame_w": 21, "frame_h": 38, "fps": 8, "mult": 1.5},
    "randy_normal_atacar":    {"archivo": "zombies/propios/randy_normal_atacar.png",   "frame_w": 21, "frame_h": 38, "fps": 10, "mult": 1.5},
    "randy_frente":           {"archivo": "zombies/propios/randy_frente.png",          "frame_w": 21, "frame_h": 38, "fps": 1 / 3, "mult": 1.5},
    "zombie_mini":                 {"archivo": "zombies/propios/zombie_nelson_caminar.png", "frame_w": 20, "frame_h": 28, "fps": 10, "ajuste": 1.75},
    "zombie_mini_atacar":          {"archivo": "zombies/propios/zombie_nelson_atacar.png", "frame_w": 20, "frame_h": 28, "fps": 12, "ajuste": 1.75},
    "zombie_gigante":              {"archivo": "zombies/propios/zombie_mackey_caminar.png", "frame_w": 36, "frame_h": 64, "fps": 6},
    "zombie_gigante_sin":          {"archivo": "zombies/propios/zombie_mackey_sin_caminar.png", "frame_w": 36, "frame_h": 64, "fps": 6},
    "zombie_gigante_golpe":        {"archivo": "zombies/propios/zombie_mackey_golpe.png", "frame_w": 36, "frame_h": 64, "fps": 6, "loop": False},
    "zombie_gigante_golpe_sin":    {"archivo": "zombies/propios/zombie_mackey_golpe_sin.png", "frame_w": 36, "frame_h": 64, "fps": 6, "loop": False},
    "zombie_gigante_lanzar":       {"archivo": "zombies/propios/zombie_mackey_lanzar.png", "frame_w": 36, "frame_h": 64, "fps": 8, "loop": False},
    "mrmackey_idle":               {"archivo": "zombies/mrmackey_idle.png", "frame_w": 20, "frame_h": 38, "fps": 2, "mult": 1.5},
    "srnelson_idle":               {"archivo": "zombies/srnelson_idle.png", "frame_w": 24, "frame_h": 27, "fps": 2, "frames": [0, 1], "mult": 1.5},
    "zombie_garrison":             {"archivo": "zombies/propios/zombie_garrison_caminar.png", "frame_w": 56, "frame_h": 48, "fps": 10, "ajuste": 5 / 4},
    "zombie_garrison_atacar":      {"archivo": "zombies/propios/zombie_garrison_atacar.png", "frame_w": 56, "frame_h": 48, "fps": 12, "ajuste": 5 / 4},
    "alien":                 {"archivo": "zombies/alien_caminar.png", "frame_w": 31, "frame_h": 48, "fps": 6},
    "alien_boton":           {"archivo": "zombies/alien_boton.png",   "frame_w": 31, "frame_h": 48, "fps": 6, "loop": False},
    "alien_atacar":          {"archivo": "zombies/propios/alien_atacar.png", "frame_w": 31, "frame_h": 48, "fps": 10},
    "girasol_sonda":         {"archivo": "plantas/cartman_sonda.png", "frame_w": 32, "frame_h": 24, "fps": 10, "loop": False, "mult": 1.5, "dy_px": 13},
    "girasol_deshabilitado": {"archivo": "plantas/cartman_deshabilitado.png", "frame_w": 32, "frame_h": 24, "fps": 6, "mult": 1.5, "dy_px": 13},
    "cartman_baile":         {"archivo": "plantas/cartman_baile.png", "frame_w": 32, "frame_h": 32, "fps": 6, "mult": 1.5},
    "iman":                   {"archivo": "plantas/iman_completo.png",         "frame_w": 40, "frame_h": 40, "fps": 4, "frames": [0, 1, 2], "seq": [0, 0, 0, 0, 0, 2, 0, 0, 0, 1], "dx": -3, "mult": 1.5, "dy_px": 4, "icon_dy": -4},
    "iman_atrae":             {"archivo": "plantas/iman_completo.png",         "frame_w": 40, "frame_h": 40, "fps": 10, "frames": [3, 4, 5], "loop": False, "dx": -3, "mult": 1.5, "dy_px": 4},
    "iman_cargado":           {"archivo": "plantas/iman_completo.png",         "frame_w": 40, "frame_h": 40, "fps": 1, "frames": [6, 7, 8], "loop": False, "dx": -3, "mult": 1.5, "dy_px": 4},
    "iman_cargado_vader":     {"archivo": "plantas/iman_cargado_vader.png",         "frame_w": 40, "frame_h": 40, "fps": 1, "loop": False, "dx": -3, "mult": 1.5, "dy_px": 4},
    "podadora":               {"archivo": "podadora/timmy_idle.png",           "frame_w": 40, "frame_h": 40, "fps": 4, "mult": 1.5, "dy_px": 4},
    "podadora_activa":        {"archivo": "podadora/timmy_correr.png", "frame_w": 40, "frame_h": 40, "fps": 10, "mult": 1.5, "dy_px": 4},
    "podadora_grito":         {"archivo": "podadora/timmy_grito.png", "frame_w": 40, "frame_h": 40, "fps": 8, "loop": False, "mult": 1.5, "dy_px": 4},
    "dedo":                   {"archivo": "soles/dedo_energia.png",            "frame_w": 32, "frame_h": 32, "fps": 4, "mult": 1.5},
    "ike":                    {"archivo": "proyectiles/ike_volando.png",        "frame_w": 38, "frame_h": 38, "fps": 1, "mult": 1.5},
    "guisante":               {"archivo": "proyectiles/guisante.png",           "frame_w": 40, "frame_h": 48, "fps": 1},
    "bola_nieve":             {"archivo": "proyectiles/bola_nieve.png",         "frame_w": 6, "frame_h": 6, "fps": 1, "mult": 1.5},

    "picante":                {"archivo": "plantas/picante.png", "frame_w": 40, "frame_h": 40, "fps": 14, "frames": list(range(14)), "loop": False, "mult": 1.5, "dy_px": 4, "icon_dy": -4},
    "picante_explota":        {"archivo": "plantas/picante.png", "frame_w": 40, "frame_h": 40, "fps": 18, "frames": list(range(14, 20)), "loop": False, "mult": 1.5, "dy_px": 4},
    "picante_fuego":          {"archivo": "sprites/nuevos/picante_fuego.png",     "frame_w": 26, "frame_h": 32, "fps": 12, "loop": False, "mult": 1.5},
    "aplastadora":            {"archivo": "plantas/aplastadora_quieta.png",  "frame_w": 40, "frame_h": 40, "fps": 4, "mult": 1.5, "dy_px": 4, "icon_dy": -4},
    "aplastadora_salto":      {"archivo": "plantas/aplastadora_salto.png",   "frame_w": 40, "frame_h": 40, "fps": 1, "mult": 1.5, "dy_px": 4},
    "aplastadora_cansada":    {"archivo": "plantas/aplastadora_cansada.png", "frame_w": 40, "frame_h": 40, "fps": 2, "mult": 1.5, "dy_px": 4},
    "cartman_festejo":        {"archivo": "sprites/nuevos/cartman_festejo.png",   "frame_w": 26, "frame_h": 24, "fps": 1, "mult": 1.5},
    "principal":              {"archivo": "sprites/nuevos/principal.png",         "frame_w": 40, "frame_h": 40, "fps": 2, "mult": 1.5, "dy_px": 4, "icon_dy": -2},
    "hankey":                 {"archivo": "sprites/nuevos/hankey.png",            "frame_w": 40, "frame_h": 40, "fps": 2, "mult": 1.5, "dy_px": 4, "icon_dy": -12},
    "mackey":                 {"archivo": "sprites/nuevos/mackey.png",            "frame_w": 40, "frame_h": 40, "fps": 6, "loop": False, "mult": 1.5, "dy_px": 4, "icon_dy": -2},
    "escalera":               {"archivo": "zombies/propios/escalera_puesta.png",      "frame_w": 15, "frame_h": 35, "fps": 1, "mult": 1.5, "ajuste": 5 / 6},
    "bungee_marca":           {"archivo": "sprites/nuevos/bungee_marca.png",          "frame_w": 24, "frame_h": 12, "fps": 4},
}

_cache = {}
_base = {}


def _load_frames(key):
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
    if key not in SPRITES:
        return None
    ck = (key, factor)
    if ck not in _cache:
        base = _base.get(key) or _load_frames(key)
        if base is None:
            return None
        _base[key] = base
        aj = SPRITES[key].get("ajuste", 1.0)
        if factor != 1 or aj != 1.0:
            _cache[ck] = [pygame.transform.scale(f, (round(f.get_width() * factor * aj), round(f.get_height() * factor * aj))) for f in base]
        else:
            _cache[ck] = base
    return _cache[ck]


def has_sprite(key):
    return key in SPRITES and get_frames(key, 1) is not None


def anim_duration(key):
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


_variantes = {}


def draw_sprite(surface, key, center, scale=1.0, t=None, flash=False, frame=None, flip=False, tint=None):
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
    cfg = SPRITES[key]
    en_juego = factor == round(ESCALA_BASE * cfg.get("mult", 1.0))
    dy = cfg.get("dy_px", 0) if en_juego else cfg.get("icon_dy", 0)
    dx = round(cfg.get("dx", 0) * factor)
    surface.blit(img, img.get_rect(center=(center[0] + dx, center[1] + dy)))
    return True
