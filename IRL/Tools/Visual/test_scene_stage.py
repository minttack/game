"""Host tests for grounded scene planning and safe editor stage control."""
from pathlib import Path
import ast
import math
import unittest
import tempfile
from scene_stage_core import TerrainHeightfield, plan_stage, confirm_assets, classify_existing, TAG

HERE=Path(__file__).resolve().parent
TERRAIN=HERE/'Generated'/'SM_IRL_TerrainPatch.obj'
# CI can run without the generated artwork files. A synthetic 65x65 test
# grid exercises indexing; when original generated OBJ exists, test that too.
_TEST_DIRECTORY=None
if not TERRAIN.is_file():
    _TEST_DIRECTORY=tempfile.TemporaryDirectory()
    TERRAIN=Path(_TEST_DIRECTORY.name)/'SM_IRL_TerrainPatch.obj'
    with TERRAIN.open('w', encoding='utf-8') as f:
        f.write('# Host-only synthetic terrain fixture; NOT game art\n')
        for j in range(65):
            for i in range(65):
                x,y=-4000+125*i,-4000+125*j
                f.write(f'v {x:.3f} {y:.3f} {x*0.008+y*0.004:.3f}\n')

class StageTests(unittest.TestCase):
    def setUp(self):
        self.field=TerrainHeightfield(TERRAIN)

    def test_mesh_grid_valid(self):
        self.assertEqual(len(self.field.heights),4225)

    def test_height_at_grid_nodes(self):
        for i,j in [(0,0),(64,64),(17,23),(31,32),(32,32),(40,41)]:
            self.assertAlmostEqual(self.field.height(-4000+125*i,-4000+125*j),
                self.field.heights[j*65+i],places=5)

    def test_midpoint_interpolates(self):
        a,b,c,d=[self.field.height(*xy) for xy in [(-4000,-4000),(-3875,-4000),(-4000,-3875),(-3875,-3875)]]
        self.assertAlmostEqual(self.field.height(-3937.5,-3937.5),(a+b+c+d)/4,places=5)

    def test_off_terrain_and_nan_rejected(self):
        for xy in [(4001,0),(-5000,0),(math.nan,0),(0,math.inf)]:
            with self.assertRaises(ValueError): self.field.height(*xy)

    def test_plan_is_deterministic(self):
        p=plan_stage(TERRAIN,(14000,0,100),seed=42)
        self.assertEqual(p,plan_stage(TERRAIN,(14000,0,100),seed=42))
        self.assertNotEqual(p,plan_stage(TERRAIN,(14000,0,100),seed=43))

    def test_only_expected_bounded_objects(self):
        p=plan_stage(TERRAIN,(14000,0,100))
        self.assertEqual(len(p),10)
        self.assertEqual([i.role for i in p[:2]],['terrain','biome'])
        self.assertEqual(len(set(i.role for i in p)),len(p))
        for item in p[2:]:
            self.assertLess(math.hypot(item.x_cm-14000,item.y_cm),3200)
            self.assertGreater(item.scale,.60)
            self.assertLess(item.scale,1.41)
            x=item.x_cm-14000; y=item.y_cm
            self.assertAlmostEqual(item.z_cm,100+self.field.height(x,y)+65*item.scale-10,places=4)

    def test_bad_bounds_rejected(self):
        for count in (-1,21):
            with self.assertRaises(ValueError):plan_stage(TERRAIN,(0,0,0),rock_count=count)
        with self.assertRaises(ValueError):plan_stage(TERRAIN,(0,float('nan'),0))

    def test_assets_fail_closed(self):
        required={'SM_IRL_TerrainPatch','SM_IRL_GraniteBoulder','SM_IRL_GrassClump',
                  'M_IRL_ForestSoil','M_IRL_Granite','M_IRL_LeafGreen'}
        self.assertTrue(confirm_assets(required))
        with self.assertRaises(ValueError):confirm_assets(required-{'SM_IRL_TerrainPatch'})

    def test_duplicate_detection(self):
        self.assertTrue(classify_existing(['Level',TAG+'_rock_02']))
        self.assertFalse(classify_existing(['PlayerStart','IRL_Rock']))

    def test_unreal_tool_python_syntax_and_gates(self):
        script=(HERE/'assemble_irl_stage.py').read_text()
        ast.parse(script)
        self.assertIn("IRL_STAGE_APPLY",script)
        self.assertIn("IRL_STAGE_SAVE",script)
        self.assertIn("editor.destroy_actor(actor)",script)
        self.assertIn("not APPLY",script)

if __name__=='__main__':unittest.main(verbosity=2)
