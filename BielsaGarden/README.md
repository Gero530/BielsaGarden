# Plantas vs Zombies — pygame

Clon simple de PvZ para PC hecho con Python + pygame.

## Cómo correrlo

```bash
pip install pygame
python main.py
```

## Controles

| Acción | Control |
|---|---|
| Elegir planta | Clic en la carta (o teclas `1` a `7`) |
| Plantar | Clic en una celda libre del césped |
| Pala (quitar planta) | Clic en "Pala" (o tecla `S`) y luego en la planta |
| Juntar energía | Clic sobre el dedo brillante |
| Cancelar selección | Clic derecho |
| Pausa | `P` o `Esc` |

## Contenido actual

**Plantas**

| Planta | Costo | Vida | Qué hace |
|---|---|---|---|
| Chef (Cartman cocinando) | 50 | 300 | Cocina chili y suelta un dedo de energía (25 de sol) cada 18 s; el primero a los 6 s. Es el generador (antes era el Girasol) |
| Stan | 100 | 300 | Como el lanzaguisantes de hielo: cuando hay un zombie en su fila se pone en pose de tiro y le tira bolas de nieve (20 de daño) cada 1,4 s. El zombie golpeado queda celeste y camina y come a la mitad de velocidad durante 4 s |
| Butters | 50 | 4000 | Como la nuez: muro que frena zombies. Quieto mientras nadie lo toca y llora mientras se lo están comiendo |
| Kyle | 100 | 300 | Catapulta: cuando hay un zombie en su fila se da vuelta y patea a Ike, que vuela en arco y cae sobre el zombie (20 de daño, igual que el guisante) cada 1,4 s |
| Kenny | 150 | — | Como la cereza: explota al plantarlo (~0,5 s) y hace 1800 de daño en un área de 3x3 casillas. Después aparecen las ratas (solo decoración) |
| Imán | 100 | 300 | Como el Magnetoseta: cuando un zombie con un objeto de metal (el balde de la cubeta) entra en su alcance (~3 casillas a la redonda, cualquier fila), le arranca el balde, que sale volando hasta el imán. El zombie sigue como uno normal. Se queda con el balde pegado (que se va deshaciendo) durante 15 s de recarga. El cono no es de metal |
| Toallin | 75 | 300 | Como la hipnoseta: el zombie que lo muerde se lo come y queda hipnotizado (violeta, camina a la derecha y muerde a los zombies que encuentra) |
| Picante | 125 | — | Como el Jalapeño pero en cruz: explota al plantarlo y quema toda su fila y toda su columna (200 de daño, justo para un zombie normal) |
| Aplastadora | 125 | 300 | Como la Calabaza pero reutilizable: salta a la casilla de enfrente si hay un zombie (y está libre), mata a todos los de esa casilla, se queda ahí y recarga 8 s |

**Zombies**

| Zombie | Vida | Armadura |
|---|---|---|
| Normal | 200 | — |
| Cono | 200 | 370 |
| Cubeta | 200 | 1100 |
| Puerta | 200 | 1100 de escudo frontal (Ike y las explosiones la saltean; el Imán se la saca) |
| Diario | 200 | 150 de escudo; sin diario se enoja y corre |
| Pértiga | 340 | — Corre y salta la primera planta |
| Escalera | 340 | — Apoya una escalera en la primera planta; la usan todos |
| Tractor | 1300 | — Lento, muerde fuerte |
| Bungee | 200 | — Cae del cielo en una casilla al azar (marca roja antes) |
| Bailarín | 340 | — Invoca hasta 4 zombies a su alrededor |
| Excavador | 300 | — Va bajo tierra, sale junto a la casa y come hacia la derecha |
| Gigante | 3000 | — Aplasta plantas de un golpe; con poca vida tira al mini zombie (150) |

Todos los números están en `settings.py` (`PLANT_DATA` y `ZOMBIE_DATA`).

**Niveles** (mapa: Tutorial → Nivel 1 → Nivel 2 → Nivel 3, se desbloquean de a uno; el progreso se guarda en partidas, ver "Partidas guardadas" más abajo). Las oleadas están en `levels/*.py`, con hordas con bandera y oleada final (formato explicado en `world/wave_manager.py`). Cada fila tiene un cortacésped de un solo uso: Timmy en su silla de ruedas, que grita "¡TIMMY!" y barre la fila cuando un zombie llega al borde del césped.
Se gana al eliminar todos los zombies enemigos (los hipnotizados no cuentan); se pierde si uno llega a la casa.

## Estructura

```
main.py              Punto de entrada
game.py              Bucle principal + cambio de escenas
settings.py          Constantes y estadísticas (acá se balancea el juego)

scenes/
  base.py            Clase Scene (handle_event / update / draw)
  menu.py            Pantalla de inicio
  gameplay.py        Partida: une grilla, entidades, HUD, recursos y fin de nivel
  result.py          Pantalla de victoria / derrota (pixel art)
  mapa.py            Mapa de niveles (desbloqueo, candados)
  equipo.py          Elegí tu equipo antes de cada nivel (máximo EQUIPO_MAX de settings.py)
  catalogo.py        Catálogo de personajes y zombies

data/
  mapa.py            Fondo del mapa y posición de cada botón de nivel
  catalogo.py        Nombres y descripciones del catálogo

tools/
  generar_placeholders.py   Crea los sprites placeholder de assets/sprites/nuevos/ (no pisa los existentes)

world/
  grid.py            Grilla 5x9: celdas, colocación de plantas, dibujo del césped
  wave_manager.py    Suelta zombies según el horario del nivel
  lawnmower.py       Cortacéspedes (Timmy): se mece esperando, traquetea y levanta polvo al salir

entities/
  plants.py          Plant + Chef (Cartman cocinando, clave `girasol`), Stan (lanzaguisantes, clave `lanzaguisantes`), Butters (nuez, clave `nuez`), Kyle, Kenny, Toallin, Imán
  zombies.py         Zombie + Normal, Cono, Cubeta
  projectiles.py     Guisante, bola de nieve de Stan (ralentiza) e Ike (proyectil en arco)
  effects.py         Efectos visuales: animación suelta (ratas de Kenny) destello del área y balde volando hacia el Imán
  sun.py             Sol (recurso)

ui/
  sprites.py         Carga y animación de sprites (tiras de LibreSprite)
  hud.py             Contador de sol, cartas con recarga, pala, barra de progreso
  button.py          Botón genérico
  fonts.py           Caché de fuentes y helper de texto

assets/
  plantas/           Sprites de plantas
  proyectiles/       Sprites de proyectiles
  zombies/           Sprites de zombies

levels/
  __init__.py        Lista de niveles
  tutorial.py        Tutorial guiado (pasos con diálogo)
  level_1.py ... level_3.py   Oleadas de cada nivel
  dialogos.py        Diálogos de Bielsa por nivel
```

## Cómo extender

- **Nueva planta**: datos en `settings.PLANT_DATA` → clase en `entities/plants.py` → registrar en `PLANT_CLASSES` → nombre y descripción en `data/catalogo.py`. Aparece sola en la pantalla de equipo (un nivel puede limitar las opciones con `"plantas": [...]`).
- **Nuevo zombie**: datos en `settings.ZOMBIE_DATA` → clase en `entities/zombies.py` → registrar en `ZOMBIE_CLASSES`.
- **Nuevo nivel**: copiar `levels/level_3.py` como `level_4.py` (con un `"id"` nuevo), cambiar las oleadas, agregarlo a `LEVELS` en `levels/__init__.py` y sumar su botón en `data/mapa.py`.
- **Sprites**: poné la tira horizontal (PNG transparente) en `assets/` y agregá una línea en `SPRITES` dentro de `ui/sprites.py`
  con el archivo, el tamaño de un frame y los fps. Se escala x2 automáticamente. Si falta el archivo se usa el dibujo con formas.
  Animaciones de acción (como el disparo) llevan `"loop": False` y se reproducen una vez.
  Para que una planta cambie de animación según su estado, sobreescribí `sprite_state()` en su clase.
  Opciones útiles de cada sprite: `"frames": [2,3,4]` (usar solo esos frames de la tira), `"seq"` (orden de los frames),
  `"mult": 1.5` (dibujarlo x3 en vez de x2, sin deformarlo) y `"dy_px"` (alinear los pies con el suelo).

### Sprites integrados

| Archivo | Uso | Frames | fps |
|---|---|---|---|
| `plantas/cartman_cocinando.png` | Cartman cocinando chili (generador), x3 | 6 | 6 |
| `soles/dedo_energia.png` | El dedo con resplandor: es la unidad de energía, x3 | 4 | 4 |
| `plantas/girasol_idle.png` | Girasol en reposo (ya no se usa) | 10 | 8 |
| `plantas/lanzaguisantes_idle.png` | Lanzaguisantes en reposo | 8 | 8 |
| `plantas/lanzaguisantes_disparo.png` | Al disparar (el guisante sale en el frame 3) | 5 | 12 |
| `plantas/nuez_idle.png` | Nuez con más de 2/3 de vida | 8 | 6 |
| `plantas/nuez_agrietada.png` | Nuez entre 1/3 y 2/3 de vida | 8 | 6 |
| `plantas/nuez_mordida.png` | Nuez con menos de 1/3 de vida | 8 | 6 |
| `proyectiles/guisante.png` | Guisante | 1 | — |
| `plantas/cartman_idle.png` | Cartman quieto (respira y parpadea), x3 | 3 | 4 (secuencia) |
| `plantas/cartman_disparo.png` | Cartman disparando (el guisante sale en el frame 3), x3 | 3 | 8 |
| `plantas/kyle_idle.png` | Kyle de frente quieto, x3 | 3 | 4 (secuencia) |
| `plantas/kyle_completo.png` | Kyle: frame 3 = de perfil listo; frames 3 a 7 = patada (Ike sale en el 5) | 7 | 8 |
| `plantas/kenny_explosion.png` | Kenny: frames 1 a 5 se infla y explota; 6 a 30 restos y ratas | 30 | 10 / 12 |
| `plantas/toallin_idle.png` | Toallin fumando, x3 | 7 | 4 |
| `proyectiles/ike_volando.png` | Ike en el aire (1 salida, 2 inclinado, 3-5 girando, 6 cayendo; el 0 no se usa en el vuelo) | 7 | según la fase del vuelo |
| `proyectiles/ike_idle.png` | Ike de frente (todavía sin usar) | 2 | — |
| `zombies/zombie_normal_caminar.png` | Zombie caminando (frames de 32×48). Cono y cubeta usan el mismo cuerpo con el accesorio encima | 5 | 6 |

Mientras muerde, el zombie usa el primer frame con un cabeceo hacia adelante. Si después dibujás una
animación de comer, agregala como `zombie_normal_comer` y la conecto.

## Intro y menú

Al ejecutar `python main.py` pasa esto, en orden:

1. **Pantalla de carga** (`scenes/loading.py`): "PRESENTANDO..." y el nombre del juego mientras se preparan los gráficos y el audio.
2. **Intro** (`scenes/menu.py` + `ui/intro_art.py`): estilo la intro de South Park en pixel art. Se acerca la cabeza de Stan y caen la calle, los cuerpos y las cabezas de Cartman, Kyle, Stan y Kenny en la parada del bus. Está sincronizada con la canción `assets/musica/intro.mp3`.
3. **Menú**: cuando aterriza la cabeza de Cartman (a los 2,9 s) aparecen los tablones CONTINUAR (solo si hay partidas guardadas) / NUEVA PARTIDA / CATÁLOGO / OPCIONES / SALIR. La canción sigue sonando en bucle, los chicos cabecean al ritmo y de vez en cuando pasa el bus.

Controles del menú: mouse, o flechas arriba/abajo + Enter. Un clic (o Enter/Espacio/Esc) saltea la intro. Al volver al menú desde Opciones o desde una partida no se repite la intro. Al tocar NUEVA PARTIDA (o elegir una partida en CONTINUAR) se abre el mapa de niveles; la música se apaga con un fundido al entrar a un nivel.

Cosas que se pueden tocar:

| Qué | Dónde |
|---|---|
| Volumen de la música | `MUSICA_VOLUMEN` en `settings.py` |
| Cambiar la canción | reemplazar `assets/musica/intro.mp3` y ajustar `MUSICA_DURACION` en `settings.py` |
| Cuándo aterriza cada cabeza | `KIDS` (`head_t`, `body_t`) en `ui/intro_art.py` |
| Orden y lugar de los chicos | `KIDS` (`x`) en `ui/intro_art.py` |
| Botones (textos, posición) | `self.botones` en `MenuScene.__init__` y `BTN_X`, `BTN_Y0`, `BTN_DY` en `scenes/menu.py` |
| Sprites de los chicos | `assets/plantas/cartman_idle.png`, `kyle_idle.png`, `kenny_explosion.png` y `assets/personajes/stan_idle.png` (se usa el frame 0 de cada uno) |

La canción va a 145 BPM (un pulso cada 0,414 s) y los momentos clave de la intro caen sobre esos pulsos: Kenny en el pulso 5, Stan en el 6 y Cartman en el 7 (justo en la pausa de la canción).

## Partidas guardadas

Hay 10 ranuras ("Partida 1" a "Partida 10") en `partidas.json`, al lado de `main.py` (no se sube a git). Cada partida guarda los niveles ganados y la velocidad; un nivel a medio jugar no se guarda (al continuar se vuelve al mapa). La lógica está en `guardado.py` y el panel en `scenes/partidas.py`.

- **Nueva partida** arranca el progreso de cero, todavía sin ranura.
- **Continuar** abre el panel con las partidas y carga la elegida.
- **Pausa > Guardar** guarda en una ranura vacía, o pisa otra después de preguntar "¿De verdad quieres sobreescribir esta partida?". La partida pasa a usar esa ranura.
- **Guardado automático** al volver al menú principal, al ganar un nivel y al cerrar el juego: en la ranura de la partida o, si es nueva, en la primera libre. Si no hay ninguna libre no se guarda (el menú lo avisa).

## Sonido

Opciones > Sonido tiene un volumen General y uno para Música, Efectos, Personajes y Enemigos (slider de 0 a 100 % y casilla de silencio cada uno), más "Silenciar en segundo plano" (marcada por defecto). Los cambios se escuchan al momento y se guardan con Aplicar en `config.json` (clave `"sonido"`). Qué efecto va en cada categoría: `CATEGORIA` en `ui/sonidos.py`; el cálculo del volumen está en `ui/audio.py`. Desde la pausa también se puede abrir Opciones.
