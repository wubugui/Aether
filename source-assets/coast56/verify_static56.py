"""Read saved Blender readbacks and independent native authority; verify exact scope."""
import json,hashlib,numpy as np
from pathlib import Path
D=Path(__file__).resolve().parent;root=D.parent.parent
orig=json.loads((D/'native-authority/authority.json').read_text());zero=json.loads((D/'zero-change-readback.json').read_text());saved=json.loads((D/'candidate-blend-readback.json').read_text());planned=json.loads((D/'candidate-native.json').read_text());scatter=json.loads((D/'scatter-replacements.json').read_text());design=json.loads((D/'static-design-checks.json').read_text())
A=orig['surfaces'][0]['arrays'];B=saved['arrays'];p=np.asarray(A[0],np.float32);q=np.asarray(B[0],np.float32);idx=np.asarray(A[12],np.int32);face=idx.reshape(-1,3);moved=np.any(p!=q,axis=1);changed=moved[face].any(axis=1);fixed_vertices=np.unique(face[~changed]);checks=[]
def check(name,value,detail=None):
 checks.append({'name':name,'passed':bool(value),'detail':detail})
 if not value:raise AssertionError(name)
def bytesof(a,i):return np.asarray(a,np.int32 if i==12 else np.float32).tobytes()
for i in [0,1,2,3,12]:
 check('Zero-change saved Blender preserves native field '+str(i),bytesof(A[i],i)==bytesof(zero['arrays'][i],i))
 check('Saved candidate Blender matches planned field '+str(i),bytesof(B[i],i)==bytesof(planned['surface_arrays'][i],i))
 for v in [A,B]:
  assert v[4:12]==[None]*8
for i in [0,1,2,3]:
 a=np.asarray(A[i],np.float32);b=np.asarray(B[i],np.float32)
 if i==2:a=a.reshape(-1,4);b=b.reshape(-1,4)
 check('All unchanged triangles preserve native field '+str(i),a[fixed_vertices].tobytes()==b[fixed_vertices].tobytes(),{'unchanged_triangles':int((~changed).sum())})
check('All indices remain bit-exact',bytesof(A[12],12)==bytesof(B[12],12))
check('All native colors remain bit-exact',bytesof(A[3],3)==bytesof(B[3],3))
check('Every XZ coordinate remains bit-exact',p[:,[0,2]].tobytes()==q[:,[0,2]].tobytes())
world=p.astype(float)+np.array(orig['origin']);lo,hi,zlo,zhi=design['box_xmin_xmax_zmin_zmax'];inside=(world[:,0]>lo)&(world[:,0]<hi)&(world[:,2]>zlo)&(world[:,2]<zhi);protected=~inside[face].all(axis=1)
check('Every modified triangle lies wholly within authorized box',not np.any(changed&protected))
check('All 2509 box-crossing or exterior triangles are exactly retained',p[face[protected]].tobytes()==q[face[protected]].tobytes(),int(protected.sum()))
boundary=np.any((p[:,[0,2]]==0)|(p[:,[0,2]]==768),axis=1);check('Four tile boundaries exactly retained',p[boundary].tobytes()==q[boundary].tobytes(),int(boundary.sum()))
check('No triangles or vertices added or removed',q.shape==p.shape and len(B[12])==len(A[12]))
check('Open terrain topology retained without adding a bottom',design['old_topology']['boundary_edges']==design['candidate_topology']['boundary_edges']==138 and design['candidate_topology']['nonmanifold_edges']==0)
c0=np.asarray(orig['collider_faces'],np.float32);c1=np.asarray(planned['collider_faces'],np.float32)
check('Original collision corners of unchanged triangles exact',c0.reshape(-1,3,3)[~changed].tobytes()==c1.reshape(-1,3,3)[~changed].tobytes())
corner_changed=moved[idx];check('Moved native vertex maps directly to all changed collision corners',np.array_equal(c1[corner_changed],q[idx[corner_changed]]))
check('Every other original collision corner exact',c0[~corner_changed].tobytes()==c1[~corner_changed].tobytes())
def collider_topology(points):
 unique,weld=np.unique(points,axis=0,return_inverse=True);f=weld.reshape(-1,3)
 edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True)
 t=points.reshape(-1,3,3);cross=np.cross((t[:,1]-t[:,0]).astype(float),(t[:,2]-t[:,0]).astype(float))
 return {'unique_positions':len(unique),'boundary_edges':int(np.sum(counts==1)),'nonmanifold_edges':int(np.sum(counts>2)),'xz_nonnegative_faces':int(np.sum(cross[:,1]>=0))}
check('Actual replacement collision keeps original open topology and no new folds',collider_topology(c0)==collider_topology(c1),{'original':collider_topology(c0),'candidate':collider_topology(c1)})
check('Collision/native error did not increase',np.max(np.abs(c1-q[idx]))<=np.max(np.abs(c0-p[idx])),{'before':float(np.max(np.abs(c0-p[idx]))),'after':float(np.max(np.abs(c1-q[idx])))})
check('44 roots accounted for',len(scatter)==44)
for r in scatter:
 old=np.asarray(r['before_buffer'],np.float32);new=np.asarray(r['candidate_buffer'],np.float32)
 keep=[0,1,2,3,4,5,6,8,9,10,11]
 check('Scatter root '+r['node']+'['+str(r['index'])+']',old[keep].tobytes()==new[keep].tobytes() and r['candidate_support']['height']>0 and abs(r['candidate_origin_offset']-r['preserved_origin_offset'])<=np.finfo(np.float32).eps*max(1,abs(r['candidate_position'][1])),{'surface':r['candidate_support'],'origin_offset':r['candidate_origin_offset'],'unchanged_XZ_basis':True})
check('Three cross-group pine roots covered',sum('_-4_-5_' in r['node'] for r in scatter)==3)
scene=root/'candidates/round40-exclusive-20260930/project/scenes/candidate53d-west/Game53dWest.tscn';check('Authoritative source world still byte-identical',hashlib.sha256(scene.read_bytes()).hexdigest()==orig['source_sha256'])
# Exact XZ geometry ensures no new projected intersections; retain original winding signs.
oldcross=np.cross((p[face[:,1]]-p[face[:,0]]).astype(float),(p[face[:,2]]-p[face[:,0]]).astype(float));newcross=np.cross((q[face[:,1]]-q[face[:,0]]).astype(float),(q[face[:,2]]-q[face[:,0]]).astype(float));check('Projected geometry and winding unchanged',np.array_equal(oldcross[:,1],newcross[:,1]) and np.all(oldcross[:,1]<0))
# Shore-contour crossing measurements are from actual saved candidate vertices.
def shoreline(pts):
 segments=[]
 for t in pts[face].astype(float)+np.array(orig['origin']):
  hits=[]
  for a,b in zip(t,np.roll(t,-1,axis=0)):
   if (a[1]<=0<b[1]) or (b[1]<=0<a[1]):hits.append(a+(b-a)*(-a[1]/(b[1]-a[1])))
  if len(hits)==2:segments.append(hits)
 return np.array(segments)
a,b=shoreline(p),shoreline(q);profile=[]
for z in [-3000,-2980,-2965,-2950,-2930,-2910,-2880,-2855,-2830,-2810,-2790]:
 row={'z':z}
 for name,segs in [('original',a),('candidate',b)]:
  mask=((segs[:,0,2]<=z)&(segs[:,1,2]>=z))|((segs[:,1,2]<=z)&(segs[:,0,2]>=z));seg=segs[mask];f=(z-seg[:,0,2])/(seg[:,1,2]-seg[:,0,2]);xs=seg[:,0,0]+f*(seg[:,1,0]-seg[:,0,0]);row[name+'_coast_x']=float(xs.min())
 row['change_x']=row['candidate_coast_x']-row['original_coast_x'];profile.append(row)
report={'passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'shore_profiles':profile,'original_source_scene_sha256':orig['source_sha256'],'candidate_blend_sha256':hashlib.sha256((D/'Ground_-4_-4_coast56.blend').read_bytes()).hexdigest(),'candidate_native_sha256':hashlib.sha256((D/'candidate-native.json').read_bytes()).hexdigest(),'limits':'Static source and exact-array checks, root-point terrain support only. No world integration, actual GPU render, full tree/rock footprint, flight or independent visual acceptance.'}
(D/'verified-static56.json').write_text(json.dumps(report,indent=2));print('STATIC56_VERIFIED',report['passed'],report['check_count']);print(json.dumps(profile,indent=2))
