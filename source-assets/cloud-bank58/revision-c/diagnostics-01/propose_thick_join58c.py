"""ProposednativeL03/L04 shoulder thickening only. NoBlender or recoverybuild."""
import copy,json,sys
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;R=P.parent/'recovery-01';sys.path.insert(0,str(R));from triangle_checks58c import stations,vertical_hits
inputs=json.loads((R/'native-control-input58c.json').read_text());candidate=copy.deepcopy(inputs);changes=[]
# Broad3D upper-side swell around twoexacthomology loop regions. Noaddedfaces,
# planefills,normaldeletion,worldmodificationorheightfield construction.
for spec in candidate['controls']:
 if spec['id'] not in ['L03','L04']:continue
 old=np.array(spec['vertices']);v=old.copy();x,z=v[:,0],v[:,2]
 amplitude=180. if spec['id']=='L03' else 170.
 horizontal=np.maximum(0,1-((x-4055)/390)**2)**2*np.maximum(0,1-((z-4170)/480)**2)**2
 t=np.clip((v[:,1]-550)/180,0,1);vertical=t*t*(3-2*t);delta=amplitude*horizontal*vertical;v[:,1]+=delta
 changed=np.flatnonzero(delta>1e-10);spec['vertices']=v.tolist()
 changes.append(dict(control=spec['id'],parameters=dict(centre_xz=[4055,4170],radii_xz=[390,480],amplitude_m=amplitude,vertical_ramp_y=[550,730]),changed_vertex_ids=changed.tolist(),maximum_vertex_lift_m=float(delta.max()),old_world_bounds=[old.min(0).tolist(),old.max(0).tolist()],new_world_bounds=[v.min(0).tolist(),v.max(0).tolist()],delta_rows=[dict(vertex_id=int(i),before=old[i].tolist(),after=v[i].tolist()) for i in changed],below_y550_unchanged=bool(np.array_equal(old[old[:,1]<=550],v[old[:,1]<=550])),all_xz_and_faces_unchanged=True))
meshes=[(s['id'],np.array(s['vertices'])[np.array(s['faces'])]) for s in candidate['controls']];plan=json.loads((R/'authoring-plan58c.json').read_text());valleys=[]
for c in plan['valley_corridors']:
 rows=[];lo,hi=c['intended_floor_y_range_m']
 for station in stations(c):
  intervals=[]
  for name,tri in meshes:
   for q in vertical_hits(tri,station['world_xz'])['solid_intervals']:intervals.append(q)
  merged=[]
  for q in sorted(intervals,key=lambda r:-r['top_y_m']):
   if merged and q['top_y_m']>=merged[-1][1]:merged[-1][1]=min(merged[-1][1],q['bottom_y_m'])
   else:merged.append([q['top_y_m'],q['bottom_y_m']])
  top,bottom=merged[0] if merged else[None,None];rows.append(dict(station,intervals=merged,passed=bool(merged and lo<=top<=hi and top-bottom>=160)))
 valleys.append(dict(id=c['id'],passing_samples=sum(r['passed'] for r in rows),sample_count=len(rows),first_surface_range_m=[min(r['intervals'][0][0] for r in rows),max(r['intervals'][0][0] for r in rows)],minimum_first_thickness_m=min(r['intervals'][0][0]-r['intervals'][0][1] for r in rows),rows=rows))
out=dict(status='PROPOSAL ONLY; no recovery02 source build or modifications to anyexisting source',changes=changes,controls_unchanged_count=55,control_count=57,total_added_vertices=0,total_added_faces=0,original_corridor_gates_unchanged=True,pre_union_candidate_valleys=valleys,
 expected_effect='Lift curved upper-side density under the two nearP02/P03 bridge loops; build actual vertical overlap into lowerbody. Finalgenus0 andshape remain unproved until independentnewunionfresh.',not_expected_to_resolve='The separate tinycoarse15negativecavity nearL09/P05 is left untouched; rawfull57had no separatecavity shell.')
(P/'proposed-thick-join58c.json').write_text(json.dumps(out,indent=2)+'\n');(P/'proposed-native-controls58c.json').write_text(json.dumps(candidate,indent=2)+'\n')
print(json.dumps(dict(changes=[{k:v for k,v in r.items() if k!='delta_rows'} for r in changes],valleys=[{k:v for k,v in r.items() if k!='rows'} for r in valleys]),indent=2))
