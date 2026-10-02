"""Source-only math/protocol negative controls. No executable launch, GLB write or native claim."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch
import numpy as np
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import contract58k as c
import bounded_support58k as support
import run_import58k as runner


def reconstructed_source():
    verified=c.source_preconditions();poly=c.load(c.K/'poly58k.py')
    proof=c.strict_json_text(verified['native_identity']['construction_proof'])
    candidate=poly.build(proof['effective_control_config'])
    frame=c.strict_json_text(verified['native_identity']['source_frame'])
    vertices=(candidate['vertices']@poly.source_basis(frame).T).astype(np.float32).astype(float)
    c.require(c.geometry_fingerprint(vertices,candidate['faces'])==verified['native_identity']['mesh'],'Static derivation must match saved native fingerprint')
    return dict(positions=vertices.tolist(),triangles=candidate['faces'].tolist(),material=dict(base_color_linear_rgba=np.asarray([.56,.60,.67,1],np.float32).astype(float).tolist(),roughness=float(np.float32(.9)),metallic=0.,double_sided=True)),frame


def split_fixture(source):
    v=c.mapped(source['positions']);faces=np.asarray(source['triangles']);positions=v[faces].reshape(-1,3)
    normals=np.cross(v[faces[:,1]]-v[faces[:,0]],v[faces[:,2]]-v[faces[:,0]])
    normals/=np.linalg.norm(normals,axis=1)[:,None]
    return dict(positions=positions.tolist(),normals=np.repeat(normals,3,axis=0).tolist(),indices=list(range(1152)))


def memory_glb(raw,material,change=None):
    chunks=[np.asarray(raw['positions'],dtype='<f4').tobytes(),np.asarray(raw['normals'],dtype='<f4').tobytes(),np.asarray(raw['indices'],dtype='<u2').tobytes()]
    views=[];offset=0
    for chunk in chunks:views.append(dict(buffer=0,byteOffset=offset,byteLength=len(chunk)));offset+=len(chunk)
    doc=dict(asset=dict(version='2.0'),buffers=[dict(byteLength=offset)],bufferViews=views,
        accessors=[dict(bufferView=0,componentType=5126,count=len(raw['positions']),type='VEC3'),dict(bufferView=1,componentType=5126,count=len(raw['normals']),type='VEC3'),dict(bufferView=2,componentType=5123,count=len(raw['indices']),type='SCALAR')],
        nodes=[dict(name=c.BANK,mesh=0)],meshes=[dict(primitives=[dict(attributes=dict(POSITION=0,NORMAL=1),indices=2,material=0)])],materials=[deepcopy(material)],scenes=[dict(nodes=[0])],scene=0)
    if change:change(doc)
    js=json.dumps(doc,separators=(',',':')).encode();js+=b' '*((-len(js))%4)
    binary=b''.join(chunks);binary+=b'\x00'*((-len(binary))%4)
    return struct.pack('<4sII',b'glTF',2,28+len(js)+len(binary))+struct.pack('<I4s',len(js),b'JSON')+js+struct.pack('<I4s',len(binary),b'BIN\x00')+binary


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source,cls.frame=reconstructed_source();cls.raw=split_fixture(cls.source)
        cls.material=dict(pbrMetallicRoughness=dict(baseColorFactor=cls.source['material']['base_color_linear_rgba'],roughnessFactor=cls.source['material']['roughness'],metallicFactor=0),doubleSided=True)
    def rejects(self,function,*args,**kwargs):
        with self.assertRaises((ValueError,KeyError,IndexError,TypeError,struct.error)):function(*args,**kwargs)
    def test_finite_right_handed_axis_mapping(self):
        self.assertEqual(np.linalg.det(c.MAP),1)
        np.testing.assert_array_equal(c.mapped([[1,2,3]]),[[1,3,-2]])
        np.testing.assert_array_equal(c.mapped(self.source['positions'])@c.MAP,np.asarray(self.source['positions']))
        self.assertEqual(self.frame['anchor_godot_world_xyz'],[3958.,0.,3667.])
    def test_saved_fingerprint_static_reconstruction(self):
        report=c.validate_geometry(self.raw,self.source)
        self.assertEqual(report['authored_vertex_count'],194);self.assertEqual(report['render_vertex_count'],1152)
    def test_split_reordering_and_godot_winding(self):
        raw=deepcopy(self.raw);permutation=np.arange(1152)[::-1]
        raw['positions']=np.asarray(raw['positions'])[permutation].tolist();raw['normals']=np.asarray(raw['normals'])[permutation].tolist();raw['indices']=(1151-np.asarray(raw['indices']).reshape(-1,3)[:,[2,1,0]]).ravel().tolist()
        c.validate_geometry(raw,self.source,clockwise=True)
    def test_every_triangle_reversal_rejected(self):
        for face in range(384):
            with self.subTest(face=face):
                raw=deepcopy(self.raw);a=face*3;raw['indices'][a+1],raw['indices'][a+2]=raw['indices'][a+2],raw['indices'][a+1]
                self.rejects(c.validate_geometry,raw,self.source)
    def test_all_position_axes_and_anchor_rejected(self):
        for axis in range(3):
            raw=deepcopy(self.raw);raw['positions'][10][axis]+=.001;self.rejects(c.validate_geometry,raw,self.source)
        raw=deepcopy(self.raw);raw['positions']=(np.asarray(raw['positions'])+self.frame['anchor_godot_world_xyz']).tolist();self.rejects(c.validate_geometry,raw,self.source)
    def test_wrong_up_and_mirror_rejected(self):
        for matrix in [np.eye(3),np.diag([-1,1,1]),-c.MAP]:
            raw=deepcopy(self.raw);raw['positions']=(np.asarray(raw['positions'])@matrix@c.MAP).tolist();self.rejects(c.validate_geometry,raw,self.source)
    def test_bad_array_count_duplicate_and_nonfinite(self):
        for kind in ['count','negative','range','duplicate','nan','infinite']:
            raw=deepcopy(self.raw)
            if kind=='count':raw['indices'].pop()
            elif kind=='negative':raw['indices'][0]=-1
            elif kind=='range':raw['indices'][0]=1152
            elif kind=='duplicate':raw['indices'][:3]=raw['indices'][3:6]
            elif kind=='nan':raw['positions'][0][0]=float('nan')
            else:raw['normals'][0][0]=float('inf')
            self.rejects(c.validate_geometry,raw,self.source)
    def test_flat_normals_not_smoothing(self):
        for normal in [[0,1,0],[-x for x in self.raw['normals'][0]],self.raw['normals'][3]]:
            raw=deepcopy(self.raw);raw['normals'][0]=normal;self.rejects(c.validate_geometry,raw,self.source)
    def test_glb_embedded_valid(self):
        doc,raw,mat=c.parse_glb_bytes(memory_glb(self.raw,self.material));c.validate_geometry(raw,self.source);c.validate_material(mat,self.source)
    def test_glb_negative_schema(self):
        alterations=[lambda d:d.update(images=[{}]),lambda d:d.update(skins=[{}]),lambda d:d.update(cameras=[{}]),lambda d:d.update(animations=[{}]),lambda d:d.update(extensionsUsed=['KHR_draco_mesh_compression']),lambda d:d['buffers'][0].update(uri='outside.bin'),lambda d:d['nodes'].append(dict(mesh=0)),lambda d:d['nodes'][0].update(translation=[3958,0,3667]),lambda d:d['nodes'][0].update(rotation=[1,0,0,0]),lambda d:d['nodes'][0].update(children=[1]),lambda d:d['scenes'][0].update(nodes=[]),lambda d:d.update(scene=1),lambda d:d['accessors'][0].update(count=1153),lambda d:d['accessors'][0].update(byteOffset=1_000_000),lambda d:d['accessors'][0].update(sparse={"count":1}),lambda d:d['accessors'][0].update(normalized=True),lambda d:d['bufferViews'][0].update(byteLength=5),lambda d:d['bufferViews'][0].update(byteStride=1),lambda d:d['meshes'][0]['primitives'][0]['attributes'].update(TEXCOORD_0=0),lambda d:d['meshes'][0]['primitives'][0].update(mode=1),lambda d:d['materials'][0].update(extensions={'unexpected':{}})]
        for index,change in enumerate(alterations):
            with self.subTest(index=index):self.rejects(c.parse_glb_bytes,memory_glb(self.raw,self.material,change))
    def test_glb_truncation(self):
        blob=memory_glb(self.raw,self.material)
        for limit in [0,1,11,12,19,20,len(blob)-1]:self.rejects(c.parse_glb_bytes,blob[:limit])
    def test_material_color_conversion(self):
        c.validate_material(self.material,self.source)
        for key,value in [('emissiveFactor',[1,0,0]),('extensions',{'KHR_materials_unlit':{}}),('alphaMode','BLEND')]:
            altered=deepcopy(self.material);altered[key]=value;self.rejects(c.validate_material,altered,self.source)
        s=self.source['material'];m=dict(albedo_srgb_rgba=[c.linear_to_srgb(v) for v in s['base_color_linear_rgba'][:3]]+[1],roughness=s['roughness'],metallic=0,texture_count=0,shader_material=False,emission_enabled=False,emission_rgb=[0,0,0],transparency=0,cull_mode=2)
        c.validate_material(m,self.source,godot=True)
        for key,value in [('albedo_srgb_rgba',s['base_color_linear_rgba']),('roughness',.5),('metallic',1),('texture_count',1),('shader_material',True),('emission_enabled',True),('emission_rgb',[1,0,0]),('transparency',1),('cull_mode',0)]:
            altered=dict(m);altered[key]=value;self.rejects(c.validate_material,altered,self.source,godot=True)
    def test_strict_json(self):
        for text in ['{"x":NaN}','{"x":1e999}','{"x":0,"x":1}']:self.rejects(c.strict_json_text,text)
    def test_source_default_never_launches(self):
        with patch.object(sys,'argv',['run_import58k.py']),patch.object(support,'run_child',side_effect=AssertionError('Native launch forbidden')),patch.object(runner.tempfile,'mkdtemp',side_effect=AssertionError('Unexpected output')):
            self.assertEqual(runner.main(),0)
    def test_python_syntax_and_no_save_render_in_export(self):
        for path in c.HERE.glob('*.py'):ast.parse(path.read_text())
        s=(c.HERE/'export58k.py').read_text()
        self.assertEqual(s.count('bpy.ops.export_scene.gltf('),1)
        for forbidden in ['save_as_mainfile','bpy.ops.render','bpy.ops.wm.save','rebuild_from_controls(']:self.assertNotIn(forbidden,s)
    def test_process_fail_closed(self):
        row=dict(status='finished',native_exit_observed=True,returncode=0,wrapper_received_signal=None,timeout_triggered=False,rss_limit_triggered=False)
        self.assertTrue(support.process_passed(row))
        for key,value in [('status','running'),('native_exit_observed',False),('returncode',1),('wrapper_received_signal',15),('timeout_triggered',True),('rss_limit_triggered',True),('terminal_report_errors',['failure'])]:
            bad=dict(row);bad[key]=value;self.assertFalse(support.process_passed(bad))
    def test_wrapper_scope_and_limits(self):
        self.assertEqual(runner.TOTAL_SECONDS,120);self.assertEqual(support.MAX_RSS_KIB,1572864)
        self.assertEqual(runner.NATIVE_SECONDS,(30,30,20,20))
        self.assertFalse(runner.IMPORT_PARAMETERS['meshes/generate_lods']);self.assertTrue(runner.IMPORT_PARAMETERS['meshes/force_disable_compression'])
        script=(c.HERE/'run_import58k.py').read_text();self.assertNotIn('--path\',str(PROJECT)',script)
        self.assertIn("file_manifest(PROJECT)",script);self.assertIn("'--path',str(scratch)",script)

if __name__=='__main__':unittest.main(verbosity=2)
