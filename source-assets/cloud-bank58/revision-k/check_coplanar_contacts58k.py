"""Supplemental coplanar-contact checker for supplied actual mesh arrays.

Python 3 + NumPy only. The reusable check_coplanar_contacts(V,F,eps=1e-8)
accepts supplied arrays without changing resource limits or reading files. It is
used on predicted arrays by preparation and on actual opened native arrays by the
future fresh-source verify and explicit editable rebuild. No CLI is provided.

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
