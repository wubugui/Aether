"""Bounded native-heightfield edit. No engine/world generation or scene writes."""
from pathlib import Path
import json, numpy as np,hashlib,collections
D=Path(__file__).resolve().parent
source=json.loads((D/'native-authority/authority.json').read_text());A=source['surfaces'][0]['arrays']
p=np.array(A[0],np.float32);indices=np.array(A[12],np.int32);faces=indices.reshape(-1,3);origin=np.array(source['origin'],np.float64);world=p.astype(np.float64)+origin
bounds=np.array([-3440,-3090,-3816,-3430],float)
inside=(world[:,0]>bounds[0])&(world[:,0]<bounds[1])&(world[:,2]>bounds[2])&(world[:,2]<bounds[3])
protected_faces=~inside[faces].all(axis=1)
_,groups=np.unique(p,axis=0,return_inverse=True);frozen_groups=np.unique(groups[faces[protected_faces].ravel()]);unlocked=inside&~np.isin(groups,frozen_groups)
def bump(z,center,width):
 t=(z-center)/width;return np.where(abs(t)<1,(1-t*t)**2,0)
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
x,y,z=world.T
# Direct source sea-level segments determine the true local waterline.
shore_segments=[]
for tt in p[faces].astype(float)+origin:
 hits=[]
 for aa,bb in zip(tt,np.roll(tt,-1,axis=0)):
  if (aa[1]<=0<bb[1]) or (bb[1]<=0<aa[1]):hits.append(aa+(bb-aa)*(-aa[1]/(bb[1]-aa[1])))
 if len(hits)==2:shore_segments.append(hits)
shore_segments=np.array(shore_segments)
def shore_at(zz):
 a,b=shore_segments[:,0],shore_segments[:,1];ok=((a[:,2]<=zz)&(b[:,2]>=zz))|((b[:,2]<=zz)&(a[:,2]>=zz));ok&=abs(b[:,2]-a[:,2])>1e-9
 hit=a[ok,0]+(zz-a[ok,2])/(b[ok,2]-a[ok,2])*(b[ok,0]-a[ok,0]);assert len(hit),zz
 return float(hit.min())
shore=np.array([shore_at(zz) if -3820<zz<-3420 else .6756552045191282*zz-853.9352502775308 for zz in z]);d=x-shore
along=smooth(-3798,-3650,z)*(1-smooth(-3530,-3440,z))
bay=bump(z,-3630,110)
delta_x=32*bay*along*unlocked
bench_width=32+14*smooth(-3700,-3510,z)
bench_height=7+2*smooth(-3700,-3510,z)
back_x=np.minimum(shore+188-60*smooth(-3660,-3500,z),bounds[1]-35)
strength=along*unlocked
# Preserve all original XZ coordinates. Shift the sampled height profile instead of
# sliding vertices against frozen triangles, so no projected fold can be introduced.
def original_height(xx,zz):
 t=p[faces].astype(float)+origin;a,b,c=t[:,0],t[:,1],t[:,2]
 den=(b[:,2]-c[:,2])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,2]-c[:,2]);ok=abs(den)>1e-10
 u=np.divide((b[:,2]-c[:,2])*(xx-c[:,0])+(c[:,0]-b[:,0])*(zz-c[:,2]),den,out=np.zeros_like(den),where=ok)
 v=np.divide((c[:,2]-a[:,2])*(xx-c[:,0])+(a[:,0]-c[:,0])*(zz-c[:,2]),den,out=np.zeros_like(den),where=ok);w=1-u-v
 ok&=(u>=-1e-7)&(v>=-1e-7)&(w>=-1e-7)
 assert ok.any(),(xx,zz)
 return float((u*a[:,1]+v*b[:,1]+w*c[:,1])[ok].max())
newp=p.copy();memo={};section_controls={}
for i in np.flatnonzero(unlocked & (strength>1e-8)):
 key=int(groups[i])
 if key not in memo:
  sea_x=shore[i]+delta_x[i]
  if x[i]>=back_x[i]:
   memo[key]=np.float32(y[i])
  else:
   back_y=original_height(back_x[i],z[i])
   controls_x=[sea_x,sea_x+8,sea_x+bench_width[i],back_x[i]]
   controls_y=[0,4,bench_height[i],back_y]
   assert controls_x[-1]>controls_x[-2]+8,(z[i],controls_x)
   if x[i]<sea_x:goal=original_height(x[i]-delta_x[i],z[i])
   else:goal=float(np.interp(x[i],controls_x,controls_y))
   # Broad longitudinal end sections are the sole height reconciliation.
   # The main landward rise itself is controlled by the explicit section knots.
   memo[key]=np.float32(y[i]+(goal-y[i])*strength[i])
   section_controls[str(float(z[i]))]={'z':float(z[i]),'x':list(map(float,controls_x)),'y':list(map(float,controls_y)),'longitudinal_weight':float(along[i])}
 newp[i,1]=memo[key]

moved=np.any(newp!=p,axis=1);changed_tri=moved[faces].any(axis=1)
assert not np.any(changed_tri&protected_faces)
assert np.array_equal(newp[faces[protected_faces]],p[faces[protected_faces]])
# Freeze attributes used by every unchanged triangle, including shared indices.
attr_locked=np.unique(faces[~changed_tri]);active_indices=np.setdiff1d(np.unique(faces[changed_tri]),attr_locked)
normals=np.array(A[1],np.float32);newnorm=normals.copy();t=newp[faces].astype(float);area=-np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);acc=np.zeros_like(p,dtype=float)
for corner in range(3):np.add.at(acc,faces[:,corner],area)
acc/=np.linalg.norm(acc,axis=1)[:,None];newnorm[active_indices]=acc[active_indices].astype(np.float32)
tan=np.array(A[2],np.float32).reshape(-1,4);newtan=tan.copy();v=tan[active_indices,:3].astype(float);n=newnorm[active_indices].astype(float);v-=np.einsum('ij,ij->i',v,n)[:,None]*n;length=np.linalg.norm(v,axis=1)
assert np.all(length>1e-8);newtan[active_indices,:3]=(v/length[:,None]).astype(np.float32)
B=[newp.tolist(),newnorm.tolist(),newtan.reshape(-1).tolist(),A[3]]+A[4:]
collider=np.array(source['collider_faces'],np.float32);newcol=collider.copy();assert len(collider)==len(indices)
# Keep exact original collider corners unless their corresponding raw mesh vertex moved.
# All incidences of a moved native coordinate receive one exact new float32 coordinate.
corner_changed=moved[indices];newcol[corner_changed]=newp[indices[corner_changed]]
# Topology proof is on exact welded positions; asset is originally an open heightfield.
def topo(pts):
 unique,weld=np.unique(pts,axis=0,return_inverse=True);f=weld[faces];edge=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,counts=np.unique(edge,axis=0,return_counts=True)
 area2=np.cross((pts[faces[:,1]]-pts[faces[:,0]]).astype(float),(pts[faces[:,2]]-pts[faces[:,0]]).astype(float))
 return {'unique_positions':len(unique),'triangle_count':len(f),'boundary_edges':int(np.sum(counts==1)),'nonmanifold_edges':int(np.sum(counts>2)),'degenerate_3d':int(np.sum(np.linalg.norm(area2,axis=1)<=1e-8)),'degenerate_xz':int(np.sum(abs(area2[:,1])<=1e-8)),'signed_xz_min':float(area2[:,1].min()),'signed_xz_max':float(area2[:,1].max())}
oldtop,newtop=topo(p),topo(newp)
assert oldtop['boundary_edges']==newtop['boundary_edges'] and oldtop['nonmanifold_edges']==newtop['nonmanifold_edges']==0
oldc=np.cross((p[faces[:,1]]-p[faces[:,0]]).astype(float),(p[faces[:,2]]-p[faces[:,0]]).astype(float))[:,1]
newc=np.cross((newp[faces[:,1]]-newp[faces[:,0]]).astype(float),(newp[faces[:,2]]-newp[faces[:,0]]).astype(float))[:,1]
assert np.all(oldc*newc>0)
# Height support sampler uses the actual candidate triangles, not procedural geography.
def sample(pts,x,z):
 t=pts[faces].astype(float)+origin;a,b,c=t[:,0],t[:,1],t[:,2];den=(b[:,2]-c[:,2])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,2]-c[:,2]);ok=abs(den)>1e-10
 u=np.divide((b[:,2]-c[:,2])*(x-c[:,0])+(c[:,0]-b[:,0])*(z-c[:,2]),den,out=np.zeros_like(den),where=ok)
 v=np.divide((c[:,2]-a[:,2])*(x-c[:,0])+(a[:,0]-c[:,0])*(z-c[:,2]),den,out=np.zeros_like(den),where=ok);w=1-u-v;ok&=(u>=-1e-7)&(v>=-1e-7)&(w>=-1e-7)
 where=np.flatnonzero(ok)
 if not len(where):return None
 y=u*a[:,1]+v*b[:,1]+w*c[:,1];i=int(where[np.argmax(y[where])]);normal=-np.cross(t[i,1]-t[i,0],t[i,2]-t[i,0]);normal/=np.linalg.norm(normal)
 return {'height':float(y[i]),'triangle_index':i,'slope_degrees':float(np.degrees(np.arccos(np.clip(normal[1],-1,1))))}
intake=json.loads((D/'intake/intake.json').read_text());scatter=[];root_minheight_failures=[]
for group in intake['scatter']['groups']:
 grouptransform=np.array(group['group_world_transform'],np.float32)
 assert np.array_equal(grouptransform[:3,:3],np.eye(3,dtype=np.float32))
 grouporigin=grouptransform[:3,3]
 for entry in group['instances']:
  buf=np.array(entry['original_buffer'],np.float32);pos=(buf[[3,7,11]]+grouporigin).astype(np.float32).astype(float);kind=group['kind']
  before=sample(p,pos[0],pos[2]);after=sample(newp,pos[0],pos[2]);newpos=pos.copy()
  assert before is not None and after is not None,('missing support',group['node'],entry['index'])
  minh={'pine':3,'rock':.5,'bush':1.5}[kind]
  if after['height']<minh:root_minheight_failures.append({'node':group['node'],'index':entry['index'],'actual_height':after['height'],'unchanged_minimum_guard':minh})
  offset=float(pos[1]-before['height']);newpos[1]=after['height']+offset
  newbuf=buf.copy();newbuf[7]=np.float32(newpos[1]-grouporigin[1])
  actualpos=(newbuf[[3,7,11]]+grouporigin).astype(np.float32).astype(float);actual=sample(newp,actualpos[0],actualpos[2])
  scatter.append({'node':group['node'],'kind':kind,'index':entry['index'],'source_group_origin':grouporigin.tolist(),'before_position':pos.tolist(),'candidate_position':actualpos.tolist(),'before_buffer':buf.tolist(),'candidate_buffer':newbuf.tolist(),'xz_relocated':False,'xz_distance':0.,'before_support':before,'candidate_support':actual,'preserved_origin_offset':offset,'candidate_origin_offset':float(actualpos[1]-actual['height'])})
report={'source_scene':source['source'],'source_sha256':source['source_sha256'],'source_mesh':source['mesh'],'source_shape':source['shape'],'box_xmin_xmax_zmin_zmax':bounds.tolist(),'origin':origin.tolist(),'design_inference':'Revision B: explicit water/foot/unequal bench/back-slope section knots; 30m inland and56m northern expansion inside same tile. Reference-informed inference.', 'positions_moved':int(moved.sum()),'triangles_changed':int(changed_tri.sum()),'normal_tangent_indices_modified':len(active_indices),'protected_faces':int(protected_faces.sum()),'unchanged_faces':int((~changed_tri).sum()),'raw_fields_unchanged_on_all_unchanged_triangles':True,'all_indices_colors_uv_absence_unchanged':True,'tile_boundary_positions_exact':bool(np.array_equal(newp[np.any((p[:,[0,2]]==0)|(p[:,[0,2]]==768),axis=1)],p[np.any((p[:,[0,2]]==0)|(p[:,[0,2]]==768),axis=1)])),'old_topology':oldtop,'candidate_topology':newtop,'max_x_displacement':float(np.max(np.abs(newp[:,0]-p[:,0]))),'construction':'Original XZ and index topology held exactly; native height profile translated laterally by Y-only reshaping with a low dry shoulder','max_height_lowering':float(np.min(newp[:,1]-p[:,1])),'geometry_collision_corner_max_abs_error_before':float(np.max(np.abs(collider-p[indices]))),'geometry_collision_corner_max_abs_error_after':float(np.max(np.abs(newcol-newp[indices]))),'root_minheight_gate_passed':not root_minheight_failures,'root_minheight_failures':root_minheight_failures,'scatter_count':len(scatter),'scatter_xz_relocated':sum(s['xz_relocated'] for s in scatter),'scatter_max_horizontal_move':max(s['xz_distance'] for s in scatter),'authorization_scope':'Only an independent source and static replacement data. No saved world/default/prefab edits.'}
for field in [0,1,2,3,12]:
 typ=np.int32 if field==12 else np.float32;old=np.array(A[field],typ);new=np.array(B[field],typ)
 if field in [0,1,3]:assert old[np.unique(faces[~changed_tri])].tobytes()==new[np.unique(faces[~changed_tri])].tobytes()
 if field==2:assert old.reshape(-1,4)[np.unique(faces[~changed_tri])].tobytes()==new.reshape(-1,4)[np.unique(faces[~changed_tri])].tobytes()
 if field in [3,12]:assert old.tobytes()==new.tobytes()
assert np.array_equal(collider.reshape(-1,3,3)[~changed_tri],newcol.reshape(-1,3,3)[~changed_tri])
(D/'section-controls.json').write_text(json.dumps(section_controls,indent=2))
(D/'candidate-native.json').write_text(json.dumps({'source_sha256':source['source_sha256'],'origin':origin.tolist(),'surface_arrays':B,'collider_faces':newcol.tolist(),'source_vertex_to_candidate_vertex':'identity 0..'+str(len(p)-1),'source_triangle_to_candidate_triangle':'identity 0..'+str(len(faces)-1),'moved_vertex_indices':np.flatnonzero(moved).tolist(),'changed_triangle_indices':np.flatnonzero(changed_tri).tolist(),'protected_face_indices':np.flatnonzero(protected_faces).tolist(),'changed_attribute_indices':active_indices.tolist()},separators=(',',':')))
(D/'scatter-replacements.json').write_text(json.dumps(scatter,indent=2));(D/'static-design-checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
