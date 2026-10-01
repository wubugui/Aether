#!/usr/bin/env python3
"""Additional actual triangle BVH probes at all four islands' eight compass sides."""
import ast, json, math, numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent
meta=json.loads((P/'support49-export.json').read_text());report=json.loads((P/'depth49-bake-report.json').read_text())
X0,Z0,X1,Z1=map(float,meta['domain_world_xz']);W,H=769,1537
fheight=np.fromfile(P/'height49-1m-rf.f32',dtype='<f4').reshape(H,W)
raw=np.fromfile(P/'support49-world-f32.bin',dtype='<f4').reshape(-1,3,3).astype(float)
lo=raw[:,:,[0,2]].min(1);hi=raw[:,:,[0,2]].max(1)
a,b,c=raw[:,0],raw[:,1],raw[:,2]
den=(b[:,2]-c[:,2])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,2]-c[:,2])
valid=(np.abs(den)>1e-12)&(hi[:,0]>=X0)&(lo[:,0]<=X1)&(hi[:,1]>=Z0)&(lo[:,1]<=Z1)
tri=raw[valid];lo=lo[valid];hi=hi[valid];a,b,c=tri[:,0],tri[:,1],tri[:,2];den=den[valid]
mids=np.arange(len(tri));centers=(lo+hi)*.5;nodes=[]
# Reuse only algorithm function definitions, without re-running bake/artifact writes.
tree=ast.parse((P/'bake_support_depth49.py').read_text())
for func in tree.body:
 if isinstance(func,ast.FunctionDef) and func.name in ['build','top','sample','summary']:
  exec(compile(ast.Module(body=[func],type_ignores=[]),'<shared BVH algorithm>','exec'),globals())
build(np.arange(len(tri)))
rows=[]
for m in meta['included_meshes']:
 if m['category']!='LakeIslands49/rockroot':continue
 name=m['path'].split('/')[2];cx,_,cz=m['world_transform'][9:12]
 candidates=[s for s in report['actual_shore_samples'] if f'/LakeIslands49/{name}/' in s['source_mesh']]
 assert candidates,name
 for side,angle in [('east',0),('southeast',math.pi/4),('south',math.pi/2),('southwest',3*math.pi/4),('west',math.pi),('northwest',5*math.pi/4),('north',3*math.pi/2),('northeast',7*math.pi/4)]:
  def adiff(s):
   x,z=s['world_xz'];ang=math.atan2(z-cz,x-cx)
   return abs(math.atan2(math.sin(ang-angle),math.cos(ang-angle)))
  shore=min(candidates,key=adiff);point=np.array(shore['world_xz']);radial=point-np.array([cx,cz]);radial/=np.linalg.norm(radial)
  samples=[]
  for offset in [-2,-1,-.5,0,.5,1,2,4]:
   x,z=point+radial*offset;actual=top(x,z);baked=sample(x,z)
   samples.append({'offset_m_from_actual_shore':offset,'world_xz':[float(x),float(z)],'actual_highest_y':actual,'baked_linear_height_y':baked,'actual_depth_m':max(0,-actual),'baked_signed_height_depth_m':max(0,-baked),'depth_error_m':abs(max(0,-actual)-max(0,-baked))})
  rows.append({'island':name,'side':side,'actual_shore_source_mesh':shore['source_mesh'],'actual_shore_world_xz':shore['world_xz'],'selected_shore_angular_distance_degrees':math.degrees(adiff(shore)),'samples':samples})
summary_data={'purpose':'Actual49 support BVH versus1m signed-height sampling around every island side; diagnostic, not material acceptance','island_count':4,'sides_per_island':8,'sample_offsets_m':[-2,-1,-.5,0,.5,1,2,4],'samples':rows,'all_side_probe_count':sum(len(r['samples']) for r in rows),'depth_error':summary([s['depth_error_m'] for r in rows for s in r['samples']])}
(P/'island-side-probes.json').write_text(json.dumps(summary_data,indent=2))
print(json.dumps({k:v for k,v in summary_data.items() if k!='samples'},indent=2))
