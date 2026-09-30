import bpy,bmesh,json,math,random,collections,os
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake48';base=json.load(open(D+'/base47.json'))
# Inferred geography, not reference-proven metric coordinates. Outer neighbours stay untouched.
knots=[(-2290,1115,1130),(-2210,1030,1290),(-2090,940,1325),(-1970,940,1210),(-1830,970,1190),(-1700,940,1210),(-1560,870,1410),(-1420,860,1475),(-1240,875,1490),(-1100,910,1480),(-960,900,1490),(-830,990,1430),(-775,1100,1130)]
def shores(z):
 for i in range(len(knots)-1):
  a,b=knots[i:i+2]
  if a[0]<=z<=b[0]:
   t=(z-a[0])/(b[0]-a[0]);t=t*t*(3-2*t)
   return a[1]*(1-t)+b[1]*t,b[2]*(1-t)+b[2]*t
 return 0,0
def weight(x,z):
 if not -2260<z<-800 or not 800<x<1510:return 0.
 l,r=shores(z);d=min(x-l,r-x)
 t=max(0,min(1,(d+25)/70));return t*t*(3-2*t)
def bed(x,z):return -23-7*math.sin((z+1250)/270)**2-3*math.cos(x/130)
report={'source_equivalence':[],'mesh_changes':[],'scatter':[]};payload={'schema_version':1,'baseline_sha256':'ba236fdb78f662351ad8e89d82df4642b27721638412c833f86f6e8f682caa32','meshes':[],'scatter':[],'source_metadata':{'design':'Continuous asymmetrical basin, retained outer edges and summit cores; coordinates inferred; source47 quantized geometry authoritative','source':'source-assets/lake48'}}
bvhs={};oldbvhs={}
def makebvh(f):return BVHTree.FromPolygons([Vector(v) for v in f],[(i,i+1,i+2) for i in range(0,len(f),3)],all_triangles=True)
def height(trees,x,z):
 hits=[t.ray_cast(Vector((x,1200,z)),Vector((0,-1,0)),2000)[0] for t in trees]
 return max((p.y for p in hits if p is not None),default=None)
for name,r in base['meshes'].items():
 src=D+'/original_'+name.replace('massif_','')+'.blend' if name.startswith('massif') else '/workspace/scratch/a29d03198654/Aether/cloud-evidence/lake-source-intake/'+name+'.blend'
 bpy.ops.wm.open_mainfile(filepath=src);o=next(o for o in bpy.data.objects if o.type=='MESH');m=o.data;origin=Vector(r['origin']);m.calc_loop_triangles()
 kd=KDTree(len(r['faces']))
 for i,p in enumerate(r['faces']):kd.insert(p,i)
 kd.balance()
 mapped=[];dist=[]
 for v in m.vertices:
  p=o.matrix_world@v.co;p=Vector((p.x+origin.x,p.z+origin.y,-p.y+origin.z));near,idx,d=kd.find(p);mapped.append(near);dist.append(d)
 def key(t):return tuple(sorted(tuple(round(x,3) for x in p) for p in t))
 before=collections.Counter(key(r['faces'][i:i+3]) for i in range(0,len(r['faces']),3));after=collections.Counter(key([mapped[i] for i in t.vertices]) for t in m.loop_triangles)
 assert before==after,(name,'source topology mismatch')
 report['source_equivalence'].append({'name':name,'triangle_topology_nearest_mapping_exact':True,'max_quantization_distance_m':max(dist),'triangles':len(r['faces'])//3})
 # Snap editable native source to the actual saved scene before carving, preserving all boundary authority.
 for v,p in zip(m.vertices,mapped):v.co=Vector((p.x-origin.x,-p.z+origin.z,p.y-origin.y))
 bm=bmesh.new();bm.from_mesh(m)
 for iteration in range(4):
  edges=[]
  for e in bm.edges:
   a,b=e.verts;mid=(a.co+b.co)/2;x=mid.x+origin.x;z=-mid.y+origin.z
   if e.calc_length()>38 and weight(x,z)>0 and (not name.startswith('Ground') or all(1e-3<v.co.x<767.999 and .001<-v.co.y<767.999 for v in e.verts)):edges.append(e)
  if not edges:break
  bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True)
 bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
 changed=0;maxchange=0
 for v in m.vertices:
  x=v.co.x+origin.x;z=-v.co.y+origin.z;y=v.co.z;w=weight(x,z)
  if name.startswith('Ground'):yn=min(y,y*(1-w)+bed(x,z)*w)
  else:yn=y-w*(155 if 'cirque' in name else 112)
  if abs(yn-y)>1e-6:changed+=1;maxchange=max(maxchange,abs(yn-y));v.co.z=yn
 m.update();m.calc_loop_triangles()
 # Vertex-color shore zone with quiet stone and muted alpine grass; original above-water colors retained elsewhere.
 attr=m.color_attributes.active_color
 if not attr:attr=m.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
 for poly in m.polygons:
  for li in poly.loop_indices:
   v=m.vertices[m.loops[li].vertex_index];x=v.co.x+origin.x;z=-v.co.y+origin.z;w=weight(x,z)
   if w>0:
    y=v.co.z;noise=.025*math.sin(x*.07+z*.11)
    col=(.29+noise,.32+noise,.32+noise,1) if y<2.5 else (.37+noise,.40+noise,.29+noise,1) if y<8 else None
    if col:attr.data[li if attr.domain=='CORNER' else v.index].color=col
 faces=[];colors=[]
 for tri in m.loop_triangles:
  # Blender CCW becomes Godot clockwise when changing coordinate basis handedness? Basis determinant +1, Godot expects reversed.
  for vi,li in zip(reversed(tri.vertices),reversed(tri.loops)):
   v=m.vertices[vi].co;faces.append([v.x+origin.x,v.z+origin.y,-v.y+origin.z]);colors.append(list(attr.data[li if attr.domain=='CORNER' else vi].color))
 oldbvhs[name]=makebvh(r['faces']);bvhs[name]=makebvh(faces)
 meshpath=r['node'].replace('/Skyfarer/','');assetpath=meshpath.rsplit('/Model/',1)[0]
 payload['meshes'].append({'name':name,'node_path':meshpath,'collision_path':assetpath+'/Collision/Shape','vertices':faces,'colors':colors})
 report['mesh_changes'].append({'name':name,'source_vertices':len(mapped),'new_vertices':len(m.vertices),'triangles':len(faces)//3,'changed_vertices':changed,'max_displacement_m':maxchange})
 bpy.ops.wm.save_as_mainfile(filepath=D+'/'+name+'_lake48.blend')
 bpy.ops.export_scene.gltf(filepath=D+'/'+name+'_lake48.glb',export_format='GLB',export_draco_mesh_compression_enable=False,export_yup=True)
# Include unchanged nearby support geometry before considering a scatter change.
for k,v in json.load(open(D+'/support47.json'))['meshes'].items():
 if k not in oldbvhs:oldbvhs[k]=makebvh(v['faces']);bvhs[k]=oldbvhs[k]
# Move only affected tree/rock placements; dry untouched anchors retain exact bytes. Original index/rotation/scale retained.
occupied=[p['position'] for g in base['scatter'] for p in g['instances']];rng=random.Random(481128)
for group in base['scatter']:
 node=group['node'];tile='Ground_1_-3' if node.endswith('_1_-3') else 'Ground_1_-2';zmin=-2304 if tile.endswith('-3') else -1536
 for rec in group['instances']:
  x,y,z=rec['position'];old=height(list(oldbvhs.values()),x,z);new=height(list(bvhs.values()),x,z)
  if old is None or new is None:raise RuntimeError('support absent')
  if abs(new-old)<.015:continue
  target=(x,new,z);reason='resupported';clearance=y-old
  if abs(clearance)>1:raise RuntimeError(('unexpected original support offset',node,rec['index'],clearance))
  if new<3:
   candidates=[]
   for attempt in range(2200):
    nx=rng.uniform(796,1506);nz=rng.uniform(zmin+24,zmin+744);h=height(list(bvhs.values()),nx,nz)
    if h is None or h<5 or h>135:continue
    if min((nx-p[0])**2+(nz-p[2])**2 for p in occupied)<12**2:continue
    # Keep scatter spread over dry upland patches, not snapped to a shoreline contour.
    cost=(nx-x)**2+(nz-z)**2
    candidates.append((cost,nx,h,nz))
    if len(candidates)>=45:break
   if not candidates:raise RuntimeError(('no scatter landing',node,rec['index']))
   _,nx,h,nz=min(candidates);target=(nx,h,nz);reason='relocated_from_submerged_basin'
  before=rec['transform'];after=list(before);after[9:12]=[before[9]+target[0]-x,before[10]+target[1]+clearance-y,before[11]+target[2]-z];occupied.append(list(target))
  payload['scatter'].append({'node_path':node.replace('/Skyfarer/',''),'index':rec['index'],'before_transform':before,'after_transform':after})
  report['scatter'].append({'node':node,'index':rec['index'],'reason':reason,'old':rec['position'],'new':[target[0],target[1]+clearance,target[2]],'preserved_support_offset':clearance})
json.dump(payload,open(D+'/lake48-payload.json','w'));json.dump(report,open(D+'/sculpt-report.json','w'),indent=2)
print('LAKE48_SCULPT_DONE',len(payload['scatter']))
