"""IRL real-PIE evidence assessment regression tests, no Unreal required."""
from copy import deepcopy
from forest_pie_evidence import assess_pie, EXPECTED_MAP

def healthy():
    base={"capsule_half_height_cm":88.0,"ground_actor":"IRL_OriginalForestTerrain",
          "blocking":True,"normal_z":0.98,"foot_clearance_cm":5.0}
    return {"source":"unreal_play_in_editor_character_physics","map_path":EXPECTED_MAP,
            "game_world":True,"possessed_character":True,
            "samples":[{"stage":"grounded_before_control","position_cm":[19700.0,0.0,110.0],**base},
                       {"stage":"grounded_after_control","position_cm":[19702.0,0.0,110.0],**base},
                       {"stage":"grounded_after_input","position_cm":[20242.0,0.0,124.0],**base}]}

cases=0
r=assess_pie(healthy())
assert r["status"]=="PIE_REVIEW_ELIGIBLE" and r["input_movement_cm"]==540.0 and r["no_input_drift_cm"]==2.0
cases+=1
def fail(modifier,tag):
    global cases
    report=healthy()
    modifier(report)
    checked=assess_pie(report)
    assert checked["status"]=="NOT_ESTABLISHED" and checked["errors"],(tag,checked)
    cases+=1

fail(lambda r:r.update(source="mock_pie"),"fake declared origin")
fail(lambda r:r.update(map_path="/Game/Wrong"),"different game map")
fail(lambda r:r.update(game_world=False),"no game world")
fail(lambda r:r.update(possessed_character=False),"unpossessed")
fail(lambda r:r["samples"].pop(),"missing sample")
fail(lambda r:r["samples"][2].update(stage="grounded_before_control"),"stage replay")
fail(lambda r:r["samples"][2].update(position_cm=[19702.,0.,124.]),"no walking")
fail(lambda r:r["samples"][2].update(position_cm=[23800.,0.,124.]),"too much displacement")
fail(lambda r:r["samples"][2].update(position_cm=[float('nan'),0.,124.]),"NaN location")
fail(lambda r:r["samples"][2].update(position_cm=[24500.,0.,124.]),"outside ground")
fail(lambda r:r["samples"][2].update(blocking=False),"no physics collision")
fail(lambda r:r["samples"][2].update(ground_actor="IRL_Granite_00"),"rock instead of ground")
fail(lambda r:r["samples"][2].update(normal_z=0.4),"not walkable")
fail(lambda r:r["samples"][2].update(foot_clearance_cm=150.),"hovering")
fail(lambda r:r["samples"][2].update(foot_clearance_cm=-100.),"under ground")
fail(lambda r:r["samples"][2].update(capsule_half_height_cm=False),"invalid capsule geometry")
fail(lambda r:r["samples"][2].update(foot_clearance_cm=float('inf')),"infinite height")
fail(lambda r:r["samples"][2].update(position_cm=[20242,0,124,1]),"bad dimensionality")
fail(lambda r:r["samples"][1].update(position_cm=[19800.,0.,110.]),"passive drift too high")
assert assess_pie(None)["status"]=="NOT_ESTABLISHED"
cases+=1
print("PASS",cases,"source-assessed PIE policy scenarios (no UE runtime claim)")
