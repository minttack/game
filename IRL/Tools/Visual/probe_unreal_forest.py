"""Run after building IRL Forest VisualValidation map in Unreal Editor 5.8.

This probe uses ACTUAL editor-world collision queries and rendered-instance
component counts, not guesses. It writes evidence under Project/Saved/IRL,
never modifies the map and never self-certifies a playable Android game.
Enable Python Editor Script Plugin. Then Tools > Execute Python Script.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from forest_world_evidence import EXPECTED_MAP, assess_scene_report

GROUND_ACTOR = "IRL_OriginalForestTerrain"
BIOME_NAMES = tuple(f"IRL_Biome_{i:02d}" for i in range(4))


def _get(hit, key):
    return hit.get_editor_property(key)


def _normalize_hit(raw):
    """Unreal Python versions may expose a HitResult or a (bool, HitResult)."""
    if raw is None:
        return None
    if isinstance(raw, tuple):
        if len(raw) != 2 or not isinstance(raw[0], bool):
            raise RuntimeError("Unexpected Unreal trace return schema")
        if not raw[0]:
            return None
        return raw[1]
    return raw


def _material_assigned(actor, unreal):
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    if component is None:
        return False
    return component.get_static_mesh() is not None and component.get_material(0) is not None


def _biome_instances(actor, unreal):
    # Three named native HISM components from graphics PR #6. Count only what
    # the real Unreal Editor currently has built; do not infer from design tiers.
    components = actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
    groups = {"GroundCover": "grass", "StoneInstances": "rocks", "LeafLitter": "litter"}
    counts = {}
    for component in components:
        key = groups.get(component.get_name())
        if key:
            counts[key] = int(component.get_instance_count())
    return counts


def _ground_trace(unreal, world, x, y, start_z, terrain, to_ignore):
    start = unreal.Vector(x, y, start_z)
    end = unreal.Vector(x, y, -2200.0)
    hit = _normalize_hit(unreal.SystemLibrary.line_trace_single(
        world,
        start, end,
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True, to_ignore,
        unreal.DrawDebugTrace.NONE,
        True))
    if hit is None:
        return dict(hit_actor="", blocking=False, normal_z=None, ground_z_cm=None)
    actor = _get(hit, "hit_actor")
    normal = _get(hit, "impact_normal")
    point = _get(hit, "impact_point")
    return dict(
        hit_actor=actor.get_actor_label() if actor is not None else "",
        blocking=bool(_get(hit, "blocking_hit")),
        normal_z=float(normal.z),
        ground_z_cm=float(point.z))


def observe_editor(unreal):
    editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if level.is_in_play_in_editor():
        raise RuntimeError("Exit PIE before taking the editor-world audit")
    world = editor.get_editor_world()
    if world is None:
        raise RuntimeError("Unreal Editor world unavailable")
    world_name = str(world.get_path_name())
    # Restrict observations to the separately cloned validation map, never the
    # original map or an arbitrary Unreal project.
    if not world_name.startswith(EXPECTED_MAP + "."):
        raise RuntimeError("Open only " + EXPECTED_MAP + " before running IRL audit")

    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    by_label = {a.get_actor_label(): a for a in actors}
    if len(by_label) != len(actors):
        raise RuntimeError("Duplicate actor labels prohibit trustworthy matching")
    terrain = by_label.get(GROUND_ACTOR)
    biomes = [by_label.get(name) for name in BIOME_NAMES]
    starts = [a for a in actors if a.get_class() == unreal.PlayerStart.static_class()]
    if terrain is None or any(x is None for x in biomes) or len(starts) != 1:
        raise RuntimeError("IRL terrain, four biomes or single starting player missing")

    decorative = [a for a in actors if a.get_actor_label().startswith("IRL_Granite_")]
    if len(decorative) != 14:
        raise RuntimeError("VisualValidation rock inventory is incomplete")
    # Visibility trace ignores decorative rocks so each observation must prove
    # the TERRAIN itself blocks collision. No spoofed rock-as-ground result.
    probes = []
    for gx in (-1, 0, 1):
        for gy in (-1, 0, 1):
            x, y = 20000.0 + gx * 2400.0, gy * 2400.0
            data = _ground_trace(unreal, world, x, y, 1500.0, terrain, decorative)
            data["name"] = f"grid_{gx}_{gy}"
            probes.append(data)
    for i, actor in enumerate(biomes):
        pos = actor.get_actor_location()
        data = _ground_trace(unreal, world, float(pos.x), float(pos.y), 1800.0, terrain, decorative)
        data["name"] = f"biome_{i:02d}"
        probes.append(data)
    start = starts[0].get_actor_location()
    data = _ground_trace(unreal, world, float(start.x), float(start.y), float(start.z) + 200.0, terrain, decorative)
    data["name"] = "player_start"
    data["spawn_clearance_cm"] = (float(start.z) - data["ground_z_cm"]
                                  if data["ground_z_cm"] is not None else None)
    probes.append(data)

    biome_counts = {name: _biome_instances(by_label[name], unreal) for name in BIOME_NAMES}
    assigned = {
        "soil": _material_assigned(terrain, unreal),
        "granite": all(_material_assigned(a, unreal) for a in decorative),
        "foliage": all(
            a.get_editor_property("ground_cover_mesh") is not None and
            a.get_editor_property("ground_cover_material") is not None
            for a in biomes)
    }
    return {
        "source": "unreal_editor_line_trace",
        "map_path": EXPECTED_MAP,
        "editor_world_path": world_name,
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "actor_counts": {"terrain": 1, "biome": len(biomes), "player_start": len(starts)},
        "ground_probes": probes, "biome_instances": biome_counts,
        "assigned_assets": assigned,
        "device": "UNREAL_EDITOR_ONLY_NOT_ANDROID",
    }


def main(unreal):
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target = Path(unreal.Paths.project_saved_dir()) / "IRL" / f"forest_editor_audit_{now}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        report = observe_editor(unreal)
        assessment = assess_scene_report(report)
    except Exception as exc:
        report = {"source": "unreal_editor_probe_exception", "failure": str(exc)}
        assessment = {"status": "NOT_ESTABLISHED", "errors": [str(exc)]}
    report["assessment"] = assessment
    target.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf8")
    unreal.log("IRL forest audit: " + str(target) + " | " + assessment["status"])
    if assessment["status"] != "EDITOR_REVIEW_ELIGIBLE":
        raise RuntimeError("IRL forest editor evidence gate FAILED: see " + str(target))
    # Only succeeds for observed Editor world; never claim full UE gameplay
    # or Android/mobile FPS. A physical packaged-game test is still necessary.
    return target


if __name__ == "__main__":
    import unreal
    main(unreal)
