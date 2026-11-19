# HW6 submission

## AI-use declaration

Which tools did you use, and for what?

I used **Claude (Anthropic)** in the claude.ai chat. No other AI tools were used.

- **Understanding the task.** Claude explained the README step by step and the order of work (paper first, then code).
- **Part A.** Claude worked out V1 for every tile and the three V2 calculations (with all four actions each) and showed how to lay the work out on paper. I wrote the calculations out by hand on paper and photographed them.
- **Part B.** Claude suggested the fixed policy (and checked its success probabilities with an exact Markov-chain calculation), and wrote `part_b.py` and `fixed_policy.py`. I ran the experiments myself and the results in this file are from my runs.
- **Part C.** Claude wrote the solver (`gridworld.py`, `value_iteration.py`, `floors.py`, `rule_checks.py`, `part_c.py`) and helped connect it to `maps.json`. I ran it and compared its output with my paper work.
- **Debugging and tooling.** Claude helped with Git and PowerShell problems (cloning, deleting a folder, paths with spaces) and with a Windows text-encoding error when saving the report.
- **Writing.** Claude drafted the explanations in Parts B and C from my results; I reviewed them against my own outputs.


## Setup and reproduction

Environment: Windows, PowerShell, Python 3.12 in a virtual environment.

Dependency versions actually used (TODO: paste the output of the command below):

```text
python -c "import gymnasium, numpy, pandas, sys; print(sys.version); print(gymnasium.__version__, numpy.__version__, pandas.__version__)"
```

Installation (from the repository root):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate` instead.

Run commands:

```powershell
python part_b.py    # Part B, writes outputs/episodes.csv, summary.csv, summary.md, traces/
python part_c.py    # Part C, writes outputs/partC_report.txt, partC_summary.md, partC_episodes_*.csv
```

Part B needs `fixed_policy.py` filled in (it was committed before the experiments). Part C reads all assignment parameters from `maps.json`. All randomness is seeded: episode seed `1000 * batch_seed + i` with batch seeds 11, 22, 33, so reruns give the same results.

Commit order: the Part A photo was committed before any code (TODO: check with `git log --oneline` and correct this sentence if it is not true), and `fixed_policy.py` was committed before running Part B.

## Part A — Paper calculations

Scan/photo of my handwritten calculations: [outputs/partA.jpg](outputs/partA.jpg) (TODO: use the real file name). The same calculations are written out below.

### 1. The problem in my own words

- **States:** the traversable tiles. The goal G and the hole H are terminal states; the wall `#` is not a state. The nonterminal states are (1,1), (1,2), (1,3), (2,1), (2,3), (3,1), (3,2), (3,3), (3,4).
- **Actions:** up, right, down, left, chosen at every nonterminal tile.
- **Transitions:** on start, floor and mud the chosen direction happens with probability 1. When a move starts on ice, it goes in the chosen direction with probability 0.8 and in each perpendicular direction with 0.1. A move into a wall or off the map leaves the agent in place; this is applied to each possible slip direction separately.
- **Rewards:** the reward depends on the tile where the move ends: floor/start −1, mud −3, ice −1, goal +10, hole −10. Nothing is paid after G or H.
- **Goal of the agent:** to maximise the expected sum of discounted rewards (discount 0.9). In practice it wants to reach G quickly, avoid H and avoid expensive tiles.

### 2. V1 for every nonterminal tile

Since V0 = 0, V1(s) is the best expected one-step reward. Moves into walls or borders keep the agent in place and pay the reward of the tile it stays on.

| Tile | Up | Right | Down | Left | V1 | Best |
| --- | --- | --- | --- | --- | --- | --- |
| (1,1) | −1 (border) | −3 (mud) | −1 | −1 (border) | −1 | up, down, left |
| (1,2) mud | −3 (border, stays on mud) | −1 | −3 (wall, stays on mud) | −1 | −1 | right, left |
| (1,3) | −1 (border) | +10 (goal) | −1 (ice) | −3 (mud) | 10 | right |
| (2,1) | −1 | −1 (wall) | −1 | −1 (border) | −1 | all four |
| (2,3) ice | −1.9 | −8.2 | −1.9 | −1 | −1 | left |
| (3,1) | −1 | −1 | −1 (border) | −1 (border) | −1 | all four |
| (3,2) | −1 (wall) | −1 | −1 (border) | −1 | −1 | all four |
| (3,3) | −1 | −1 | −1 (border) | −1 | −1 | all four |
| (3,4) | −10 (hole) | −1 (border) | −1 (border) | −1 | −1 | right, down, left |

The ice tile (2,3), written out. Up: 0.8·(−1) [to (1,3)] + 0.1·(−1) [left, wall, stays] + 0.1·(−10) [right, hole] = −1.9. Right: 0.8·(−10) [hole] + 0.1·(−1) [up] + 0.1·(−1) [down] = −8.2. Down: 0.8·(−1) [to (3,3)] + 0.1·(−1) [left, wall, stays] + 0.1·(−10) [right, hole] = −1.9. Left: 0.8·(−1) [wall, stays] + 0.1·(−1) [up] + 0.1·(−1) [down] = −1.

V1 map (G and H are terminal, value 0):

```text
 -1    -1    10     G 0
 -1     #    -1     H 0
 -1    -1    -1    -1
```

### 3. V2 at (1,2), (1,3) and (2,3), using only V1

Each action value is reward + 0.9 · V1(next tile).

**(1,2), mud**

| Action | Calculation | Value |
| --- | --- | --- |
| Up (border, stays on mud) | −3 + 0.9·(−1) | −3.9 |
| Right to (1,3) | −1 + 0.9·10 | **8** |
| Down (wall, stays on mud) | −3 + 0.9·(−1) | −3.9 |
| Left to (1,1) | −1 + 0.9·(−1) | −1.9 |

V2(1,2) = 8.

**(1,3)**

| Action | Calculation | Value |
| --- | --- | --- |
| Up (border, stays) | −1 + 0.9·10 | 8 |
| Right to goal | 10 + 0.9·0 | **10** |
| Down to (2,3) | −1 + 0.9·(−1) | −1.9 |
| Left to (1,2), mud | −3 + 0.9·(−1) | −3.9 |

V2(1,3) = 10.

**(2,3), ice.** Outcome values: to (1,3): −1 + 0.9·10 = 8; stay on (2,3) or go to (3,3): −1 + 0.9·(−1) = −1.9; into the hole: −10.

| Action | Probability-weighted sum | Value |
| --- | --- | --- |
| Up | 0.8·8 + 0.1·(−1.9) [left, wall] + 0.1·(−10) [right, hole] = 6.4 − 0.19 − 1 | **5.21** |
| Right | 0.8·(−10) [hole] + 0.1·8 [up] + 0.1·(−1.9) [down] = −8 + 0.8 − 0.19 | −7.39 |
| Down | 0.8·(−1.9) [to (3,3)] + 0.1·(−1.9) [left, wall] + 0.1·(−10) [right, hole] = −1.52 − 0.19 − 1 | −2.71 |
| Left | 0.8·(−1.9) [wall, stays] + 0.1·8 [up] + 0.1·(−1.9) [down] = −1.52 + 0.8 − 0.19 | −0.91 |

V2(2,3) = 5.21.

### 4. Best actions, ties and why two rounds are not enough

| Tile | V2 | Best action | Ties |
| --- | --- | --- | --- |
| (1,2) | 8 | → right | none |
| (1,3) | 10 | → right | none |
| (2,3) | 5.21 | ↑ up | none |

At (2,3) the best action after V1 was left (−1), but after V2 it is up (5.21). This shows that the best action can still change from one round to the next.

Two rounds do not prove the final optimal policy because V2 only looks two moves ahead: information about the +10 reward has reached only the tiles next to the goal. Tiles farther away, such as the start (3,1), still have V1 = −1 and have not yet "seen" the goal, and many of them are tied at this point (for example all four actions at (3,1)). Values keep changing until they stop moving by more than a small tolerance, and only then can the greedy policy be trusted. The solver in Part C needed 12 iterations to converge on this map, and its final values are quite different from V1 and V2 (for example 1.536 at (3,1)). In hindsight, the final policy at the three requested tiles has the same arrows as V2 (→, →, ↑), but this had to be checked by running to convergence.

## Part B — FrozenLake

### Fixed policy, written before the experiments

States are numbered `row * 4 + col`; actions are 0 = left, 1 = down, 2 = right, 3 = up. The map is `SFFF / FHFH / FFFH / HFFG`, so the holes are states 5, 7, 11 and 12 and the goal is state 15.

| State | Action | Reasoning |
| --- | --- | --- |
| 0 | 2 (right) | Start of the route. Under slipping the outcomes are right, down (state 4) or up (stays at the border): no hole. |
| 1 | 2 (right) | Route step. Risk: a downward slip enters hole 5 (probability 1/3). |
| 2 | 1 (down) | Route step. Outcomes are left (1), down (6) or right (3): no hole. |
| 3 | 3 (up) | Not on the route. Up and right hit the border, left returns to 2: no hole. |
| 4 | 0 (left) | Not on the route. Left hits the border, up goes to 0, down goes to 8: no hole. |
| 6 | 1 (down) | Route step. Risk: both sideways slips enter holes 5 and 7 (probability 2/3). |
| 8 | 3 (up) | Not on the route. Outcomes are up (4), right (9) or left (border): hole 12 is avoided. |
| 9 | 1 (down) | Route step. Outcomes are left (8), down (13) or right (10): no hole. |
| 10 | 0 (left) | Detour. Going down would be shorter, but a sideways slip could enter hole 11; going left to 9 avoids that. |
| 13 | 2 (right) | Route step. Outcomes are right (14), up (9) or down (border): hole 12 is avoided. |
| 14 | 2 (right) | Last step. Right reaches the goal; the sideways slips go up (10) or hit the border. |

Without slipping this policy follows the path 0 → 1 → 2 → 6 → 10 → 9 → 13 → 14 → 15 (8 steps). The same table has to be used in both modes, so it cannot be best for both. A policy that is best under slipping pushes against walls and would stay in place without slipping. I chose a policy that reaches the goal for certain without slipping and accepted weaker performance with slipping, mainly because of states 1 and 6.

### Results

| Slippery? | Policy | Batch seed | Goals /50 | Holes /50 | Time limits /50 | Success % | Mean steps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| False | fixed | 11 | 50 | 0 | 0 | 100 | 8.00 |
| False | fixed | 22 | 50 | 0 | 0 | 100 | 8.00 |
| False | fixed | 33 | 50 | 0 | 0 | 100 | 8.00 |
| False | random | 11 | 0 | 50 | 0 | 0 | 7.94 |
| False | random | 22 | 1 | 49 | 0 | 2 | 7.16 |
| False | random | 33 | 2 | 48 | 0 | 4 | 6.66 |
| True | fixed | 11 | 7 | 43 | 0 | 14 | 11.20 |
| True | fixed | 22 | 6 | 44 | 0 | 12 | 10.10 |
| True | fixed | 33 | 10 | 40 | 0 | 20 | 13.60 |
| True | random | 11 | 1 | 49 | 0 | 2 | 7.98 |
| True | random | 22 | 3 | 47 | 0 | 6 | 7.66 |
| True | random | 33 | 1 | 49 | 0 | 2 | 7.16 |

Files: [all episode rows](outputs/episodes.csv), [per-batch summary](outputs/summary.md), and example traces in [outputs/traces/](outputs/traces/):

- fixed policy, no slipping, success: [trace](outputs/traces/slippery-False_fixed_success.txt)
- fixed policy, slipping, success: [trace](outputs/traces/slippery-True_fixed_success.txt)
- fixed policy, slipping, failure: [trace](outputs/traces/slippery-True_fixed_failure.txt)
- random policy, success and failure, without slipping: [success](outputs/traces/slippery-False_random_success.txt), [failure](outputs/traces/slippery-False_random_failure.txt)
- random policy, success and failure, with slipping: [success](outputs/traces/slippery-True_random_success.txt), [failure](outputs/traces/slippery-True_random_failure.txt)

One outcome never occurred: the fixed policy without slipping never failed, so there is no failure trace for that condition.

### What slipping changed

With the fixed policy, success fell from 100% in all three batches without slipping to 12–20% with slipping (23 goals out of 150 episodes, 15.3%). The remaining 127 episodes ended in a hole, and no episode reached the 100-step limit. Without slipping the outcome is the same every time, because nothing is random: 8 steps, every episode. With slipping the chosen action is executed with probability 1/3 and each perpendicular direction with probability 1/3, so the agent can be pushed sideways. This is most dangerous at state 6 (both sideways moves are holes) and state 1 (one sideways move is a hole), which the route has to pass. Mean steps rose to about 10–14 because slipping sometimes delays the agent before it falls or finishes.

The random policy was poor in both modes: 0–4% success without slipping and 2–6% with it. These two ranges are not meaningfully different. A uniformly random action followed by a slip is still a uniformly random direction, so slipping changes nothing in distribution for this policy; the differences we see are sampling noise.

### Variation across batches

The three batches of the same condition are not identical when randomness is involved: for the fixed policy with slipping they gave 14%, 12% and 20%. A batch of 50 episodes with success probability about 15% has a standard error of about 5 percentage points, so this spread is expected. As a sanity check, an exact calculation with the transition probabilities (absorbing Markov chain, 100-step horizon, done with the help of Claude) gives about 15.5% for this policy, close to our pooled 15.3%. Without slipping all batches were identical, because the environment and the policy are both deterministic.

One successful episode is insufficient evidence because success can be luck: even the random policy reached the goal in some episodes. A reliable estimate of how good a policy is needs many episodes, and the batch-to-batch spread shows how uncertain even 50 episodes are.

### Why these runs do not train a policy

The fixed policy was written by hand before the experiments and never changes. The simulations only measure how good it is: no value estimates, action preferences or parameters are updated from the episode results, and results from earlier episodes do not influence later ones. The random policy is also not learning, since its actions do not depend on rewards. Training would require using the outcomes to improve the policy, which we do not do here.

## Part C — Custom solver

Reproduce with `python part_c.py` (virtual environment active, `maps.json` in the same folder). The script reads every assignment parameter (maps, rewards, discount, seeds, tolerance) from `maps.json`, builds the floor rules in `floors.py`, and writes the full report to [outputs/partC_report.txt](outputs/partC_report.txt) and the episode rows to [outputs/partC_episodes_A.csv](outputs/partC_episodes_A.csv) and [outputs/partC_episodes_ext.csv](outputs/partC_episodes_ext.csv). The solver (`value_iteration.py`) knows nothing about specific floor letters, so adding a floor means adding one entry to the tile table.

### Compare code with paper

V1 from the code, for the paper map (rows 1–3, columns 1–4):

```text
 -1.000   -1.000   10.000    G  0
 -1.000    ####    -1.000    H  0
 -1.000   -1.000   -1.000   -1.000
```

V2 at the three requested tiles, computed only from V1:

| Tile | Up | Right | Down | Left | V2 | Best |
| --- | --- | --- | --- | --- | --- | --- |
| (1,2) mud | -3.9 | 8.0 | -3.9 | -1.9 | 8.0 | right |
| (1,3) | 8.0 | 10.0 | -1.9 | -3.9 | 10.0 | right |
| (2,3) ice | 5.21 | -7.39 | -2.71 | -0.91 | 5.21 | up |

These agree with my paper calculations, so there were no discrepancies to correct. (TODO: check once more against your photo; if any number differs, state which side was wrong and why.)

### Values, policies and convergence

| Map | Iterations | Final max change | Converged? |
| --- | --- | --- | --- |
| Paper map | 12 | 2.165e-07 | yes (tolerance 1e-6, safeguard 10,000 never reached) |
| Extended map | 11 | 2.406e-07 | yes |

Tie-breaking: for each state the Q-value of every action is computed from the final values; all actions within 1e-9 of the best are considered tied, and the first of them in the order up, right, down, left is chosen. No ties occurred on either map.

Paper map, final values and policy:

```text
   4.200    8.000   10.000    G  0        →  →  →  G
   2.780    ####     5.824    H  0        ↑  #  ↑  H
   1.536    2.818    4.242    2.818       →  →  ↑  ←
```

Extended map (`.M.G / .#IH / SD.W`), final values and policy:

```text
   4.200    8.000   10.000    G  0        →  →  →  G
   2.780    ####     5.824    H  0        ↑  #  ↑  H
   1.502    2.818    4.242    2.818       ↑  →  ↑  ←
```

Both maps are in [outputs/partC_report.txt](outputs/partC_report.txt).

### Simulation results

Policy from the final values, 100-step limit, episode seeds `1000 * batch_seed + i`, discounted return `r0 + 0.9*r1 + 0.9^2*r2 + ...`:

| Map | Batch seed | Goals /50 | Holes /50 | Time limits /50 | Mean steps | Mean discounted return |
| --- | --- | --- | --- | --- | --- | --- |
| A | 11 | 47 | 3 | 0 | 5.04 | 2.230 |
| A | 22 | 44 | 6 | 0 | 4.96 | 1.442 |
| A | 33 | 42 | 8 | 0 | 4.88 | 0.970 |
| ext | 11 | 50 | 0 | 0 | 5.00 | 1.502 |
| ext | 22 | 50 | 0 | 0 | 5.00 | 1.502 |
| ext | 33 | 50 | 0 | 0 | 5.00 | 1.502 |

For comparison, value iteration gives V(start) = 1.536 on the paper map and 1.502 on the extended map.

### Explain your results

**What changed.** Only one state changed between the maps: the start tile (3,1). Its value fell from 1.536 to 1.502 and its best action changed from right to up. All other values and actions are identical. Sand and water affect a state only when a move ends on them, and the policy never needs water at all.

**Where cost and risk mattered.** From the start there are two routes. The right route goes along the bottom row, then up through the ice tile (2,3) into the goal. It has cheap floor but one risky step: leaving ice, a sideways slip to the right enters the hole (probability 0.1). The up route goes through the mud tile (1,2), which costs -3, but every move is deterministic. On the paper map the right route is worth -1 + 0.9 · 2.818 = 1.536 and the up route is worth -1 + 0.9 · 2.78 = 1.502, so the agent accepts the ice risk for a margin of only 0.034. On the extended map the first step of the right route lands on sand (-2 instead of -1), which lowers that route to -2 + 0.9 · 2.818 = 0.536. Now the safe mud route is clearly better (1.502 against 0.536), so the policy changes at the start.

**How the policy handles ice.** On the paper map the policy crosses the ice tile and always moves up from it, towards the goal row. That has a 0.8 chance of progress, a 0.1 chance of staying (a left slip into the wall) and a 0.1 chance of entering the hole. Repeating the move, the chance of ending in the hole is 0.1 / 0.9 ≈ 11%, which is close to the 17 holes in 150 episodes (11.3%). On the extended map the route from the start avoids the ice, which is why there are no holes.

**Simulations and computed values.** On the extended map every episode follows the same deterministic route (5 steps), so the discounted return is exactly 1.502 in every episode and equals V(start). On the paper map the return depends on whether the agent falls into the hole, so each batch of 50 differs (0.970 to 2.230). Their average, about 1.55, is close to V(start) = 1.536 but not equal to it. A finite simulation estimates an expectation from a limited sample, with noise, and cuts episodes at 100 steps. The computed values assume an infinite horizon, but 0.9^100 is about 2.7e-5, so the 100-step limit has no practical effect here, and no episode reached it.

### Rule checks

Output of the checks is in [outputs/partC_report.txt](outputs/partC_report.txt) (section "RULE CHECKS"); all assertions passed. In short:

- **Boundaries and walls.** From (1,1), up and left leave the agent in place with reward -1. From (3,1), down stays. From (2,1), right (into the wall (2,2)) stays. On mud, a move into the wall stays with the mud reward -3. On the ice tile (2,3), action left has a wall in the chosen direction: the 0.8 outcome stays at (2,3), and each 0.1 slip is resolved separately (to (1,3) and (3,3)), all with reward -1.
- **Ice probabilities.** For all four actions at (2,3) the probabilities are 0.8, 0.1 and 0.1 and sum to 1. Mud, sand, water and the start tile have a single outcome with probability 1 for every action.
- **Floor rewards.** Ending a move on mud gives -3, ordinary floor -1, sand -2, water -5, goal +10, hole -10.
- **Terminal handling.** Goal and hole have no transitions and value 0. An episode that starts at (1,3) and moves right receives the single reward 10, takes 1 step and ends: nothing is paid after the goal.
