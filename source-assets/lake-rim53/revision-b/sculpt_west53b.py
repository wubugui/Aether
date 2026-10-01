"""Local additive, closed native ridge layers. No world regeneration or scene writes."""
import bpy,bmesh,json,math,random,collections,os,hashlib
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53'
ROOT='/workspace/scratch/a29d03198654/Aether'
OUT=D+'/revision-b'
base=json.load(open(D+'/base51b.json'))
paths={'massif_west_spur':D+'/original_west_spur.blend'}
SHA='b169f62527a52b9f2a3f091c2d7db136ad7cd67111e405f08f390eeb082e2bb1'
def tree(f):return BVHTree.FromPolygons([Vector(p) for p in f],[(i,i+1,i+2) for i in range(0,len(f),3)],all_triangles=True)
oldfaces=[p for r in base['meshes'].values() for p in r['faces']];oldtree=tree(oldfaces)
def height(tr,x,z):
 p,n,i,d=tr.ray_cast(Vector((x,1500,z)),Vector((0,-1,0)),3000)
 return None if p is None else p.y
# Every listed building uses its actual mesh footprint; northern six get the requested 50m margin.
protected=[]
for b in base['buildings']:
 margin=50 if any('_'+str(i)+'/' in b['node'] for i in range(57188,57194)) else 10
 protected.append({'node':b['node'],'xmin':b['min'][0]-margin,'xmax':b['max'][0]+margin,'zmin':b['min'][2]-margin,'zmax':b['max'][2]+margin,'margin':margin})
protected.append({'node':'conservative_west_village_envelope','xmin':508,'xmax':702,'zmin':-2000,'zmax':-1796,'margin':0})
def overlaps(pts,reg):
 return min(p[0] for p in pts)<=reg['xmax'] and max(p[0] for p in pts)>=reg['xmin'] and min(p[2] for p in pts)<=reg['zmax'] and max(p[2] for p in pts)>=reg['zmin']
def protected_face(pts):return any(overlaps(pts,r) for r in protected)
def key(t):return tuple(sorted(tuple(round(x,4) for x in p) for p in t))
def bco(p,org):return (p[0]-org[0],-p[2]+org[2],p[1]-org[1])
def world(v,org):return [v[0]+org[0],v[2]+org[1],-v[1]+org[2]]
def make_material(name,basecol):
 mat=bpy.data.materials.new(name);mat.diffuse_color=(*basecol,1);mat.use_nodes=True
 nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');vc=nt.nodes.new('ShaderNodeVertexColor');vc.layer_name='Palette';nt.links.new(vc.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.87
 return mat
report={'baseline_sha256':SHA,'source_equivalence':[],'buildings_protected':protected,'source_changes':[],'component_audits':[],'water_domain':'Actual saved51b highest triangles of six neighboring tiles and eleven mountain bodies. Local geometry audit only; no depth bake replaced.'}
payload={'schema_version':1,'baseline_sha256':SHA,'source_metadata':{'design':'Independent closed rock ridges and snow lenses over the authoritative native source, four targeted mountain families','scope':'Native source candidate only; parent must integrate and validate saved/runtime material, collisions, scatter and original cameras','authoring_coordinates':'Inferred scene design coordinates, not reference-derived metric facts'},'mountains':[],'scatter':[]}
# Crest knots: z, center x, western width, eastern width, height. Their asymmetry makes broad saddle/ribs.
knots={
'massif_west_spur':[(-2240,205,28,50,101),(-2180,211,154,207,179),(-2110,225,200,251,255),(-2030,242,221,257,299),(-1950,221,195,277,271),(-1880,222,182,279,229),(-1810,250,221,250,284),(-1730,278,232,217,256),(-1650,322,210,179,199),(-1570,375,163,126,135),(-1490,433,48,52,70)],
'massif_cirque_wall':[(-2133,745,35,36,114),(-2070,750,67,118,174),(-1990,753,49,128,226),(-1910,765,59,139,238),(-1840,780,70,125,201),(-1770,796,74,119,185),(-1690,783,102,100,176),(-1610,765,91,98,129),(-1545,747,45,60,74),(-1510,743,20,29,44)],
'massif_east_foothill':[(-2160,1770,60,70,95),(-2100,1744,184,174,232),(-2020,1760,260,255,295),(-1950,1792,310,263,328),(-1870,1818,321,282,286),(-1790,1790,312,292,244),(-1720,1815,299,264,282),(-1635,1850,240,220,226),(-1550,1854,183,193,165),(-1490,1890,90,98,100),(-1455,1905,26,32,40)]}
# Planned geological snow channels run across the slopes, not by camera or reference number.
def gully(z,u,name):
 shift=.065*math.sin((z+1910)/80)
 if name=='massif_west_spur':axes=[(.36+shift,.13),(-.43-shift,.105)]
 elif name=='massif_cirque_wall':axes=[(.38+shift,.14),(-.40,.09)]
 else:axes=[(-.34+shift,.115),(.44-shift,.13)]
 return max(math.exp(-((u-c)/w)**2) for c,w in axes)
def create_object(name,verts,faces,org,col_kind,mat):
 mesh=bpy.data.meshes.new(name+'_editable_mesh');mesh.from_pydata([bco(p,org) for p in verts],[],faces);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat)
 attr=mesh.color_attributes.new(name='Palette',type='FLOAT_COLOR',domain='CORNER')
 for poly in mesh.polygons:
  p=sum((mesh.vertices[i].co for i in poly.vertices),Vector())/len(poly.vertices);w=world(p,org);v=.026*math.sin(w[0]*.079+w[2]*.048)
  if col_kind=='snow':
   shade=max(-.065,min(.06,poly.normal.x*.045+poly.normal.y*.035))
   col=(.48+v+shade,.59+v+shade,.70+v+shade,1)
  elif col_kind=='apron':col=(.32+v,.35+v,.34+v,1)
  else:
   # Broad cool stone planes; small warm faces above the shoulder retain material hierarchy.
   col=(.17+v,.225+v,.285+v,1)
  for li in poly.loop_indices:attr.data[li].color=col
 return o

def lens(name,verts,faces,selection,org,kind,mat,thick=1.8):
 # Closed union of selected triangles, matching the actual underlying triangle surface.
 if not selection:return None
 # Split separate face fans at a shared vertex so corner-touching snow patches remain manifold.
 incident=collections.defaultdict(list)
 for fi in selection:
  for vi in faces[fi]:incident[vi].append(fi)
 fanmap={};top=[];bottom=[]
 for vi,fl in incident.items():
  pending=set(fl)
  while pending:
   todo=[pending.pop()];fan=[]
   while todo:
    fi=todo.pop();fan.append(fi)
    shared=set(faces[fi])-{vi}
    near=[fj for fj in pending if shared.intersection(set(faces[fj])-{vi})]
    for fj in near:pending.remove(fj);todo.append(fj)
   idx=len(top);x,y,z=verts[vi];t=thick*(.8+.2*math.sin(x*.023+z*.028))
   top.append([x,y+t,z]);bottom.append([x,y-.32,z])
   for fi in fan:fanmap[(fi,vi)]=idx
 n=len(top);newfaces=[];counts=collections.Counter()
 for fi in selection:
  a,b,c=[fanmap[(fi,i)] for i in faces[fi]];newfaces.append((a,b,c));newfaces.append((c+n,b+n,a+n))
  for e in [(a,b),(b,c),(c,a)]:counts[e]+=1
 for a,b in list(counts):
  if (b,a) not in counts:newfaces.extend([(a,a+n,b+n),(a,b+n,b)])

 ec=collections.Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in newfaces for i in range(3))
 bad={str(e):n for e,n in ec.items() if n!=2}
 if bad:print('LENS_DEBUG',name,bad,flush=True)
 return create_object(name,top+bottom,newfaces,org,kind,mat)

def grid_ridge(name,org,mat,snowmat):
 rows=[];kk=knots[name]
 for a,b in zip(kk,kk[1:]):
  steps=max(1,round((b[0]-a[0])/28))
  for step in range(steps):
   t=step/steps;rows.append([x*(1-t)+y*t for x,y in zip(a,b)])
 rows.append(kk[-1]);cols=15;verts=[];uv=[];surface_support=[]
 for r,(z,c,wl,wr,crest) in enumerate(rows):
  for k in range(cols):
   u=2*k/(cols-1)-1
   x=c+u*(wl if u<0 else wr)
   zz=z
   h=height(oldtree,x,zz)
   if h is None:raise RuntimeError(('missing real ground',name,x,zz))
   if h<4:raise RuntimeError(('ridge touches retained lake',name,x,zz,h))
   w=max(0,1-abs(u))**1.32
   longitudinal=min(1,r/1.3,(len(rows)-1-r)/1.3)
   rib=1-.165*gully(zz,u,name)*(1-abs(u))
   surface=h-7+max(0,crest-h+7)*w*longitudinal*rib
   if protected_face([[x,surface,zz]]):raise RuntimeError(('new ridge intersects protected footprint',name,x,zz))
   verts.append([x,surface,zz]);uv.append((u,zz));surface_support.append(h)
 faces=[]
 for r in range(len(rows)-1):
  for k in range(cols-1):
   a=r*cols+k;b=a+1;c=a+cols;d=c+1
   fs=[(a,c,b),(b,c,d)] if (r+k)%2 else [(a,c,d),(a,d,b)]
   for f in fs:
    p=[Vector(verts[i]) for i in f]
    # In world basis a Blender-equivalent upward face has a negative world cross.y.
    if (p[1]-p[0]).cross(p[2]-p[0]).y>0:f=tuple(reversed(f))
    faces.append(f)
 n=len(verts);bottom=[[p[0],surface_support[i]-23,p[2]] for i,p in enumerate(verts)]
 perimeter=list(range(cols))+[r*cols+cols-1 for r in range(1,len(rows))]+list(range(n-2,n-cols-1,-1))+[r*cols for r in range(len(rows)-2,0,-1)]
 closed=faces+[tuple(i+n for i in reversed(f)) for f in faces]
 for a,b in zip(perimeter,perimeter[1:]+perimeter[:1]):closed.extend([(a,b,b+n),(a,b+n,a+n)])
 ridge=create_object('ridge_shoulders',verts+bottom,closed,org,'rock',mat)
 cap=[];gull=[]
 for i,f in enumerate(faces):
  pp=[verts[a] for a in f];u=sum(uv[a][0] for a in f)/3;z=sum(p[2] for p in pp)/3;y=sum(p[1] for p in pp)/3
  p0,p1,p2=map(Vector,pp);nn=(p1-p0).cross(p2-p0).normalized();slope=abs(nn.y)
  # An irregular high cap, rocky ribs exposed between two lower snow-filled gullies.
  threshold=(159 if name!='massif_cirque_wall' else 147)+18*math.sin(z*.029)+24*max(0,-u)
  if y>threshold and slope>.45 and abs(u)<.70 and (gully(z,u,name)>.30 or (u>.05 and u<.48 and math.sin(z*.023+u*9)>.05) or (u<-.08 and u>-.35 and y>threshold+32)):
   cap.append(i)
  elif y>(89 if name!='massif_cirque_wall' else 77) and gully(z,u,name)>.47 and slope>.32 and abs(u)>.12:
   gull.append(i)
 snow1=lens('snow_cap',verts,faces,cap,org,'snow',snowmat,2.2)
 snow2=lens('snow_gully',verts,faces,gull,org,'snow',snowmat,1.35)
 # Low rock skirt remains a separate closed editable layer across actual shoulder triangles.
 apron=[]
 for i,f in enumerate(faces):
  y=sum(verts[a][1] for a in f)/3;u=sum(uv[a][0] for a in f)/3
  if 18<y<105 and (u>.48 if name!='massif_east_foothill' else u<-.48):apron.append(i)
 apron_obj=lens('shore_rock_apron',verts,faces,apron,org,'apron',mat,.8)
 return [o for o in [ridge,snow1,snow2,apron_obj] if o]

for name,src in paths.items():
 bpy.ops.wm.open_mainfile(filepath=src);original=next(o for o in bpy.data.objects if o.type=='MESH');m=original.data;org=base['meshes'][name]['origin'];r=base['meshes'][name]
 for o in list(bpy.data.objects):
  if o!=original:bpy.data.objects.remove(o,do_unlink=True)
 kd=KDTree(len(r['faces']))
 for i,p in enumerate(r['faces']):kd.insert(p,i)
 kd.balance();mapped=[];ds=[]
 for v in m.vertices:
  p=world(original.matrix_world@v.co,org);q,ii,d=kd.find(p);mapped.append(q);ds.append(d)
 m.calc_loop_triangles();before=collections.Counter(key(r['faces'][i:i+3]) for i in range(0,len(r['faces']),3));after=collections.Counter(key([mapped[i] for i in t.vertices]) for t in m.loop_triangles)
 assert before==after,(name,'source topology differs from saved51b')
 for v,p in zip(m.vertices,mapped):v.co=bco(p,org)
 original.name='rock_body';m.name=name+'_saved51b_authoritative_body';original['source_authority']=src;original['saved51b_sha256']=SHA;original['coordinate_mapping']='Godot(x,y,z) = origin + Blender(x,z,-y)'
 report['source_equivalence'].append({'name':name,'source_path':src,'source_sha256':hashlib.sha256(open(src,'rb').read()).hexdigest(),'exact_triangle_topology_after_nearest_mapping':True,'max_mapping_error_m':max(ds),'triangles':len(m.loop_triangles),'mapped_saved51b_before_edit':True})
 rockmat=make_material('Rim53 stone vertex palette',(.31,.345,.375));snowmat=make_material('Rim53 snow vertex palette',(.78,.84,.88))
 altered=[];locked=[]
 if name!='massif_frost_crown':
  parts=[original]+grid_ridge(name,org,rockmat,snowmat)
 else:
  for tri in m.loop_triangles:
   if protected_face([mapped[i] for i in tri.vertices]):locked.extend(tri.vertices)
  locked=set(locked)
  for v,p in zip(m.vertices,mapped):
   if p.y>355 and v.index not in locked:
    y=355+34.5*(1-math.exp(-(p.y-355)/24))
    # A wide broken saddle replaces the sharp upper needle without disturbing lower support.
    y-=3.8*math.exp(-((p.x-1218)/25)**2)*math.exp(-((p.z+2918)/42)**2)
    v.co.z=y;altered.append({'index':v.index,'old':list(p),'new':world(v.co,org)})
  m.update();m.calc_loop_triangles();verts=[world(v.co,org) for v in m.vertices];faces=[tuple(t.vertices) for t in m.loop_triangles]
  cap=[];gull=[];should=[];apron=[]
  for i,f in enumerate(faces):
   pp=[verts[a] for a in f];y=sum(p[1] for p in pp)/3
   if protected_face(pp):continue
   if min(p[1] for p in pp)>337 and y>357:cap.append(i)
   elif min(p[1] for p in pp)>325 and y>344:gull.append(i)
   if min(p[1] for p in pp)>320 and y<361:should.append(i)
  parts=[original]
  for o in [lens('ridge_shoulders',verts,faces,should,org,'rock',rockmat,.7),lens('snow_cap',verts,faces,cap,org,'snow',snowmat,1.3),lens('snow_gully',verts,faces,gull,org,'snow',snowmat,.8)]:
   if o:parts.append(o)
  # Existing lower shore/root body remains wholly authoritative; no new apron belongs on this inland crown.
 report['source_changes'].append({'name':name,'original_body_vertices_changed':altered,'protected_source_vertices_locked':sorted(locked),'original_body_other_vertices_exact':True})
 components=[];merged=[]
 for o in parts:
  mesh=o.data;mesh.calc_loop_triangles();attr=mesh.color_attributes.active_color;faces=[];colors=[]
  for t in mesh.loop_triangles:
   for vi,li in zip(reversed(t.vertices),reversed(t.loops)):
    faces.append(world(mesh.vertices[vi].co,org));colors.append(list(attr.data[li if attr.domain=='CORNER' else vi].color))
  bm=bmesh.new();bm.from_mesh(mesh)
  audit={'mountain':name,'component':o.name,'vertices':len(mesh.vertices),'triangles':len(faces)//3,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-8 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True),'bounds':[[min(p[i] for p in faces) for i in range(3)],[max(p[i] for p in faces) for i in range(3)]]}
  bm.free();report['component_audits'].append(audit)
  assert audit['boundary_edges']==0 and audit['nonmanifold_edges']==0 and audit['degenerate_faces']==0,(name,o.name,audit)
  o['world_origin_godot']=org;o['candidate']='lake-rim53';o['component_role']=o.name
  components.append({'name':o.name,'vertices':faces,'colors':colors,'material_binding':'inherit_verified_51b_mountain_surface_material'});merged+=faces
 payload['mountains'].append({'name':name,'asset_node_path':'World/Mountains/'+name,'origin':org,'components':components,'collision_vertices':merged})
 bpy.context.scene['source_baseline']=SHA;bpy.context.scene['scope']='Four local editable mountain candidate. Preserve baseline until engine+visual review.'
 bpy.ops.wm.save_as_mainfile(filepath=OUT+'/'+name+'_rim53.blend')
 bpy.ops.export_scene.gltf(filepath=OUT+'/'+name+'_rim53.glb',export_format='GLB',export_draco_mesh_compression_enable=False,export_yup=True,export_cameras=False,export_lights=False)
 print('RIM53_SAVED',name,len(components),len(merged)//3,flush=True)
json.dump(payload,open(OUT+'/rim53-payload.json','w'))
json.dump(report,open(OUT+'/sculpt-report.json','w'),indent=2)
print('RIM53_ALL_SOURCES_SAVED',flush=True)
