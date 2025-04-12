# Implementación del Jugador para el Juego Hex
*Arianne Camila Palancar Ochando C311*

*Fecha: 2025-4-11*

## Resumen
Este informe presenta una descripción detallada de la implementación del jugador de Hex, incluyendo las estrategias, algoritmos y heurísticas utilizadas para tomar decisiones óptimas durante el juego.

## Introducción
El juego Hex es un juego de estrategia para dos jugadores que se juega en un tablero romboidal con casillas hexagonales. El jugador 1 (horizontal) intenta conectar los bordes izquierdo y derecho, mientras que el jugador 2 (vertical) intenta conectar los bordes superior e inferior.

## Representación del estado de juego
La implementación utiliza las siguientes estructuras para representar el estado del juego:

- El tablero se modela como una matriz de enteros donde:
  - 0 representa una casilla vacía
  - 1 representa una ficha del jugador 1 (conexión horizontal)
  - 2 representa una ficha del jugador 2 (conexión vertical)
    
- Se detectan grupos conectados (conjuntos de fichas del mismo color que están adyacentes) mediante búsqueda en profundidad (DFS).

- Los grupos se clasifican en categorías como:
  - **Top**: Grupos conectados al borde superior
  - **Bottom**: Grupos conectados al borde inferior
  - **Left**: Grupos conectados al borde izquierdo
  - **Right**: Grupos conectados al borde derecho
  - **TopBottom**: Grupos que conectan los bordes superior e inferior
  - **LeftRight**: Grupos que conectan los bordes izquierdo y derecho

## Algoritmo principal: Minimax con poda Alfa-Beta
El jugador implementa el algoritmo Minimax con poda Alfa-Beta para la toma de decisiones:

- **Profundidad máxima**: 5 niveles por defecto
- **Límite de tiempo**: Configurable, con verificaciones periódicas para evitar exceder el tiempo asignado
- **Función de evaluación**: Combina múltiples factores heurísticos

## Función de evaluación heurística
La evaluación del tablero se basa en tres componentes principales:

1. **Regiones de influencia**: Calcula el conjunto de casillas que están bajo el control o influencia de cada jugador.
2. **Conectividad**: Evalúa qué tan bien conectados están los grupos de cada jugador con sus respectivos bordes objetivo.
3. **Potencial de victoria**: Calcula la longitud de los caminos más cortos hacia la victoria para cada jugador.

La puntuación final se calcula como:
```
score = (len(player_influence) - len(opponent_influence)) +
        (player_connectivity - opponent_connectivity) +
        (player_potential - opponent_potential)
```

## Generación de movimientos candidatos
Para mejorar la eficiencia, el algoritmo no explora todos los movimientos posibles, sino que genera un conjunto de movimientos candidatos basados en reglas heurísticas:

### Reglas heurísticas implementadas
El método `generate_candidate_moves` implementa las siguientes reglas heurísticas (ordenadas por prioridad):

1. **Regla 1-2**: Verificar grupos TopBottom (para el jugador) o LeftRight (para el oponente) con portadores (carriers).
   - Si un grupo del jugador conecta los bordes superior e inferior, se identifican posiciones portadoras.
   - Si un grupo del oponente conecta los bordes izquierdo y derecho, se identifican posiciones portadoras.

2. **Regla 3-4**: Movimientos "uno para conectar" (OneToConnect) de grupos a bordes objetivo.
   - Si un grupo está conectado al borde superior, se generan movimientos que lo conectarían al borde inferior.
   - Si un grupo está conectado al borde inferior, se generan movimientos que lo conectarían al borde superior.

3. **Regla 5-6**: Movimientos "uno para conectar" entre grupos de bordes opuestos.
   - Se buscan movimientos que conectarían un grupo del borde superior con un grupo del borde inferior.

Además, el algoritmo implementa estrategias defensivas que no están explícitamente en las reglas originales:

### Estrategias defensivas adicionales
1. **Bloqueo de conexiones inminentes**: Bloquea movimientos del oponente que conectarían sus grupos con sus bordes objetivo.
   - Para el jugador horizontal, bloquea conexiones verticales del oponente.
   - Para el jugador vertical, bloquea conexiones horizontales del oponente.

2. **Bloqueo de conexiones entre grupos**: Impide que el oponente conecte sus grupos entre sí.
   - Identifica movimientos que conectarían dos grupos del oponente y los bloquea.

3. **Bloqueo de conexiones virtuales**: Identifica y bloquea patrones de "conexión virtual" que el oponente podría utilizar.
   - Detecta patrones de escalera (dos celdas vacías en fila que podrían conectar grupos).
   - Detecta patrones de puente (conexiones diagonales entre grupos).

### Estrategias ofensivas:
1. **Conexión de grupos propios**: Prioriza movimientos que conecten grupos propios con los bordes objetivo o entre sí.
2. **Movimientos "uno para conectar"**: Identifica posiciones que, con un solo movimiento, conectarían grupos propios con los bordes objetivo.
3. **Conexión entre grupos**: Busca movimientos que conecten grupos propios entre sí, especialmente aquellos que ya están conectados a bordes opuestos.

## Optimizaciones adicionales

### Libro de aperturas
El jugador utiliza un libro de aperturas predefinido para los primeros movimientos en tableros de diferentes tamaños:
- Para tableros 11x11: Posiciones centrales y cercanas al centro
- Para tableros más pequeños: Posiciones estratégicas específicas

### Estrategia de simetría
Cuando juega como segundo jugador, el algoritmo puede utilizar una estrategia de simetría:
- Si el primer jugador juega en el centro, responde con una posición adyacente
- Si el primer jugador juega fuera del centro, responde en el centro o en la posición simétrica
- Para movimientos posteriores, puede seguir respondiendo con movimientos simétricos

### Optimización del tiempo
El algoritmo monitorea constantemente el tiempo de ejecución y ajusta su comportamiento:
- Verifica periódicamente si se acerca al límite de tiempo (90% del máximo)
- Termina la búsqueda prematuramente si es necesario para garantizar una respuesta dentro del límite

## Algoritmos auxiliares

### Identificación de grupos
Utiliza búsqueda en profundidad (DFS) para identificar grupos conectados de piedras del mismo color.

### Cálculo de caminos más cortos
Implementa el algoritmo de Dijkstra para calcular la longitud del camino más corto entre bordes opuestos, considerando:
- Costo 0 para casillas con piedras propias
- Costo 1 para casillas vacías
- Costo infinito (no transitables) para casillas con piedras del oponente

## Conclusiones
La implementación combina técnicas clásicas de inteligencia artificial (Minimax, poda Alfa-Beta) con heurísticas específicas del dominio del juego Hex. Las estrategias ofensivas y defensivas, junto con las optimizaciones adicionales, permiten al jugador tomar decisiones efectivas dentro de las restricciones de tiempo establecidas.

## Referencias
[1] Yang, J., Liao, S., & Pawlak, M. (2001). "Another Solution of Hex". [Apply Heuristic Search to Discover a New Winning Solution in 8 × 8 Hex Game](https://webdocs.cs.ualberta.ca/~hayward/papers/yang8.pdf), 454-463.
