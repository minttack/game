"""Unreal Editor-only post-build verification for the IRL forest validation map.

Run after build_irl_forest_validation_level.py and inspect the emitted JSON.
This is a real-editor check, not a substitute for compiling or playing the map.
"""
import json
from pathlib import Path
import unreal

EXPECTED_MAP_PREFIX = "/Game/IRL/Maps/Lvl_IRL_Forest_VisualValidation."
EXPECTED_LABELS = {
    "IRL_OriginalForestTerrain": 1,
    **{f"IRL_Granite_{i:02d}": 1 for i in range(14)},
    **{f"IRL_Biome_{i:02d}": 1 for i in range(4)},
}
ASSET_PREFIX = "/Game/IRL/Visual/ProceduralStarter/"


def _asset_object_path(name):
    """UObject.get_path_name() includes the asset object after a dot."""
    return f"{ASSET_PREFIX}{name}.{name}"


def _validated_instance_count(actor, label, errors):
    """Read a genuine integer count and fail closed on missing/invalid evidence."""
    try:
        count = actor.last_generated_instance_count()
    except Exception as exc:
        errors.append(f"{label}: could not read generated instance count: {exc}")
        return None
    # Unreal's reflected int32 should arrive as a Python int. None, bool, strings,
    # and other unexpected values must never silently produce a PASS report.
    if type(count) is not int:
        errors.append(f"{label}: invalid generated instance count: {count!r}")
        return count
    if count <= 0:
        errors.append(f"{label}: no decorative instances generated")
    return count


def verify():
    editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor.get_editor_world()
    if world is None:
        raise RuntimeError("No Unreal Editor world is currently loaded")
    world_path = world.get_path_name()
    if not world_path.startswith(EXPECTED_MAP_PREFIX):
        raise RuntimeError(
            f"Wrong map loaded: {world_path}. Open the new IRL visual-validation map first."
        )

    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = actors_api.get_all_level_actors()
    by_label = {}
    for actor in actors:
        label = actor.get_actor_label()
        by_label.setdefault(label, []).append(actor)

    errors = []
    checks = {
        "loaded_map": world_path,
        "actor_count": len(actors),
        "expected_scene_labels": {},
        "mesh_assets": {},
        "material_assets": {},
        "biome_instances": {},
    }
    for label, count in EXPECTED_LABELS.items():
        found = by_label.get(label, [])
        checks["expected_scene_labels"][label] = len(found)
        if len(found) != count:
            errors.append(f"{label}: expected {count}, got {len(found)}")

    mesh_expectations = {
        "IRL_OriginalForestTerrain": "SM_IRL_TerrainPatch",
        **{f"IRL_Granite_{i:02d}": "SM_IRL_GraniteBoulder" for i in range(14)},
    }
    for label, mesh_name in mesh_expectations.items():
        found = by_label.get(label, [])
        if len(found) != 1:
            continue
        actor = found[0]
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        mesh = component.get_static_mesh() if component else None
        mesh_path = mesh.get_path_name() if mesh else None
        checks["mesh_assets"][label] = mesh_path
        expected_path = _asset_object_path(mesh_name)
        if mesh_path != expected_path:
            errors.append(f"{label}: expected mesh {expected_path}, got {mesh_path}")
        material_name = ("M_IRL_ForestSoil" if label == "IRL_OriginalForestTerrain"
                         else "M_IRL_Granite")
        material = component.get_material(0) if component else None
        material_path = material.get_path_name() if material else None
        checks["material_assets"][label] = material_path
        expected_material = _asset_object_path(material_name)
        if material_path != expected_material:
            errors.append(
                f"{label}: expected material {expected_material}, got {material_path}"
            )

    for index in range(4):
        label = f"IRL_Biome_{index:02d}"
        found = by_label.get(label, [])
        if len(found) != 1:
            continue
        checks["biome_instances"][label] = _validated_instance_count(
            found[0], label, errors
        )

    checks["status"] = "PASS" if not errors else "FAIL"
    checks["errors"] = errors
    output = Path(unreal.Paths.project_saved_dir()) / "IRLVisualValidationReport.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(checks, indent=2), encoding="utf-8")
    unreal.log(f"IRL visual validation: {checks['status']} — report: {output}")
    if errors:
        raise RuntimeError("IRL visual validation failed: " + "; ".join(errors))
    return str(output)


if __name__ == "__main__":
    verify()
