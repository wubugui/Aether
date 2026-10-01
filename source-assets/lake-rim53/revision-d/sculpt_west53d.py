"""Local additive, closed native ridge layers. No world regeneration or scene writes."""
import bpy,bmesh,json,math,random,collections,os,hashlib
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53'
ROOT='/workspace/scratch/a29d03198654/Aether'
OUT=D+'/revision-d'
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
'massif_west_spur':[(-2240,205,28,50,101),(-2180,205,154,207,175),(-2100,210,189,255,268),(-2045,222,201,276,283),(-1980,232,206,268,245),(-1920,237,215,263,285),(-1880,245,219,256,323.5),(-1810,295,233,205,256),(-1740,343,218,158,211),(-1660,375,178,126,161),(-1570,405,150,96,104),(-1490,433,48,52,70)],
'massif_cirque_wall':[(-2133,745,35,36,114),(-2070,750,67,118,174),(-1990,753,49,128,226),(-1910,765,59,139,238),(-1840,780,70,125,201),(-1770,796,74,119,185),(-1690,783,102,100,176),(-1610,765,91,98,129),(-1545,747,45,60,74),(-1510,743,20,29,44)],
'massif_east_foothill':[(-2160,1770,60,70,95),(-2100,1744,184,174,232),(-2020,1760,260,255,295),(-1950,1792,310,263,328),(-1870,1818,321,282,286),(-1790,1790,312,292,244),(-1720,1815,299,264,282),(-1635,1850,240,220,226),(-1550,1854,183,193,165),(-1490,1890,90,98,100),(-1455,1905,26,32,40)]}
# Planned geological snow channels run across the slopes, not by camera or reference number.
def gully(z,u,name):
 # Three unequal downslope axes. Distance is measured across each channel in metres,
 # never as a fixed u-band parallel to the longitudinal ridge.
 au=abs(u)
 if u>=0:
  axes=[(-2055+125*au,13+24*au),(-1880+145*au,17+30*au)]
 else:
  axes=[(-2055-110*au,17+22*au),(-1880+125*au,12+30*au)]
 return max(math.exp(-((z-c)/w)**2) for c,w in axes)*min(1,au/.12)

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
 from mathutils.geometry import delaunay_2d_cdt
 kk=knots[name];rng=random.Random(53003);points=[];constraints=[]
 def parms(z):
  for a,b in zip(kk,kk[1:]):
   if a[0]<=z<=b[0]:
    t=(z-a[0])/(b[0]-a[0]);return [x*(1-t)+y*t for x,y in zip(a,b)]
  return kk[0] if z<kk[0][0] else kk[-1]
 def point(z,u):
  _,c,wl,wr,crest=parms(z);return (c+u*(wl if u<0 else wr),z)
 def add(p):points.append(Vector(p));return len(points)-1
 # Actual footprint edges are constrained. Sparse irregular internal nodes describe
 # geological shoulders and explicit crest/channel banks; no repeated loft faces.
 outline=[]
 for side,rows in [(-1,kk),(1,list(reversed(kk)))]:
  for row in rows:outline.append(add(point(row[0],side)))
 if sum(points[outline[i]].x*points[outline[(i+1)%len(outline)]].y-points[outline[(i+1)%len(outline)]].x*points[outline[i]].y for i in range(len(outline)))<0:outline.reverse()
 for a,b in zip(outline,outline[1:]+outline[:1]):constraints.append((a,b))
 crestids=[add(point(row[0],0)) for row in kk[1:-1]]
 constraints.extend(zip(crestids,crestids[1:]))
 for z in range(int(kk[0][0])+45,int(kk[-1][0])-30,58):
  for u in [-.84,-.63,-.40,-.18,.16,.37,.62,.85]:
   add(point(z+rng.uniform(-18,18),u+rng.uniform(-.045,.045)))
 # Constraint axes and banks carry both actual incised rock valleys and their snow.
 for side,start,drift,width in [(1,-2055,125,13),(1,-1880,145,17),(-1,-2055,-110,17),(-1,-1880,125,12)]:
  for bank in [-1,0,1]:
   curve=[]
   for au in [.12,.24,.40,.59,.78,.91]:
    z=start+drift*au+bank*(width+25*au);curve.append(add(point(z,side*au)))
   constraints.extend(zip(curve,curve[1:]))
 xy,ed,tri,ov,oe,of=delaunay_2d_cdt(points,list(constraints),[outline],1,1e-5,False)
 faces=[tuple(f) for f in tri];verts=[];uv=[];supports=[]
 ec=collections.Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in faces for i in range(3))
 boundary=[e for e,count in ec.items() if count==1];boundary_vertices=set(i for e in boundary for i in e)
 for i,q in enumerate(xy):
  x,z=q;_,c,wl,wr,crest=parms(z);u=(x-c)/(wl if x<c else wr);u=max(-1,min(1,u))
  h=height(oldtree,x,z)
  if h is None or h<4:raise RuntimeError(('actual dry support required',x,z,h))
  w=max(0,1-abs(u))**1.22
  length=max(0,min(1,(z-kk[0][0])/70,(kk[-1][0]-z)/80))
  y=h-18+max(0,crest-h+18)*w*length
  y-=gully(z,u,name)*(16+18*abs(u))*math.sin(math.pi*abs(u))
  if i in boundary_vertices:y=h-18
  if protected_face([[x,y,z]]):raise RuntimeError(('protected new footprint',x,z))
  verts.append([x,y,z]);supports.append(h);uv.append((u,z))
 # Each edge is checked between endpoints against actual saved support. Increase
 # burial only as much as needed, retaining a4m measured margin across the whole edge.
 for a,b in boundary:
  p,q=map(Vector,(verts[a],verts[b]));steps=max(2,math.ceil((q-p).length/.5));excess=-1e9
  for j in range(steps+1):
   v=p.lerp(q,j/steps);hh=height(oldtree,v.x,v.z);excess=max(excess,v.y-hh)
  if excess>-4:
   amount=excess+4
   verts[a][1]-=amount;verts[b][1]-=amount
 bottom=[[p[0],min(supports[i]-40,p[1]-12),p[2]] for i,p in enumerate(verts)];n=len(verts)
 # Consistent top winding in Blender basis; recalc supplies the outward shell orientation.
 for i,f in enumerate(faces):
  pp=[Vector(verts[a]) for a in f]
  if (pp[1]-pp[0]).cross(pp[2]-pp[0]).y>0:faces[i]=tuple(reversed(f))
 closed=faces+[tuple(i+n for i in reversed(f)) for f in faces]
 directed=collections.Counter((f[i],f[(i+1)%3]) for f in faces for i in range(3))
 for a,b in directed:
  if (b,a) not in directed:closed.extend([(a,b,b+n),(a,b+n,a+n)])
 ridge=create_object('ridge_shoulders',verts+bottom,closed,org,'rock',mat)
 cap=[];gull=[];apron=[]
 for i,f in enumerate(faces):
  pp=[verts[a] for a in f];u=sum(uv[a][0] for a in f)/3;z=sum(p[2] for p in pp)/3;y=sum(p[1] for p in pp)/3
  p0,p1,p2=map(Vector,pp);slope=abs((p1-p0).cross(p2-p0).normalized().y)
  channel=gully(z,u,name)
  snowline=179+22*math.sin(z*.027)+13*math.sin(z*.061)
  capmask=(abs(u)<.25 and y>snowline+13 and math.sin(z*.026)>-.4) or (channel>.20 and y>snowline) or (y>265 and u>-.38)
  if capmask and slope>.36:cap.append(i)
  elif channel>.43 and 77<y<252 and slope>.28 and abs(u)>.15:gull.append(i)
  if 20<y<110 and u>.55:apron.append(i)
 out=[ridge,lens('snow_cap',verts,faces,cap,org,'snow',snowmat,1.6),lens('snow_gully',verts,faces,gull,org,'snow',snowmat,1.35),lens('shore_rock_apron',verts,faces,apron,org,'apron',mat,.8)]
 return [o for o in out if o]

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
