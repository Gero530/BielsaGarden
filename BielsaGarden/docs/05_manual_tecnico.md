# Bielsa Garden — Manual técnico

| | |
|---|---|
| **Juego** | Bielsa Garden |
| **Materia** | _(a completar)_ |
| **Integrantes** | _(a completar)_ |
| **Fecha** | 5 de noviembre de 2026 |
| **Versión** | 1.0 |

---

## Índice

1. [Tecnologías y dependencias](#1-tecnologías-y-dependencias)
2. [Cómo ejecutarlo](#2-cómo-ejecutarlo)
3. [Estructura de carpetas](#3-estructura-de-carpetas)
4. [Dónde está cada cosa](#4-dónde-está-cada-cosa)
5. [Cómo extender el juego](#5-cómo-extender-el-juego)
6. [Sprites: formato y catálogo](#6-sprites-formato-y-catálogo)
7. [Decisiones de diseño](#7-decisiones-de-diseño)
8. [Herramientas de desarrollo](#8-herramientas-de-desarrollo)

---

## 1. Tecnologías y dependencias

| Elemento | Versión usada | Uso |
|---|---|---|
| Python | 3.8.10 | Lenguaje de todo el proyecto. |
| pygame-ce | 2.5.2 | Ventana, dibujo, entrada, sonido y música. |
| LibreSprite | — | Edición manual de los sprites (PNG). |
| Git / GitHub | — | Control de versiones (repositorio `Gero530/BielsaGarden`). |

No hay otras dependencias externas: el resto usa solo la biblioteca estándar de Python. Las herramientas de `tools/` usan también únicamente `pygame`.

## 2. Cómo ejecutarlo

```bash
pip install pygame-ce
python main.py
```

El juego debe ejecutarse desde su carpeta (la que contiene `main.py`), porque las rutas de `assets/` se arman a partir de la ubicación de los módulos.

La configuración de pantalla se guarda en `config.json`:

```json
{ "resolucion": [1000, 600], "pantalla_completa": false }
```

Para correr las pruebas automáticas, sin ventana:

```bash
python tools/pruebas_simuladas.py
```

## 3. Estructura de carpetas

```
BielsaGarden/
├── main.py                 Punto de entrada: crea Game y llama a run()
├── game.py                 Bucle principal, escena actual, transición de cortina, progreso en memoria
├── display.py              Ventana: resolución, pantalla completa, escalado, conversión del mouse, config.json
├── settings.py             Constantes y stats: pantalla, grilla, energía, PLANT_DATA, ZOMBIE_DATA, música, sonido
├── config.json             Configuración de pantalla elegida por el jugador
│
├── scenes/                 Una clase por pantalla (heredan de Scene)
│   ├── base.py             Scene: handle_event / update / draw
│   ├── loading.py          Pantalla de carga (precarga gráficos y audio)
│   ├── menu.py             Presentación animada y menú principal
│   ├── options.py          Opciones (resolución y pantalla completa)
│   ├── mapa.py             Mapa de niveles: desbloqueo, candados, flecha del próximo nivel
│   ├── catalogo.py         Catálogo de personajes y zombies (fichas y números)
│   ├── equipo.py           Elegí tu equipo (hasta EQUIPO_MAX) y zombies que vienen
│   ├── gameplay.py         Partida: grilla, entidades, HUD, oleadas, pausa, velocidad, tutorial, fin
│   └── result.py           Pantalla de victoria o derrota
│
├── world/                  El tablero
│   ├── grid.py             Grilla 5×9, casillas, escaleras puestas, fondo del nivel
│   ├── wave_manager.py     Suelta zombies según el horario del nivel; hordas, avisos y progreso
│   └── lawnmower.py        Podadoras (Timmy), una por fila
│
├── entities/               Lo que se mueve
│   ├── plants.py           Plant y una subclase por personaje; PLANT_CLASSES; ícono de las cartas
│   ├── zombies.py          Zombie y una subclase por tipo; ZOMBIE_CLASSES
│   ├── projectiles.py      Pea (base), Snowball (Stan) e Ike (Kyle)
│   ├── effects.py          Efectos: animaciones sueltas, destellos, texto flotante, metal volando, rayo
│   └── sun.py              El dedo de energía (cae, se junta, desaparece)
│
├── ui/                     Interfaz y recursos
│   ├── hud.py              Contador de energía, cartas con recarga, pala, velocidad, barra de progreso
│   ├── dialogo.py          Diálogo de Bielsa: retrato, burbuja, texto letra por letra
│   ├── sprites.py          Registro SPRITES, carga de tiras, animación y dibujo escalado
│   ├── button.py           Tablones de madera y botones (CartelButton)
│   ├── widgets.py          Pestañas, selector y casilla de verificación de Opciones
│   ├── pixel_font.py       Fuente de píxeles 5×7 propia
│   ├── fonts.py            Caché de fuentes del sistema
│   ├── intro_art.py        Arte del menú: fondo, nubes, bus, carteles colgantes, cortina
│   ├── sonidos.py          Efectos de sonido
│   └── musica.py           Música del menú y de la partida
│
├── levels/                 Contenido de los niveles
│   ├── __init__.py         LEVELS: lista ordenada de niveles
│   ├── tutorial.py         Tutorial: oleadas y pasos guiados
│   ├── level_1.py … level_3.py   Oleadas y configuración de cada nivel
│   └── dialogos.py         Frases de Bielsa
│
├── data/                   Datos de presentación
│   ├── catalogo.py         Nombres y descripciones; función nombre(clave)
│   └── mapa.py             Imagen del mapa y posición de cada botón de nivel
│
├── assets/                 Recursos (ver la sección 6)
├── tools/                  Generadores de sprites, fondos y mapa; pruebas simuladas (ver la sección 8)
└── docs/                   Esta documentación
```

## 4. Dónde está cada cosa

| Qué | Dónde | Notas |
|---|---|---|
| Stats de personajes | `settings.py` → `PLANT_DATA` | costo, vida, recarga y valores propios (cadencia, daño, alcance…). |
| Stats de zombies | `settings.py` → `ZOMBIE_DATA` | vida, armadura, escudo, velocidad (px/s), daño por segundo y valores propios. |
| Energía | `settings.py` → `SOL_VALOR`, `SOL_VIDA`, `SOL_VEL_CAIDA` | 25 por dedo; 9 s en el piso. |
| Tamaño máximo del equipo | `settings.py` → `EQUIPO_MAX` | 7. |
| Grilla y pantalla | `settings.py` → `GRID_*`, `CELL_*`, `SCREEN_*`, `HOUSE_X` | 5×9 casillas de 80×96 px. |
| Nombres y descripciones | `data/catalogo.py` → `PERSONAJES`, `ZOMBIES` | Único lugar de los nombres visibles. En el código se usa `nombre(clave)`. |
| Frases flotantes | `data/catalogo.py` → `FRASES_AL_PLANTAR`, `FRASE_KENNY_EXPLOTA` | |
| Frases de Bielsa | `levels/dialogos.py` | `TUTORIAL`, `ANTES_DEL_NIVEL`, `AL_GANAR`, `AL_PERDER`. |
| Retratos de Bielsa | `ui/dialogo.py` → `RETRATOS` | Archivo y posición de la boca de cada retrato. |
| Oleadas | `levels/level_N.py` → `"oleadas"` | Formato en `world/wave_manager.py`. |
| Pasos del tutorial | `levels/tutorial.py` → `"tutorial"` | Texto, acción esperada, pista, inicio de oleadas. |
| Fondo de cada nivel | `levels/level_N.py` → `"fondo"` | PNG de 250×150 en `assets/fondos/`. |
| Mapa | `data/mapa.py` | Imagen (`assets/mapa/fondo_mapa.png`) y centro de cada botón. |
| Sprites | `ui/sprites.py` → `SPRITES` | Ver la sección 6. |
| Sonidos y música | `ui/sonidos.py`, `ui/musica.py`, `settings.py` | Volúmenes y temas en `settings.py`. |

**Equivalencia de claves internas y nombres visibles**

| Clave interna | Nombre en el juego | Clase |
|---|---|---|
| `girasol` | Chef Cartman | `Sunflower` |
| `lanzaguisantes` | Stan | `Peashooter` |
| `nuez` | Butters | `WallNut` |
| `kyle` | Kyle | `Catapult` |
| `kenny` | Kenny | `Kenny` |
| `toallin` | Toallin | `Toallin` |
| `iman` | Santi | `Magnet` |
| `picante` | Jesús | `Picante` |
| `aplastadora` | Gero | `Aplastadora` |

Las claves internas se conservan de versiones anteriores para no romper el código ni los archivos de sprites. Los nombres que ve el jugador salen solo de `data/catalogo.py`.

## 5. Cómo extender el juego

### 5.1 Agregar un personaje (planta)

1. **Stats** — en `settings.py`, agregar una entrada en `PLANT_DATA` con al menos `costo`, `vida` y `recarga`, más los valores propios.
2. **Comportamiento** — en `entities/plants.py`, crear una subclase de `Plant` con `key = "clave"`. Sobrescribir `update(dt, world)` para su lógica y, si cambia de animación según su estado, `sprite_state()`. `world` es la `GameplayScene`: da acceso a `world.zombies`, `world.grid`, `world.projectiles`, `world.effects` y `world.suns`.
3. **Registro** — agregar la clase a la tupla de `PLANT_CLASSES` al final de `entities/plants.py`.
4. **Textos** — en `data/catalogo.py`, agregar `"clave": {"nombre": ..., "descripcion": ...}` en `PERSONAJES`. El orden de ese diccionario es el orden del catálogo y de la pantalla de equipo.
5. **Sprites** — poner la tira en `assets/plantas/` y registrarla en `SPRITES` de `ui/sprites.py` con la misma clave (sección 6). Si no hay sprite, `draw_plant_icon` dibuja una figura con formas.
6. **Disponibilidad** — aparece sola en la pantalla de equipo. Un nivel puede limitar los personajes con `"plantas": [...]`.

### 5.2 Agregar un zombie

1. **Stats** — en `settings.py`, agregar una entrada en `ZOMBIE_DATA` con `vida`, `velocidad` y `dps`, y opcionalmente `armadura` o `escudo`.
2. **Comportamiento** — en `entities/zombies.py`, crear una subclase de `Zombie` con `key` y `sprite_key`. Los ganchos disponibles son:
   - `special(dt, world)`: estados propios; devuelve `True` si ya se movió en ese paso.
   - `on_plant(target, world)`: qué hace al llegar a una planta; devuelve `True` si no se la come.
   - `sprite_state()`: qué animación mostrar.
   - Atributos de clase: `metal`, `escudo_total`, `puede_trepar`, `hipnotizable` y `aplasta_pisables`.
3. **Registro** — agregar la clase a `ZOMBIE_CLASSES`.
4. **Textos** — en `data/catalogo.py`, agregar la entrada en `ZOMBIES`.
5. **Sprites** — registrar en `SPRITES` la clave de caminar (`sprite_key`) y, opcionalmente, `sprite_key + "_atacar"`, que se usa sola mientras come.
6. **Usarlo** — nombrarlo en las oleadas de un nivel. La pantalla de equipo lo muestra en VIENEN automáticamente.

### 5.3 Agregar un nivel

1. Copiar `levels/level_3.py` como `levels/level_4.py` y cambiar el `"id"` (único), el `"nombre"`, `"sol_inicial"`, `"intervalo_sol_cielo"`, `"fondo"` y las `"oleadas"`.
2. Registrar el nivel en `LEVELS`, en `levels/__init__.py`. El orden de esa lista es el orden de desbloqueo.
3. Agregar su botón en `data/mapa.py` → `NIVELES` (el `id` debe coincidir). Si el `id` no existe, el mapa avisa con un error claro.
4. Opcional: generar un fondo nuevo agregando una función en `tools/fondos.py`.

**Formato de una oleada:**

```python
{"t": 120, "zombies": ["normal", "cono", ("cubeta", 2)], "bandera": True}
```

| Clave | Significado |
|---|---|
| `t` | Segundo en que empieza la oleada (desde que arrancan las oleadas). |
| `zombies` | Lista de tipos, o de pares `(tipo, fila)` para fijar la fila (0 = arriba). Sin fila, la elige al azar. |
| `cada` | Segundos entre un zombie y el siguiente de la misma oleada (1,5 por defecto; 0,8 en hordas). |
| `bandera` | Horda grande: cartel "¡Se viene una horda!" 3 s antes y bandera en la barra. |
| `final` | Oleada final: cartel "¡Oleada final!". |

Los avisos extra del nivel van en `"avisos"`, como una lista de `(segundo, texto[, sonido])`.

## 6. Sprites: formato y catálogo

### 6.1 Formato

- Cada animación es una **tira horizontal** en PNG con transparencia: los frames van uno al lado del otro, todos del mismo tamaño.
- Se registra en `SPRITES` (`ui/sprites.py`) con: `archivo`, `frame_w`, `frame_h` y `fps`, y opcionalmente:
  - `loop: False`: se reproduce una vez y queda en el último frame.
  - `frames: [i, …]`: usa solo esos frames de la tira (varias animaciones de un mismo PNG).
  - `seq: [i, …]`: orden de reproducción (repetir frames, parpadeos).
  - `mult`: multiplica la escala; `1.5` muestra el sprite x3 en vez de x2.
  - `dx`, `dy_px` e `icon_dy`: correcciones de posición en juego y en las cartas.
  - `icono`: frame fijo para la carta del HUD y el catálogo.
- **Escala**: todo se agranda por un número entero, sin suavizado. Los zombies se ven x2 y los personajes x3.
- **Orientación**: los zombies miran a la izquierda y tienen los pies en la última fila del frame.
- Si falta el archivo, el juego avisa en la consola y usa un dibujo con formas.

### 6.2 Sprites registrados

Tamaño de frame, cantidad de frames y fps tal como están en esta versión (medidos sobre los archivos).

**Personajes**

| Clave | Archivo | Frame | Frames | fps | Escala |
|---|---|---|---|---|---|
| girasol (Chef) | plantas/cartman_cocinando.png | 32×24 | 6 | 6 | x3 |
| girasol_sonda / girasol_deshabilitado | plantas/cartman_sonda.png / cartman_deshabilitado.png | 32×24 | 6 / 6 | 10 / 6 | x3 |
| lanzaguisantes (Stan) | plantas/stan_idle.png | 40×40 | 3 | 4 | x3 |
| lanzaguisantes_disparo | plantas/stan_disparo.png | 40×40 | 4 | 8 | x3 |
| nuez / nuez_comido (Butters) | plantas/butters_idle.png / butters_comido.png | 40×40 | 2 / 8 | 2 / 8 | x3 |
| kyle / kyle_patada | plantas/kyle_idle.png / kyle_completo.png | 38×38 | 3 / 5 de 7 | 4 / 8 | x3 |
| kenny / kenny_ratas | plantas/kenny_explosion.png | 32×32 | 5 / 25 de 31 | 10 / 12 | x3 |
| toallin | plantas/toallin_idle.png | 32×32 | 7 | 4 | x3 |
| iman / iman_atrae / iman_cargado (Santi) | plantas/iman_completo.png | 40×40 | 3 + 3 + 3 de 9 | 4 / 10 / 1 | x3 |
| picante / picante_explota (Jesús) | plantas/picante.png | 40×40 | 14 + 6 de 20 | 14 / 18 | x3 |
| picante_fuego | sprites/nuevos/picante_fuego.png | 26×32 | 6 | 12 | x3 |
| aplastadora / _salto / _cansada (Gero) | plantas/aplastadora_quieta.png / _salto.png / _cansada.png | 40×40 | 4 / 8 / 2 | 4 / elegido por código / 2 | x3 |

**Zombies** (todos en `assets/zombies/propios/` salvo el alien; caminar = 8 frames, atacar = 6)

| Zombie | Frame | Animaciones (frames) |
|---|---|---|
| Normal (también cono y balde) | 31×48 | caminar (8), atacar (6) |
| Puerta | 31×48 | con puerta y sin puerta: caminar (8), atacar (6) |
| Diario | 31×48 | normal y enojado: caminar (8), atacar (6) |
| Escalera | 31×48 | con y sin escalera: caminar (8), atacar (6); colocar (6) |
| Pértiga | 48×48 con pértiga, 31×48 sin | caminar (8), atacar (6), salto (6) |
| Excavador | 31×48 | con y sin pico: caminar (8), atacar (6); tierra (4) |
| Bailarín | 31×48 | caminar (8), atacar (6), baile (8) |
| Bungee | 31×48 | caminar (8), atacar (6), bajar (4) |
| Mini zombie | 20×32 | caminar (8), atacar (6) |
| Gigante | 44×64 | con y sin el mini: caminar (8), golpe (6); lanzar (6) |
| Tractor | 56×48 | caminar (8), atacar (6) |
| Alien | 31×48 | caminar (5) y botón (8) en `assets/zombies/`; atacar (6) |

**Otros**

| Clave | Archivo | Frame | Frames |
|---|---|---|---|
| dedo (energía) | soles/dedo_energia.png | 32×32 | 4 |
| bola_nieve | proyectiles/bola_nieve.png | 6×6 | 1 |
| ike | proyectiles/ike_volando.png | 38×38 | 7 |
| podadora / podadora_activa | podadora/timmy_idle.png / timmy_correr.png | 40×40 | 1 / 4 |
| escalera (apoyada) | zombies/propios/escalera_puesta.png | 20×40 | 1 |
| bungee_marca | sprites/nuevos/bungee_marca.png | 24×12 | 2 |
| cartman_festejo | sprites/nuevos/cartman_festejo.png | 32×40 | 4 |
| Retratos de Bielsa | dialogo/bielsa1.png, bielsa2.png, bielsa_victoria.png, bielsa_derrota.png | 768 × 654 a 900 (bloques de 6 px; se muestran a la mitad) | 1 |
| Fondos de nivel | fondos/tutorial.png, nivel1.png, nivel2.png, nivel3.png | 250×150 (se muestran x4) | 1 |
| Mapa | mapa/fondo_mapa.png | 250×150 (x4) | 1 |

## 7. Decisiones de diseño

### 7.1 Escenas

Cada pantalla es una subclase de `Scene` con tres métodos: `handle_event`, `update(dt)` y `draw(surface)`. `Game` mantiene una sola escena activa, le pasa los eventos y el tiempo, y la cambia con `change_scene`, que además dibuja la transición de cortina. Esto aísla cada pantalla y permite crear escenas nuevas sin tocar el bucle principal.

### 7.2 Resolución lógica fija

Todo se dibuja en una superficie de 1000 × 600 (`Game.screen`). `display.present()` la escala a la ventana o a la pantalla completa, y `display.convert_event()` traduce las coordenadas del mouse. Así el código de las escenas no depende de la resolución elegida.

### 7.3 Tiempo y velocidad x2/x3

El bucle corre a 60 cuadros por segundo y el tiempo de cada cuadro se limita a 50 ms, para que una demora no haga "saltar" a los zombies. Con velocidad x2 o x3, `GameplayScene.update` ejecuta **2 o 3 pasos normales de lógica por cuadro, con el mismo `dt`**, en lugar de multiplicar `dt`. De esta forma los disparos, choques y recargas se calculan exactamente igual que a x1, y el balance no cambia. Los diálogos, la pausa y los carteles avanzan a velocidad normal, y una pausa o un diálogo cortan los pasos pendientes de ese cuadro. La velocidad se guarda en `Game.velocidad` para el nivel siguiente.

### 7.4 Desbloqueo de niveles

`Game.progreso` es un conjunto con los `id` de los niveles ganados; vive **solo en memoria**. Un nivel está desbloqueado si es el primero de `LEVELS` o si el anterior está en `progreso`. `GameplayScene.finish(victory=True)` agrega el `id` antes de mostrar el diálogo final. El último equipo elegido se guarda de la misma forma en `Game.equipo`.

### 7.5 Daño, armadura y escudo

`Zombie.take_damage(amount, frontal)` aplica el daño en orden: primero el **escudo** (puerta o diario), solo si el golpe es frontal o el escudo cubre todo (el diario); después la **armadura** (cono o balde) y, por último, la **vida**. Ike y las explosiones usan `frontal=False`, por eso saltean la puerta.

### 7.6 Datos separados de la lógica

Los números están en `settings.py`, los textos en `data/catalogo.py` y `levels/dialogos.py`, y las oleadas en `levels/`. Esto permite balancear o reescribir el juego sin tocar las clases. Los nombres visibles salen de un único lugar (`nombre(clave)`), de modo que renombrar un personaje es un solo cambio.

### 7.7 Pixel art

Para mantener el estilo, todo se escala por enteros con `pygame.transform.scale` (vecino más cercano), nunca con `smoothscale`. El HUD y la burbuja del diálogo se dibujan a una resolución menor y se agrandan; la fuente es un mapa de bits propio (`ui/pixel_font.py`).

### 7.8 Tutorial dentro de la partida

El tutorial es un nivel normal con una lista de pasos. Cada paso tiene un diálogo y una condición de espera (`("planta", clave)`, `("juntar", n)`, `("muertes", n)`). `GameplayScene` comprueba la condición en cada paso de la lógica y, al cumplirse, muestra el siguiente. Los pasos seguidos que no esperan nada se agrupan en un mismo diálogo. Las oleadas no empiezan hasta el paso marcado con `"oleadas": True`.

## 8. Herramientas de desarrollo

| Herramienta | Uso |
|---|---|
| `tools/pruebas_simuladas.py` | 41 pruebas sin ventana de personajes, zombies, mecánicas, mapa, equipo, fin de nivel y tutorial (ver [06_plan_de_pruebas.md](06_plan_de_pruebas.md)). |
| `tools/zombies_pixel.py`, `tools/zombies_disenos.py` | Generan los sprites de los zombies a partir de mapas de píxeles escritos a mano (`assets/zombies/propios/`). `--preview` genera GIF de vista previa. |
| `tools/fondos.py` | Genera los fondos de los niveles a partir de `assets/fondos/A_vereda.png`. |
| `tools/mapa.py` | Genera el mapa de niveles. |
| `tools/generar_placeholders.py` | Genera sprites provisorios en `assets/sprites/nuevos/` (por ejemplo, el fuego de Jesús). |
| `tools/generar_vecinos.py`, `tools/preview_zombies.py`, `tools/zombies.px.js` | Herramientas de una versión anterior de los zombies; ya no se usan. |

Todos los generadores **no pisan** archivos existentes, salvo que se ejecuten con `--forzar`, para no perder retoques hechos a mano en LibreSprite.
