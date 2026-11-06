# Reporte de Entrega — Ejercicio 1: Q-learning en Cliff Walking

**Estudiante:** C-Ramirez  
**Algoritmo:** Q-learning tabular (Watkins) con conducta $\varepsilon$-greedy  
**Entorno:** Cliff Walking 4×12 (Sutton & Barto)  

---

## 1. Parámetros de la Corrida

| Parámetro | Valor |
|---|---|
| Tasa de aprendizaje ($\alpha$) | 0.5 |
| Factor de descuento ($\gamma$) | 1.0 (sin descuento) |
| Factor de exploración ($\varepsilon$) | 0.1 |
| Episodios de entrenamiento | 500 |
| Límite de pasos por episodio | 200 |
| Inicialización de la tabla $Q(s, a)$ | 0.0 |
| Orden de desempate de acciones | `N`, `E`, `S`, `W` |
| Semilla aleatoria fija | `42` |

---

## 2. Política Greedy Aprendida y Retorno Óptimo

### 2.1. Métricas de Evaluación Greedy ($\varepsilon = 0$)
- **Retorno greedy obtenido:** `-13.0`
- **Total de pasos:** `13`
- **Camino recorrido:**  
  `[(3, 0), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (3, 11)]`
- **Secuencia de acciones:**  
  `N -> E -> E -> E -> E -> E -> E -> E -> E -> E -> E -> E -> S`

### 2.2. Mapa de la Cuadrícula y Política Greedy con Flechas
Representación sobre la cuadrícula $4 \times 12$ donde:
- `S`: Inicio en `(3, 0)`
- `G`: Meta en `(3, 11)`
- `C`: Acantilado (The Cliff) en `(3, 1)` hasta `(3, 10)`
- `↑, →, ↓, ←`: Acción greedy en cada estado no terminal

```
      0   1   2   3   4   5   6   7   8   9  10  11 
    -------------------------------------------------
 0 |   ←   →   ↑   ↑   →   →   →   →   ↓   →   →   ↓ 
 1 |   ↓   ↓   →   →   ↓   →   ↓   →   →   →   ↓   ↓ 
 2 |   →   →   →   →   →   →   →   →   →   →   →   ↓ 
 3 |  S↑   C   C   C   C   C   C   C   C   C   C   G 
```

---

## 3. Recompensa Durante el Entrenamiento

- La serie completa de recompensas para los 500 episodios se encuentra guardada en `recompensas_entrenamiento.csv`.
- La visualización gráfica correspondiente (curva de recompensas por episodio y media móvil con ventana de 10 episodios) se encuentra guardada en `curva_aprendizaje.png`.
- **Media de recompensa (últimos 50 episodios):** `-40.08`
- **Media de recompensa (últimos 20 episodios):** `-41.65`

---

## 4. Preguntas de Análisis y Discusión Conceptual

### 4.1. ¿Por qué el camino de 13 pasos, pegado al acantilado, es óptimo?
En el entorno Cliff Walking, cada transición ordinaria (así como chocar contra las paredes) tiene una recompensa fija de $r = -1$. En consecuencia, maximizar el retorno acumulado sin descuento ($\gamma = 1$) es matemáticamente equivalente a minimizar el número de pasos necesarios para llegar desde la posición inicial $S = (3, 0)$ hasta la meta $G = (3, 11)$.

Cualquier camino válido debe evitar las casillas del acantilado situadas en la fila 3 (columnas 1 a 10). La trayectoria más directa consiste en:
1. Dar **1 paso al Norte** hacia $(2, 0)$ para salir de la fila del acantilado.
2. Dar **11 pasos al Este** a lo largo de toda la fila 2 hasta colocarse en $(2, 11)$, inmediatamente encima de la meta.
3. Dar **1 paso al Sur** para entrar a $G = (3, 11)$.

La suma de estos movimientos es exactamente $1 + 11 + 1 = 13$ pasos. Al recibir $r = -1$ por cada uno, el retorno óptimo es $13 \times (-1) = -13.0$. Si el agente subiera más al norte (filas 1 o 0), agregaría al menos dos pasos adicionales (uno para subir y otro para bajar), resultando en un camino más largo y un retorno subóptimo (ej. $-15$ o menor).

### 4.2. ¿Por qué la curva de entrenamiento queda por debajo de −13 aunque la política greedy ya sea óptima?
Durante la fase de entrenamiento, el agente selecciona sus acciones según la política de comportamiento $\varepsilon$-greedy con $\varepsilon = 0.1$. Esto significa que en el $10\%$ de las decisiones no se toma la acción óptima, sino una acción elegida de manera uniforme al azar.

Dado que el camino óptimo discurre por la fila 2, inmediatamente adyacente a la fila 3 (el acantilado), cualquier acción exploratoria aleatoria en dirección Sur (`S`) provoca que el agente caiga al abismo. Caer acarrea una severa penalización de $r = -100$ y reinicia al agente en $S$.

Q-learning es un algoritmo **off-policy**: la regla de actualización temporal (TD target) emplea el valor máximo futuro $\max_{a'} Q(s', a')$, evaluando la política óptima greedy independientemente de las acciones exploratorias tomadas. Sin embargo, la recompensa observada y registrada en la curva de aprendizaje durante el entrenamiento refleja la ejecución de la política de conducta con exploración activa ($\varepsilon = 0.1$). Por tanto, la curva se estabiliza alrededor de $\approx -40$ a $-50$, muy por debajo de $-13$, debido a las caídas ocasionales provocadas por la exploración.

### 4.3. En el paso que cae al acantilado, ¿cuál es $s'$ en el backup de Q-learning, y por qué ese backup no trata el acantilado como estado terminal?
- **Identificación de $s'$:**  
  De acuerdo con la especificación del libro de Sutton & Barto, al caer al acantilado el agente es enviado de vuelta a la casilla de inicio, por lo que el siguiente estado es:
  $$s' = S = (3, 0)$$
  La actualización temporal de Q-learning para esta transición es:
  $$Q(s, a) \leftarrow Q(s, a) + \alpha \left[ -100.0 + \gamma \max_{a'} Q(S, a') - Q(s, a) \right]$$

- **Por qué no es terminal:**  
  Las casillas de The Cliff actúan como un obstáculo dinámico penalizado dentro del entorno y no como la terminación de la tarea. El episodio no concluye (`done = False`), sino que continúa acumulando pasos y recompensas a partir de $S$ hasta alcanzar la meta $G = (3, 11)$ o el límite de pasos.  
  Si el acantilado se tratara erróneamente como un estado terminal, el valor futuro se anularía ($\max_{a'} Q(s', a') = 0$), ignorando el costo futuro esperado de reiniciar el recorrido desde $S$. Al mantener $s' = S$ no terminal, se preserva y propaga correctamente la dinámica descrita en la teoría de Sutton & Barto.

