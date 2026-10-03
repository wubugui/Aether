"""Bounded scope, absolute-control semantics and restoration tests. No visibility claim."""
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
 def setUpClass(cls):
  cls.c=g.read(g.CANDIDATE_PATH);cls.b=g.read(g.BINDING_PATH);cls.old=g.read(HERE.parent/'form-v3/candidate.json')
 def test_one_deterministic_candidate(self):
  c,b,r=prep.make();self.assertEqual(c,self.c);self.assertEqual(b,self.b);self.assertEqual(json.loads(json.dumps(r)),g.read(HERE/'FORM_CHANGE_REPORT.json'))
 def test_original_spatial_and_edit_gates_unchanged(self):
  def fn(path,name):
   text=path.read_text();return ast.get_source_segment(text,next(v for v in ast.parse(text).body if isinstance(v,ast.FunctionDef) and v.name==name))
  for name in ('spatial_gate','planar_certificate','evaluate','validate_evaluated','validate_native_raw'):
   self.assertEqual(fn(HERE/'geometry58l.py',name),fn(HERE.parent/'form-v3/geometry58l.py',name))
 def test_fixed_topology_other_controls_paths_and_nodes(self):
  for key in ('faces','planar_triangles','manual_edit_probe','external_rim_authority_float64_xz','section_paths'):self.assertEqual(self.c[key],self.old[key])
  self.assertEqual(self.c['controls'][2:],self.old['controls'][2:])
  for key in self.c['named_nodes']:
   if key not in ('A','B'):self.assertEqual(self.c['named_nodes'][key],self.old['named_nodes'][key])
  self.assertTrue(g.validate_form_scope(self.c,self.b))
 def test_AB_real_defaults_handles_ranges_and_exercise(self):
  for index,(name,default,minimum,maximum,exercise) in enumerate([('A',945,915,970,950),('B',975,945,985,980)]):
   row=self.c['controls'][index];i=self.c['named_nodes'][name]['vertex_index']
   self.assertEqual([row[k] for k in ('default','min','max','exercise_value')],[default,minimum,maximum,exercise]);self.assertEqual(row['position_world'],self.c['vertices_world'][i]);self.assertEqual(self.c['named_nodes'][name]['world_xyz'],row['position_world'])
   moved=g.evaluate(self.c,{row['id']:exercise});self.assertEqual(moved[i,1],exercise);self.assertGreater(np.count_nonzero(row['weights']),100)
   self.assertTrue(np.array_equal(g.evaluate(self.c),self.c['vertices_world']))
 def test_false_old_height_binding_rejected(self):
  c=copy.deepcopy(self.c);c['controls'][0]['default']=1005
  with self.assertRaisesRegex(ValueError,'AB_PARAMETER_SEMANTICS'):g.validate_form_scope(c,self.b)
 def test_defaults_manual_combined_restoration(self):
  c=self.c;base=[s.local(p) for p in c['vertices_world']];vals=[r['default'] for r in c['controls']];manual=copy.deepcopy(base);i=c['manual_edit_probe']['vertex_index'];manual[i][2]=s.f32(manual[i][2]+.125)
  authored,moved=s.edit(c,manual,base,base,vals);g.validate_evaluated(c,[s.world(p) for p in moved]);self.assertEqual(moved,manual)
  vv=vals[:];vv[0]=c['controls'][0]['exercise_value'];_,combined=s.edit(c,moved,authored,moved,vv);g.validate_evaluated(c,[s.world(p) for p in combined]);_,restored=s.edit(c,combined,authored,combined,vals);self.assertEqual(restored,manual)
  reset,points=s.edit(c,base,authored,restored,vals);self.assertEqual(reset,base);self.assertEqual(points,base)
 def test_first_real_failure_kept_and_minimally_fixed(self):
  bad=g.read(HERE/'preparation-history/attempt01/GEOMETRY_RESULT.json');self.assertFalse(bad['passed']);self.assertIn('FORM_V4_VALLEY_FLOOR_FIXED',bad['error']);self.assertTrue(g.read(HERE/'GEOMETRY_RESULT.json')['passed'])
  badc=g.read(HERE/'preparation-history/attempt01/candidate.json');d=np.asarray(self.c['vertices_world'])-np.asarray(badc['vertices_world']);self.assertEqual(np.flatnonzero(np.any(d!=0,axis=1)).tolist(),[885,977]);self.assertEqual(d[977].tolist(),[0,.29931640625,0])
 def test_scope_drift_and_true_rim_refused(self):
  scope=self.b['form_v4'];c=copy.deepcopy(self.c);outside=next(i for i in range(self.c['rim_count'],self.c['planar_vertex_count']) if all((np.linalg.norm((np.asarray(c['vertices_world'][i])[[0,2]]-rg['center'])/rg['radii'])>rg['support_scale']) if rg['shape']=='ellipse' else not(rg['bounds'][0]<=c['vertices_world'][i][0]<=rg['bounds'][1] and rg['bounds'][2]<=c['vertices_world'][i][2]<=rg['bounds'][3]) for rg in scope['regions_world_xz']));c['vertices_world'][outside][1]+=.125
  with self.assertRaisesRegex(ValueError,'OUTSIDE_XYZ_FIXED'):g.validate_form_scope(c,self.b)
  c=copy.deepcopy(self.c);c['vertices_world'][15][0]+=.125
  with self.assertRaisesRegex(ValueError,'TRUE_RIM_XYZ_FIXED'):g.validate_form_scope(c,self.b)
 def test_local_internal_near_rim_XZ_released_only(self):
  v=np.asarray(self.c['vertices_world']);o=np.asarray(self.old['vertices_world']);d=g.rim_distance(o[:self.c['planar_vertex_count']][:,[0,2]],np.asarray(self.c['external_rim_authority_float64_xz']));changed=np.any(v[:len(d)][:,[0,2]]!=o[:len(d)][:,[0,2]],axis=1);self.assertTrue(np.any(changed&(d<90)&(d>0)));self.assertTrue(np.array_equal(v[:203],o[:203]));self.assertFalse(self.c['form_v4']['old_two_rectangle_patch_identity'])
 def test_original_rejection_and_prescribed_states(self):
  for row in self.c['controls']:self.assertTrue(np.any(g.evaluate(self.c,{row['id']:row['exercise_value']})!=self.c['vertices_world']))
  self.assertTrue(np.any(g.evaluate(self.c,{'C05_Main_Valley.width_multiplier':1.05})!=self.c['vertices_world']))
  for value in [{'C01_Crown_A':1005},{'C05_Main_Valley.width_multiplier':1.11},{'C06_Belly':560}]:
   with self.assertRaises(ValueError):g.evaluate(self.c,value)
 def test_original_cameras_material_lighting(self):
  oldb=g.read(HERE.parent/'form-v3/bindings.json')
  for key in ('author_frame','material','source_inspection_lighting','world_cameras'):self.assertEqual(self.b[key],oldb[key])
 def test_embedded_geometry_self_contained_and_unaccepted(self):
  text=s.expected_texts(HERE,self.c,self.b);ns={'__name__':'embedded','__file__':'/isolated/source-assets/cloud-bank58/revision-l/form-v4/geometry58l.py'};exec(compile(text['GEOMETRY58L.py'],'GEOMETRY58L.py','exec'),ns);self.assertEqual(ns['VERSION'],self.c['version']);self.assertTrue(ns['validate_form_scope'](self.c,self.b));self.assertFalse(g.read(HERE/'FORM_CHANGE_REPORT.json')['visual_acceptance'])
if __name__=='__main__':unittest.main(verbosity=2)
