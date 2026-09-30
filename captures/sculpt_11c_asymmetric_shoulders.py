"""Local native snow-shoulder brushes with fixed summit, back and foot slopes."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,shutil
root=Path('D:/test6');prior=root/'captures/mountain_study_11b';out=root/'captures/mountain_study_11c';assert not out.exists();out.mkdir()
items=json.loads((prior/'manifest.json').read_text());report=[]
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
for item in items:
 name=item['name']
 if name not in ['massif_frost_crown','massif_west_summit']:
  for ext in ['glb','blend']:shutil.copy2(prior/(name+'.'+ext),out/(name+'.'+ext))
  report.append(item);continue
 bpy.ops.wm.open_mainfile(filepath=str(prior/(name+'.blend')));obj=bpy.data.objects[name];mesh=obj.data
 group=obj.vertex_groups.new(name='Sculpt east snow shoulder');count=0
 for v in mesh.vertices:
  x,z,h=v.co.x,-v.co.y,v.co.z
  if name=='massif_frost_crown':
   brush=math.exp(-((x-82)/98)**2-((z+28)/78)**2)*smooth(0,32,x)*smooth(180,300,h)
   amount=62
  else:
   brush=math.exp(-((x-46)/64)**2-((z+24)/55)**2)*smooth(0,22,x)*smooth(190,280,h)
   amount=26
  if brush<.005:continue
  v.co.z+=amount*brush;group.add([v.index],brush,'REPLACE');count+=1
 mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(len(e.link_faces)==2 for e in bm.edges)
 volume=abs(bm.calc_volume(signed=True));bm.to_mesh(mesh);bm.free();mesh.update()
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 obj['modeling_study']='Asymmetric east snow shoulder; native world-space metre brush, fixed summit and XZ footprint'
 target=out/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
 row=dict(item);row.update(glb_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),changed_vertices=count,volume_m3=volume);report.append(row);print(name,count,flush=True)
(out/'manifest.json').write_text(json.dumps(report,indent=2));(root/'captures/preview_alpine_11c.gd').write_text((root/'captures/preview_alpine_11a.gd').read_text().replace('11a','11c'))
