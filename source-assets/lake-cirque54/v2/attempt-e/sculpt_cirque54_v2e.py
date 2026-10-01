"""Independent remodeled upper cirque with a preserved clipped wet surface."""
import bpy,bmesh,json,math,collections,hashlib,sys,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
R=Path('/workspace/scratch/a29d03198654/Aether');OUT=R/'source-assets/lake-cirque54/v2/attempt-e';I=R/'source-assets/lake-cirque54/intake'
sys.path.insert(0,str(I));import land_support as land
AUTH=json.load(open(R/'source-assets/lake-cirque54/v2/native-authority/cirque-native-authority.json'));ORG=AUTH['origin'];SHA=land.INVENTORY['source_sha256']
SRC=R/'source-assets/lake48/massif_cirque_wall_lake48.blend'
intake=json.load(open(OUT.parent/'native-authority/upper-remesh-intake-c.json'));oldverts=intake['vertices_with_cached_y0_intersections'];oldfaces=intake['original_triangles']
def bco(p,org):return (p[0]-org[0],-p[2]+org[2],p[1]-org[1])
def world(v,org):return [v[0]+org[0],v[2]+org[1],-v[1]+org[2]]
def make_material(name,basecol):
 mat=bpy.data.materials.new(name);mat.diffuse_color=(*basecol,1);mat.use_nodes=True
 nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');vc=nt.nodes.new('ShaderNodeVertexColor');vc.layer_name='Palette';nt.links.new(vc.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.87
 return mat
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

def tree(ff):return BVHTree.FromPolygons([Vector(p) for p in ff],[(i,i+1,i+2) for i in range(0,len(ff),3)],all_triangles=True)
oldtree=tree(AUTH['faces'])
def old_height(x,z):
 p,_,_,_=oldtree.ray_cast(Vector((x,1500,z)),Vector((0,-1,0)),3000)
 return p.y if p else None
def dist_segment(x,z,a,b):
 dx=b[0]-a[0];dz=b[2]-a[2];l=dx*dx+dz*dz
 t=max(0,min(1,((x-a[0])*dx+(z-a[2])*dz)/l)) if l else 0
 return math.hypot(x-a[0]-t*dx,z-a[2]-t*dz),t
shore=[oldverts[i] for i in intake['waterline_loops'][0]]
water_shore=[oldverts[i] for i in intake['waterline_loops_original'][0]]
def inside_shore(x,z):
 inside=False
 for a,b in zip(shore,shore[1:]+shore[:1]):
  if ((a[2]>z)!=(b[2]>z)) and x<(b[0]-a[0])*(z-a[2])/(b[2]-a[2])+a[0]:inside=not inside
 return inside
def plane_height(x,z,tri):
 a,b,c=tri;den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
 if abs(den)<1e-12:return None
 u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den;v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den;w=1-u-v
 return u*a[1]+v*b[1]+w*c[1] if min(u,v,w)>=-1e-7 else None
locked_triangles=[[oldverts[i] for i in oldfaces[r['original_triangle']]] for r in intake['protected_faces']]
locked_edges=[(a,b) for tri in locked_triangles for a,b in zip(tri,tri[1:]+tri[:1])]
def protected_height(x,z):
 yy=[y for tri in locked_triangles if (y:=plane_height(x,z,tri)) is not None]
 return max(yy) if yy else None

# Along-ridge changes define three shoulder levels; lateral breakpoints form broad
# slopes and benches. Actual waterline distance caps excessive shore-side rise.
KNOTS=[(-2080,790,94,100,115),(-2002,802,151,127,137),(-1917,814,181,142,146),(-1842,820,185,147,150),(-1760,822,145,152,140),(-1678,824,111,140,126),(-1590,816,76,108,102),(-1510,785,25,65,65)]
CHANNELS={'a':[(798,-1975,32),(824,-1895,42),(850,-1808,45),(874,-1715,42),(887,-1635,30)],'b':[(775,-1844,29),(794,-1760,36),(823,-1680,34),(844,-1609,29)]}
def ridge_parameters(z):
 for a,b in zip(KNOTS,KNOTS[1:]):
  if a[0]<=z<=b[0]:
   t=(z-a[0])/(b[0]-a[0]);return [a[i]*(1-t)+b[i]*t for i in range(1,5)]
 return KNOTS[0][1:] if z<KNOTS[0][0] else KNOTS[-1][1:]
def channel_distance(x,z,line):
 best=None
 for a,b in zip(line,line[1:]):
  d,t=dist_segment(x,z,[a[0],0,a[1]],[b[0],0,b[1]]);r=(d,a[2]*(1-t)+b[2]*t)
  if best is None or r[0]<best[0]:best=r
 return best
def new_height(x,z):
 locked=protected_height(x,z)
 if locked is not None:return max(0,locked)
 old=old_height(x,z)
 if old is None:return 0.
 shore_distance=min(dist_segment(x,z,a,b)[0] for a,b in zip(water_shore,water_shore[1:]+water_shore[:1]))
 if shore_distance<1e-4:return 0.
 c,crest,left,right=ridge_parameters(z);u=abs((x-c)/(left if x<c else right))
 profile=[(0,1),(.26,.97),(.52,.79),(.76,.47),(1.0,.08),(1.30,0)]
 lateral=0.
 for a,b in zip(profile,profile[1:]):
  if a[0]<=u<=b[0]:
   t=(u-a[0])/(b[0]-a[0]);lateral=a[1]*(1-t)+b[1]*t;break
 raw=crest*lateral
 for name,line in CHANNELS.items():
  d,width=channel_distance(x,z,line)
  raw-=(16 if name=='a' else 12)*max(0,1-(d/width)**2)**2
 # The cap follows genuine distance to the original waterline; no new shore wall.
 raw=min(max(0,raw),1.25*shore_distance)
 protect_distance=min(dist_segment(x,z,a,b)[0] for a,b in locked_edges)
 t=min(1,protect_distance/62.);weight=t*t*(3-2*t)
 boundary_distance=min(dist_segment(x,z,a,b)[0] for a,b in zip(shore,shore[1:]+shore[:1]));bt=min(1,boundary_distance/30.);bw=bt*bt*(3-2*bt)
 return max(min(max(0,old)*.12,1.0),old*(1-weight*bw)+raw*weight*bw)

bpy.ops.wm.open_mainfile(filepath=str(SRC))
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
points=[];point_lookup={};constraints=[]
def add_world(x,z):
 # Local XZ avoids unnecessarily rounding worldZ~-2000 in CDT's float vectors.
 q=Vector((x-ORG[0],z-ORG[2]));key=(float(q.x),float(q.y))
 if key not in point_lookup:point_lookup[key]=len(points);points.append(q)
 return point_lookup[key]
outline=[add_world(p[0],p[2]) for p in shore]
if sum(points[a].x*points[b].y-points[b].x*points[a].y for a,b in zip(outline,outline[1:]+outline[:1]))<0:outline.reverse()
constraints.extend(zip(outline,outline[1:]+outline[:1]))
# Whole protected original planes are bounded by constraints. New triangulation
# may split them but cannot change their geometric surface or color region.
for r in intake['protected_faces']:
 ids=[add_world(oldverts[i][0],oldverts[i][2]) for i in r['whole_polygon_locked']]
 constraints.extend(zip(ids,ids[1:]+ids[:1]))
# Reuse the useful irregular locations of the old dry surface; their heights are
# remodelled. Add authored broad ridge, bench and channel-bank controls.
for p in oldverts[:intake['old_original_unique_vertices']]:
 if p[1]>0:add_world(p[0],p[2])
authoring=[]
for j,row in enumerate(KNOTS):
 z,c,crest,left,right=row
 for k,u in enumerate([-.76,-.51,-.25,0,.25,.52,.77]):
  x=c+u*(left if u<0 else right);zz=z+[-8,9,-6,0,11,-5,7][k]
  if inside_shore(x,zz) and protected_height(x,zz) is None:add_world(x,zz);authoring.append({'role':'broad_shoulder_break','xz':[x,zz],'y':new_height(x,zz)})
for name,line in CHANNELS.items():
 paths=[[],[],[],[],[]]
 for i,(x,z,width) in enumerate(line):
  a=line[max(0,i-1)];b=line[min(len(line)-1,i+1)];dx=b[0]-a[0];dz=b[1]-a[1];length=math.hypot(dx,dz);nx=-dz/length;nz=dx/length
  for k,u in enumerate([-1,-.5,0,.5,1]):
   xx=x+nx*width*u;zz=z+nz*width*u
   if inside_shore(xx,zz) and protected_height(xx,zz) is None:paths[k].append(add_world(xx,zz));authoring.append({'role':'broad_channel_'+name,'width_fraction':u,'xz':[xx,zz],'y':new_height(xx,zz)})
 for ids in paths:
  for a,b in zip(ids,ids[1:]):
   if all(inside_shore(points[a].lerp(points[b],t/100).x+ORG[0],points[a].lerp(points[b],t/100).y+ORG[2]) and protected_height(points[a].lerp(points[b],t/100).x+ORG[0],points[a].lerp(points[b],t/100).y+ORG[2]) is None for t in range(1,100)):constraints.append((a,b))
xy,_,tris,orig,_,_=delaunay_2d_cdt(points,constraints,[outline],1,1e-6,False)
# CDT's inside mode can retain constraint-bounded pockets outside a concave input
# face. Use the original polygon itself; every shoreline edge is a constraint.
tris=[tuple(f) for f in tris if inside_shore(sum(xy[i].x for i in f)/len(f)+ORG[0],sum(xy[i].y for i in f)/len(f)+ORG[2]) and protected_height(sum(xy[i].x for i in f)/len(f)+ORG[0],sum(xy[i].y for i in f)/len(f)+ORG[2]) is None]
# Restore every original cached shoreline point, including collinear points CDT
# may omit from its face loops. Split using an interior fan, never zero-area ears.
shore_ids=[]
for p in shore:
 q=Vector((p[0]-ORG[0],p[2]-ORG[2]));matches=[i for i,v in enumerate(xy) if tuple(v)==tuple(q)]
 if matches:shore_ids.append(matches[0])
 else:shore_ids.append(len(xy));xy.append(q)
rebuilt=[]
for face in tris:
 poly=[];needs_split=False
 for a,b in zip(face,face[1:]+face[:1]):
  poly.append(a);ab=xy[b]-xy[a];middle=[]
  for j in shore_ids:
   if j in (a,b):continue
   t=(xy[j]-xy[a]).dot(ab)/ab.length_squared
   if 1e-7<t<1-1e-7 and (xy[j]-xy[a]-ab*t).length<2e-5:middle.append((t,j))
  if middle:needs_split=True;poly.extend(j for _,j in sorted(middle))
 if needs_split or all(i in shore_ids for i in face):
  center=sum((xy[i] for i in face),Vector((0,0)))/len(face);ci=len(xy);xy.append(center)
  rebuilt.extend((ci,a,b) for a,b in zip(poly,poly[1:]+poly[:1]))
 else:rebuilt.append(face)
tris=rebuilt
protected_native_vertices={}
for r in intake['protected_faces']:
 ids=[]
 for oi in oldfaces[r['original_triangle']]:
  p=oldverts[oi];q=Vector((p[0]-ORG[0],p[2]-ORG[2]));matches=[i for i,v in enumerate(xy) if tuple(v)==tuple(q)]
  assert len(matches)==1,('Missing original protected native vertex',oi)
  vi=matches[0];ids.append(vi);protected_native_vertices[vi]=p[:]
 if sum(xy[a].x*xy[b].y-xy[b].x*xy[a].y for a,b in zip(ids,ids[1:]+ids[:1]))<0:ids.reverse()
 tris.append(tuple(ids))
top_verts=[]
for q in xy:
 x,z=float(q.x)+ORG[0],float(q.y)+ORG[2];top_verts.append([x,new_height(x,z),z])
edge_count=collections.Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in tris for i in range(3))
boundary={i for e,c in edge_count.items() if c==1 for i in e}
for i in boundary:
 matches=[p for p in shore if tuple(Vector((p[0]-ORG[0],p[2]-ORG[2])))==tuple(xy[i])]
 assert len(matches)==1,('Unexpected extra native interface vertex',i,list(xy[i]))
 top_verts[i]=matches[0][:]
for i,p in protected_native_vertices.items():top_verts[i]=p[:]
# Weld top and inherited wet parts at exactly the same native local coordinates.
verts=[];lookup={}
def add_vertex(p):
 q=Vector(bco(p,ORG));key=tuple(float(x) for x in q)
 if key not in lookup:lookup[key]=len(verts);verts.append(world(q,ORG))
 return lookup[key]
top_map={i:add_vertex(top_verts[i]) for i in sorted({j for f in tris for j in f})};faces=[];wet_ledger=[];top_faces=[]
for f in tris:
 face=tuple(top_map[i] for i in reversed(f));faces.append(face);top_faces.append(face)
for r in intake['wet_polygons']:
 ids=[add_vertex(oldverts[i]) for i in r['polygon']]
 children=[]
 for k in range(1,len(ids)-1):
  face=(ids[0],ids[k+1],ids[k]);faces.append(face);children.append(face)
 wet_ledger.append({'old_triangle':r['original_triangle'],'original_clipped_polygon_world':[oldverts[i] for i in r['polygon']],'new_child_vertex_indices':children})
rock=make_material('Cirque54v2 native stone palette',(.17,.225,.285));snow=make_material('Cirque54v2 broad snow palette',(.48,.59,.70))
body=create_object('remodeled_cirque_body',verts,faces,ORG,'rock',rock)
selections={n:[] for n in ['snow_gully_a','snow_gully_b','upper_snow_basin','north_snow_patch']}
for fi,f in enumerate(top_faces):
 pp=[Vector(verts[i]) for i in f];p=sum(pp,Vector())/3;x,y,z=p;slope=abs((pp[1]-pp[0]).cross(pp[2]-pp[0]).normalized().y)
 if protected_height(x,z) is not None:continue
 a=channel_distance(x,z,CHANNELS['a']);b=channel_distance(x,z,CHANNELS['b'])
 if a[0]<a[1]*.87 and 34<y<178 and slope>.36:selections['snow_gully_a'].append(fi)
 elif b[0]<b[1]*.91 and 37<y<164 and slope>.4:selections['snow_gully_b'].append(fi)
 elif ((x-830)/61)**2+((z+1856)/103)**2<1 and y>91 and slope>.57:selections['upper_snow_basin'].append(fi)
 elif ((x-790)/59)**2+((z+2033)/64)**2<1 and y>47 and slope>.5:selections['north_snow_patch'].append(fi)
parts=[body]
for name,selected in selections.items():
 obj=lens(name,verts,top_faces,selected,ORG,'snow',snow,1.2)
 if obj:parts.append(obj)
components=[];merged=[];audits=[]
for o in parts:
 mesh=o.data;mesh.calc_loop_triangles();attr=mesh.color_attributes.active_color;ff=[];cc=[]
 for t in mesh.loop_triangles:
  for vi,li in zip(reversed(t.vertices),reversed(t.loops)):ff.append(world(mesh.vertices[vi].co,ORG));cc.append(list(attr.data[li].color))
 bm=bmesh.new();bm.from_mesh(mesh);r={'component':o.name,'vertices':len(mesh.vertices),'triangles':len(ff)//3,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-8 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True),'bounds':[[min(p[k] for p in ff) for k in range(3)],[max(p[k] for p in ff) for k in range(3)]]};bm.free();audits.append(r)
 if any(r[k] for k in ['boundary_edges','nonmanifold_edges','degenerate_faces']) or r['signed_volume']<=0:print('CIRQUE54V2_GEOMETRY_GATE_FAIL',r,flush=True)
 o['world_origin_godot']=ORG;o['component_role']=o.name;o['baseline_sha256']=SHA
 components.append({'name':o.name,'vertices':ff,'colors':cc,'material_binding':'inherit_verified_saved53_cirque_surface_material'});merged+=ff
payload={'schema_version':2,'baseline_sha256':SHA,'source_metadata':{'scope':'Independent remodelled upper cirque source only; old source48/53/54v1 frozen','root_strategy':'All432original touch-water/wet triangles kept whole at exactnative coordinates. Only260fully dry uppertriangles remodelled through42original positive-height boundaryedges; all protected original dry planes retained. Strict wet-native proof required before integration.'},'mountains':[{'name':'massif_cirque_wall','asset_node_path':'World/Mountains/massif_cirque_wall','origin':ORG,'components':components,'collision_vertices':merged}],'scatter':[]}
bpy.context.scene['scope']='Independent cirque54v2 upper remodelling; original resources frozen; no native scene saved'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'massif_cirque_wall_cirque54v2.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'massif_cirque_wall_cirque54v2.glb'),export_format='GLB',export_draco_mesh_compression_enable=False,export_yup=True,export_cameras=False,export_lights=False)
json.dump(payload,open(OUT/'cirque54v2-payload.json','w'));json.dump({'audits':audits,'authoring':authoring,'ridge_parameters':KNOTS,'channels':CHANNELS,'source48_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest()},open(OUT/'sculpt-report.json','w'),indent=2)
json.dump({'vertices_world':verts,'top_faces':top_faces,'wet_face_ledger':wet_ledger,'waterline_original_world':shore,'protected_original_faces':intake['protected_faces'],'cdt_input_points_local':[list(p) for p in points]},open(OUT/'surface-and-wet-ledger.json','w'),indent=2)
assert all(not any(r[k] for k in ['boundary_edges','nonmanifold_edges','degenerate_faces']) and r['signed_volume']>0 for r in audits),'Source is saved as failed geometry for inspection; no preview pass'
print('CIRQUE54V2_SAVED',len(components),len(merged)//3,'maxY',max(p[1] for p in merged),flush=True)
