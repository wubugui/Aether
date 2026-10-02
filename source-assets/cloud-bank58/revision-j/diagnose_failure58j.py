"""Read-only diagnostics of the rejected fixed candidate. Never waives a gate."""
from collections import Counter,defaultdict
from itertools import combinations
import hashlib,json,os,sys,time,traceback
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P))
import poly58j as poly
from probe_candidate58j import metric_areas
from check_preparation58j import c,E_REPORT,visibility_proof

def main():
 start=time.monotonic();os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2]);config=json.loads((P/'design58j.json').read_text());tol=config['tolerances']
 audit=dict(consecutive_equal_arithmetic_stations=0,zero_dimensional_clip_outputs=0,zero_area_clip_outputs=0,nonunique_parallel_plane_triples=0,maximum_weld_displacement_m=0.,shared_edge_stations_inserted=0)
 cages=[poly.cage(row,tol,audit) for row in config['controls']];surface=poly.exposed_polygons(cages,tol,audit);V,F,owners,panels=poly.weld_conform(surface,tol,audit)
 edges=set(tuple(sorted((int(a),int(b)))) for face in F for a,b in zip(face,np.roll(face,-1)))
 mesh=dict(vertices=V,faces=F,owners=owners,panels=panels)
 report=dict(candidate='58J',status='Read-only diagnostics of rejected candidate; topology failure remains authoritative',valid_candidate=False,visual_acceptance=False,native_started=False,design_sha256=c.sha(P/'design58j.json'),vertices=len(V),triangles=len(F),edges=len(edges),euler=len(V)-len(edges)+len(F),exposed_polygon_count=len(surface),metric_union_slopes=metric_areas(mesh),arithmetic_audit=audit)
 tri=V[F];areas=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)*.5
 region=defaultdict(float)
 for owner,area in zip(owners,areas):region[owner]+=float(area)
 report['exposed_area_m2_by_region']=dict(region)
 names=[r['id'] for r in config['controls']]
 simplex={}
 def intersection(ids):
  planes=np.vstack([cages[k]['planes'] for k in ids]);A=np.c_[planes[:,:3],np.ones(len(planes))]
  result=linprog([0.,0.,0.,-1.],A_ub=A,b_ub=planes[:,3],bounds=[(None,None)]*4,method='highs')
  poly.require(result.success,'Chebyshev diagnostic solver failed')
  return dict(regions=[names[k] for k in ids],maximum_common_inscribed_radius_m=float(result.x[3]),center_UVY=result.x[:3].tolist(),positive_volume_overlap=bool(result.x[3]>tol['classification_m']))
 for n in (2,3,4):
  for ids in combinations(range(8),n):
   if n>2 and not all(simplex.get(tuple(x),{}).get('positive_volume_overlap',False) for x in combinations(ids,n-1)):continue
   simplex[ids]=intersection(ids)
 report['pairwise_intersections']=[v for k,v in simplex.items() if len(k)==2]
 report['empty_triples_with_all_pair_overlaps']=[v for k,v in simplex.items() if len(k)==3 and not v['positive_volume_overlap']]
 report['higher_common_overlaps']=[v for k,v in simplex.items() if len(k)>=3 and v['positive_volume_overlap']]
 frame=json.loads(c.PLAN.read_text());source=(V@poly.source_basis(frame).T).astype(np.float32).astype(float)
 reference=next(r for r in json.loads(E_REPORT.read_text())['layouts'] if r['layout']=='B_staggered_crowns');report['camera_diagnostics_only']=[]
 for camera in reference['cameras']:
  view=np.c_[source,np.ones(len(V))]@np.linalg.inv(camera['matrix_world']).T;clip=view@np.array(camera['projection']).T;xy=(clip[:,:2]/clip[:,3,None]+1)/2
  margin=float(min(xy.min(),1-xy.max()));report['camera_diagnostics_only'].append(dict(name=camera['name'],minimum_margin=margin,seven_percent_gate_passed=margin>=.07,geometric_visibility=visibility_proof(source,F,owners,panels,camera,xy)))
 report['elapsed_seconds']=time.monotonic()-start
 out=P/'failure-diagnostics58j.json';poly.require(not out.exists(),'Do not overwrite failure diagnostics');c.write(out,report)
 print(json.dumps(c.native(report),indent=2))
if __name__=='__main__':main()
