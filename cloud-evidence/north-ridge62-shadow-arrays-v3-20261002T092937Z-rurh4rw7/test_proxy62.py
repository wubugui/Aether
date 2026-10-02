#!/usr/bin/env python3
import copy,json,math,random,sys,unittest
from fractions import Fraction
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import proxy_math62 as m
import prepare_proxy62 as p
import run_proxy62 as r
I=[1.,0.,0.,0.,1.,0.,0.,0.,1.,0.,0.,0.]

class Math(unittest.TestCase):
    def test_swizzle(self):self.assertEqual(m.row_to_columns(list(range(12))),[0,4,8,1,5,9,2,6,10,3,7,11])
    def test_capsule_identity(self):
        b=m.tree_capsule_box(I);self.assertLessEqual(b['min'][0],-2.4);self.assertGreaterEqual(b['max'][1],11);self.assertLessEqual(b['min'][1],0)
    def test_full_affine_capsule(self):
        t=[-2.,3.,.5,4.,-1.,2.,.2,-5.,3.,100.,-10.,50.];b=m.tree_capsule_box(t)
        for y in [0.,2.4,5.5,8.6,11.]:
            radius=2.4 if 2.4<=y<=8.6 else 0.
            for angle in range(0,360,7):
                v=[radius*math.cos(math.radians(angle)),y,radius*math.sin(math.radians(angle))]
                q=[sum(t[j*3+i]*v[j]for j in range(3))+t[9+i]for i in range(3)]
                self.assertTrue(all(b['min'][i]<=q[i]<=b['max'][i]for i in range(3)))
    def test_interval_outer_exact_rational_corners(self):
        rng=random.Random(62)
        for _ in range(80):
            t=[m.f32(rng.uniform(-100,100))for _ in range(12)];lo=[m.f32(rng.uniform(-10,0))for _ in range(3)];hi=[m.f32(rng.uniform(0,10))for _ in range(3)]
            b=m.transform_box_outer(t,{'min':lo,'max':hi})
            for k in range(8):
                v=[hi[i]if k>>i&1 else lo[i]for i in range(3)]
                for i in range(3):
                    exact=Fraction(t[9+i])+sum(Fraction(t[j*3+i])*Fraction(v[j])for j in range(3))
                    self.assertLessEqual(Fraction(b['min'][i]),exact);self.assertGreaterEqual(Fraction(b['max'][i]),exact)
    def test_boundary_inclusive_and_vertical_not_gate(self):
        b={'min':[1.,999.,2.],'max':[3.,1000.,4.]};self.assertTrue(m.hits(b,[3,5,4,6]));self.assertFalse(m.hits(b,[3.0001,5,4,6]))
    def test_proxy_only_edge(self):
        t=I[:];t[9]=3.;proxy=m.tree_capsule_box(t);visual={'min':[2.9,0.,-.1],'max':[3.1,1.,.1]};q=[0,1,-1,1]
        self.assertFalse(m.hits(visual,q));self.assertTrue(m.hits(proxy,q));self.assertTrue(m.hits(m.union(visual,proxy),q))
    def test_native_negative_scale(self):
        t=I[:];t[0]=-2.;t[9]=10.;self.assertEqual(m.transform_box_native(t,{'min':[-1.,0.,-1.],'max':[3.,4.,1.]}),{'min':[4.,0.,-1.],'max':[12.,4.,1.]})
    def test_malformed_rejected(self):
        for b in [None,{}, {'min':[1,0,0],'max':[0,1,1]}, {'min':[0,0,0],'max':[math.nan,1,1]}]:
            with self.assertRaises(ValueError):m.hits(b,[0,1,0,1])
        with self.assertRaises(ValueError):m.tree_capsule_box([math.nan]*12)
    def test_protection_actual_binding(self):
        self.assertEqual(p.protected({'resource':'res://assets/coast61/oak_-5_-5_CoastalPines36b.res'}),'coast61_-5_-5')
        self.assertEqual(p.protected({'resource':'res://assets/coast56/poplar_-4_-4_CoastalPines36b.res'}),'coast56_-4_-4')
        self.assertEqual(p.protected({'resource':'res://assets/scatter/Grounded_oak_-5_-5.res'}),'')

class Protocol(unittest.TestCase):
    def setUp(self):
        self.req=json.loads((p.HERE/'native-request.json').read_text());b={'min':[-1.,0.,-1.],'max':[1.,2.,1.]};self.fixture={'passed':True,'issues':[],'world_instantiated':False,'runtime_collision_observed':False,'all_occupancy_complete':False,'visual_meshes':[]}
        def mesh(uri,sha,src):
            ss=[{'index':x['index'],'primitive':3,'format':x['format'],'vertex_count':x['vertex_count'],'index_count':x['index_count'],'vertex_bytes_sha256':'0'*64,'vertex_bounds':copy.deepcopy(b)}for x in src]
            return {'mesh_resource':uri,'surface_storage_sha256':sha,'shadow_mesh_resource':'','shadow_surface_storage_sha256':'','vertex_bounds':copy.deepcopy(b),'combined_vertex_bounds':copy.deepcopy(b),'face_bounds':copy.deepcopy(b),'face_bytes_sha256':'1'*64,'vertex_count':sum(x['vertex_count']for x in ss),'face_vertex_count':sum(x['index_count']or x['vertex_count']for x in ss),'surfaces':ss}
        for x in self.req['visual_meshes']:
            item=mesh(x['mesh_resource'],x['primary_surface_storage_sha256'],x['primary_surfaces'])
            if x['shadow_mesh_resource']:
                item['shadow_mesh_resource']=x['shadow_mesh_resource'];item['shadow_surface_storage_sha256']=x['shadow_surface_storage_sha256'];item['shadow']=mesh(x['shadow_mesh_resource'],x['shadow_surface_storage_sha256'],x['shadow_surfaces'])
            self.fixture['visual_meshes'].append(item)
        rock=copy.deepcopy(next(x for x in self.fixture['visual_meshes']if x['mesh_resource']=='res://assets/meshes/rock.res'))
        rock.update(mesh_resource=self.req['rock_expected_primary_resource'],prefab=p.ROCK_PREFAB,imported_scene=p.ROCK_IMPORT,mesh_node_count=1,first_mesh_node_path='Model/rock',mesh_node_transform_applied_to_proxy=False,mesh_node_transform_variant_hex='00'*52,
                    imported_node_inventory=[{'index':0,'path':'.','type':'Node3D'},{'index':1,'path':'rock','type':'MeshInstance3D','mesh_resource':self.req['rock_expected_primary_resource']}])
        self.fixture['rock']=rock
    def test_positive_fixture_not_execution_proof(self):self.assertEqual(p.validate_native(self.fixture,self.req),self.fixture['rock']['face_bounds'])
    def test_false_native_rejected(self):
        for key,val in [('passed',False),('issues',['failure']),('world_instantiated',True),('runtime_collision_observed',True),('all_occupancy_complete',True),('visual_meshes',[])]:
            d=copy.deepcopy(self.fixture);d[key]=val
            with self.assertRaises((ValueError,KeyError)):p.validate_native(d,self.req)
    def test_visual_identity_mutations_rejected(self):
        for key,val in [('mesh_resource','wrong'),('surface_storage_sha256','wrong'),('shadow_mesh_resource','wrong'),('shadow_surface_storage_sha256','wrong'),('vertex_count',0),('face_vertex_count',0),('combined_vertex_bounds',{})]:
            d=copy.deepcopy(self.fixture);d['visual_meshes'][0][key]=val
            with self.assertRaises((ValueError,KeyError)):p.validate_native(d,self.req)
    def test_rock_wrong_source_or_missing_faces_rejected(self):
        for key,val in [('prefab','wrong'),('imported_scene','res://assets/collision/rock.res'),('mesh_node_count',2),('first_mesh_node_path',''),('mesh_resource','res://assets/meshes/rock.res'),('mesh_node_transform_applied_to_proxy',True),('face_bounds',{}),('face_vertex_count',0),('face_vertex_count',4),('face_bytes_sha256','bad')]:
            d=copy.deepcopy(self.fixture);d['rock'][key]=val
            with self.assertRaises((ValueError,KeyError)):p.validate_native(d,self.req)
    def test_review_malformed_report_regressions(self):
        for key,value in [('surfaces',[]),('face_vertex_count',1),('vertex_count',1),('surface_storage_sha256','Z'*64),('combined_vertex_bounds',{'min':[0.,0.,0.],'max':[0.,0.,0.]})]:
            d=copy.deepcopy(self.fixture);d['visual_meshes'][0][key]=value
            with self.assertRaises((ValueError,KeyError)):p.validate_native(d,self.req)
        for key,value in [('imported_node_inventory',[]),('mesh_resource',p.ROCK_IMPORT+'::garbage'),('mesh_node_transform_variant_hex','xyz'),('face_bytes_sha256','z'*64)]:
            d=copy.deepcopy(self.fixture);d['rock'][key]=value
            with self.assertRaises((ValueError,KeyError)):p.validate_native(d,self.req)
        d=copy.deepcopy(self.fixture);d['visual_meshes'][0]['shadow']['vertex_count']+=1
        with self.assertRaises(ValueError):p.validate_native(d,self.req)
    def test_per_surface_triangle_divisibility(self):
        d=copy.deepcopy(self.fixture);rock=d['rock'];s=copy.deepcopy(rock['surfaces'][0]);s.update(index=0,vertex_count=3,index_count=1)
        t=copy.deepcopy(s);t.update(index=1,index_count=2);rock.update(surfaces=[s,t],vertex_count=6,face_vertex_count=3)
        with self.assertRaises(ValueError):p.validate_native(d,self.req)
    def test_process_limits_fail_closed(self):
        d={'status':'finished','returncode':0,'external_signal':None,'timeout_triggered':False,'wall_seconds':1.,'cpu_affinity':[24,25]};self.assertTrue(r.process_ok(d,[]))
        for key,val in [('returncode',1),('status','running'),('timeout_triggered',True),('wall_seconds',60.0001),('wall_seconds',math.nan),('wall_seconds',-1),('cpu_affinity',[24]),('external_signal',15),('exception','failed')]:
            q=copy.deepcopy(d);q[key]=val;self.assertFalse(r.process_ok(q,[]))
        self.assertFalse(r.process_ok(d,['ERROR: failure']))
    def test_freeze_exact_set(self):
        r.validate_freeze({k:'0'*64 for k in r.FROZEN_NAMES})
        for f in [{},{'../bad':'0'*64},{'/tmp/bad':'0'*64},{k:'z'*64 for k in r.FROZEN_NAMES}]:
            with self.assertRaises(RuntimeError):r.validate_freeze(f)
        for k in r.FROZEN_NAMES:
            f={x:'0'*64 for x in r.FROZEN_NAMES};del f[k]
            with self.assertRaises(RuntimeError):r.validate_freeze(f)
    def test_source_guard(self):r.source_guards()

if __name__=='__main__':unittest.main(verbosity=2)
