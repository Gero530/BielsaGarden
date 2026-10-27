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
| Elegir planta | Clic en la carta (o teclas `1` a `6`) |
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
| Lanzaguisantes | 100 | 300 | Dispara guisantes (20 de daño) cada 1,4 s si hay un zombie en su fila |
| Nuez | 50 | 4000 | Muro que frena zombies |
| Kyle | 100 | 300 | Catapulta: cuando hay un zombie en su fila se da vuelta y patea a Ike, que vuela en arco y cae sobre el zombie (20 de daño, igual que el guisante) cada 1,4 s |
| Kenny | 150 | — | Como la cereza: explota al plantarlo (~0,5 s) y hace 1800 de daño en un área de 3x3 casillas. Después aparecen las ratas (solo decoración) |
| Toallin | 75 | 300 | Como la hipnoseta: el zombie que lo muerde se lo come y queda hipnotizado (violeta, camina a la derecha y muerde a los zombies que encuentra) |

**Zombies**

| Zombie | Vida | Armadura |
|---|---|---|
| Normal | 200 | — |
| Cono | 200 | 370 |
| Cubeta | 200 | 1100 |

**Nivel 1**: 16 zombies en ~3 minutos, con oleada final. Cada fila tiene un cortacésped de un solo uso.
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
  result.py          Pantalla de victoria / derrota

world/
  grid.py            Grilla 5x9: celdas, colocación de plantas, dibujo del césped
  wave_manager.py    Suelta zombies según el horario del nivel
  lawnmower.py       Cortacéspedes

entities/
  plants.py          Plant + Chef (Cartman cocinando, clave `girasol`), Lanzaguisantes (Cartman), Nuez, Kyle, Kenny, Toallin
  zombies.py         Zombie + Normal, Cono, Cubeta
  projectiles.py     Guisante e Ike (proyectil en arco)
  effects.py         Efectos visuales: animación suelta (ratas de Kenny) y destello del área
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
  level_1.py         Oleadas y avisos del nivel 1
```

## Cómo extender

- **Nueva planta**: datos en `settings.PLANT_DATA` → clase en `entities/plants.py` → registrar en `PLANT_CLASSES` → agregar su key en `"plantas"` del nivel.
- **Nuevo zombie**: datos en `settings.ZOMBIE_DATA` → clase en `entities/zombies.py` → registrar en `ZOMBIE_CLASSES`.
- **Nuevo nivel**: copiar `levels/level_1.py` como `level_2.py`, cambiar las oleadas y agregarlo a `LEVELS` en `levels/__init__.py`.
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
