"""Fresh native reopen; each component's actual triangles checked against itself."""
import bpy,json,math,collections,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=Path('/workspace/scratch/a29d03198654/Aether/source-assets/lake-cirque54/v1')
EPS=1e-5
bpy.ops.wm.open_mainfile(filepath=str(D/'massif_cirque_wall_cirque54.blend'))
def distinct(points):
 out=[]
 for p in points:
  if all((p-q).length>EPS for q in out):out.append(p)
 return out
def inside(p,tri):
 a,b,c=tri;u=b-a;v=c-a;w=p-a;uu=u.dot(u);uv=u.dot(v);vv=v.dot(v);wu=w.dot(u);wv=w.dot(v);den=uu*vv-uv*uv
 if abs(den)<1e-14:return False
 s=(vv*wu-uv*wv)/den;t=(uu*wv-uv*wu)/den
 return s>=-1e-8 and t>=-1e-8 and s+t<=1+1e-8
def edge_plane(a,b,tri,n):
 da=(a-tri[0]).dot(n);db=(b-tri[0]).dot(n);out=[]
 if abs(da)<=EPS and inside(a,tri):out.append(a)
 if abs(db)<=EPS and inside(b,tri):out.append(b)
 if da*db<0 and abs(da-db)>1e-12:
  p=a+(b-a)*(da/(da-db))
  if inside(p,tri):out.append(p)
 return out
def area(poly):return .5*sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))
def coplanar_overlap(a,b,n):
 axis=max(range(3),key=lambda k:abs(n[k]));keep=[k for k in range(3) if k!=axis]
 aa=[(p[keep[0]],p[keep[1]]) for p in a];bb=[(p[keep[0]],p[keep[1]]) for p in b]
 if area(bb)<0:bb.reverse()
 poly=aa
 for u,v in zip(bb,bb[1:]+bb[:1]):
  old=poly;poly=[]
  if not old:break
  def side(p):return (v[0]-u[0])*(p[1]-u[1])-(v[1]-u[1])*(p[0]-u[0])
  for p,q in zip(old,old[1:]+old[:1]):
   sp,sq=side(p),side(q)
   if sp>=-1e-10:poly.append(p)
   if (sp>=0)!=(sq>=0):
    t=sp/(sp-sq);poly.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
 return abs(area(poly)) if len(poly)>2 else 0.0
def on_shared(p,shared):
 if any((p-q).length<=EPS*3 for q in shared):return True
 for a in shared:
  for b in shared:
   ab=b-a
   if ab.length_squared<EPS*EPS:continue
   t=(p-a).dot(ab)/ab.length_squared
   if -1e-7<=t<=1+1e-7 and (p-a-ab*t).length<=EPS*3:return True
 return False
results=[]
for o in sorted((o for o in bpy.data.objects if o.type=='MESH'),key=lambda o:o.name):
 mesh=o.data;mesh.calc_loop_triangles();verts=[o.matrix_world@v.co for v in mesh.vertices];idx=[tuple(t.vertices) for t in mesh.loop_triangles];tris=[[verts[i] for i in t] for t in idx]
 tree=BVHTree.FromPolygons(verts,idx,all_triangles=True,epsilon=0.0)
 pairs=sorted({(min(a,b),max(a,b)) for a,b in tree.overlap(tree) if a!=b});bad=[];touch=[];shared_boundary=0;rejected_by_plane=0
 for ai,bi in pairs:
  a,b=tris[ai],tris[bi];na=(a[1]-a[0]).cross(a[2]-a[0]).normalized();nb=(b[1]-b[0]).cross(b[2]-b[0]).normalized()
  da=[(p-b[0]).dot(nb) for p in a];db=[(p-a[0]).dot(na) for p in b]
  if min(da)>EPS or max(da)<-EPS or min(db)>EPS or max(db)<-EPS:rejected_by_plane+=1;continue
  common=distinct([p for p in a if any((p-q).length<=EPS for q in b)])
  if na.cross(nb).length<1e-6 and max(abs(x) for x in da)<EPS:
   overlap=coplanar_overlap(a,b,na)
   if overlap>1e-7:bad.append({'triangles':[ai,bi],'type':'coplanar_positive_area_overlap','projected_overlap_area_m2':overlap})
   elif common:shared_boundary+=1
   else:touch.append({'triangles':[ai,bi],'type':'coplanar_zero_area_contact_or_disjoint'})
   continue
  points=[]
  for p,q in zip(a,a[1:]+a[:1]):points+=edge_plane(p,q,b,nb)
  for p,q in zip(b,b[1:]+b[:1]):points+=edge_plane(p,q,a,na)
  points=distinct(points)
  if not points:continue
  length=max((p-q).length for p in points for q in points)
  if common and all(on_shared(p,common) for p in points):shared_boundary+=1;continue
  if length>EPS*3:bad.append({'triangles':[ai,bi],'type':'noncoplanar_crossing_segment','length_m':length,'points_local':[list(p) for p in points]})
  else:touch.append({'triangles':[ai,bi],'type':'isolated_nonshared_vertex_contact','points_local':[list(p) for p in points]})
 result={'component':o.name,'actual_loop_triangles':len(tris),'bvh_candidate_pairs':len(pairs),'plane_separated_pairs':rejected_by_plane,'ordinary_shared_vertex_or_edge_intersections':shared_boundary,'self_crossing_count':len(bad),'self_crossings':bad,'other_zero_area_contacts_or_disjoint_coplanar_candidates':touch,'no_self_crossing':not bad};results.append(result)
 print('CIRQUE54_SELF_INTERSECTION',o.name,'triangles',len(tris),'candidate_pairs',len(pairs),'crossings',len(bad),'contacts',len(touch),flush=True)
report={'blend_sha256':hashlib.sha256((D/'massif_cirque_wall_cirque54.blend').read_bytes()).hexdigest(),'method':'Fresh Blender4.5.14 reopen, actual mesh loop triangles in native source coordinates. Per component BVH overlap broad phase; normalized-plane separation, edge/plane and barycentric containment for noncoplanar triangles, convex2Dclipping for coplanar triangles. Ordinary geometric shared-edge/shared-vertex intersections excluded only when the entire intersection stays on that boundary. Positive-area coplanar overlap or a non-boundary crossing segment is a self-intersection. Components are checked independently; intentional layer/root intersections between distinct objects are not counted.','distance_tolerance_m':EPS,'coplanar_projected_area_tolerance_m2':1e-7,'components':results,'all9_components_no_self_crossing':len(results)==9 and all(r['no_self_crossing'] for r in results)}
json.dump(report,open(D/'actual-triangle-self-intersection-proof.json','w'),indent=2)
assert report['all9_components_no_self_crossing'], 'Actual triangle self-crossings detected; source not clear'
