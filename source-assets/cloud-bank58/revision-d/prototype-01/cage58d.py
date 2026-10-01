"""Context-rebuilt small D crease cage. No Blender, renderer or world operation.

One shared upper-crease surface with full3D folded sides and unequal underside.
No separatecaps, voxelremesh, noise or smoothprimitive. Side winding corrected
here; the pre-reset325/646draft was never validated.
"""
import json,math
from pathlib import Path
import numpy as np
from scipy.spatial import Delaunay
from matplotlib.path import Path as PolyPath
P=Path(__file__).resolve().parent;D=P.parent;PLAN=D/'control-plan58d.json'
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def signed_volume(v,f):
 t=np.asarray(v)[np.asarray(f)];return float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6)
def sample_path(points,spacing):
 q=np.array(points,float);out=[]
 for a,b in zip(q,q[1:]):
  count=max(1,math.ceil(np.linalg.norm(b[:2]-a[:2])/spacing));out.extend(a+(b-a)*(i/count) for i in range(count))
 return [*out,q[-1]]
def nearest_curve(q,points):
 best=None
 for i,(a,b) in enumerate(zip(points,points[1:])):
  diff=b[:2]-a[:2];t=float(np.clip((q-a[:2])@diff/(diff@diff),0,1));near=a+(b-a)*t;distance=float(np.linalg.norm(q-near[:2]))
  if best is None or distance<best[0]:best=(distance,near,i,t)
 return best
def triangulate(points,boundary,constraints):
 points=[list(map(float,p)) for p in points];constraints=list(constraints);refinements=[]
 for iteration in range(9):
  xy=np.array(points)[:,:2];tri=Delaunay(xy).simplices.tolist();edges={tuple(sorted((int(a),int(b)))) for t in tri for a,b in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])]};missing=[(a,b) for a,b in constraints if tuple(sorted((a,b))) not in edges]
  if not missing:break
  revised=[]
  for a,b in constraints:
   if tuple(sorted((a,b))) in edges:revised.append((a,b));continue
   mid=(np.array(points[a])+np.array(points[b]))*.5;found=[i for i,p in enumerate(points) if np.linalg.norm(np.array(p[:2])-mid[:2])<1e-7]
   if found:
    k=found[0];assert abs(points[k][2]-mid[2])<1e-4,('Conflicting UV constraints',a,b,k,points[k],mid)
   else:k=len(points);points.append(mid.tolist())
   assert k not in(a,b);revised.extend([(a,k),(k,b)]);refinements.append(dict(old_edge=[a,b],new_vertex=k,point=mid.tolist()))
  constraints=revised
 else:raise RuntimeError(('Constraint recovery failed',[(a,b,points[a],points[b]) for a,b in missing]))
 poly=PolyPath(boundary);keep=[]
 for t in tri:
  q=xy[t]
  if poly.contains_point(q.mean(0),radius=1e-6):
   if cross(q[1]-q[0],q[2]-q[0])<0:t=[t[0],t[2],t[1]]
   keep.append(t)
 return points,keep,constraints,refinements
def build(plan):
 upper=[c for c in plan['curves'] if c['role'] in ['primary','medium']];belly=[c for c in plan['curves'] if c['role']=='under_fold'];outline=np.array(plan['outline_local_uv'],float)
 # This20m boundary-guide adjustment keeps unchangedR2endpoint(70,-240)inside.
 outline[3]=[70,-255];poly=PolyPath(outline);points=[];roles=[];index={};constraints=[];curve_rows=[]
 def add(q,role,force=False):
  q=np.array(q,float);key=tuple(np.round(q[:2],7))
  if key in index:
   i=index[key]
   if force and abs(points[i][2]-q[2])>1e-5:raise ValueError(('Incompatible control height',roles[i],role,points[i],q.tolist()))
   return i
  i=len(points);index[key]=i;points.append(q.tolist());roles.append(role);return i
 paths=[]
 for c in upper:paths.append((c['id'],sample_path(c['knots_local_uv_and_worldY_m'],70 if c['role']=='primary' else 55)))
 for valley in plan['valley_controls']:
  q=sample_path(valley['knots_local_uv_and_worldY_m'],45);paths.append((valley['id'],q));a=np.array(q)
  for sign in [-1,1]:
   rail=[]
   for i,q0 in enumerate(a):
    diff=a[min(i+1,len(a)-1),:2]-a[max(0,i-1),:2];normal=np.array([-diff[1],diff[0]])/np.linalg.norm(diff);p=q0.copy();p[:2]+=normal*valley['half_width_m']*sign;p[2]+=15;rail.append(p)
   paths.append((valley['id']+('left' if sign<0 else'right'),rail))
 for name,path in paths:
  ids=[add(q,name,True) for q in path];curve_rows.append(dict(id=name,vertex_ids=ids));constraints.extend(zip(ids,ids[1:]))
 # Insert all actual child-junctions into each parent edge before triangulation.
 split=[]
 for a,b in constraints:
  av=np.array(points[a]);bv=np.array(points[b]);diff=bv[:2]-av[:2];length2=diff@diff;items=[(0,a),(1,b)]
  for k,p in enumerate(points):
   if k in(a,b):continue
   p=np.array(p);t=(p[:2]-av[:2])@diff/length2
   if 1e-8<t<1-1e-8 and np.linalg.norm(av[:2]+diff*t-p[:2])<1e-6:
    expect=av[2]+(bv[2]-av[2])*t;assert abs(expect-p[2])<1e-5,('Crossing crease/valley',roles[a],roles[k],expect,p[2]);items.append((float(t),k))
  items=sorted(set(items));split.extend((a0[1],b0[1]) for a0,b0 in zip(items,items[1:]))
 constraints=split;creasearrays=[(c,np.array(c['knots_local_uv_and_worldY_m'],float)) for c in upper]
 def height(uv):
  candidates=[]
  for c,a in creasearrays:
   dist,near,i,t=nearest_curve(uv,a);width=np.array(c['left_right_halfwidth_m'])[i].mean();weight=max(0,1-dist/(width*2.1))
   if weight>0:candidates.append((dist,near[2]-(1.7 if c['role']=='primary' else 1.9)*dist))
  return max(470,max((y for _,y in candidates),default=505))
 for c,a in creasearrays:
  for i,q in enumerate(a):
   diff=a[min(i+1,len(a)-1),:2]-a[max(0,i-1),:2];normal=np.array([-diff[1],diff[0]])/np.linalg.norm(diff)
   for sign,width in [(-1,c['left_right_halfwidth_m'][i][0]),(1,c['left_right_halfwidth_m'][i][1])]:
    uv=q[:2]+normal*width*sign
    if poly.contains_point(uv,radius=-1):
     close=False
     for valley in plan['valley_controls']:
      dist,_,_,_=nearest_curve(uv,np.array(valley['knots_local_uv_and_worldY_m'],float))
      if dist<valley['half_width_m']+12:close=True
     if not close:add([*uv,height(uv)],c['id']+'_shoulder')
 boundary=[]
 for a,b in zip(outline,np.roll(outline,-1,axis=0)):
  n=max(1,math.ceil(np.linalg.norm(b-a)/65));samples=[j/n for j in range(n)];edge=b-a
  for q in points:
   t=(np.array(q[:2])-a)@edge/(edge@edge)
   if 0<=t<1 and np.linalg.norm(a+t*edge-q[:2])<1e-6:samples.append(float(t))
  for t in sorted(set(round(t,10) for t in samples)):
   uv=a+(b-a)*t;existing=next((i for i,q in enumerate(points) if np.linalg.norm(uv-q[:2])<1e-6),None)
   if existing is not None:boundary.append(existing)
   else:boundary.append(add([*uv,max(470,height(uv)-35)],'upper_outline'))
 constraints.extend(zip(boundary,boundary[1:]+boundary[:1]));boundary_xy=np.array([points[i][:2] for i in boundary]);points,topfaces,constraints,refine=triangulate(points,boundary_xy,constraints);roles+=['crease_refinement']*(len(points)-len(roles))
 ordered=[]
 for a,b in zip(boundary,boundary[1:]+boundary[:1]):
  av=np.array(points[a][:2]);bv=np.array(points[b][:2]);diff=bv-av;items=[]
  for i,q in enumerate(points):
   t=(np.array(q[:2])-av)@diff/(diff@diff)
   if -1e-8<=t<1-1e-8 and np.linalg.norm(av+t*diff-q[:2])<1e-6:items.append((float(t),i))
  ordered.extend(i for t,i in sorted(items))
 boundary=ordered;top_count=len(points);faces=list(topfaces);rings=[boundary];returns=[np.array(c['knots_local_uv_and_worldY_m'],float) for c in plan['curves'] if c['role']=='side_under_return']
 for layer in [1,2]:
  ring=[]
  for i,idx in enumerate(boundary):
   q=np.array(points[idx]);nearest=sorted((float(np.linalg.norm(q[:2]-r[0,:2])),j) for j,r in enumerate(returns))[:2];weights=np.array([1/max(distance,20)**2 for distance,j in nearest]);weights/=weights.sum();offsets=[returns[j][layer,:2]-returns[j][0,:2] for distance,j in nearest];uv=q[:2]+sum(w*offset for w,offset in zip(weights,offsets));target_y=sum(w*returns[j][layer,2] for w,(distance,j) in zip(weights,nearest));previous_y=points[rings[-1][i]][2];yy=min(previous_y-(80 if layer==1 else 90),target_y)
   ring.append(len(points));points.append([*uv,yy]);roles.append('side_outward_fold'if layer==1 else'lower_inward_fold')
  prev=rings[-1]
  for i in range(len(boundary)):
   j=(i+1)%len(boundary);a,b,c,e=prev[i],prev[j],ring[j],ring[i]
   faces.extend([[a,e,b],[b,e,c]]) # corrected shared-edge winding
  rings.append(ring)
 lower_ring=rings[-1];underpoints=[points[i] for i in lower_ring];underroles=['lower_boundary']*len(lower_ring);underconstraints=list(zip(range(len(lower_ring)),list(range(1,len(lower_ring)))+[0]));under_poly=PolyPath(np.array(underpoints)[:,:2])
 for c in belly:
  ids=[]
  for q in sample_path(c['knots_local_uv_and_worldY_m'],65):
   if under_poly.contains_point(q[:2]):ids.append(len(underpoints));underpoints.append(q.tolist());underroles.append(c['id'])
  underconstraints.extend(zip(ids,ids[1:]))
 underpoints,underfaces,underconstraints,underrefine=triangulate(underpoints,np.array(underpoints[:len(lower_ring)])[:,:2],underconstraints);mapping=list(lower_ring)
 for i,q in enumerate(underpoints[len(lower_ring):]):mapping.append(len(points));points.append(q);roles.append(underroles[len(lower_ring)+i] if len(lower_ring)+i<len(underroles) else'under_refinement')
 faces.extend([[mapping[t[0]],mapping[t[2]],mapping[t[1]]] for t in underfaces]);u=np.array(plan['local_u_world']);v=np.array(plan['local_v_world']);anchor=np.array(plan['anchor_godot_world_xyz']);local=np.array(points);world=anchor+local[:,0,None]*u+local[:,1,None]*v+np.c_[np.zeros(len(local)),local[:,2],np.zeros(len(local))]
 if signed_volume(world,faces)<0:faces=[list(reversed(f)) for f in faces]
 return dict(reconstructed_after_workspace_reset=True,boundary_corrections=[dict(original_uv=[70,-235],new_uv=[70,-255],reason='Keep unchanged R2 endpoint inside boundary')],name='CloudBank58D_small_continuous_fold_cage',vertices=world.tolist(),faces=faces,local_uv_worldY=local.tolist(),vertex_roles=roles,top_vertex_count=top_count,upper_boundary_indices=boundary,side_ring_indices=rings,upper_curve_vertex_rows=curve_rows,upper_constraints=constraints,lower_constraints=underconstraints,upper_constraint_refinements=refine,lower_constraint_refinements=underrefine,planned_curves=plan['curves'],active_surface_curve_roles=['primary','medium','side_under_return','under_fold'],small_folds_status='Guide only in this first prototype',method='Shared crease cells, actual U-guide derived side returns, noncoplanar B-guide underside; no voxel union',geometry_passed=False,visual_acceptance=False)
if __name__=='__main__':
 mesh=build(json.loads(PLAN.read_text()));(P/'native-cage-input58d.json').write_text(json.dumps(mesh,indent=2)+'\n');print('Reconstructed static D cage',len(mesh['vertices']),len(mesh['faces']))
