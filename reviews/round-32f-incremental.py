from pathlib import Path
import json,ast,math,numpy as np
from collections import Counter
from shapely.geometry import Polygon
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8'))
old=read('reviews/round-32e-reopened-source.json')['objects'];new=read('reviews/round-32f-reopened-source.json')['objects']
ep=read('captures/foreground_island_study_32e/design-plan.json');fp=read('captures/foreground_island_study_32f/design-plan.json')
tree=read('reviews/round-32e-actual-tree-bases.json');rows=[];basechecks=[]
for name,a in old.items():
 b=new[name];av,bv=np.array(a['vertices']),np.array(b['vertices']);samefaces=a['polygons']==b['polygons'];samexy=np.array_equal(av[:,:2],bv[:,:2]);changed=np.flatnonzero(np.any(av!=bv,axis=1))
 rows.append(dict(object=name,polygon_indices_exact=samefaces,vertex_xy_exact=samexy,changed_vertex_count=len(changed),maximum_vertex_displacement_m=float(np.linalg.norm(av-bv,axis=1).max())))
 assert samexy
for tr in tree['checks']:
 mask=Polygon(tr['actual_base_polygon_xy']);hits=[];changedhits=[]
 for name,a in old.items():
  counters=[]
  for mesh in [a,new[name]]:
   counter=Counter();verts=np.array(mesh['vertices'])
   for i,f in enumerate(mesh['polygons']):
    t=verts[f];pol=Polygon(t[:,:2])
    if not pol.is_valid or pol.area<1e-12:continue
    if pol.intersection(mask).area>1e-12:counter[tuple(sorted(map(tuple,t)))]+=1
   counters.append(counter)
  hits.extend([name]*sum(counters[0].values()))
  if counters[0]!=counters[1]:changedhits.append(dict(object=name,old_only=sum((counters[0]-counters[1]).values()),new_only=sum((counters[1]-counters[0]).values())))
 basechecks.append(dict(xy=tr['xy'],scale=tr['scale'],all_mesh_projected_intersecting_faces=len(hits),changed_intersecting_faces=changedhits,can_inherit_32e_full_upper_envelope_support=not changedhits))
ns={'__file__':__file__};code=(R/'reviews/round-32e-pad-transition-local.py').read_text(encoding='utf-8').split('samples=[]')[0];exec(code,ns);env=ns['env'];src=(R/'blender/model_foreground_island_32f.py').read_text(encoding='utf-8');fs=[v for v in ast.parse(src).body if isinstance(v,ast.FunctionDef) and v.name in ['near_edge','smooth','base','route_hits','heightfield']];exec(compile(ast.Module(body=fs,type_ignores=[]),'actual32f_height_functions','exec'),env)
trans=read('reviews/round-32e-pad-transition-local.json');jumps=[]
for s in trans['largest_sampled_boundary_jumps']:
 p=next(p for p in fp['pads'] if p['id']==s['pad']);xy=np.array(s['xy']);c,si=math.cos(p['yaw']),math.sin(p['yaw']);rot=np.array([[c,-si],[si,c]]);uv=rot.T@(xy-np.array(p['xy']));ax=int(np.argmin(abs(abs(uv)-p['half'])));norm=rot[:,ax]*np.sign(uv[ax]);z=env['heightfield'](*(xy+norm*.0001));jumps.append(dict(pad=p['id'],xy=s['xy'],old_outside_minus_full_height_m=s['outside_minus_full_height_m'],new_outside_minus_full_height_m=z-p['height']))
faces=[];cap='island_a grass and exposed rock terrain';bv=np.array(new[cap]['vertices'])
for row in trans['actual_local_upward_faces_over30degrees']:
 i=row['native_polygon_index'];f=new[cap]['polygons'][i];t=bv[f];n=np.cross(t[1]-t[0],t[2]-t[0]);faces.append(dict(native_polygon_index=i,old_slope_degrees=row['slope_degrees'],new_slope_degrees=math.degrees(math.acos(n[2]/np.linalg.norm(n))),new_vertices=t.tolist()))
r=dict(round='32f',geometry_increment=rows,tree_base_inheritance=basechecks,design_pad_tree_route_boundary_fields_exact={k:ep[k]==fp[k] for k in ['pads','trees_blender_xy_scale','routes','boundary_xyh']},boundary_function_recheck=jumps,same_actual_local_face_slope_recheck=faces,all8_real_tree_bases_support_inherited=all(x['can_inherit_32e_full_upper_envelope_support'] for x in basechecks),limits=['These are the same bounded actual source faces and previously sampled pad-edge locations, not an exhaustive maximum of all transition slopes.','The regularized weight uses t²+1e-12 and inside snaps fordist<1e-5, so this is numerical near-continuity, not a claim of mathematically infinite weight or exact C1 continuity.','No new GPU or full-world scan;32e full tree-base support is inherited only when every old/new mesh face whose XY projection intersects the real base is exactly unchanged.'])
(R/'reviews/round-32f-incremental.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps(dict(rows=rows,treeinherit=r['all8_real_tree_bases_support_inherited'],treechanges=[x for x in basechecks if x['changed_intersecting_faces']],jumps=jumps[:2],slopes=faces[:3]),indent=2))
