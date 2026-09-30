"""Settle only the native plateau's lower rim on the study terrain."""
from pathlib import Path
import sys,json,bpy,bmesh,numpy as np
from mathutils import Vector
root=Path('D:/test6');sys.path.insert(0,str(root/'blender'));sys.path.insert(0,str(root/'captures'))
import cliff_terrace_topology as C
import terrain_topology as T
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
# Track the original asset's terrain-contact band before changing the cage.
old_ground={v.index:ground_at(v.co.x+origin[0],-v.co.y+origin[2]) for v in mesh.vertices if v.co.z> -14}
import cliff_sections_10d
C.SAMPLER=T.SurfaceSampler()
changed=[]
for v in mesh.vertices:
    if v.index not in old_ground:continue
    old=old_ground[v.index]
    fresh=ground_at(v.co.x+origin[0],-v.co.y+origin[2])
    weight=1-float(cliff_sections_10d.W.smooth(3,12,v.co.z-old))
    target=v.co.z+(fresh-old)*weight
    if v.index in rim:target=fresh-1.5
    if abs(target-v.co.z)>.001:changed.append([v.index,float(v.co.z),target])
    v.co.z=target
# Split only the shared contact edge and its two adjacent triangles.
# This avoids subdivision adding unrelated face-interior vertices.
vertices=[np.array(v.co) for v in mesh.vertices]
faces=[tuple(f.vertices) for f in mesh.polygons]
rim_edges=[tuple(e.vertices) for e in mesh.edges if all(k in rim for k in e.vertices)]
import math
for a,b in rim_edges:
    aa,bb=vertices[a],vertices[b]
    count=math.ceil(np.linalg.norm((aa-bb)[:2])/3)
    if count<=1:continue
    curve=[a]
    for j in range(1,count):
        p=aa*(1-j/count)+bb*(j/count)
        p[2]=ground_at(p[0]+origin[0],-p[1]+origin[2])-1.5
        curve.append(len(vertices));vertices.append(p)
    curve.append(b)
    adjacent=[i for i,f in enumerate(faces) if a in f and b in f]
    assert len(adjacent)==2
    for i in adjacent:
        face=faces[i];c=next(k for k in face if k not in (a,b))
        path=curve if face[(face.index(a)+1)%3]==b else curve[::-1]
        replacements=[(c,x,y) for x,y in zip(path,path[1:])]
        faces[i]=replacements[0];faces.extend(replacements[1:])
# Rebuild the actual 2.5D roof with millimetre coordinate welding. The old
# CDT shell contains near-collinear needle strips that collapse in float32.
# Keep the edited native height controls; add no noise or artificial relief.
from mathutils.geometry import delaunay_2d_cdt
cloud={}
for p in vertices:
    if p[2]> -14:cloud.setdefault((round(float(p[0]),3),round(float(p[1]),3)),[]).append(float(p[2]))
controls=[[x,y,float(np.mean(z))] for (x,y),z in cloud.items()]
xy,_,roof,mapping,_,_=delaunay_2d_cdt([Vector(p[:2]) for p in controls],[],[],0,.002,True)
vertices=[[float(p.x),float(p.y),float(np.mean([controls[k][2] for k in ids]))] for p,ids in zip(xy,mapping)]
roof=[tuple(f) for f in roof]
edge_count={};oriented={}
for f in roof:
    for a,b in zip(f,f[1:]+f[:1]):
        key=tuple(sorted((a,b)));edge_count[key]=edge_count.get(key,0)+1;oriented[key]=(a,b)
boundary=[oriented[e] for e,count in edge_count.items() if count==1]
for k in {k for e in boundary for k in e}:
    p=vertices[k];p[2]=ground_at(p[0]+origin[0],-p[1]+origin[2])-1.5
count=len(vertices);vertices.extend([[x,y,-15.] for x,y,z in vertices[:]])
faces=list(roof)
faces.extend([(c+count,b+count,a+count) for a,b,c in roof])
for a,b in boundary:faces.extend([(b,a,a+count),(b,a+count,b+count)])
bm=bmesh.new()
for p in vertices:bm.verts.new(p)
bm.verts.ensure_lookup_table()
for f in faces:bm.faces.new([bm.verts[k] for k in f])
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
print('REBUILT CONTACT SHELL',len(bm.verts),len(bm.faces),'bad edges',sum(len(e.link_faces)!=2 for e in bm.edges),'degenerate',sum(f.calc_area()<=1e-8 for f in bm.faces),flush=True)
assert all(len(e.link_faces)==2 for e in bm.edges) and all(f.calc_area()>1e-8 for f in bm.faces)
volume=abs(bm.calc_volume());bm.to_mesh(mesh);bm.free();mesh.update()
sun=Vector((-.48,-.30,.82)).normalized();attr=mesh.color_attributes.get('Palette') or mesh.color_attributes.new(name='Palette',type='FLOAT_COLOR',domain='CORNER')
def rgb(h):return np.array([int(h[k:k+2],16)/255 for k in (0,2,4)])
for face in mesh.polygons:
    light=max(0,face.normal.dot(sun));grass=face.normal.z>.8 and face.center.z>5
    c=rgb(['929f78','9fac81','8f9f79'][face.index%3])*(.65+.32*light) if grass else rgb('616e78')*(1-light)+rgb('bcb8ad')*light
    c=np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
    for k in face.loop_indices:attr.data[k].color=(*c,1)
obj['closed_volume_m3']=volume
contact=[v.index for v in mesh.vertices if v.co.z> -14 and abs(v.co.z-(ground_at(v.co.x+origin[0],-v.co.y+origin[2])-1.5))<.02]
obj.vertex_groups.new(name='Seated ground rim').add(contact,1.,'REPLACE')
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
path=root/'captures/cliff_sections_10i_eastern_plateau'
bpy.ops.export_scene.gltf(filepath=str(path.with_suffix('.glb')),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
bpy.ops.wm.save_as_mainfile(filepath=str(path.with_suffix('.blend')))
report={'asset':item['name'],'rim_vertices':len(rim),'changed':changed,'volume_m3':volume,'vertices':len(mesh.vertices),'faces':len(mesh.polygons)}
(root/'captures/round-10i-plateau-seating.json').write_text(json.dumps(report,indent=2))
preview=(root/'captures/preview_cliff_sections_10d.gd').read_text()
preview=preview.replace('\troot.add_child(game)','\treplace_asset(game.get_node("World/Cliffs/cliff_eastern_plateau"),"D:/test6/captures/cliff_sections_10i_eastern_plateau.glb")\n\troot.add_child(game)')
(root/'captures/preview_cliff_sections_10i.gd').write_text(preview)
print('Adjusted',len(changed),'native contact-band vertices; volume',volume,flush=True)
