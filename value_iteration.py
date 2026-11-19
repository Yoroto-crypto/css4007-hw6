"""Value iteration with the known transition model."""
from gridworld import ACTIONS


def q_value(mdp, s, a, V, gamma):
    return sum(p * (r + gamma * V[n]) for p, n, r in mdp.transitions(s, a))


def value_iteration(mdp, gamma=0.9, tol=1e-6, max_iter=10000):
    """Returns V, iterations, last max change, converged flag, history [V0, V1, V2, ...]."""
    V = {s: 0.0 for s in mdp.states()}
    history = [dict(V)]
    delta, converged, k = float("inf"), False, 0
    for k in range(1, max_iter + 1):
        new, delta = dict(V), 0.0  # synchronous: every state uses the PREVIOUS round's V
        for s in mdp.states():
            if mdp.is_terminal(s):
                continue
            new[s] = max(q_value(mdp, s, a, V, gamma) for a in ACTIONS)
            delta = max(delta, abs(new[s] - V[s]))
        V = new
        history.append(dict(V))
        if delta < tol:
            converged = True
            break
    return V, k, delta, converged, history


def greedy_policy(mdp, V, gamma=0.9, eps=1e-9):
    """Best action per state. Ties (within eps) are broken by the order U, R, D, L."""
    policy, ties = {}, {}
    for s in mdp.states():
        if mdp.is_terminal(s):
            continue
        qs = {a: q_value(mdp, s, a, V, gamma) for a in ACTIONS}
        best = max(qs.values())
        tied = [a for a in ACTIONS if best - qs[a] <= eps]
        policy[s], ties[s] = tied[0], tied
    return policy, ties
