import json,collections
from pathlib import Path
D=Path(__file__).resolve().parent;j=json.load(open(D/'upper-remesh-intake.json'));v=j['vertices_with_cached_y0_intersections'];fs=j['original_triangles'];dry=[(i,f) for i,f in enumerate(fs) if min(v[k][1] for k in f)>0];wet=[{'original_triangle':i,'polygon':f} for i,f in enumerate(fs) if min(v[k][1] for k in f)<=0];es=collections.Counter(tuple(sorted((a,b))) for _,f in dry for a,b in zip(f,f[1:]+f[:1]));border=[e for e,c in es.items() if c==1];links=collections.defaultdict(list)
for a,b in border:links[a].append(b);links[b].append(a)
left=set(border);a,b=left.pop();loop=[a,b]
while loop[-1]!=loop[0]:
 opts=[q for q in links[loop[-1]] if tuple(sorted((loop[-1],q))) in left];assert len(opts)==1;q=opts[0];left.remove(tuple(sorted((loop[-1],q))));loop.append(q)
assert not left
j['waterline_loops_original']=j['waterline_loops'];j['waterline_loops']=[loop[:-1]];j['wet_polygons']=wet;j['protected_faces']=[r for r in j['protected_faces'] if min(v[k][1] for k in fs[r['original_triangle']])>0];j['strict_native_strategy']='Every original GPU/collision triangle with minimumY<=0 is kept whole at native float32 coordinates. Only260fully dry triangles are remodelled. The42edge positive-height interface uses original vertices; no new waterline intersection is serialized.';json.dump(j,open(D/'upper-remesh-intake-c.json','w'),indent=2);print('ORIGINAL_WET_TRIANGLES',len(wet),'DRY_REMODEL_TRIANGLES',len(dry),'ORIGINAL_INTERFACE_EDGES',len(loop)-1)
