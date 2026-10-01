import bpy,json,math,collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53';base=json.load(open(D+'/base51b.json'))
f=[p for m in base['meshes'].values() for p in m['faces']];tr=BVHTree.FromPolygons(list(map(Vector,f)),[(i,i+1,i+2) for i in range(0,len(f),3)],all_triangles=True)
out=[]
for sub in ['/revision-c']:
 bpy.ops.wm.open_mainfile(filepath=D+sub+'/massif_west_spur_rim53.blend');o=bpy.data.objects['ridge_shoulders'];m=o.data;m.calc_loop_triangles();n=len(m.vertices)//2;org=base['meshes']['massif_west_spur']['origin'];edges=collections.Counter()
 for t in m.loop_triangles:
  if all(i<n for i in t.vertices):
   for a,b in zip(t.vertices,list(t.vertices[1:])+[t.vertices[0]]):edges[tuple(sorted((a,b)))]+=1
 def w(v):return Vector((v.co.x+org[0],v.co.z,-v.co.y+org[2]))
 delta=[]
 for (a,b),count in edges.items():
  if count!=1:continue
  p=w(m.vertices[a]);q=w(m.vertices[b]);steps=math.ceil((q-p).length/0.5)
  for i in range(steps+1):
   v=p.lerp(q,i/steps);h,no,idx,dd=tr.ray_cast(Vector((v.x,1500,v.z)),Vector((0,-1,0)),3000);assert h
   delta.append(v.y-h.y)
 r={'revision':sub or 'first','boundary_samples_0_5m':len(delta),'max_boundary_above_actual_support_m':max(delta),'min_boundary_below_actual_support_m':min(delta),'all_boundary_buried':max(delta)<=0};out.append(r);print(r)
json.dump(out,open(D+'/revision-c/root-join-check.json','w'),indent=2)
