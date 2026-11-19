"""Floor rules, kept separate from the solver.
To add a new floor type: add one entry to FLOORS. The solver needs no changes.

reward   : received when a move ENDS on this tile
passable : False for walls
terminal : episode ends when entering this tile
slip     : probability of EACH perpendicular direction when a move STARTS on this tile
           (0 = deterministic). Ice: 0.1 each, so 0.8 for the chosen direction.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Floor:
    name: str
    reward: float = 0.0
    passable: bool = True
    terminal: bool = False
    slip: float = 0.0


FLOORS = {
    ".": Floor("floor", -1),
    "S": Floor("start", -1),
    "M": Floor("mud", -3),
    "I": Floor("ice", -1, slip=0.1),
    "G": Floor("goal", 10, terminal=True),
    "H": Floor("hole", -10, terminal=True),
    "#": Floor("wall", 0, passable=False),
    "D": Floor("sand", -2),
    "W": Floor("water", -5),
}


def load_config(path="maps.json"):
    """Read maps, discount, seeds and tile rules from the assignment's maps.json."""
    import json
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def floors_from_config(cfg):
    """Build the floor table from maps.json (the only place where tile rules live)."""
    return {ch: Floor(name=t["meaning"], reward=t.get("reward", 0.0),
                      passable=t.get("traversable", True), terminal=t.get("terminal", False),
                      slip=t.get("perpendicular_each", 0.0))
            for ch, t in cfg["tiles"].items()}
