"""Settle only the native plateau's lower rim on the study terrain."""
from pathlib import Path
import sys,json,bpy,bmesh,numpy as np
from mathutils import Vector
root=Path('D:/test6');sys.path.insert(0,str(root/'blender'));sys.path.insert(0,str(root/'captures'))
import cliff_sections_10d
from cliff_terrace_topology import ground_at
item=next(i for i in json.loads((root/'assets/cliff_kit.json').read_text()) if i['name']=='cliff_eastern_plateau')
bpy.ops.wm.open_mainfile(filepath=str(root/item['native_source']))
obj=bpy.data.objects['cliff_eastern_plateau'];mesh=obj.data;origin=np.array(item['position'])
rim=set()
for edge in mesh.edges:
    a,b=[mesh.vertices[i] for i in edge.vertices]
    if (a.co.xy-b.co.xy).length>.001:continue
    if a.co.z< -14 and b.co.z> -14:rim.add(b.index)
    if b.co.z< -14 and a.co.z> -14:rim.add(a.index)
assert len(rim)>12
changed=[]
for k in rim:
    v=mesh.vertices[k];height=ground_at(v.co.x+origin[0],-v.co.y+origin[2])-1.5
    if abs(height-v.co.z)>.001:changed.append([k,float(v.co.z),height])
    v.co.z=height
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
assert all(len(e.link_faces)==2 for e in bm.edges) and all(f.calc_area()>1e-8 for f in bm.faces)
volume=abs(bm.calc_volume());bm.to_mesh(mesh);bm.free();mesh.update()
sun=Vector((-.48,-.30,.82)).normalized();attr=mesh.color_attributes['Palette']
def rgb(h):return np.array([int(h[k:k+2],16)/255 for k in (0,2,4)])
for face in mesh.polygons:
    light=max(0,face.normal.dot(sun));grass=face.normal.z>.8 and face.center.z>5
    c=rgb(['929f78','9fac81','8f9f79'][face.index%3])*(.65+.32*light) if grass else rgb('616e78')*(1-light)+rgb('bcb8ad')*light
    c=np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
    for k in face.loop_indices:attr.data[k].color=(*c,1)
obj['closed_volume_m3']=volume
obj.vertex_groups.new(name='Seated ground rim').add(sorted(rim),1.,'REPLACE')
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
path=root/'captures/cliff_sections_10e_eastern_plateau'
bpy.ops.export_scene.gltf(filepath=str(path.with_suffix('.glb')),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
bpy.ops.wm.save_as_mainfile(filepath=str(path.with_suffix('.blend')))
report={'asset':item['name'],'rim_vertices':len(rim),'changed':changed,'volume_m3':volume,'vertices':len(mesh.vertices),'faces':len(mesh.polygons)}
(root/'captures/round-10e-plateau-seating.json').write_text(json.dumps(report,indent=2))
preview=(root/'captures/preview_cliff_sections_10d.gd').read_text()
preview=preview.replace('\troot.add_child(game)','\treplace_asset(game.get_node("World/Cliffs/cliff_eastern_plateau"),"D:/test6/captures/cliff_sections_10e_eastern_plateau.glb")\n\troot.add_child(game)')
(root/'captures/preview_cliff_sections_10e.gd').write_text(preview)
print('Seated',len(changed),'of',len(rim),'native rim vertices; volume',volume,flush=True)
