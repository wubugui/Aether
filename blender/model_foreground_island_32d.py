"""Rebuild only the local A island from explicitly authored crest and rock sections."""
from pathlib import Path
import bpy,bmesh,json,hashlib,math,shutil
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
R=Path(__file__).resolve().parents[1];PLAN=R/'captures/foreground32d-design-plan.json';plan=json.loads(PLAN.read_text(encoding='utf-8'));SRC=R/plan['source'];OUT=R/'captures/foreground_island_study_32d'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)==plan['source_sha256'];assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py');shutil.copy2(PLAN,OUT/'design-plan.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC));capm=list(bpy.data.objects['island_a grass and exposed rock terrain'].data.materials);corem=list(bpy.data.objects['island_a faulted bedrock'].data.materials);pathmat=bpy.data.objects['island_a terrain fitted keeper paths'].data.materials[0]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
boundary=plan['boundary_xyh'];pads=plan['pads'];routes=plan['routes'];trees=plan['trees_blender_xy_scale'];n=len(boundary)
def mesh(name,vs,fs,mats):
 data=bpy.data.meshes.new(name+' mesh');data.from_pydata(vs,[],fs);data.update();o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o)
 for m in mats:data.materials.append(m)
 return o
def inside(point,loop):
 x,y=point;hit=False;j=len(loop)-1
 for i,p in enumerate(loop):
  a,b=p[:2];c,d=loop[j][:2]
  if (b>y)!=(d>y) and x<(c-a)*(y-b)/(d-b)+a:hit=not hit
  j=i
 return hit
def near_edge(x,y):
 best=None
 for i,p in enumerate(boundary):
  q=boundary[(i+1)%n];dx,dy=q[0]-p[0],q[1]-p[1];t=max(0,min(1,((x-p[0])*dx+(y-p[1])*dy)/(dx*dx+dy*dy)));dist=math.hypot(x-p[0]-t*dx,y-p[1]-t*dy)
  if best is None or dist<best[0]:best=(dist,i,t,p[2]+t*(q[2]-p[2]))
 return best
def smooth(t):return t*t*(3-2*t)
def base(x,y):
 return 27.3+2.8*math.exp(-((x+3)/16)**2-((y-6)/13)**2)+1.2*math.exp(-((x+35)/18)**2-((y-5)/18)**2)-.017*max(x,0)**2-.005*max(y-15,0)**2-.005*max(-x-42,0)**2
def route_hits(x,y):
 hits=[]
 for route in routes:
  for p,q in zip(route['xyh'],route['xyh'][1:]):
   dx,dy=q[0]-p[0],q[1]-p[1];t=max(0,min(1,((x-p[0])*dx+(y-p[1])*dy)/(dx*dx+dy*dy)));dist=math.hypot(x-p[0]-t*dx,y-p[1]-t*dy)
   if dist<2.1:
    w=1-smooth(max(0,min(1,(dist-.75)/1.35)));hits.append((p[2]+t*(q[2]-p[2]),w,dist))
 return hits
def heightfield(x,y):
 shore=near_edge(x,y)
 if shore[0]<1e-5:return shore[3]
 value=base(x,y);t=smooth(min(1,shore[0]/5));value=shore[3]*(1-t)+value*t
 rh=route_hits(x,y)
 if rh:
  weight=max(v[1] for v in rh);target=sum(h*w for h,w,d in rh)/sum(w for h,w,d in rh);value=value*(1-weight)+target*weight
 for tx,ty,sc in trees:
  dist=math.hypot(x-tx,y-ty)
  if dist<2.5:
   w=1-smooth(max(0,min(1,(dist-1)/1.5)));value=value*(1-w)+base(tx,ty)*w
 full=None;changes=[]
 for pad in pads:
  dx,dy=x-pad['xy'][0],y-pad['xy'][1];c,s=math.cos(pad['yaw']),math.sin(pad['yaw']);u,v=c*dx+s*dy,-s*dx+c*dy;dist=max(abs(u)-pad['half'][0],abs(v)-pad['half'][1],0)
  if dist<1e-5:full=pad['height']
  if dist<3:changes.append((pad['height'],1-smooth(dist/3)))
 if full is not None:return full
 if changes:
  w=max(v[1] for v in changes);h=sum(h*w for h,w in changes)/sum(w for h,w in changes);value=value*(1-w)+h*w
 return value
coords=[Vector(p[:2]) for p in boundary];edges=[]
def loop(points):
 start=len(coords);coords.extend(Vector(p) for p in points)
 for i in range(len(points)):edges.append((start+i,start+(i+1)%len(points)))
for pad in pads:
 c,s=math.cos(pad['yaw']),math.sin(pad['yaw']);x,y=pad['xy']
 for margin in [0,3]:
  hx,hy=pad['half'][0]+margin,pad['half'][1]+margin;loop([(x+c*u-s*v,y+s*u+c*v) for u,v in [(-hx,-hy),(hx,-hy),(hx,hy),(-hx,hy)]])
for x,y,sc in trees:loop([(x+math.cos(i*math.pi/4),y+math.sin(i*math.pi/4)) for i in range(8)])
for x in range(-55,21,5):
 for y in range(-10,44,5):
  if inside((x+.7,y+.3),boundary):coords.append(Vector((x+.7,y+.3)))
ribbons=[]
for route in routes:
 points=route['xyh'];left=[];right=[]
 for i,p in enumerate(points):
  tangent=(Vector(points[min(i+1,len(points)-1)][:2])-Vector(points[max(i-1,0)][:2])).normalized();normal=Vector((-tangent.y,tangent.x));left.append(Vector(p[:2])+normal*route['width']/2);right.append(Vector(p[:2])-normal*route['width']/2)
 ribbon=left+right[::-1];assert all(inside(p,boundary) for p in ribbon),'Road ribbon outside new compact crest';ribbons.append(ribbon);loop(ribbon)
 for p,q in zip(points,points[1:]):
  a,b=Vector(p[:2]),Vector(q[:2]);length=(b-a).length;tangent=(b-a).normalized();normal=Vector((-tangent.y,tangent.x));steps=max(1,math.ceil(length/2))
  for k in range(steps+1):
   at=a.lerp(b,k/steps)
   for off in [-2.1,-.75,0,.75,2.1]:
    v=at+normal*off
    if inside(v,boundary):coords.append(v)
pv,pe,pt,_,_,_=delaunay_2d_cdt(coords,edges,[list(range(n))],1,.00001)
tris=[list(f) for f in pt if inside(sum((pv[i] for i in f),Vector((0,0)))/len(f),boundary)];assert all(len(f)==3 for f in tris)
used=sorted({i for f in tris for i in f});lut={i:j for j,i in enumerate(used)};top=[(pv[i].x,pv[i].y,heightfield(pv[i].x,pv[i].y)) for i in used];tris=[tuple(lut[i] for i in f) for f in tris];count=len(top)
ec={};direct={}
for f in tris:
 for i in range(3):
  a,b=f[i],f[(i+1)%3];key=tuple(sorted((a,b)));ec[key]=ec.get(key,0)+1;direct[key]=(a,b)
boundary_edges=[direct[k] for k,v in ec.items() if v==1];nextv=dict(boundary_edges);chain=[boundary_edges[0][0]]
while nextv[chain[-1]]!=chain[0]:chain.append(nextv[chain[-1]])
assert len(chain)==len(boundary_edges)
bottom=[(x,y,z-plan['cap_thickness_m']) for x,y,z in top]
faces=list(tris)+[tuple(i+count for i in reversed(f)) for f in tris]+[(a,b,b+count,a+count) for a,b in boundary_edges]
cap=mesh('island_a grass and exposed rock terrain',top+bottom,faces,capm)
for p in cap.data.polygons:
 if p.index>=len(tris):p.material_index=1
 elif p.normal.z<.66:p.material_index=2
# Each rock contour is sampled at the actual cap boundary subdivisions.
cv=list(bottom);cf=list(tris);previous=list(chain)
for ring in plan['rock_section_rings_xyh']+[[(x,y,-6) for x,y,z in plan['rock_section_rings_xyh'][-1]]]:
 current=[]
 for vi in chain:
  x,y,z=top[vi];dist,i,t,h=near_edge(x,y);assert dist<1e-4,('Unexpected nonshore boundary',vi,[x,y,z],dist)
  a,b=Vector(ring[i]),Vector(ring[(i+1)%n]);current.append(len(cv));cv.append(tuple(a.lerp(b,t)))
 for j in range(len(chain)):
  k=(j+1)%len(chain);cf.append((previous[j],current[j],current[k],previous[k]))
 previous=current
cf.append(tuple(reversed(previous)));core=mesh('island_a faulted bedrock',cv,cf,corem)
for p in core.data.polygons:
 if p.center.z<2:p.material_index=min(2,len(corem)-1)
 elif p.normal.x>.3 and p.normal.z<.6:p.material_index=min(1,len(corem)-1)
# Broad connected-looking authored shoulders replace the compressed old wedges.
shape8=[(-1,-.5),(-.4,-.9),(.6,-.8),(1,-.2),(.85,.55),(.2,1),(-.75,.7),(-1,.1)]
def rock(name,center,size,turn):
 c,s=math.cos(turn),math.sin(turn);cx,cy,cz=center;sx,sy,sz=size;vs=[];fs=[]
 for j,(r,h,ox,oy) in enumerate([(1.12,-.35,0,0),(1,.05,-.03,.01),(.81,.63,.13,-.07),(.38,1,-.21,.12)]):
  for i,(x,y) in enumerate(shape8):
   px,py=(x*r+ox)*sx,(y*r+oy)*sy;dh=[-.18,.11,0,-.12,.16,-.09,.04,-.18][i] if j>1 else 0;vs.append((cx+c*px-s*py,cy+s*px+c*py,cz+(h+dh)*sz))
 fs.append(tuple(range(7,-1,-1)))
 for j in range(3):
  for i in range(8):fs.append((j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i))
 fs.append(tuple(range(24,32)));o=mesh(name,vs,fs,corem)
 for p in o.data.polygons:p.material_index=min(2,len(corem)-1) if p.center.z<1.4 else (min(1,len(corem)-1) if p.normal.x>.4 else 0)
for i,(at,size,turn) in enumerate([((-15,-10,12),(12,7,10),-.2),((9,13,11),(7,11,8),.4),((19,31,7),(6,9,7),-.35)]):rock('island_a cliff outcrop %02d'%i,at,size,turn)
for i,(at,size,turn) in enumerate([((-48,-21,0),(8,5,4),.2),((-29,-14,0),(9,5,3),-.3),((1,-9,0),(7,5,4),.35),((22,22,0),(6,8,3),.4),((-54,28,0),(8,6,4),-.2)]):rock('island_a low shore ledge %02d'%i,at,size,turn)
# Path clipping retains every crossed actual terrain edge, so no hovering ribbons.
terrain=BVHTree.FromPolygons([Vector(v) for v in top],tris,all_triangles=True)
def height(x,y):
 hit=terrain.ray_cast(Vector((x,y,100)),Vector((0,0,-1)));assert hit[0] is not None,(x,y);return hit[0].z
pc=[Vector((x,y)) for x,y,z in top];loops=[]
for ribbon in ribbons:loops.append(list(range(len(pc),len(pc)+len(ribbon))));pc+=ribbon
vv,ee,tt,_,_,_=delaunay_2d_cdt(pc,list(ec),loops,1,.00001)
selected=[f for f in tt if any(inside(sum((vv[i] for i in f),Vector((0,0)))/len(f),ribbon) for ribbon in ribbons)]
used=sorted({i for f in selected for i in f});lookup={i:j for j,i in enumerate(used)};vs=[(vv[i].x,vv[i].y,height(vv[i].x,vv[i].y)+.045) for i in used];pn=len(vs);fs=[tuple(lookup[i] for i in f) for f in selected];edges={}
for f in fs:
 for i in range(len(f)):
  key=tuple(sorted((f[i],f[(i+1)%len(f)])));edges[key]=edges.get(key,0)+1
fs+=[tuple(i+pn for i in reversed(f)) for f in list(fs)];fs +=[(a,b,b+pn,a+pn) for (a,b),cnt in edges.items() if cnt==1];vs +=[(x,y,z-.20) for x,y,z in list(vs)];mesh('island_a terrain fitted keeper paths',vs,fs,[pathmat])
stats=[];defects=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update();vol=bm.calc_volume(signed=True);bad=sum(not e.is_manifold for e in bm.edges);tiny=sum(f.calc_area()<1e-10 for f in bm.faces)
 row=dict(name=o.name,vertices=len(bm.verts),faces=len(bm.faces),volume_m3=vol,nonmanifold_edges=bad,tiny_faces=tiny);stats.append(row)
 if bad or tiny or vol<=0:defects.append(row)
 bm.to_mesh(o.data);bm.free();o['authoring_role']='Independent editable32d local foreground island component'
sites=[]
for pad in pads:
 c,s=math.cos(pad['yaw']),math.sin(pad['yaw']);samples=[]
 for u in [-pad['half'][0],0,pad['half'][0]]:
  for v in [-pad['half'][1],0,pad['half'][1]]:
   x,y=pad['xy'][0]+c*u-s*v,pad['xy'][1]+s*u+c*v;z=height(x,y);samples.append(dict(xy=[x,y],z=z,error=z-pad['height']))
 sites.append(dict(id=pad['id'],samples=samples,max_error=max(abs(v['error']) for v in samples)))
treecheck=[]
for x,y,sc in trees:
 loc,normal,face,dist=terrain.ray_cast(Vector((x,y,100)),Vector((0,0,-1)));treecheck.append(dict(xy=[x,y],scale=sc,height=loc.z,normal=list(normal),face=face));assert normal.z>=.65
bpy.context.scene['scope']=plan['scope'];bpy.context.scene['32d_site_design']=json.dumps(plan);bpy.context.scene['path_routes_blender_xy']=json.dumps([r['xyh'] for r in routes]);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'island_a.blend'))
report=dict(scope=plan['scope'],source_basis_sha256=sha(SRC),native=stats,defects=defects,sites=sites,tree_axis_check=treecheck,passed=not defects and all(p['max_error']<.001 for p in sites))
(OUT/'native-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');assert report['passed'],json.dumps(dict(defects=defects,sites=sites))
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(OUT/'island_a.glb'),export_format='GLB',use_selection=True,export_apply=True);report.update(source_sha256=sha(OUT/'island_a.blend'),glb_sha256=sha(OUT/'island_a.glb'));(OUT/'native-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('32d COMPACT CREST SAVED',json.dumps(report),flush=True)
