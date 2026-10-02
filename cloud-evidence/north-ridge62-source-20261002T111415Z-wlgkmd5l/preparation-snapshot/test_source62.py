"""Pure Python positive/negative preparation checks. No native subprocess calls."""
import ast,copy,json,unittest,hashlib,base64,struct
from pathlib import Path
import numpy as np
import contract62 as c
import prepare_bindings62 as p

class SourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.b=c.read(c.HERE/'bindings62.json')
    def test_frozen_reproducible(self):
        b,proof=p.build_binding();self.assertEqual(b,self.b);self.assertTrue(proof['passed'])
    def test_every_candidate_row(self):
        patch=c.read(c.PREP/'candidate-vertex-y.json');actual=c.expected(self.b)['world_xyz']
        count=0
        for tile in patch['tiles']:
            row=next(x for x in self.b['tiles']if x['name']==tile['tile']);table={tuple(self.b['before_xyz'][i]):actual[i][1]for i in row['master_vertex_ids']}
            for override in tile['vertex_y_overrides']:
                self.assertEqual(c.digest([table[tuple(override['before_xyz'])]]),c.digest([override['candidate_y']]));count+=1
        self.assertEqual(count,1246)
    def test_changed_geometry_and_unchanged_bytes(self):
        a=np.array(self.b['before_xyz']);b=np.array(c.expected(self.b)['world_xyz']);f=np.array(self.b['master_faces_blender']);mask=np.any(a[f]!=b[f],axis=(1,2));self.assertEqual(int(mask.sum()),2479)
        self.assertEqual(c.digest(a[:,[0,2]]),c.digest(b[:,[0,2]]));unchanged=np.logical_not(self.b['changed']);self.assertEqual(c.digest(a[unchanged]),c.digest(b[unchanged]))
    def test_semantic_height_edit_actually_rebuilds(self):
        targets=[x['target_y']for x in self.b['controls']];targets[14]+=10;a=np.array(c.expected(self.b)['vertices']);b=np.array(c.expected(self.b,targets)['vertices']);self.assertGreater(np.count_nonzero(a[:,2]!=b[:,2]),0);self.assertEqual(c.digest(a[:,:2]),c.digest(b[:,:2]))
    def test_boundary_edit_rejected(self):
        targets=[x['target_y']for x in self.b['controls']];targets[0]+=1
        with self.assertRaises(ValueError):c.expected(self.b,targets)
    def test_candidate_mutation_rejected(self):
        b=copy.deepcopy(self.b);b['candidate_y'][100]+=1
        with self.assertRaises(ValueError):c.check_binding(b)
    def test_winding_mutation_rejected(self):
        b=copy.deepcopy(self.b);b['master_faces_blender'][0].reverse()
        with self.assertRaises(ValueError):c.check_binding(b)
    def test_source_slot_welding_rejected(self):
        b=copy.deepcopy(self.b);b['tiles'][0]['master_vertex_ids']=list(dict.fromkeys(b['tiles'][0]['master_vertex_ids']))
        with self.assertRaises(ValueError):c.check_binding(b)
    def test_source_index_mutation_rejected(self):
        b=copy.deepcopy(self.b);b['tiles'][0]['original_source_index_sequence'][0]=1
        with self.assertRaises(ValueError):c.check_binding(b)
    def test_source_color_mutation_rejected(self):
        b=copy.deepcopy(self.b);b['tiles'][0]['original_color_rgba8'][0][0]^=1
        with self.assertRaises(ValueError):c.check_binding(b)
    def test_original_packed_bytes(self):
        for tile in self.b['tiles']:
            for key,value in tile['original_packed_storage_base64'].items():
                data=base64.b64decode(value,validate=True);pin=tile['original_surface_identity']['packed_payloads'][key];self.assertEqual(hashlib.sha256(data).hexdigest(),pin['sha256']);self.assertEqual(len(data),pin['bytes'])
    def test_exact_original_corner_mapping(self):
        for tile in self.b['tiles']:
            f=np.array(tile['faces_blender'])[:,[0,2,1]].ravel();self.assertEqual(f.tolist(),tile['original_source_index_sequence']);self.assertEqual(len(tile['source_triangle_corner_to_master_vertex']),6144)
            for k,(tri,corner,master,source) in enumerate(tile['source_triangle_corner_to_master_vertex']):self.assertEqual((tri,corner,source),(k//3,k%3,int(f[k])));self.assertEqual(master,tile['master_vertex_ids'][source])
    def test_camera_pose_orientation(self):
        views=c.read(c.ROOT/'source-assets/north-ridge62-intake/plan.json')['fixed_reference_views']
        for view in self.b['views'][:2]:
            self.assertEqual({k:view[k]for k in ('eye','target','fov')},views[view['name']]);m=c.expected_camera_matrix(view);self.assertAlmostEqual(np.linalg.det(m[:3,:3]),1);self.assertTrue(np.allclose(m[:3,:3].T@m[:3,:3],np.eye(3)))
    def test_source_no_native_start_on_import(self):
        for path in c.HERE.glob('*.py'):ast.parse(path.read_text())
        for name in ['contract62.py','prepare_bindings62.py']:
            tree=ast.parse((c.HERE/name).read_text());imports=[n.module for n in ast.walk(tree)if isinstance(n,ast.ImportFrom)]+[a.name for n in ast.walk(tree)if isinstance(n,ast.Import)for a in n.names]
            self.assertNotIn('bpy',imports);self.assertNotIn('subprocess',imports)
    def test_wrapper_only_inherited_process_helper(self):
        tree=ast.parse((c.HERE/'run_source62.py').read_text());calls=[ast.unparse(n.func)for n in ast.walk(tree)if isinstance(n,ast.Call)];self.assertIn('support.run_child',calls);self.assertNotIn('subprocess.Popen',calls);self.assertIn('inherited.file_manifest',calls)
        s=(c.HERE/'run_source62.py').read_text();self.assertIn("TOTAL={'source':60,'views':90}",s);self.assertIn(".open('x')",s);self.assertNotIn('Godot_v',s)
    def test_native_raw_before_validate(self):
        s=(c.HERE/'native62.py').read_text();self.assertLess(s.index('c.write(rawpath,raw)'),s.index("report['validation']=c.validate_raw(raw,b)"));self.assertNotIn('export_scene',s);self.assertNotIn('resolution_percentage=50',s)
    def test_no_fictional_normal_bit_equality(self):
        s=(c.HERE/'contract62.py').read_text();self.assertIn('Corner geometric normal gate, no polygon/corner bit-equality assumption',s)
    def test_reviewer_six_authority_mutations_rejected(self):
        for field in ('master_vertex_ids','master_face_ids','original_local','packed_bytes','camera','changed'):
            b=copy.deepcopy(self.b)
            if field in ('master_vertex_ids','master_face_ids'):b['tiles'][0][field][0]+=1
            elif field=='original_local':b['tiles'][0]['original_source_local_xyz'][0][0]+=1
            elif field=='packed_bytes':b['tiles'][0]['original_packed_storage_base64']['vertex_data']='AAAA'
            elif field=='camera':b['views'][0]['eye'][0]+=1
            else:b['changed']=[False]*len(b['changed'])
            with self.subTest(field=field),self.assertRaises(ValueError):c.check_binding(b)
    def test_resource_and_controller_semantics_rejected(self):
        b=copy.deepcopy(self.b);b['tiles'][0]['source_resource']='made_up_resource'
        with self.assertRaises(ValueError):c.check_binding(b)
        b=copy.deepcopy(self.b);b['weights64']=(np.array(b['weights64'])*.5).tolist();b['collar64']=(np.array(b['collar64'])*2).tolist()
        with self.assertRaises(ValueError):c.check_binding(b)
    def test_explicit_edit_mode_gate(self):
        s=(c.HERE/'rebuild62.py').read_text();self.assertIn("ob.mode=='OBJECT' and not ob.data.is_editmode",s);self.assertLess(s.index("ob.mode=='OBJECT'"),s.index('write_mesh(master,'))
    def test_frozen_prep_sha(self):self.assertEqual(c.sha(c.PREP/'FINAL_SHA256.json'),c.PREPARATION_SHA)
if __name__=='__main__':unittest.main(verbosity=2)
