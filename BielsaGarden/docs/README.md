# Bielsa Garden — Documentación del proyecto

| | |
|---|---|
| **Juego** | Bielsa Garden |
| **Materia** | _(a completar)_ |
| **Integrantes** | _(a completar)_ |
| **Fecha** | 5 de noviembre de 2026 |
| **Versión** | 1.0 |

---

## Índice

| N.º | Documento | Contenido |
|---|---|---|
| 01 | [Manual de usuario](01_manual_de_usuario.md) | Instalación, controles, pantallas, reglas del juego, tablas de plantas y zombies, niveles y preguntas frecuentes. |
| 02 | [Casos de uso](02_casos_de_uso.md) | Actores, diagrama de casos de uso y una ficha por cada caso. |
| 03 | [Requerimientos](03_requerimientos.md) | Requerimientos funcionales y no funcionales, y alcance de la versión. |
| 04 | [Diagramas](04_diagramas.md) | Diagramas de clases, de estados, de secuencia y de arquitectura. |
| 05 | [Manual técnico](05_manual_tecnico.md) | Estructura del código, dependencias, cómo extender el juego, formato de los sprites y decisiones de diseño. |
| 06 | [Plan de pruebas](06_plan_de_pruebas.md) | Casos de prueba con su resultado real y bugs conocidos. |
| 07 | [Diagrama de Gantt](07_gantt.md) | Actividades del proyecto agrupadas por etapa, para completar con fechas y responsables. |
| — | [img/](img/) | Capturas del juego usadas en los documentos. |

## Cómo leer esta documentación

- **Para jugar**, alcanza con el [Manual de usuario](01_manual_de_usuario.md).
- **Para entender qué hace el sistema**, se recomienda leer en orden los [Casos de uso](02_casos_de_uso.md) y los [Requerimientos](03_requerimientos.md). Cada requerimiento indica el caso de uso del que surge.
- **Para trabajar sobre el código**, conviene empezar por el diagrama de arquitectura de [Diagramas](04_diagramas.md) y seguir con el [Manual técnico](05_manual_tecnico.md).
- **Para verificar el funcionamiento**, el [Plan de pruebas](06_plan_de_pruebas.md) describe cada prueba. Todas se pueden repetir con `python tools/pruebas_simuladas.py`.

Los diagramas están escritos en Mermaid, dentro de los propios archivos. GitHub y la mayoría de los visores de Markdown (por ejemplo, Visual Studio Code con una extensión de Mermaid) los muestran como imágenes.

Todos los datos numéricos (costos, vida, velocidades, tiempos) se tomaron del código de esta versión, principalmente de `settings.py`. Si se modifican esos valores, las tablas de los documentos 01 y 05 deben actualizarse.

## Convenciones

- Las rutas de archivos son relativas a la carpeta del juego (donde está `main.py`).
- "Personaje" o "planta" designan a los defensores que coloca el jugador. El juego mantiene la terminología del género (*Plants vs. Zombies*), aunque los defensores sean personas.
- La pantalla del juego mide 1000 × 600 píxeles. Los valores en "px" se refieren a esa medida.
