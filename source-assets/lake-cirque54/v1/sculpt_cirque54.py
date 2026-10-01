"""Cirque54 single moderate shoulder, authored geology and two real downslope grooves."""
import bpy,bmesh,json,math,random,collections,os,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
ROOT=Path('/workspace/scratch/a29d03198654/Aether')
OUT=ROOT/'source-assets/lake-cirque54/v1'
sys.path.insert(0,str(OUT.parent/'intake'))
import land_support as land
SHA=land.INVENTORY['source_sha256']
SRC=ROOT/'source-assets/lake48/massif_cirque_wall_lake48.blend'
NAME='massif_cirque_wall'
AUTH=land.INVENTORY['cirque_mesh'];ORG=AUTH['origin']
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

def tri_key(t):return tuple(sorted(tuple(round(float(x),4) for x in p) for p in t))
def nearest_channel(x,z,channel):
 best=None
 for a,b in zip(channel,channel[1:]):
  ax,ay,az,aw=a;bx,by,bz,bw=b;dx=bx-ax;dz=bz-az
  t=max(0,min(1,((x-ax)*dx+(z-az)*dz)/(dx*dx+dz*dz)))
  xx=ax+t*dx;zz=az+t*dz;dist=math.hypot(x-xx,z-zz)
  row=(dist,aw+t*(bw-aw),ay+t*(by-ay),t)
  if best is None or row[0]<best[0]:best=row
 return best

# X,Y,Z,half width. Each valley descends across the shoulder, never around it.
CHANNELS={
 'a':[(781,206,-1994,18),(800,183,-1944,22),(818,159,-1902,26),(843,123,-1844,29),(871,97,-1787,30),(906,62,-1720,25)],
 'b':[(752,175,-1915,12),(767,148,-1848,14),(790,125,-1780,16),(812,105,-1705,17),(842,84,-1635,14)],
 'back':[(776,197,-2040,12),(758,167,-2060,15),(741,130,-2084,17)]}
OUTLINE=[(725,-2110),(838,-2110),(911,-2070),(931,-1982),(934,-1885),(933,-1770),(919,-1700),(897,-1624),(871,-1559),(829,-1495),(772,-1505),(731,-1562),(717,-1682),(708,-1776),(704,-1850),(704,-1996),(709,-2061)]
RIDGES=[[(767,185,-2072),(785,214,-2037),(795,228,-1998),(795,231,-1956),(805,226,-1898),(815,196,-1845),(827,174,-1784),(850,116,-1694),(826,96,-1602),(806,63,-1540)],
 [(741,147,-2070),(728,149,-2009),(730,164,-1948),(733,169,-1882),(751,142,-1807),(762,131,-1741),(780,107,-1674),(762,81,-1599)],
 [(860,153,-2072),(884,157,-2012),(899,131,-1938),(906,108,-1855),(912,77,-1774),(891,80,-1670),(864,86,-1597)]]

def sculpt():
 points=[];heights=[];roles=[];edges=[]
 def add(x,y,z,role):
  h,owner=land.highest(x,z)
  if h is None or h<2:raise RuntimeError(('dry support required',x,z,h,owner,role))
  if 508<=x<=702 and -2000<=z<=-1796:raise RuntimeError(('village block',x,z))
  points.append(Vector((x,z)));heights.append(y);roles.append(role);return len(points)-1
 outline=[add(x,land.height(x,z)-14,z,'buried perimeter') for x,z in OUTLINE]
 if sum(points[a].x*points[b].y-points[b].x*points[a].y for a,b in zip(outline,outline[1:]+outline[:1]))<0:outline.reverse()
 edges.extend(zip(outline,outline[1:]+outline[:1]))
 for line in RIDGES:
  ids=[add(x,max(y,land.height(x,z)+3),z,'authored shoulder') for x,y,z in line]
  edges.extend(zip(ids,ids[1:]))
 for label,line in CHANNELS.items():
  center=[];left=[];right=[]
  for i,(x,y,z,width) in enumerate(line):
   a=line[max(0,i-1)];b=line[min(len(line)-1,i+1)];dx=b[0]-a[0];dz=b[2]-a[2];ll=math.hypot(dx,dz);nx=-dz/ll;nz=dx/ll
   y=max(y,land.height(x,z)+3)
   center.append(add(x,y,z,'channel '+label))
   for sign,dest in [(-1,left),(1,right)]:
    xx=x+nx*width*sign;zz=z+nz*width*sign;yy=y+(18 if label=='a' else 13)*(1 if i<len(line)-1 else .7)
    dest.append(add(xx,max(yy,land.height(xx,zz)+3),zz,'bank '+label))
  for ids in [center,left,right]:edges.extend(zip(ids,ids[1:]))
 # A few distinct rock platforms break the lake-facing planes without repeated rows.
 for x,y,z in [(855,112,-1831),(878,101,-1806),(870,105,-1727),(835,138,-1730),(805,150,-1821),(800,100,-1627),(847,77,-1566),(794,74,-1569),(748,111,-1710),(716,97,-1902),(908,76,-1810),(905,54,-1664),(815,168,-2055),(820,202,-1974)]:
  add(x,max(y,land.height(x,z)+3),z,'unequal rock platform')
 xy,_,tri,orig,_,_=delaunay_2d_cdt(points,edges,[outline],1,1e-5,False)
 faces=[tuple(f) for f in tri];verts=[]
 perimeter=collections.Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in faces for i in range(3))
 boundary=[e for e,n in perimeter.items() if n==1];bv={i for e in boundary for i in e}
 for i,p in enumerate(xy):
  x,z=p;hh=land.height(x,z)
  exact=[j for j,q in enumerate(points) if (p-q).length<.00005]
  if exact:y=min(heights[j] for j in exact)
  else:
   # CDT intersections are genuine crease intersections. Choose the incised lower
   # profile where two lines meet; no random or camera-dependent height field.
   matches=[]
   for a,b in edges:
    ab=points[b]-points[a];t=(p-points[a]).dot(ab)/ab.length_squared
    if -.00001<=t<=1.00001 and (p-points[a]-ab*t).length<.0002:matches.append(heights[a]*(1-t)+heights[b]*t)
   assert matches,('unbound CDT point',list(p))
   y=min(matches)
  if i not in bv:y=max(y,hh+2.5)
  else:y=min(y,hh-14)
  verts.append([x,y,z])
 # Protect complete edges, not just vertices: every half metre has >=4m burial.
 for a,b in boundary:
  p,q=map(Vector,(verts[a],verts[b]));steps=max(2,math.ceil((q-p).length/.5));delta=[]
  for j in range(steps+1):
   v=p.lerp(q,j/steps);h=land.height(v.x,v.z)
   if h is None:raise RuntimeError(('missing boundary support',list(v)))
   delta.append(v.y-h)
  amount=max(0,max(delta)+4)
  verts[a][1]-=amount;verts[b][1]-=amount
 supports=[land.height(p[0],p[2]) for p in verts];n=len(verts)
 bottom=[[p[0],min(supports[i]-32,p[1]-12),p[2]] for i,p in enumerate(verts)]
 for i,f in enumerate(faces):
  a,b,c=map(Vector,(verts[j] for j in f))
  if (b-a).cross(c-a).y>0:faces[i]=tuple(reversed(f))
 closed=faces+[tuple(i+n for i in reversed(f)) for f in faces]
 directed=collections.Counter((f[i],f[(i+1)%3]) for f in faces for i in range(3))
 for a,b in directed:
  if (b,a) not in directed:closed.extend([(a,b,b+n),(a,b+n,a+n)])
 rock=make_material('Cirque54 cool stone vertex palette',(.17,.225,.285));snow=make_material('Cirque54 thick snow vertex palette',(.48,.59,.70))
 body=create_object('upper_cirque_mass',verts+bottom,closed,ORG,'rock',rock)
 selection={k:[] for k in ['snow_gully_a','snow_gully_b','snow_field_north','snow_field_saddle','snow_back_basin','lower_rock_shoulders','shore_rock_apron']}
 for i,f in enumerate(faces):
  pp=[Vector(verts[j]) for j in f];p=sum(pp,Vector())/3;x,y,z=p;slope=abs((pp[1]-pp[0]).cross(pp[2]-pp[0]).normalized().y)
  a=nearest_channel(x,z,CHANNELS['a']);b=nearest_channel(x,z,CHANNELS['b']);back=nearest_channel(x,z,CHANNELS['back'])
  if a[0]<a[1]*.72 and 66<y<221 and slope>.27:selection['snow_gully_a'].append(i)
  elif b[0]<b[1]*.78 and 86<y<196 and slope>.3:selection['snow_gully_b'].append(i)
  elif ((x-790)/43)**2+((z+2018)/61)**2<1 and y>163 and slope>.42:selection['snow_field_north'].append(i)
  elif ((x-804)/28)**2+((z+1880)/55)**2<1 and y>157 and slope>.44:selection['snow_field_saddle'].append(i)
  elif back[0]<back[1]*.8 and y>141 and slope>.32:selection['snow_back_basin'].append(i)
  elif 73<y<150 and x>785 and slope>.4:selection['lower_rock_shoulders'].append(i)
  elif 20<y<82 and x>820:selection['shore_rock_apron'].append(i)
 parts=[body]
 for name,selected in selection.items():
  is_snow=name.startswith('snow');obj=lens(name,verts,faces,selected,ORG,'snow' if is_snow else 'apron',snow if is_snow else rock,1.4 if is_snow else .7)
  if obj:parts.append(obj)
 authoring={'outline':OUTLINE,'ridges':RIDGES,'channels':CHANNELS,'top_vertices':verts,'top_faces':faces,'boundary_edges':boundary,'authored_points':[{'xz':list(p),'y':y,'role':r} for p,y,r in zip(points,heights,roles)],'full_saved_support_colliders_queried':sorted(land.TREES),'selection_faces':selection,'selected_vertex_count':n}
 json.dump(authoring,open(OUT/'authoring-surface.json','w'),indent=2)
 return parts

bpy.ops.wm.open_mainfile(filepath=str(SRC));original=next(o for o in bpy.data.objects if o.type=='MESH');m=original.data
for o in list(bpy.data.objects):
 if o!=original:bpy.data.objects.remove(o,do_unlink=True)
kd=KDTree(len(AUTH['faces']))
for i,p in enumerate(AUTH['faces']):kd.insert(p,i)
kd.balance();mapped=[];dist=[]
for v in m.vertices:
 p=world(original.matrix_world@v.co,ORG);q,_,d=kd.find(p);mapped.append(q);dist.append(d)
m.calc_loop_triangles()
assert collections.Counter(tri_key(AUTH['faces'][i:i+3]) for i in range(0,len(AUTH['faces']),3))==collections.Counter(tri_key([mapped[i] for i in t.vertices]) for t in m.loop_triangles),'source topology mismatch'
for v,p in zip(m.vertices,mapped):v.co=bco(p,ORG)
original.name='rock_body';m.name='cirque48_exact_saved53_root';original['source_authority']=str(SRC);original['saved53west_sha256']=SHA
parts=[original]+sculpt();components=[];merged=[];audits=[]
for o in parts:
 mesh=o.data;mesh.calc_loop_triangles();attr=mesh.color_attributes.active_color;ff=[];cc=[]
 for t in mesh.loop_triangles:
  for vi,li in zip(reversed(t.vertices),reversed(t.loops)):
   ff.append(world(mesh.vertices[vi].co,ORG));cc.append(list(attr.data[li if attr.domain=='CORNER' else vi].color))
 bm=bmesh.new();bm.from_mesh(mesh)
 audit={'component':o.name,'vertices':len(mesh.vertices),'triangles':len(ff)//3,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-8 for f in bm.faces),'signed_volume':bm.calc_volume(signed=True),'bounds':[[min(p[i] for p in ff) for i in range(3)],[max(p[i] for p in ff) for i in range(3)]]};bm.free()
 assert not any(audit[k] for k in ['boundary_edges','nonmanifold_edges','degenerate_faces']) and audit['signed_volume']>0,(o.name,audit)
 audits.append(audit);o['world_origin_godot']=ORG;o['candidate']='cirque54_v1';o['component_role']=o.name
 components.append({'name':o.name,'vertices':ff,'colors':cc,'material_binding':'inherit_verified_saved53west_cirque_surface_material'});merged+=ff
payload={'schema_version':1,'baseline_sha256':SHA,'source_metadata':{'scope':'Independent editable cirque source only; not integrated or visually accepted','source':'Source48 exact692triangle root mapped to actual saved53west','water_domain':'Full saved-scene mask4 intake; Ocean excluded; exact dry union proof is separate'},'mountains':[{'name':NAME,'asset_node_path':'World/Mountains/'+NAME,'origin':ORG,'components':components,'collision_vertices':merged}],'scatter':[]}
report={'baseline_sha256':SHA,'source_path':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'source_equivalence':{'triangles':692,'exact_triangle_topology_after_nearest_mapping':True,'max_mapping_error_m':max(dist),'original_root_vertices_changed_after_mapping':0},'component_audits':audits,'note':'New components intentionally intersect the retained original root below their visible surfaces. No source48 or saved native candidate modified. New dry-footprint, root-edge and reopen proofs are separate.'}
bpy.context.scene['scope']='Cirque54 independent moderate shoulder source; 53west stays frozen';bpy.context.scene['baseline_sha256']=SHA
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'massif_cirque_wall_cirque54.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'massif_cirque_wall_cirque54.glb'),export_format='GLB',export_draco_mesh_compression_enable=False,export_yup=True,export_cameras=False,export_lights=False)
json.dump(payload,open(OUT/'cirque54-payload.json','w'));json.dump(report,open(OUT/'sculpt-report.json','w'),indent=2)
print('CIRQUE54_SAVED',len(components),len(merged)//3,flush=True)
