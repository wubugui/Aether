"""Native alpine east-facing light planes, with unchanged geometry."""
from pathlib import Path
import bpy,json,math,numpy as np,hashlib,sys
from mathutils import Vector
root=Path('D:/test6');label='11i'
prior=root/'captures/mountain_study_11h';out=root/'captures/mountain_study_11i';assert not out.exists();out.mkdir()
sun=Vector((-.48,-.30,.82)).normalized();report=[];phases=[.18,.53,.37,.71,.16,.42,.83,.39,.63,.25,.51]
for i,item in enumerate(json.loads((prior/'manifest.json').read_text())):
 name=item['name'];bpy.ops.wm.open_mainfile(filepath=str(prior/(name+'.blend')));obj=bpy.data.objects[name];mesh=obj.data
 peak=max(v.co.z for v in mesh.vertices);attr=mesh.color_attributes['Palette']
 for face in mesh.polygons:
  light=max(0,face.normal.dot(sun));h=face.center.z
  snowline=peak*.30+12*math.sin(face.center.x*.018+phases[i])
  snow=peak>140 and h>snowline and (face.normal.z>.32 or h>peak*.72)
  if i==0:
   local=np.array([face.center.x,-face.center.y]);rib=np.array([(.265,.005),(.24,.105),(.17,.23),(.20,.36),(.18,.52),(.24,.69)])*520;distance=1e9
   for a,b in zip(rib[:-1],rib[1:]):
    d=b-a;t=np.clip(np.dot(local-a,d)/max(np.dot(d,d),1e-8),0,1);distance=min(distance,float(np.linalg.norm(local-a-d*t)))
   snow=snow and not(distance<35 and 75<h<peak*.74)
  if snow:c=np.array([232,231,227])/255*(np.array([.75,.80,.92])*(1-light)+light)
  else:c=np.array([134,153,176])/255*(.70+.34*light)
  if h<26:c=np.array([157,170,130])/255*(.72+.29*light)
  elif not snow:c+=np.array([.04,0,.03])
  c=np.clip(c,0,1);c=np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
  for k in face.loop_indices:attr.data[k].color=(*c,1)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 obj['modeling_study']='Neutral warm-white lit snow, cold blue shade and ridge-aware exposed rock; native face painting'
 target=out/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
 bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
 row=dict(item);row.update(glb_sha256=hashlib.sha256(target.read_bytes()).hexdigest());report.append(row)
(out/'manifest.json').write_text(json.dumps(report,indent=2));(root/'captures'/('preview_alpine_'+label+'.gd')).write_text((root/'captures/preview_alpine_11a.gd').read_text().replace('11a',label))
