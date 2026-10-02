"""Pure shared source contract. No engine imports, launches, or project writes."""
import hashlib, json, math, struct, gzip, base64
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PREP=HERE.parent/'preparation-v1'
VERSION='north-ridge62-build-v1'
ORIGIN=[-2560.0,0.0,-4608.0]
TILES=['Ground_-4_-7','Ground_-3_-7','Ground_-4_-6','Ground_-3_-6']
PREPARATION_SHA='12d9f492d3ae1251d37f6b8b94e9e5877eb85dd96f723f97542a5c4885818702'
BLENDER=ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
BLENDER_SHA='050c02562f81fe80ba616a80198fa02d381e60f8b61b8d39add881f4bca0d7d8'
SOURCE=HERE/'north-ridge62.blend'
MATERIALS=[dict(name='R62_Grass',color=[.23,.32,.13,1.],roughness=.96),dict(name='R62_Rock',color=[.30,.34,.37,1.],roughness=.94),dict(name='R62_Snow',color=[.78,.84,.87,1.],roughness=.90)]
TEXTS=['BINDINGS62.json','CONTRACT62.py','REBUILD62.py','README62.txt']

def require(ok,message):
    if not ok:raise ValueError(message)
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
def digest(v,dtype='<f4'):return hashlib.sha256(np.asarray(v,dtype=dtype).tobytes()).hexdigest()
def f32(v):return np.asarray(v,dtype='<f4').astype(float)
def local(xyz):
    p=np.asarray(xyz,float)-ORIGIN
    return np.column_stack((p[:,0],-p[:,2],p[:,1]))
def world(xyz):
    p=np.asarray(xyz,float)
    return np.column_stack((p[:,0],p[:,2],-p[:,1]))+ORIGIN

def evaluate(binding,targets=None):
    controls=binding['controls'];targets=np.array([c['target_y'] for c in controls] if targets is None else targets,float)
    require(targets.shape==(27,) and np.isfinite(targets).all(),'27 finite control targets')
    require(np.array_equal(targets[:12],np.array([c['target_y'] for c in controls[:12]])),'Boundary controls fixed')
    base=np.asarray(binding['before_xyz'],float);out=base.copy()
    delta=np.maximum(0.,targets-np.array([c['base_y'] for c in controls]))
    ids=np.asarray(binding['control_ids'],int);weights=np.asarray(binding['weights64'],float)
    displacement=np.sum(weights*delta[ids],axis=1)*np.asarray(binding['collar64'],float)
    changed=displacement>1e-6
    out[changed,1]=f32(np.array(binding['canonical_base_y'])[changed]+displacement[changed])
    return out

def materials(vertices,faces):
    a=np.asarray(vertices,float)[np.asarray(faces,int)];n=np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]);n/=np.linalg.norm(n,axis=1)[:,None]
    slope=np.degrees(np.arccos(np.clip(n[:,2],-1,1)));y=a[:,:,2].mean(axis=1)
    return np.where((y>=540)&(slope<67),2,np.where((y>=390)|((y>=130)&(slope>=26)),1,0)).astype(int).tolist()

def expected(binding,targets=None):
    xyz=evaluate(binding,targets);verts=f32(local(xyz));faces=np.asarray(binding['master_faces_blender'],int)
    return dict(world_xyz=xyz.tolist(),vertices=verts.tolist(),faces=faces.tolist(),materials=materials(verts,faces))

def check_binding(b):
    check_authority(b)
    require(b['version']==VERSION and b['origin_godot']==ORIGIN,'Contract identity/frame')
    require(len(b['controls'])==27 and len(b['controls'][12:])==15,'27 controls /15 relief')
    require([r['name'] for r in b['tiles']]==TILES,'Only four tiles')
    n=len(b['before_xyz']);f=np.array(b['master_faces_blender'],int)
    require(n>0 and f.shape==(8192,3) and f.min()>=0 and f.max()<n,'Original four terrain topologies')
    for key in ['control_ids','weights64','collar64','canonical_base_y','candidate_y','changed']:
        require(len(b[key])==n,'Point binding count '+key)
    require(np.array(b['control_ids']).shape==(n,3),'Three control barycentric slots')
    w=np.array(b['weights64']);require(np.isfinite(w).all() and (w>=-1e-8).all(),'Finite barycentric weights')
    sums=w.sum(axis=1);require(np.all((abs(sums)<1e-12)|(abs(sums-1)<1e-10)),'Barycentric nonzero rows normalized')
    collar=np.asarray(b['collar64']);require(np.isfinite(collar).all() and np.all((collar>=0)&(collar<=1)),'Collar within zero/one')
    for key,pin in AUTHOR_FIELD_PINS.items():require(digest(b[key],pin['dtype'])==pin['sha256'],'Frozen full-precision controller field '+key)
    q=expected(b);before=np.asarray(b['before_xyz']);after=np.asarray(q['world_xyz'])
    require(f32(before[:,[0,2]]).tobytes()==f32(after[:,[0,2]]).tobytes(),'XZ exact')
    require(f32(after[:,1]).tobytes()==f32(b['candidate_y']).tobytes(),'Evaluated frozen candidate float32 Y')
    require(f32(world(q['vertices'])).tobytes()==f32(after).tobytes(),'Local origin/axis float32 roundtrip')
    require(sum(r['changed_original_triangles'] for r in b['tiles'])==2479,'2479 changed original triangles')
    require(sum(r['changed_unique_original_coordinates'] for r in b['tiles'])==1246,'1246 per-tile frozen overrides')
    require(all(np.cross(np.array(q['vertices'])[f[:,1]]-np.array(q['vertices'])[f[:,0]],np.array(q['vertices'])[f[:,2]]-np.array(q['vertices'])[f[:,0]])[:,2]>0),'Godot clockwise reversed to Blender CCW upward')
    require(b['native_vertex_index_mapping_proved'] is True,'Offline source GPU index witness required')
    require([len(t['master_vertex_ids'])for t in b['tiles']]==[6144,6144,6058,6009],'Retain original attribute split vertices')
    for tile in b['tiles']:
        require(np.array(tile['faces_blender'])[:,[0,2,1]].ravel().tolist()==tile['original_source_index_sequence'],'Original GPU index order retained')
        require(digest(np.array(tile['original_color_rgba8'])/255.)==digest(tile['original_color_float32']),'Original RGBA8 conversion exact')
    return dict(passed=True,master_vertices=n,original_triangles=8192,changed_triangles=2479,per_tile_overrides=1246,positions_sha256=digest(q['vertices']),triangles_sha256=digest(f,'<i4'),candidate_world_y_sha256=digest(after[:,1]),source_only=True,world_integration_allowed=False)

def validate_raw(raw,b):
    require(raw['version']==VERSION and raw['blender_version']==[4,5,14] and raw['pid']>0,'Actual pinned native identity')
    require(len(raw['cpu_affinity'])==2,'Actual native CPU2')
    exp=expected(b);names=['R62_MASTER_EVALUATED']+['R62_'+x for x in TILES]
    require([x['name'] for x in raw['terrain']]==names,'One master + four derivative objects')
    for i,row in enumerate(raw['terrain']):
        if i==0:idx=list(range(len(exp['vertices'])));faces=exp['faces'];mats=exp['materials']
        else:
            t=b['tiles'][i-1];idx=t['master_vertex_ids'];faces=t['faces_blender'];mats=[exp['materials'][k] for k in t['master_face_ids']]
        require(digest(row['vertices'])==digest(np.array(exp['vertices'])[idx]),'Native exact float32 geometry '+row['name'])
        require(row['faces']==faces and row['material_indices']==mats,'Exact topology/material-region mapping '+row['name'])
        require(row['flat']==[True]*len(faces),'Every face flat')
        require(row['matrix_world']==np.eye(4).tolist(),'No native transform drift')
        require(row['source_properties']==({} if i==0 else dict(derived_from='R62_MASTER_EVALUATED',source_resource=b['tiles'][i-1]['source_resource'],original_mapping_scope=b['mapping_scope'])),'Native source resource metadata')
        require(row['material_slots']==[m['name'] for m in MATERIALS],'Editable material slots')
        require(row['attributes']['source_master_vertex']==idx,'Source master vertex mapping')
        require(row['attributes']['original_source_vertex']==([-1]*len(idx) if i==0 else list(range(len(idx)))),'Original GPU vertex slot mapping')
        require(digest(row['attributes']['original_color'])==digest([[0.,0.,0.,0.]]*len(idx) if i==0 else b['tiles'][i-1]['original_color_float32']),'Original RGBA native authoring data')
        require(digest(row['attributes']['original_local'])==digest([[0.,0.,0.]]*len(idx) if i==0 else b['tiles'][i-1]['original_source_local_xyz']),'Original source-local XYZ preserved, never inferred by subtracting world origin')
        require(digest(row['attributes']['original_world'])==digest(np.array(b['before_xyz'])[idx]),'Original source XYZ attribute bytes')
        require(digest(row['attributes']['collar'])==digest(np.array(b['collar64'])[idx]),'Native collar attribute bytes')
        require(digest(row['attributes']['canonical_base_y'])==digest(np.array(b['canonical_base_y'])[idx]),'Native canonical original Y bytes')
        require(row['attributes']['changed']==[b['changed'][k] for k in idx],'Native changed-mask attribute')
        require(row['attributes']['source_tile']==(b['master_tile_ids'] if i==0 else [i-1]*len(faces)) and row['attributes']['material_region']==mats,'Native tile/material-region face attributes')
        expected_weights=np.zeros((len(idx),27),np.float32)
        for j,k in enumerate(idx):
            for ci,weight in zip(b['control_ids'][k],b['weights64'][k]):expected_weights[j,ci]+=max(0.,weight)
        require(row['group_names']==[c['name'] for c in b['controls']],'27 named weight groups')
        require(digest(row['weights'])==digest(expected_weights),'Every native barycentric weight float32 byte')
        require(row['attributes']['source_triangle']==list(range(len(faces))) if i else row['attributes']['source_triangle']==b['master_source_triangles'],'Original triangle mapping')
        n=np.array(row['polygon_normals']);cn=np.array(row['corner_normals']);v=np.array(row['vertices']);ff=np.array(faces)
        geom=np.cross(v[ff[:,1]]-v[ff[:,0]],v[ff[:,2]]-v[ff[:,0]]);geom/=np.linalg.norm(geom,axis=1)[:,None]
        require(np.max(np.abs(n-geom))<=3e-5,'Polygon geometric normal gate')
        require(cn.shape==(len(faces)*3,3),'Complete native corner normals')
        cn=cn.reshape(-1,3,3);require(digest(cn[:,0])==digest(cn[:,1])==digest(cn[:,2]),'Actual per-face corner normals flat')
        require(np.max(np.abs(cn[:,0]-geom))<=3e-5,'Corner geometric normal gate, no polygon/corner bit-equality assumption')
    require(raw['control_vertices']==f32(local([[c['xz'][0],c['target_y'],c['xz'][1]] for c in b['controls']])).tolist(),'Actual master control points')
    require(raw['control_faces']==b['control_faces_blender'] and raw['control_matrix_world']==np.eye(4).tolist(),'Master controller triangulation and identity object transform')
    require(raw['semantic_handles']==[dict(name=c['name'],location=f32(local([[*c['xz'][:1],c['target_y'],c['xz'][1]]]))[0].tolist(),lock_location=[True,True,False],lock_rotation=[True]*3,lock_scale=[True]*3) for c in b['controls'][12:]],'15 height-only semantic handles')
    require(raw['embedded_binding_sha256']==hashlib.sha256(json.dumps(b,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),'Embedded full precision binding')
    require(raw['embedded_text_names']==TEXTS,'Editable source texts')
    expected_text_hashes={'BINDINGS62.json':hashlib.sha256(json.dumps(b,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),'CONTRACT62.py':sha(HERE/'contract62.py'),'REBUILD62.py':sha(HERE/'rebuild62.py'),'README62.txt':sha(HERE/'SOURCE_README.txt')}
    require(raw['embedded_text_sha256']==expected_text_hashes,'Actual embedded edit code and exact full-precision recipe')
    for actual,planned in zip(raw['materials'],MATERIALS):
        require(actual['name']==planned['name'] and actual['use_nodes'] and actual['metallic']==0,'Native editable principled material')
        require(digest(actual['base_color'])==digest(planned['color']) and digest([actual['roughness']])==digest([planned['roughness']]),'Native material values')
    require(len(raw['materials'])==3,'Exactly rock/grass/snow materials')
    validate_cameras(raw['cameras'],b['views'])
    require(raw['render_settings']==dict(engine='CYCLES',resolution=[1179,664],percentage=100,pixel_aspect=[1.,1.],threads=2,samples=8,use_denoising=False),'Fixed full-size CPU source render budget settings')
    require(not raw['external_libraries'] and not raw['image_dependencies'],'Self-contained source without external assets')
    expected_objects=sorted(['R62_MASTER_CONTROL','R62_MASTER_EVALUATED','R62 neutral key']+['R62_'+x for x in TILES]+['R62_CAMERA_'+v['name'] for v in b['views']]+['R62_HANDLE_'+x['name'] for x in b['controls'][12:]])
    require(raw['object_names']==expected_objects and len(raw['mesh_names'])==6,'No extra world objects or topology sources')
    require(raw['scene_flags']==dict(source_version=VERSION,origin_godot_json=json.dumps(ORIGIN),world_integration_allowed=False,source_material_study_only=True,weather_acceptance=False,visual_acceptance=False,auto_rebuild=False,edited_after_frozen_build=False),'Source-only scene flags')
    return dict(passed=True,geometry=check_binding(b),exact_native_float32_arrays=True,raw_normals_geometric_and_flat_passed=True,world_integration_allowed=False,visual_acceptance=False)

def expected_camera_matrix(view):
    eye=local([view['eye']])[0];target=local([view['target']])[0]
    forward=target-eye;forward/=np.linalg.norm(forward)
    right=np.cross(forward,[0.,0.,1.]);right/=np.linalg.norm(right)
    up=np.cross(right,forward)
    out=np.eye(4);out[:3,0]=right;out[:3,1]=up;out[:3,2]=-forward;out[:3,3]=eye
    return out

def validate_cameras(actual,views):
    require(len(actual)==len(views)==4,'Exactly four fixed source cameras')
    for row,view in zip(actual,views):
        require(row['name']==view['name'] and row['declared_view']==view,'Unchanged declared original/supplemental view')
        require(row['type']=='PERSP' and row['sensor_fit']=='VERTICAL' and row['sensor_height']==32,'Vertical FOV camera setup')
        require(np.max(np.abs(np.array(row['matrix_world'])-expected_camera_matrix(view)))<=3e-6,'Actual camera position/orientation, no retarget')
        require(abs(row['angle_y']-math.radians(view['fov']))<=2e-7,'Actual original vertical FOV')
        require(abs(row['lens']-16/math.tan(math.radians(view['fov']/2)))<=2e-6,'Actual camera focal length')
        require(abs(row['clip_start']-.1)<1e-8 and row['clip_end']==10000,'Camera clipping')


MAPPING_SUMMARY_SHA='72b6d2d6ad1c7623d3a4e81a30c2daf20641d145f97a12605936998c1a36a371'

def mapping_authority():
    directory=HERE/'offline-mapping';summary=read(directory/'mapping-summary.json')
    require(sha(directory/'mapping-summary.json')==MAPPING_SUMMARY_SHA,'Fixed independent four-mesh mapping authority')
    for name,pin in summary['artifacts'].items():
        path=directory/name;require(path.stat().st_size==pin['bytes'] and sha(path)==pin['sha256'],'Original mapping artifact identity '+name)
    return [json.loads(gzip.decompress((directory/(name+'.mapping.json.gz')).read_bytes()))for name in TILES]

def check_authority(b):
    require(sha(PREP/'FINAL_SHA256.json')==PREPARATION_SHA,'Frozen preparation identity')
    freeze=read(PREP/'FINAL_SHA256.json')
    for name in ['candidate-plan.json','candidate-vertex-y.json']:
        require(sha(PREP/name)==freeze['files'][name]['sha256'],'Independent frozen proposal '+name)
    plan=read(PREP/'candidate-plan.json');patch=read(PREP/'candidate-vertex-y.json')
    require(b['controls']==plan['controls'] and b['source_pins']==plan['source_pins'],'Exact frozen 27 control definitions and source pins')
    control_positions=local([[x['xz'][0],x['target_y'],x['xz'][1]]for x in plan['controls']]);control_faces=[]
    for face in plan['control_triangles']:
        a,bp,cc=control_positions[face];control_faces.append(face if np.cross(bp-a,cc-a)[2]>0 else [face[0],face[2],face[1]])
    require(b['control_faces_blender']==control_faces,'Frozen shared control triangulation')
    intake=ROOT/'source-assets/north-ridge62-intake/plan.json'
    require(sha(intake)==plan['source_pins'][str(intake.relative_to(ROOT))]['sha256'],'Frozen original camera intake')
    views=[dict(name=key,kind='fixed_reference_source_geometry_only',**v)for key,v in read(intake)['fixed_reference_views'].items()]
    views += [dict(name='side',kind='diagnostic_only',eye=[-3840,690,-4740],target=[-2490,340,-4730],fov=55),dict(name='back',kind='diagnostic_only',eye=[-2460,790,-6060],target=[-2510,350,-4660],fov=55)]
    require(b['views']==views,'Original reference and fixed diagnostic cameras')
    mappings=mapping_authority();before=[];lookup={};faces=[];tile_faces=[]
    for mapping in mappings:
        rows=mapping['source_vertices'];indices=mapping['index_sequence'];mf=[]
        for k in range(0,len(indices),3):
            face=[]
            for source_id in indices[k:k+3]:
                key=tuple(rows[source_id]['survey_world_xyz_json'])
                if key not in lookup:lookup[key]=len(before);before.append(list(key))
                face.append(lookup[key])
            mf.append([face[0],face[2],face[1]])
        tile_faces.append(mf);faces.extend(mf)
    require(b['before_xyz']==before and b['master_faces_blender']==faces,'Original ordered survey source/master mapping')
    candidate=np.array(before,float)[:,1].tolist();changed=[False]*len(before)
    for patch_tile in patch['tiles']:
        for row in patch_tile['vertex_y_overrides']:
            i=lookup[tuple(row['before_xyz'])];candidate[i]=row['candidate_y'];changed[i]=True
    require(b['candidate_y']==candidate and b['changed']==changed,'Every frozen changed/unchanged source Y membership')
    cursor=0
    for ti,(tile,mapping,mf) in enumerate(zip(b['tiles'],mappings,tile_faces)):
        rows=mapping['source_vertices'];source=mapping['source'];ids=[lookup[tuple(row['survey_world_xyz_json'])]for row in rows]
        require(tile['master_vertex_ids']==ids and tile['master_face_ids']==list(range(cursor,cursor+2048)),'Every derived source slot and face maps to shared master')
        cursor+=2048
        require(np.asarray(ids)[np.asarray(tile['faces_blender'])].tolist()==mf,'Every tile face equals its original master face')
        require(tile['original_source_local_xyz']==[row['source_local_xyz']for row in rows],'True original local positions')
        require(tile['original_color_rgba8']==[row['source_color_rgba8']for row in rows] and tile['original_color_float32']==[row['source_color_rgba_normalized_float32']for row in rows],'Original split-vertex colors')
        require(tile['original_surface_identity']==source,'Original resource/format/transform identity')
        require(tile['source_resource']==source['resource'] and tile['source_node']==source['survey_node'] and tile['source_origin']==source['world_transform_columns'][9:],'Original resource/node/origin labels')
        require(tile['changed_original_triangles']==plan['tiles'][tile['name']]['changed_original_triangles'] and tile['changed_unique_original_coordinates']==plan['tiles'][tile['name']]['unique_changed_vertices'],'Exact per-tile mutation counts')
        require(tile['original_source_index_sequence']==mapping['index_sequence'],'Original source index sequence')
        require(set(tile['original_packed_storage_base64'])==set(source['packed_payloads']),'All original packed channels')
        for key,encoded in tile['original_packed_storage_base64'].items():
            raw=base64.b64decode(encoded,validate=True);pin=source['packed_payloads'][key]
            require(len(raw)==pin['bytes'] and hashlib.sha256(raw).hexdigest()==pin['sha256'],'Original packed payload bytes')
    require(b['master_source_triangles']==list(range(2048))*4 and b['master_tile_ids']==[i for i in range(4)for _ in range(2048)],'Full master source triangle/tile ownership')

AUTHOR_FIELD_PINS={'control_ids': {'dtype': '<i4', 'sha256': '49dbd83ccf426d5b339f396bcf183993466eb1b65ce4252e366b44a9de31ced9'}, 'weights64': {'dtype': '<f8', 'sha256': '3344946c130ba7a15677e4f17a4d4cb21502cff423f08a04e5c32b7a5c0f1a62'}, 'collar64': {'dtype': '<f8', 'sha256': 'fd93e0ede94522144e57c5875531e91978dab820812fc8d3aa122e8fa9150fb1'}, 'canonical_base_y': {'dtype': '<f8', 'sha256': '27ee437e60c4391d99957f3fc1871a570078a4a60d7ebe3f7469af65a809409f'}}
