"""Synthetic negative controls only. Does not generate candidate geometry."""
import copy,json,sys,unittest
from pathlib import Path
sys.dont_write_bytecode=True
import check_contract as m
HERE=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.c,cls.b,cls.e=[json.loads((HERE/p).read_text()) for p in ['contact-contract.json','external-rim.json','contact-evidence.json']]
    def reject(self,edit,code):
        c,b,e=map(copy.deepcopy,[self.c,self.b,self.e]);edit(c,b,e)
        with self.assertRaisesRegex(m.Rejected,code):m.validate(c,b,e)
    def test_valid_design_only(self):self.assertFalse(m.validate(self.c,self.b,self.e)['native_allowed'])
    def test_route_a(self):self.reject(lambda c,b,e:c.update(route='A'),'EXPLICIT_ROUTE_B')
    def test_old_lower_seam_reintroduced(self):self.reject(lambda c,b,e:c['released_identity'].update(old_lower_seam_locked=True),'OLD_SEAM_RELEASED')
    def test_outer_y_lock_reintroduced(self):self.reject(lambda c,b,e:c['external_lock'].update(source_y_locked=True),'NO_OLD_Y_LOCK')
    def test_positive_area_patch_lock(self):self.reject(lambda c,b,e:c['external_lock'].update(old_positive_area_surface_patches_locked=[530]),'NO_OLD_Y_LOCK')
    def test_internal_seam_not_rim(self):
        with self.assertRaisesRegex(m.Rejected,'INTERNAL_SEAM_IS_NOT_RIM'):m.classify_rim(0,'old-lower-seam')
    def test_80_inclusive(self):self.assertEqual(m.classify_rim(80,'external-rim.json'),'core')
    def test_internal_hole_not_rim(self):
        with self.assertRaisesRegex(m.Rejected,'INTERNAL_SEAM_IS_NOT_RIM'):m.classify_rim(0,'internal-hole')
    def test_thickness_lowered(self):self.reject(lambda c,b,e:c['unchanged_gates'].update(interior_min_vertical_thickness_m=119),'UNCHANGED_GATES')
    def test_belly_upper_raised(self):self.reject(lambda c,b,e:c['unchanged_gates'].update(interior_belly_y_m=[560,634]),'UNCHANGED_GATES')
    def test_seam_exception(self):self.reject(lambda c,b,e:c['unchanged_gates'].update(new_interior_seam_exception=True),'UNCHANGED_GATES')
    def test_profile_drift(self):self.reject(lambda c,b,e:c['v2_preservation'].update(A_belly_xyz_m=[4140,585,3910]),'V2_IDENTITY')
    def test_junction_drift(self):self.reject(lambda c,b,e:c['v2_preservation'].update(V2_xyz_m=[4480,750,4070]),'V2_IDENTITY')
    def test_boundary_coordinate_drift(self):self.reject(lambda c,b,e:b['source_segments'][0]['xz_endpoints_m'][0].__setitem__(0,0),'BOUNDARY_IDENTITY')
    def test_world_anchor_drift(self):self.reject(lambda c,b,e:c['frozen_world'].update(anchor_xyz_m=[0,0,0]),'WORLD_FRAME')
    def test_local_claims_global(self):self.reject(lambda c,b,e:c['contact_contract'].update(local_witnesses_are_global_proof=True),'SAMPLES_NOT_GLOBAL_PROOF')
    def test_stage_claim(self):self.reject(lambda c,b,e:c['stage'].update(contact_accepted=True),'STAGE_CLOSED')
    def test_zero_area_witness(self):self.reject(lambda c,b,e:e['finite_local_witnesses'][0].update(halfwidth_m=0),'LOCAL_OPEN_SQUARE')
    def test_cube_outside_validity_disk(self):self.reject(lambda c,b,e:e['finite_local_witnesses'][0].update(halfwidth_m=100),'LOCAL_OPEN_SQUARE')
    def test_projection_overlap_separated_solids(self):self.assertGreater(m.signed_gap([560,680],[[700,800]]),0)
    def test_envelope_does_not_fill_internal_gap(self):
        self.assertLess(m.signed_gap([600,700],[[500,900]]),0)
        self.assertGreater(m.signed_gap([600,700],[[500,550],[750,900]]),0)
    def test_tangent_is_not_positive_volume(self):self.assertEqual(m.signed_gap([560,680],[[680,800]]),0)
    def test_real_positive_interval_overlap(self):self.assertLess(m.signed_gap([625,745],[[632.9,725.6]]),0)
    def test_single_ray_cannot_admit(self):
        with self.assertRaisesRegex(m.Rejected,'DESIGN_ONLY'):m.candidate_acceptance({'one_ray_overlap':True})
    def test_forged_complete_cannot_admit(self):
        with self.assertRaisesRegex(m.Rejected,'DESIGN_ONLY'):m.candidate_acceptance({'passed':True,'native_allowed':True})
    def test_true_rim_conflict_not_ignored(self):self.reject(lambda c,b,e:e['profile_true_rim_checks'][0].update(violations=[{'belly':700}]),'PROFILE_TRUE_RIM_CONFLICT')
if __name__=='__main__':unittest.main(verbosity=2)
