import bpy,bmesh,json,struct
from pathlib import Path
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'cloud_sea52g_b_main.blend'))
ob=bpy.data.objects['CloudSea52g_b_v0_main_crown'];me=ob.data
bm=bmesh.new();bm.from_mesh(me);todo=set(bm.verts);components=[]
while todo:
    stack=[todo.pop()];count=0
    while stack:
        v=stack.pop();count+=1
        for e in v.link_edges:
            w=e.other_vert(v)
            if w in todo:todo.remove(w);stack.append(w)
    components.append(count)
me.calc_loop_triangles();verts=[v.co.copy() for v in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles]
tree=BVHTree.FromPolygons(verts,tris,all_triangles=True,epsilon=0)
bad=[(a,b) for a,b in tree.overlap(tree) if a<b and not(set(tris[a])&set(tris[b]))]
zero=sum((verts[t[1]]-verts[t[0]]).cross(verts[t[2]]-verts[t[0]]).length<1e-7 for t in tris)
aspect=[max((verts[t[(k+1)%3]]-verts[t[k]]).length_squared for k in range(3))/max((verts[t[1]]-verts[t[0]]).cross(verts[t[2]]-verts[t[0]]).length,1e-12) for t in tris]
lo=[min(v[k] for v in verts) for k in range(3)];hi=[max(v[k] for v in verts) for k in range(3)]
r={'name':ob.name,'vertices':len(verts),'triangles':len(tris),'bounds_blender_xyz':[lo,hi],
 'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
 'components':components,'signed_volume':bm.calc_volume(signed=True),'zero_area_triangles':zero,
 'nonadjacent_triangle_intersections':len(bad),'intersection_pairs':bad[:50],
 'triangle_aspect_over_20':sum(v>20 for v in aspect),'triangle_aspect_max':max(aspect)}
bm.free()
raw=(P/'cloud_sea_52g_b_main_v0.glb').read_bytes();size,kind=struct.unpack_from('<II',raw,12);g=json.loads(raw[20:20+size]);assert len(g['meshes'])==1
n=next(n for n in g['nodes'] if 'mesh' in n);pr=g['meshes'][n['mesh']]['primitives'][0];acc=g['accessors'][pr['attributes']['POSITION']]
expected=[[lo[0],lo[2],-hi[1]],[hi[0],hi[2],-lo[1]]]
error=max(abs(a-b) for A,B in zip(expected,[acc['min'],acc['max']]) for a,b in zip(A,B));assert error<.001
out={'status':'Geometry validation only; visual review pending','part':r,
 'axis_mapping':'Blender(x,y,z) -> glTF/Godot(x,z,-y)','axis_error_m':error,'attributes':list(pr['attributes']),
 'editable_cage_meshes':sum(o.name.startswith('CONTROL52g_b_') and o.type=='MESH' for o in bpy.data.objects),
 'editable_region_reference_handles':sum(o.name.startswith('CONTROL52g_b_') and o.type=='EMPTY' for o in bpy.data.objects),
 'visual_acceptance':False}
(P/'geometry52g-b.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
assert not(r['boundary_edges'] or r['nonmanifold_edges'] or zero or bad)
assert len(components)==1 and r['signed_volume']>0
