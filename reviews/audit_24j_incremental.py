"""Bounded independent increment review; no asset writes."""
from pathlib import Path
import json,hashlib,struct
from collections import Counter
import numpy as np
import shapely
from shapely.geometry import Polygon,Point,LineString
R=Path(r'E:\FeiTing'); old=json.loads((R/'captures/village_paving_design_24i/paving.json').read_text()); new=json.loads((R/'captures/village_paving_design_24j/paving.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out={'scope':'Independent bounded 24i to 24j JSON and actual GLB increment check. Not GPU/visual/full walking acceptance.','changed_solids':[],'other_group_changes':[],'assets':[]}
def poly(s):return shapely.union_all([Polygon([s['vertices_xz'][i] for i in t]) for t in s['cap_triangles']])
unchanged=0
for a,b in zip(old['groups'],new['groups']):
    assert len(a['solids'])==len(b['solids'])
    out['other_group_changes'].append({'group':a['name'],'keys':[k for k in set(a)|set(b) if k!='solids' and a.get(k)!=b.get(k)]})
    for i,(s,t) in enumerate(zip(a['solids'],b['solids'])):
        if s==t:unchanged+=1;continue
        p,q=poly(s),poly(t); delta=p.symmetric_difference(q)
        ds=Counter(x for edge in t['boundary_edges'] for x in edge)
        distances=[]
        for ri,coords in enumerate(b['routes']):
            line=LineString(coords)
            for offset in [0,-.6,.6]:distances.append({'route':ri,'offset':offset,'distance_m':delta.distance(line.offset_curve(offset) if offset else line)})
        out['changed_solids'].append({'group':a['name'],'index':i,'name':t['name'],'changed_keys':[k for k in set(s)|set(t) if s.get(k)!=t.get(k)],'added_area_m2':q.difference(p).area,'removed_area_m2':p.difference(q).area,'change_bounds_world_xz':delta.bounds,'all_boundary_degrees_two':all(n==2 for n in ds.values()),'nearest_profile':min(distances,key=lambda d:d['distance_m']),'nearest_entry_polygon_distance_m':min(delta.distance(shapely.from_geojson(e['polygon_geojson'])) for e in b['entries'])})
out['unchanged_solids']=unchanged
gate=json.loads((R/'reviews/round-24j-village-paving-native-check.json').read_text())
out['gate_passed']=gate['passed']
for asset in gate['assets']:
    folder=R/'captures/village_paving_study_24j'; raw=(folder/(asset['asset']+'.glb')).read_bytes(); n=struct.unpack_from('<I',raw,12)[0]; doc=json.loads(raw[20:20+n]); blob=raw[28+n:]
    def acc(idx):
        a=doc['accessors'][idx];v=doc['bufferViews'][a['bufferView']];dtype={5126:'<f4',5125:'<u4',5123:'<u2'}[a['componentType']];dims={'VEC3':3,'SCALAR':1}[a['type']];sz=np.dtype(dtype).itemsize
        return np.ndarray((a['count'],dims),dtype=dtype,buffer=blob,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dims*sz),sz)).copy()
    local_edges=[]; checked=0
    for node in doc['nodes']:
        if 'mesh' not in node:continue
        assert not any(k in node for k in ['matrix','translation','rotation','scale'])
        for prim in doc['meshes'][node['mesh']]['primitives']:
            v=acc(prim['attributes']['POSITION']); ff=acc(prim['indices']).reshape(-1,3); edgecount=Counter()
            for f in ff:
                tri=v[f]
                if np.min(np.linalg.norm(tri[:,[0,2]]-np.array([-39.105,-28.989]),axis=1))>.009:continue
                for i,j in [(0,1),(1,2),(2,0)]:
                    aa,bb=tri[i],tri[j]
                    if np.linalg.norm(aa[[0,2]]-np.array([-39.105,-28.989]))<=.009 and np.linalg.norm(aa[[0,2]]-bb[[0,2]])<1e-6 and abs(float(aa[1]-bb[1]))>.03:
                        edgecount[tuple(sorted((tuple(np.round(aa,5).tolist()),tuple(np.round(bb,5).tolist()))))]+=1
            for e,inc in edgecount.items():local_edges.append({'mesh':node.get('name'),'edge_local_xyz':e,'incident_triangles':inc})
    out['assets'].append({'name':asset['asset'],'blend_hash_matches_gate':sha(folder/(asset['asset']+'.blend'))==asset['source_sha256'],'glb_hash_matches_gate':hashlib.sha256(raw).hexdigest()==asset['glb_sha256'],'blend_sha256':asset['source_sha256'],'glb_sha256':asset['glb_sha256'],'gate_parts':len(asset['parts']),'local_vertical_edges_near_repair':local_edges})
out['design_copy_matches']=sha(R/'captures/village_paving_study_24j/paving-design.json')==sha(R/'captures/village_paving_design_24j/paving.json')
out['grading_failure']=json.loads((R/'captures/village_grading_study_24j/build-report.json').read_text())['parts'][0]
(R/'reviews/round-24j-village-paving-independent-increment-review.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
