"""Reopen source and compare all original geometry/control/color bytes before checks."""
import bpy,bmesh,json,hashlib,struct
from pathlib import Path
from mathutils.bvhtree import BVHTree

P=Path(__file__).resolve().parent
def fingerprint(ob):
    me=ob.data;h=hashlib.sha256()
    for v in me.vertices:h.update(struct.pack('<3f',*v.co))
    for f in me.polygons:
        h.update(struct.pack('<I',len(f.vertices)))
        h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
    for ca in me.color_attributes:
        h.update(ca.name.encode());h.update(ca.domain.encode());h.update(ca.data_type.encode())
        for c in ca.data:h.update(struct.pack('<4f',*c.color))
    h.update(json.dumps([[float(x) for x in row] for row in ob.matrix_world]).encode())
    h.update(json.dumps([m.name for m in me.materials]).encode())
    return h.hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P.parent/'cloud-sea52e/cloud_sea52e.blend'))
old={ob.name:fingerprint(ob) for ob in bpy.data.objects if ob.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(P/'cloud_sea52f.blend'))
new={name:fingerprint(bpy.data.objects[name]) for name in old}
assert old==new,'A retained 52e final or control changed'
rows=[]
for ob in bpy.data.objects:
    if not ob.name.startswith(('CloudSea52e_','CloudSea52f_')):continue
    me=ob.data;bm=bmesh.new();bm.from_mesh(me)
    remaining=set(bm.verts);components=[]
    while remaining:
        stack=[remaining.pop()];count=0
        while stack:
            v=stack.pop();count+=1
            for e in v.link_edges:
                w=e.other_vert(v)
                if w in remaining:remaining.remove(w);stack.append(w)
        components.append(count)
    me.calc_loop_triangles();verts=[v.co.copy() for v in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles]
    tree=BVHTree.FromPolygons(verts,tris,all_triangles=True,epsilon=0)
    intersections=[(a,b) for a,b in tree.overlap(tree) if a<b and not(set(tris[a])&set(tris[b]))]
    zero=sum((verts[t[1]]-verts[t[0]]).cross(verts[t[2]]-verts[t[0]]).length<1e-7 for t in tris)
    lo=[min(v[k] for v in verts) for k in range(3)];hi=[max(v[k] for v in verts) for k in range(3)]
    r={'name':ob.name,'vertices':len(verts),'triangles':len(tris),'bounds_blender_xyz':[lo,hi],
       'boundary_edges':sum(e.is_boundary for e in bm.edges),
       'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
       'connected_components':components,'signed_volume':bm.calc_volume(signed=True),
       'zero_area_triangles':zero,'nonadjacent_triangle_intersections':len(intersections),'intersection_pairs':intersections[:50]}
    bm.free();rows.append(r)
    print(json.dumps(r))
axis=[]
for fn,expected_count in [('cloud_sea_52f_connector_v0.glb',1),('cloud_sea_52f_prototype_v0.glb',4)]:
    data=(P/fn).read_bytes();size,kind=struct.unpack_from('<II',data,12);g=json.loads(data[20:20+size])
    assert len(g['meshes'])==expected_count
    for n in g['nodes']:
        if 'mesh' not in n:continue
        assert not any(k in n for k in ('matrix','translation','rotation','scale'))
        pr=g['meshes'][n['mesh']]['primitives'][0];acc=g['accessors'][pr['attributes']['POSITION']]
        row=next(r for r in rows if r['name']==n['name']);lo,hi=row['bounds_blender_xyz']
        expected=[[lo[0],lo[2],-hi[1]],[hi[0],hi[2],-lo[1]]]
        error=max(abs(a-b) for A,B in zip(expected,[acc['min'],acc['max']]) for a,b in zip(A,B))
        assert error<.001
        axis.append({'file':fn,'node':n['name'],'expected_godot_xyz':expected,'actual_glb_xyz':[acc['min'],acc['max']],
                     'max_abs_error':error,'attributes':list(pr['attributes'])})
out={'status':'Geometry checks only; visual acceptance pending',
     'old_52e_mesh_and_control_fingerprints_unchanged':old==new,'retained_count':len(old),
     'old_fingerprints':old,'new_fingerprints':new,'new_control_count':sum(o.name.startswith('CONTROL52f_') for o in bpy.data.objects),
     'parts':rows,'axis_mapping':'Blender (x,y,z) -> glTF/Godot (x,z,-y)','axis_checks':axis,
     'material_reused':'Cloud46 diffuse warm crown cool belly','visual_acceptance':False}
(P/'geometry52f.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'old_meshes_and_controls_unchanged':True,'new':rows[-1],'axis_mapping_verified':True},indent=2))

assert all(not(r['boundary_edges'] or r['nonmanifold_edges'] or r['zero_area_triangles'] or r['nonadjacent_triangle_intersections']) and len(r['connected_components'])==1 and r['signed_volume']>0 for r in rows)
