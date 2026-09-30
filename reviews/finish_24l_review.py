from pathlib import Path
exec(Path(r'E:\FeiTing\reviews\audit_24l_actual.py').read_text().split('old,oldsha=')[0])
path=R/'reviews/round-24l-village-grading-independent-review.json';out=json.loads(path.read_text())
old,_=load(R/'captures/headland_study_23g/mainland_headland.glb');new,_=load(R/'captures/village_grading_study_24l/mainland_headland.glb');_,_,_,up=prepare(old)
edges=Counter()
for r in up:
    for a,b in zip(r['v'],np.roll(r['v'],-1,axis=0)):edges[tuple(sorted((tuple(a),tuple(b))))]+=1
adj={}
for e,n in edges.items():
    if n==1:
        a,b=e;adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a)
todo=set(adj);components=[];actual={tuple(v) for r in new for v in r['v']}
while todo:
    start=todo.pop();found={start};stack=[start]
    while stack:
        for v in adj[stack.pop()]:
            if v not in found:found.add(v);todo.discard(v);stack.append(v)
    components.append(found)
out['upper_border']['connected_component_vertex_counts']=sorted([len(c) for c in components],reverse=True)
core=max(components,key=len);out['upper_border']['core_border_vertex_count']=len(core);out['upper_border']['core_missing_exact_vertices']=len(core-actual)
d=json.loads((R/'captures/village_paving_design_24j/paving.json').read_text());p=Point(-2224.3179219903564,-1872.8434267137125)
out['bay_counterexample_covering_design_solids']=[{'name':s['name'],'top_y':s['top_y'],'kind':s['kind']} for g in d['groups'] for s in g['solids'] if any(Polygon([s['vertices_xz'][i] for i in t]).distance(p)<1e-4 for t in s['cap_triangles'])]
out['status']='REJECT combined 24l terrain plus 24j paving: actual bay cap penetrated 0.75m; actual foreground stacked caps match runtime failure. Further foundation-region audit intentionally deferred after sufficient rejecting counterexamples.'
out['foundation_region_audit']='Not completed: actual house assets identified, but rejecting cap counterexamples found before comparing nine foundation regions.'
path.write_text(json.dumps(out,indent=2),encoding='utf-8');print(out['upper_border']);print(out['bay_counterexample_covering_design_solids'])
