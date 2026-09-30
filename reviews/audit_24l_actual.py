"""Actual GLB triangle intersection audit, independent of grading implementation."""
from pathlib import Path
from collections import Counter
import json,struct,hashlib,math
import numpy as np
import shapely
from shapely.geometry import Polygon,Point
R=Path(r'E:\FeiTing'); O=np.array([-2180.,0.,-1830.])
def load(path):
    raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);buf=raw[28+n:];result=[]
    def acc(idx):
        a=d['accessors'][idx];v=d['bufferViews'][a['bufferView']];dtype={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']];sz=np.dtype(dtype).itemsize;k={'VEC3':3,'SCALAR':1}[a['type']]
        return np.ndarray((a['count'],k),dtype=dtype,buffer=buf,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',sz*k),sz)).copy()
    for node in d['nodes']:
        if 'mesh' not in node:continue
        assert not any(k in node for k in ['translation','rotation','scale','matrix']),node
        for p in d['meshes'][node['mesh']]['primitives']:
            v=acc(p['attributes']['POSITION']).astype(float);tris=v[acc(p['indices']).reshape(-1,3)]
            material=d.get('materials',[{}])[p.get('material',0)].get('name','')
            for t in tris:result.append({'v':t,'node':node.get('name',''),'material':material})
    return result,hashlib.sha256(raw).hexdigest()
def vertices(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return list(g.exterior.coords)+[p for ring in g.interiors for p in ring.coords]
    if hasattr(g,'geoms'):return [p for part in g.geoms for p in vertices(part)]
    return list(g.coords)
def prepare(rows):
    polys=[];planes=[];source=[]
    for row in rows:
        v=row['v'];p=Polygon(v[:,[0,2]])
        if p.area<1e-10:continue
        if np.cross(v[1]-v[0],v[2]-v[0])[1]<=0:continue
        polys.append(p);planes.append(np.linalg.solve(np.column_stack([v[:,0],v[:,2],np.ones(3)]),v[:,1]));source.append(row)
    return polys,planes,shapely.STRtree(polys),source
old,oldsha=load(R/'captures/headland_study_23g/mainland_headland.glb'); new,newsha=load(R/'captures/village_grading_study_24l/mainland_headland.glb')
np_,nh,nt,nr=prepare(new);op,oh,ot,orr=prepare(old)
gate=json.loads((R/'reviews/round-24l-village-grading-native-check.json').read_text())
out={'scope':'Actual GLB geometry plus current source/gate SHA identity. Independent triangle-plane intersection maxima, not GPU/visual/full walk acceptance.','source_identity':{'old_glb_sha256':oldsha,'new_glb_sha256':newsha,'glb_matches_native_gate':newsha==gate['glb_sha256'],'blend_matches_native_gate':hashlib.sha256((R/'captures/village_grading_study_24l/mainland_headland.blend').read_bytes()).hexdigest()==gate['source_sha256']},'paving':[]}
for name in ['foreground','bay']:
    pavement,sha=load(R/('captures/village_paving_study_24j/village_'+name+'.glb')); topcaps=[r for r in pavement if np.cross(r['v'][1]-r['v'][0],r['v'][2]-r['v'][0])[1]>1e-9 and np.ptp(r['v'][:,1])<1e-5]
    worst=None;hits=0;over=0.;checked=0
    for cap in topcaps:
        p=Polygon(cap['v'][:,[0,2]]); y=float(np.mean(cap['v'][:,1]));checked+=1
        for ii in nt.query(p):
            inter=p.intersection(np_[ii])
            if inter.area<1e-10:continue
            pts=np.array(vertices(inter));vals=pts@nh[ii][:2]+nh[ii][2]-y;k=int(np.argmax(vals));penetration=float(vals[k]);hits+=1
            if penetration>.001:over+=inter.area
            if worst is None or penetration>worst['terrain_above_cap_m']:worst={'terrain_above_cap_m':penetration,'world_xz':(pts[k]+O[[0,2]]).tolist(),'cap_y':y,'terrain_y':float(vals[k]+y),'cap_material':cap['material'],'terrain_material':nr[ii]['material'],'intersection_area_m2':inter.area}
    row={'group':name,'actual_glb_sha256':sha,'top_cap_triangles_checked':checked,'terrain_cap_overlaps':hits,'worst':worst,'overlap_area_with_extreme_penetration_over_1mm_m2':over};out['paving'].append(row);print(json.dumps(row),flush=True)
    if worst and worst['terrain_above_cap_m']>.01:print('REJECTING COUNTEREXAMPLE',flush=True)

def facekey(row):return (row['material'],tuple(sorted(tuple(v) for v in row['v'])))
preserved=Counter(facekey(r) for r in new)
lower=[r for r in old if np.cross(r['v'][1]-r['v'][0],r['v'][2]-r['v'][0])[1]<=1e-10]
missing=Counter(facekey(r) for r in lower)-preserved
out['original_nonupward_faces']={'count':len(lower),'missing_exact_geometry_material_triangles':sum(missing.values())}
oldverts={tuple(v) for r in old for v in r['v']};newverts={tuple(v) for r in new for v in r['v']}
edges=Counter()
for r in orr:
    if 'buttress' in r['node'].lower():continue
    t=r['v']
    for a,b in zip(t,np.roll(t,-1,axis=0)):edges[tuple(sorted((tuple(a),tuple(b))))]+=1
border={v for e,n in edges.items() if n==1 for v in e}
out['upper_border']={'vertex_count':len(border),'missing_exact_vertices':len(border-newverts)}
run=R/'captures/validation_runs/village-paving-24l-20260908T133935Z-a85da8d179904470851864e01545b1c3/study-inputs'
for asset,path in [('keeper_house',run/'keeper_house.glb'),('fisher_cottage',run/'headland/fisher_cottage.glb'),('quay_workshop',run/'headland/quay_workshop.glb')]:
    rr,sha=load(path);print(asset,sorted(set((r['node'],r['material']) for r in rr)),flush=True)
out['status']='phase1 complete; actual foundation region comparison pending'
(R/'reviews/round-24l-village-grading-independent-review.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
