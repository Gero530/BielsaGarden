# Bielsa Garden — Plan de pruebas

| | |
|---|---|
| **Juego** | Bielsa Garden |
| **Materia** | _(a completar)_ |
| **Integrantes** | _(a completar)_ |
| **Fecha** | 5 de noviembre de 2026 |
| **Versión** | 1.0 |

---

## 1. Objetivo y alcance

Verificar que cada personaje, cada zombie y las mecánicas generales funcionan como describe el [Manual de usuario](01_manual_de_usuario.md), incluidas las interacciones poco frecuentes entre mecánicas, el mapa, la pantalla de equipo, la pausa, la velocidad y el fin de nivel.

## 2. Metodología

Se usaron dos tipos de prueba:

1. **Pruebas simuladas automáticas** (41 casos, prefijos PL, ZO, ME, MA, EQ, FI y TU). El script `tools/pruebas_simuladas.py` crea una partida real (`GameplayScene`) sin ventana, arma la situación de cada caso (coloca personajes y zombies en casillas concretas), avanza el tiempo a 60 pasos por segundo y compara el resultado con lo esperado. Para que los resultados se puedan repetir, la velocidad de los zombies se fija en su valor nominal, sin la variación aleatoria de ±8 % que tiene en el juego.
2. **Pruebas visuales** (prefijo VI). Se capturaron pantallas reales del juego, sin ventana, y se revisaron a simple vista. Esas capturas están en [img/](img/).

**Ejecución:** 5 de noviembre de 2026, Windows 10, Python 3.8.10, pygame-ce 2.5.2.

Para repetir las pruebas automáticas:

```bash
python tools/pruebas_simuladas.py
```

**Resultado general: 41 de 41 pruebas automáticas pasan; 8 de 8 pruebas visuales pasan.**

## 3. Casos de prueba

### 3.1 Personajes

| ID | Qué se prueba | Pasos | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|---|
| PL-01 | Producción de Chef Cartman | Plantar a Chef en (fila 2, col 0) sin soles del cielo; registrar cuándo aparece cada dedo durante 24 s. | Primer dedo a los 6 s y el segundo 18 s después. | Dedos producidos a los 6,0 s y 24,0 s. | Pasa |
| PL-02 | Juntar energía | Esperar el dedo de Chef con energía 0 y hacer clic sobre él. | La energía pasa a 25. | El clic lo junta; energía = 25. | Pasa |
| PL-03 | Disparo y ralentización de Stan | Stan en (2,1); zombie en otra fila durante 1,5 s; luego zombie en su fila durante 3 s. | No dispara sin blanco en su fila; al zombie de su fila le baja la vida y lo ralentiza. | Sin blanco no dispara; el zombie de su fila quedó con 180 de vida y ralentizado. | Pasa |
| PL-04 | Resistencia de Butters | Butters en (2,3) con un zombie normal mordiéndolo. | Muere a los ~40 s (4000 / 100). | Murió a los 40,0 s. | Pasa |
| PL-05 | Ike de Kyle | Kyle en (2,1), zombie en (2,7), 4 s. | Le baja la vida y no lo ralentiza. | Vida 160 (dos golpes de 20); sin ralentizar. | Pasa |
| PL-06 | Kenny: área, aliados y reaparición | Kenny en (2,4); balde en (1,5) (dentro del área), normal en (2,8) (fuera) y un hipnotizado en (3,3); 1 s; luego 30,5 s más. | Muere el balde, vive el de afuera, vive el hipnotizado; Kenny reaparece y espera. | Balde muerto; el de afuera vivo; el hipnotizado vivo; Kenny reapareció en espera. | Pasa |
| PL-07 | Hipnosis de Toallin | Toallin en (2,3) y un zombie mordiéndolo; 2 s. | El zombie queda hipnotizado, Toallin desaparece y el zombie camina a la derecha. | Hipnotizado; Toallin desapareció; avanza a la derecha. | Pasa |
| PL-08 | Santi saca el balde | Santi en (2,2), zombie con balde en (3,4); 2,5 s y luego 15 s. | Armadura 0, Santi "cargado"; a los 15 s vuelve a "listo". | Armadura 0, estado "cargado"; 15 s después, "listo". | Pasa |
| PL-09 | Santi saca la puerta | Santi en (2,2), zombie con puerta en (2,5); 2,5 s. | Escudo 0 y el zombie se dibuja sin puerta. | Escudo 0; sprite `zombie_puerta_sin`. | Pasa |
| PL-10 | Santi saca el pico del excavador | Santi en (2,3), excavador bajo tierra en (2,5); 3 s. | El excavador pierde el pico y sale a la superficie. | Sin metal; fase "camina"; fuera de la tierra. | Pasa |
| PL-11 | Explosión en cruz de Jesús | Jesús en (2,4); diario en (2,8) (su fila) y cono en (0,4) (su columna). | Explota a ~1,06 s; muere el diario (350); el cono sobrevive. | Explotó a los 1,07 s; diario muerto; cono vivo con 20 de armadura. | Pasa |
| PL-12 | Salto de Gero | Gero en (1,2); un gigante y un cono en la casilla (1,3); 2,5 s. | Mata a los dos (sin importar la vida), se muda a la columna 3 y queda cansado 18 s. | Ambos muertos; columna 3; cansado; recarga 18 s. | Pasa |
| PL-13 | Gero sin adónde saltar | Gero en la última columna (3,8), zombie en su casilla; 2,5 s. | Aplasta su propia casilla y no se mueve. | Zombie muerto; sigue en la columna 8. | Pasa |

### 3.2 Zombies

| ID | Qué se prueba | Pasos | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|---|
| ZO-01 | Zombie normal | Medir el avance durante 5 s; luego hacerlo morder a Butters durante 3 s. | 18 px/s; ~300 de daño en 3 s. | 18,0 px/s; Butters perdió 299. | Pasa |
| ZO-02 | Armadura de cono y balde | Aplicar 569 de daño al cono y 1299 al balde; luego 1 más a cada uno. | Siguen vivos y después mueren. | Vivos con 569/1299; muertos con 1 más. | Pasa |
| ZO-03 | Puerta frente a Stan y Kyle | Stan contra un zombie con puerta (3 s); en otra partida, Kyle contra otro (4 s). | Stan gasta la puerta sin dañar el cuerpo ni ralentizar; Ike daña el cuerpo sin tocar la puerta. | Stan: gasta la puerta, cuerpo intacto, sin ralentizar. Kyle: cuerpo 160, puerta 1100. | Pasa |
| ZO-04 | Diario roto | Aplicar 150 de daño a un zombie del diario. | Se enoja, queda quieto 1 s y su velocidad pasa a ~48. | Enojado; quieto 1,0 s; velocidad 49 (48 con la variación al azar). | Pasa |
| ZO-05 | Salto de la pértiga | Butters en (2,4), pértiga en (2,8); 12 s. | La pasa por arriba sin morderla, pierde la pértiga y camina a 18. | Pasó; Butters intacto; sin pértiga; velocidad 18. | Pasa |
| ZO-06 | Pértiga frente a una escalera (caso raro) | Butters en (2,4) con una escalera puesta, pértiga en (2,8). | Salta con la pértiga (no trepa la escalera). | Saltó con la pértiga. | Pasa |
| ZO-07 | Escalera compartida | Butters en (2,3), zombie con escalera en (2,6); 12 s; luego un normal en (2,5). | La escalera queda puesta y el normal pasa por arriba sin morder. | Escalera puesta; el normal la pasó; Butters sin mordidas. | Pasa |
| ZO-08 | Tractor frente a Toallin (caso raro) | Toallin en (2,4), tractor pegado; 3 s. | Se come a Toallin sin quedar hipnotizado. | Toallin comido; tractor no hipnotizado. | Pasa |
| ZO-09 | Caída del bungee | Crear 200 bungees y registrar su columna; dejar caer uno. | Columnas de 2 a 8; al caer pasa a "suelo". | Columnas [2…8]; fase "suelo". | Pasa |
| ZO-10 | Invocación del bailarín | Bailarín en (2,5); 2,5 s. | Invoca 4 zombies (adelante, atrás, arriba y abajo). | 5 zombies en el campo (1 + 4). | Pasa |
| ZO-11 | Recorrido completo del excavador | Stan en (2,0), excavador en (2,8); dejar correr hasta que se vaya. | Bajo tierra no recibe daño; sale en la columna 0, come la planta de atrás y se va por la derecha. | Intacto bajo tierra; salió; comió a Stan; se fue. | Pasa |
| ZO-12 | Gigante: golpe y lanzamiento | Butters en (2,3), gigante pegado; luego bajar la vida del gigante al 40 %. | Aplasta a Butters en ~1 s; lanza al mini, que cae cerca de la casa. | Aplastado a los 1,0 s; mini lanzado; cayó cerca de la casa. | Pasa |
| ZO-13 | Alien y Chef | Chef en (0,0), alien entrando por la fila 2; esperar el botón; luego eliminar al alien. | El Chef se apaga y vuelve a cocinar cuando el alien muere. | Chef apagado; al morir el alien, vuelve a cocinar. | Pasa |
| ZO-14 | Alien bloqueado por una planta | Butters en (2,8), alien pegado; 2 s. | El alien se la come. | Comiendo; Butters perdió 199. | Pasa |

### 3.3 Mecánicas generales y casos raros

| ID | Qué se prueba | Pasos | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|---|
| ME-01 | Podadora | Zombie en el borde de la fila 2 y un cono en (2,4); 4 s. | La podadora mata a los dos y queda usada. | Ambos muertos; podadora usada. | Pasa |
| ME-02 | Derrota | Podadora de la fila 2 gastada y un zombie en el borde; 4 s. | Se pierde el nivel y aparece el diálogo de derrota. | Resultado: derrota; retrato de derrota. | Pasa |
| ME-03 | Velocidad x2 | Pasar a x2 y medir el tiempo de juego que avanza en un cuadro; abrir otro nivel. | Avanza el doble y el nivel siguiente arranca en x2. | 0,0333 s por cuadro (x1 = 0,0167); el otro nivel arrancó en x2. | Pasa |
| ME-04 | Pausa | Pausar, apretar `1`, esperar 2 s y reanudar. | El zombie no se mueve, la tecla no elige cartas y al reanudar sigue. | Quieto en pausa; la tecla no tuvo efecto; al reanudar siguió. | Pasa |
| ME-05 | Validaciones al plantar | Con 150 de energía, plantar a Stan; repetir en la misma casilla, en otra (en recarga) y con 10 de energía. | Solo el primero se planta y cobra 100. | Plantó (energía 10); los otros tres intentos fueron rechazados. | Pasa |
| ME-06 | Recarga de la carta | Plantar a Stan y consultar la carta a los 7,4 s y a los 7,6 s. | No está lista antes de 7,5 s y sí después. | 7,4 s: no; 7,6 s: sí. | Pasa |
| ME-07 | Pala | Butters en (1,1); usar la pala. | La casilla queda libre. | Sacado; casilla libre. | Pasa |
| ME-08 | Pelea entre hipnotizado y enemigo (caso raro) | Un hipnotizado y un zombie enemigo enfrentados; 5 s. | Se muerden hasta que uno muere. | Murió el enemigo; el hipnotizado sigue vivo. | Pasa |
| ME-09 | Victoria | Nivel 1 sin oleadas pendientes ni zombies. | Cartel, diálogo de victoria y nivel registrado como ganado. | Victoria; retrato de victoria; nivel guardado. | Pasa |

### 3.4 Mapa, equipo y fin de nivel

| ID | Qué se prueba | Pasos | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|---|
| MA-01 | Desbloqueo del mapa | Consultar el estado de los 4 niveles sin progreso y con el tutorial ganado. | Solo el tutorial disponible; después, el nivel 1 disponible. | [disponible, bloqueado, bloqueado, bloqueado] → [ganado, disponible, bloqueado, bloqueado]. | Pasa |
| EQ-01 | Pantalla de equipo | Hacer clic en las 9 cartas; intentar jugar sin equipo; abrir otro nivel. | Máximo 7; sin equipo muestra el aviso; recuerda el último equipo. | 7 elegidos; aviso mostrado; equipo recordado. | Pasa |
| FI-01 | Diálogo antes del resultado | Perder un nivel, esperar el diálogo y hacer clic. | Recién con el clic aparece la pantalla de resultado. | La escena siguiente fue `ResultScene`. | Pasa |
| FI-02 | Botones del resultado | Crear el resultado de ganar el nivel 1, ganar el 3 y perder. | SIGUIENTE NIVEL solo al ganar un nivel que no es el último. | Nivel 1: con SIGUIENTE NIVEL; nivel 3 y derrota: sin él. | Pasa |
| TU-01 | Tutorial completo | Jugador automático que avanza cada diálogo, junta energía y planta Chef y Stan. | Se muestran las 12 frases, cada paso espera su acción y se gana. | 12 frases; victoria a los 116 s. | Pasa |

### 3.5 Pruebas visuales

| ID | Qué se prueba | Pasos | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|---|
| VI-01 | Menú principal | Abrir el juego y saltear la presentación. | Título y cuatro botones visibles. | Ver [img/menu.png](img/menu.png). | Pasa |
| VI-02 | Mapa | Abrir el mapa con el tutorial ganado. | T dorado, 1 con flecha, 2 y 3 con candado. | Ver [img/mapa.png](img/mapa.png). | Pasa |
| VI-03 | Catálogo | Pasar el mouse por Jesús y por el zombie con pértiga. | Ficha con nombre, descripción y números. | Ver [img/catalogo_personajes.png](img/catalogo_personajes.png). | Pasa |
| VI-04 | Partida y HUD | Nivel 2 con defensa y zombies. | Contador, cartas, pala, velocidad, barra con banderas y podadoras. | Ver [img/partida.png](img/partida.png). | Pasa |
| VI-05 | Pausa | Pausar la partida. | Tramado sobre la partida, cartel PAUSA y tres botones. | Ver [img/pausa.png](img/pausa.png). | Pasa |
| VI-06 | Diálogos | Tutorial, victoria y derrota. | Retrato correcto, colita hacia la boca, texto sin cortes. | Ver [img/dialogo_tutorial.png](img/dialogo_tutorial.png) y los de fin de nivel. Las 23 frases entran en la burbuja. | Pasa |
| VI-07 | Última fila | Plantas y zombies en la fila 5. | Pisan el pasto; la cerca de abajo queda por debajo de los pies. | Correcto en los cuatro fondos. | Pasa |
| VI-08 | Rendimiento | Nivel 3 con 150 zombies y las 45 casillas ocupadas, 300 cuadros. | Menos de 16,7 ms por cuadro. | Lógica 1,2 ms + dibujo 3,4 ms por cuadro. | Pasa |

## 4. Bugs conocidos y observaciones

Bugs del [informe de revisión](../informe_revision.html) que se volvieron a verificar y **ya están corregidos**:

| Bug anterior | Verificado por |
|---|---|
| El excavador volvía caminando y el nivel no terminaba. | ZO-11 (ahora se va de la pantalla). |
| Gero (Aplastadora) no hacía nada en la última columna. | PL-13 |
| La explosión de Kenny dañaba a los hipnotizados y la frenaba la puerta. | PL-06 |
| No se podía salir de un nivel desde la pausa. | VI-05 (botones VOLVER AL MAPA y MENÚ PRINCIPAL). |
| La bola de nieve frenaba al zombie aunque pegara en la puerta. | ZO-03 |
| La pértiga trepaba una escalera en vez de saltar. | ZO-06 |
| Con la pausa, las teclas 1 a 9 seguían eligiendo cartas. | ME-04 |
| Un id inexistente en `data/mapa.py` cerraba el juego con un error poco claro. | Revisión del código (ahora muestra un mensaje que indica los id válidos). |

Bugs y observaciones **pendientes**:

| N.º | Descripción | Prioridad |
|---|---|---|
| 1 | En las columnas 6 a 8 de la última fila, el nombre del nivel y la barra de progreso tapan la parte de abajo de la marca roja del bungee. Sigue visible, pero cortada. | Baja |
| 2 | El progreso (niveles ganados y último equipo) no se guarda en disco: al cerrar el juego se pierde. Es una limitación conocida de esta versión. | Media |
| 3 | El título de la ventana dice "Plantas vs Zombies - pygame" (`settings.TITLE`), mientras que el menú dice "BIELSA GARDEN". | Baja |
| 4 | `README.md` está desactualizado: menciona números y nombres viejos (por ejemplo, Picante con 200 de daño, Aplastadora con 8 s de recarga, el Imán) y las teclas 1 a 7. | Baja |
| 5 | `ui/sprites.py` todavía registra sprites que ya no se usan: PC Principal, Mr. Hankey, Mr. Mackey y el grito de Timmy (sus archivos no existen), y `cartman_baile`. No producen errores porque nunca se piden. | Baja |
| 6 | El cono y el balde se dibujan con figuras geométricas sobre el sprite del zombie, a diferencia del resto, que es pixel art. | Baja |
| 7 | Los nombres de los niveles 2 y 3 ("La calle", "El centro") y los dibujos del mapa (escuela, City Wok) no coinciden con los fondos actuales (otoño, atardecer). | Baja |
| 8 | En los diálogos, Bielsa llama "chili" a la energía, el HUD la llama "Cheesy Poofs" y lo que se junta son "dedos". | Baja |
| 9 | Hay herramientas de una versión anterior que ya no se usan: `tools/generar_vecinos.py`, `tools/preview_zombies.py` y `tools/zombies.px.js`. | Baja |
