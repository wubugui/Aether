"""Inspect native stair solids and top normals, independent of raster visibility."""
import bpy,bmesh,sys,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];label=sys.argv[sys.argv.index('--')+1]
source=root/'captures'/('lighthouse_study_'+label)/'lighthouse.blend'
output=root/'reviews'/('round-'+label+'-step-solid-check.json');assert not output.exists()
bpy.ops.wm.open_mainfile(filepath=str(source));records=[]
for obj in bpy.context.scene.objects:
    if not obj.name.startswith('Entry stone step'):continue
    bm=bmesh.new();bm.from_mesh(obj.data);bm.transform(obj.matrix_world);bm.normal_update()
    top=max(v.co.z for v in bm.verts)
    top_normals=[list(f.normal) for f in bm.faces if all(abs(v.co.z-top)<.0001 for v in f.verts)]
    volume=bm.calc_volume(signed=True);manifold=all(e.is_manifold for e in bm.edges)
    records.append({'name':obj.name,'volume_m3':volume,'manifold':manifold,'top_normals_blender':top_normals,'passed':volume>0 and manifold and len(top_normals)==1 and top_normals[0][2]>.99});bm.free()
assert len(records)==3
report={'scope':'Native stair closed-edge, signed volume and upward top-face inspection only.','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'passed':all(x['passed'] for x in records),'steps':records}
output.write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
