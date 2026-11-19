"""Part B: random vs fixed policy on FrozenLake-v1 (4x4), 4 conditions x 3 batches x 50 episodes.

Run:  python part_b.py
Output: outputs/episodes.csv, outputs/summary.csv, outputs/summary.md, outputs/traces/*.txt
"""
import os

import gymnasium as gym
import numpy as np
import pandas as pd

from fixed_policy import POLICY

HOLES = {5, 7, 11, 12}
GOAL = 15
NONTERMINAL = [0, 1, 2, 3, 4, 6, 8, 9, 10, 13, 14]
ACTION_NAMES = {0: "LEFT", 1: "DOWN", 2: "RIGHT", 3: "UP"}
BATCH_SEEDS = (11, 22, 33)
EPISODES_PER_BATCH = 50
MAX_STEPS = 100
OUT_DIR = "outputs"


def validate_policy():
    missing = [s for s in NONTERMINAL if POLICY.get(s) not in (0, 1, 2, 3)]
    if missing:
        raise SystemExit(f"Fill in fixed_policy.py first. Missing/invalid states: {missing}")


def make_env(slippery):
    return gym.make("FrozenLake-v1", map_name="4x4", is_slippery=slippery,
                    render_mode="ansi", max_episode_steps=MAX_STEPS)


def run_episode(env, policy_fn, episode_seed, record=False):
    """One episode with reset()/step(). Returns dict with steps, reward, outcome (and trace)."""
    obs, _ = env.reset(seed=episode_seed)
    total_reward, steps = 0.0, 0
    terminated = truncated = False
    trace = [f"episode seed = {episode_seed}\nstart\n{env.render()}"] if record else None
    while not (terminated or truncated):
        action = int(policy_fn(obs))
        obs, reward, terminated, truncated, _ = env.step(action)
        steps += 1
        total_reward += reward
        if record:
            trace.append(f"step {steps}: action={ACTION_NAMES[action]} -> state {obs}, "
                         f"reward {reward}\n{env.render()}")
    # outcome from the final state; a terminal state on the last step still counts as terminal
    if obs == GOAL:
        outcome = "goal"
    elif obs in HOLES:
        outcome = "hole"
    else:
        outcome = "time_limit"
    return {"steps": steps, "reward": total_reward, "outcome": outcome, "trace": trace}


def random_policy_factory(batch_seed):
    rng = np.random.default_rng(batch_seed)  # seeded action generator
    return lambda obs: rng.integers(4)


def fixed_policy_fn(obs):
    return POLICY[obs]


def main():
    validate_policy()
    os.makedirs(f"{OUT_DIR}/traces", exist_ok=True)
    rows, saved_traces = [], set()

    for slippery in (False, True):
        env = make_env(slippery)
        for policy_name in ("random", "fixed"):
            for batch_seed in BATCH_SEEDS:
                policy_fn = (random_policy_factory(batch_seed) if policy_name == "random"
                             else fixed_policy_fn)
                for i in range(EPISODES_PER_BATCH):
                    ep_seed = 1000 * batch_seed + i
                    res = run_episode(env, policy_fn, ep_seed, record=True)
                    cond = f"slippery={slippery}"
                    rows.append({"condition": cond, "slippery": slippery, "policy": policy_name,
                                 "batch_seed": batch_seed, "episode_seed": ep_seed,
                                 "steps": res["steps"], "total_reward": res["reward"],
                                 "outcome": res["outcome"]})
                    kind = "success" if res["outcome"] == "goal" else "failure"
                    key = (slippery, policy_name, kind)
                    if key not in saved_traces:
                        saved_traces.add(key)
                        fname = f"{OUT_DIR}/traces/slippery-{slippery}_{policy_name}_{kind}.txt"
                        with open(fname, "w", encoding="utf-8") as f:
                            f.write(f"{cond}, policy={policy_name}, batch={batch_seed}, "
                                    f"outcome={res['outcome']}\n\n" + "\n".join(res["trace"]))
        env.close()

    df = pd.DataFrame(rows)
    df.to_csv(f"{OUT_DIR}/episodes.csv", index=False)

    g = df.groupby(["slippery", "policy", "batch_seed"])
    summary = pd.DataFrame({
        "Goals /50": g["outcome"].apply(lambda s: (s == "goal").sum()),
        "Holes /50": g["outcome"].apply(lambda s: (s == "hole").sum()),
        "Time limits /50": g["outcome"].apply(lambda s: (s == "time_limit").sum()),
        "Success %": g["outcome"].apply(lambda s: 100 * (s == "goal").mean()),
        "Mean steps": g["steps"].mean(),
    }).reset_index()
    summary.to_csv(f"{OUT_DIR}/summary.csv", index=False)

    lines = ["| Slippery? | Policy | Batch seed | Goals /50 | Holes /50 | Time limits /50 | Success % | Mean steps |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for _, r in summary.iterrows():
        lines.append(f"| {r['slippery']} | {r['policy']} | {r['batch_seed']} | {r['Goals /50']} | "
                     f"{r['Holes /50']} | {r['Time limits /50']} | {r['Success %']:.0f} | {r['Mean steps']:.2f} |")
    md = "\n".join(lines)
    with open(f"{OUT_DIR}/summary.md", "w", encoding="utf-8") as f:
        f.write(md + "\n")
    print(md)
    print("\nTraces saved:", sorted(saved_traces))
    missing = [(s, p, k) for s in (False, True) for p in ("random", "fixed")
               for k in ("success", "failure") if (s, p, k) not in saved_traces]
    if missing:
        print("Outcomes that never occurred (mention in SUBMISSION.md):", missing)


if __name__ == "__main__":
    main()
