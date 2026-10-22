"""Run inside UE 5.8 Python Editor: Tools > Execute Python Script.
Enable Python Editor Script Plugin. Source assets should be generated locally first.
Never replaces the original IRL map; refuses existing named assets by default.
"""
from pathlib import Path
import os
import unreal

SOURCE_DIR = Path(os.environ.get('IRL_PBR_SOURCE_DIR', str(Path(__file__).resolve().parent / 'Generated')))
DEST = '/Game/IRL/Visual/ProceduralStarter'
OVERWRITE = False

if not SOURCE_DIR.exists():
    raise RuntimeError('Run generate_irl_showcase.py first. Set IRL_PBR_SOURCE_DIR to generated folder.')

assets = sorted(list(SOURCE_DIR.glob('T_*.png')) + list(SOURCE_DIR.glob('SM_IRL_*.obj')))
assert len(assets) == 15, f'Expected 12 textures and 3 meshes, got {len(assets)}'

editor = unreal.EditorAssetLibrary
editor.make_directory(DEST)
tasks=[]
for file in assets:
    path = DEST + '/' + file.stem
    if editor.does_asset_exist(path) and not OVERWRITE:
        unreal.log(f'IRL: preserving existing asset {path}')
        continue
    task=unreal.AssetImportTask()
    task.filename = str(file)
    task.destination_path = DEST
    task.destination_name = file.stem
    task.automated = True
    task.save = True
    task.replace_existing = OVERWRITE
    tasks.append(task)
if tasks:
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    unreal.log(f'IRL: imported {len(tasks)} original starter assets')

for name in ['ForestSoil','Granite','LeafGreen']:
    for channel in ['Normal','Roughness','Height']:
        tex = unreal.load_asset(f'{DEST}/T_{name}_{channel}')
        if tex is None: raise RuntimeError(f'Missing imported texture {name} {channel}')
        tex.set_editor_property('srgb', False)
        if channel=='Normal':
            tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP)
        else:
            tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
        editor.save_loaded_asset(tex)

for name in ['ForestSoil','Granite','LeafGreen']:
    asset_path = f'{DEST}/M_IRL_{name}'
    if editor.does_asset_exist(asset_path):
        if not OVERWRITE:
            unreal.log(f'IRL: preserving material {asset_path}')
            continue
        material = unreal.load_asset(asset_path)
    else:
        material=unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            f'M_IRL_{name}', DEST, unreal.Material, unreal.MaterialFactoryNew())
    assert material
    if name == 'LeafGreen':
        material.set_editor_property('two_sided', True)  # thin foliage blades
    unreal.MaterialEditingLibrary.delete_all_material_expressions(material)
    for kind,property_id,output in [
        ('BaseColor',unreal.MaterialProperty.MP_BASE_COLOR,'RGB'),
        ('Normal',unreal.MaterialProperty.MP_NORMAL,'RGB'),
        ('Roughness',unreal.MaterialProperty.MP_ROUGHNESS,'R'),
    ]:
        texture=unreal.load_asset(f'{DEST}/T_{name}_{kind}')
        if texture is None: raise RuntimeError(f'Missing {name} {kind}')
        node=unreal.MaterialEditingLibrary.create_material_expression(
            material, unreal.MaterialExpressionTextureSample, -500, len(name)*15)
        node.set_editor_property('texture',texture)
        ok=unreal.MaterialEditingLibrary.connect_material_property(node,output,property_id)
        if not ok: raise RuntimeError(f'Material connection failed {name} {kind}')
    errors=unreal.MaterialEditingLibrary.recompile_material(material)
    if errors: raise RuntimeError(f'Material {name} failed to compile: {list(errors)}')
    editor.save_loaded_asset(material)
    unreal.log(f'IRL: created material {asset_path}')

# The opt-in IRL visual stage traces this exact terrain mesh for foliage.
# A single, static 8192-triangle patch is acceptable for this staging test;
# do not apply complex-as-simple to high-detail mobile environments broadly.
terrain_mesh = unreal.load_asset(f'{DEST}/SM_IRL_TerrainPatch')
if terrain_mesh is None:
    raise RuntimeError('Source terrain mesh did not import')
body_setup = terrain_mesh.get_editor_property('body_setup')
if body_setup is None:
    raise RuntimeError('Terrain mesh has no collision body setup')
body_setup.set_editor_property('collision_trace_flag',
                               unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
editor.save_loaded_asset(terrain_mesh)
unreal.log('IRL: stage terrain static surface collision configured for biome traces')

unreal.log('IRL assets imported. Existing game level unchanged; use assemble_irl_stage.py to place opt-in area.')
