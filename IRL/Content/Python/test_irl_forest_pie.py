"""IRL first real gameplay physics audit — UE 5.8 PythonAutomationTest.

Requires Python Editor Script Plugin and PythonAutomationTest Plugin.
Discovered under Editor > Python > IRL > test_irl_forest_pie.
Uses *actual PIE* player-character movement and collision, not mock values.
Does not start a separate game, edit the original map, or certify Android.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import unreal

VISUAL_TOOLS = Path(__file__).resolve().parents[2] / "Tools" / "Visual"
sys.path.insert(0, str(VISUAL_TOOLS))
from forest_world_evidence import EXPECTED_MAP
from forest_pie_evidence import assess_pie
from probe_unreal_forest import main as editor_audit, _normalize_hit, _get

state = {"world": None, "result": None}
sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
unreal_editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def _ground_sample(world, character, stage):
    position = character.get_actor_location()
    capsule = character.get_capsule_component()
    if capsule is None:
        raise RuntimeError("PIE character missing actual collision capsule")
    hh = float(capsule.get_scaled_capsule_half_height())
    terrain = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.StaticMeshActor)
    rocks = [a for a in terrain if a.get_actor_label().startswith("IRL_Granite_")]
    raw = unreal.SystemLibrary.line_trace_single(
        world,
        unreal.Vector(position.x, position.y, position.z + 100.0),
        unreal.Vector(position.x, position.y, position.z - hh - 600.0),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        [character] + rocks,
        unreal.DrawDebugTrace.NONE,
        True)
    hit = _normalize_hit(raw)
    if hit is None:
        return {"stage": stage, "position_cm": [float(position.x),float(position.y),float(position.z)],
                "capsule_half_height_cm": hh,
                "ground_actor": "", "blocking": False, "normal_z": None, "foot_clearance_cm": None}
    actor = _get(hit,"hit_actor")
    normal = _get(hit,"impact_normal")
    floor = _get(hit,"impact_point")
    return {
        "stage": stage,
        "position_cm": [float(position.x),float(position.y),float(position.z)],
        "capsule_half_height_cm": hh,
        "ground_actor": actor.get_actor_label() if actor else "",
        "blocking": bool(_get(hit,"blocking_hit")),
        "normal_z": float(normal.z),
        "foot_clearance_cm": float(position.z - hh - floor.z),
    }


def _save_report(report):
    path = Path(unreal.Paths.project_saved_dir())/"IRL"/(
        "forest_pie_player_test_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,allow_nan=False),encoding="utf8")
    unreal.log("IRL PIE physical movement report: " + str(path))
    return path


@unreal.AutomationScheduler.add_latent_command
def load_only_the_original_game_forest_test_map():
    if sub.is_in_play_in_editor():
        raise RuntimeError("IRL audit cannot start with an already running PIE")
    if not unreal.EditorAssetLibrary.does_asset_exist(EXPECTED_MAP):
        raise RuntimeError("IRL validation map missing; run safe editor forest builder first")
    if not sub.load_level(EXPECTED_MAP):
        raise RuntimeError("Unreal cannot load isolated IRL validation map")


@unreal.AutomationScheduler.add_latent_command
def require_actual_editor_collision_before_play():
    state["editor_report"] = str(editor_audit(unreal))


@unreal.AutomationScheduler.add_latent_command
def begin_actual_gameplay():
    sub.editor_request_begin_play()


@unreal.AutomationScheduler.add_latent_command
def move_avatar_through_real_game_physics():
    report = {
        "source": "unreal_play_in_editor_character_physics",
        "map_path": EXPECTED_MAP,
        "game_world": False,
        "possessed_character": False,
        "samples": [],
        "editor_preflight_report": state.get("editor_report"),
        "device": "UE_EDITOR_PIE_NOT_ANDROID",
    }
    try:
        world = None
        character = None
        # Release Python between frames, permitting an actual UE world to tick.
        for _ in range(240):
            if sub.is_in_play_in_editor():
                world = unreal_editor.get_game_world()
                if world is not None:
                    character = unreal.GameplayStatics.get_player_character(world, 0)
                    if character is not None and character.get_controller() is not None:
                        break
            yield
        if world is None or character is None or character.get_controller() is None:
            raise RuntimeError("PIE never possessed a real player character")
        report["game_world"] = True
        report["possessed_character"] = True

        # Observe after the pawn has a chance to FALL and land on collision.
        for _ in range(90):
            yield
        report["samples"].append(_ground_sample(world,character,"grounded_before_move"))

        # Use CharacterMovement input, never teleport or move the player by fiat.
        for _ in range(75):
            character.add_movement_input(unreal.Vector(1.0,0.0,0.0),1.0,True)
            yield
        for _ in range(12):
            yield
        report["samples"].append(_ground_sample(world,character,"grounded_after_move"))
        report["assessment"] = assess_pie(report)
    except Exception as exc:
        report["assessment"] = {"status":"NOT_ESTABLISHED","errors":[str(exc)]}
    finally:
        # Persist evidence BEFORE requesting PIE teardown. No test can leave
        # the editor silently in an active game after an assertion failure.
        path=_save_report(report)
        sub.editor_request_end_play()
    if report["assessment"]["status"]!="PIE_REVIEW_ELIGIBLE":
        raise RuntimeError("IRL PIE gameplay failed; inspect " + str(path) + " " +
                           str(report["assessment"]["errors"]))
    unreal.log("IRL PIE review eligible (NOT Android/release): " + str(path))
