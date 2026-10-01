"""Fresh Blender process validates the saved union checkpoint only."""
import hashlib,json,sys
from pathlib import Path
import bpy
P=Path(__file__).resolve().parent;B=P.parent;A=B.parent
sys.path[:0]=[str(P),str(B),str(A)]
from verify_final58b import geometry
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((P/'union-geometry58b.json').read_text());assert before['native_union_geometry_passed']
assert before['source_sha256']==sha(P/'cloud_bank58b_union.blend')
bpy.ops.wm.open_mainfile(filepath=str(P/'cloud_bank58b_union.blend'))
row,*_=geometry(bpy.data.objects['CloudBank58B_four_root_folded_volume'])
exact=row==before['geometry'];passed=row['closed_geometry_passed'] and exact
(P/'union-fresh-readback58b.json').write_text(json.dumps(dict(passed=bool(passed),union_sha256=sha(P/'cloud_bank58b_union.blend'),saved_geometry_matches_live=exact,geometry=row,
    final_source_completed=False,world_loaded=False,rendered=False,visual_acceptance=False),indent=2)+'\n')
assert passed,'Saved union differs or fails; preserve checkpoint and failure'
print('Fresh saved union source readback passed; final facets and visual acceptance remain pending',flush=True)
