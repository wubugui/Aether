"""Actual finite PL intersections against the unchanged PCHIP targets.
Each cubic residual is checked at interval endpoints and all real derivative
roots. No zero-error equivalence or accepted approximation tolerance is claimed.
"""
import sys,os
os.environ['OPENBLAS_NUM_THREADS']='1';sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry58l as g
import prepare_candidate58l as prep
import numpy as np,json,argparse

def audit(c):
    m,plan,definition,nodes,profiles=prep.load_profiles();v,T,B=g.solid_arrays(c);xz=T[:,[0,2]];tri=np.array(c['planar_triangles']);edges=np.array(list(prep.triangle_edges(tri)));e0=xz[edges[:,0]];ed=xz[edges[:,1]]-e0
    all_rows={};summary=[]
    for name,p in profiles.items():
        rows=[];cuts=list(p['stations'])+list(p['path_s'])
        for j,(sa,sb) in enumerate(zip(p['path_s'],p['path_s'][1:])):
            a=p['path_xz'][j];direction=(p['path_xz'][j+1]-a)/(sb-sa);den=g.cross(direction,ed);good=den!=0
            t=np.zeros(len(edges));u=np.zeros(len(edges));t[good]=g.cross(e0[good]-a,ed[good])/den[good];u[good]=g.cross(e0[good]-a,direction)/den[good]
            cuts.extend((sa+t[(t>0)&(t<sb-sa)&(u>=0)&(u<=1)&good]).tolist())
        cuts=np.unique(np.array(cuts));cuts=cuts[(cuts>=p['stations'][0])&(cuts<=p['stations'][-1])]
        for lo,hi in zip(cuts[:-1],cuts[1:]):
            if hi<=lo:continue
            mid=(lo+hi)/2;q=m.world_xz(p,mid);verts=xz[tri];crosses=np.stack([g.cross(verts[:,(k+1)%3]-verts[:,k],q-verts[:,k]) for k in range(3)],1);which=np.flatnonzero(np.all(crosses>=-1e-8,1));g.require(len(which)>0,'PROFILE_LEFT_ACTUAL_DOMAIN')
            tid=int(which[0]);ids=tri[tid];matrix=np.column_stack((xz[ids],np.ones(3)));q0=m.world_xz(p,lo);q1=m.world_xz(p,hi);direction=(q1-q0)/(hi-lo)
            row=dict(lo_m=float(lo),hi_m=float(hi),triangle=tid)
            for key,heights in [('top',T[:,1]),('bottom',B[:,1])]:
                plane=np.linalg.solve(matrix,heights[ids]);slope=float(plane[:2]@direction);at_lo=float(plane[:2]@q0+plane[2]);k=min(np.searchsorted(p[key].x,mid,side='right')-1,len(p[key].x)-2);co=p[key].c[:,k].copy();base=p[key].x[k]
                # residual target PCHIP - actual PL plane, x measured from knot.
                co[2]-=slope;co[3]-=at_lo+slope*(base-lo)
                roots=np.roots(np.polyder(co));at=[lo,hi]+[float(r.real+base) for r in roots if abs(r.imag)<1e-9 and lo<r.real+base<hi];res=np.polyval(co,np.array(at)-base);ix=int(np.argmax(np.abs(res)))
                row[key]=dict(max_abs_error_m=float(abs(res[ix])),at_m=at[ix],signed_error_m=float(res[ix]),endpoint_errors_m=[float(res[0]),float(res[1])])
            rows.append(row)
        all_rows[name]=rows
        knots=[]
        for t,top,bottom in zip(p['stations'],p['top_values'],p['bottom_values']):
            q=m.world_xz(p,t);i=int(np.argmin(np.linalg.norm(xz-q,axis=1)));knots.append(dict(station_m=float(t),vertex_index=i,xz_rounding_error_m=float(np.linalg.norm(xz[i]-q)),top_error_m=float(T[i,1]-top),bottom_error_m=float(B[i,1]-bottom)))
        summary.append(dict(section=name,interval_count=len(rows),max_top_error_m=max(r['top']['max_abs_error_m'] for r in rows),max_bottom_error_m=max(r['bottom']['max_abs_error_m'] for r in rows),knots=knots,knots_y_preserved_exactly=all(x['top_error_m']==0 and x['bottom_error_m']==0 for x in knots)))
    return dict(candidate_sha256=g.sha(g.CANDIDATE_PATH),profile_definition_sha256=g.sha(g.HERE.parent/'design-v2/profile-definition.json'),method=__doc__,sections=summary,intervals=all_rows,approximation_accepted=False,pointwise_PCHIP_identity=False,native_executed=False,contact_acceptance=False,world_acceptance=False)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args()
    if a.write:
        r=audit(g.read(g.CANDIDATE_PATH));g.write(g.HERE/'profile-approximation.json',r);print(json.dumps({k:v for k,v in r.items() if k!='intervals'},indent=2))
    else:print('No-op default. --write audits already-prepared actual candidate only.')
