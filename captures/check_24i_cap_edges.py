from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'captures/village_paving_design_24i/paving.json').read_text())
for group in data['groups']:
    for s in group['solids']:
        counts={}
        for tri in s['cap_triangles']:
            for a,b in zip(tri,tri[1:]+tri[:1]):
                e=tuple(sorted((a,b)));counts[e]=counts.get(e,0)+1
        caps={e for e,c in counts.items() if c==1};walls={tuple(sorted(e)) for e in s['boundary_edges']}
        if caps!=walls or any(c>2 for c in counts.values()):print(json.dumps({'name':s['name'],'max_cap_edge_use':max(counts.values()),'overused':[(e,c) for e,c in counts.items() if c>2],'cap_only':list(caps-walls),'wall_only':list(walls-caps),'vertices':s['vertices_xz']},indent=2))

