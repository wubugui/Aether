"""Inspect candidate native polygons without changing the Blender file."""
import bpy,json,sys,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
label=sys.argv[sys.argv.index('--')+1]
source=root/'captures'/('lighthouse_study_'+label)/'lighthouse.blend'
output=root/'reviews'/('round-'+label+'-source-face-check.json')
assert not output.exists()
bpy.ops.wm.open_mainfile(filepath=str(source))
issues=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':continue
    for p in obj.data.polygons:
        if p.area<1.e-10:issues.append({'object':obj.name,'polygon':p.index,'area':p.area})
report={'scope':'Native zero-area polygon inspection only; not complete topology or visual acceptance.','passed':not issues,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'issues':issues}
output.write_text(json.dumps(report,indent=2))
print(json.dumps(report),flush=True)
