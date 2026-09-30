from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'captures/localize_island_30d_visible_slope.py').read_text()
s=s.replace('lantern-island-30d-20260908T183203Z-dfad421d9cb14734824e8942e33ac04c','lantern-island-30k-r1-20260908T193210Z-09e7ff871c9941519a561b4fede063ee').replace('30d','30k')
s=s.replace('[[620,548],[700,550],[770,552],[825,570],[900,548],[970,548]]','[[620,540],[695,525],[755,550],[810,545]]')
s=s.replace('Central visible day-c-front wall is on south/east-facing main terrain. West/Southwest/North cutbacks do not alone address this view; choose next edits from these source triangles and actual protected regions, not object names.','Localizes four directly seen30k front-slope points: wide left inclined face and central incision/face. Use current native source indices only; no whole-image segmentation or artistic acceptance claim.')
exec(compile(s,str(__file__),'exec'))
# Coplanar connected patches identify the actual broad editable surfaces,
# rather than equating exporter triangulation with distinct sculpted facets.
import collections
o=e['new']['island_c grass and exposed rock terrain'];verts=np.array(o['vertices']);faces=np.array(o['polygons']);ts=verts[faces]
ns=np.cross(ts[:,1]-ts[:,0],ts[:,2]-ts[:,0]);areas=np.linalg.norm(ns,axis=1)/2;ns/=np.linalg.norm(ns,axis=1)[:,None]
edges=collections.defaultdict(list)
for i,f in enumerate(faces):
    for a,b in zip(f,np.roll(f,-1)):edges[tuple(sorted((int(a),int(b))))].append(i)
adj=collections.defaultdict(set)
for v in edges.values():
    if len(v)==2:adj[v[0]].add(v[1]);adj[v[1]].add(v[0])
for sample in report['samples']:
    if not sample['source'] or sample['source']['name']!='island_c grass and exposed rock terrain':continue
    seed=sample['source']['face'];normal=ns[seed];level=float(normal@ts[seed,0]);seen={seed};queue=[seed]
    while queue:
        for j in adj[queue.pop()]:
            if j in seen:continue
            if float(normal@ns[j])>1-1e-8 and max(abs(ts[j]@normal-level))<1e-5:seen.add(j);queue.append(j)
    indices=sorted(seen);points=ts[indices].reshape(-1,3)
    sample['connected_coplanar_patch']=dict(source_faces=indices,area_m2=float(sum(areas[indices])),bounds_min_xyz=points.min(axis=0).tolist(),bounds_max_xyz=points.max(axis=0).tolist(),normal_tolerance=1e-8,plane_distance_tolerance_m=1e-5)
out.write_text(json.dumps(report,indent=2))
print([(x['pixel'],x['source']['face'],x.get('connected_coplanar_patch',{}).get('area_m2')) for x in report['samples']])
