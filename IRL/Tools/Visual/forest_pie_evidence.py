"""IRL BIE forest Play-in-Editor evidence policy (independent of Unreal).

PIE-scoped source reports can become REVIEW_ELIGIBLE, never "released".
An observation is an actual trace only when the editor script reports it;
this evaluator does not authenticate a human player, Unreal, or a device.
"""
import math

EXPECTED_MAP = "/Game/IRL/Maps/Lvl_IRL_Forest_VisualValidation"
TERRAIN_LABEL = "IRL_OriginalForestTerrain"
MIN_HORIZONTAL_MOVE_CM = 50.0
MAX_HORIZONTAL_MOVE_CM = 3000.0  # includes variable-duration PIE ticks on slower editor hosts
MIN_NORMAL_Z = 0.70
# Capsule base should be within a small tolerance of actually traced floor.
MIN_FOOT_CLEARANCE_CM = -25.0
MAX_FOOT_CLEARANCE_CM = 65.0

def _real(value):
    return type(value) in (float, int) and math.isfinite(value)

def _position(value):
    return isinstance(value, list) and len(value) == 3 and all(_real(v) for v in value)

def assess_pie(report):
    errors=[]
    if not isinstance(report,dict):
        return {"status":"NOT_ESTABLISHED","errors":["Invalid PIE report"]}
    if report.get("source") != "unreal_play_in_editor_character_physics":
        errors.append("Not a declared Play-in-Editor character physics source")
    if report.get("map_path") != EXPECTED_MAP:
        errors.append("Not the isolated IRL visual-test map")
    if report.get("game_world") is not True or report.get("possessed_character") is not True:
        errors.append("No actual possessed character in PIE game world")
    samples=report.get("samples")
    if not isinstance(samples, list) or len(samples)!=2:
        errors.append("Must record exactly two distinct game-state observations")
        samples=[]
    expected_stages=("grounded_before_move","grounded_after_move")
    for i, sample in enumerate(samples):
        if not isinstance(sample,dict):
            errors.append("Malformed game-state observation")
            continue
        if sample.get("stage")!=expected_stages[i]:
            errors.append("Incorrect game-state sample sequence")
        if not _position(sample.get("position_cm")):
            errors.append("Invalid player world position")
        elif not (16000 <= sample["position_cm"][0] <= 24000 and
                  -4000 <= sample["position_cm"][1] <= 4000):
            errors.append("Player left original 80m forest terrain")
        if sample.get("ground_actor")!=TERRAIN_LABEL or sample.get("blocking") is not True:
            errors.append("Ground trace missed the original blocking terrain")
        z=sample.get("normal_z")
        if not _real(z) or not (MIN_NORMAL_Z <= z <= 1.0001):
            errors.append("Ground under character is not walkable")
        foot=sample.get("foot_clearance_cm")
        if not _real(foot) or not MIN_FOOT_CLEARANCE_CM <= foot <= MAX_FOOT_CLEARANCE_CM:
            errors.append("Character capsule is not standing on terrain")
        h=sample.get("capsule_half_height_cm")
        if not _real(h) or not 30.0 <= h <= 250.0:
            errors.append("Character capsule height absent or implausible")
    if len(samples)==2 and all(isinstance(x,dict) and _position(x.get("position_cm")) for x in samples):
        before,after=samples[0]["position_cm"],samples[1]["position_cm"]
        moved=math.hypot(after[0]-before[0],after[1]-before[1])
        if not MIN_HORIZONTAL_MOVE_CM <= moved <= MAX_HORIZONTAL_MOVE_CM:
            errors.append("No believable horizontal movement through game input")
    else:
        moved=None
    result={
        "status":"PIE_REVIEW_ELIGIBLE" if not errors else "NOT_ESTABLISHED",
        "errors":sorted(set(errors)),
        "horizontal_movement_cm":round(moved,3) if moved is not None else None,
        "limitations":[
            "Script-reported engine measurements are not independently authenticated.",
            "This PIE result is not an Android FPS, thermals or two-player validation.",
            "No proof of AAA assets, persistence or autonomous BIE life is implied."
        ],
    }
    return result
