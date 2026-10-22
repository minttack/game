"""Strict acceptance and rejection tests for source-reported forest evidence."""
from copy import deepcopy
from forest_world_evidence import EXPECTED_MAP, PROBE_NAMES, assess_scene_report

def healthy():
    return {
        "source": "unreal_editor_line_trace",
        "map_path": EXPECTED_MAP,
        "actor_counts": {"terrain":1,"biome":4,"player_start":1},
        "ground_probes": [
            {"name":name,"hit_actor":"IRL_OriginalForestTerrain","blocking":True,
             "normal_z":0.97,"ground_z_cm":20.0,
             **({"spawn_clearance_cm":600.0} if name=="player_start" else {})}
            for name in sorted(PROBE_NAMES)],
        "biome_instances":{f"IRL_Biome_{i:02d}":{"grass":90,"rocks":20,"litter":35} for i in range(4)},
        "assigned_assets":{"soil":True,"granite":True,"foliage":True},
    }

checks=0
r=healthy()
ok=assess_scene_report(r)
assert ok["status"]=="EDITOR_REVIEW_ELIGIBLE" and ok["tests"]==14
checks+=1
def bad(mutator, reason):
    global checks
    sample=healthy()
    mutator(sample)
    result=assess_scene_report(sample)
    assert result["status"]=="NOT_ESTABLISHED",(reason,result)
    assert result["errors"],reason
    checks+=1

bad(lambda r: r.update(source="mocked_unreal_editor"),"untrusted declared source")
bad(lambda r: r.update(map_path="/Game/ThirdPerson/Lvl_ThirdPerson"),"wrong map")
bad(lambda r: r["actor_counts"].update(biome=3),"missing biome")
bad(lambda r: r["ground_probes"].pop(),"missing ground location")
bad(lambda r: r["ground_probes"].append(deepcopy(r["ground_probes"][0])),"duplicate ground observation")
bad(lambda r: r["ground_probes"][0].update(hit_actor="IRL_Granite_00"),"rock substituted as floor")
bad(lambda r: r["ground_probes"][0].update(blocking=False),"nonblocking collision")
bad(lambda r: r["ground_probes"][0].update(normal_z=0.32),"steep unwalkable slope")
bad(lambda r: r["ground_probes"][0].update(ground_z_cm=float("nan")),"NaN height")
bad(lambda r: next(p for p in r["ground_probes"] if p["name"]=="player_start").update(spawn_clearance_cm=40.0),"player intersects floor")
bad(lambda r: next(p for p in r["ground_probes"] if p["name"]=="player_start").update(spawn_clearance_cm=2000.0),"player in air")
bad(lambda r: r["biome_instances"]["IRL_Biome_03"].update(grass=0,rocks=0,litter=0),"missing foliage")
bad(lambda r: r["biome_instances"]["IRL_Biome_00"].update(grass=99999),"unbounded vegetation")
bad(lambda r: r["assigned_assets"].update(soil=False),"missing terrain material")
bad(lambda r: r["biome_instances"]["IRL_Biome_00"].update(rocks=-1),"negative instances")
bad(lambda r: r["biome_instances"]["IRL_Biome_00"].update(rocks=True),"invalid bool as count")
assert assess_scene_report(None)["status"]=="NOT_ESTABLISHED"
checks+=1
print("PASS",checks,"forest source-evidence policy groups, including fail-closed cases")
