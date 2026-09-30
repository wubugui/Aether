"""Native slope-aware meadow transition beneath the separate alpine modules."""
from pathlib import Path
import bpy,json,math,numpy as np,hashlib
from mathutils import Vector
root=Path('D:/test6');prior=root/'captures/mountain_study_11c';out=root/'captures/mountain_study_11d';assert not out.exists();out.mkdir()
report=[]
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
sun=Vector((-.48,-.30,.82)).normalized()
for item in json.loads((prior/'manifest.json').read_text()):
 name=item['name'];bpy.ops.wm.open_mainfile(filepath=str(prior/(name+'.blend')));obj=bpy.data.objects[name];mesh=obj.data
 peak=max(v.co.z for v in mesh.vertices);attr=mesh.color_attributes['Palette'];changed=0
 for face in mesh.polygons:
  x,z,h=face.center.x,-face.center.y,face.center.z
  line=max(40,min(115,peak*.35))+20*math.sin(x*.018+z*.007)
  blend=(1-smooth(line-25,line+15,h))*smooth(.2,.65,face.normal.z)
  if blend<.01 or h<0:continue
  light=max(0,face.normal.dot(sun));green=np.array([141,155,119])/255*(.78+.25*light)
  for k in face.loop_indices:
   c=np.asarray(attr.data[k].color[:3]);c=np.where(c<=.0031308,c*12.92,1.055*np.maximum(c,0)**(1/2.4)-.055)
   c=c*(1-blend)+green*blend;c=np.clip(c,0,1);c=np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
   attr.data[k].color=(*c,1)
  changed+=1
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 obj['modeling_study']='Blue-violet rock, snow shoulder and slope-dependent meadow toes painted on native faces'
 target=out/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
 row=dict(item);row.update(glb_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),foothill_faces=changed);report.append(row);print(name,changed,flush=True)
(out/'manifest.json').write_text(json.dumps(report,indent=2));(root/'captures/preview_alpine_11d.gd').write_text((root/'captures/preview_alpine_11a.gd').read_text().replace('11a','11d'))
