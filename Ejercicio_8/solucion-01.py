import csv
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuración de matplotlib para entornos sin interfaz gráfica
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


@dataclass
class MoveResult:
    nxt: tuple[int, int]
    reward: float
    done: bool


class World:
    """
    Entorno Cliff Walking (Sutton & Barto):
    - Cuadrícula de 4 filas x 12 columnas.
    - S = (3, 0), G = (3, 11), Cliffs = (3, 1) ... (3, 10).
    - Acciones: 'N', 'E', 'S', 'W'.
    - Transición regular o choque con pared: r = -1.0.
    - Caída al acantilado: r = -100.0, s' = S, done = False (el episodio continúa).
    - Meta G: r = -1.0, s' = G, done = True (el episodio termina).
    """
    _actions = ('N', 'E', 'S', 'W')
    _cliff_reward = -100.0
    _cell_reward = -1.0
    _arrows = {'N': '↑', 'E': '→', 'S': '↓', 'W': '←'}

    def __init__(
        self,
        rows: int = 4,
        cols: int = 12,
        start: tuple[int, int] = (3, 0),
        goal: tuple[int, int] = (3, 11),
        cliffs: Optional[List[tuple[int, int]]] = None
    ):
        if cliffs is None:
            cliffs = [(3, c) for c in range(1, 11)]
        if start in cliffs or goal in cliffs:
            raise ValueError("Start and Goal cannot be in cliffs")
        self._rows = rows
        self._cols = cols
        self._start = start
        self._goal = goal
        self._cliffs = cliffs
        self.terminals = {self._goal}
        self._create_world()
        self._generate_labels()

    def _create_world(self):
        def reward(cell):
            if cell in self._cliffs:
                return type(self)._cliff_reward
            return type(self)._cell_reward
        self._world = [[reward((row, col)) for col in range(self._cols)] for row in range(self._rows)]
        self.non_terminals = [
            (r, c) for r in range(self._rows) for c in range(self._cols)
            if (r, c) not in self.terminals and (r, c) not in self._cliffs
        ]

    def _generate_labels(self):
        def label(cell):
            if cell == self._start:
                return 'S'
            elif cell == self._goal:
                return 'G'
            elif cell in self._cliffs:
                return 'C'
            return '.'
            
        self.labels = [[label((row, col)) for col in range(self._cols)] for row in range(self._rows)]

    def render_world(self) -> str:
        """Devuelve una representación visual en texto del mapa del entorno."""
        lines = []
        header = "      " + " ".join(f"{c:^3}" for c in range(self._cols))
        lines.append(header)
        lines.append("    " + "-" * (len(header) - 4))
        for r in range(self._rows):
            row_str = " ".join(f"{self.labels[r][c]:^3}" for c in range(self._cols))
            lines.append(f" {r} |  {row_str}")
        return "\n".join(lines)

    def step(self, cell: tuple[int, int], mov: str) -> MoveResult:
        r, c = cell
        if mov == 'N':
            r -= 1
        elif mov == 'S':
            r += 1
        elif mov == 'E':
            c += 1
        elif mov == 'W':
            c -= 1
        
        # Choque con la pared: se queda en la misma casilla, r = -1, done = False
        if not (0 <= r < self._rows and 0 <= c < self._cols):
            return MoveResult(cell, self._cell_reward, False)
        
        nxt = (r, c)
        # Caída al acantilado: regresa a START, r = -100, done = False (el episodio sigue)
        if nxt in self._cliffs:
            return MoveResult(self._start, self._cliff_reward, False)
        
        # Meta: llega a GOAL, r = -1, done = True (el episodio termina)
        if nxt == self._goal:
            return MoveResult(self._goal, self._cell_reward, True)
        
        # Paso ordinario: r = -1, done = False
        return MoveResult(nxt, self._cell_reward, False) 
    
    @classmethod
    @property
    def actions(cls):
        return cls._actions

    @property
    def start(self):
        return self._start

    @property
    def goal(self):
        return self._goal

    @property
    def rows(self):
        return self._rows

    @property
    def cols(self):
        return self._cols

    @property
    def cliffs(self):
        return self._cliffs


class Q_Learning:
    def __init__(self, world: World, alpha: float = 0.5, gamma: float = 1.0):
        self._world = world
        self._alpha = alpha
        self._gamma = gamma

    def _argmax_action(self, Q: dict, state: tuple[int, int], actions: tuple[str, ...]) -> str:
        """
        Selecciona la acción con el mayor Q(s, a).
        En caso de empates, la primera acción en el orden fijo de actions gana (ej. N, E, S, W).
        """
        best = actions[0]
        best_v = Q[state][best]
        for a in actions[1:]:
            if Q[state][a] > best_v:
                best, best_v = a, Q[state][a]
        return best

    def _epsilon_greedy(
        self,
        Q: dict[tuple[int, int], dict[str, float]],
        state: tuple[int, int],
        actions: tuple[str, ...],
        epsilon: float,
        rng: random.Random,
    ) -> str:
        if state not in Q:
            return actions[0]
        if rng.random() < epsilon:
            return rng.choice(list(actions))
        return self._argmax_action(Q, state, actions)

    def _max_q(self, Q: dict[tuple[int, int], dict[str, float]], state: tuple[int, int], actions: tuple[str, ...]) -> float:
        if state not in Q:
            return 0.0
        return max(Q[state][a] for a in actions)

    def _td_target_q(
        self,
        Q: dict[tuple[int, int], dict[str, float]],
        reward: float,
        nxt: tuple[int, int],
        done: bool,
    ) -> float:
        # Si nxt es terminal (meta), el valor futuro es 0.
        # Si nxt es Start tras caer, Start no es terminal: se usa max_a' Q(S, a').
        future = 0.0 if done else self._max_q(Q, nxt, self._world.actions)
        return reward + self._gamma * future

    def _apply_update(
        self,
        Q: dict[tuple[int, int], dict[str, float]],
        state: tuple[int, int],
        action: str,
        target: float,
        alpha: float,
    ) -> float:
        old = Q[state][action]
        Q[state][action] = old + alpha * (target - old)
        return Q[state][action]

    def train(
        self,
        rng: random.Random,
        epsilon: float = 0.1,
        episodes: int = 500,
        max_steps: int = 200
    ) -> tuple[dict[tuple[int, int], dict[str, float]], list[float]]:
        """
        Entrenamiento de Q-learning tabular:
        - Inicializa Q(s, a) = 0 para cada estado no terminal y acción.
        - Para cada episodio, parte de Start y sigue la política epsilon-greedy.
        - Actualiza con la regla off-policy de Watkins usando el máximo del estado siguiente.
        """
        n = episodes
        eps = epsilon
        Q = {s: {a: 0.0 for a in self._world.actions} for s in self._world.non_terminals}

        returns: list[float] = []
        for _ in range(n):
            s = self._world.start
            G = 0.0
            a = self._epsilon_greedy(Q, s, self._world.actions, eps, rng)
            for _step in range(max_steps):
                if s not in Q:
                    break
                tr = self._world.step(s, a)
                G += tr.reward
                target = self._td_target_q(Q, tr.reward, tr.nxt, tr.done)
                self._apply_update(Q, s, a, target, self._alpha)
                s = tr.nxt
                if tr.done:
                    break
                a = self._epsilon_greedy(Q, s, self._world.actions, eps, rng)
            returns.append(G)
        return Q, returns


def greedy_policy(world: World, Q: dict) -> dict[tuple[int, int], str]:
    """Obtiene el mapa de acción greedy para cada estado no terminal."""
    policy = {}
    for s in world.non_terminals:
        best = world.actions[0]
        best_v = Q[s][best]
        for a in world.actions[1:]:
            if Q[s][a] > best_v:
                best, best_v = a, Q[s][a]
        policy[s] = best
    return policy


def format_grid_policy(world: World, Q: dict) -> str:
    """
    Imprime la política greedy sobre la cuadrícula completa 4x12 usando flechas
    (↑, →, ↓, ←), 'C' para el acantilado y 'G' para la meta.
    """
    arrows = {'N': '↑', 'E': '→', 'S': '↓', 'W': '←'}
    lines = []
    header = "      " + " ".join(f"{c:^3}" for c in range(world.cols))
    lines.append(header)
    lines.append("    " + "-" * (len(header) - 4))
    for r in range(world.rows):
        cells = []
        for c in range(world.cols):
            cell = (r, c)
            if cell == world.goal:
                cells.append(" G ")
            elif cell in world.cliffs:
                cells.append(" C ")
            elif cell == world.start:
                best = world.actions[0]
                best_v = Q[cell][best]
                for a in world.actions[1:]:
                    if Q[cell][a] > best_v:
                        best, best_v = a, Q[cell][a]
                cells.append(f"S{arrows[best]} ")
            elif cell in Q:
                best = world.actions[0]
                best_v = Q[cell][best]
                for a in world.actions[1:]:
                    if Q[cell][a] > best_v:
                        best, best_v = a, Q[cell][a]
                cells.append(f" {arrows[best]} ")
            else:
                cells.append(" · ")
        lines.append(f" {r} |  " + " ".join(cells))
    return "\n".join(lines)


def evaluate_greedy(world: World, Q: dict, max_steps: int = 50):
    """Evalúa la política greedy desde Start (sin exploración, epsilon=0)."""
    s = world.start
    path = [s]
    actions_taken = []
    G = 0.0
    for _ in range(max_steps):
        if s not in Q:
            break
        # Selecciona la mejor acción greedy
        best = world.actions[0]
        best_v = Q[s][best]
        for a in world.actions[1:]:
            if Q[s][a] > best_v:
                best, best_v = a, Q[s][a]
        
        actions_taken.append(best)
        tr = world.step(s, best)
        G += tr.reward
        s = tr.nxt
        path.append(s)
        if tr.done:
            break
    return path, actions_taken, G


def moving_average(values: list[float], window: int = 10) -> list[float]:
    """Calcula la media móvil con una ventana determinada (por defecto 10 episodios)."""
    ma = []
    for i in range(len(values)):
        start_idx = max(0, i - window + 1)
        sub = values[start_idx:i + 1]
        ma.append(sum(sub) / len(sub))
    return ma


def sparkline(values: list[float], width: int = 40) -> str:
    """Genera un sparkline textual compacto para la terminal."""
    if not values:
        return ""
    lo, hi = min(values), max(values)
    span = hi - lo if hi > lo else 1.0
    blocks = " ▂▃▄▅▆▇█"
    step = max(1, len(values) // width)
    chars = []
    for v in values[::step]:
        idx = int(round((v - lo) / span * (len(blocks) - 1)))
        idx = max(0, min(len(blocks) - 1, idx))
        chars.append(blocks[idx])
    return "".join(chars)


def save_returns_to_csv(returns: list[float], filename: Path) -> None:
    """Guarda la serie completa de recompensas de entrenamiento y su media móvil en un archivo CSV."""
    ma10 = moving_average(returns, window=10)
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Episodio", "Recompensa_Acumulada", "Media_Movil_10"])
        for i, (r, ma) in enumerate(zip(returns, ma10), 1):
            writer.writerow([i, r, f"{ma:.2f}"])


def plot_learning_curve(returns: list[float], window: int = 10, filename: Path = Path("curva_aprendizaje.png")) -> bool:
    """Genera y guarda la gráfica de recompensa por episodio comparada con la media móvil."""
    if not HAS_MATPLOTLIB:
        return False
    ma = moving_average(returns, window=window)
    episodes = range(1, len(returns) + 1)

    plt.figure(figsize=(10, 5.5))
    plt.plot(episodes, returns, alpha=0.35, color='steelblue', label='Recompensa por episodio (ε = 0.1)')
    plt.plot(episodes, ma, color='crimson', linewidth=2, label=f'Media móvil ({window} episodios)')
    plt.axhline(y=-13, color='forestgreen', linestyle='--', linewidth=1.5, label='Retorno óptimo greedy (-13)')

    plt.title('Curva de Aprendizaje en Cliff Walking (Q-Learning Tabular)', fontsize=13, fontweight='bold')
    plt.xlabel('Episodios', fontsize=11)
    plt.ylabel('Recompensa acumulada por episodio', fontsize=11)
    plt.ylim(-150, 0)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='lower right', fontsize=10)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    return True



if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent

    print("==================================================")
    print("CASO DE PRUEBA: CLIFF WALKING (SUTTON & BARTO)")
    print("==================================================")

    # 1. Configuración del entorno 4x12
    cliffs = [(3, c) for c in range(1, 11)]
    start = (3, 0)
    goal = (3, 11)
    world = World(rows=4, cols=12, start=start, goal=goal, cliffs=cliffs)

    print("\n[Mapa del entorno 4x12]")
    print(world.render_world())

    # -------------------------------------------------------------
    # Prueba 1: Transiciones individuales clave (ejercicio-01.md paso 3)
    # -------------------------------------------------------------
    print("\n[Test 1] Verificando transiciones del entorno:")
    
    # a) Paso Norte desde S
    res_n = world.step(start, 'N')
    assert res_n.nxt == (2, 0) and res_n.reward == -1.0 and not res_n.done
    print("  [OK] Paso Norte desde S: (3, 0) -> (2, 0), r=-1, done=False")

    # b) Paso Este desde S (caída al acantilado)
    res_e = world.step(start, 'E')
    assert res_e.nxt == start and res_e.reward == -100.0 and not res_e.done
    print("  [OK] Caída al acantilado: regresa a S=(3, 0), r=-100, done=False")

    # c) Paso Sur desde (2, 11) a G (meta)
    res_g = world.step((2, 11), 'S')
    assert res_g.nxt == goal and res_g.reward == -1.0 and res_g.done
    print("  [OK] Llegada a la meta: (2, 11) -> G=(3, 11), r=-1, done=True")

    # d) Choque con la pared Oeste desde S
    res_w = world.step(start, 'W')
    assert res_w.nxt == start and res_w.reward == -1.0 and not res_w.done
    print("  [OK] Choque contra la pared: permanece en (3, 0), r=-1, done=False")

    # -------------------------------------------------------------
    # Prueba 2: Entrenamiento y criterio de aceptación óptimo (-13)
    # -------------------------------------------------------------
    seed = 42
    episodes = 500
    alpha = 0.5
    gamma = 1.0
    epsilon = 0.1
    max_steps = 200

    print(f"\n[Test 2] Entrenando Q-learning ({episodes} episodios, alpha={alpha}, gamma={gamma}, eps={epsilon}, seed={seed})...")
    rng = random.Random(seed)
    ql = Q_Learning(world, alpha=alpha, gamma=gamma)
    Q, returns = ql.train(rng=rng, epsilon=epsilon, episodes=episodes, max_steps=max_steps)

    # Evaluar política greedy
    path, actions, greedy_ret = evaluate_greedy(world, Q)

    print(f"  • Semilla utilizada: {seed}")
    print(f"  • Retorno greedy (ε = 0): {greedy_ret}")
    print(f"  • Total de pasos: {len(actions)}")
    print(f"  • Secuencia de acciones: {' -> '.join(actions)}")
    print(f"  • Camino recorrido: {path}")

    # Validaciones obligatorias de ejercicio-01.md
    assert len(actions) == 13, f"Se esperaban 13 pasos, se obtuvieron {len(actions)}"
    assert greedy_ret == -13.0, f"El retorno óptimo debe ser -13.0, se obtuvo {greedy_ret}"
    assert path[0] == start and path[-1] == goal, "El camino debe ir de S a G"
    assert actions == ['N'] + ['E'] * 11 + ['S'], "El camino debe ser pegado al borde del acantilado"

    print("\n==================================================")
    print("¡TODAS LAS VALIDACIONES OBLIGATORIAS PASARON! [OK]")
    print("==================================================")

    # -------------------------------------------------------------
    # Visualización de la política greedy en la cuadrícula (Paso 5)
    # -------------------------------------------------------------
    print("\n[Política Greedy Aprendida en la Cuadrícula]")
    print(format_grid_policy(world, Q))

    # -------------------------------------------------------------
    # Estadísticas y guardado de recompensas por episodio (Paso 6 y Entrega)
    # -------------------------------------------------------------
    ma10 = moving_average(returns, window=10)
    tail20 = returns[-20:]
    mean20 = sum(tail20) / len(tail20)
    tail50 = returns[-50:]
    mean50 = sum(tail50) / len(tail50)

    print("\n[Estadísticas del Entrenamiento]")
    print(f"  • Total de episodios: {len(returns)}")
    print(f"  • Recompensa episodio 1: {returns[0]:.1f}")
    print(f"  • Recompensa media (últimos 20 episodios): {mean20:.2f}")
    print(f"  • Recompensa media (últimos 50 episodios): {mean50:.2f}")
    print(f"  • Sparkline de retornos: {sparkline(returns)}")

    # Guardar en CSV
    csv_file = script_dir / "recompensas_entrenamiento.csv"
    save_returns_to_csv(returns, csv_file)
    print(f"  • Serie de recompensas guardada en: {csv_file.name}")

    # Guardar gráfica
    png_file = script_dir / "curva_aprendizaje.png"
    if plot_learning_curve(returns, window=10, filename=png_file):
        print(f"  • Gráfica de aprendizaje guardada en: {png_file.name}")
