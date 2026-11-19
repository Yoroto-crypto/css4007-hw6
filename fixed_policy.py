"""Part B: YOUR fixed policy for FrozenLake 4x4.

Fill this in BEFORE running part_b.py, and commit it before the results.
Explain the reasoning for each state in SUBMISSION.md.

Map (state = row * 4 + col):
     0:S   1:F   2:F   3:F
     4:F   5:H   6:F   7:H
     8:F   9:F  10:F  11:H
    12:H  13:F  14:F  15:G

Actions in Gymnasium FrozenLake: 0 = LEFT, 1 = DOWN, 2 = RIGHT, 3 = UP.
Only the 11 non-terminal states need an action.
"""

POLICY = {0: 2, 1: 2, 2: 1, 3: 3, 4: 0, 6: 1, 8: 3, 9: 1, 10: 0, 13: 2, 14: 2}
