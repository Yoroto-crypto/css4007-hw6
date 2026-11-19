"""Rule checks required before trusting the solver. Called from part_c.py."""
from gridworld import ACTIONS, GridWorld, p1, simulate_episode
from value_iteration import value_iteration


def run_checks(mdp_a, mdp_b, out):
    out("=== RULE CHECKS ===")
    out("\n1. Walls and boundaries (map A; coordinates are (row,col), 1-based)")
    for s, a, why in [((0, 0), "U", "top boundary"), ((0, 0), "L", "left boundary"),
                      ((2, 0), "D", "bottom boundary"), ((1, 0), "R", "wall (2,2) on the right"),
                      ((0, 1), "D", "wall (2,2) below mud")]:
        t = mdp_a.transitions(s, a)
        assert t == [(1.0, s, mdp_a.floor(s).reward)], t
        out(f"  {p1(s)} action {a} ({why}) -> stays at {p1(s)}, reward {t[0][2]}")
    t = mdp_a.transitions((1, 2), "L")
    out("  ice (2,3) action L (wall in the chosen direction), each slip handled separately:")
    for p, n, r in t:
        out(f"    prob {p:.1f} -> {p1(n)} reward {r}")

    out("\n2. Ice probabilities sum to 1")
    for a in ACTIONS:
        t = mdp_a.transitions((1, 2), a)
        total = sum(p for p, _, _ in t)
        assert abs(total - 1) < 1e-12
        out(f"  action {a} at (2,3): probabilities {[round(p, 2) for p, _, _ in t]} sum = {total:.1f}")
    out("  non-ice tiles are deterministic (one outcome, probability 1):")
    for mdp, s, name in [(mdp_a, (0, 1), "mud"), (mdp_b, (2, 1), "sand"), (mdp_b, (2, 3), "water"),
                         (mdp_a, (2, 0), "start")]:
        for a in ACTIONS:
            t = mdp.transitions(s, a)
            assert len(t) == 1 and t[0][0] == 1.0
        out(f"  {name} {p1(s)}: all 4 actions have a single outcome with probability 1.0")

    out("\n3. Rewards for ending a move on each floor type")
    for mdp, s, a, name in [(mdp_a, (0, 0), "R", "mud"), (mdp_a, (0, 0), "D", "floor"),
                            (mdp_b, (2, 0), "R", "sand"), (mdp_b, (2, 2), "R", "water"),
                            (mdp_a, (0, 2), "R", "goal"), (mdp_a, (2, 3), "U", "hole")]:
        p, n, r = mdp.transitions(s, a)[0]
        out(f"  {p1(s)} {a} -> {p1(n)} ({name}): reward {r}")
    assert mdp_a.transitions((0, 0), "R")[0][2] == -3
    assert mdp_b.transitions((2, 0), "R")[0][2] == -2
    assert mdp_b.transitions((2, 2), "R")[0][2] == -5

    out("\n4. Terminal handling")
    for s in [(0, 3), (1, 3)]:
        assert mdp_a.transitions(s, "U") == []
        out(f"  {p1(s)} is terminal: no transitions, no further rewards")
    V, *_ = value_iteration(mdp_a)
    out(f"  final V at G (1,4) = {V[(0, 3)]}, at H (2,4) = {V[(1, 3)]}")
    ep = simulate_episode(mdp_a, {(0, 2): "R"}, seed=1, start=(0, 2))
    assert ep["steps"] == 1 and ep["rewards"] == [10]
    out(f"  episode from (1,3) moving R: rewards {ep['rewards']}, steps {ep['steps']}, "
        f"outcome {ep['outcome']} (episode stops; nothing is paid after the goal)")
    out("\nAll rule checks passed.")
