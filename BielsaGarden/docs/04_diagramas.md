# Bielsa Garden — Diagramas

| | |
|---|---|
| **Juego** | Bielsa Garden |
| **Materia** | _(a completar)_ |
| **Integrantes** | _(a completar)_ |
| **Fecha** | 5 de noviembre de 2026 |
| **Versión** | 1.0 |

---

Todos los diagramas están en Mermaid y reflejan las clases y los nombres del código. Las claves internas (por ejemplo, `girasol` o `aplastadora`) se conservan de versiones anteriores; la equivalencia con los nombres que ve el jugador está en el [Manual técnico](05_manual_tecnico.md#4-dónde-está-cada-cosa).

## 1. Diagrama de clases

### 1.1 Escenas, juego e interfaz

```mermaid
classDiagram
    direction LR
    class Game {
        +screen: Surface
        +scene: Scene
        +progreso: set
        +equipo: list
        +velocidad: int
        +intro_done: bool
        +change_scene(scene)
        +run()
    }
    class Scene {
        <<abstract>>
        +game: Game
        +handle_event(event)
        +update(dt)
        +draw(surface)
    }
    class LoadingScene
    class MenuScene
    class OptionsScene
    class MapaScene {
        +desbloqueado(idx) bool
        +estado(idx) str
    }
    class CatalogoScene
    class EquipoScene {
        +pool: list
        +equipo: list
        +jugar()
    }
    class GameplayScene {
        +level: dict
        +grid: Grid
        +zombies: list
        +projectiles: list
        +suns: list
        +mowers: list
        +sun: int
        +velocidad: int
        +paused: bool
        +dialogo: Dialogo
        +try_place(key, row, col) bool
        +collect_sun_at(pos) bool
        +dig(row, col) bool
        +cambiar_velocidad()
        +toggle_pausa()
        +finish(victory)
    }
    class ResultScene {
        +victory: bool
        +siguiente()
        +retry()
    }
    class HUD {
        +cards: list
        +card_at(pos) SeedCard
        +get_card(key) SeedCard
        +draw(...)
    }
    class SeedCard {
        +key: str
        +cooldown: float
        +ready(sun) bool
        +start_cooldown()
    }
    class Dialogo {
        +mensajes: list
        +retrato: str
        +terminado: bool
        +avanzar()
    }
    class CartelButton

    Game "1" o-- "1" Scene : escena actual
    Scene <|-- LoadingScene
    Scene <|-- MenuScene
    Scene <|-- OptionsScene
    Scene <|-- MapaScene
    Scene <|-- CatalogoScene
    Scene <|-- EquipoScene
    Scene <|-- GameplayScene
    Scene <|-- ResultScene
    GameplayScene "1" *-- "1" HUD
    HUD "1" *-- "1..9" SeedCard
    GameplayScene "1" o-- "0..1" Dialogo
    GameplayScene ..> ResultScene : crea al terminar
    MapaScene ..> EquipoScene : crea
    EquipoScene ..> GameplayScene : crea
    MenuScene ..> CartelButton
    ResultScene ..> CartelButton
```

### 1.2 Mundo, niveles, plantas, zombies y proyectiles

```mermaid
classDiagram
    direction TB
    class GameplayScene
    class Grid {
        +cells: list
        +ladders: set
        +fondo: str
        +place(plant)
        +remove(row, col)
        +is_free(row, col) bool
        +cell_at(pos)
    }
    class WaveManager {
        +pending: list
        +flags: list
        +update(dt) tuple
        +finished: bool
        +progress: float
    }
    class LawnMower {
        +row: int
        +active: bool
        +used: bool
        +update(dt, world)
    }
    class Level {
        <<dict en levels/>>
        id
        nombre
        fondo
        sol_inicial
        intervalo_sol_cielo
        oleadas
        plantas
        tutorial
    }
    class Sun {
        +value: int
        +clicked(pos) bool
    }

    class Plant {
        <<abstract>>
        +key: str
        +hp: int
        +row: int
        +col: int
        +update(dt, world)
        +take_damage(amount)
        +sprite_state()
    }
    class Sunflower["Sunflower (Chef Cartman)"]
    class Peashooter["Peashooter (Stan)"]
    class WallNut["WallNut (Butters)"]
    class Catapult["Catapult (Kyle)"]
    class Kenny
    class Toallin
    class Magnet["Magnet (Santi)"]
    class Picante["Picante (Jesús)"]
    class Aplastadora["Aplastadora (Gero)"]

    class Zombie {
        <<abstract>>
        +key: str
        +hp: int
        +armor: int
        +shield: int
        +speed: float
        +row: int
        +x: float
        +eating: bool
        +hypno: bool
        +update(dt, world)
        +take_damage(amount, frontal)
        +special(dt, world) bool
        +on_plant(target, world) bool
    }
    class NormalZombie
    class ConeZombie
    class BucketZombie
    class DoorZombie
    class NewspaperZombie
    class PoleZombie
    class LadderZombie
    class TractorZombie
    class BungeeZombie
    class DancerZombie
    class DiggerZombie
    class GiantZombie
    class MiniZombie
    class AlienZombie

    class Pea
    class Snowball
    class Ike

    GameplayScene "1" *-- "1" Grid
    GameplayScene "1" *-- "1" WaveManager
    GameplayScene "1" *-- "5" LawnMower
    GameplayScene "1" o-- "*" Zombie
    GameplayScene "1" o-- "*" Sun
    GameplayScene "1" o-- "*" Pea
    GameplayScene "1" o-- "*" Ike
    GameplayScene ..> Level : lee
    WaveManager ..> Level : lee las oleadas
    Grid "1" o-- "0..45" Plant

    Plant <|-- Sunflower
    Plant <|-- Peashooter
    Plant <|-- WallNut
    Plant <|-- Catapult
    Plant <|-- Kenny
    Plant <|-- Toallin
    Plant <|-- Magnet
    Plant <|-- Picante
    Plant <|-- Aplastadora

    Zombie <|-- NormalZombie
    Zombie <|-- ConeZombie
    Zombie <|-- BucketZombie
    Zombie <|-- DoorZombie
    Zombie <|-- NewspaperZombie
    Zombie <|-- PoleZombie
    Zombie <|-- LadderZombie
    Zombie <|-- TractorZombie
    Zombie <|-- BungeeZombie
    Zombie <|-- DancerZombie
    Zombie <|-- DiggerZombie
    Zombie <|-- GiantZombie
    Zombie <|-- MiniZombie
    Zombie <|-- AlienZombie

    Pea <|-- Snowball
    Sunflower ..> Sun : crea
    Peashooter ..> Snowball : dispara
    Catapult ..> Ike : patea
    Ike ..> Zombie : daña
    Snowball ..> Zombie : daña y ralentiza
    GiantZombie ..> MiniZombie : lanza
    DancerZombie ..> NormalZombie : invoca
    AlienZombie ..> Sunflower : apaga
```

## 2. Diagrama de estados de las escenas

```mermaid
stateDiagram-v2
    [*] --> Carga
    Carga --> Menu : gráficos y audio listos
    Menu --> Mapa : JUGAR
    Menu --> Catalogo : CATÁLOGO
    Menu --> Opciones : OPCIONES
    Menu --> [*] : SALIR
    Catalogo --> Menu : VOLVER / Esc
    Opciones --> Menu : APLICAR o VOLVER / Esc
    Mapa --> Menu : VOLVER / Esc
    Mapa --> Equipo : nivel 1, 2 o 3
    Mapa --> Partida : Tutorial
    Equipo --> Mapa : VOLVER / Esc
    Equipo --> Partida : ¡A JUGAR! (equipo no vacío)

    state Partida {
        [*] --> DialogoInicial
        DialogoInicial --> Jugando : se cierra el diálogo
        Jugando --> Pausa : P / Esc
        Pausa --> Jugando : CONTINUAR / P / Esc
        Jugando --> DialogoTutorial : paso del tutorial
        DialogoTutorial --> Jugando : se cierra el diálogo
        Jugando --> DialogoFinal : victoria o derrota
    }

    Pausa --> Mapa : VOLVER AL MAPA
    Pausa --> Menu : MENÚ PRINCIPAL
    DialogoFinal --> Resultado : clic o tecla
    Resultado --> Equipo : SIGUIENTE NIVEL / REINTENTAR
    Resultado --> Partida : REINTENTAR (tutorial)
    Resultado --> Mapa : VOLVER AL MAPA / Esc
    Resultado --> Menu : MENÚ PRINCIPAL
```

> Entre una escena y otra, `Game.change_scene` muestra una transición de "cortina de cartulina". Al entrar a un nivel desde el mapa hay además un fundido a negro.

## 3. Diagramas de estados de las entidades

### 3.1 Zombie (comportamiento general)

```mermaid
stateDiagram-v2
    [*] --> Caminando : aparece por la derecha
    Caminando --> Comiendo : hay una planta adelante
    Comiendo --> Caminando : la planta murió
    Caminando --> Especial : su tipo lo pide
    Comiendo --> Especial : su tipo lo pide
    Especial --> Caminando : termina la acción
    Caminando --> Trepando : la planta tiene escalera
    Trepando --> Caminando : la pasó
    Caminando --> Hipnotizado : mordió a Toallin
    Hipnotizado --> PeleandoAliado : zombie enemigo adelante
    PeleandoAliado --> Hipnotizado : el enemigo murió

    Caminando --> Muerto : vida = 0, podadora o Gero
    Comiendo --> Muerto : vida = 0, podadora o Gero
    Especial --> Muerto : vida = 0
    Hipnotizado --> Muerto : vida = 0 o sale de la pantalla
    Caminando --> LlegoALaCasa : cruza el borde sin podadora
    Muerto --> [*]
    LlegoALaCasa --> [*] : derrota

    note right of Especial
        Según el tipo:
        pértiga: salta la primera planta
        escalera: apoya la escalera (1 s)
        bailarín: baila e invoca (1,5 s)
        excavador: bajo tierra / sale
        bungee: aviso y caída
        gigante: golpe (1 s) / lanza al mini
        alien: aprieta el botón
        diario: queda quieto 1 s al perder el diario
    end note
    note left of Caminando
        En paralelo, una bola de nieve lo deja
        "ralentizado" 4 s: camina, come y
        se anima a la mitad de velocidad.
    end note
```

### 3.2 Gero (Aplastadora)

```mermaid
stateDiagram-v2
    [*] --> Quieta : se planta (espera 0,5 s)
    Quieta --> Preparando : zombie enfrente, o en su casilla si no puede avanzar
    Preparando --> Saltando : 0,5 s (frames 1 a 3)
    Saltando --> Aterrizando : 0,55 s (frames 4 a 6)
    Aterrizando --> Cansada : 0,5 s (frames 7 y 8)
    Cansada --> Quieta : 18 s de recarga
    Quieta --> [*] : la comen
    Cansada --> [*] : la comen

    note right of Aterrizando
        Al empezar este estado mata a todos
        los zombies de la casilla (frame 7).
    end note
    note left of Saltando
        No la pueden morder. Se muda a la
        casilla nueva al empezar el salto.
    end note
```

## 4. Diagramas de secuencia

### 4.1 Colocar una planta

```mermaid
sequenceDiagram
    actor J as Jugador
    participant G as GameplayScene
    participant H as HUD / SeedCard
    participant R as Grid
    participant P as Plant

    J->>G: clic en una carta (o tecla 1..9)
    G->>H: card_at(pos)
    H-->>G: carta
    G->>H: ready(energía)
    alt alcanza la energía y no está en recarga
        G->>G: selected = clave
    else no está lista
        G-->>J: no pasa nada
    end
    J->>G: clic en una casilla del césped
    G->>R: cell_at(pos)
    R-->>G: (fila, columna)
    G->>G: try_place(clave, fila, columna)
    G->>H: get_card(clave).ready(energía)
    G->>R: is_free(fila, columna)
    alt casilla libre y carta lista
        G->>P: create_plant(clave, fila, columna)
        G->>R: place(planta)
        G->>G: energía -= costo
        G->>H: start_cooldown()
        G->>G: selected = None
        G-->>J: la planta aparece y la carta se oscurece
    else casilla ocupada
        G-->>J: no se coloca (la carta sigue elegida)
    end
```

### 4.2 Un zombie llega a la podadora

```mermaid
sequenceDiagram
    participant G as GameplayScene
    participant Z as Zombie
    participant M as LawnMower (fila)
    participant O as Otros zombies de la fila

    loop cada paso de la partida
        G->>Z: update(dt, mundo)
        Z->>Z: x -= velocidad · dt
        G->>M: update(dt, mundo)
        M->>M: ¿hay un zombie de la fila con x < borde del césped?
    end
    alt la podadora está disponible
        M->>M: active = True, grita "¡TIMMY!"
        loop mientras cruza la fila
            M->>M: x += velocidad · dt
            M->>Z: alive = False (si lo alcanza)
            M->>O: alive = False (si los alcanza)
        end
        M->>M: sale de la pantalla: used = True
        G->>G: limpia los zombies muertos y suma eliminados
    else la podadora ya se usó
        Z->>Z: sigue caminando hasta la casa
        G->>G: check_end(): x < HOUSE_X
        G->>G: finish(victory=False)
        G-->>G: diálogo de derrota y pantalla de resultado
    end
```

## 5. Diagrama de arquitectura

```mermaid
flowchart TB
    main["main.py<br/>punto de entrada"] --> game["game.py<br/>bucle principal y cambio de escenas"]
    game --> display["display.py<br/>ventana, resolución, escalado"]
    game --> scenes

    subgraph scenes["scenes/ — pantallas"]
        loading[loading.py] --> menu[menu.py]
        menu --> options[options.py]
        menu --> catalogo[catalogo.py]
        menu --> mapa[mapa.py]
        mapa --> equipo[equipo.py]
        equipo --> gameplay[gameplay.py]
        gameplay --> result[result.py]
    end

    subgraph world["world/ — el tablero"]
        grid[grid.py]
        waves[wave_manager.py]
        mower[lawnmower.py]
    end

    subgraph entities["entities/ — lo que se mueve"]
        plants[plants.py]
        zombies[zombies.py]
        projectiles[projectiles.py]
        effects[effects.py]
        sun[sun.py]
    end

    subgraph ui["ui/ — interfaz y recursos"]
        hud[hud.py]
        dialogo[dialogo.py]
        sprites[sprites.py]
        button[button.py]
        font[pixel_font.py]
        sonidos[sonidos.py / musica.py]
        intro[intro_art.py]
    end

    subgraph datos["Datos"]
        settings["settings.py<br/>stats y constantes"]
        catalogoData["data/catalogo.py<br/>nombres y textos"]
        mapaData["data/mapa.py<br/>botones del mapa"]
        levels["levels/<br/>oleadas, tutorial, diálogos"]
    end

    assets[("assets/<br/>PNG, MP3, fondos")]
    tools["tools/<br/>generadores de sprites, fondos y mapa;<br/>pruebas simuladas"]

    gameplay --> world
    gameplay --> entities
    gameplay --> hud
    gameplay --> dialogo
    gameplay --> levels
    mapa --> mapaData
    catalogo --> catalogoData
    equipo --> levels
    entities --> settings
    entities --> sprites
    entities --> catalogoData
    world --> settings
    hud --> catalogoData
    sprites --> assets
    sonidos --> assets
    dialogo --> assets
    tools -. generan .-> assets
    tools -. prueban .-> gameplay
```
