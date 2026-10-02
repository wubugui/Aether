"""Pure actual-candidate gates and negative controls; never native validation."""
import sys,os,unittest,copy
os.environ['OPENBLAS_NUM_THREADS']='1';sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry58l as g
import numpy as np
class GeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.c=g.read(g.CANDIDATE_PATH)
    def rejected(self,fn,text):
        with self.assertRaisesRegex(ValueError,text):fn()
    def test_actual_candidate_closed_oriented_genus_zero(self):
        r=g.validate_candidate(self.c);self.assertTrue(r['topology']['all_vertex_links_one_cycle']);self.assertEqual(r['topology']['euler'],2)
    def test_seven_real_controls(self):
        for row in self.c['controls']:
            v=g.evaluate(self.c,{row['id']:row['exercise_value']});self.assertTrue(np.any(v!=self.c['vertices_world']))
    def test_width_real_response(self):self.assertTrue(np.any(g.evaluate(self.c,{'C05_Main_Valley.width_multiplier':1.05})!=self.c['vertices_world']))
    def test_defaults_identity(self):self.assertTrue(np.array_equal(g.evaluate(self.c),self.c['vertices_world']))
    def test_secondary_out_of_range(self):self.rejected(lambda:g.evaluate(self.c,{'C05_Main_Valley.width_multiplier':1.11}),'CONTROL_RANGE')
    def test_primary_out_of_range(self):self.rejected(lambda:g.evaluate(self.c,{'C01_Crown_A':1050}),'CONTROL_RANGE')
    def test_valid_parameter_but_invalid_geometry_rejected(self):self.rejected(lambda:g.evaluate(self.c,{'C06_Belly':560}),'CORE_VOLUME')
    def test_manual_height_edit(self):
        v=np.array(self.c['vertices_world']);r=self.c['manual_edit_probe'];v[r['vertex_index'],1]+=.125;self.assertTrue(g.validate_evaluated(self.c,g.native_world(v))['passed'])
    def test_manual_xz_change_rejected(self):
        v=np.array(self.c['vertices_world']);v[self.c['rim_count']+20,0]+=1;self.rejected(lambda:g.validate_evaluated(self.c,v),'XZ_LAYOUT')
    def test_topology_damage(self):
        c=copy.deepcopy(self.c);c['faces'].pop();self.rejected(lambda:g.validate_candidate(c),'TWO_SHEET_LAYOUT')
    def test_reverse_winding(self):
        c=copy.deepcopy(self.c);c['faces'][0]=c['faces'][0][::-1];self.rejected(lambda:g.validate_candidate(c),'SHELL_FACES')
    def test_rim_drift(self):
        c=copy.deepcopy(self.c);c['vertices_world'][0][0]+=1;self.rejected(lambda:g.validate_candidate(c),'FROZEN_RIM')
    def test_pchip_node_drift(self):
        c=copy.deepcopy(self.c);i=g.read(g.BINDING_PATH)['baseline_authority'][0]['vertex_index'];c['vertices_world'][i][1]+=1;self.rejected(lambda:g.validate_candidate(c),'V2_BASELINE')
    def test_world_claim_rejected(self):
        c=copy.deepcopy(self.c);c['world_acceptance']=True;self.rejected(lambda:g.validate_candidate(c),'FALSE_WORLD')
    def test_anchor_drift(self):
        c=copy.deepcopy(self.c);c['anchor_world'][0]+=1;self.rejected(lambda:g.validate_candidate(c),'FRAME')
    def test_nonpositive_thickness(self):
        c=copy.deepcopy(self.c);i=c['rim_count']+1;c['vertices_world'][i][1]=c['vertices_world'][c['planar_vertex_count']+1][1];self.rejected(lambda:g.spatial_gate(c),'POSITIVE_INTERIOR')
    def test_mismatched_two_sheet_projection(self):
        c=copy.deepcopy(self.c);c['vertices_world'][-1][0]+=1;self.rejected(lambda:g.spatial_gate(c),'TWO_SHEET_XZ')
    def test_actual_crossing_edges_rejected(self):
        self.rejected(lambda:g.planar_certificate(np.array([[0.,0],[1,1],[0,1],[1,0]]),np.array([[0,1,2],[0,2,3]]),4),'PLANAR_INVERTED')
    def test_zero_area_triangle_rejected(self):self.rejected(lambda:g.planar_certificate(np.array([[0.,0],[1,0],[2,0]]),np.array([[0,1,2]]),3),'PLANAR_INVERTED')
    def test_old_nonmanifold_candidate_still_rejected(self):
        c=g.read(g.HERE/'candidate-attempt03.json');c['external_rim_authority_float64_xz']=g.read(g.BINDING_PATH)['external_rim_authority_float64_xz'];self.rejected(lambda:g.spatial_gate(c),'Nonmanifold')
    def test_profile_approximation_is_not_claimed_exact(self):
        r=g.read(g.HERE/'profile-approximation.json');self.assertFalse(r['pointwise_PCHIP_identity']);self.assertFalse(r['approximation_accepted']);self.assertTrue(all(s['knots_y_preserved_exactly'] for s in r['sections']));self.assertTrue(all(s['max_top_error_m']>0 for s in r['sections']))
if __name__=='__main__':unittest.main(verbosity=2)
