import bpy,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53';O=D+'/integration-west53'
b=json.load(open(D+'/base51b.json'));p=json.load(open(O+'/integration-payload.json'));r=json.load(open(O+'/scatter-reconcile-report.json'));s=json.load(open(D+'/revision-d/sculpt-report.json'))
f=[v for n,m in b['meshes'].items() if n!='massif_west_spur' for v in m['faces']]+p['mountains'][0]['collision_vertices']
t=BVHTree.FromPolygons(list(map(Vector,f)),[(i,i+1,i+2) for i in range(0,len(f),3)],all_triangles=True)
def h(x,z):
 v,_,_,_=t.ray_cast(Vector((x,1500,z)),Vector((0,-1,0)),3000);return v.y if v else None
rows=[]
for x in [120,200,246.5,310,380,460]:
 for z in [-2130,-2040,-1960,-1881.25,-1800,-1720,-1630]:
  y=h(x,z)
  if y is not None:rows.append({'x':x,'z':z,'expected_y':y})
build=[]
for rect in s['buildings_protected']:
 for i in range(3):
  for j in range(3):
   x=rect['xmin']+(rect['xmax']-rect['xmin'])*i/2;z=rect['zmin']+(rect['zmax']-rect['zmin'])*j/2;y=h(x,z)
   if y is not None:build.append({'node':rect['node'],'x':x,'z':z,'expected_y':y})
scatter=[]
for row in r['scatter']:
 pos=row['new_world_position'];scatter.append({'node_path':row['node'].removeprefix('/Skyfarer/'),'index':row['index'],'position':pos,'expected_support_y':pos[1]-row['new_support_clearance_m'],'status':row['status'],'baseline_clearance_m':row['baseline_support_clearance_m']})
json.dump({'mountain':rows,'buildings':build,'scatter':scatter,'method':'Expected actual highest support from same source geometry and preserved native neighbor meshes. Runtime must query layer4 from above the peak and ground_height above the peak; no procedural height assumption.'},open(O+'/runtime-probes.json','w'),indent=2)
print('PROBES',len(rows),len(build),len(scatter))
