"""Pure-Python placement plan for IRL's one Unreal game, not an alternative game.

No Unreal dependency. The 65x65 mesh is read from the exact generated OBJ;
this prevents illustrative positions from being mistaken for grounded placement.
"""
from dataclasses import dataclass
from pathlib import Path
import math
import random

SIZE = 65
HALF_EXTENT_CM = 4000.0
TAG = 'IRL_VISUAL_STAGE_V01'


@dataclass(frozen=True)
class Placement:
    role: str
    asset: str
    x_cm: float
    y_cm: float
    z_cm: float
    yaw_deg: float = 0.0
    scale: float = 1.0


class TerrainHeightfield:
    def __init__(self, source):
        path = Path(source)
        raw = [line.split() for line in path.read_text(encoding='utf-8').splitlines()
               if line.startswith('v ')]
        if len(raw) != SIZE * SIZE:
            raise ValueError('Expected exactly 4225 vertices in the IRL 65x65 terrain source')
        self.heights = []
        for index, values in enumerate(raw):
            if len(values) != 4:
                raise ValueError('Malformed terrain vertex')
            _, x, y, z = values
            x, y, z = float(x), float(y), float(z)
            expected_x = -HALF_EXTENT_CM + (index % SIZE) * 125.0
            expected_y = -HALF_EXTENT_CM + (index // SIZE) * 125.0
            if (not all(math.isfinite(t) for t in (x, y, z))
                    or abs(x - expected_x) > 0.001
                    or abs(y - expected_y) > 0.001):
                raise ValueError('Vertex grid not in expected Unreal centimeter layout')
            self.heights.append(z)

    def height(self, x_cm, y_cm):
        if (not all(math.isfinite(v) for v in (x_cm, y_cm))
                or abs(x_cm) > HALF_EXTENT_CM or abs(y_cm) > HALF_EXTENT_CM):
            raise ValueError('Terrain query outside verified geometry')
        u, v = (x_cm + HALF_EXTENT_CM) / 125.0, (y_cm + HALF_EXTENT_CM) / 125.0
        i, j = min(int(u), SIZE - 2), min(int(v), SIZE - 2)
        tx, ty = u - i, v - j
        a = self.heights[j * SIZE + i]
        b = self.heights[j * SIZE + i + 1]
        c = self.heights[(j + 1) * SIZE + i]
        d = self.heights[(j + 1) * SIZE + i + 1]
        return (a * (1-tx)*(1-ty) + b*tx*(1-ty)
                + c*(1-tx)*ty + d*tx*ty)


def plan_stage(source, anchor_xyz, *, seed=60112, rock_count=8):
    """Plan one bounded 80m patch offset from a real editor anchor.

    'anchor' is supplied by the Unreal editor, never inferred from the player.
    No permanent changes; the editor tool uses a separate explicit apply gate.
    """
    if len(anchor_xyz) != 3 or not all(math.isfinite(v) for v in anchor_xyz):
        raise ValueError('Need finite scene anchor XYZ in cm')
    if not (0 <= rock_count <= 20):
        raise ValueError('Maximum 20 visual rocks per preview area')
    field = TerrainHeightfield(source)
    ax, ay, az = anchor_xyz
    plan = [Placement('terrain','SM_IRL_TerrainPatch',ax,ay,az)]
    plan.append(Placement('biome','IRLLivingBiomeDetailActor',ax,ay,
                          az + field.height(0,0) + 250.0))
    rand = random.Random(seed)
    for index in range(rock_count):
        angle = 2 * math.pi * (index + 0.22 * rand.random()) / max(rock_count,1)
        radius = rand.uniform(900.0, 3000.0)
        x,y = radius*math.cos(angle),radius*math.sin(angle)
        scale = rand.uniform(0.65,1.40)
        plan.append(Placement(f'rock_{index:02d}', 'SM_IRL_GraniteBoulder',
            ax+x,ay+y,az+field.height(x,y)+65.0*scale-10.0,
            rand.uniform(0,360),scale))
    return tuple(plan)


def confirm_assets(names):
    required = {'SM_IRL_TerrainPatch','SM_IRL_GraniteBoulder','SM_IRL_GrassClump',
                'M_IRL_ForestSoil','M_IRL_Granite','M_IRL_LeafGreen'}
    missing = required.difference(names)
    if missing:
        raise ValueError('Missing required original IRL Unreal assets: '+', '.join(sorted(missing)))
    return True


def classify_existing(labels):
    """Fail closed on partial or complete prior placements to avoid duplicates."""
    return any(str(x).startswith(TAG) for x in labels)
