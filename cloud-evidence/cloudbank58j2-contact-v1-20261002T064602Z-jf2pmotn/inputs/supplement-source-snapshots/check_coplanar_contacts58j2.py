"""Read-only supplemental coplanar-contact check of fixed 58J2 math arrays.

Python 3 + NumPy only. CLI caps affinity to two available CPUs where supported,
CPU time to 30 seconds and address space to 512 MiB on this Linux environment.
The reusable check_coplanar_contacts(V,F,eps=1e-8) accepts supplied arrays without
changing resource settings or accessing files. It does not assert native source
transforms: CLI tests UVY doubles and source-basis float32 prediction only.
Actual future Blender Empty-transform/readback coordinates remain untested.

Uses precisely the inherited coplanar branch's distance and angular predicates.
An orthonormal 2-D chart preserves planar distances; long-double edge arithmetic
finds vertex containment, edge crossings, collinear overlap ends and <=epsilon
contacts. This supplements zero-area contact coverage for that branch, and does
not replace topology, noncoplanar intersection or native/render verification.
It is a numerical check, not exact-arithmetic proof.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS','2')
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
import hashlib
import json
import platform
import resource
import sys
import time
import types
from pathlib import Path
from collections import Counter
import numpy as np

def cross(a,b):
    return a[0]*b[1]-a[1]*b[0]

def point_segment(p,a,b):
    edge=b-a
    t=np.clip(np.dot(p-a,edge)/np.dot(edge,edge),0,1)
    q=a+t*edge
    return float(np.linalg.norm(p-q)),q

def inside(p,t,eps=1e-8):
    sign=1 if cross(t[1]-t[0],t[2]-t[0])>=0 else -1
    return min(float(sign*cross(t[(k+1)%3]-t[k],p-t[k])/
                     np.linalg.norm(t[(k+1)%3]-t[k])) for k in range(3))>=-eps

def contacts(a,b,eps=1e-8):
    out=[]
    for p in a:
        if inside(p,b,eps):
            out.append(p)
    for p in b:
        if inside(p,a,eps):
            out.append(p)
    min_boundary_distance=float('inf')
    for ia in range(3):
        p=a[ia];r=a[(ia+1)%3]-p
        for ib in range(3):
            q=b[ib];s=b[(ib+1)%3]-q;den=cross(r,s)
            if den!=0:
                t=cross(q-p,s)/den;u=cross(q-p,r)/den
                et=eps/np.linalg.norm(r);eu=eps/np.linalg.norm(s)
                if -et<=t<=1+et and -eu<=u<=1+eu:
                    pa=p+np.clip(t,0,1)*r;pb=q+np.clip(u,0,1)*s
                    # Retain only <=eps Euclidean contacts after clamping.
                    gap=float(np.linalg.norm(pa-pb))
                    min_boundary_distance=min(min_boundary_distance,gap)
                    if gap<=eps:
                        out.extend((pa,pb))
            for v,c,d in [(p,q,q+s),(p+r,q,q+s),(q,p,p+r),(q+s,p,p+r)]:
                gap,nearest=point_segment(v,c,d)
                min_boundary_distance=min(min_boundary_distance,gap)
                if gap<=eps:
                    out.extend((v,nearest))
    return out,min_boundary_distance

def check_coplanar_contacts(V,F,eps=1e-8):
    V=np.asarray(V,float);F=np.asarray(F,int);T=V[F]
    C=np.cross(T[:,1]-T[:,0],T[:,2]-T[:,0])
    N=C/np.linalg.norm(C,axis=1)[:,None]
    low=T.min(axis=1);high=T.max(axis=1)
    count=0;hist=Counter();no_shared_gap=float('inf')
    violations=[];worst_shared=0.;aabb=0
    for i,a in enumerate(T):
        candidates=np.flatnonzero(np.all(high[i]+eps>=low,axis=1)&
                                  np.all(high+eps>=low[i],axis=1))
        for j in candidates:
            if j<=i:
                continue
            aabb+=1;b=T[j];n,m=N[i],N[j]
            ab=b@n-a[0]@n;ba=a@m-b[0]@m
            if np.all(ab>eps) or np.all(ab<-eps) or np.all(ba>eps) or np.all(ba<-eps):
                continue
            if not (np.linalg.norm(np.cross(n,m))<1e-7 and
                    max(np.max(np.abs(ab)),np.max(np.abs(ba)))<=eps):
                continue
            count+=1
            shared=sorted(set(map(int,F[i]))&set(map(int,F[j])))
            hist[len(shared)]+=1
            u=a[1]-a[0];u=u/np.linalg.norm(u);v=np.cross(n,u)
            basis=np.stack((u,v),axis=1)
            aa=np.asarray((a-a[0])@basis,dtype=np.longdouble)
            bb=np.asarray((b-a[0])@basis,dtype=np.longdouble)
            pts,gap=contacts(aa,bb,eps)
            if not shared:
                no_shared_gap=min(no_shared_gap,gap)
                if pts:
                    violations.append({'i':int(i),'j':int(j),'shared':shared,
                                       'contact_count':len(pts),'gap_m':gap})
            elif pts:
                common=np.asarray((V[shared]-a[0])@basis,dtype=np.longdouble)
                for p in pts:
                    distance=(float(np.linalg.norm(p-common[0])) if len(shared)==1
                              else point_segment(p,common[0],common[1])[0])
                    worst_shared=max(worst_shared,distance)
                    if distance>eps:
                        violations.append({'i':int(i),'j':int(j),'shared':shared,
                                           'outside_shared_locus_m':distance})
    return {'aabb_pairs':aabb,'coplanar_pairs':count,
        'coplanar_shared_index_histogram':dict(hist),
        'min_projected_gap_no_shared_m':no_shared_gap if np.isfinite(no_shared_gap) else None,
        'maximum_contact_distance_from_indexed_shared_locus_m':worst_shared,
        'nonindexed_contact_violations':violations,'eps_m':eps}

def main():
    start=time.monotonic()
    cpus=sorted(os.sched_getaffinity(0))[:2]
    os.sched_setaffinity(0,cpus)
    resource.setrlimit(resource.RLIMIT_CPU,(30,30))
    resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
    P=root/'source-assets/cloud-bank58/revision-j2'
    code=P/'poly58j2.py'
    frame=P.parent/'revision-d/control-plan58d.json'
    input_paths=[code,P/'design58j2.json',P/'candidate-probe58j2.json',frame]
    hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in input_paths}
    poly=types.ModuleType('review_poly')
    exec(compile(code.read_bytes(),str(code),'exec'),poly.__dict__)
    config=json.loads((P/'design58j2.json').read_text())
    stored=json.loads((P/'candidate-probe58j2.json').read_text())
    mesh=poly.build(config)
    if mesh['fingerprint']!=stored['fingerprint']:
        raise ValueError('Fixed candidate fingerprint mismatch')
    plan=json.loads(frame.read_text())
    source=mesh['vertices']@poly.source_basis(plan).T
    # Abstract 2-D controls: point contact, segment contact, separation.
    a=np.array([[0,0],[2,0],[0,2]],dtype=np.longdouble)
    if not contacts(a,np.array([[2,0],[3,0],[2,-1]],dtype=np.longdouble))[0]:
        raise ValueError('Point-contact control missed')
    if not contacts(a,np.array([[.5,0],[1.5,0],[1,-1]],dtype=np.longdouble))[0]:
        raise ValueError('Segment-contact control missed')
    if contacts(a,np.array([[3,0],[4,0],[3,1]],dtype=np.longdouble))[0]:
        raise ValueError('Separated control incorrectly reported contact')
    print(json.dumps({'scope':'Fixed J2 math UVY and source-basis float32 arrays only',
        'actual_native_empty_transform_readback_tested':False,
        'dependencies':{'python':platform.python_version(),'numpy':np.__version__},
        'cpu_affinity':cpus,'cpu_time_limit_seconds':30,'address_space_limit_MiB':512,
        'input_sha256':hashes,'abstract_2d_controls_passed':3}))
    for label,V,key in [
        ('double_UVY',mesh['vertices'],'double_precision_intersections'),
        ('source_basis_float32',source.astype(np.float32).astype(float),'float32_intersections')]:
        result=check_coplanar_contacts(V,mesh['faces'],eps=1e-8)
        result={'array':label,**result}
        result['matches_probe_coplanar_count']=(
            result['coplanar_pairs']==stored[key]['coplanar_pairs_tested'])
        print(json.dumps(result))
        if not result['matches_probe_coplanar_count']:
            raise ValueError('Inherited coplanar pair count mismatch')
        if result['nonindexed_contact_violations']:
            raise ValueError('Nonindexed coplanar contact found')
    if hashes!={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in input_paths}:
        raise ValueError('Input files changed during check')
    print(json.dumps({'passed':True,'fixed_candidate_fingerprint':mesh['fingerprint'],
        'input_hashes_unchanged':True,'elapsed_seconds':time.monotonic()-start,
        'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))

if __name__=='__main__':
    main()
