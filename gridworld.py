"""Grid World MDP: parses a map, gives transitions, and simulates episodes."""
import numpy as np

from floors import FLOORS

DIRS = {"U": (-1, 0), "R": (0, 1), "D": (1, 0), "L": (0, -1)}
ACTIONS = ("U", "R", "D", "L")  # order = tie-breaking order
PERP = {"U": ("L", "R"), "R": ("U", "D"), "D": ("L", "R"), "L": ("U", "D")}
ARROWS = {"U": "↑", "R": "→", "D": "↓", "L": "←"}


def p1(s):
    """0-based (row, col) -> 1-based string, as in the assignment."""
    return f"({s[0] + 1},{s[1] + 1})"


class GridWorld:
    def __init__(self, rows, floors=FLOORS):
        self.rows = list(rows)
        self.floors = floors
        self.n_rows, self.n_cols = len(self.rows), len(self.rows[0])
        self.start = next((r, c) for r in range(self.n_rows) for c in range(self.n_cols)
                          if self.rows[r][c] == "S")

    def floor(self, s):
        return self.floors[self.rows[s[0]][s[1]]]

    def states(self):
        return [(r, c) for r in range(self.n_rows) for c in range(self.n_cols)
                if self.floor((r, c)).passable]

    def is_terminal(self, s):
        return self.floor(s).terminal

    def move(self, s, direction):
        """Deterministic move. Wall/outside leaves you in place; reward is for the ending tile."""
        dr, dc = DIRS[direction]
        n = (s[0] + dr, s[1] + dc)
        inside = 0 <= n[0] < self.n_rows and 0 <= n[1] < self.n_cols
        if not inside or not self.floor(n).passable:
            n = s
        return n, self.floor(n).reward

    def transitions(self, s, a):
        """List of (probability, next_state, reward). Terminal states have no transitions."""
        if self.is_terminal(s):
            return []
        p = self.floor(s).slip  # depends on the tile we LEAVE
        if p == 0:
            outcomes = [(1.0, a)]
        else:
            outcomes = [(1 - 2 * p, a), (p, PERP[a][0]), (p, PERP[a][1])]
        return [(prob, *self.move(s, d)) for prob, d in outcomes]


def simulate_episode(mdp, policy, seed, gamma=0.9, max_steps=100, start=None):
    """Follow a fixed policy. Returns steps, outcome, discounted return r0 + g*r1 + g^2*r2 ..."""
    rng = np.random.default_rng(seed)
    s = start or mdp.start
    steps, ret, rewards = 0, 0.0, []
    while steps < max_steps and not mdp.is_terminal(s):
        u, cum = rng.random(), 0.0
        for prob, n, r in mdp.transitions(s, policy[s]):
            cum += prob
            if u < cum:
                break  # falls back to the last outcome if rounding leaves a gap
        ret += gamma ** steps * r
        rewards.append(r)
        s = n
        steps += 1
    f = mdp.floor(s)
    outcome = ("goal" if f.reward > 0 else "hole") if f.terminal else "time_limit"
    return {"steps": steps, "outcome": outcome, "disc_return": ret, "rewards": rewards, "final": s}
