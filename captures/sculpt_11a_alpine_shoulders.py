"""Native Blender study of broader upper shoulders, preserving every footprint."""
from pathlib import Path
import bpy,bmesh,json,math,numpy as np,hashlib
root=Path('D:/test6');out=root/'captures/mountain_study_11a'
assert not out.exists();out.mkdir()
kit=json.loads((root/'assets/mountain_kit.json').read_text());report=[]
for item in kit[:7]:
 source=root/item['native_source'];before=hashlib.sha256(source.read_bytes()).hexdigest()
 bpy.ops.wm.open_mainfile(filepath=str(source))
 obj=bpy.data.objects[item['name']];mesh=obj.data
 peak=max(v.co.z for v in mesh.vertices);changed=0
 for v in mesh.vertices:
  h=v.co.z
  if h<=15:continue
  t=max(0,min(1,h/peak));fade=max(0,min(1,(h-15)/35));fade=fade*fade*(3-2*fade)
  v.co.z=h+peak*.13*math.sin(math.pi*t)**1.4*fade;changed+=1
 mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 assert all(len(e.link_faces)==2 for e in bm.edges)
 volume=abs(bm.calc_volume(signed=True));bm.to_mesh(mesh);bm.free();mesh.update()
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 obj['modeling_study']='Raised upper shoulders and drainage benches in native mesh; local XZ footprint and summit remain fixed'
 target=out/(item['name']+'.glb')
 bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(item['name']+'.blend')))
 row={'name':item['name'],'native_before_sha256':before,'glb_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'changed_vertices':changed,'volume_m3':volume,'summit_m':peak}
 report.append(row);print('STUDY',item['name'],changed,flush=True)
(out/'manifest.json').write_text(json.dumps(report,indent=2))
