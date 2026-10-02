"""Independently check translation certificates and all overlap-nerve changes.

No authored parameter changes, native apps, images, or mesh search. Intersection
radii are computed only for the original J and the one fixed J2 candidate.
"""
from collections import Counter
import hashlib
from itertools import combinations
import json
import os
from pathlib import Path
import sys
import time
import numpy as np
from scipy.optimize import linprog
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));import poly58j2 as poly
from check_preparation58j2 import c,protect
J=P.parent/'revision-j'

def certificate(config,repair,solution):
 ids=solution['fixed_regions'];moving=solution['moving_region'];r=repair['radius_selected_before_solution_m']
 by_id={v['id']:v for v in config['controls']};origin=np.asarray(solution['reference_origin_UVY'])
 rows=[];supports=[]
 for id in [*ids,moving]:
  for p in poly.planes_for(by_id[id]):
   rows.append([*p[:3],*(-p[:3] if id==moving else np.zeros(3))]);supports.append(p[3]-r-p[:3]@origin)
 A=np.asarray(rows);b=np.asarray(supports);q=solution['global_optimality_certificate']
 poly.require(np.array_equal(A,np.asarray(q['inequality_matrix'])) and np.array_equal(b,np.asarray(q['inequality_supports'])),'Certificate source linear constraints differ')
 z=np.asarray(q['solution_relative']);lam=np.asarray(q['full_nonnegative_multipliers']);delta=z[3:]
 poly.require(np.array_equal(delta,np.asarray(solution['translation_UVY_m'])),'Stored translation differs from certificate')
 slack=b-A@z;stationarity=np.r_[np.zeros(3),delta]+A.T@lam
 poly.require(np.min(slack)>=-1e-8,'KKT primal feasibility')
 poly.require(np.min(lam)>=0,'KKT dual feasibility')
 poly.require(np.max(np.abs(stationarity))<1e-8,'KKT stationarity')
 poly.require(np.max(np.abs(slack*lam))<1e-8,'KKT complementarity')
 primal=.5*float(delta@delta);dual=-.5*float(delta@delta)-float(lam@b)
 poly.require(abs(primal-dual)<1e-7,'KKT global duality gap')
 norm=float(np.linalg.norm(delta));direction=delta/norm
 R=np.c_[A[:,:3],A[:,3:]@direction]
 result=linprog([0.,0.,0.,1.],A_ub=R,b_ub=b,bounds=[(None,None)]*3+[(0,None)],method='highs')
 poly.require(result.success and abs(result.x[3]-norm)<1e-7,'Independent minimum directed LP')
 return dict(moving_region=moving,passed=True,minimum_norm_m=norm,minimum_primal_slack_m=float(slack.min()),
  maximum_stationarity_residual=float(np.abs(stationarity).max()),maximum_complementarity_residual=float(np.abs(slack*lam).max()),
  primal_objective=primal,dual_lower_bound=dual,duality_gap=primal-dual,directed_LP_minimum_m=float(result.x[3]))

def overlaps(config):
 names=[x['id'] for x in config['controls']];planes=[poly.planes_for(x) for x in config['controls']]
 rows={};tol=config['tolerances']['classification_m']
 # Every pair/triple measured. Larger sets need only be measured if all facets
 # have positive common volume; omission then follows by subset containment.
 for count in range(2,9):
  for ids in combinations(range(8),count):
   if count>3 and not all(rows.get(x,{}).get('positive_volume_overlap',False) for x in combinations(ids,count-1)):continue
   p=np.vstack([planes[k] for k in ids]);A=np.c_[p[:,:3],np.ones(len(p))]
   result=linprog([0.,0.,0.,-1.],A_ub=A,b_ub=p[:,3],bounds=[(None,None)]*4,method='highs')
   poly.require(result.success,'Common-radius LP failed')
   radius=float(result.x[3]);rows[ids]=dict(regions=[names[k] for k in ids],maximum_common_inscribed_radius_m=radius,
    center_UVY=result.x[:3].tolist(),positive_volume_overlap=bool(radius>tol))
 positive={ids:row for ids,row in rows.items() if row['positive_volume_overlap']}
 missing=[row for ids,row in rows.items() if len(ids)==3 and not row['positive_volume_overlap'] and all(rows[t]['positive_volume_overlap'] for t in combinations(ids,2))]
 return rows,positive,missing

def main():
 start=time.monotonic();os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2]);protected=protect()
 path=P/'repair-audit58j2.json';poly.require(not path.exists(),'Never overwrite audit evidence')
 old=json.loads((J/'design58j.json').read_text());new=json.loads((P/'design58j2.json').read_text());repair=json.loads((P/'translation-derivation58j2.json').read_text())
 poly.require(c.sha(J/'design58j.json')==repair['parent_design_sha256'],'Frozen parent design SHA mismatch')
 poly.require(c.sha(J/'poly58j.py')==c.sha(P/'poly58j2.py'),'Topology/union/intersection implementation changed')
 poly.require(old['tolerances']==new['tolerances'],'Original tolerances/budgets changed')
 solutions={x['moving_region']:x for x in repair['solutions']};changes=[]
 for a,b in zip(old['controls'],new['controls']):
  poly.require(a['id']==b['id'],'Changed control order or identity')
  for k in set(a)|set(b):
   if a.get(k)!=b.get(k):changes.append(a['id']+'.'+k)
  if a['id'] in solutions:
   delta=np.asarray(solutions[a['id']]['translation_UVY_m']);poly.require(np.array_equal(np.asarray(a['center'])+delta,np.asarray(b['center'])),'Center differs from minimum translation')
  po,pn=poly.planes_for(a),poly.planes_for(b)
  poly.require(np.array_equal(po[:,:3],pn[:,:3]),'Metric normals changed')
  poly.require(np.allclose(pn[:,3]-po[:,3],po[:,:3]@(np.asarray(b['center'])-a['center']),rtol=0,atol=2e-13),'Plane transform is not translation only')
 poly.require(sorted(changes)==['Back_Diagonal_Ledge.center','Left_Short_Accent.center'],'Changes exceed two authorized centers')
 checks=[certificate(old,repair,s) for s in solutions.values()]
 before,positive_before,missing_before=overlaps(old);after,positive_after,missing_after=overlaps(new)
 new_ids=sorted(set(positive_after)-set(positive_before));lost_ids=sorted(set(positive_before)-set(positive_after))
 for solution in solutions.values():
  regions=set([*solution['fixed_regions'],solution['moving_region']]);r=next(v for v in after.values() if set(v['regions'])==regions)
  poly.require(r['maximum_common_inscribed_radius_m']>=repair['radius_selected_before_solution_m']-1e-9,'Target triple overlap radius not met')
 poly.require(not missing_after,'Unfilled triple clique remains')
 poly.require(not lost_ids,'A previous positive-volume overlap was lost')
 poly.require(all(c.sha(c.ROOT/k)==v['sha256'] for k,v in protected.items()),'Protected old evidence changed')
 report=dict(candidate='58J2',passed=True,one_fixed_candidate_only=True,changed_control_fields=changes,
  local_planes_metric_normals_scales_yaws_unchanged=True,topology_union_intersection_code_byte_identical=True,tolerances_and_budgets_unchanged=True,
  certificates=checks,all_pair_triple_LPs_evaluated=True,higher_intersections_pruned_only_by_impossible_subsets=True,
  positive_nerve_simplex_counts_before=dict(Counter(len(k) for k in positive_before)),positive_nerve_simplex_counts_after=dict(Counter(len(k) for k in positive_after)),
  new_positive_overlaps=[after[k] for k in new_ids],lost_positive_overlaps=[before[k] for k in lost_ids],
  empty_triples_with_all_pairwise_overlaps_before=missing_before,empty_triples_with_all_pairwise_overlaps_after=missing_after,
  pairwise_radius_changes=[dict(regions=after[k]['regions'],before_m=before[k]['maximum_common_inscribed_radius_m'],after_m=after[k]['maximum_common_inscribed_radius_m']) for k in after if len(k)==2],
  overlap_LP_results_before=list(before.values()),overlap_LP_results_after=list(after.values()),
  protected_file_count=len(protected),protected_unchanged=True,native_started=False,visual_acceptance=False,elapsed_seconds=time.monotonic()-start)
 c.write(path,report)
 print(json.dumps({k:v for k,v in report.items() if not k.startswith('overlap_LP_results') and k!='pairwise_radius_changes'},indent=2))
if __name__=='__main__':main()
