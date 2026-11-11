"""
Pruebas simuladas del juego (sin ventana): cada caso arma una situación en una partida real
(GameplayScene), avanza el tiempo a 60 cuadros por segundo y compara con lo esperado.
Es la base del plan de pruebas de docs/06_plan_de_pruebas.md.

    python tools/pruebas_simuladas.py            # imprime una tabla con los resultados
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
os.chdir(RAIZ)

import tempfile
import pygame
import game as gm
import cuentas
# Las pruebas no tocan las cuentas del jugador: usan un archivo temporal, vacío al empezar
# (sin cuenta activa, los logros se cuentan en memoria y no se guardan)
cuentas.RUTA = os.path.join(tempfile.gettempdir(), "bielsa_pruebas_cuentas.json")
if os.path.exists(cuentas.RUTA):
    os.remove(cuentas.RUTA)
cuentas.recargar()
from settings import CELL_W, GRID_X, SCREEN_W, PLANT_DATA, ZOMBIE_DATA, CHEF_REACTIVA
from scenes.gameplay import GameplayScene
from levels import LEVELS
from scenes.result import ResultScene
from scenes.mapa import MapaScene
from scenes.equipo import EquipoScene
from entities.plants import create_plant
from entities.zombies import create_zombie

DT = 1 / 60
G = gm.Game()
import ajustes                       # las pruebas usan los valores originales (sin Opciones > Juego)
ajustes.config.clear()
ajustes.aplicar()
RESULTADOS = []


def escena(nivel=1, sol=1000):
    sc = GameplayScene(G, nivel)
    sc.dialogo = None
    sc.waves_on = False
    sc.tuto, sc.tuto_paso = [], None
    sc.sky_timer = 1e9          # sin soles del cielo (salvo que la prueba los pida)
    sc.sun = sol
    return sc


def correr(sc, seg, hasta=None):
    for _ in range(int(seg / DT)):
        sc.update(DT)
        if hasta and hasta():
            return True
    return False


def planta(sc, k, r, c):
    p = create_plant(k, r, c, sc.grid)
    sc.grid.place(p)
    return p


def zombie(sc, k, r, col=None, x=None):
    z = create_zombie(k, r, sc.grid)
    z.x = x if x is not None else sc.grid.cell_rect(r, col).centerx
    z.speed = ZOMBIE_DATA[k]["velocidad"]       # sin el ±8% al azar, para que la prueba sea repetible
    sc.zombies.append(z)
    return z


def caso(id_, que):
    def deco(fn):
        try:
            obtenido, pasa = fn()
        except Exception as e:                 # una prueba que explota cuenta como falla
            obtenido, pasa = "Error: %r" % e, False
        RESULTADOS.append((id_, que, obtenido, pasa))
        return fn
    return deco


# ------------------------------------------------------------------ plantas
@caso("PL-01", "Chef Cartman: primer dedo a los 6 s y después cada 18 s")
def _():
    sc = escena()
    planta(sc, "girasol", 2, 0)
    vistos, t, momentos = set(), 0.0, []
    while t < 24.2:                       # cuenta los dedos que van saliendo (cada uno dura 9 s en el piso)
        sc.update(DT); t += DT
        for s in sc.suns:
            if id(s) not in vistos:
                vistos.add(id(s)); momentos.append(round(t, 1))
    return "dedos producidos a los %s s" % momentos, \
        len(momentos) == 2 and abs(momentos[0] - 6) < 0.1 and abs(momentos[1] - 24) < 0.1


@caso("PL-02", "Juntar un dedo suma 25 de energía")
def _():
    sc = escena(sol=0)
    planta(sc, "girasol", 2, 0)
    correr(sc, 9)
    s = sc.suns[0]
    ok = sc.collect_sun_at((int(s.x), int(s.y)))
    return "clic sobre el dedo: %s, energía = %d" % (ok, sc.sun), ok and sc.sun == 25


@caso("PL-03", "Stan dispara solo si hay un zombie en su fila; la bola daña 20 y ralentiza")
def _():
    sc = escena()
    planta(sc, "lanzaguisantes", 2, 1)
    otro = zombie(sc, "normal", 0, 8)
    correr(sc, 1.5)
    sin_blanco = len(sc.projectiles) == 0 and otro.hp == 200
    z = zombie(sc, "normal", 2, 8)
    correr(sc, 3.0)
    return ("sin zombie en la fila no dispara: %s; zombie de su fila: vida %d, ralentizado %s"
            % (sin_blanco, z.hp, z.slow > 0)), sin_blanco and z.hp < 200 and z.slow > 0


@caso("PL-04", "Butters aguanta ~40 s a un zombie normal (4000 de vida, 100 por segundo)")
def _():
    sc = escena()
    b = planta(sc, "nuez", 2, 3)
    zombie(sc, "normal", 2, x=sc.grid.cell_rect(2, 4).left + 12)
    t = 0.0
    while b.alive and t < 60:
        sc.update(DT); t += DT
    return "Butters murió a los %.1f s" % t, 38 <= t <= 42


@caso("PL-05", "Kyle patea a Ike, que cae sobre el zombie de su fila (20 de daño, no ralentiza)")
def _():
    sc = escena()
    planta(sc, "kyle", 2, 1)
    z = zombie(sc, "normal", 2, 7)
    correr(sc, 4.0)
    return "vida del zombie: %d, ralentizado: %s" % (z.hp, z.slow > 0), z.hp < 200 and z.slow <= 0


@caso("PL-06", "Kenny explota en 3x3 (1800), no daña a un hipnotizado y revive a los 30 s")
def _():
    sc = escena()
    planta(sc, "kenny", 2, 4)
    adentro = zombie(sc, "cubeta", 1, 5)
    afuera = zombie(sc, "normal", 2, 8)
    aliado = zombie(sc, "normal", 3, 3)
    aliado.hypnotize(); aliado.speed = 0
    correr(sc, 1.0)
    r1 = (not adentro.alive, afuera.alive, aliado.alive)
    correr(sc, 30.5)
    k = sc.grid.get(2, 4)
    revive = k is not None and k.key == "kenny" and k.esperando
    return ("cubeta en el área muere: %s; fuera del área vive: %s; hipnotizado vive: %s; revive y espera: %s"
            % (r1 + (revive,))), all(r1) and revive


@caso("PL-07", "Toallin: el zombie que lo muerde queda hipnotizado y camina a la derecha")
def _():
    sc = escena()
    planta(sc, "toallin", 2, 3)
    z = zombie(sc, "normal", 2, x=sc.grid.cell_rect(2, 4).left + 10)
    correr(sc, 1.0)
    x0 = z.x
    correr(sc, 1.0)
    return ("hipnotizado: %s; Toallin desaparece: %s; avanza a la derecha: %s"
            % (z.hypno, sc.grid.get(2, 3) is None, z.x > x0)), z.hypno and sc.grid.get(2, 3) is None and z.x > x0


@caso("PL-08", "Santi (imán) le saca el balde a un zombie con balde en su alcance y recarga 15 s")
def _():
    sc = escena()
    m = planta(sc, "iman", 2, 2)
    z = zombie(sc, "cubeta", 3, 4)
    correr(sc, 2.5)
    a = (z.armor, m.state)
    correr(sc, 15.0)
    return "armadura después: %d, estado: %s; 15 s más tarde: %s" % (a[0], a[1], m.state), \
        a == (0, "cargado") and m.state == "listo"


@caso("PL-09", "Santi le saca la puerta al zombie con puerta")
def _():
    sc = escena()
    planta(sc, "iman", 2, 2)
    z = zombie(sc, "puerta", 2, 5)
    correr(sc, 2.5)
    return "escudo: %d, dibujo: %s" % (z.shield, z.sprite_state()[0]), z.shield == 0


@caso("PL-10", "Santi le saca el pico al excavador bajo tierra: sale a la superficie")
def _():
    sc = escena()
    planta(sc, "iman", 2, 3)
    z = zombie(sc, "excavador", 2, 5)
    correr(sc, 3.0)
    return "metal: %s, fase: %s, bajo tierra: %s" % (z.metal, z.fase, z.underground), \
        not z.metal and z.fase in ("sale", "camina")


@caso("PL-11", "Jesús explota al ~1,06 s en cruz con 350: mata al del diario y deja vivo al del cono")
def _():
    sc = escena()
    j = planta(sc, "picante", 2, 4)
    d = zombie(sc, "diario", 2, 8)
    c = zombie(sc, "cono", 0, 4)
    t = 0.0
    while not j.exploto and t < 3:
        sc.update(DT); t += DT
    correr(sc, 0.5)
    return ("explota a los %.2f s; diario muerto: %s; cono vivo con %d de armadura"
            % (t, not d.alive, c.armor)), 1.0 <= t <= 1.12 and not d.alive and c.alive


@caso("PL-12", "Gero salta a la casilla de enfrente, mata a todos los de esa casilla y queda cansado")
def _():
    sc = escena()
    g = planta(sc, "aplastadora", 1, 2)
    z1 = zombie(sc, "gigante", 1, x=sc.grid.cell_rect(1, 3).centerx + 20)
    z2 = zombie(sc, "cono", 1, x=sc.grid.cell_rect(1, 3).centerx + 30)
    correr(sc, 2.5)
    return ("gigante muerto: %s; cono muerto: %s; ahora en columna %d; cansado: %s; recarga %.0f s"
            % (not z1.alive, not z2.alive, g.col, g.cansada, g.cooldown)), \
        not z1.alive and not z2.alive and g.col == 3 and g.cansada


@caso("PL-13", "Gero en la última columna aplasta su propia casilla sin moverse")
def _():
    sc = escena()
    g = planta(sc, "aplastadora", 3, 8)
    z = zombie(sc, "normal", 3, x=sc.grid.cell_rect(3, 8).centerx + 10)
    correr(sc, 2.5)
    return "zombie muerto: %s; columna: %d" % (not z.alive, g.col), not z.alive and g.col == 8


# ------------------------------------------------------------------ zombies
@caso("ZO-01", "Zombie normal: camina 18 px/s y come 100 de vida por segundo")
def _():
    sc = escena()
    z = zombie(sc, "normal", 2, 8)
    x0 = z.x
    correr(sc, 5.0)
    v = (x0 - z.x) / 5
    b = planta(sc, "nuez", 4, 3)
    zombie(sc, "normal", 4, x=sc.grid.cell_rect(4, 4).left + 12)
    correr(sc, 3.0)
    return "velocidad %.1f px/s; Butters perdió %d en 3 s" % (v, 4000 - b.hp), \
        abs(v - 18) < 0.5 and 290 <= 4000 - b.hp <= 310


@caso("ZO-02", "Cono y balde: la armadura (370 / 1100) se gasta antes que el cuerpo (200)")
def _():
    sc = escena()
    c = zombie(sc, "cono", 1, 8)
    b = zombie(sc, "cubeta", 2, 8)
    c.take_damage(569); b.take_damage(1299)
    vivos = c.alive and b.alive
    c.take_damage(1); b.take_damage(1)
    return "con 569 / 1299 de daño siguen vivos: %s; con 1 más mueren: %s" % (vivos, not c.alive and not b.alive), \
        vivos and not c.alive and not b.alive


@caso("ZO-03", "Zombie con puerta: la bola de nieve pega en la puerta (sin ralentizar); Ike le pega al cuerpo")
def _():
    sc = escena()
    planta(sc, "lanzaguisantes", 2, 1)
    z = zombie(sc, "puerta", 2, 7)
    correr(sc, 3.0)
    a = (z.shield < 1100, z.hp == 200, z.slow <= 0)
    sc2 = escena()
    planta(sc2, "kyle", 2, 1)
    z2 = zombie(sc2, "puerta", 2, 7)
    correr(sc2, 4.0)
    return ("Stan: gasta la puerta %s, cuerpo intacto %s, sin ralentizar %s; Kyle: cuerpo %d, puerta %d"
            % (a + (z2.hp, z2.shield))), all(a) and z2.hp < 200 and z2.shield == 1100


@caso("ZO-04", "Zombie del diario: al romperle el diario se queda quieto 1 s y después corre (48 px/s)")
def _():
    sc = escena()
    z = zombie(sc, "diario", 2, 8)
    z.take_damage(150)
    return "enojado: %s, quieto %.1f s, velocidad %.0f" % (z.enojado, z.stun, z.speed), \
        z.enojado and z.stun == 1.0 and 44 <= z.speed <= 52


@caso("ZO-05", "Pértiga: corre y salta la primera planta; después camina a 18 px/s")
def _():
    sc = escena()
    b = planta(sc, "nuez", 2, 4)
    z = zombie(sc, "pertiga", 2, 8)
    correr(sc, 12)
    return "pasó la planta: %s; Butters intacto: %s; sin pértiga: %s; velocidad %.0f" % (
        z.x < b.rect.left, b.hp == 4000, not z.pole, z.speed), z.x < b.rect.left and b.hp == 4000 and not z.pole


@caso("ZO-06", "Pértiga que llega a una planta con escalera la salta igual (no trepa)")
def _():
    sc = escena()
    b = planta(sc, "nuez", 2, 4)
    sc.grid.ladders.add((2, 4))
    z = zombie(sc, "pertiga", 2, 8)
    saltos = []
    for _ in range(int(12 / DT)):
        sc.update(DT)
        if z.jump is not None:
            saltos.append(1)
    return "saltó con la pértiga: %s" % bool(saltos), bool(saltos)


@caso("ZO-07", "Escalera: apoya la escalera en la primera planta y los demás la pasan por arriba")
def _():
    sc = escena()
    b = planta(sc, "nuez", 2, 3)
    z = zombie(sc, "escalera", 2, 6)
    correr(sc, 12)
    puesta = (2, 3) in sc.grid.ladders
    z.alive = False                       # el de la escalera ya cumplió (que no llegue a la casa)
    n = zombie(sc, "normal", 2, 5)
    hp0 = b.hp
    paso = correr(sc, 20, lambda: n.x < b.rect.left)
    return "escalera puesta: %s; el normal la pasó por arriba: %s; Butters sin mordidas: %s" % (
        puesta, paso, b.hp == hp0), puesta and paso and b.hp == hp0


@caso("ZO-08", "Tractor: no lo hipnotiza Toallin (se lo come) y no usa escaleras")
def _():
    sc = escena()
    planta(sc, "toallin", 2, 4)
    z = zombie(sc, "tractor", 2, x=sc.grid.cell_rect(2, 5).left + 30)
    correr(sc, 3)
    return "Toallin comido: %s; tractor hipnotizado: %s" % (sc.grid.get(2, 4) is None, z.hypno), \
        sc.grid.get(2, 4) is None and not z.hypno


@caso("ZO-09", "Bungee: siempre cae desde la 3.ª columna (col 2 a 8) y después camina")
def _():
    sc = escena()
    cols = {create_zombie("bungee", 2, sc.grid).col for _ in range(200)}
    z = zombie(sc, "bungee", 2, x=None) if False else create_zombie("bungee", 2, sc.grid)
    sc.zombies.append(z)
    correr(sc, 4)
    return "columnas de caída: %s; después de caer: %s" % (sorted(cols), z.fase), \
        min(cols) >= 2 and z.fase == "suelo"


@caso("ZO-10", "Bailarín: frena, baila e invoca hasta 4 zombies a su alrededor")
def _():
    sc = escena()
    zombie(sc, "bailarin", 2, 5)
    correr(sc, 2.5)
    return "zombies en el campo: %d (1 bailarín + invocados)" % len(sc.zombies), len(sc.zombies) == 5


@caso("ZO-11", "Excavador: bajo tierra no recibe disparos, sale en la 1.ª columna, come hacia la derecha y se va")
def _():
    sc = escena()
    planta(sc, "lanzaguisantes", 2, 0)
    z = zombie(sc, "excavador", 2, 8)
    correr(sc, 3)
    intacto = z.hp == 300 and not z.targetable
    salio = correr(sc, 40, lambda: z.fase == "camina")
    planta_comida = correr(sc, 60, lambda: sc.grid.get(2, 0) is None)
    se_fue = correr(sc, 60, lambda: not z.alive)
    return ("bajo tierra intacto: %s; salió: %s; comió la planta de atrás: %s; se fue: %s"
            % (intacto, salio, planta_comida, se_fue)), intacto and salio and planta_comida and se_fue


@caso("ZO-12", "Gigante: aplasta una planta de un golpe (1 s) y con media vida revolea al mini zombie")
def _():
    sc = escena()
    b = planta(sc, "nuez", 2, 3)
    z = zombie(sc, "gigante", 2, x=sc.grid.cell_rect(2, 4).left + 20)
    t = 0.0
    while b.alive and t < 10:
        sc.update(DT); t += DT
    z.x = sc.grid.cell_rect(2, 7).centerx
    z.hp = z.max_hp * 0.4
    correr(sc, 2.0)
    minis = [m for m in sc.zombies if m.key == "mini"]
    # El gigante lo tira al azar entre GRID_X + 30 y GRID_X + 2 casillas (zombies.py): ese es el rango
    lugar = minis and (GRID_X + 20 <= minis[0].x <= GRID_X + CELL_W * 2 + 10)
    return ("Butters (4000) aplastado a los %.1f s; mini lanzado: %s; cae cerca de la casa: %s"
            % (t, bool(minis), bool(lugar))), t <= 1.6 and bool(minis) and bool(lugar) and not z.tiene_mini


@caso("ZO-13", "Alien: entra 2 casillas, aprieta el botón y apaga a los Chef hasta que muere")
def _():
    sc = escena()
    chef = planta(sc, "girasol", 0, 0)
    a = zombie(sc, "alien", 2, x=SCREEN_W + 10)
    correr(sc, 25, lambda: a.state == "quieto")
    apagado = chef.deshabilitado
    a.kill()
    correr(sc, 0.2)
    return "estado del alien: %s; Chef apagado: %s; al morir vuelve a cocinar: %s" % (
        a.state, apagado, not chef.deshabilitado), apagado and not chef.deshabilitado


@caso("ZO-14", "Alien: si una planta le corta el paso, se la come")
def _():
    sc = escena()
    b = planta(sc, "nuez", 2, 8)
    a = zombie(sc, "alien", 2, x=sc.grid.cell_rect(2, 8).right + 15)
    correr(sc, 2)
    return "comiendo: %s; Butters perdió %d" % (a.eating, 4000 - b.hp), a.eating and b.hp < 4000


# ------------------------------------------------------------------ mecánicas y casos raros
@caso("ME-01", "Podadora: un zombie en el borde la activa, limpia la fila y no vuelve a salir")
def _():
    sc = escena()
    z1 = zombie(sc, "normal", 2, x=GRID_X + 3)
    z2 = zombie(sc, "cono", 2, 4)
    correr(sc, 4)
    m = sc.mowers[2]
    return "los dos zombies de la fila muertos: %s; podadora usada: %s" % (not z1.alive and not z2.alive, m.used), \
        not z1.alive and not z2.alive and m.used


@caso("ME-02", "Con la podadora gastada, un zombie que llega a la casa hace perder el nivel")
def _():
    sc = escena()
    sc.mowers[2].used = True
    zombie(sc, "normal", 2, x=GRID_X + 3)
    correr(sc, 4)
    return "resultado: %s; diálogo de derrota: %s" % (sc.result, sc.dialogo and sc.dialogo.retrato), sc.result is False


@caso("ME-03", "Velocidad x2: cada cuadro avanza dos pasos; se recuerda al empezar otro nivel")
def _():
    sc = escena()
    sc.cambiar_velocidad()
    t0 = sc.time
    sc.update(DT)
    paso = sc.time - t0
    otra = GameplayScene(G, 2).velocidad
    sc.cambiar_velocidad(); sc.cambiar_velocidad()       # x3 -> x1 (deja todo como estaba)
    return "avance por cuadro a x2: %.4f s (x1 = %.4f); el nivel siguiente arranca en x%d" % (paso, DT, otra), \
        abs(paso - 2 * DT) < 1e-9 and otra == 2


@caso("ME-04", "Pausa: congela la partida y las teclas 1-9 no eligen cartas")
def _():
    sc = escena()
    z = zombie(sc, "normal", 2, 8)
    sc.toggle_pausa()
    x0 = z.x
    sc.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1, mod=0, unicode="1", scancode=0))
    correr(sc, 2)
    quieto, sin_sel = z.x == x0, sc.selected is None
    sc.toggle_pausa()
    correr(sc, 1)
    return "zombie quieto en pausa: %s; tecla 1 sin efecto: %s; al reanudar sigue: %s" % (
        quieto, sin_sel, z.x < x0), quieto and sin_sel and z.x < x0


@caso("ME-05", "Plantar: cobra el costo, inicia la recarga y no deja plantar en una casilla ocupada ni sin energía")
def _():
    sc = escena(sol=150)
    ok = sc.try_place("lanzaguisantes", 2, 2)
    ocupada = sc.try_place("girasol", 2, 2)
    en_recarga = sc.try_place("lanzaguisantes", 3, 2)
    sc.sun = 10
    sin_energia = sc.try_place("girasol", 1, 1)
    return ("planta: %s (energía %d); casilla ocupada: %s; en recarga: %s; sin energía: %s"
            % (ok, sc.sun, ocupada, en_recarga, sin_energia)), ok and not ocupada and not en_recarga and not sin_energia


@caso("ME-06", "La carta vuelve a estar disponible al terminar su recarga (Stan: 7,5 s)")
def _():
    sc = escena()
    sc.try_place("lanzaguisantes", 2, 2)
    correr(sc, 7.4)
    antes = sc.hud.get_card("lanzaguisantes").ready(sc.sun)
    correr(sc, 0.2)
    despues = sc.hud.get_card("lanzaguisantes").ready(sc.sun)
    return "lista a los 7,4 s: %s; a los 7,6 s: %s" % (antes, despues), not antes and despues


@caso("ME-07", "Pala: saca la planta y libera la casilla")
def _():
    sc = escena()
    planta(sc, "nuez", 1, 1)
    ok = sc.dig(1, 1)
    return "sacada: %s; casilla libre: %s" % (ok, sc.grid.is_free(1, 1)), ok and sc.grid.is_free(1, 1)


@caso("ME-08", "Un hipnotizado y un zombie enemigo se muerden hasta que uno muere")
def _():
    sc = escena()
    h = zombie(sc, "normal", 2, 3)
    h.hypnotize()
    e = zombie(sc, "normal", 2, x=h.x + 25)
    correr(sc, 5)
    return "hipnotizado vivo: %s; enemigo vivo: %s" % (h.alive, e.alive), h.alive != e.alive


@caso("ME-09", "Victoria: sin oleadas pendientes ni zombies, aparece el cartel y después el diálogo")
def _():
    sc = escena()
    sc.waves.pending = []
    correr(sc, 1.5)
    return "resultado: %s; retrato: %s; nivel ganado guardado: %s" % (
        sc.result, sc.dialogo and sc.dialogo.retrato, "nivel1" in G.progreso), \
        sc.result is True and sc.dialogo is not None and "nivel1" in G.progreso


# ------------------------------------------------------------------ mapa, equipo y fin de nivel
@caso("MA-01", "Mapa: al empezar solo el tutorial está disponible; ganar uno desbloquea el siguiente")
def _():
    G.progreso = set()
    m = MapaScene(G)
    a = [m.estado(i) for i in range(4)]
    G.progreso = {"tutorial"}
    b = [m.estado(i) for i in range(4)]
    return "sin ganar nada: %s; con el tutorial ganado: %s" % (a, b), \
        a == ["disponible", "bloqueado", "bloqueado", "bloqueado"] and b[:2] == ["ganado", "disponible"] and b[2] == "bloqueado"


@caso("EQ-01", "Equipo: hasta 7 personajes; sin ninguno no deja jugar; recuerda el último equipo")
def _():
    G.equipo = []
    e = EquipoScene(G, 1)
    for c in e.cartas:
        e.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=c.rect.center))
    n = len(e.equipo)
    e2 = EquipoScene(G, 1)
    e2.equipo = []
    e2.jugar()
    no_juega = e2.aviso > 0
    G.equipo = ["girasol", "nuez"]
    recuerda = EquipoScene(G, 2).equipo == ["girasol", "nuez"]
    return "elegidos con 9 clics: %d; sin equipo muestra aviso: %s; recuerda el anterior: %s" % (
        n, no_juega, recuerda), n == 7 and no_juega and recuerda


@caso("FI-01", "Fin de nivel: el diálogo va primero y con un clic aparece la pantalla de resultado")
def _():
    sc = escena()
    sc.finish(victory=False)
    cambios = []
    orig = G.change_scene
    G.change_scene = cambios.append
    for _ in range(300):
        sc.update(DT)
    sc.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(500, 300)))
    sc.update(DT)
    G.change_scene = orig
    return "escena siguiente: %s" % (type(cambios[0]).__name__ if cambios else None), \
        bool(cambios) and isinstance(cambios[0], ResultScene)


@caso("FI-02", "Resultado: SIGUIENTE NIVEL solo al ganar un nivel que no es el último")
def _():
    textos = lambda r: [b.text for b in r.botones] if hasattr(r, "botones") else [b.text for b in r.buttons]
    try:
        a = textos(ResultScene(G, True, 1))
        ultimo = len(LEVELS) - 1                     # el último nivel del juego (hoy, el 6)
        b = textos(ResultScene(G, True, ultimo))
        c = textos(ResultScene(G, False, 1))
    except AttributeError:
        return "no se pudieron leer los botones", False
    return "gana nivel 1: %s | gana el último (%d): %s | pierde: %s" % (a, ultimo, b, c), \
        "SIGUIENTE NIVEL" in a and "SIGUIENTE NIVEL" not in b and "SIGUIENTE NIVEL" not in c


@caso("TU-01", "Tutorial completo con un jugador automático: 12 frases, espera cada acción y se gana")
def _():
    sc = GameplayScene(G, 0)
    frases, t = [], 0.0
    clic = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(500, 300))
    while t < 400 and sc.result is None:
        if sc.dialogo:
            for _ in range(600):
                if sc.dialogo.escrito:
                    break
                sc.update(DT)
            f = sc.dialogo.mensajes[sc.dialogo.indice]
            if not frases or frases[-1] != f:
                frases.append(f)
            sc.handle_event(clic)
        else:
            for s in list(sc.suns):
                if s.alive:
                    sc.collect_sun_at((int(s.x), int(s.y)))
            for col, k in ((0, "girasol"), (1, "girasol"), (2, "lanzaguisantes"), (3, "lanzaguisantes")):
                for r in range(5):
                    if sc.can_place(k, r, col):
                        sc.try_place(k, r, col)
        sc.update(DT); t += DT
    return "frases mostradas: %d; resultado: %s a los %.0f s" % (len(frases), sc.result, t), \
        len(frases) == 12 and sc.result is True


def main():
    ok = sum(1 for r in RESULTADOS if r[3])
    for id_, que, obtenido, pasa in RESULTADOS:
        print("| %s | %s | %s | %s |" % (id_, que, obtenido, "Pasa" if pasa else "Falla"))
    print("\n%d de %d pruebas pasan" % (ok, len(RESULTADOS)))


if __name__ == "__main__":
    main()
