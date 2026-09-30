"""Native Blender proportion remodeling with constrained full-size pad/path topology."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,shutil,collections
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
R=Path(__file__).resolve().parents[1];SRC=R/'captures/lantern_island_study_29e/island_c.blend';OUT=R/'captures/lantern_island_study_30a';assert not OUT.exists();OUT.mkdir()
shutil.copy2(__file__,OUT/'builder.py');shutil.copy2(R/'captures/island-30a-proportion-plan.json',OUT/'proportion-plan.json');plan=json.loads((OUT/'proportion-plan.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(SRC))
tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths';cn='island_c faulted bedrock';terrain=bpy.data.objects[tn];path=bpy.data.objects[pn];core=bpy.data.objects[cn]
def sig(o):return {'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'materials':[p.material_index for p in o.data.polygons]}
old={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'}
scale=plan['land_scale_blender_xyz']
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  for v in o.data.vertices:v.co=(v.co.x*scale[0],v.co.y*scale[1],v.co.z*scale[2])
source=plan['source_scaled_terrain_vertices'];source_top=plan['source_top_triangles'];source_n=plan['source_top_vertex_count']
def surface(x,y):
 for face in source_top:
  a,b,c=[source[i] for i in face]
  if x<min(a[0],b[0],c[0])-1e-4 or x>max(a[0],b[0],c[0])+1e-4 or y<min(a[1],b[1],c[1])-1e-4 or y>max(a[1],b[1],c[1])+1e-4:continue
  det=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/det;v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/det;w=1-u-v
  if min(u,v,w)>=-1e-4:return u*a[2]+v*b[2]+w*c[2]
 raise AssertionError(('missing source surface',x,y))
def edge_distance(p,a,b):
 p,a,b=Vector(p),Vector(a),Vector(b);d=b-a;t=max(0.,min(1.,(p-a).dot(d)/max(d.length_squared,1e-20)));return (p-a-t*d).length
def inside(p,polygon):
 x,y=p;yes=False
 for a,b in zip(polygon,polygon[1:]+polygon[:1]):
  if edge_distance(p,a,b)<2e-5:return True
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes
for site in plan['sites']:site['height']=surface(*site['center'])
points,edges,faces,orig,_,_=delaunay_2d_cdt([Vector(p) for p in plan['cdt_points']],plan['cdt_edges'],[plan['cdt_outline']],1,.00001)
assert all(len(f)==3 for f in faces)
top=[]
for p in points:
 base=surface(p.x,p.y);candidates=[]
 for site in plan['sites']:
  poly=site['polygon']
  if inside((p.x,p.y),poly):candidates.append((1.,site['height']))
  else:
   distance=min(edge_distance((p.x,p.y),a,b) for a,b in zip(poly,poly[1:]+poly[:1]))
   if distance<3.5:
    f=distance/3.5;candidates.append((1-f*f*(3-2*f),site['height']))
 if candidates:
  w,h=max(candidates);base=base*(1-w)+h*w
 top.append((p.x,p.y,base))
n=len(top);lower=[(x,y,z-.65) for x,y,z in top]
counts=collections.Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in faces for i in range(3));border=[e for e,c in counts.items() if c==1]
assert len(border)==18,len(border)
capfaces=[list(f) for f in faces]+[[i+n for i in reversed(f)] for f in faces]+[[a,b,b+n,a+n] for a,b in border]
def replace(o,verts,polys):
 mats=list(o.data.materials);data=bpy.data.meshes.new(o.name+' 30a topology');data.from_pydata(verts,[],polys);data.update();o.data=data
 for m in mats:data.materials.append(m)
replace(terrain,top+lower,capfaces)
for p in terrain.data.polygons:p.material_index=0 if p.index<len(faces) and p.normal.z>.85 and p.center.z>8 else (2 if p.normal.x<-.60 else 3)
prior=json.loads((R/'captures/lantern_island_study_29e/terrain-plan.json').read_text());mapping=[]
for old_index in prior['core_boundary_map']:
 q=source[old_index];j=min(range(n),key=lambda i:(top[i][0]-q[0])**2+(top[i][1]-q[1])**2);assert (top[j][0]-q[0])**2+(top[j][1]-q[1])**2<1e-8;mapping.append(j)
assert len(set(mapping))==18
coreverts=[list(v.co) for v in core.data.vertices[:54]]+lower;corefaces=[list(reversed(range(18)))]
for level in range(3):
 for i in range(18):
  j=(i+1)%18;a=level*18+i;b=level*18+j;c=(level+1)*18+j if level<2 else 54+mapping[j];d=(level+1)*18+i if level<2 else 54+mapping[i]
  corefaces.extend([[a,b,d],[b,c,d]] if (i+level)%2 else [[a,b,c],[a,c,d]])
corefaces += [[54+i for i in f] for f in faces];replace(core,coreverts,corefaces)
for p in core.data.polygons:p.material_index=2 if p.center.z<.6 else (1 if p.normal.x<-.60 and p.normal.z<.5 else 0)
selected=[]
for f in faces:
 cx=sum(top[i][0] for i in f)/3;cy=sum(top[i][1] for i in f)/3
 if any(inside((cx,cy),rings[0]) and not any(inside((cx,cy),h) for h in rings[1:]) for rings in plan['road_polygons']):selected.append(f)
used=sorted({i for f in selected for i in f});lookup={i:j for j,i in enumerate(used)};pv=[(top[i][0],top[i][1],top[i][2]+.045) for i in used];np=len(pv);pf=[[lookup[i] for i in f] for f in selected]
pc=collections.Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in pf for i in range(3));pathfaces=pf+[[i+np for i in reversed(f)] for f in pf]+[[a,b,b+np,a+np] for (a,b),c in pc.items() if c==1]
pv += [(x,y,z-.35) for x,y,z in pv];replace(path,pv,pathfaces)
native=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),(o.name,'not closed');assert all(f.calc_area()>1e-10 for f in bm.faces),(o.name,'zero face')
 vol=bm.calc_volume(signed=True);assert vol>0,(o.name,vol);bm.to_mesh(o.data);bm.free();native.append({'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'volume_m3':vol})
plan.update(top_vertex_count=n,path_top_triangles=len(pf),core_cap_offset=54,core_boundary_map=mapping)
(OUT/'proportion-plan.json').write_text(json.dumps(plan,indent=2));bpy.context.scene['scope']=plan['scope'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'island_c.blend'))
(OUT/'geometry-evidence.json').write_text(json.dumps({'old':old,'new':{o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'},'sites':plan['sites'],'land_scale':scale}),encoding='utf-8')
groups={}
for o in list(bpy.context.scene.objects):
 if o.type=='MESH':groups.setdefault(o.data.materials[0].name,[]).append(o)
for material,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 if len(objects)>1:bpy.ops.object.join()
 bpy.context.object.name='island_c_'+material
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(OUT/'island_c.glb'),export_format='GLB',use_selection=True,export_apply=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(OUT/'model-report.json').write_text(json.dumps({'label':'30a','source_basis':str(SRC.relative_to(R)),'source_basis_sha256':sha(SRC),'source_sha256':sha(OUT/'island_c.blend'),'glb_sha256':sha(OUT/'island_c.glb'),'native':native,'scope':plan['scope']},indent=2));print('30a BLENDER NATIVE PROPORTIONS SAVED '+str(n)+' terrain vertices '+str(len(pf))+' road triangles',flush=True)
