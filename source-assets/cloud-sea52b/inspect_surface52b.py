import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent
out=[]
for version in ['52','52b']:
    bpy.ops.wm.open_mainfile(filepath=str(P.parent/f'cloud-sea{version}'/f'cloud_sea{version}.blend'))
    for ob in bpy.data.objects:
        if not ob.name.startswith(f'CloudSea{version}_v'):continue
        me=ob.data;me.calc_loop_triangles();verts=[v.co.copy() for v in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles]
        tree=BVHTree.FromPolygons(verts,tris,all_triangles=True,epsilon=0)
        bad=[]
        for a,b in tree.overlap(tree):
            if a>=b or set(tris[a])&set(tris[b]):continue
            bad.append([a,b])
        out.append({'version':version,'name':ob.name,'nonadjacent_triangle_intersections':len(bad),'pairs':bad[:100],'zero_area_triangles':sum((verts[t[1]]-verts[t[0]]).cross(verts[t[2]]-verts[t[0]]).length<1e-7 for t in tris)})
(P/'surface-integrity52b.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
assert not any(r['nonadjacent_triangle_intersections'] or r['zero_area_triangles'] for r in out if r['version']=='52b')
