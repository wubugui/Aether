from pathlib import Path
import ast,json,math,numpy as np
R=Path(__file__).resolve().parents[1]
plan=json.loads((R/'captures/foreground_island_study_32e/design-plan.json').read_text(encoding='utf-8'))
src=(R/'blender/model_foreground_island_32e.py').read_text(encoding='utf-8')
env=dict(math=math,boundary=plan['boundary_xyh'],pads=plan['pads'],routes=plan['routes'],trees=plan['trees_blender_xy_scale'],n=len(plan['boundary_xyh']))
fs=[v for v in ast.parse(src).body if isinstance(v,ast.FunctionDef) and v.name in ['near_edge','smooth','base','route_hits','heightfield']]
exec(compile(ast.Module(body=fs,type_ignores=[]),'actual32e_height_functions','exec'),env)
def dist(xy,p):
 d=np.array(xy)-p['xy'];c,s=math.cos(p['yaw']),math.sin(p['yaw']);u,v=np.array([[c,s],[-s,c]])@d
 return max(abs(u)-p['half'][0],abs(v)-p['half'][1],0)
samples=[]
for p in plan['pads']:
 c,s=math.cos(p['yaw']),math.sin(p['yaw']);rot=np.array([[c,-s],[s,c]])
 for ax in range(2):
  for sign in [-1,1]:
   for q in np.linspace(-.99,.99,81):
    uv=np.zeros(2);uv[ax]=sign*p['half'][ax];uv[1-ax]=q*p['half'][1-ax]
    norm=rot[:,ax]*sign;xy=np.array(p['xy'])+rot@uv
    if any(dist(xy,other)<1e-5 for other in plan['pads'] if other is not p):continue
    z=env['heightfield'](*(xy+norm*1e-4));jump=z-p['height']
    if abs(jump)>.001:samples.append(dict(pad=p['id'],xy=xy.tolist(),outside_offset_m=.0001,outside_minus_full_height_m=jump,other_pad_distances={o['id']:dist(xy,o) for o in plan['pads'] if o is not p}))
samples.sort(key=lambda a:abs(a['outside_minus_full_height_m']),reverse=True)
o=json.loads((R/'reviews/round-32e-reopened-source.json').read_text(encoding='utf-8'))['objects']['island_a grass and exposed rock terrain'];v=np.array(o['vertices']);faces=[]
for i,f in enumerate(o['polygons']):
 t=v[f];ctr=t.mean(axis=0);n=np.cross(t[1]-t[0],t[2]-t[0]);ln=np.linalg.norm(n)
 if n[2]<=0 or not(-16<ctr[0]<4 and 7<ctr[1]<17):continue
 slope=math.degrees(math.acos(n[2]/ln))
 if slope>30:faces.append(dict(native_polygon_index=i,vertex_indices=f,vertices=t.tolist(),slope_degrees=slope,xy_area_m2=float(n[2]/2),centroid=ctr.tolist()))
faces.sort(key=lambda a:a['slope_degrees'],reverse=True)
report=dict(round='32e',scope='Bounded actual pad-transition function and reopened source faces between tower and right-house region; no pixel ray attribution or self-intersection scan.',height_function_source='blender/model_foreground_island_32e.py:53-60',cause='At a pad edge its finite weight tends to1, while another nearby pad retains a nonzero weight. The normalized target outside does not tend to the full pad height returned inside. Actual mesh remains connected but narrow triangles can bridge a finite height jump.',boundary_sample_count_with_jump_over1mm=len(samples),largest_sampled_boundary_jumps=samples[:12],actual_local_upward_faces_over30degrees=faces[:15],actual_local_steep_face_count=len(faces),limits=['Boundary samples are finite function evaluations100micrometers outside, not an exhaustive maximum or measured crack width.','Actual source face indices are independently measured but have not been reprojected to the reported image pixels.','Full pad and building support checks remain passed; this does not establish all terrain surfaces continuous in slope.'])
(R/'reviews/round-32e-pad-transition-local.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(boundary_count=len(samples),worst=samples[:1],localfaces=faces[:3]),indent=2))
