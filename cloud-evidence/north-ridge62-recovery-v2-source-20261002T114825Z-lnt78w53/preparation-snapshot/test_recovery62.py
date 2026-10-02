"""Pure equivalence and fail-closed tests. Fake RNA is explicitly NOT native proof."""
import ast,base64,copy,hashlib,importlib.util,json,struct,sys,tempfile,types,unittest
from pathlib import Path
import numpy as np
import contract62 as c
import bulk62 as bulk

def load_rebuild(fake):
    old=sys.modules.get('bpy');sys.modules['bpy']=fake
    try:
        spec=importlib.util.spec_from_file_location('recovery_rebuild_mock',c.HERE/'rebuild62.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    finally:
        if old is None:sys.modules.pop('bpy',None)
        else:sys.modules['bpy']=old
    m.bulk_module=lambda:bulk;return m

class FakeValues:
    def __init__(self,count):self.count=count;self.fields={};self.calls=[]
    def __len__(self):return self.count
    def foreach_set(self,name,buf):self.fields[name]=np.asarray(buf).copy();self.calls.append(name)
    def foreach_get(self,name,buf):buf[:]=self.fields[name]
class FakeAttrs:
    def __init__(self,mesh):self.mesh=mesh;self.schemas={};self.values={};self.generation=0
    def new(self,name,type,domain):
        self.generation+=1;self.schemas[name]=(type,domain);self.values[name]=FakeValues(len(self.mesh.vertices)if domain=='POINT'else len(self.mesh.polygons))
    def __getitem__(self,name):return FakeHandle(self,name,self.generation)
class FakeHandle:
    def __init__(self,owner,name,generation):self.owner=owner;self.name=name;self.generation=generation
    @property
    def data(self):
        if self.generation!=self.owner.generation:raise RuntimeError('Stale RNA attribute handle')
        return self.owner.values[self.name]
class FakeMesh:
    def __init__(self,name):self.name=name;self.users=0;self.vertices=[];self.polygons=FakeValues(0);self.materials=[];self.attributes=FakeAttrs(self)
    def from_pydata(self,v,e,f):self.vertices=np.asarray(v,dtype='<f4');self.faces=f;self.polygons=FakeValues(len(f))
    def update(self):pass
class FakeMeshes:
    def new(self,name):return FakeMesh(name)
    def remove(self,mesh):pass
class FakeGroup:
    def __init__(self,name,index):self.name=name;self.index=index;self.weights={};self.calls=0
    def add(self,ids,weight,mode):
        if mode!='REPLACE':raise RuntimeError('Unexpected mode')
        self.calls+=1
        for i in ids:self.weights[i]=struct.pack('<f',weight)
class FakeGroups(list):
    def new(self,name):self.append(FakeGroup(name,len(self)));return self[-1]

class RecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b=c.read(c.BINDING_PATH);cls.expected=c.expected(cls.b)
        cls.jobs=[(list(range(len(cls.b['before_xyz']))),cls.expected['faces'],cls.expected['materials'],cls.b['master_source_triangles'],cls.b['master_tile_ids'],None)]
        for i,tile in enumerate(cls.b['tiles']):cls.jobs.append((tile['master_vertex_ids'],tile['faces_blender'],[cls.expected['materials'][x]for x in tile['master_face_ids']],list(range(2048)),[i]*2048,tile))
    def test_original_77_freeze_unchanged(self):
        freeze=c.read(c.ORIGINAL/'FINAL_SHA256.json')
        self.assertEqual(c.sha(c.ORIGINAL/'FINAL_SHA256.json'),'5f330a85d21da0ffdf3c57c6183b52e86bb6b4c0fa976431946a6f9a46afcc49')
        for name,pin in freeze['files'].items():self.assertEqual(c.sha(c.ROOT/name),pin['sha256'])
    def test_original_failed_run_still_failed(self):
        p=c.ROOT/'cloud-evidence/north-ridge62-source-20261002T111415Z-wlgkmd5l';r=c.read(p/'wrapper-report.json')
        self.assertFalse(r['passed']);self.assertEqual(r['stages'][0]['returncode'],-9);self.assertTrue(r['stages'][0]['timeout_triggered']);self.assertFalse(any((p/'outputs').iterdir()));self.assertFalse((c.ORIGINAL/'north-ridge62.blend').exists())
    def test_original_shape_exact(self):
        proof=c.check_binding(self.b);self.assertEqual(proof['candidate_world_y_sha256'],'2eca5d39aedc03678f7d4611aa8aa497bb616ec9e7b5bade5da16db5284d13d5');self.assertEqual(proof['positions_sha256'],'30b541d723bccaef3d5b7bae5f1569bfe65c9c67b256a451ddf33deb382f4a40')
    def test_weight_batches_exact_all_memberships(self):
        total=0;calls=0
        for ids,*_ in self.jobs:
            old={(j,ci):struct.pack('<f',w)for j,mid in enumerate(ids)for ci,w in zip(self.b['control_ids'][mid],self.b['weights64'][mid])if w>0};new={}
            batches=bulk.weight_batches(self.b,ids)
            for ci,w,indices in batches:
                for j in indices:self.assertNotIn((j,ci),new);new[j,ci]=struct.pack('<f',w)
            self.assertEqual(new,old);total+=len(new);calls+=len(batches)
        self.assertEqual(total,24566);self.assertEqual(calls,7192)
    def test_sub_float32_weight_batch_equivalence(self):
        b={'control_ids':[[0,1,2]]*3,'weights64':[[.2,.8,0],[.2+1e-10,.8,0],[0,.8,.2]]};groups=bulk.weight_batches(b,[0,1,2]);self.assertEqual(sum(len(i)for _,_,i in groups),6);self.assertEqual(len(groups),3)
    def test_zero_and_negative_weight_not_introduced(self):
        b={'control_ids':[[0,1,2]],'weights64':[[0,-1e-20,1e-40]]};groups=bulk.weight_batches(b,[0]);self.assertEqual(len(groups),1);self.assertEqual(groups[0][0],2)
    def test_every_attribute_buffer_matches_scalar_semantics(self):
        fields=0
        for ids,faces,mats,tris,tiles,tile in self.jobs:
            buffers=bulk.attribute_buffers(self.b,ids,tris,tiles,mats,tile)
            expected={'source_master_vertex':ids,'original_source_vertex':list(range(len(ids)))if tile else [-1]*len(ids),'original_color':tile['original_color_float32']if tile else [[0]*4]*len(ids),'original_local':tile['original_source_local_xyz']if tile else [[0]*3]*len(ids),'original_world':[self.b['before_xyz'][i]for i in ids],'canonical_base_y':[self.b['canonical_base_y'][i]for i in ids],'collar':[self.b['collar64'][i]for i in ids],'changed':[self.b['changed'][i]for i in ids],'source_triangle':tris,'source_tile':tiles,'material_region':mats}
            for name,kind,_ in bulk.SCHEMAS:
                arr=np.asarray(expected[name],dtype=bulk.KINDS[kind][1]).ravel();self.assertEqual(arr.tobytes(),buffers[name].tobytes());self.assertTrue(buffers[name].flags.c_contiguous);fields+=1
        self.assertEqual(fields,55)
    def test_mock_write_mesh_every_field_and_weight(self):
        fake=types.SimpleNamespace(data=types.SimpleNamespace(meshes=FakeMeshes(),materials={m['name']:m['name']for m in self.b['materials']}));rebuild=load_rebuild(fake)
        for ids,faces,mats,tris,tiles,tile in self.jobs:
            ob=types.SimpleNamespace(name='FAKE_RNA',data=FakeMesh('old'),vertex_groups=FakeGroups());vertices=[self.expected['vertices'][i]for i in ids]
            rebuild.write_mesh(ob,vertices,faces,mats,self.b,ids,tris,tiles,tile)
            self.assertEqual(ob.data.vertices.tobytes(),np.asarray(vertices,dtype='<f4').tobytes());self.assertEqual(ob.data.faces,faces)
            self.assertEqual(ob.data.polygons.fields['material_index'].tolist(),mats);self.assertFalse(ob.data.polygons.fields['use_smooth'].any())
            buffers=bulk.attribute_buffers(self.b,ids,tris,tiles,mats,tile)
            for name,kind,domain in bulk.SCHEMAS:
                self.assertEqual(ob.data.attributes.schemas[name],(kind,domain));prop=bulk.KINDS[kind][0];self.assertEqual(ob.data.attributes.values[name].fields[prop].tobytes(),buffers[name].tobytes())
            actual={(j,g.index):v for g in ob.vertex_groups for j,v in g.weights.items()};old={(j,ci):struct.pack('<f',w)for j,mid in enumerate(ids)for ci,w in zip(self.b['control_ids'][mid],self.b['weights64'][mid])if w>0};self.assertEqual(actual,old)
    def test_mock_rejects_stale_attribute_handle(self):
        mesh=FakeMesh('test');mesh.attributes.new('a','FLOAT','POINT');a=mesh.attributes['a'];mesh.attributes.new('b','FLOAT','POINT')
        with self.assertRaises(RuntimeError):a.data.foreach_set('value',[])
    def test_bulk_read_matches_actual_mock_bytes(self):
        for kind,(prop,dtype,n)in bulk.KINDS.items():
            data=FakeValues(3);values=np.arange(3*n).astype(dtype);data.fields[prop]=values
            out=bulk.read_collection(data,prop,dtype,n);self.assertEqual(np.asarray(out,dtype=dtype).ravel().tobytes(),values.tobytes())
    def test_negative_source_and_shape_gates_retained(self):
        for field in ('candidate_y','master_faces_blender','master_vertex_ids','master_face_ids','original_local','packed','camera','weights','changed'):
            b=copy.deepcopy(self.b)
            if field=='candidate_y':b[field][0]+=1
            elif field=='master_faces_blender':b[field][0].reverse()
            elif field in ('master_vertex_ids','master_face_ids'):b['tiles'][0][field][0]+=1
            elif field=='original_local':b['tiles'][0]['original_source_local_xyz'][0][0]+=1
            elif field=='packed':b['tiles'][0]['original_packed_storage_base64']['vertex_data']='AAAA'
            elif field=='camera':b['views'][0]['eye'][0]+=1
            elif field=='weights':b['weights64']=(np.array(b['weights64'])*.5).tolist();b['collar64']=(np.array(b['collar64'])*2).tolist()
            else:b['changed']=[False]*len(b['changed'])
            with self.subTest(field=field),self.assertRaises(ValueError):c.check_binding(b)
    def test_text_loading_uses_exact_original_compact_bytes(self):
        compact=json.dumps(self.b,separators=(',',':'),ensure_ascii=False)
        self.assertEqual(len(compact.encode()),5424727);self.assertNotIn('\n',compact);self.assertEqual(hashlib.sha256(compact.encode()).hexdigest(),hashlib.sha256(c.BINDING_PATH.read_bytes()[:-1]).hexdigest())
        node=next(n for n in ast.parse((c.HERE/'native62.py').read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='text');code=compile(ast.Module(body=[node],type_ignores=[]),'native_text_function','exec')
        with tempfile.TemporaryDirectory(prefix='ridge62-pure-text-')as temp:
            class Texts:
                def load(self,filepath,internal):
                    self.internal=internal;self.value=Path(filepath).read_text();return types.SimpleNamespace(name='',is_in_memory=True,filepath='',as_string=lambda:self.value)
            texts=Texts();namespace={'bpy':types.SimpleNamespace(data=types.SimpleNamespace(texts=texts)),'c':c,'telemetry':types.SimpleNamespace(emit=lambda *a,**k:None),'_EMBED_DIR':Path(temp)};exec(code,namespace);namespace['text']('BINDINGS62.json',compact);self.assertTrue(texts.internal);self.assertEqual(texts.value.encode(),compact.encode())
    def test_no_text_write_or_from_string_regression(self):
        tree=ast.parse((c.HERE/'native62.py').read_text());calls=[ast.unparse(n.func)for n in ast.walk(tree)if isinstance(n,ast.Call)];self.assertIn('bpy.data.texts.load',calls);self.assertNotIn('t.write',calls);self.assertNotIn('t.from_string',calls)
    def test_telemetry_flush_and_cpu_fields(self):
        s=(c.HERE/'telemetry62.py').read_text();self.assertIn('flush=True',s);self.assertIn('os.fsync',s);self.assertIn('ru_utime',s);self.assertIn('ru_stime',s);self.assertIn('ru_maxrss',s)
    def test_bounded_new_budget_and_old_image_settings(self):
        s=(c.HERE/'run_source62.py').read_text();self.assertIn("TOTAL={'source':120,'views':90}",s);self.assertIn("NATIVE_CAPS={'build':75,'verify':30,'render':90}",s);self.assertIn('support.run_child',s);self.assertIn('inherited.file_manifest',s);self.assertIn(".open('x')",s)
        n=(c.HERE/'native62.py').read_text();self.assertIn('resolution_x=1179',n);self.assertIn('resolution_y=664',n);self.assertIn('resolution_percentage=100',n);self.assertIn('scene.cycles.samples=8',n)
    def test_binding_failure_has_terminal_scope_and_postraw_validation(self):
        tree=ast.parse((c.HERE/'native62.py').read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main');guard=next(n for n in main.body if isinstance(n,ast.Try));body=ast.unparse(ast.Module(body=guard.body,type_ignores=[]));final=ast.unparse(ast.Module(body=guard.finalbody,type_ignores=[]));self.assertIn('c.check_binding(b)',body);self.assertIn('c.write(',final)
        capture=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='capture');self.assertNotIn('c.require',ast.unparse(capture));self.assertLess(body.index('c.write(rawpath, raw)'),body.index('c.validate_raw(raw, b)'))
    def test_all_source_ast_and_no_run_artifacts(self):
        for p in c.HERE.glob('*.py'):ast.parse(p.read_text())
        self.assertFalse(c.SOURCE.exists());self.assertFalse(list(c.HERE.glob('*attempt.json')));self.assertFalse(list(c.HERE.glob('*.png')))
if __name__=='__main__':unittest.main(verbosity=2)
