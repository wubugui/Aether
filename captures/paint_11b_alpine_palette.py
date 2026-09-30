"""Palette-only native mountain study; geometry remains the integrated source."""
from pathlib import Path
import bpy,json,numpy as np,hashlib
root=Path('D:/test6');out=root/'captures/mountain_study_11b';assert not out.exists();out.mkdir()
kit=json.loads((root/'assets/mountain_kit.json').read_text());report=[]
for item in kit:
 source=root/item['native_source'];bpy.ops.wm.open_mainfile(filepath=str(source))
 obj=bpy.data.objects[item['name']];mesh=obj.data;attr=mesh.color_attributes['Palette']
 for face in mesh.polygons:
  if face.center.z<26:continue
  for k in face.loop_indices:
   c=np.asarray(attr.data[k].color[:3]);c=np.where(c<=.0031308,c*12.92,1.055*np.maximum(c,0)**(1/2.4)-.055)
   c=np.clip(c+np.array([.045,-.006,.04]),0,1)
   c=np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
   attr.data[k].color=(*c,1)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 obj['modeling_study']='Palette-only blue-violet rock and cool white snow; source geometry retained'
 target=out/(item['name']+'.glb')
 bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(item['name']+'.blend')))
 report.append({'name':item['name'],'native_before_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'volume_m3':item['volume_m3']})
(out/'manifest.json').write_text(json.dumps(report,indent=2))
preview=(root/'captures/preview_alpine_11a.gd').read_text().replace('11a','11b')
(root/'captures/preview_alpine_11b.gd').write_text(preview)
