"""IRL Unreal 5.8 editor-only VISUAL VALIDATION MAP builder.

Execute after import_into_unreal.py inside the original Unreal Editor.
Never touches DefaultEngine.ini, does not overwrite any level, and clones the
actual /Game/ThirdPerson/Lvl_ThirdPerson template so original gameplay stays.

Unreal Python Editor API calls require engine testing before integration.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from forest_scene_plan import build_plan, verify_plan, ObjectPlacement

BASE_MAP = "/Game/ThirdPerson/Lvl_ThirdPerson"
NEW_MAP = "/Game/IRL/Maps/Lvl_IRL_Forest_VisualValidation"
ASSETS = "/Game/IRL/Visual/ProceduralStarter"
BIOME_CLASS = "/Script/IRL.IRLLivingBiomeDetailActor"


def _asset(unreal, suffix):
    path = f"{ASSETS}/{suffix}"
    value = unreal.load_asset(path)
    if value is None:
        raise RuntimeError(f"Missing imported IRL visual asset {path}. Run import_into_unreal.py first.")
    return value


def _spawn(unreal, actor_subsystem, cls, placement):
    x, y, z = placement.location_cm
    actor = actor_subsystem.spawn_actor_from_class(cls, unreal.Vector(x, y, z),
        unreal.Rotator(pitch=0.0, yaw=placement.yaw_degrees, roll=0.0))
    if not actor:
        raise RuntimeError(f"Unreal could not place {placement.name}")
    actor.set_actor_label(placement.name)
    return actor


def _materialize_mesh(unreal, editor_actors, placement, mesh, material):
    actor = _spawn(unreal, editor_actors, unreal.StaticMeshActor, placement)
    actor.set_actor_scale3d(unreal.Vector(placement.scale, placement.scale, placement.scale))
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    if component is None:
        raise RuntimeError(f"Spawned actor {placement.name} is missing a StaticMeshComponent")
    component.set_static_mesh(mesh)
    component.set_material(0, material)
    # Cloned level template remains untouched; only new map gets new geometry.
    return actor


def make(unreal):
    asset_library = unreal.EditorAssetLibrary
    level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    editor_actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if level_editor.is_in_play_in_editor():
        raise RuntimeError("Stop Play-In-Editor before building the IRL visual map")
    if not asset_library.does_asset_exist(BASE_MAP):
        raise RuntimeError("Original IRL ThirdPerson map missing; refusing unrelated scene")
    if asset_library.does_asset_exist(NEW_MAP):
        raise RuntimeError("IRL visual test map already exists; refusing to overwrite it")
    terrain = _asset(unreal, "SM_IRL_TerrainPatch")
    rock = _asset(unreal, "SM_IRL_GraniteBoulder")
    grass = _asset(unreal, "SM_IRL_GrassClump")
    soil_mat = _asset(unreal, "M_IRL_ForestSoil")
    rock_mat = _asset(unreal, "M_IRL_Granite")
    leaf_mat = _asset(unreal, "M_IRL_LeafGreen")
    biome_class = unreal.load_class(None, BIOME_CLASS)
    if biome_class is None:
        raise RuntimeError("IRL native biome class not compiled; build graphics PR #6 in Unreal first")

    plan = build_plan()
    verify_plan(plan)
    if not level_editor.new_level_from_template(NEW_MAP, BASE_MAP):
        raise RuntimeError("Failed to clone original map into non-destructive validation level")

    # From this point changes affect only the NEW named test map.
    biome_count = 0
    for placement in plan:
        if placement.category == "terrain":
            _materialize_mesh(unreal, editor_actors, placement, terrain, soil_mat)
        elif placement.category == "rock":
            _materialize_mesh(unreal, editor_actors, placement, rock, rock_mat)
        elif placement.category == "biome":
            actor = _spawn(unreal, editor_actors, biome_class, placement)
            actor.set_editor_property("ground_cover_mesh", grass)
            actor.set_editor_property("ground_cover_material", leaf_mat)
            actor.set_editor_property("stone_mesh", rock)
            actor.set_editor_property("stone_material", rock_mat)
            actor.set_editor_property("leaf_litter_mesh", grass)
            actor.set_editor_property("leaf_litter_material", leaf_mat)
            actor.set_editor_property("patch_radius_cm", 1600.0)
            actor.set_editor_property("seed", 20261022 + biome_count * 13)
            # In-editor preview; runtime also generates from BeginPlay.
            actor.apply_visual_tier(1)
            biome_count += 1
        elif placement.category == "player_start":
            original_starts = [a for a in editor_actors.get_all_level_actors()
                               if a.get_class() == unreal.PlayerStart.static_class()]
            # Copied template should have exactly one start. Preserve unrelated
            # spawns rather than picking an arbitrary multiplayer location.
            if len(original_starts) != 1:
                raise RuntimeError(f"Expected one PlayerStart in cloned map, got {len(original_starts)}")
            x, y, z = placement.location_cm
            original_starts[0].set_actor_location(unreal.Vector(x, y, z), False, False)

    existing = editor_actors.get_all_level_actors()
    if not any(a.get_class() == unreal.DirectionalLight.static_class() for a in existing):
        _spawn(unreal, editor_actors, unreal.DirectionalLight,
            ObjectPlacement("lighting", "IRL_VisualSun", (20000, 0, 1800), 15.0))
    if not any(a.get_class() == unreal.SkyLight.static_class() for a in existing):
        _spawn(unreal, editor_actors, unreal.SkyLight,
            ObjectPlacement("lighting", "IRL_VisualSky", (20000, 0, 1800)))
    if not any(a.get_class() == unreal.SkyAtmosphere.static_class() for a in existing):
        _spawn(unreal, editor_actors, unreal.SkyAtmosphere,
            ObjectPlacement("lighting", "IRL_VisualAtmosphere", (0, 0, 0)))
    if not level_editor.save_current_level():
        raise RuntimeError("New IRL visual-validation map could not be saved")
    unreal.log(f"IRL visual level saved: {NEW_MAP}, {len(plan)} planned placements")
    return NEW_MAP


if __name__ == "__main__":
    import unreal
    make(unreal)
