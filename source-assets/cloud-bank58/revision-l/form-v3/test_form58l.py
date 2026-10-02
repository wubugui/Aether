"""Reuse original finite geometry/API checks for this one two-patch candidate."""
import os,sys,unittest,copy,ast,json
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry58l as g,prepare_form58l as prep,native_support58l as s
import numpy as np
HERE=Path(__file__).resolve().parent
class FormTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.c=g.read(g.CANDIDATE_PATH);cls.b=g.read(g.BINDING_PATH);cls.old=g.read(HERE.parent/'form-v2/candidate.json')
 def test_original_complete_geometry_gate(self):
  v=g.validate_candidate(self.c);self.assertTrue(v['non_self_intersection']);self.assertEqual(v['topology']['euler'],2);self.assertEqual(v['topology']['components'],1)
 def test_deterministic_single_candidate(self):
  c,b,r=prep.make();self.assertEqual(c,self.c);self.assertEqual(b,self.b);self.assertEqual(json.loads(json.dumps(r)),g.read(HERE/'FORM_CHANGE_REPORT.json'))
 def test_core_gate_source_unchanged(self):
  def fn(path,name):
   text=path.read_text();return ast.get_source_segment(text,next(v for v in ast.parse(text).body if isinstance(v,ast.FunctionDef) and v.name==name))
  for name in ('spatial_gate','planar_certificate','evaluate','validate_evaluated','validate_native_raw'):
   self.assertEqual(fn(HERE/'geometry58l.py',name),fn(HERE.parent/'form-v2/geometry58l.py',name))
 def test_topology_controls_nodes_unchanged(self):
  for k in ('faces','planar_triangles','controls','named_nodes','manual_edit_probe','external_rim_authority_float64_xz'):self.assertEqual(self.c[k],self.old[k])
 def test_pair_XZ_and_core_belly_y_unchanged(self):
  _,T,B=g.solid_arrays(self.c);_,oldT,oldB=g.solid_arrays(self.old);self.assertTrue(np.array_equal(T[:,[0,2]],B[:,[0,2]]));rim=np.asarray(self.c['external_rim_authority_float64_xz']);core=(g.rim_distance(T[:,[0,2]],rim)>=80)|(g.rim_distance(oldT[:,[0,2]],rim)>=80);self.assertTrue(np.array_equal(B[core,1],oldB[core,1]))
 def test_all_prescribed_primary_and_width_states(self):
  for row in self.c['controls']:self.assertTrue(np.any(g.evaluate(self.c,{row['id']:row['exercise_value']})!=self.c['vertices_world']))
  self.assertTrue(np.any(g.evaluate(self.c,{'C05_Main_Valley.width_multiplier':1.05})!=self.c['vertices_world']))
 def test_defaults_manual_combined_restoration(self):
  c=self.c;base=[s.local(p) for p in c['vertices_world']];vals=[r['default'] for r in c['controls']];manual=copy.deepcopy(base);i=c['manual_edit_probe']['vertex_index'];manual[i][2]=s.f32(manual[i][2]+.125)
  authored,moved=s.edit(c,manual,base,base,vals);g.validate_evaluated(c,[s.world(p) for p in moved]);self.assertEqual(moved,manual)
  vv=vals[:];vv[0]=c['controls'][0]['exercise_value'];_,combined=s.edit(c,moved,authored,moved,vv);g.validate_evaluated(c,[s.world(p) for p in combined]);_,restored=s.edit(c,combined,authored,combined,vals);self.assertEqual(restored,manual)
  reset,points=s.edit(c,base,authored,restored,vals);self.assertEqual(reset,base);self.assertEqual(points,base)
 def test_original_range_and_invalid_geometry_rejected(self):
  for values in [{'C01_Crown_A':1050},{'C05_Main_Valley.width_multiplier':1.11},{'C06_Belly':560}]:
   with self.assertRaises(ValueError):g.evaluate(self.c,values)
 def test_outside_scope_drift_refused(self):
  c=copy.deepcopy(self.c);c['vertices_world'][300][1]+=.125
  with self.assertRaisesRegex(ValueError,'OUTSIDE_XYZ_FIXED'):g.validate_form_scope(c,self.b)
 def test_true_rim_xz_drift_refused(self):
  c=copy.deepcopy(self.c);c['vertices_world'][15][0]+=.125
  with self.assertRaisesRegex(ValueError,'TRUE_RIM_XZ_FIXED'):g.validate_form_scope(c,self.b)
 def test_core_belly_drift_refused(self):
  c=copy.deepcopy(self.c);i=490+c['planar_vertex_count']-c['rim_count'];c['vertices_world'][i][1]+=.125
  with self.assertRaisesRegex(ValueError,'CORE_AND_OUTSIDE_BELLY_Y_FIXED'):g.validate_form_scope(c,self.b)
 def test_real_XZ_lateral_edit_and_local_Y_identity_release(self):
  delta=np.asarray(self.c['vertices_world'])-np.asarray(self.old['vertices_world']);self.assertGreater(np.linalg.norm(delta[:,[0,2]],axis=1).max(),10);self.assertFalse(self.c['form_v3']['old_internal_XZ_identity']);self.assertFalse(self.c['form_v3']['old_edge_belly_Y_identity'])
 def test_top_limit_failure_retained(self):
  failed=g.read(HERE/'preparation-history/attempt01/GEOMETRY_RESULT.json');self.assertFalse(failed['passed']);self.assertIn('FORM_V3_TOP_Y_MAX_120M',failed['error']);self.assertTrue(g.read(HERE/'GEOMETRY_RESULT.json')['passed'])
 def test_original_cameras_material_lighting(self):
  b=g.read(HERE.parent/'form-v2/bindings.json')
  for key in ('author_frame','material','source_inspection_lighting','world_cameras'):self.assertEqual(self.b[key],b[key])
 def test_complete_embedded_geometry_standalone(self):
  text=s.expected_texts(HERE,self.c,self.b);ns={'__name__':'embedded','__file__':'/isolated/source-assets/cloud-bank58/revision-l/form-v3/geometry58l.py'};exec(compile(text['GEOMETRY58L.py'],'GEOMETRY58L.py','exec'),ns);self.assertEqual(ns['VERSION'],self.c['version']);self.assertTrue(ns['validate_form_scope'](self.c,self.b))
 def test_projection_limits_not_disguised_as_acceptance(self):
  p=g.read(HERE/'PROJECTION_SAMPLES.json');self.assertFalse(p['visual_acceptance']);self.assertFalse(p['native_executed']);small=next(x for x in p['samples'] if x['name']=='small_return');self.assertFalse(small['new_projection']['visible_at_sample'])
if __name__=='__main__':unittest.main(verbosity=2)
