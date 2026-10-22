"""IRL source-manifest and walkable collision regression checks.

Uses an Unreal API stub; tests contract only, not the engine physics solver.
"""
import subprocess
import sys
import tempfile
from pathlib import Path
from forest_collision_gate import (
    verify_source_manifest, ensure_imported_ground_collision,
    require_walkable_terrain_component, ORIGINAL_ASSET_PATH
)

source=Path(__file__).with_name("generate_irl_showcase.py")
with tempfile.TemporaryDirectory() as tmp:
    folder=Path(tmp)
    subprocess.run([sys.executable,str(source),"--size","256","--out",str(folder),"--seed","20261022"],check=True,capture_output=True)
    assert verify_source_manifest(folder)==16
    original=(folder/"T_ForestSoil_Normal.png").read_bytes()
    (folder/"T_ForestSoil_Normal.png").write_bytes(original[:-1]+bytes([original[-1]^1]))
    try:verify_source_manifest(folder)
    except RuntimeError as exc:assert "checksum mismatch" in str(exc)
    else:raise AssertionError("Corrupt texture accepted")
    (folder/"T_ForestSoil_Normal.png").write_bytes(original)
    assert verify_source_manifest(folder)==16
    (folder/"SM_IRL_GrassClump.obj").unlink()
    try:verify_source_manifest(folder)
    except RuntimeError as exc:assert "source missing" in str(exc)
    else:raise AssertionError("Missing mesh accepted")
print("PASS original source manifest: 16 verified files, corruption/missing source rejected")

class Flag:
    CTF_USE_COMPLEX_AS_SIMPLE=3
class Unreal:
    CollisionTraceFlag=Flag
    class StaticMeshComponent: pass
class Body:
    def __init__(self,flag=0):self.flag=flag
    def get_editor_property(self,name):
        assert name=="collision_trace_flag"
        return self.flag
    def set_editor_property(self,name,v):
        assert name=="collision_trace_flag"
        self.flag=v
class Mesh:
    def __init__(self,body):self.body=body
    def get_editor_property(self,name):
        assert name=="body_setup"
        return self.body

saves=[]
def save_and_confirm(mesh):
    saves.append(mesh)
    return True
mesh=Mesh(Body())
target=ORIGINAL_ASSET_PATH+"/SM_IRL_TerrainPatch"
assert ensure_imported_ground_collision(Unreal,mesh,target,save_and_confirm)
assert saves==[mesh]
assert mesh.body.flag==Flag.CTF_USE_COMPLEX_AS_SIMPLE
assert ensure_imported_ground_collision(Unreal,mesh,target,save_and_confirm)
assert saves==[mesh], "Existing valid collision should not be re-saved"
failed=Mesh(Body())
try:ensure_imported_ground_collision(Unreal,failed,target,lambda mesh: False)
except RuntimeError as exc:assert 'failed to save' in str(exc)
else:raise AssertionError('Unsaved physics configuration accepted')
try:ensure_imported_ground_collision(Unreal,mesh,"/Game/Other/Unrelated",save_and_confirm)
except RuntimeError as exc:assert "outside IRL" in str(exc)
else:raise AssertionError("Unrelated asset was accepted")
try:ensure_imported_ground_collision(Unreal,Mesh(None),target,save_and_confirm)
except RuntimeError as exc:assert "no BodySetup" in str(exc)
else:raise AssertionError("Missing collision body accepted")
class Component:
    def __init__(self):self.profile="None"
    def set_collision_profile_name(self,value):self.profile=value
    def get_collision_profile_name(self):return self.profile
class Actor:
    def __init__(self,component):self.component=component
    def get_component_by_class(self,cls):return self.component
component=Component()
assert require_walkable_terrain_component(Unreal,Actor(component)) is component
assert component.profile=="BlockAll"
try:require_walkable_terrain_component(Unreal,Actor(None))
except RuntimeError as exc:assert "no static mesh" in str(exc)
else:raise AssertionError("Missing ground component accepted")
print("PASS collision preflight: asset allowlist, safe idempotency, no body, blocking ground")
