Herramienta: Claude (Anthropic)

- fase de Diseño:

Objetivo: 
Implementar una animación de inicio de juego en la clase Game y rediseñar los gráficos vectoriales (pygame.draw) de la nave del jugador, enemigos y Boss para darles un aspecto futurista.


Prompts Exactos:

"Actúa como desarrollador de videojuegos en Pygame especializado en gráficos vectoriales. Tengo un proyecto en Python (main.py) donde dibujo las figuras mediante primitivas geométricas (pygame.draw.polygon, pygame.draw.circle) sin imágenes externas. Necesito agregar: 1) Una pantalla o animación de inicio antes de que comience el estado STATE_PLAYING (que diga 'Presiona ENTER para iniciar' con un efecto de parpadeo), y 2) Rediseñar el dibujo de la nave del jugador y del Boss en sus métodos draw() para darles una estética futurista detallada con luces e hilos de neón. Te consulto esto porque quiero mejorar el impacto visual desde el primer segundo de ejecución sin recurrir a archivos .png. Por favor, dame un ejemplo de código en Python que incluya las coordenadas relativas de los polígonos para el rediseño de la nave y la lógica del nuevo estado de inicio en Game."

Fundamentación (Las 4 Reglas de Oro):

Claridad: Solicita explícitamente la pantalla de inicio con parpadeo y los polígonos vectoriales para la nave futurista y el Boss.

Contexto: Explica que el juego usa un sistema basado en estados (STATE_PLAYING) y gráficos renderizados puramente por código en main.py.

Fundamentación: Justifica la necesidad de la consulta en crear una mejor experiencia e impacto visual inicial sin cargar imágenes externas.

Solicitud de ejemplos: Pide un ejemplo de código funcional con la lógica del estado de inicio y las coordenadas geométricas de los Sprites.

Verificación: Creé el estado STATE_START en la clase Game, agregué la captura de la tecla K_RETURN en handle_event y probé ejecutar el script; verifiqué que la pantalla de inicio se mostraba correctamente, parpadeaba el texto y que la nave del jugador mostraba sus nuevos vértices futuristas bien alineados.

- fase de tecnicas

Objetivo: Agregar la función de ataque potente con munición limitada mediante la tecla 'B' y equilibrar las variaciones de comportamiento en la lista de enemigos.

Prompt Exacto:

"Necesito adaptar las clases Player y Game de mi shooter vertical en Pygame para añadir un ataque especial de munición limitada. En mi código actual, controlo el disparo continuo en _handle_continuous_input() con Espacio o Z. Deseo implementar: 1) Un disparo masivo de proyectiles más grandes al presionar la tecla 'B', el cual consuma munición limitada (comenzando con 3 cargas), y 2) Que la munición actual se dibuje en el HUD (_draw_hud). Hago esta consulta porque quiero ofrecer una mecánica de emergencia estratégica al jugador cuando se acumulen muchos enemigos en pantalla. Proporcióname un ejemplo de cómo capturar el evento de la tecla 'B' en _handle_continuous_input(), restar munición, y generar los proyectiles especiales con una variante en la clase Bullet."

Fundamentación (Las 4 Reglas de Oro):

Claridad: Pide la implementación del disparo especial con la tecla 'B', control de munición limitada y su reflejo en el HUD.

Contexto: Menciona los métodos exactos de su script (_handle_continuous_input(), _draw_hud(), clase Bullet).

Fundamentación: Explica que la mecánica busca darle al jugador una opción estratégica de defensa ante situaciones de peligro.

-Fase de progresión de Nivel, Bosses y Power-ups Acumulables

Objetivo: Programar la aparición de objetos coleccionables (power-ups temporales), el enfrentamiento contra el Boss, el otorgamiento de mejoras permanentes acumulables y el cambio de color del escenario al subir de nivel.

Prompt Exacto:

"Necesito implementar el ciclo completo de progresión de nivel y power-ups en mi código de Pygame. Actualmente mi clase Boss no está integrada correctamente en _handle_collisions(). Requiero: 1) Una clase PowerUp que caiga del techo al destruir enemigos dando 'doble disparo' o 'disparo rápido' durante 5 segundos usando pygame.time.get_ticks(), 2) Hacer que al derrotar al Boss el jugador reciba una mejora permanente de velocidad que se pueda acumular (stackear) con los power-ups temporales, y 3) Cambiar los colores de las constantes COLOR_BG_TOP y COLOR_BG_BOTTOM para simular que avanzamos al Nivel 2. Te consulto esto porque me cuesta coordinar los temporizadores no bloqueantes y el cambio de nivel tras la muerte del Boss. Por favor, dame un ejemplo de código corto donde se muestre la colisión con el Boss, la entrega del poder permanente y la actualización del degradado de fondo."

Fundamentación (Las 4 Reglas de Oro):

Claridad: Solicita la clase PowerUp, temporizadores no bloqueantes, stacking de poderes permanentes y cambio de colores del mapa.

Contexto: Señala la falla en la llamada a Boss en _handle_collisions() de su código actual y el uso de degradados de color en el fondo.

Fundamentación: Expresa la dificultad técnica de gestionar estados temporales con pygame.time.get_ticks() sin congelar el juego.

Solicitud de ejemplos: Pide un ejemplo enfocado en la colisión del Boss, entrega de mejoras y la transición visual entre niveles.

Verificación: Invocé correctamente la clase Boss al alcanzar cierto puntaje, comprobé que al destruirlo soltara la mejora, verifiqué con un print() de consola que los temporizadores de los buffs temporales convivieran sin conflictos con la mejora permanente de velocidad, y confirmé que el fondo cambiara de color a un tono azul/púrpura al pasar al Nivel 2.

Solicitud de ejemplos: Solicita un ejemplo de código que muestre la detección de la tecla 'B', la modificación a Bullet y el dibujo en el HUD.

Verificación: Asigné una variable self.special_ammo = 3 en Player, probé presionar 'B' en partida para confirmar que solo disparaba si la munición era mayor a 0, verifiqué que la bala especial fuera más grande/destructiva y comprobé que el contador del HUD se actualizara en tiempo real.
