"""Twelve existing proxy hits checked against actual source GLB triangles."""
from pathlib import Path
import json,struct,math
import numpy as np
R=Path(__file__).resolve().parents[1]
RUN=R/'captures/validation_runs/water-34d-20260909T000325Z-9d52dcd583c84d04a34254a8eab8e9e3'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
source=(R/'reviews/round-32b-asset-footprint-decoder.py').read_text(encoding='utf-8-sig')
source=source.replace("    assert prim.get('mode',4)==4;", "    mat=doc['materials'][prim['material']]\n    if mat.get('alphaMode','OPAQUE')!='OPAQUE' or 'Lamp core' in mat.get('name','') or 'glass' in mat.get('name','').lower():continue\n    assert prim.get('mode',4)==4;")
exec(source,globals())
blender=asset_world_triangles(R/'assets/models/lighthouse.glb')
local=blender[:,:,[0,2,1]]*np.array([1,1,-1])
em=read(RUN/'images/actual-emitter-reflection.json');d=read(RUN/'images/night-reference.png.json')
placements={x['island']:x for x in d['placements'] if x['kind']=='lighthouse'}
samples=[]
for e in em['emitters'][:4]:
    island=e['light_node'].split('Lighthouse_')[1].split('/')[0];p=placements[island]
    c,s=math.cos(p['yaw']),math.sin(p['yaw']);rot=np.array([[c,0,s],[0,1,0],[-s,0,c]])
    tri=local@rot.T+np.array(p['position']);origin=np.array(e['emitter_center'])
    hits=[x for x in e['occlusion_hits'] if 'Lighthouse_'+island+'OpaqueReflectionCaster' in x['collider']]
    for k in [0,len(hits)//2,len(hits)-1]:
        hit=hits[k];az=((hit['x']+.5)/64-.5)*2*math.pi;down=(hit['y']+.5)/32
        direction=np.array([math.cos(az)*math.sqrt(1-down*down),-down,math.sin(az)*math.sqrt(1-down*down)])
        edge1=tri[:,1]-tri[:,0];edge2=tri[:,2]-tri[:,0];h=np.cross(np.broadcast_to(direction,edge2.shape),edge2)
        det=np.einsum('ij,ij->i',edge1,h);valid=np.abs(det)>1e-12
        inv=np.zeros_like(det);inv[valid]=1/det[valid];q0=origin-tri[:,0]
        u=np.einsum('ij,ij->i',q0,h)*inv;q=np.cross(q0,edge1);v=q@direction*inv;t=np.einsum('ij,ij->i',edge2,q)*inv
        good=valid&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(t>1e-6)
        nearest=float(t[good].min()) if good.any() else None
        samples.append({'emitter_index':e['index'],'pixel':[hit['x'],hit['y']],'actual_collider':hit['collider'],'actual_distance_m':hit['distance_m'],'independent_glb_opaque_triangles':len(tri),'independent_nearest_distance_m':nearest,'absolute_error_m':abs(nearest-hit['distance_m']) if nearest is not None else None})
report={'scope':'Twelve existing caster-hit directions against actual opaque source GLB transformed by recorded tower pose; not full world ray visibility.', 'samples':samples,'all_within_2mm':all(x['absolute_error_m'] is not None and x['absolute_error_m']<.002 for x in samples)}
(R/'reviews/34d-opaque-hit-sample-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
main=read(R/'reviews/34d-water-independent-technical.json');main['bounded_opaque_source_hit_samples']=report
main['checks']['twelve_opaque_source_hit_samples_within_2mm']=report['all_within_2mm'];main['bounded_technical_checks_passed']=all(main['checks'].values())
(R/'reviews/34d-water-independent-technical.json').write_text(json.dumps(main,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'pass':report['all_within_2mm'],'max_error_m':max((x['absolute_error_m'] or 0) for x in samples),'samples':samples},indent=2))
