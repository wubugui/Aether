import bpy,bmesh,json,struct,hashlib
from collections import Counter
from mathutils.kdtree import KDTree
from pathlib import Path
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'cloud_sea52h_main.blend'))
ob=bpy.data.objects['CloudSea52h_v0_main_crown'];me=ob.data
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
raw=(P/'cloud_sea_52h_main_v0.glb').read_bytes();size,kind=struct.unpack_from('<II',raw,12);g=json.loads(raw[20:20+size]);assert len(g['meshes'])==1
n=next(n for n in g['nodes'] if 'mesh' in n);pr=g['meshes'][n['mesh']]['primitives'][0];acc=g['accessors'][pr['attributes']['POSITION']]
expected=[[lo[0],lo[2],-hi[1]],[hi[0],hi[2],-lo[1]]]
error=max(abs(a-b) for A,B in zip(expected,[acc['min'],acc['max']]) for a,b in zip(A,B));assert error<.001
out={'status':'Geometry validation only; visual review pending','part':r,
 'axis_mapping':'Blender(x,y,z) -> glTF/Godot(x,z,-y)','axis_error_m':error,'attributes':list(pr['attributes']),
 'editable_control_volume_meshes':sum(o.name.startswith('CONTROL52h_') and o.type=='MESH' for o in bpy.data.objects),
 'editable_region_reference_handles':sum(o.name.startswith('CONTROL52h_') and o.type=='EMPTY' for o in bpy.data.objects),
 'visual_acceptance':False}
# Native Blender GLB import readback: match every triangle to the saved final.
before_objects=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(P/'cloud_sea_52h_main_v0.glb'))
imported=[o for o in bpy.data.objects if o not in before_objects and o.type=='MESH']
assert len(imported)==1
im=imported[0];im.data.calc_loop_triangles();kd=KDTree(len(verts))
for i,v in enumerate(verts):kd.insert(v,i)
kd.balance();mapping=[];distances=[]
for v in im.data.vertices:
    point,index,distance=kd.find(im.matrix_world@v.co);mapping.append(index);distances.append(distance)
def canonical_triangle(t):return min(tuple(t),tuple(t[1:]+t[:1]),tuple(t[2:]+t[:2]))
expected_faces=Counter(canonical_triangle(list(t)) for t in tris)
actual_faces=Counter(canonical_triangle([mapping[i] for i in t.vertices]) for t in im.data.loop_triangles)
controls=[]
for o in before_objects:
    if o.name.startswith('CONTROL52h_') and o.type=='MESH':
        cb=bmesh.new();cb.from_mesh(o.data)
        controls.append({'name':o.name,'vertices':len(cb.verts),'faces':len(cb.faces),'boundary_edges':sum(e.is_boundary for e in cb.edges),'nonmanifold_edges':sum(not e.is_manifold for e in cb.edges),'signed_volume':cb.calc_volume(signed=True),'editable_modifiers':[m.type for m in o.modifiers]});cb.free()
out['native_glb_readback']={'imported_meshes':len(imported),'max_vertex_distance_m':max(distances),'all_oriented_triangle_vertex_correspondence_exact':actual_faces==expected_faces,'imported_triangles':len(im.data.loop_triangles),'no_source_save':True}
out['editable_controls']=controls
out['native_blend_final_meshes']=sum(o.type=='MESH' and o.name.startswith('CloudSea52h_') for o in before_objects)
out['source_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [P/'cloud_sea52h_main.blend',P/'cloud_sea_52h_main_v0.glb']}
assert max(distances)<.001 and actual_faces==expected_faces
assert len(controls)==2 and all(c['boundary_edges']==0 and c['nonmanifold_edges']==0 and c['signed_volume']>0 for c in controls)
(P/'geometry52h.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
assert not(r['boundary_edges'] or r['nonmanifold_edges'] or zero or bad)
assert len(components)==1 and r['signed_volume']>0
