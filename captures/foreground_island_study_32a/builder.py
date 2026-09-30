"""Local foreground A reconstruction from actual20l native source; no world rebuild."""
from pathlib import Path
import bpy,bmesh,json,hashlib,math,shutil
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
R=Path(__file__).resolve().parents[1];SRC=R/'captures/lantern_islands_study_20l/island_a.blend';OUT=R/'captures/foreground_island_study_32a'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)=='6b19a42b34fb670f46ed7887ad6d7ee33f4b4f456f88cdb71aa5158683ce0bd2'
bpy.ops.wm.open_mainfile(filepath=str(SRC))
cap=bpy.data.objects['island_a grass and exposed rock terrain'];core=bpy.data.objects['island_a faulted bedrock'];path=bpy.data.objects['island_a terrain fitted keeper paths'];pathmat=path.data.materials[0]
source_bvh=BVHTree.FromPolygons([v.co.copy() for v in cap.data.vertices],[list(p.vertices) for p in cap.data.polygons])
def oldheight(x,y):
 hit=source_bvh.ray_cast(Vector((x,y,100)),Vector((0,0,-1)))
 assert hit[0] is not None,(x,y)
 return hit[0].z
def cage(x,y):
 return (7+.22*(x-7) if x>7 else (-35+.75*(x+35) if x< -35 else x), -10+.30*(y+10) if y< -10 else (30+.70*(y-30) if y>30 else y))
def inverse(x,y):
 return (7+(x-7)/.22 if x>7 else (-35+(x+35)/.75 if x< -35 else x),-10+(y+10)/.30 if y< -10 else (30+(y-30)/.70 if y>30 else y))
# Full native house footprints remain rigid; only their terrain sites move.
pads=[dict(id='left_house',xy=[-23,3],half=[4.4,6.15],yaw=0.,height=28.,scale=1.),dict(id='right_house',xy=[-8,19],half=[3.8,5.3],yaw=-.15,height=28.5,scale=.85)]
routes=[[[-23,-3.1],[-22,-6],[-14,-6],[-9,-3],[3,-1],[6,5],[1,9]],[[-8.8,13.75],[-12,13],[-14,9],[-14,4],[-12,0],[-9,-3]],[[-22,-6],[-29,-9],[-36,-13],[-48,-17],[-59,-18]]]
trees=[[-38,7,.95],[-32,11,1.05],[-29,16,.8],[-38,19,.65],[-30,-3,.65],[4,22,.7],[10,29,.48],[16,36,.38]]
scope='32a authored local A composition design: contract camera-facing rock/grass envelope through coherent positive piecewise XY cage, regrade two new actual house pads and replace old orphan routes with full terrain-fitted paths. Existing tower and all other world regions retained. Coordinates are authored choices informed by current projection, not known reference geography. Actual visual, detailed grade and full-flight acceptance pending.'
plan=dict(scope=scope,source=str(SRC.relative_to(R)),source_sha256=sha(SRC),cage=dict(x_breaks=[-35,7],x_outer_slopes=[.75,.22],y_breaks=[-10,30],y_outer_slopes=[.30,.70]),pads=pads,tower=dict(xy=[-3,6],height=30.0621,yaw=.25),routes_blender_xy=routes,trees_blender_xy_scale=trees)
(OUT/'design-plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
bpy.data.objects.remove(path,do_unlink=True)
before={o.name:dict(vertices=len(o.data.vertices),faces=len(o.data.polygons)) for o in bpy.context.scene.objects if o.type=='MESH'}
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 for axis,bounds in [(0,[-35,7]),(1,[-10,30])]:
  for value in bounds:
   co=Vector((0,0,0));no=co.copy();co[axis]=value;no[axis]=1
   bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=co,plane_no=no,clear_inner=False,clear_outer=False)
 for v in bm.verts:v.co.x,v.co.y=cage(v.co.x,v.co.y)
 if o in [cap,core]:
  # Shared inner and outer pad boundaries make complete footprints planar.
  for pad in pads:
   c,s=math.cos(pad['yaw']),math.sin(pad['yaw']);center=Vector((*pad['xy'],0))
   for axis in [0,1]:
    normal=Vector((c,s,0)) if axis==0 else Vector((-s,c,0))
    for extent in [pad['half'][axis],pad['half'][axis]+3.5]:
     for side in [-1,1]:
      bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=center+normal*extent*side,plane_no=normal,clear_inner=False,clear_outer=False)
  for v in bm.verts:
   x,y,z=v.co;delta=0.
   for pad in pads:
    dx,dy=x-pad['xy'][0],y-pad['xy'][1];c,s=math.cos(pad['yaw']),math.sin(pad['yaw']);u,w=c*dx+s*dy,-s*dx+c*dy
    distance=max(abs(u)-pad['half'][0],abs(w)-pad['half'][1],0.)
    if distance<3.5 and z>12:
     sx,sy=inverse(x,y);t=distance/3.5;weight=1-t*t*(3-2*t)
     delta+=(pad['height']-oldheight(sx,sy))*weight
   v.co.z+=delta*min(1,max(0,(z-12)/4))
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
 bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 o['authoring_role']='Independent editable foreground A component, coherently reshaped from20l'
 print('RESHAPED',o.name,len(o.data.vertices),len(o.data.polygons),flush=True)
# Reconstruct only the path asset against the actual new triangulated cap.
topfaces=[p for p in cap.data.polygons if p.normal.z>.00001];used=sorted({i for p in topfaces for i in p.vertices});lut={k:i for i,k in enumerate(used)}
top=[cap.data.vertices[i].co.copy() for i in used];coords=[Vector((v.x,v.y)) for v in top];tris=[[lut[i] for i in p.vertices] for p in topfaces]
terrain_bvh=BVHTree.FromPolygons(top,tris,all_triangles=True)
def height(x,y):
 hit=terrain_bvh.ray_cast(Vector((x,y,100)),Vector((0,0,-1)));assert hit[0] is not None,(x,y)
 return hit[0].z
def inside(point,loop):
 x,y=point;hit=False;j=len(loop)-1
 for i,(a,b) in enumerate(loop):
  c,d=loop[j]
  if (b>y)!=(d>y) and x<(c-a)*(y-b)/(d-b)+a:hit=not hit
  j=i
 return hit
ribbons=[]
for route in routes:
 left=[];right=[]
 for i,p in enumerate(route):
  direction=(Vector(route[min(i+1,len(route)-1)])-Vector(route[max(i-1,0)])).normalized();n=Vector((-direction.y,direction.x))*.8
  left.append(Vector(p)+n);right.append(Vector(p)-n)
 ribbons.append(left+right[::-1])
edges=list({tuple(sorted((f[i],f[(i+1)%3]))) for f in tris for i in range(3)});loops=[]
for ribbon in ribbons:
 loops.append(list(range(len(coords),len(coords)+len(ribbon))));coords+=ribbon
pv,pe,pt,_,_,_=delaunay_2d_cdt(coords,edges,loops,1,.00001)
selected=[f for f in pt if any(inside(sum((pv[i] for i in f),Vector((0,0)))/len(f),ribbon) for ribbon in ribbons)]
used=sorted({i for f in selected for i in f});lut={i:j for j,i in enumerate(used)};vs=[(pv[i].x,pv[i].y,height(pv[i].x,pv[i].y)+.045) for i in used];n=len(vs)
fs=[tuple(lut[i] for i in f) for f in selected];counts={}
for f in fs:
 for i in range(len(f)):
  e=tuple(sorted((f[i],f[(i+1)%len(f)])));counts[e]=counts.get(e,0)+1
fs+= [tuple(i+n for i in reversed(f)) for f in list(fs)];fs +=[(a,b,b+n,a+n) for (a,b),count in counts.items() if count==1];vs +=[(x,y,z-.35) for x,y,z in list(vs)]
data=bpy.data.meshes.new('32a terrain fitted path mesh');data.from_pydata(vs,[],fs);data.materials.append(pathmat);path=bpy.data.objects.new('island_a terrain fitted keeper paths',data);bpy.context.collection.objects.link(path)
stats=[];defects=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
 volume=bm.calc_volume(signed=True);bad=sum(not e.is_manifold for e in bm.edges);small=sum(f.calc_area()<1e-10 for f in bm.faces)
 stats.append(dict(name=o.name,vertices=len(bm.verts),faces=len(bm.faces),volume_m3=volume,nonmanifold_edges=bad,tiny_faces=small))
 if bad or small or volume<=0:defects.append(stats[-1])
 bm.to_mesh(o.data);bm.free()
sites=[]
for pad in pads+[dict(id='tower',xy=[-3,6],half=[4.015,4.015],yaw=.25,height=30.0621032714844)]:
 c,s=math.cos(pad['yaw']),math.sin(pad['yaw']);samples=[]
 for a in [-1,0,1]:
  for b in [-1,0,1]:
   u,w=a*pad['half'][0],b*pad['half'][1];x,y=pad['xy'][0]+c*u-s*w,pad['xy'][1]+s*u+c*w;z=height(x,y);samples.append(dict(xy=[x,y],z=z,error=z-pad['height']))
 sites.append(dict(id=pad['id'],samples=samples,max_error=max(abs(t['error']) for t in samples)))
bpy.context.scene['scope']=scope;bpy.context.scene['path_routes_blender_xy']=json.dumps(routes);bpy.context.scene['32a_site_design']=json.dumps(plan)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'island_a.blend'))
report=dict(scope=scope,source_basis_sha256=sha(SRC),native=stats,defects=defects,sites=sites,passed=not defects and all(s['max_error']<.001 for s in sites),before=before)
(OUT/'native-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert report['passed'],json.dumps(dict(defects=defects,sites=sites))
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(OUT/'island_a.glb'),export_format='GLB',use_selection=True,export_apply=True)
report.update(source_sha256=sha(OUT/'island_a.blend'),glb_sha256=sha(OUT/'island_a.glb'))
(OUT/'native-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('32a FOREGROUND SAVED',json.dumps(report),flush=True)
