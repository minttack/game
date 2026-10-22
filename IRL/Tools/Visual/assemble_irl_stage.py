"""Opt-in Unreal Editor 5.8 setup for the EXISTING IRL project and open level.

GENERATE source assets, run import_into_unreal.py, then run this script from
Tools > Execute Python Script in the Unreal Editor (PythonScriptPlugin enabled).
Default is DRY RUN. Apply only if IRL_STAGE_APPLY=1; save only if also
IRL_STAGE_SAVE=1. Never alters the default map, game mode or runtime life state.
No stand-alone game is created. Assets and world are always inspected first.
"""
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from scene_stage_core import TAG, confirm_assets, classify_existing, plan_stage

import unreal

DEST = '/Game/IRL/Visual/ProceduralStarter'
APPLY = os.environ.get('IRL_STAGE_APPLY') == '1'
SAVE = os.environ.get('IRL_STAGE_SAVE') == '1'


def setup():
    if SAVE and not APPLY:
        raise RuntimeError('IRL_STAGE_SAVE requires IRL_STAGE_APPLY=1')
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
    if not level:
        raise RuntimeError('Open the EXISTING IRL level in Unreal Editor before running')
    editor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = list(editor.get_all_level_actors())
    labels = [actor.get_actor_label() for actor in actors]
    if classify_existing(labels):
        unreal.log_warning('IRL visual stage already exists. Safe no-op: no duplicate actors spawned.')
        return {'status':'already_present','planned':0}
    assets = {}
    needed = ('SM_IRL_TerrainPatch','SM_IRL_GraniteBoulder','SM_IRL_GrassClump',
              'M_IRL_ForestSoil','M_IRL_Granite','M_IRL_LeafGreen')
    for name in needed:
        assets[name] = unreal.load_asset(f'{DEST}/{name}')
    confirm_assets({k for k,v in assets.items() if v is not None})
    clazz = unreal.load_class(None,'/Script/IRL.IRLLivingBiomeDetailActor')
    if not clazz:
        raise RuntimeError('IRL graphics C++ (PR #6) must be compiled and loaded before applying stage')
    anchor = (0.0,0.0,0.0)
    # Position the stage ~140m from the first level start. No default player
    # pawn or tutorial objective is moved, deleted or replaced.
    starts=[actor for actor in actors if isinstance(actor,unreal.PlayerStart)]
    if starts:
        starts.sort(key=lambda actor:actor.get_actor_label())
        point=starts[0].get_actor_location()
        anchor = (point.x + 14000.0,point.y,point.z - 100.0)
    terrain_file = Path(os.environ.get('IRL_PBR_SOURCE_DIR',str(HERE/'Generated'))) / 'SM_IRL_TerrainPatch.obj'
    plan=plan_stage(terrain_file, anchor)
    unreal.log(f'IRL stage {"APPLY" if APPLY else "DRY RUN"}: '
               f'{len(plan)} placements, anchor={anchor}; no existing game actors modified')
    for item in plan:
        unreal.log(f'  {item.role}: {item.asset} XY=({item.x_cm:.0f},{item.y_cm:.0f}), Z={item.z_cm:.0f}')
    if not APPLY:
        return {'status':'dry_run','planned':len(plan)}
    spawned=[]
    try:
        for item in plan:
            location=unreal.Vector(item.x_cm,item.y_cm,item.z_cm)
            rotation=unreal.Rotator(0.0,item.yaw_deg,0.0)
            actor_type = clazz if item.role=='biome' else unreal.StaticMeshActor
            actor=editor.spawn_actor_from_class(actor_type,location,rotation)
            if actor is None:
                raise RuntimeError('Failed to spawn '+item.role)
            spawned.append(actor)
            actor.set_actor_label(TAG+'_'+item.role)
            if item.role=='biome':
                actor.set_editor_property('ground_cover_mesh', assets['SM_IRL_GrassClump'])
                actor.set_editor_property('ground_cover_material', assets['M_IRL_LeafGreen'])
                actor.set_editor_property('stone_mesh', assets['SM_IRL_GraniteBoulder'])
                actor.set_editor_property('stone_material', assets['M_IRL_Granite'])
                actor.set_editor_property('seed', 60112)
            else:
                component=actor.get_editor_property('static_mesh_component')
                component.set_static_mesh(assets[item.asset])
                component.set_material(0,assets['M_IRL_ForestSoil' if item.role=='terrain' else 'M_IRL_Granite'])
                actor.set_actor_scale3d(unreal.Vector(item.scale,item.scale,item.scale))
        if SAVE:
            ok=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
            if not ok:raise RuntimeError('Could not save level. Check content folder status/permissions')
        else:
            unreal.log_warning('IRL stage PLACED but NOT SAVED. Inspect visually, then save manually only if approved.')
    except Exception:
        # Revert only actors spawned by THIS invocation; leave existing game intact.
        for actor in reversed(spawned):
            editor.destroy_actor(actor)
        raise
    return {'status':'placed' if SAVE else 'placed_unsaved','planned':len(plan)}


if __name__=='__main__':
    unreal.log(str(setup()))
