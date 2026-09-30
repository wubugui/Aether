from pathlib import Path
import math,json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1]
def shader_interval(o,d,rebase=False):
 o=o.astype(np.float32);d=d.astype(np.float32)
 inv=1/(d+np.float32(.000001));a=(np.array([-51.2,-51.2,-560],np.float32)-o)*inv;b=(np.array([51.2,51.2,0],np.float32)-o)*inv
 near=np.minimum(a,b);far=np.maximum(a,b);en=max(near[0],near[1],near[2],0);ex=min(far)
 origin_distance=0.
 if rebase:
  origin_distance=en;o=o+d*np.float32(en);ex=ex-en;en=0.
 rc=np.float32(.8)-np.float32(.09)*o[2];qa=np.dot(d[:2],d[:2])-np.float32(.09*.09)*d[2]*d[2];qb=np.float32(2)*(np.dot(o[:2],d[:2])+rc*np.float32(.09)*d[2]);qc=np.dot(o[:2],o[:2])-rc*rc
 if abs(qa)<1e-7:
  if abs(qb)>1e-7:
   t=-qc/qb
   if qb>0:ex=min(ex,t)
   else:en=max(en,t)
  elif qc>0:ex=en
 else:
  disc=qb*qb-np.float32(4)*qa*qc
  if disc<0:
   if qa>0:ex=en
  else:
   h=np.sqrt(max(disc,0));t0,t1=sorted([(-qb-h)/(2*qa),(-qb+h)/(2*qa)])
   if qa>0:en=max(en,t0);ex=min(ex,t1)
   elif en<t0:ex=min(ex,t0)
   else:en=max(en,t1)
 return float(en+origin_distance),float(ex+origin_distance)
def reference_interval(o,d):
 # Independent double precision convex solid slab/polynomial subdivision.
 ts=[0.]
 if abs(d[2])>1e-14:ts +=[(z-o[2])/d[2] for z in [-560.,0.]]
 qa=np.dot(d[:2],d[:2])-.09**2*d[2]**2;rc=.8-.09*o[2];qb=2*(np.dot(o[:2],d[:2])+rc*.09*d[2]);qc=np.dot(o[:2],o[:2])-rc**2
 if abs(qa)>1e-14:
  disc=qb*qb-4*qa*qc
  if disc>=0:ts +=[(-qb-math.sqrt(disc))/(2*qa),(-qb+math.sqrt(disc))/(2*qa)]
 elif abs(qb)>1e-14:ts +=[-qc/qb]
 ts=sorted(set(t for t in ts if t>=0))
 hits=[]
 for a,b in zip(ts,ts[1:]):
  p=o+d*(a+b)*.5
  if -560<=p[2]<=0 and np.dot(p[:2],p[:2])<=(.8-.09*p[2])**2+1e-9:hits.append((a,b))
 return (hits[0][0],hits[-1][1]) if hits else (0.,0.)
rng=np.random.default_rng(2806);cases=[]
for i in range(12000):
 o=rng.uniform([-1300,-1300,-1700],[1300,1300,900]);s=rng.uniform(0,560);r=(.8+.09*s)*rng.uniform(0,1);theta=rng.uniform(0,2*math.pi);p=np.array([r*math.cos(theta),r*math.sin(theta),-s]);d=p-o;d/=np.linalg.norm(d);cases.append((o,d))
for o in [[0,0,-200],[0,0,20],[70,0,-200],[0,0,-900],[.8,0,0]]:
 for d in [[0,0,-1],[0,0,1],[1,0,0],[0,1,0],[.09,0,-1],[-.09,0,1]]:
  d=np.array(d,dtype=float);d/=np.linalg.norm(d);cases.append((np.array(o,dtype=float),d))
errors=[];max_error=0.;changed_membership=0
for i,(o,d) in enumerate(cases):
 a,b=shader_interval(o,d);c,e=reference_interval(o,d);la=max(b-a,0);lb=max(e-c,0);err=abs(la-lb);max_error=max(max_error,err)
 if (la>1e-3)!=(lb>1e-3):changed_membership+=1
 if err>.05:errors.append({'case':i,'origin':o.tolist(),'ray':d.tolist(),'shader':[a,b],'reference':[c,e],'length_error_m':err})
data={'scope':'Independent CPU float32 emulation of28f interval versus double precision subdivided finite convex cone. No GPU rendering; excludes scene depth and shadow map.','cases':len(cases),'max_length_error_m':max_error,'membership_mismatch_gt1mm':changed_membership,'errors_gt5cm':len(errors),'largest_errors':sorted(errors,key=lambda x:-x['length_error_m'])[:10],'shader_sha256':hashlib.sha256((R/'captures/lantern_volume_28f.gdshader').read_bytes()).hexdigest()}
(R/'reviews/round-28f-independent-interval-check.json').write_text(json.dumps(data,indent=2),encoding='utf-8');print(json.dumps(data,indent=2))
errors_new=[];mismatch_new=0;maximum_new=0.
for i,(o,d) in enumerate(cases):
 a,b=shader_interval(o,d,True);c,e=reference_interval(o,d);la=max(b-a,0);lb=max(e-c,0);err=abs(la-lb);maximum_new=max(maximum_new,err)
 if (la>1e-3)!=(lb>1e-3):mismatch_new+=1
 if err>.05:errors_new.append({'case':i,'length_error_m':err,'shader':[a,b],'reference':[c,e]})
data['rebased']={'max_length_error_m':maximum_new,'membership_mismatch_gt1mm':mismatch_new,'errors_gt5cm':len(errors_new),'largest_errors':sorted(errors_new,key=lambda x:-x['length_error_m'])[:10]}
data['shader_sha256']='316fbb2b1fcb39ed21d83b0ee9c72bd693b15f92b1f2e032d52bbf85777fd04f'
data['rebased']['shader_sha256']=hashlib.sha256((R/'captures/lantern_volume_28f.gdshader').read_bytes()).hexdigest()
data['scope']+=' Unrebased baseline and rebased variant are distinguished by separate shader hashes. CPU float32 arithmetic is not a bit-identical GPU/compiler emulator.'
(R/'reviews/round-28f-independent-interval-check.json').write_text(json.dumps(data,indent=2),encoding='utf-8');print(json.dumps(data['rebased'],indent=2))
