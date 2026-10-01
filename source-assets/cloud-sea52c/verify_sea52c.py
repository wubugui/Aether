import bpy,bmesh,json,math,hashlib,struct
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import convex_hull_2d, intersect_line_line_2d
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'cloud_sea52c.blend'))
def stats(ob):
    me=ob.data;bm=bmesh.new();bm.from_mesh(me)
    todo=set(bm.verts);components=[]
    while todo:
        stack=[todo.pop()];n=0
        while stack:
            v=stack.pop();n+=1
            for e in v.link_edges:
                w=e.other_vert(v)
                if w in todo:todo.remove(w);stack.append(w)
        components.append(n)
    b=[[min(v.co[k] for v in me.vertices) for k in range(3)],[max(v.co[k] for v in me.vertices) for k in range(3)]]
    s={'name':ob.name,'vertices':len(me.vertices),'triangles':sum(len(f.vertices)-2 for f in me.polygons),'bounds_blender_xyz':b,'dimensions_xyz':[b[1][k]-b[0][k] for k in range(3)],'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'connected_components':components,'signed_volume':bm.calc_volume(signed=True),'materials':[m.name for m in me.materials]};bm.free()
    assert s['boundary_edges']==0 and s['nonmanifold_edges']==0 and len(components)==1 and s['signed_volume']>0
    return s
def hull(ob):
    p=[Vector((v.co.x,v.co.y)) for v in ob.data.vertices];return [p[i] for i in convex_hull_2d(p)]
def pointseg(p,a,b):
    d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared));return (p-a-t*d).length
def gap(A,B):
    value=1e9
    for i,a in enumerate(A):
        b=A[(i+1)%len(A)]
        for j,c in enumerate(B):
            d=B[(j+1)%len(B)]
            if intersect_line_line_2d(a,b,c,d):return 0
            value=min(value,pointseg(a,c,d),pointseg(b,c,d),pointseg(c,a,b),pointseg(d,a,b))
    return value
out={'read_back_source':str(P/'cloud_sea52c.blend'),'visual_acceptance':False,'variants':[]}
for vi in range(3):
    obs=list(bpy.data.collections[f'cloud_sea_52c_{vi}'].objects);rows=[stats(ob) for ob in obs]
    bounds=[[min(r['bounds_blender_xyz'][0][k] for r in rows) for k in range(3)],[max(r['bounds_blender_xyz'][1][k] for r in rows) for k in range(3)]]
    gaps=[{'pieces':[obs[i].name,obs[j].name],'conservative_convex_hull_horizontal_gap':gap(hull(obs[i]),hull(obs[j]))} for i,j in [(0,1),(0,2),(1,2)]]
    glb=(P/f'cloud_sea_52c_{vi}.glb').read_bytes();length,kind=struct.unpack_from('<II',glb,12);g=json.loads(glb[20:20+length]);assert len(g['meshes'])==3
    exported=[]
    for node in g['nodes']:
        if 'mesh' not in node:continue
        m=g['meshes'][node['mesh']];pr=m['primitives'][0];a=g['accessors'][pr['attributes']['POSITION']]
        exported.append({'node':node['name'],'position_min':a['min'],'position_max':a['max'],'attributes':list(pr['attributes'])})
    out['variants'].append({'variant':vi,'parts':rows,'combined_bounds_blender_xyz':bounds,'combined_dimensions_xyz':[bounds[1][k]-bounds[0][k] for k in range(3)],'world_max_y_with_anchor700':700+bounds[1][2],'gaps':gaps,'glb_meshes':len(g['meshes']),'glb_nodes':exported})
(P/'geometry52c.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
