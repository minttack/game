"""No-engine geometry, reproducibility and layout tests."""
from forest_scene_plan import build_plan, verify_plan
from collections import Counter

one=build_plan()
two=build_plan()
three=build_plan(seed=13)
assert one==two
assert one!=three
assert verify_plan(one)
assert Counter(x.category for x in one)=={"terrain":1,"rock":14,"biome":4,"player_start":1}
assert len({p.name for p in one})==len(one)
assert any(p.location_cm[0]>=20000 for p in one)
for item in one:
    assert isinstance(item.location_cm,tuple) and len(item.location_cm)==3
try:
    verify_plan(tuple(one[:-1]))
except ValueError:
    pass
else:
    raise AssertionError("Should reject missing PlayerStart")
print("PASS forest scene plan: deterministic, bounded, spatially valid and unique")
