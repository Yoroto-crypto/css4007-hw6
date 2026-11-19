# HW6 submission

## AI-use declaration

Which tools did you use, and for what?

## Setup and reproduction

Record dependency versions, installation commands and exact run commands.

## Part A — Paper calculations

Link your scan/photo here. Include V1 for every nonterminal tile, the three requested V2 calculations, best-action arrows/ties and your explanation. Commit this part before coding.

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

TODO (use your own trace files): in one or two sentences describe the failed slippery trace, for example at which state the agent was pushed sideways and into which hole.

### What slipping changed

With the fixed policy, success fell from 100% in all three batches without slipping to 12–20% with slipping (23 goals out of 150 episodes, 15.3%). The remaining 127 episodes ended in a hole, and no episode reached the 100-step limit. Without slipping the outcome is the same every time, because nothing is random: 8 steps, every episode. With slipping the chosen action is executed with probability 1/3 and each perpendicular direction with probability 1/3, so the agent can be pushed sideways. This is most dangerous at state 6 (both sideways moves are holes) and state 1 (one sideways move is a hole), which the route has to pass. Mean steps rose to about 10–14 because slipping sometimes delays the agent before it falls or finishes.

The random policy was poor in both modes: 0–4% success without slipping and 2–6% with it. These two ranges are not meaningfully different. A uniformly random action followed by a slip is still a uniformly random direction, so slipping changes nothing in distribution for this policy; the differences we see are sampling noise.

### Variation across batches

The three batches of the same condition are not identical when randomness is involved: for the fixed policy with slipping they gave 14%, 12% and 20%. A batch of 50 episodes with success probability about 15% has a standard error of about 5 percentage points, so this spread is expected. As a sanity check, an exact calculation with the transition probabilities (absorbing Markov chain, 100-step horizon, done with the help of Claude) gives about 15.5% for this policy, close to our pooled 15.3%. Without slipping all batches were identical, because the environment and the policy are both deterministic.

One successful episode is insufficient evidence because success can be luck: even the random policy reached the goal in some episodes. A reliable estimate of how good a policy is needs many episodes, and the batch-to-batch spread shows how uncertain even 50 episodes are.

### Why these runs do not train a policy

The fixed policy was written by hand before the experiments and never changes. The simulations only measure how good it is: no value estimates, action preferences or parameters are updated from the episode results, and results from earlier episodes do not influence later ones. The random policy is also not learning, since its actions do not depend on rewards. Training would require using the outcomes to improve the policy, which we do not do here.

## Part C — Custom solver

### Compare code with paper

Show V1 and the requested V2 values. Explain discrepancies.

### Values, policies and convergence

Link both value/policy maps. Record iteration counts, final value changes and tie-breaking rule.

### Simulation results

| Map | Batch seed | Goals /50 | Holes /50 | Time limits /50 | Mean steps | Mean discounted return |
| --- | --- | --- | --- | --- | --- | --- |

### Explain your results

Which values/actions changed with sand and water? Where did cost and risk matter? How do simulations relate to the computed values?

### Rule checks

Show boundary/wall behavior, slip probabilities, floor rewards and terminal handling.

