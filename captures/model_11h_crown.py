"""Complete native crown massif, rebuilt from unequal ridge/valley controls."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,shutil,numpy as np
from mathutils import Vector,noise
from mathutils.geometry import delaunay_2d_cdt
root=Path('D:/test6');out=root/'captures/mountain_study_11h';prior=root/'captures/mountain_study_11b';assert not out.exists();out.mkdir()
items=json.loads((prior/'manifest.json').read_text());name='massif_frost_crown'
for item in items[1:]:
 for ext in ['glb','blend']:shutil.copy2(prior/(item['name']+'.'+ext),out/(item['name']+'.'+ext))
bpy.ops.wm.open_mainfile(filepath=str(prior/(name+'.blend')));obj=bpy.data.objects[name];height=max(v.co.z for v in obj.data.vertices)
points=[];edges=[];groups={}
def point(p):
 p=tuple(p)
 if p in points:return points.index(p)
 points.append(p);return len(points)-1
def chain(label,coords):
 ids=[point(p) for p in coords];edges.extend(zip(ids[:-1],ids[1:]));groups[label]=ids
outline=[(-.90,-.59),(-.44,-.94),(.16,-.93),(.68,-.66),(.95,-.16),(.87,.34),(.55,.74),(.03,.96),(-.51,.82),(-.90,.40),(-1,-.06)]
border=[point((x*(1+.06*math.sin(i)),z*(1+.06*math.cos(i*2)),-.012)) for i,(x,z) in enumerate(outline)];edges.extend(zip(border,border[1:]+border[:1]))
peak=(0,0,1)
chain('North summit ridge',[(-.34,-.73,.09),(-.24,-.51,.31),(-.12,-.34,.52),(-.07,-.19,.76),peak])
chain('East corniced shoulder',[peak,(.085,-.038,.965),(.175,-.055,.835),(.265,.005,.65),(.36,.16,.45),(.48,.39,.19),(.58,.64,.04)])
chain('West shoulder and col',[peak,(-.14,.028,.845),(-.205,.125,.585),(-.31,.245,.64),(-.43,.365,.40),(-.62,.54,.16),(-.76,.48,.035)])
chain('South descending rock rib',[peak,(-.04,.12,.68),(-.015,.26,.45),(.09,.39,.32),(.05,.56,.18),(-.08,.76,.035)])
chain('Inner snow gully',[(.065,.085,.615),(.105,.20,.40),(.095,.36,.23),(.12,.55,.075),(.15,.72,.025)])
chain('Front rock spur',[(.265,.005,.65),(.24,.105,.48),(.17,.23,.59),(.20,.36,.37),(.18,.52,.19),(.24,.69,.04)])
chain('Outer snow gully',[(.28,.12,.44),(.33,.235,.31),(.395,.39,.16),(.45,.56,.055),(.48,.65,.025)])
chain('Western valley',[(-.12,.06,.63),(-.23,.24,.36),(-.34,.40,.19),(-.49,.64,.045)])
chain('Northwest hollow',[(-.16,-.16,.59),(-.32,-.20,.39),(-.49,-.12,.21),(-.69,.06,.045)])
chain('Northeast spur',[(-.07,-.19,.76),(.105,-.27,.625),(.29,-.40,.43),(.48,-.59,.20),(.62,-.64,.03)])
chain('Rear basin',[(.00,-.41,.32),(.05,-.63,.17),(.17,-.79,.04)])
chain('Western low ridge',[(-.24,-.51,.31),(-.47,-.49,.27),(-.65,-.30,.14),(-.83,-.16,.035)])
chain('East foothill spur',[(.265,.005,.65),(.43,-.075,.405),(.63,.015,.22),(.80,.16,.03)])
for p in [(-.53,-.67,.085),(.34,-.72,.105),(-.78,.29,.06),(.71,.42,.065),(-.17,.53,.13),(.04,.075,.785)]:point(p)
coords=[Vector((p[0]*520,p[1]*520)) for p in points]
xy,_,faces,original,_,_=delaunay_2d_cdt(coords,edges,[],0,.00001,True);verts=[]
for p,ids in zip(xy,original):
 if ids:h=sum(points[i][2] for i in ids)/len(ids)
 else:
  values=[]
  for a,b in edges:
   aa=np.array(coords[a]);bb=np.array(coords[b]);d=bb-aa;t=np.clip(np.dot(np.array(p)-aa,d)/max(np.dot(d,d),1e-12),0,1)
   if np.linalg.norm(np.array(p)-aa-d*t)<.001:values.append(points[a][2]*(1-t)+points[b][2]*t)
  assert values;h=sum(values)/len(values)
 verts.append([p.x,-p.y,h*height])
faces=[tuple(f) for f in faces];counts={}
for f in faces:
 for a,b in zip(f,f[1:]+f[:1]):key=tuple(sorted((a,b)));counts[key]=counts.get(key,0)+1
boundary=[e for e,n in counts.items() if n==1];bottom={}
for a,b in boundary:
 for i in [a,b]:
  if i not in bottom:bottom[i]=len(verts);verts.append([verts[i][0],verts[i][1],-12])
 faces.extend([(a,b,bottom[b]),(a,bottom[b],bottom[a])])
center=len(verts);verts.append([0,0,-12])
for a,b in boundary:faces.append((bottom[b],bottom[a],center))
mesh=bpy.data.meshes.new('Frost Crown ridge valley control mesh');mesh.from_pydata(verts,[],faces);mesh.update()
obj.data=mesh;obj.vertex_groups.clear()
for label,ids in groups.items():
 group=obj.vertex_groups.new(name=label)
 for i,orig in enumerate(original):
  if any(k in ids for k in orig):group.add([i],1,'REPLACE')
bm=bmesh.new();bm.from_mesh(mesh);prior_vertices=set(bm.verts)
exposed=[e for e in bm.edges if e.calc_length()>135 and all(v.co.z>35 for v in e.verts)]
bmesh.ops.subdivide_edges(bm,edges=exposed,cuts=1,use_grid_fill=True)
for vertex in bm.verts:
 if vertex not in prior_vertices:
  t=max(0,min(1,vertex.co.z/height));vertex.co.z+=noise.noise_vector(vertex.co*.025+Vector((3.1,7.2,2.3))).z*12*math.sin(math.pi*t)
bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(len(e.link_faces)==2 for e in bm.edges)
volume=abs(bm.calc_volume(signed=True));bm.to_mesh(mesh);bm.free();mesh.update()
attr=mesh.color_attributes.new(name='Palette',type='FLOAT_COLOR',domain='CORNER');sun=Vector((-.48,-.30,.82)).normalized()
for face in mesh.polygons:
 light=max(0,face.normal.dot(sun));h=face.center.z;snowline=height*.30+12*math.sin(face.center.x*.018+.18)
 local=np.array([face.center.x,-face.center.y]);rib=[np.array(points[k][:2])*520 for k in groups['Front rock spur']];distance=1e9
 for a,b in zip(rib[:-1],rib[1:]):
  d=b-a;t=np.clip(np.dot(local-a,d)/max(np.dot(d,d),1e-8),0,1);distance=min(distance,float(np.linalg.norm(local-a-d*t)))
 exposed_rib=distance<35 and 75<h<height*.74
 snow=h>snowline and (face.normal.z>.32 or h>height*.72) and not exposed_rib
 if snow:c=np.array([234,231,225])/255*(np.array([.75,.80,.90])*(1-light)+light)
 else:c=np.array([134,153,176])/255*(.70+.34*light)
 if h<26:c=np.array([157,170,130])/255*(.72+.29*light)
 elif snow:c+=np.array([.02,0,.045])*(1-light)+np.array([.025,.008,.018])*light
 else:c+=np.array([.035,0,.045])
 c=np.clip(c,0,1);c=np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
 for k in face.loop_indices:attr.data[k].color=(*c,1)
mesh.color_attributes.active_color_index=0;mesh.color_attributes.render_color_index=0
mat=bpy.data.materials.new('Frost Crown snow and blue rock');mat.use_nodes=True;nt=mat.node_tree;node=nt.nodes.new('ShaderNodeVertexColor');node.layer_name='Palette';bsdf=nt.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=1;nt.links.new(node.outputs['Color'],bsdf.inputs['Base Color']);mesh.materials.append(mat)
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;obj['modeling_study']='Explicit asymmetric summit shoulder col ridge and drainage network, fully closed independent asset';obj['closed_volume_m3']=volume
target=out/(name+'.glb');bpy.ops.export_scene.gltf(filepath=str(target),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE');bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'.blend')))
items[0].update(glb_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),vertices=len(mesh.vertices),faces=len(mesh.polygons),volume_m3=volume,control_vertices=len(points),named_chains=list(groups))
(out/'manifest.json').write_text(json.dumps(items,indent=2));(root/'captures/preview_alpine_11h.gd').write_text((root/'captures/preview_alpine_11a.gd').read_text().replace('11a','11h'));print(items[0],flush=True)
