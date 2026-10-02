"""Pure synthetic contract negative controls; never native geometry evidence."""
import copy,json,tempfile,unittest
from pathlib import Path
import numpy as np
import contract58l as c


def fixture():
    # Tetrahedron fixture in SOURCE axes, then world mapped: not a bank candidate.
    v=np.array([[0,0,600],[10,0,600],[0,10,600],[0,0,610]],float)
    f=[[0,2,1],[0,1,3],[0,3,2],[1,2,3]]
    w=c.world_vertices(v)
    controls=[]
    for j,name in enumerate(c.CONTROL_IDS):
        d=np.zeros((4,3));d[1:,1]=.01*(j+1)
        controls.append(dict(id=name,position_world=[4140,1005,3910],semantic='Synthetic scalar test only',units='m',default=0,min=-1,max=1,weights=[0,1,1,1],displacements_world=d.tolist()))
    return dict(schema='cloudbank58l-offline-candidate-v1',implementation_ready=True,vertices_world=w.tolist(),faces=f,anchor_world=[3958,0,3667],scale=[1,1,1],locked_indices=[0],controls=controls,groups=[dict(name='OUTER_LOCK',indices=[0])])

class Tests(unittest.TestCase):
    def reject(self,fn):self.assertRaises((c.Rejected,ValueError),fn)
    def test_fixture_schema_only(self):
        r=c.check_candidate(fixture(),fixture_only=True);self.assertTrue(r['passed']);self.assertFalse(r['launch_allowed']);self.assertTrue(r['fixture_only'])
    def test_native_path_rejects_even_wellformed_fixture(self):self.reject(lambda:c.check_candidate(fixture()))
    def test_current_blocked_candidate(self):self.reject(c.check_candidate)
    def test_anchor_drift(self):
        x=fixture();x['anchor_world'][0]+=1;self.reject(lambda:c.check_candidate(x,True))
    def test_scale_drift(self):
        x=fixture();x['scale'][0]=2;self.reject(lambda:c.check_candidate(x,True))
    def test_face_reverse(self):
        x=fixture();x['faces'][0].reverse();self.reject(lambda:c.check_candidate(x,True))
    def test_duplicate_face(self):
        x=fixture();x['faces'].append(x['faces'][0]);self.reject(lambda:c.check_candidate(x,True))
    def test_degenerate(self):
        x=fixture();x['faces'][0][0]=x['faces'][0][1];self.reject(lambda:c.check_candidate(x,True))
    def test_missing_control(self):
        x=fixture();x['controls'].pop();self.reject(lambda:c.check_candidate(x,True))
    def test_zero_control(self):
        x=fixture();x['controls'][0]['displacements_world']=np.zeros((4,3)).tolist();self.reject(lambda:c.check_candidate(x,True))
    def test_control_lock_nonzero(self):
        x=fixture();x['controls'][0]['weights'][0]=1;self.reject(lambda:c.check_candidate(x,True))
    def test_control_lock_displacement(self):
        x=fixture();x['controls'][0]['displacements_world'][0][1]=1;self.reject(lambda:c.check_candidate(x,True))
    def test_unweighted_displacement(self):
        x=fixture();x['controls'][0]['weights'][1]=0;self.reject(lambda:c.check_candidate(x,True))
    def test_out_of_range_control(self):
        x=fixture();x['controls'][0]['default']=2;self.reject(lambda:c.check_candidate(x,True))
    def test_duplicate_control_ids(self):
        x=fixture();x['controls'][1]['id']=x['controls'][0]['id'];self.reject(lambda:c.check_candidate(x,True))
    def test_group_out_of_bounds(self):
        x=fixture();x['groups'][0]['indices']=[999];self.reject(lambda:c.check_candidate(x,True))
    def test_nonfinite(self):
        x=fixture();x['vertices_world'][0][0]=float('nan');self.reject(lambda:c.check_candidate(x,True))
    def test_f32_storage_not_absolute_world_quantization(self):
        w=np.array([[3958.001234,600.001234,3667.001234]])
        expected=np.array([[.001234,-.001234,600.001234]],dtype=np.float32)
        self.assertTrue(np.allclose(c.source_vertices(w),expected,rtol=0,atol=1e-10))
        self.assertFalse(np.array_equal(c.source_vertices(w),c.source_vertices(w.astype(np.float32))))
    def test_bound_inputs(self):self.assertGreater(len(c.check_inputs()['files']),20)
    def test_input_sha_tamper(self):
        b=c.read(c.BINDING_PATH);b['files'][0]['sha256']='0'*64;self.reject(lambda:c.check_inputs(b))
    def test_camera_exact_original_bytes(self):
        b=c.read(c.BINDING_PATH);old=c.read(c.ROOT/'source-assets/cloud-bank58/revision-l/design-v1/evidence-bindings.json')['fixed_actual_camera_records']
        self.assertEqual(len(b['world_cameras']),4)
        for a,r in zip(b['world_cameras'],old):
            self.assertEqual(a['camera_transform'],r['camera_transform']);self.assertEqual(a['camera_projection'],r['camera_projection'])
    def test_linear_not_srgb_material(self):
        m=c.read(c.BINDING_PATH)['material'];self.assertEqual(m['linear_rgba'],np.asarray([.56,.60,.67,1],np.float32).astype(float).tolist());self.assertNotEqual(m['linear_rgba'],m['godot_actual']['albedo_srgb_rgba'])
    def test_raw_cannot_self_report_ready(self):self.reject(lambda:c.validate_raw({'passed':True},1,fixture()))

if __name__=='__main__':unittest.main(verbosity=2)
