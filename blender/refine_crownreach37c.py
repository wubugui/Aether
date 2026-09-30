"""Lower the observed raised courtyard blocks; preserve 37b architecture."""
from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[1];OUT=R/'captures/crownreach_study_37c';OUT.mkdir(exist_ok=False)
SOURCE=R/'captures/crownreach_study_37b/castle.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));changes=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':continue
    if obj.name.startswith('Courtyard paving'):
        for v in obj.data.vertices:v.co.z-=.55
        changes.append({'name':obj.name,'height_delta':-.55,'reason':'37b gate-low showed 0.6m abrupt doorstep; retain embedded bottom and lower top to local .20m'})
    elif obj.name=='East gallery embedded floor':
        for v in obj.data.vertices:
            if v.co.z>.5:v.co.z-=.4
        changes.append({'name':obj.name,'top_delta':-.4,'reason':'Match the adjacent courtyard height'})
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'castle.blend'))
bpy.ops.object.select_all(action='DESELECT')
parts=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in parts:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'castle.glb'),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
report={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'changes':changes,'parts':len(parts),'instance_origin':[43.288,18.845,-282.521],'instance_scale':[1,1,1],'scope':'Only 40 pavement meshes and adjacent gallery floor lowered; source geometry else retained.'}
(OUT/'model-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(OUT/'builder.py').write_text(Path(__file__).read_text(),encoding='utf-8')
print('CROWNREACH37C SAVED',len(parts),flush=True)
