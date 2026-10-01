"""Bounded native-heightfield edit. No engine/world generation or scene writes."""
from pathlib import Path
import json, numpy as np,hashlib,collections
D=Path(__file__).resolve().parent
source=json.loads((D/'native-authority/authority.json').read_text());A=source['surfaces'][0]['arrays']
p=np.array(A[0],np.float32);indices=np.array(A[12],np.int32);faces=indices.reshape(-1,3);origin=np.array(source['origin'],np.float64);world=p.astype(np.float64)+origin
bounds=np.array([-3010,-2660,-3040,-2760],float)
inside=(world[:,0]>bounds[0])&(world[:,0]<bounds[1])&(world[:,2]>bounds[2])&(world[:,2]<bounds[3])
protected_faces=~inside[faces].all(axis=1)
_,groups=np.unique(p,axis=0,return_inverse=True);frozen_groups=np.unique(groups[faces[protected_faces].ravel()]);unlocked=inside&~np.isin(groups,frozen_groups)
def bump(z,center,width):
 t=(z-center)/width;return np.where(abs(t)<1,(1-t*t)**2,0)
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
x,y,z=world.T;shore=.641329667*z-964.807821;d=x-shore
cape=bump(z,-2965,75);bay=bump(z,-2855,65)
weight=1-smooth(35,145,np.abs(d));delta_x=(-50*cape+25*bay)*weight*unlocked
strength=np.clip(cape+.65*bay,0,1)*(1-smooth(80,150,d))*unlocked
height_goal=np.minimum(y,2+.2*np.maximum(d,0));delta_y=np.where(y>0,(height_goal-y)*strength,0)
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
newp=p.copy();memo={}
for i in np.flatnonzero(unlocked & ((abs(delta_x)>1e-6)|(strength>1e-6))):
 key=int(groups[i])
 if key not in memo:
  shifted=original_height(x[i]-delta_x[i],z[i]) if abs(delta_x[i])>1e-6 else float(y[i])
  coast_distance=d[i]-delta_x[i]
  low_goal=min(shifted,2+.2*max(coast_distance,0))
  lowered=shifted+(low_goal-shifted)*strength[i] if shifted>0 else shifted
  memo[key]=np.float32(lowered)
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
scope=json.loads((D.parent.parent/'cloud-evidence/coast-boundary-readonly-20261001/scope.json').read_text());scatter=[]
for group in scope['scatter']:
 for entry in group['instances_in_box']:
  m=__import__('re').search(r'_(-?\d+)_(-?\d+)(?:_|$)',group['node']);grouporigin=np.array([int(m[1])*768,0,int(m[2])*768],np.float32)
  buf=np.array(entry['transform_buffer'],np.float32);pos=(buf[[3,7,11]]+grouporigin).astype(np.float32).astype(float);kind=group['kind'];before=sample(p,pos[0],pos[2]);after=sample(newp,pos[0],pos[2]);newpos=pos.copy();moved_xz=False
  minh={'pine':3,'bush':1.5,'rock':.5}[kind]
  if after is None or after['height']<minh:
   choices=[]
   for dx in np.arange(0,41,2):
    for dz in np.arange(-20,21,4):
     if dx*dx+dz*dz>40*40:continue
     xx,zz=pos[0]+dx,pos[2]+dz
     if not bounds[0]<xx<bounds[1] or not bounds[2]<zz<bounds[3]:continue
     hit=sample(newp,xx,zz)
     if hit and hit['height']>=minh and hit['slope_degrees']<42:choices.append((dx*dx+dz*dz,xx,zz,hit))
   assert choices,('no safe bounded relocation',group['node'],entry['index']);_,xx,zz,after=min(choices,key=lambda t:t[0]);newpos[0]=xx;newpos[2]=zz;moved_xz=True
  offset=float(pos[1]-before['height']);newpos[1]=after['height']+offset
  # PackedFloat32 translation is cell-local in the actual source group.
  newbuf=buf.copy();newbuf[7]=np.float32(newpos[1])
  if moved_xz:newbuf[[3,11]]=(newpos-grouporigin)[[0,2]].astype(np.float32)
  actualpos=(newbuf[[3,7,11]]+grouporigin).astype(np.float32).astype(float);actual=sample(newp,actualpos[0],actualpos[2])
  scatter.append({'node':group['node'],'kind':kind,'index':entry['index'],'source_group_origin':grouporigin.tolist(),'before_position':pos.tolist(),'candidate_position':actualpos.tolist(),'before_buffer':buf.tolist(),'candidate_buffer':newbuf.tolist(),'xz_relocated':moved_xz,'xz_distance':float(np.linalg.norm((actualpos-pos)[[0,2]])),'before_support':before,'candidate_support':actual,'preserved_origin_offset':offset,'candidate_origin_offset':float(actualpos[1]-actual['height'])})
report={'source_scene':source['source'],'source_sha256':source['source_sha256'],'source_mesh':source['mesh'],'source_shape':source['shape'],'box_xmin_xmax_zmin_zmax':bounds.tolist(),'origin':origin.tolist(),'design_inference':'One broad low cape and a short bay. Reference-inspired design coordinates; not a claimed exact reference geography. No camera/weather adjustment.', 'positions_moved':int(moved.sum()),'triangles_changed':int(changed_tri.sum()),'normal_tangent_indices_modified':len(active_indices),'protected_faces':int(protected_faces.sum()),'unchanged_faces':int((~changed_tri).sum()),'raw_fields_unchanged_on_all_unchanged_triangles':True,'all_indices_colors_uv_absence_unchanged':True,'tile_boundary_positions_exact':bool(np.array_equal(newp[np.any((p[:,[0,2]]==0)|(p[:,[0,2]]==768),axis=1)],p[np.any((p[:,[0,2]]==0)|(p[:,[0,2]]==768),axis=1)])),'old_topology':oldtop,'candidate_topology':newtop,'max_x_displacement':float(np.max(np.abs(newp[:,0]-p[:,0]))),'construction':'Original XZ and index topology held exactly; native height profile translated laterally by Y-only reshaping with a low dry shoulder','max_height_lowering':float(np.min(newp[:,1]-p[:,1])),'geometry_collision_corner_max_abs_error_before':float(np.max(np.abs(collider-p[indices]))),'geometry_collision_corner_max_abs_error_after':float(np.max(np.abs(newcol-newp[indices]))),'scatter_count':len(scatter),'scatter_xz_relocated':sum(s['xz_relocated'] for s in scatter),'scatter_max_horizontal_move':max(s['xz_distance'] for s in scatter),'authorization_scope':'Only an independent source and static replacement data. No saved world/default/prefab edits.'}
for field in [0,1,2,3,12]:
 typ=np.int32 if field==12 else np.float32;old=np.array(A[field],typ);new=np.array(B[field],typ)
 if field in [0,1,3]:assert old[np.unique(faces[~changed_tri])].tobytes()==new[np.unique(faces[~changed_tri])].tobytes()
 if field==2:assert old.reshape(-1,4)[np.unique(faces[~changed_tri])].tobytes()==new.reshape(-1,4)[np.unique(faces[~changed_tri])].tobytes()
 if field in [3,12]:assert old.tobytes()==new.tobytes()
assert np.array_equal(collider.reshape(-1,3,3)[~changed_tri],newcol.reshape(-1,3,3)[~changed_tri])
(D/'candidate-native.json').write_text(json.dumps({'source_sha256':source['source_sha256'],'origin':origin.tolist(),'surface_arrays':B,'collider_faces':newcol.tolist(),'source_vertex_to_candidate_vertex':'identity 0..9422','source_triangle_to_candidate_triangle':'identity 0..3197','moved_vertex_indices':np.flatnonzero(moved).tolist(),'changed_triangle_indices':np.flatnonzero(changed_tri).tolist(),'protected_face_indices':np.flatnonzero(protected_faces).tolist(),'changed_attribute_indices':active_indices.tolist()},separators=(',',':')))
(D/'scatter-replacements.json').write_text(json.dumps(scatter,indent=2));(D/'static-design-checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
