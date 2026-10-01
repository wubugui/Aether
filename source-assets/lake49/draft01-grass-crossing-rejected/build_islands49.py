import bpy,bmesh,math,json,random,os,hashlib,collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake49'
S='/workspace/scratch/a29d03198654/Aether/source-assets/lake48'
os.makedirs(D,exist_ok=True)
BASE='3034e74f33087f8eb843ffc19e170bb14bbe85d1c7a272edfa01af614bd18fcd'
# Read actual saved48 triangle geometry and all unchanged adjacent mountain feet.
p48=json.load(open(S+'/lake48-payload.json'));bedfaces=[];changed=set()
for m in p48['meshes']:bedfaces+=m['vertices'];changed.add(m['name'])
for name,m in json.load(open(S+'/support47.json'))['meshes'].items():
 if name not in changed:bedfaces+=m['faces']
bedbvh=BVHTree.FromPolygons([Vector(v) for v in bedfaces],[(i,i+1,i+2) for i in range(0,len(bedfaces),3)],all_triangles=True)
def bed(x,z):
 hit=bedbvh.ray_cast(Vector((x,1200,z)),Vector((0,-1,0)),2400)[0]
 assert hit is not None,(x,z,'No bed support')
 return hit.y

def godot(p,a):return [p.x+a[0],p.z,-p.y+a[2]]
def local(g,a):return Vector((g[0]-a[0],-(g[2]-a[2]),g[1]))
PALETTES={'rockroot':[(.22,.25,.29,1),(.27,.29,.31,1),(.30,.31,.32,1)],'shoulder':[(.33,.36,.40,1),(.39,.41,.43,1),(.46,.45,.43,1),(.31,.35,.41,1)],'wetshore':[(.51,.47,.40,1),(.60,.54,.44,1),(.44,.44,.43,1)],'grasscap':[(.32,.38,.22,1),(.38,.43,.26,1),(.28,.34,.21,1)],'tree_trunk':[(.20,.15,.105,1),(.28,.205,.14,1),(.34,.26,.17,1)],'tree_crown':[(.12,.235,.17,1),(.16,.29,.20,1),(.21,.33,.215,1),(.27,.365,.24,1)],'grass_tuft':[(.35,.44,.18,1),(.44,.50,.23,1)]}
meshes=[];objects=[];rng=None;anchor=None

def mesh_obj(name,vs,fs,role,collision=True):
 m=bpy.data.meshes.new(name+'_Mesh');m.from_pydata(vs,[],fs);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
 o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o['lake49_role']=role;o['collision']=collision
 pal=PALETTES[role]
 attr=m.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER');m.color_attributes.active_color=attr
 for p in m.polygons:
  col=pal[rng.randrange(len(pal))]
  # Quiet facet variation follows a restrained palette, no random rainbow noise.
  for li in p.loop_indices:attr.data[li].color=col
 mat=bpy.data.materials.get('Lake49_'+role)
 if not mat:
  mat=bpy.data.materials.new('Lake49_'+role);mat.diffuse_color=pal[0];mat.use_nodes=True;nodes=mat.node_tree.nodes;bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.93;vc=nodes.new('ShaderNodeVertexColor');vc.layer_name='Color';mat.node_tree.links.new(vc.outputs['Color'],bs.inputs['Base Color'])
 m.materials.append(mat);objects.append(o);return o

def ring_mesh(name,rings,role,collision=True,cap_bottom=True,cap_top=True):
 n=len(rings[0]);vs=[v for r in rings for v in r];fs=[]
 for k in range(len(rings)-1):
  for i in range(n):j=(i+1)%n;fs.extend([(k*n+i,k*n+j,(k+1)*n+j),(k*n+i,(k+1)*n+j,(k+1)*n+i)])
 if cap_bottom:
  q=len(vs);vs.append(tuple(sum(v[d] for v in rings[0])/n for d in range(3)))
  fs += [(q,(i+1)%n,i) for i in range(n)]
 if cap_top:
  q=len(vs);vs.append(tuple(sum(v[d] for v in rings[-1])/n for d in range(3)))
  off=(len(rings)-1)*n;fs += [(q,off+i,off+(i+1)%n) for i in range(n)]
 return mesh_obj(name,vs,fs,role,collision)

def bvh(o):
 m=o.data;m.calc_loop_triangles();return BVHTree.FromPolygons([v.co for v in m.vertices],[tuple(t.vertices) for t in m.loop_triangles],all_triangles=True)
def surf(o,x,y):
 p=bvh(o).ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)[0]
 assert p is not None,(o.name,x,y)
 return p.z

def irregular_boulder(name,center,scale,role='wetshore'):
 # An irregular closed twelve-corner rock, not a sphere or circular disk.
 outline=[(-.95,-.35),(-.55,-.92),(.25,-1),(.95,-.45),(.8,.52),(.08,.9),(-.70,.66)]
 rings=[]
 for k,(s,z) in enumerate([(.68,-.65),(1,-.06),(.66,.58),(.29,.96)]):
  rings.append([(center[0]+(x*s+.15*k/3)*scale[0],center[1]+(y*s-.06*k)*scale[1],center[2]+(z+rng.uniform(-.12,.12))*scale[2]) for x,y in outline])
 return ring_mesh(name,rings,role)

def grass_patch(name,center,radii,shoulder):
 n=11;ring=[]
 for i in range(n):
  t=i*2*math.pi/n;rr=[.80,1,.83,.94,.73,.96,.81,.91,.68,.89,.92][i];x=center[0]+math.cos(t)*radii[0]*rr;y=center[1]+math.sin(t)*radii[1]*rr;z=surf(shoulder,x,y);ring.append((x,y,z+.045))
 # Multi-ring surface tracks support triangles; a thin closed skin, never a hat.
 top=[]
 for s in [1,.55]:
  top.append([(center[0]+(x-center[0])*s,center[1]+(y-center[1])*s,surf(shoulder,center[0]+(x-center[0])*s,center[1]+(y-center[1])*s)+.045) for x,y,z in ring])
 vs=[(x,y,z-.13) for x,y,z in top[0]]+top[0]+top[1];fs=[]
 for k in range(2):
  for i in range(n):j=(i+1)%n;fs += [(k*n+i,k*n+j,(k+1)*n+j),(k*n+i,(k+1)*n+j,(k+1)*n+i)]
 topc=len(vs);vs.append((center[0],center[1],surf(shoulder,*center)+.045));botc=len(vs);vs.append((center[0],center[1],surf(shoulder,*center)-.085))
 for i in range(n):j=(i+1)%n;fs.extend([(2*n+i,2*n+j,topc),(j,i,botc)])
 return mesh_obj(name,vs,fs,'grasscap',False)

def segment(name,a,b,rad0,rad1,role='tree_trunk',n=6):
 a=Vector(a);b=Vector(b);d=(b-a).normalized();u=d.cross(Vector((0,0,1)))
 if u.length<.01:u=d.cross(Vector((0,1,0)))
 u.normalize();v=d.cross(u);rings=[]
 for p,r in [(a,rad0),(b,rad1)]:rings.append([tuple(p+(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n))*r) for i in range(n)])
 return ring_mesh(name,rings,role,role=='tree_trunk')

def pine(name,xy,h,supports):
 x,y=xy;hits=[(surf(o,x,y),o) for o in supports if bvh(o).ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)[0] is not None];z,support=max(hits,key=lambda q:q[0]);base=Vector((x,y,z));lean=Vector((rng.uniform(-.025,.035)*h,rng.uniform(-.018,.025)*h,0));r=.020*h
 trunk=segment(name+'_trunk',base-Vector((0,0,.16)),base+lean+Vector((0,0,h*.96)),r,r*.19)
 # Tier center offsets and branch clusters deliberately differ per whorl and tree.
 for k in range(5):
  frac=.23+.145*k;rad=h*(.205-.031*k);cz=z+h*frac;shift=lean*frac;angle0=rng.uniform(0,math.tau);lobes=5 if k<3 else 4
  vs=[];fs=[]
  for j in range(lobes):
   angle=angle0+j*math.tau/lobes+rng.uniform(-.18,.18);d=Vector((math.cos(angle),math.sin(angle),0));p=Vector((-d.y,d.x,0));length=rad*rng.uniform(.82,1.15);c=Vector((x+shift.x,y+shift.y,cz+rng.uniform(-.03,.03)*h));tip=c+d*length+Vector((0,0,-.022*h));side=.29*length
   # Angular descending skirt, lifted folded ridge and forked tip. All boughs closed.
   q=[c-d*.16*length+p*.17*length+Vector((0,0,.12*h)),c+d*.47*length+p*side+Vector((0,0,.035*h)),tip+p*.10*length,c+d*.62*length-p*side+Vector((0,0,-.025*h)),c-d*.16*length-p*.17*length+Vector((0,0,.10*h)),c+d*.40*length+Vector((0,0,.20*h)),c+d*.28*length+Vector((0,0,-.055*h))]
   off=len(vs);vs += [tuple(t) for t in q];ff=[(0,1,5),(1,2,5),(2,3,5),(3,4,5),(4,0,5),(1,0,6),(2,1,6),(3,2,6),(4,3,6),(0,4,6)];fs += [tuple(off+t for t in f) for f in ff]
   if k<3:segment(name+'_branch_%02d_%02d'%(k,j),c,c+d*length*.80+Vector((0,0,-.015*h)),r*.38,r*.06)
  mesh_obj(name+'_crown_tier_%02d'%k,vs,fs,'tree_crown',False)
 # Narrow irregular multi-level leader links the final whorl to the apex.
 rings=[]
 for frac,rr in [(.76,.065),(.86,.082),(.94,.041), (1,.003)]:
  c=base+lean*frac+Vector((0,0,h*frac));rings.append([tuple(c+Vector((math.cos(i*math.tau/5)*rr*h,math.sin(i*math.tau/5)*rr*h,0))) for i in range(5)])
 ring_mesh(name+'_leader',rings,'tree_crown',False)
 return {'name':name,'foot_world':godot(base,anchor),'support_mesh':support.name,'trunk_mesh':trunk.name,'height_m':h,'trunk_burial_m':.16}

specs=[{'name':'island_near_left','anchor':[1045,0,-1150],'size':[68,42],'height':4.6,'seed':491,'trees':[(-12,-2,10),(10,5,14)]},{'name':'island_far_middle','anchor':[1060,0,-1650],'size':[72,42],'height':3.3,'seed':492,'trees':[(-18,0,10),(0,-4,14),(17,4,17)]},{'name':'island_near_right','anchor':[1380,0,-1120],'size':[40,26],'height':3.6,'seed':493,'trees':[(-7,-1,9),(7,1,11)]},{'name':'foreground_rock','anchor':[1200,0,-1070],'size':[18,14],'height':4,'seed':494,'trees':[]}]
payload={'schema_version':1,'baseline_sha256':BASE,'source_metadata':{'design':'Four native independent49 rockroot islands; seven asymmetrical multi-bough pines; exact48 bed BVH; all coordinates inferred','source':'source-assets/lake49','coordinate_system':'Payload Godot world XYZ, clockwise triangles. Native blend local Blender Z-up; GLB local Y-up; apply island.anchor once.','hardware_gpu_acceptance':False},'islands':[]}
checks={'islands':[],'all_closed':True}
for spec in specs:
 bpy.ops.wm.read_factory_settings(use_empty=True);objects=[];rng=random.Random(spec['seed']);anchor=spec['anchor'];name=spec['name'];w,d=spec['size'];h=spec['height'];n=16
 outline=[]
 mult=[.90,.98,.81,1,.84,.94,.74,.92,1,.82,.96,.81,.90,.78,1,.85]
 for i in range(n):
  t=i*math.tau/n;outline.append((math.cos(t)*w/2*mult[i],math.sin(t)*d/2*mult[i]))
 # Dense bottom rings conform to actual48 topmost bed: 1.5m burial at each vertex.
 rings=[];bed_samples=[]
 for s in [.001,.20,.40,.60,.80,1.06]:
  rr=[]
  for x,y in outline:
   bx,by=x*s,y*s;gy=bed(anchor[0]+bx,anchor[2]-by);rr.append((bx,by,gy-1.5));bed_samples.append({'world':[anchor[0]+bx,gy-1.5,anchor[2]-by],'actual_bed_y':gy,'burial_m':1.5})
  rings.append(rr)
 rings.append([(x,y,-.34) for x,y in outline])
 root=ring_mesh(name+'_rockroot',rings,'rockroot')
 # A ridge-biased, cut-back mass with irregular shoulders, not a circular cone.
 shoulder_rings=[]
 for k,s in enumerate([.995,1,.75,.40]):
  rr=[]
  for i,(x,y) in enumerate(outline):
   if k==0:z=-.65
   elif k==1:z=rng.uniform(-.12,.42)
   elif k==2:z=h*(.36+.36*(.5+.5*math.sin(i*1.71+.8)))
   else:z=h*(.70+.28*(.5+.5*math.sin(i*1.43+.3)))
   rr.append((x*s+(k/3)*w*.055,y*s-(k/3)*d*.045,z))
  shoulder_rings.append(rr)
 shoulder=ring_mesh(name+'_shoulder',shoulder_rings,'shoulder')
 supports=[shoulder]
 if spec['trees']:
  cap=grass_patch(name+'_grasscap_west',(-w*.10,-d*.005),(w*.22,d*.25),shoulder);supports.append(cap)
  cap=grass_patch(name+'_grasscap_east',(w*.18,d*.065),(w*.17,d*.23),shoulder);supports.append(cap)
 # Discrete pale edge rocks, connected underwater to the root footprint.
 for k,i in enumerate([1,4,7,9,12,14]):
  x,y=outline[i];q=.89;irregular_boulder(name+'_wetshore_%02d'%k,(x*q,y*q,.10),(w*.07*(1+k%2*.4),d*.10,h*.35),'wetshore')
 trees=[]
 for i,(x,y,hh) in enumerate(spec['trees']):trees.append(pine(name+'_pine_%02d'%(i+1),(x,y),hh,supports))
 if not spec['trees']:
  for i in range(7):
   x=-1.6+rng.random()*.9;y=.5+rng.random()*.6;z=surf(shoulder,x,y);tilt=Vector((rng.uniform(-.55,.55),rng.uniform(-.45,.45),rng.uniform(1,1.8)));p=Vector((x,y,z));q=p+tilt
   v=[p+Vector((-.07,0,0)),p+Vector((.07,0,0)),p+Vector((0,.08,0)),q];mesh_obj(name+'_grassblade_%02d'%i,[tuple(x) for x in v],[(0,1,2),(0,3,1),(1,3,2),(2,3,0)],'grass_tuft',False)
 records=[];stats=[]
 for o in objects:
  m=o.data;m.calc_loop_triangles();attr=m.color_attributes.active_color;verts=[];cols=[]
  for t in m.loop_triangles:
   for vi,li in zip(reversed(t.vertices),reversed(t.loops)):verts.append(godot(m.vertices[vi].co,anchor));cols.append(list(attr.data[li].color))
  role=o['lake49_role'];records.append({'name':o.name,'role':role,'vertices':verts,'colors':cols,'collision':bool(o['collision'])})
  bm=bmesh.new();bm.from_mesh(m);volume=bm.calc_volume(signed=True);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);badarea=sum(f.calc_area()<1e-10 for f in bm.faces);bm.free();stat={'name':o.name,'role':role,'triangles':len(verts)//3,'open_edges':boundary,'nonmanifold_edges':nonmanifold,'degenerate_faces':badarea,'outward_signed_volume_m3':volume};stats.append(stat);assert boundary==0 and nonmanifold==0 and badarea==0 and volume>0,stat
 # Explicit metadata is stored in native source objects as well as payload.
 for o in objects:o['island_anchor_godot']=anchor;o['source_game48_sha256']=BASE
 bpy.context.scene['asset_name']=name;bpy.context.scene['source_game48_sha256']=BASE;bpy.context.scene['world_anchor_godot']=anchor
 bpy.ops.wm.save_as_mainfile(filepath=D+'/'+name+'.blend')
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=D+'/'+name+'.glb',export_format='GLB',use_selection=True,export_yup=True,export_draco_mesh_compression_enable=False,export_apply=True)
 rec={**{k:v for k,v in spec.items() if k not in ['trees','seed']},'source_blend':'source-assets/lake49/'+name+'.blend','source_glb':'source-assets/lake49/'+name+'.glb','meshes':records,'trees':trees,'bedroot_samples':bed_samples}
 payload['islands'].append(rec);checks['islands'].append({'name':name,'meshes':stats,'tree_count':len(trees),'bed_root_vertex_samples':len(bed_samples),'rockroot_bed_burial_m':1.5})
 print('CREATED',name,len(records),'objects',sum(s['triangles'] for s in stats),'triangles',flush=True)
json.dump(payload,open(D+'/lake49-payload.json','w'));json.dump(checks,open(D+'/native-topology-checks.json','w'),indent=2)
print('LAKE49_NATIVE_DONE',flush=True)
