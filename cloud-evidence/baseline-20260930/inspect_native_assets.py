import bpy,json,hashlib
from pathlib import Path
root=Path('/workspace/scratch/a29d03198654/Aether')
files=[root/'candidates/round40-exclusive-20260930/source-assets/hub-upper43/upper_cloud43.blend',root/'blender/cliff_kit/cliff_eastern_plateau.blend']
reports=[]
for file in files:
 before=hashlib.sha256(file.read_bytes()).hexdigest()
 bpy.ops.wm.open_mainfile(filepath=str(file),load_ui=False)
 reports.append({'path':str(file.relative_to(root)),'sha256':before,'blender':bpy.app.version_string,'mesh_objects':sum(o.type=='MESH' for o in bpy.data.objects),'materials':len(bpy.data.materials),'collections':len(bpy.data.collections),'vertices':sum(len(o.data.vertices) for o in bpy.data.objects if o.type=='MESH'),'unchanged':before==hashlib.sha256(file.read_bytes()).hexdigest()})
(root/'cloud-evidence/baseline-20260930/native-assets.json').write_text(json.dumps(reports,indent=2))
print(json.dumps(reports,indent=2))
