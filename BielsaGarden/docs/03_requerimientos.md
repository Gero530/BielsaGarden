# Bielsa Garden — Requerimientos

| | |
|---|---|
| **Juego** | Bielsa Garden |
| **Materia** | _(a completar)_ |
| **Integrantes** | _(a completar)_ |
| **Fecha** | 5 de noviembre de 2026 |
| **Versión** | 1.0 |

---

## 1. Requerimientos funcionales

Cada requerimiento indica el caso de uso del que surge ([02_casos_de_uso.md](02_casos_de_uso.md)).

### 1.1 Inicio, menús y configuración

| ID | Requerimiento | Caso de uso |
|---|---|---|
| RF-01 | El sistema debe mostrar una pantalla de carga mientras prepara los gráficos y el audio. | CU-01 |
| RF-02 | El sistema debe mostrar una presentación animada con música al iniciar, que el jugador pueda saltear con un clic o con `Enter`, `Espacio` o `Esc`, y que no se repita en la misma ejecución. | CU-01 |
| RF-03 | El menú principal debe ofrecer las opciones JUGAR, CATÁLOGO, OPCIONES y SALIR, operables con el mouse y con el teclado. | CU-01 |
| RF-04 | El sistema debe permitir elegir la resolución de la ventana entre las que entran en el monitor, y activar o desactivar la pantalla completa. | CU-02 |
| RF-05 | Los cambios de configuración deben aplicarse solo al confirmar, guardarse en un archivo y recuperarse al volver a abrir el juego. | CU-02 |
| RF-06 | El catálogo debe mostrar todos los personajes y todos los zombies, con nombre, descripción y números (costo, daño, vida y recarga de los personajes; vida total, daño y velocidad de los zombies). | CU-04 |

### 1.2 Mapa y equipo

| ID | Requerimiento | Caso de uso |
|---|---|---|
| RF-07 | El mapa debe mostrar los niveles en orden, cada uno como bloqueado, disponible o ganado, e indicar cuál es el próximo nivel por jugar. | CU-03 |
| RF-08 | Al iniciar el juego solo el tutorial debe estar disponible; ganar un nivel debe desbloquear el siguiente. | CU-03, CU-13 |
| RF-09 | Antes de cada nivel (salvo el tutorial), el sistema debe permitir elegir un equipo de entre 1 y 7 personajes y mostrar los zombies que aparecen en ese nivel. | CU-05 |
| RF-10 | El sistema debe recordar el último equipo elegido mientras el juego esté abierto. | CU-05, CU-15 |

### 1.3 Partida

| ID | Requerimiento | Caso de uso |
|---|---|---|
| RF-11 | La partida debe desarrollarse en un césped de 5 filas por 9 columnas; los zombies deben avanzar de derecha a izquierda. | CU-06 |
| RF-12 | El sistema debe soltar a los zombies según el horario de oleadas definido para cada nivel, anunciar cada horda con un cartel y mostrar el progreso con una barra con banderas. | CU-06 |
| RF-13 | El sistema debe generar energía en forma de dedos que caen del cielo a intervalos fijos y que suelta Chef Cartman; cada dedo debe valer 25 y desaparecer si no se lo junta a tiempo. | CU-08 |
| RF-14 | El jugador debe poder juntar un dedo haciendo clic sobre él, con prioridad sobre otras acciones. | CU-08 |
| RF-15 | El jugador debe poder colocar un personaje del equipo en una casilla libre, siempre que tenga la energía suficiente y la carta no esté en recarga; al hacerlo, el sistema debe descontar el costo e iniciar la recarga. | CU-07 |
| RF-16 | Las cartas deben poder elegirse con el mouse o con las teclas `1` a `9`, y la selección debe poder cancelarse. | CU-07 |
| RF-17 | El jugador debe poder quitar un personaje con la pala (botón o tecla `S`), sin recuperar la energía. | CU-09 |
| RF-18 | Cada personaje debe cumplir su función automáticamente según su tipo (generar energía, disparar, resistir, explotar, hipnotizar, quitar metal, aplastar). | CU-06 |
| RF-19 | Cada zombie debe comportarse según su tipo (armadura, escudo, salto, escalera, caída del cielo, invocación, avance bajo tierra, lanzamiento del mini zombie, apagado de los generadores). | CU-06 |
| RF-20 | Cada fila debe tener una podadora de un solo uso que se active cuando un zombie llega al borde izquierdo y elimine a los zombies de esa fila. | CU-06 |
| RF-21 | El jugador debe poder alternar la velocidad de la partida entre x1, x2 y x3 sin que cambien las reglas, y la velocidad elegida debe mantenerse entre niveles. | CU-10 |
| RF-22 | El jugador debe poder pausar la partida y, desde la pausa, continuar, volver al mapa o ir al menú principal. Durante la pausa no deben aceptarse acciones de juego. | CU-11 |

### 1.4 Fin de nivel, tutorial y diálogos

| ID | Requerimiento | Caso de uso |
|---|---|---|
| RF-23 | El sistema debe declarar la victoria cuando no queden oleadas pendientes ni zombies enemigos; los zombies hipnotizados no deben impedirla. | CU-13 |
| RF-24 | El sistema debe declarar la derrota cuando un zombie enemigo llegue a la casa. | CU-14 |
| RF-25 | Al terminar un nivel, el sistema debe mostrar primero un diálogo de Bielsa (de victoria o de derrota) y después la pantalla de resultado con los zombies eliminados, el tiempo y las acciones disponibles. | CU-13, CU-14 |
| RF-26 | La pantalla de resultado debe ofrecer SIGUIENTE NIVEL (solo al ganar un nivel que no sea el último), REINTENTAR, VOLVER AL MAPA y MENÚ PRINCIPAL. | CU-13, CU-14, CU-15 |
| RF-27 | El tutorial debe guiar al jugador paso a paso con diálogos de Bielsa, esperar a que realice cada acción pedida antes de continuar y mostrar una pista mientras espera. | CU-12 |
| RF-28 | Antes de cada nivel (salvo el tutorial), Bielsa debe decir una frase elegida al azar de una lista. | CU-06, CU-16 |
| RF-29 | Los diálogos deben mostrar el texto letra por letra, completarlo con un clic, avanzar con un clic o cualquier tecla y poder saltearse con `Esc`. Mientras haya un diálogo, la partida debe quedar detenida. | CU-16 |

## 2. Requerimientos no funcionales

| ID | Categoría | Requerimiento |
|---|---|---|
| RNF-01 | Rendimiento | El juego debe funcionar a 60 cuadros por segundo (16,7 ms por cuadro). Medición de esta versión, sin ventana, con el nivel 3, 150 zombies iniciales (182 con los invocados) y las 45 casillas ocupadas al comenzar: la lógica tardó en promedio 1,2 ms y el dibujo 3,4 ms por cuadro. |
| RNF-02 | Rendimiento | Una demora puntual del sistema no debe hacer saltar a las entidades: el tiempo de cada cuadro se limita a 50 ms. |
| RNF-03 | Plataforma | El juego debe ejecutarse en una computadora de escritorio con Python 3.8 o superior y `pygame-ce`. Se desarrolló y se probó en Windows 10. |
| RNF-04 | Resolución | El juego debe dibujarse a 1000 × 600 píxeles y escalarse a la resolución elegida o a la pantalla completa, sin deformarse. En Windows con escalado de pantalla, la ventana no debe verse borrosa. |
| RNF-05 | Estética | Todos los gráficos deben respetar el estilo pixel art: se agrandan por números enteros (x2 o x3) y sin suavizado; la interfaz usa tablones de madera y una fuente de píxeles propia. |
| RNF-06 | Usabilidad | Todas las acciones deben poder hacerse con el mouse; las más frecuentes deben tener atajo de teclado. Cada pantalla debe poder abandonarse con `Esc`. |
| RNF-07 | Usabilidad | El juego debe dar respuesta visual a las acciones: cartas oscurecidas cuando no se pueden usar, casilla resaltada al plantar, destello al recibir daño, carteles de horda. |
| RNF-08 | Usabilidad | Los textos deben estar en español rioplatense y leerse sin cortes de palabras dentro de su recuadro. |
| RNF-09 | Mantenibilidad | Los números de balance deben estar centralizados en `settings.py`; los nombres y descripciones, en `data/catalogo.py`; las frases de Bielsa, en `levels/dialogos.py`; las oleadas, en un archivo por nivel. |
| RNF-10 | Mantenibilidad | Agregar un personaje, un zombie o un nivel no debe requerir modificar la lógica general: solo registrarlo en los lugares previstos (ver el [Manual técnico](05_manual_tecnico.md)). |
| RNF-11 | Robustez | Si falta un archivo de imagen, el juego no debe cerrarse: debe usar un dibujo alternativo y avisar en la consola. Si falta el audio, debe continuar sin sonido. |
| RNF-12 | Verificabilidad | Las mecánicas deben poder probarse sin ventana, con el script `tools/pruebas_simuladas.py`. |

## 3. Alcance

### 3.1 Incluido en esta versión

- Un tutorial guiado y tres niveles, con desbloqueo progresivo.
- Nueve personajes: Chef Cartman, Stan, Butters, Kyle, Kenny, Toallin, Santi, Jesús y Gero.
- Catorce tipos de zombie: normal, cono, balde, puerta, diario, pértiga, escalera, tractor, bungee, bailarín, excavador, gigante, mini zombie y alien.
- Mapa de niveles, catálogo, pantalla de equipo, pausa y pantalla de resultado.
- Velocidad x1, x2 y x3.
- Diálogos de Bielsa con retratos.
- Opciones de resolución y pantalla completa.
- Música y efectos de sonido.
- Fondos propios para cada nivel.

### 3.2 Fuera del alcance de esta versión

- **Guardado del progreso en disco**: los niveles ganados y el último equipo se pierden al cerrar el juego.
- **Opciones de sonido**: no hay control de volumen dentro del juego; los volúmenes se ajustan en `settings.py`.
- **Modos de juego adicionales** (supervivencia, minijuegos, nivel infinito) y niveles nocturnos o con agua.
- **Multijugador**.
- **Idiomas distintos del español**.
- **Instalador o ejecutable**: el juego se ejecuta desde el código fuente con Python.
- **Personajes eliminados durante el desarrollo**: PC Principal, Mr. Hankey y Mr. Mackey (se quitaron en el commit `21fd3cb`).
