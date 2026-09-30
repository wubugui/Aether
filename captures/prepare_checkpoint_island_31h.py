from pathlib import Path
R=Path(__file__).resolve().parents[1];p=R/'captures/checkpoint_island_31h.py';assert not p.exists()
s=(R/'captures/checkpoint_island_31g.py').read_text(encoding='utf-8').replace('31g','31h')
s=s.replace('reference-view-1342-progress-31f.json','reference-view-1342-progress-31g.json')
s=s.replace("'independent-geometry.json','local-intersections.json','actual-tree-support.json',","'material-identity.json',").replace(",'full-depth-independent.json'",'')
s=s.replace('bindings=[dict(path=p,sha256=sha(R/p)) for p in reports]',"reports += ['reviews/round-31g-independent-geometry.json','reviews/round-31g-local-intersections.json','reviews/round-31g-actual-tree-support.json']\nbindings=[dict(path=p,sha256=sha(R/p)) for p in reports]")
s=s.replace('31f actual native source, rear sector cut and448 faces replaced by84 triangles using8 authored3D controls;637 old internal edges removed,70 boundary edges preserved.','31h material correction over actual31g identical native/GLB geometry. Only72 faces changed grass to exposed rock,12 upper faces retain grass. Exact identity report supports inherited31g geometric checks.')
s=s.replace('A/B20l; C/D31h actual rear topology replacement','A/B20l; C/D31h material correction on unchanged31g actual rear topology')
p.write_text(s,encoding='utf-8')
