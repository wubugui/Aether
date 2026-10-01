import bpy,bmesh,json,hashlib,struct
from pathlib import Path
from collections import Counter
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'cloud_sea52h_c.blend'))
def geometry(ob):
 me=ob.data;me.calc_loop_triangles();verts=[v.co.copy() for v in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles]
 bm=bmesh.new();bm.from_mesh(me);todo=set(bm.verts);components=[]
 while todo:
  stack=[todo.pop()];count=0
  while stack:
   v=stack.pop();count+=1
   for e in v.link_edges:
    w=e.other_vert(v)
    if w in todo:todo.remove(w);stack.append(w)
  components.append(count)
 tree=BVHTree.FromPolygons(verts,tris,all_triangles=True,epsilon=0)
 bad=[(a,b) for a,b in tree.overlap(tree) if a<b and not(set(tris[a])&set(tris[b]))]
 area=[(verts[t[1]]-verts[t[0]]).cross(verts[t[2]]-verts[t[0]]).length for t in tris]
 aspect=[max((verts[t[(k+1)%3]]-verts[t[k]]).length_squared for k in range(3))/max(a,1e-12) for t,a in zip(tris,area)]
 low=[min(v[k] for v in verts) for k in range(3)];high=[max(v[k] for v in verts) for k in range(3)]
 r={'name':ob.name,'vertices':len(verts),'triangles':len(tris),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'components':components,'signed_volume_m3':bm.calc_volume(signed=True),'nonadjacent_triangle_intersections':len(bad),'intersection_pairs':bad[:50],'zero_area_triangles':sum(a<1e-7 for a in area),'triangle_aspect_over20':sum(a>20 for a in aspect),'triangle_aspect_max':max(aspect),'bounds_blender_xyz':[low,high],'dimensions_m':[b-a for a,b in zip(low,high)]};bm.free()
 return r,verts,tris

rows=[]
for name in ['CONTROL52hC_exact_positive_union','CONTROL52hC_continuous_medium_fold_surface']:
 r,verts,tris=geometry(bpy.data.objects[name]);rows.append(r)
passed=all(not(r['boundary_edges'] or r['nonmanifold_edges'] or r['nonadjacent_triangle_intersections'] or r['zero_area_triangles']) and len(r['components'])==1 and r['signed_volume_m3']>0 for r in rows)
(P/'intermediate-controls52h-c.json').write_text(json.dumps({'closed_continuous_controls_passed':passed,'controls':rows,'visual_acceptance':False},indent=2)+'\n')
print(json.dumps({'closed_continuous_controls_passed':passed,'controls':[{k:r[k] for k in ['name','vertices','triangles','components','boundary_edges','nonmanifold_edges','nonadjacent_triangle_intersections','zero_area_triangles']} for r in rows]},indent=2))
assert passed
