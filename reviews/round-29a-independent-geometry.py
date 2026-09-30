from pathlib import Path
import json,struct,hashlib,collections,math
import numpy as np
from shapely.geometry import Polygon,MultiPoint,Point
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
NEW=R/'captures/lantern_island_study_29a'
OLD=R/'captures/lantern_islands_study_20l/island_c.glb'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def glb(p):
    data=p.read_bytes();assert data[:4]==b'glTF';i=12;j=None;b=None
    while i<len(data):
        n,k=struct.unpack_from('<II',data,i);chunk=data[i+8:i+8+n];i+=8+n
        if k==0x4e4f534a:j=json.loads(chunk)
        elif k==0x004e4942:b=chunk
    def acc(i):
        a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];nc={'SCALAR':1,'VEC3':3}[a['type']];stride=v.get('byteStride',np.dtype(dt).itemsize*nc)
        return np.ndarray((a['count'],nc),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,np.dtype(dt).itemsize)).copy()
    out={}
    for node in j['nodes']:
        if 'mesh' not in node:continue
        assert 'matrix' not in node and node.get('translation',[0,0,0])==[0,0,0] and node.get('scale',[1,1,1])==[1,1,1] and node.get('rotation',[0,0,0,1])==[0,0,0,1]
        ts=[]
        for p in j['meshes'][node['mesh']]['primitives']:
            assert p.get('mode',4)==4
            v=acc(p['attributes']['POSITION']);v=v[:,[0,2,1]]*np.array([1,-1,1]);idx=acc(p['indices']).ravel().reshape(-1,3);ts.extend(v[idx])
        out[node['name']]=np.array(ts)
    return out
def pointkey(p):return tuple(round(float(v),5) for v in p)
def tri_key(t):return tuple(sorted(pointkey(p) for p in t))
def counter(ts):return collections.Counter(tri_key(t) for t in ts)
old=glb(OLD);new=glb(NEW/'island_c.glb');e=json.loads((NEW/'geometry-evidence.json').read_text());n=e['new']
path_name='island_c terrain fitted keeper paths';terrain_name='island_c grass and exposed rock terrain';core_name='island_c faulted bedrock'
assert n[path_name]==e['old']['path'];assert n[terrain_name]==e['old']['terrain']
checks={}
for role,needle in [('path','footpath'),('terrain','grass')]:
    names=[k for k in old if needle in k.lower()];assert len(names)==1,names
    k=names[0];assert counter(old[k])==counter(new[k]);checks[role]={'mesh':k,'actual_glb_triangles':len(new[k]),'triangles_unchanged_at_1e_5_m':True}
path_ts=new[checks['path']['mesh']];norm=np.cross(path_ts[:,1]-path_ts[:,0],path_ts[:,2]-path_ts[:,0]);norm/=np.linalg.norm(norm,axis=1)[:,None];top=path_ts[norm[:,2]>.5];assert len(top)==259
road=unary_union([Polygon(t[:,:2]) for t in top]);pads=[Polygon(p) for p in e['protection']['pads']];trees=[Point(p) for p in e['protection']['trees']]
alltris=counter(np.concatenate(list(new.values())));allpoints={pointkey(p) for t in np.concatenate(list(new.values())) for p in t}
crags=[]
for name,obj in n.items():
    if name in [path_name,terrain_name,core_name]:continue
    verts=np.array(obj['vertices']);polys=obj['polygons'];assert all(len(p)==3 for p in polys)
    assert all(pointkey(v) in allpoints for v in verts);assert not (counter(verts[np.array(polys)])-alltris)
    shape=MultiPoint(verts[:,:2]).convex_hull
    crags.append({'name':name,'actual_export_all_vertices_and_faces_present':True,'road_gap_m':shape.distance(road),'pad_gap_m':min(shape.distance(p) for p in pads),'tree_axis_gap_m':min(shape.distance(t) for t in trees),'min_z_m':float(verts[:,2].min()),'max_z_m':float(verts[:,2].max())})
assert len(crags)==24
v0=np.array(e['old']['core']['vertices']);v1=np.array(n[core_name]['vertices']);changed=np.flatnonzero(np.any(v0!=v1,axis=1)).tolist();assert changed==list(range(36,72));assert n[core_name]['polygons']==e['old']['core']['polygons']
report={'scope':'Independent actual GLB decode plus emitted source geometry cross-check. No Blender/GPU rerun; no full walking or exact tree branch clearance claim. Native reopened gate remains separate evidence.','files':{str(p.relative_to(R)):sha(p) for p in [OLD,NEW/'island_c.glb',NEW/'island_c.blend',NEW/'geometry-evidence.json']},'actual_glb_preservation':checks,'path_top_triangles':len(top),'path_max_slope_deg':float(np.degrees(np.arccos(norm[norm[:,2]>.5,2])).max()),'path_source_exact':True,'terrain_source_exact':True,'changed_core_vertex_indices':changed,'core_topology_unchanged':True,'crags':crags,'min_road_gap_m':min(c['road_gap_m'] for c in crags),'min_padded_foundation_gap_m':min(c['pad_gap_m'] for c in crags),'min_tree_axis_gap_m':min(c['tree_axis_gap_m'] for c in crags)}
assert report['min_road_gap_m']>=1.2 and report['min_padded_foundation_gap_m']>=.2 and report['min_tree_axis_gap_m']>=1.5
(R/'reviews/round-29a-independent-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['crags','files','changed_core_vertex_indices']},indent=2))
