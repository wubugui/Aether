"""Fail-closed author-source contract. Pure Python/NumPy; imports never launch engines.

This preparation deliberately cannot turn schema/fixture tests into a spatial
acceptance. A release needs a concrete new candidate and an implemented, reviewed
whole-bank geometry gate. Neither is silently synthesized from two 1-D curves.
"""
from __future__ import annotations
import hashlib, importlib.util, json, os
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
VERSION='cloudbank58l-source-preparation-v1'
SOURCE=HERE/'cloud_bank58l.blend'
CANDIDATE_PATH=HERE/'candidate-status.json'
BINDING_PATH=HERE/'input-bindings.json'
BLENDER=ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
BLENDER_SHA='050c02562f81fe80ba616a80198fa02d381e60f8b61b8d39add881f4bca0d7d8'
ANCHOR=np.array([3958.,0.,3667.])
CONTROL_IDS=['C01_Crown_A','C02_Crown_B','C03_Return_C','C04_Shoulder_D','C05_Main_Valley','C06_Belly','C07_Meso_Relief']
NORMAL_EPS=3e-5  # Existing K actual-source outward-normal bound; not shape tolerance.
class Rejected(ValueError):pass

def require(value,message):
    if not value:raise Rejected(message)
def read(path):return json.loads(Path(path).read_text())
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def write(path,value):
    path=Path(path);data=json.dumps(value,indent=2,allow_nan=False)+'\n'
    with path.open('w') as f:f.write(data);f.flush();os.fsync(f.fileno())
def load(path):
    path=Path(path);spec=importlib.util.spec_from_file_location('cloud58l_'+path.stem,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def source_vertices(world):
    w=np.asarray(world,float);return np.column_stack((w[:,0]-3958.,3667.-w[:,2],w[:,1])).astype('<f4')
def world_vertices(source):
    v=np.asarray(source,float);return np.column_stack((v[:,0]+3958.,v[:,2],3667.-v[:,1]))
def finite_array(value,shape,name,integer=False):
    a=np.asarray(value);require(a.shape==shape,name+':shape')
    require(a.dtype.kind in ('iu' if integer else 'fiu') and np.isfinite(a).all(),name+':finite/type')
    return a.astype(int if integer else float)
def check_inputs(binding=None):
    b=read(BINDING_PATH) if binding is None else binding
    for row in b['files']:
        p=ROOT/row['path'];require(p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'INPUT_CHANGED:'+row['path'])
    return b

def check_candidate(candidate=None,fixture_only=False):
    """Necessary schema+topology+response tests; never a whole-bank geometry proof.

    fixture_only is solely for tiny synthetic unit fixtures and ALWAYS returns
    launch_allowed=False. Native calls cannot skip the explicit spatial gate.
    """
    c=read(CANDIDATE_PATH) if candidate is None else candidate
    require(c.get('implementation_ready') is True,'CANDIDATE_NOT_READY:'+','.join(c.get('blockers',['missing candidate'])))
    require(c.get('schema')=='cloudbank58l-offline-candidate-v1','CANDIDATE_SCHEMA')
    v=np.asarray(c['vertices_world'],float);f=np.asarray(c['faces'])
    require(v.ndim==2 and v.shape[1]==3 and np.isfinite(v).all(),'VERTICES')
    require(f.ndim==2 and f.shape[1]==3 and f.dtype.kind in 'iu' and f.min()>=0 and f.max()<len(v),'FACES')
    require(len(f)<=5164 and len(v)<=2584,'NEW_FULL_BANK_BUDGET')
    require(len({tuple(x) for x in source_vertices(v).tolist()})==len(v),'DUPLICATE_F32_VERTICES')
    poly=load(ROOT/'source-assets/cloud-bank58/revision-k/poly58k.py')
    sv=source_vertices(v).astype(float)
    topo=poly.topology(sv,f,dict(maximum_vertices=2584,maximum_triangles=5164,minimum_area_m2=1e-6,minimum_edge_m=1e-5))
    require(c.get('anchor_world')==[3958,0,3667] and c.get('scale')==[1,1,1],'FRAME_OR_SCALE_CHANGED')
    locks=c['locked_indices'];require(all(type(x)is int and 0<=x<len(v) for x in locks) and len(set(locks))==len(locks),'LOCK_INDICES')
    controls=c['controls'];require([x['id'] for x in controls]==CONTROL_IDS,'SEVEN_CONTROL_IDENTITIES')
    responses=[]
    for row in controls:
        require(all(type(row[k])in (int,float) and np.isfinite(row[k]) for k in ('default','min','max')) and row['min']<=row['default']<=row['max'] and row['min']<row['max'],'CONTROL_BOUNDS:'+row['id'])
        require(isinstance(row['semantic'],str) and row['semantic'] and isinstance(row['units'],str),'CONTROL_SEMANTICS')
        finite_array(row['position_world'],(3,),'CONTROL_POSITION')
        w=finite_array(row['weights'],(len(v),),'CONTROL_WEIGHTS')
        d=finite_array(row['displacements_world'],(len(v),3),'CONTROL_DISPLACEMENTS')
        require(np.all((w>=0)&(w<=1)) and np.any(w>0),'CONTROL_NONZERO_WEIGHT')
        require(np.all(w[locks]==0) and np.all(d[locks]==0),'LOCKED_CONTROL_EFFECT')
        require(np.all(d[w==0]==0),'UNWEIGHTED_CONTROL_EFFECT')
        t=row['max'] if row['max']!=row['default'] else row['min']
        changed=source_vertices(v+d*(t-row['default']))
        require(np.any(changed!=sv) and np.array_equal(changed[locks],sv[locks]),'CONTROL_NO_F32_RESPONSE')
        responses.append(dict(id=row['id'],nonzero_vertices=int(np.any(changed!=sv,axis=1).sum())))
    groups=c['groups'];names=[x['name'] for x in groups]
    require(len(set(names))==len(names),'GROUP_NAMES_DUPLICATED')
    for row in groups:
        require(all(type(x)is int and 0<=x<len(v) for x in row['indices']) and len(set(row['indices']))==len(row['indices']),'GROUP_INDICES')
    if not fixture_only:
        # Deliberately fail-closed. This stage has no accepted 2D/3D interface
        # selection, no candidate triangulation and no whole-bank spatial gate.
        # Removing this blocker requires a NEW independently reviewed preparation,
        # never a CLI flag, a report boolean, or the parent's scheduling token.
        raise Rejected('SPATIAL_IMPLEMENTATION_UNRESOLVED: no approved continuous interface/whole-bank candidate gate in build-v1')
    return dict(passed=True,launch_allowed=False,fixture_only=True,topology=topo,control_responses=responses,
                welded_vertices=len(v),triangles=len(f),render_corner_count=3*len(f),native_run=False)

def validate_raw(raw,pid,candidate=None,binding=None):
    """Full array checks for captured real native data; no trusted passed field.

    Not exercised with real native data in preparation. A real acceptance stays
    blocked at check_candidate until the outstanding spatial implementation exists.
    """
    c=read(CANDIDATE_PATH) if candidate is None else candidate
    check_candidate(c)
    require(raw['version']==VERSION and type(raw['pid'])is int and raw['pid']==pid and pid>0,'RAW_IDENTITY_PID')
    require(raw['blender_version']==[4,5,14],'NATIVE_VERSION')
    require(len(raw['cpu_affinity'])==2 and len(set(raw['cpu_affinity']))==2,'CPU2')
    require(Path(raw['opened_filepath']).resolve()==SOURCE.resolve(),'ACTUAL_OPENED_SOURCE')
    m=raw['mesh'];v=finite_array(m['vertices'],(len(c['vertices_world']),3),'RAW_VERTICES')
    f=finite_array(m['faces'],(len(c['faces']),3),'RAW_FACES',True)
    require(np.array_equal(v,source_vertices(c['vertices_world'])) and np.array_equal(f,c['faces']),'ACTUAL_F32_GEOMETRY')
    p=finite_array(m['polygon_normals'],(len(f),3),'RAW_POLYGON_NORMALS')
    n=finite_array(m['corner_normals'],(len(f)*3,3),'RAW_CORNER_NORMALS')
    require(np.array_equal(p,p.astype('<f4').astype(float)) and np.array_equal(n,n.astype('<f4').astype(float)),'NORMAL_F32')
    exact=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);exact/=np.linalg.norm(exact,axis=1)[:,None]
    require(np.max(np.abs(exact-p))<=NORMAL_EPS and np.max(np.abs(np.linalg.norm(p,axis=1)-1))<=NORMAL_EPS,'ACTUAL_OUTWARD_NORMALS')
    require(m['polygon_loop_counts']==[3]*len(f) and m['polygon_loop_starts']==list(range(0,len(f)*3,3)) and m['loop_vertex_indices']==f.ravel().tolist(),'EXACT_LOOP_MAP')
    require(np.array_equal(n,np.repeat(p,3,axis=0)) and m['flat']==[True]*len(f),'FLAT_ACTUAL_NORMALS')
    require(m['material_indices']==[0]*len(f) and len(m['material_slots'])==1,'MATERIAL_BINDING')
    require(raw['external_libraries']==[] and raw['external_images']==[],'NO_EXTERNAL_DEPENDENCIES')
    return dict(passed=True,actual_native_normals=True,world_acceptance=False,visual_acceptance=False)

if __name__=='__main__':
    print(json.dumps({'version':VERSION,'engine_started':False,'status':'no-op; build-v1 spatial preparation is blocked'},indent=2))
