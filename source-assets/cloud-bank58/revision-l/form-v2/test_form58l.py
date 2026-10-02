"""Bounded actual form candidate checks, not native or visual acceptance."""
import os,sys,unittest,copy,ast,json
os.environ['OPENBLAS_NUM_THREADS']='1';sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry58l as g,prepare_form58l as prep,native_support58l as s
import numpy as np
HERE=Path(__file__).resolve().parent
class FormTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.c=g.read(g.CANDIDATE_PATH);cls.b=g.read(g.BINDING_PATH);cls.old=g.read(HERE.parent/'source-v1/candidate.json')
 def test_original_complete_geometry_gate(self):
  v=g.validate_candidate(self.c);self.assertTrue(v['non_self_intersection']);self.assertEqual(v['topology']['euler'],2);self.assertEqual(v['topology']['components'],1)
 def test_deterministic_single_candidate(self):
  c,b=prep.make();self.assertEqual(c,self.c);self.assertEqual(b,self.b)
 def test_fixed_all_xz_rim_bottom_topology_controls(self):
  n=self.c['planar_vertex_count'];r=self.c['rim_count'];a=np.array(self.c['vertices_world']);b=np.array(self.old['vertices_world']);self.assertTrue(np.array_equal(a[:,[0,2]],b[:,[0,2]]));self.assertTrue(np.array_equal(a[:r],b[:r]));self.assertTrue(np.array_equal(a[n:],b[n:]));self.assertEqual(self.c['faces'],self.old['faces']);self.assertEqual(self.c['controls'],self.old['controls'])
 def test_old_volume_gate_source_unchanged(self):
  def fn(path,name):
   s=path.read_text();return ast.get_source_segment(s,next(v for v in ast.parse(s).body if isinstance(v,ast.FunctionDef) and v.name==name))
  for name in ('spatial_gate','planar_certificate','evaluate','validate_evaluated','validate_native_raw'):
   self.assertEqual(fn(HERE/'geometry58l.py',name),fn(HERE.parent/'source-v1/geometry58l.py',name))
 def test_all_prescribed_primary_and_width_states(self):
  for row in self.c['controls']:
   self.assertTrue(np.any(g.evaluate(self.c,{row['id']:row['exercise_value']})!=self.c['vertices_world']))
  self.assertTrue(np.any(g.evaluate(self.c,{'C05_Main_Valley.width_multiplier':1.05})!=self.c['vertices_world']))
 def test_defaults_and_manual_combined_restoration(self):
  c=self.c;base=[s.local(p) for p in c['vertices_world']];vals=[r['default'] for r in c['controls']];probe=c['manual_edit_probe'];manual=copy.deepcopy(base);i=probe['vertex_index'];manual[i][2]=s.f32(manual[i][2]+.125)
  authored,moved=s.edit(c,manual,base,base,vals);g.validate_evaluated(c,[s.world(p) for p in moved]);self.assertEqual(moved,manual)
  vv=vals[:];vv[0]=c['controls'][0]['exercise_value'];_,combined=s.edit(c,moved,authored,moved,vv);g.validate_evaluated(c,[s.world(p) for p in combined]);_,restored=s.edit(c,combined,authored,combined,vals);self.assertEqual(restored,manual)
  reset,resetpoints=s.edit(c,base,authored,restored,vals);self.assertEqual(reset,base);self.assertEqual(resetpoints,base)
 def test_range_and_invalid_geometry_still_rejected(self):
  for values in [{'C01_Crown_A':1050},{'C05_Main_Valley.width_multiplier':1.11},{'C06_Belly':560}]:
   with self.assertRaises(ValueError):g.evaluate(self.c,values)
 def test_bound_displacement_rejects_excess(self):
  c=copy.deepcopy(self.c);c['vertices_world'][500][1]+=300
  with self.assertRaisesRegex(ValueError,'DISPLACEMENT'):g.validate_form_scope(c,self.b)
 def test_frozen_belly_and_floor_reject_change(self):
  for i in [self.c['planar_vertex_count']+50,self.b['form_v2']['preserved_valley_vertices'][-1]]:
   c=copy.deepcopy(self.c);c['vertices_world'][i][1]+=.125
   with self.assertRaises(ValueError):g.validate_form_scope(c,self.b)
 def test_honest_profile_semantic_delta(self):
  self.assertFalse(self.c['form_v2']['old_top_PCHIP_identity']);self.assertTrue(self.c['form_v2']['old_bottom_PCHIP_identity']);rows=self.b['baseline_authority'];self.assertTrue(any(r['top_world']!=r['historical_v2_top_world'] for r in rows))
  for a,b in zip(rows,g.read(HERE.parent/'source-v1/bindings.json')['baseline_authority']):self.assertEqual(a['bottom_world'],b['bottom_world'])
 def test_original_cameras_material_lighting(self):
  b=g.read(HERE.parent/'source-v1/bindings.json')
  for key in ('author_frame','material','source_inspection_lighting','world_cameras'):self.assertEqual(self.b[key],b[key])
 def test_complete_embedded_form_geometry_standalone(self):
  c=self.c;b=self.b;text=s.expected_texts(HERE,c,b);ns={'__name__':'embedded','__file__':'/isolated/source-assets/cloud-bank58/revision-l/form-v2/geometry58l.py'};exec(compile(text['GEOMETRY58L.py'],'GEOMETRY58L.py','exec'),ns);self.assertEqual(ns['VERSION'],c['version']);self.assertTrue(ns['validate_form_scope'](c,b))
if __name__=='__main__':unittest.main(verbosity=2)
