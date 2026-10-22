"""Deterministic pure-Python scene layout for the ONE IRL Unreal project.

Positions use centimeters, matching IRL and Unreal. No editor/network access.
This is a graphics validation region, not a separately shippable game.
"""
from dataclasses import dataclass
import random

TERRAIN_SIZE_CM = 8000
DEFAULT_CENTER_CM = (20000, 0, 0)
SEED = 20261022


@dataclass(frozen=True)
class ObjectPlacement:
    category: str
    name: str
    location_cm: tuple[float, float, float]
    yaw_degrees: float = 0.0
    scale: float = 1.0


def build_plan(seed=SEED, center_cm=DEFAULT_CENTER_CM):
    if not isinstance(seed, int) or not isinstance(center_cm, tuple) or len(center_cm) != 3:
        raise ValueError("Seed and world-space center must be valid")
    cx, cy, cz = (float(v) for v in center_cm)
    rng = random.Random(seed)
    placements = [ObjectPlacement("terrain", "IRL_OriginalForestTerrain", (cx, cy, cz))]
    for index in range(14):
        # Rock centers are strictly inside original 80m terrain extent.
        x = rng.uniform(-3100, 3100)
        y = rng.uniform(-3100, 3100)
        placements.append(ObjectPlacement("rock", f"IRL_Granite_{index:02d}",
            (cx + x, cy + y, cz + 140.0), rng.uniform(0, 360), rng.uniform(0.7, 2.4)))
    for index, (x, y) in enumerate([(-1200, -900), (1200, 900), (-900, 1400), (1300, -1200)]):
        placements.append(ObjectPlacement("biome", f"IRL_Biome_{index:02d}",
            (cx + x, cy + y, cz + 180.0), 0.0, 1.0))
    placements.append(ObjectPlacement("player_start", "IRL_OriginalForestSpawn",
        (cx - 300, cy, cz + 600)))
    return tuple(placements)


def verify_plan(placements):
    if len(placements) != 20:
        raise ValueError("Expected 1 terrain + 14 rocks + 4 biome regions + 1 player start")
    if len({p.name for p in placements}) != len(placements):
        raise ValueError("Duplicate scene actor identity")
    cx, cy, _ = next(p.location_cm for p in placements if p.category == "terrain")
    for p in placements:
        if p.category in {"rock", "biome", "player_start"}:
            # Biome actor's patch radius is 1600cm; keep all local traces on terrain.
            extra = 1600 if p.category == "biome" else 0
            if abs(p.location_cm[0] - cx) + extra > 4000 or abs(p.location_cm[1] - cy) + extra > 4000:
                raise ValueError("Scene decoration extends outside terrain tile")
        if p.scale <= 0:
            raise ValueError("Negative or zero mesh scale")
    return True
