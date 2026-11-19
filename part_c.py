"""Part C: value iteration on the Part A map and on the extended map, simulations, rule checks.

Run:  python part_c.py
Output: outputs/partC_report.txt, outputs/partC_episodes_<map>.csv, outputs/partC_summary.md
"""
import os

import pandas as pd

from floors import load_config, floors_from_config
from gridworld import ACTIONS, ARROWS, GridWorld, p1, simulate_episode
from rule_checks import run_checks
from value_iteration import greedy_policy, q_value, value_iteration

CFG = load_config("maps.json")  # all assignment parameters come from this file
MAPS = {"A": CFG["paper_map"], "ext": CFG["extended_map"]}
GAMMA = CFG["discount"]
TOL, MAX_ITER = CFG["solver"]["tolerance"], CFG["solver"]["max_iterations"]
BATCH_SEEDS = tuple(CFG["simulation"]["batch_seeds"])
N_EPISODES = CFG["simulation"]["episodes_per_batch"]
MAX_STEPS = CFG["simulation"]["max_steps"]
V2_POSITIONS = [(r - 1, c - 1) for r, c in CFG["paper_v2_positions"]]  # file is 1-based
OUT_DIR = "outputs"

report = []


def out(text=""):
    print(text)
    report.append(text)


def value_map(mdp, V, digits=3):
    lines = []
    for r in range(mdp.n_rows):
        cells = []
        for c in range(mdp.n_cols):
            s, ch = (r, c), mdp.rows[r][c]
            if not mdp.floor(s).passable:
                cells.append("   #### ")
            elif mdp.is_terminal(s):
                cells.append(f"   {ch}  0 ".rjust(8))
            else:
                cells.append(f"{V[s]:8.{digits}f}")
        lines.append(" ".join(cells))
    return "\n".join(lines)


def policy_map(mdp, policy):
    lines = []
    for r in range(mdp.n_rows):
        cells = []
        for c in range(mdp.n_cols):
            s, ch = (r, c), mdp.rows[r][c]
            if not mdp.floor(s).passable:
                cells.append("#")
            elif mdp.is_terminal(s):
                cells.append(ch)
            else:
                cells.append(ARROWS[policy[s]])
        lines.append("  ".join(cells))
    return "\n".join(lines)


def solve(name, mdp):
    out(f"\n{'=' * 60}\nMAP {name}\n" + "\n".join(mdp.rows))
    V, k, delta, converged, hist = value_iteration(mdp, GAMMA, TOL, MAX_ITER)
    policy, ties = greedy_policy(mdp, V, GAMMA)
    out(f"\nV1 map:\n{value_map(mdp, hist[1])}")
    out("\nV2 at the requested tiles (computed only from V1):")
    for s in V2_POSITIONS:
        qs = {a: q_value(mdp, s, a, hist[1], GAMMA) for a in ACTIONS}
        best = max(qs.values())
        tied = [a for a in ACTIONS if best - qs[a] < 1e-9]
        q_txt = ", ".join(f"{a}={q:.4f}" for a, q in qs.items())
        out(f"  {p1(s)}: {q_txt}  ->  V2 = {hist[2][s]:.4f}, best = {tied}")
    status = "converged" if converged else "NOT CONVERGED (hit the safeguard)"
    out(f"\nIterations: {k} ({status}); final max change = {delta:.3e}")
    out(f"\nFinal values:\n{value_map(mdp, V)}")
    out("\nPolicy (ties broken by order U, R, D, L):\n" + policy_map(mdp, policy))
    tied_states = {s: t for s, t in ties.items() if len(t) > 1}
    out("States with tied best actions: " +
        (", ".join(f"{p1(s)}:{''.join(t)}" for s, t in tied_states.items()) or "none"))
    return V, policy


def simulate_map(name, mdp, policy):
    rows = []
    for b in BATCH_SEEDS:
        for i in range(N_EPISODES):
            seed = 1000 * b + i
            ep = simulate_episode(mdp, policy, seed, GAMMA, MAX_STEPS)
            rows.append({"map": name, "batch_seed": b, "episode_seed": seed, "steps": ep["steps"],
                         "outcome": ep["outcome"], "discounted_return": ep["disc_return"]})
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUT_DIR}/partC_episodes_{name}.csv", index=False)
    return df


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    floors = floors_from_config(CFG)
    mdps = {n: GridWorld(rows, floors) for n, rows in MAPS.items()}
    results = {n: solve(n, m) for n, m in mdps.items()}

    out(f"\n{'=' * 60}\nWHAT CHANGED FROM MAP A TO THE EXTENDED MAP")
    (VA, pA), (VB, pB) = results["A"], results["ext"]
    for s in mdps["A"].states():
        if mdps["A"].is_terminal(s):
            continue
        dv = VB[s] - VA[s]
        if abs(dv) > 1e-6 or pA[s] != pB[s]:
            out(f"  {p1(s)}: V {VA[s]:.3f} -> {VB[s]:.3f} (diff {dv:+.3f}), action {pA[s]} -> {pB[s]}")

    all_rows = []
    for n, mdp in mdps.items():
        all_rows.append(simulate_map(n, mdp, results[n][1]))
    df = pd.concat(all_rows)

    lines = ["| Map | Batch seed | Goals /50 | Holes /50 | Time limits /50 | Mean steps | Mean discounted return |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for (m, b), g in df.groupby(["map", "batch_seed"]):
        lines.append(f"| {m} | {b} | {(g.outcome == 'goal').sum()} | {(g.outcome == 'hole').sum()} | "
                     f"{(g.outcome == 'time_limit').sum()} | {g.steps.mean():.2f} | {g.discounted_return.mean():.3f} |")
    out(f"\n{'=' * 60}\nSIMULATION RESULTS (3 batches x 50 episodes, limit {MAX_STEPS} steps)\n" + "\n".join(lines))
    out("\nFor comparison, V(start) from value iteration: " +
        ", ".join(f"{n}: {results[n][0][mdps[n].start]:.3f}" for n in mdps))
    with open(f"{OUT_DIR}/partC_summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    out("")
    run_checks(mdps["A"], mdps["ext"], out)
    with open(f"{OUT_DIR}/partC_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")


if __name__ == "__main__":
    main()
