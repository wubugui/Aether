import bpy,json,collections
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53';base=json.load(open(D+'/base51b.json'));org=base['meshes']['massif_west_spur']['origin']
bpy.ops.wm.open_mainfile(filepath=D+'/revision-c/massif_west_spur_rim53.blend');m=bpy.data.objects['ridge_shoulders'].data;m.calc_loop_triangles();n=len(m.vertices)//2;edges=collections.Counter()
for t in m.loop_triangles:
 if all(i<n for i in t.vertices):
  for a,b in zip(t.vertices,list(t.vertices[1:])+[t.vertices[0]]):edges[tuple(sorted((a,b)))]+=1
def w(i):
 p=m.vertices[i].co;return [p.x+org[0],p.z,-p.y+org[2]]
json.dump([[w(a),w(b)] for (a,b),count in edges.items() if count==1],open(D+'/revision-c/root-edges-world.json','w'))
