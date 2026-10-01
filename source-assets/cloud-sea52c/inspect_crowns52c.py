import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'cloud_sea52c.blend'))
rows=[]
for ob in bpy.data.objects:
    if not ob.name.startswith('CloudSea52c_v'):continue
    me=ob.data;verts=[v.co.copy() for v in me.vertices];adj={i:set() for i in range(len(verts))}
    for e in me.edges:
        a,b=e.vertices;adj[a].add(b);adj[b].add(a)
    lo=min(v.z for v in verts);hi=max(v.z for v in verts)
    peaks=[i for i,v in enumerate(verts) if v.z>lo+.33*(hi-lo) and all(v.z>=verts[j].z for j in adj[i])]
    peaks.sort(key=lambda i:verts[i].z,reverse=True)
    chosen=[]
    for i in peaks:
        if all((verts[i].xy-verts[j].xy).length>45 for j in chosen):chosen.append(i)
    tree=BVHTree.FromPolygons(verts,[list(f.vertices) for f in me.polygons]);saddles=[]
    for a,b in zip(chosen,chosen[1:]):
        samples=[]
        for k in range(1,20):
            p=verts[a].lerp(verts[b],k/20);hit=tree.ray_cast(Vector((p.x,p.y,hi+100)),Vector((0,0,-1)))
            if hit[0]:samples.append(hit[0].z)
        if samples:saddles.append({'peaks':[a,b],'segment_minimum_z':min(samples),'drop_from_lower_peak':min(verts[a].z,verts[b].z)-min(samples)})
    rows.append({'name':ob.name,'mesh_local_maxima_above_lower_third_separated45m':[{'vertex':i,'position':list(verts[i])} for i in chosen],'straight_top_surface_between_descending_peaks':saddles})
(P/'crown-relief52c.json').write_text(json.dumps(rows,indent=2))
print(json.dumps([{'name':r['name'],'peaks':len(r['mesh_local_maxima_above_lower_third_separated45m']),'saddle_drops':[round(s['drop_from_lower_peak'],1) for s in r['straight_top_surface_between_descending_peaks']]} for r in rows],indent=2))
