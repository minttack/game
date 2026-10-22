"""Mock Unreal Editor test: no engine claims, verifies mutation/rollback decisions."""
import importlib
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

class Vector:
    def __init__(self,x,y,z):self.x,self.y,self.z=x,y,z

class Rotator:
    def __init__(self,*args):self.args=args

class MeshComponent:
    def __init__(self):self.mesh=None;self.material=None
    def set_static_mesh(self,asset):self.mesh=asset
    def set_material(self,index,asset):self.material=(index,asset)

class Actor:
    def __init__(self,location=None):
        self.location=location or Vector(0,0,0)
        self.label='OldActor';self.properties={};self.mesh_component=MeshComponent()
    def get_actor_label(self):return self.label
    def set_actor_label(self,s):self.label=s
    def get_actor_location(self):return self.location
    def set_editor_property(self,key,value):self.properties[key]=value
    def get_editor_property(self,key):
        if key=='static_mesh_component':return self.mesh_component
        return self.properties.get(key)
    def set_actor_scale3d(self,scale):self.scale=scale

class PlayerStart(Actor):pass
class StaticMeshActor(Actor):pass
class BiomeActor(Actor):pass

class ActorEditor:
    def __init__(self):self.actors=[PlayerStart(Vector(100,200,300))];self.spawned=[];self.destroyed=[];self.fail_at=-1
    def get_all_level_actors(self):return list(self.actors)
    def spawn_actor_from_class(self,kind,loc,rot):
        if len(self.spawned)==self.fail_at:return None
        actor=kind(loc)
        self.actors.append(actor);self.spawned.append(actor)
        return actor
    def destroy_actor(self,actor):
        self.actors.remove(actor);self.destroyed.append(actor)

class LevelEditor:
    def __init__(self):self.saves=0
    def get_current_level(self):return object()
    def save_current_level(self):self.saves+=1;return True

class VisualStageMockTests(unittest.TestCase):
    def setUp(self):
        self.editor=ActorEditor();self.level=LevelEditor()
        fake=types.ModuleType('unreal')
        fake.EditorActorSubsystem=ActorEditor
        fake.LevelEditorSubsystem=LevelEditor
        fake.PlayerStart=PlayerStart
        fake.StaticMeshActor=StaticMeshActor
        fake.Vector=Vector
        fake.Rotator=Rotator
        fake.get_editor_subsystem=lambda kind: self.editor if kind==ActorEditor else self.level
        fake.load_asset=lambda path: path
        fake.load_class=lambda *_:BiomeActor
        fake.log=lambda *_:None
        fake.log_warning=lambda *_:None
        self.module_mock=patch.dict(sys.modules,{'unreal':fake})
        self.module_mock.start()
        self.env=patch.dict(os.environ,{'IRL_PBR_SOURCE_DIR':str(HERE/'Generated')},clear=False)
        self.env.start()
        sys.modules.pop('assemble_irl_stage',None)

    def tearDown(self):
        sys.modules.pop('assemble_irl_stage',None)
        self.env.stop();self.module_mock.stop()

    def load(self,apply=False,save=False):
        with patch.dict(os.environ,{'IRL_STAGE_APPLY':'1' if apply else '0',
                                    'IRL_STAGE_SAVE':'1' if save else '0'}):
            sys.modules.pop('assemble_irl_stage',None)
            return importlib.import_module('assemble_irl_stage')

    def test_default_dry_run_does_not_mutate(self):
        result=self.load().setup()
        self.assertEqual(result['status'],'dry_run')
        self.assertEqual(len(self.editor.actors),1)
        self.assertEqual(self.level.saves,0)

    def test_applied_placements_retain_original_and_are_idempotent(self):
        first=self.editor.actors[0]
        script=self.load(apply=True)
        self.assertEqual(script.setup()['status'],'placed_unsaved')
        self.assertEqual(len(self.editor.actors),11)
        self.assertIs(first,self.editor.actors[0]);self.assertEqual(first.get_actor_label(),'OldActor')
        self.assertEqual(script.setup()['status'],'already_present')
        self.assertEqual(len(self.editor.actors),11)
        self.assertEqual(self.level.saves,0)
        new_biome=[a for a in self.editor.actors if isinstance(a,BiomeActor)]
        self.assertEqual(len(new_biome),1)
        self.assertTrue(new_biome[0].get_editor_property('ground_cover_mesh').endswith('SM_IRL_GrassClump'))

    def test_partial_failure_rolls_back_new_actors_only(self):
        script=self.load(apply=True)
        self.editor.fail_at=4
        with self.assertRaisesRegex(RuntimeError,'Failed to spawn'):
            script.setup()
        self.assertEqual(len(self.editor.actors),1)
        self.assertEqual(len(self.editor.destroyed),4)
        self.assertEqual(self.level.saves,0)

    def test_saved_only_with_both_flags(self):
        with self.assertRaisesRegex(RuntimeError,'requires'):
            self.load(save=True).setup()
        self.assertEqual(self.level.saves,0)
        self.assertEqual(self.load(apply=True,save=True).setup()['status'],'placed')
        self.assertEqual(self.level.saves,1)

if __name__=='__main__':unittest.main(verbosity=2)
