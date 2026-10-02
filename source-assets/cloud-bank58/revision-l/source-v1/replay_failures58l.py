"""Read actual retained finite candidates; preserve why each preparation refused.
Original logs are immutable. This replay distinguishes conservative rejection
from a proven volume violation; later gates never rewrite the original result.
"""
import sys,os
os.environ['OPENBLAS_NUM_THREADS']='1';sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry58l as g
import numpy as np
from collections import Counter

def coarse_first(c):
    _,T,B=g.solid_arrays(c);tri=np.array(c['planar_triangles']);rim=T[:c['rim_count']][:,[0,2]];a=rim;d=np.roll(rim,-1,axis=0)-rim;thick=T[:,1]-B[:,1]
    for i,t in enumerate(tri):
        q=T[t][:,[0,2]];u=np.clip(np.sum((q[:,None]-a)*d,axis=2)/np.sum(d*d,axis=1),0,1);upper=float(np.linalg.norm(q[:,None]-a-u[:,:,None]*d,axis=2).max(0).min())
        valid=B[t,1].min()>=560 and B[t,1].max()<=630 and thick[t].min()>=120
        if not valid and upper>=80:return dict(triangle=i,whole_triangle_external_distance_upper_m=upper,bottom_y=B[t,1].tolist(),thickness=thick[t].tolist(),is_proven_actual_interior_violation=False)
    return None

def report():
    rows=[]
    for i in (1,2,3):
        p=g.HERE/f'candidate-attempt{i:02}.json';c=g.read(p);edges=Counter(tuple(sorted((a,b))) for f in c['faces'] for a,b in zip(f,f[1:]+f[:1]));bad=[dict(edge=list(k),incidence=v) for k,v in edges.items() if v!=2]
        c['external_rim_authority_float64_xz']=g.read(g.BINDING_PATH)['external_rim_authority_float64_xz']
        try:g.spatial_gate(c);current=dict(passed=True)
        except ValueError as exc:current=dict(passed=False,rejection=str(exc))
        rows.append(dict(candidate=p.name,sha256=g.sha(p),bytes=p.stat().st_size,coarse_original_classification=coarse_first(c),nonmanifold_edges=bad,current_stricter_actual_subdomain_replay=current))
    result=dict(native_run=False,original_logs_preserved=True,attempts=rows,changes=[
      {'after_attempt':1,'actual_edit':'New baseline return smoothstep width80m ->45m. Seven control taper remains exactly80m. No core threshold changed.','reason':'Whole-triangle conservative check could not certify some edge-straddling triangles; not automatically a proven interior violation.'},
      {'after_attempt':2,'actual_edit':'Replace whole-triangle exemption test by clipping each affine B<560/B>630/thickness<120 subdomain, then bound complete convex subdomain distance to a single true rim segment. Also preserve already-defined lower profile when adding coincident named top node.','reason':'Evaluate the same core contract on the actual violating subset; preserve shared A_belly570 rather than overwriting it with absent optional bottom.'},
      {'after_attempt':3,'actual_edit':'Split every internal triangulation edge whose two endpoints are rim vertices with one actual interior vertex before lifting paired sheets.','reason':'A zero-thickness internal rim-rim chord made four incident faces. Added interior vertices create separate positive-thickness upper/lower edges; all old candidates retained.'}],current_candidate_sha256=g.sha(g.CANDIDATE_PATH),current_geometry=g.validate_candidate())
    return result
if __name__=='__main__':g.write(g.HERE/'failure-replay.json',report())
