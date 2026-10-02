"""Pure offline numerical and protocol regression/negative tests; no native app."""
import json,math,sys,unittest,tempfile,hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
sys.dont_write_bytecode=True
import solve_support62 as s

def row():return {'original_world_transform_columns':[1,0,0,0,1,0,0,0,1,0,0,0],'class':'pine'}
def terrain():return s.Terrain([[[-5,0,-5],[5,0,-5],[5,0,5]],[[-5,0,-5],[5,0,5],[-5,0,5]]],[['test',0],['test',1]])
class Tests(unittest.TestCase):
 def test_native_asset_hashes(self):
  m,p=s.models(s.read(s.E/'native-proxy-meshes.json'));self.assertEqual(len(m),5);self.assertEqual(len(p),5);self.assertEqual(m['rock']['proxy_get_faces_sha256'],'20738d402431be5922fc6659aa80de1a7907abd3438c62ac989cca7b2e278267')
 def test_reject_changed_frozen_source_pin(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'input';p.write_bytes(b'original');pin={'bytes':8,'sha256':hashlib.sha256(b'original').hexdigest()};s.check_pin(p,pin);p.write_bytes(b'altered!')
   with self.assertRaises(ValueError):s.check_pin(p,pin)
 def test_consumed_sources_match_frozen_plan(self):
  plan=s.read(s.PREP/'candidate-plan.json')
  for p in [s.SURVEY,s.E/'native-proxy-meshes.json',s.E/'wrapper-report.json']:s.check_pin(p,plan['source_pins'][str(p.relative_to(s.R))])
 def test_capsule_flat_natural_curvature(self):
  out=s.capsule(row(),terrain());self.assertAlmostEqual(out['max_d'],0,12);self.assertFalse(out['whole_capsule_projection_seated']);self.assertAlmostEqual(out['enclosing_rectangle_area_m2'],out['enclosing_rectangle_terrain_covered_area_m2'],7)
 def test_capsule_slope_exact_tangent(self):
  t=np.array(terrain().tri);t[:,:,1]=.8*t[:,:,0]-.6*t[:,:,2];out=s.capsule(row(),s.Terrain(t,terrain().labels));r=float(np.float32(2.4));self.assertAlmostEqual(out['max_d'],r*(math.sqrt(2)-1),11)
 def test_capsule_affine_is_not_orthogonalized(self):
  r=row();r['original_world_transform_columns']=[2,0,.3,0,.7,0,.4,0,1.1,0,0,0];t=terrain();out=s.capsule(r,t);self.assertAlmostEqual(out['max_d'],0,12)
 def test_capsule_reject_tilt(self):
  r=row();r['original_world_transform_columns'][1]=.01
  with self.assertRaises(ValueError):s.capsule(r,terrain())
 def test_capsule_reject_singular(self):
  r=row();r['original_world_transform_columns'][0]=0
  with self.assertRaises(ValueError):s.capsule(r,terrain())
 def test_capsule_reject_hole(self):
  t=terrain()
  with self.assertRaises(ValueError):s.capsule(row(),s.Terrain(t.tri[:1],t.labels[:1]))
 def test_capsule_triangle_disjoint(self):self.assertIsNone(s.cap_triangle_max(np.array([[3,3],[4,3],[3,4.]]),np.array([1.,0]),0.,1.,1.))
 def test_capsule_clipped_extrema_independent_optimizer(self):
  rng=np.random.default_rng(6201)
  for i in range(30):
   tri=np.array([[-2.,-.8],[1.8,-.8],[.1,2.]]);tri+=rng.uniform(-.5,.5,(1,2));q=rng.uniform(-4,4,2);sy=rng.uniform(.4,2);hit=s.cap_triangle_max(tri,q,1.2,sy,1.3);self.assertIsNotNone(hit);value,u=hit
   # Independent smooth 3D convex ball formulation avoids a sqrt singularity
   # at the disk edge; the earlier 2D SLSQP fixture failure is retained.
   fun=lambda p:-(float(q@p[:2])+1.2-sy*1.3+sy*p[2])
   cons=[{'type':'ineq','fun':lambda p:1.3**2-p@p},{'type':'ineq','fun':lambda p:p[2]}]
   for a,b in zip(tri,np.roll(tri,-1,axis=0)):cons.append({'type':'ineq','fun':lambda p,a=a,b=b:s.cross2(b-a,p[:2]-a)})
   opt=minimize(fun,[0.,0.,.5],method='SLSQP',constraints=cons,options={'ftol':1e-12,'maxiter':500})
   self.assertTrue(opt.success or abs(opt.fun+value)<1e-8);self.assertAlmostEqual(-opt.fun,value,7)

 def test_foot_plane_extrema(self):
  t=terrain();v=np.array(t.tri);v[:,:,1]=v[:,:,0]*.4;poly=np.array([[-1,0,-1],[1,0,-1],[1,0,1],[-1,0,1.]])
  result=s.feet(row(),[poly],s.Terrain(v,t.labels));self.assertAlmostEqual(result['min_d'],-.4);self.assertAlmostEqual(result['max_d'],.4)
 def test_foot_hole_rejected(self):
  poly=np.array([[-1,0,-1],[1,0,-1],[1,0,1],[-1,0,1.]])
  with self.assertRaises(ValueError):s.feet(row(),[poly],s.Terrain(terrain().tri[:1],[['test',0]]))
 def test_no_five_ray_shortcut(self):
  # A terrain apex away from root/corner rays is found by polygon clipping.
  p=[[-1,0,-1],[1,0,-1],[1,0,1],[-1,0,1],[.2,2,.3]];t=s.Terrain([[p[i],p[(i+1)%4],p[4]]for i in range(4)],[['spike',i]for i in range(4)]);poly=np.array(p[:4],float);out=s.feet(row(),[poly],t);self.assertEqual(out['max_d'],2.);self.assertGreater(out['max_d'],t.height(0,0))
 def test_interval_empty_is_not_relaxed(self):
  m={'first_layer':1.,'height':5.,'max_y':4.};out=s.interval(row(),m,{'min_d':0.,'max_d':2.},0.);self.assertTrue(out['empty']);self.assertEqual(out['air_gap_gate_m'],.001)
 def test_interval_boundary_inclusive(self):
  m={'first_layer':1.,'height':5.,'max_y':4.};out=s.interval(row(),m,{'min_d':0.,'max_d':.501},0.);self.assertLessEqual(abs(out['lower_y_translation_m']-out['upper_y_translation_m']),1e-15)
 def test_affine_columns_full(self):
  r=row();r['original_world_transform_columns']=[1,2,3,4,5,6,7,8,10,11,12,13];np.testing.assert_equal(s.affine(r,[[2,3,4]]),[[53,63,77]])
 def test_source_visual_collision_difference_not_suppressed(self):
  a,b,c,records=s.terrains();self.assertEqual(len(records),6);self.assertTrue(all(not r['source_visual_collision_bit_identical']for r in records));self.assertTrue(np.any(a.tri!=c.tri));self.assertEqual(sum(b.changed),2479)
 def test_frozen_keep_inventory(self):
  r=s.read(s.D/'support-results.json');self.assertEqual(len(r['rows']),167);self.assertEqual(len(r['exact_keep_509']),509);self.assertEqual(sum(bool(q['protected_neighbor'])for q in r['exact_keep_509']),2);self.assertTrue(r['zero_deletions']);self.assertFalse(r['all_167_support_proved'])
 def test_all_candidates_obey_final_gates(self):
  for r in s.read(s.D/'support-results.json')['rows']:
   if r['status']=='conditional_source_y_candidate':
    dy=r['selected_dy_m'];self.assertLessEqual(r['interval']['lower_y_translation_m'],dy);self.assertLessEqual(dy,r['interval']['upper_y_translation_m']);self.assertTrue(r['visible_geometry']['passed']);self.assertFalse(r['placement_written']);self.assertFalse(r['native_collision_surface_proved'])
   elif r['status']=='preserve_exact_actual_foot_unchanged':self.assertEqual(r['selected_dy_m'],0.)
if __name__=='__main__':unittest.main(verbosity=2)
