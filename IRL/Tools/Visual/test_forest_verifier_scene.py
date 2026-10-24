"""Offline Unreal forest scene verifier contract tests.

These are host stubs, not proof of a successful Unreal Engine editor run.
"""
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path

sys.modules.setdefault("unreal", types.SimpleNamespace())
script = Path(__file__).with_name("verify_irl_forest_visual_level.py")
spec = importlib.util.spec_from_file_location("irl_forest_scene_verifier", script)
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class Asset:
    def __init__(self, name):
        self.path = verifier._asset_object_path(name)

    def get_path_name(self):
        return self.path


class Component:
    def __init__(self, mesh, material):
        self.mesh = Asset(mesh) if mesh else None
        self.material = Asset(material) if material else None

    def get_static_mesh(self):
        return self.mesh

    def get_material(self, index):
        assert index == 0
        return self.material


class Actor:
    def __init__(self, label, mesh=None, material=None, count=None):
        self.label = label
        self.component = Component(mesh, material) if mesh else None
        self.count = count
        self.props = {
            name: Asset(asset_name)
            for name, asset_name in verifier.BIOME_ASSETS.items()
        } if count is not None else {}

    def get_editor_property(self, name):
        return self.props[name]

    def get_actor_label(self):
        return self.label

    def get_component_by_class(self, klass):
        return self.component

    def last_generated_instance_count(self):
        return self.count


class World:
    def __init__(self, path):
        self.path = path

    def get_path_name(self):
        return self.path


def make_scene():
    actors = [Actor("IRL_OriginalForestTerrain", "SM_IRL_TerrainPatch", "M_IRL_ForestSoil")]
    actors.extend(
        Actor(f"IRL_Granite_{i:02d}", "SM_IRL_GraniteBoulder", "M_IRL_Granite")
        for i in range(14)
    )
    actors.extend(Actor(f"IRL_Biome_{i:02d}", count=120) for i in range(4))
    return actors


class ForestSceneContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.actors = make_scene()
        self.world = World(
            "/Game/IRL/Maps/Lvl_IRL_Forest_VisualValidation."
            "Lvl_IRL_Forest_VisualValidation"
        )
        self.original_unreal = verifier.unreal
        self.editor_class = type("UnrealEditorSubsystem", (), {})
        self.actor_class = type("EditorActorSubsystem", (), {})
        self.component_class = type("StaticMeshComponent", (), {})
        editor = types.SimpleNamespace(get_editor_world=lambda: self.world)
        actors_api = types.SimpleNamespace(get_all_level_actors=lambda: self.actors)
        def get_subsystem(klass):
            if klass is self.editor_class:
                return editor
            if klass is self.actor_class:
                return actors_api
            raise AssertionError("Unexpected subsystem")
        verifier.unreal = types.SimpleNamespace(
            UnrealEditorSubsystem=self.editor_class,
            EditorActorSubsystem=self.actor_class,
            StaticMeshComponent=self.component_class,
            Paths=types.SimpleNamespace(project_saved_dir=lambda: self.temp.name),
            get_editor_subsystem=get_subsystem,
            log=lambda message: None,
        )

    def tearDown(self):
        verifier.unreal = self.original_unreal
        self.temp.cleanup()

    def report(self):
        return json.loads(
            (Path(self.temp.name) / "IRLVisualValidationReport.json").read_text()
        )

    def test_object_paths_include_unreal_package_and_object(self):
        self.assertEqual(
            verifier._asset_object_path("SM_IRL_TerrainPatch"),
            "/Game/IRL/Visual/ProceduralStarter/"
            "SM_IRL_TerrainPatch.SM_IRL_TerrainPatch",
        )

    def test_valid_forest_scene_passes(self):
        result = verifier.verify()
        self.assertTrue(Path(result).is_file())
        report = self.report()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["errors"], [])
        self.assertEqual(len(report["mesh_assets"]), 15)
        self.assertEqual(len(report["material_assets"]), 15)
        self.assertEqual(len(report["biome_instances"]), 4)
        self.assertEqual(len(report["biome_assets"]), 4)

    def test_missing_biome_fails(self):
        self.actors.pop()
        with self.assertRaisesRegex(RuntimeError, "IRL_Biome_03"):
            verifier.verify()
        self.assertEqual(self.report()["status"], "FAIL")

    def test_duplicate_rock_fails(self):
        self.actors.append(self.actors[1])
        with self.assertRaisesRegex(RuntimeError, "IRL_Granite_00"):
            verifier.verify()
        self.assertEqual(self.report()["status"], "FAIL")

    def test_wrong_mesh_fails(self):
        self.actors[0].component.mesh = Asset("SM_IRL_GrassClump")
        with self.assertRaisesRegex(RuntimeError, "expected mesh"):
            verifier.verify()
        self.assertEqual(self.report()["status"], "FAIL")

    def test_wrong_material_fails(self):
        self.actors[1].component.material = Asset("M_IRL_LeafGreen")
        with self.assertRaisesRegex(RuntimeError, "expected material"):
            verifier.verify()
        self.assertEqual(self.report()["status"], "FAIL")

    def test_wrong_biome_asset_fails(self):
        self.actors[-1].props["ground_cover_mesh"] = Asset("SM_IRL_GraniteBoulder")
        with self.assertRaisesRegex(RuntimeError, "ground_cover_mesh expected"):
            verifier.verify()
        self.assertEqual(self.report()["status"], "FAIL")

    def test_missing_biome_asset_fails(self):
        self.actors[-1].props["stone_material"] = None
        with self.assertRaisesRegex(RuntimeError, "stone_material expected"):
            verifier.verify()
        self.assertEqual(self.report()["status"], "FAIL")

    def test_empty_biome_instances_fail(self):
        self.actors[-1].count = 0
        with self.assertRaisesRegex(RuntimeError, "no decorative instances"):
            verifier.verify()
        self.assertEqual(self.report()["status"], "FAIL")

    def test_wrong_map_is_rejected(self):
        self.world.path = "/Game/ThirdPerson/Lvl_ThirdPerson.Lvl_ThirdPerson"
        with self.assertRaisesRegex(RuntimeError, "Wrong map loaded"):
            verifier.verify()

    def test_missing_world_is_rejected(self):
        self.world = None
        with self.assertRaisesRegex(RuntimeError, "No Unreal Editor world"):
            verifier.verify()


if __name__ == "__main__":
    unittest.main(verbosity=2)
