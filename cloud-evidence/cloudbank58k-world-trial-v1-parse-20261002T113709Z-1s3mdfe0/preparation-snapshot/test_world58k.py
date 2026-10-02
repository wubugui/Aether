import ast
import copy
import json
import os
from pathlib import Path
import subprocess
import struct
import sys
import unittest
import numpy as np
sys.dont_write_bytecode = True
import provenance58k as p
import run_world58k as runner


class WorldTrialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads((p.HERE/'placement-provenance.json').read_text())

    def test_exact_current_branch_and_one_unit(self):
        d = self.plan
        self.assertTrue(d['historical_52f_is_not_current_61'])
        self.assertEqual(d['selected_root'],'CloudSea_1_1')
        self.assertEqual(len(d['current_clouds']),4)
        r = d['current_clouds']['CloudSea_1_1']
        self.assertEqual(r['path'],'SkyRegion39/CloudSea_1_1/cloud_sea_46_0_continuous_crown')
        self.assertEqual((r['vertex_count'],r['index_count']),(14374,15492))
        self.assertEqual(p.sha(p.SCENE),d['current_cloud_source_sha256'])

    def test_offline_provenance_reproducible(self):
        self.assertEqual(p.analyze(),self.plan)

    def test_double_transform_negative_controls(self):
        raw = json.loads((p.NATIVE/'native-reload.json').read_text())
        vertices = np.array(raw['geometry']['positions'],float)
        correct = vertices+p.ANCHOR
        r = np.array(self.plan['current_clouds']['CloudSea_1_1']['root_transform'])
        basis = r[:9].reshape(3,3).T
        wrong_root = correct@basis.T+r[9:]
        wrong_twice = correct+p.ANCHOR
        wrong_recenter = correct-(vertices.min(0)+vertices.max(0))/2
        for wrong in [wrong_root,wrong_twice,wrong_recenter]:
            self.assertGreater(float(np.max(np.abs(wrong-correct))),100)
        self.assertTrue(np.array_equal(correct.min(0),self.plan['k_world_bounds'][0]))

    def test_extent_mismatch_is_explicit(self):
        risk = self.plan['coverage_mismatch']
        self.assertLess(risk['k_to_old_xz_aabb_area_ratio'],0.075)
        self.assertFalse(risk['suitability_proven'])
        self.assertTrue(self.plan['current_clouds']['CloudSea_1_1']['k_aabb_contained'])
        self.assertTrue(all(x['aabb_gap_m']==0 for x in self.plan['current_clouds'].values()))

    def test_ray_actual_triangle_hit_and_miss(self):
        tri = np.array([[[-1,-1,5],[1,-1,5],[0,1,5]]],float)
        self.assertEqual(p.ray_hits(np.array([0.,0,0]),np.array([0.,0,10]),tri),5)
        self.assertIsNone(p.ray_hits(np.array([0.,0,0]),np.array([0.,0,4]),tri))
        self.assertIsNone(p.ray_hits(np.array([2.,0,0]),np.array([2.,0,10]),tri))
        self.assertEqual(p.ray_hits(np.array([0.,0,0]),np.array([0.,0,10]),tri[:,::-1]),5)

    def test_visibility_scope_not_a_pixel_pass(self):
        d = self.plan['original_front_projected_k']
        self.assertEqual(len(d['samples']),384)
        self.assertEqual(d['self_clear_centroid_samples'],178)
        self.assertEqual(d['clear_centroid_samples_after_single_replacement'],83)
        self.assertFalse(d['pixel_coverage_proven'])
        self.assertTrue(d['all_vertices_in_front'])

    def test_native_identity_and_material_retained(self):
        s = (p.HERE/'trial58k.gd').read_text()
        self.assertIn(runner.NATIVE_SHA,s)
        for token in ['shell.material_override == null','Transform3D(Basis.IDENTITY, ANCHOR)',
                      '6d3e3be9014ae790556976d1e40cf60ee460e9aa869efca6b9abce397f9b8262',
                      'ea7db52bc6c7f11cafcbaeb3043feac4593f2eed131d0a0ce9fe11e59fd46a2d']:
            self.assertIn(token,s)
        self.assertNotIn('material_override =',s.replace('material_override ==',''))
        self.assertNotIn('surface_set_material',s)
        self.assertNotIn('ResourceSaver',s)

    def test_opt_in_template_is_not_game62(self):
        text = (p.HERE/'CloudKTrial.tscn.template').read_text()
        self.assertEqual(text.count('[node '),2)
        self.assertIn('enabled = false',text)
        self.assertIn('res://scenes/candidate61-coast/Game61Coast.tscn',text)
        self.assertNotIn('Game62',text)
        self.assertEqual(text.count('script ='),1)

    def test_explicit_resource_and_time_budgets(self):
        self.assertEqual(runner.LIMITS['maximum_aggregate_rss_kib'],3145728)
        self.assertEqual(runner.LIMITS['renderer_child_seconds'],240)
        self.assertEqual(runner.LIMITS['wrapper_seconds'],300)
        self.assertEqual(runner.LIMITS['parse_child_seconds'],30)
        old = (p.HERE.parent/'import-v1/bounded_support58k.py').read_text()
        new = (p.HERE/'world_support58k.py').read_text()
        self.assertEqual(new.replace('MAX_RSS_KIB = 3145728','MAX_RSS_KIB = 1572864'),old)
        for path in p.HERE.glob('*.py'): ast.parse(path.read_text())

    def test_one_copy_and_no_engine_default(self):
        text = (p.HERE/'run_world58k.py').read_text()
        self.assertEqual(text.count('shutil.copytree(p.PROJECT,scratch'),1)
        self.assertIn('Same unchanged work copy; no recopy/fallback',text)
        before = sorted(x.name for x in p.HERE.iterdir())
        env = os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'
        r = subprocess.run([sys.executable,str(p.HERE/'run_world58k.py')],env=env,capture_output=True,text=True,timeout=10)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('no engine',r.stdout)
        self.assertEqual(before,sorted(x.name for x in p.HERE.iterdir()))

    def test_capture_plan_and_truthful_dimensions(self):
        s = (p.HERE/'observe58k.gd').read_text()
        self.assertEqual(s.count('await capture('),4)
        for token in ['actual_window_size','actual_texture_size','actual_visible_rect_size',
                      'actual_content_scale_size','actual_final_transform','camera_projection',
                      'world_k_projected_vertices','pixel_visibility_passed',
                      'game.observe_reference("1216")','root.size = Vector2i(1180,664)']:
            self.assertIn(token,s)
        self.assertNotIn('mesh.get_faces(',s)
        self.assertNotIn('ResourceSaver',s)

    def test_png_image_contract_independent_of_texture_metadata(self):
        # Synthetic in-memory header only. No PNG/artifact is produced.
        prefix = b'\x89PNG\r\n\x1a\n' + struct.pack('>I',13) + b'IHDR'
        header = prefix + struct.pack('>II',1179,664) + b'\x08\x06\x00\x00\x00' + b'\x00'*4
        self.assertEqual(runner.png_dimensions(header),[1179,664])
        self.assertNotEqual(runner.png_dimensions(header),[831,468])
        for bad in [header[:20],b'X'+header[1:],header[:12]+b'IDAT'+header[16:]]:
            with self.assertRaises(ValueError): runner.png_dimensions(bad)
        source = (p.HERE/'run_world58k.py').read_text()
        self.assertIn("item['resolution'] == [1179,664]",source)
        self.assertNotIn("item['resolution'] == item['actual_texture_size']",source)


if __name__ == '__main__':
    unittest.main(verbosity=2)
