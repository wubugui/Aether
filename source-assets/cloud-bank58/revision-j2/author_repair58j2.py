"""One minimum-norm, linear-constraint local repair of frozen 58J.

This is not a shape search. Each of two explicitly selected cages moves once;
all local planes, scales/yaws, tolerances and view inputs are inherited exactly.
The positive common inscribed-ball radius is fixed at 0.5 m before solving.
SLSQP identifies the active linear constraints of a convex quadratic program;
a direct KKT linear solve supplies the stored solution and global certificate.
A separate ray LP independently certifies the minimum directed movement.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import numpy as np
from scipy.optimize import minimize, linprog
P=Path(__file__).resolve().parent;J=P.parent/'revision-j'
sys.path.insert(0,str(J));import poly58j as poly
RADIUS_M=0.5
MAX_TRANSLATION_M=40.0
TASKS=[(['Main_Crown','Rear_Crown'],'Back_Diagonal_Ledge'),
       (['Main_Crown','Front_Short_Fold'],'Left_Short_Accent')]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)

def solve_translation(config,fixed_ids,moving_id,initial):
 controls={r['id']:r for r in config['controls']}
 labels=[];constraints=[];supports=[]
 for id in [*fixed_ids,moving_id]:
  for k,p in enumerate(poly.planes_for(controls[id])):
   labels.append(dict(region=id,plane=k))
   # z = [witness relative to initial, translation]. All normals unit length.
   constraints.append([*p[:3],*(-p[:3] if id==moving_id else np.zeros(3))])
   supports.append(float(p[3]-RADIUS_M-p[:3]@initial))
 A=np.asarray(constraints);b=np.asarray(supports)
 H=np.diag([0.,0.,0.,1.,1.,1.])
 seed=linprog(np.zeros(6),A_ub=A,b_ub=b,bounds=[(None,None)]*6,method='highs')
 require(seed.success,'Linear constraints have no feasible seed')
 result=minimize(lambda z: .5*float(z@H@z),seed.x,jac=lambda z:H@z,
                 constraints=[dict(type='ineq',fun=lambda z:b-A@z,jac=lambda z:-A)],
                 method='SLSQP',options=dict(ftol=1e-12,maxiter=200))
 require(result.success,'QP active-set identification failed: '+result.message)
 active=np.flatnonzero(np.abs(A@result.x-b)<1e-7)
 C=A[active];K=np.block([[H,C.T],[C,np.zeros((len(active),len(active)))]])
 rhs=np.r_[np.zeros(6),b[active]]
 certified=np.linalg.lstsq(K,rhs,rcond=None)[0];z=certified[:6];dual=certified[6:]
 slack=b-A@z;stationarity=H@z+C.T@dual
 require(float(slack.min())>=-1e-8,'KKT primal feasibility')
 require(float(dual.min())>=-1e-8,'KKT dual feasibility')
 require(float(np.abs(stationarity).max())<1e-8,'KKT stationarity')
 require(float(np.abs(C@z-b[active]).max())<1e-8,'KKT active constraints')
 delta=z[3:];distance=float(np.linalg.norm(delta));direction=delta/distance
 require(0<distance<MAX_TRANSLATION_M,'Outside predeclared local translation cap')
 # Independent directed LP: z_ray=[witness-relative-to-initial,t], minimize t.
 Ar=np.c_[A[:,:3],A[:,3:]@direction]
 ray=linprog([0.,0.,0.,1.],A_ub=Ar,b_ub=b,bounds=[(None,None)]*3+[(0,None)],method='highs')
 require(ray.success,'Directed LP failed')
 require(abs(float(ray.x[3])-distance)<1e-7,'Minimum directed distance differs from convex QP')
 full_dual=np.zeros(len(b));full_dual[active]=dual
 primal=.5*distance*distance
 dual_bound=-.5*distance*distance-float(full_dual@b)
 require(abs(primal-dual_bound)<1e-7,'Global minimum duality gap')
 return dict(fixed_regions=fixed_ids,moving_region=moving_id,target_common_ball_radius_m=RADIUS_M,
  translation_UVY_m=delta.tolist(),translation_length_m=distance,direction_UVY=direction.tolist(),
  old_center_UVY=controls[moving_id]['center'],new_center_UVY=(np.asarray(controls[moving_id]['center'])+delta).tolist(),
  witness_UVY=(initial+z[:3]).tolist(),reference_origin_UVY=initial.tolist(),
  mathematical_program='minimize 0.5*||delta||^2, subject to N_i*x + radius <= d_i for fixed cages; N_j*(x-delta) + radius <= d_j for moving cage',
  global_optimality_certificate=dict(convex_objective=True,linear_constraints=True,active_planes=[dict(**labels[i],multiplier=float(q)) for i,q in zip(active,dual)],
   minimum_primal_slack_m=float(slack.min()),maximum_stationarity_residual=float(np.abs(stationarity).max()),
   maximum_active_residual_m=float(np.abs(C@z-b[active]).max()),primal_objective=primal,dual_lower_bound=dual_bound,
   duality_gap=primal-dual_bound,minimum_active_multiplier=float(dual.min()),
   inequality_matrix=A.tolist(),inequality_supports=b.tolist(),solution_relative=z.tolist(),full_nonnegative_multipliers=full_dual.tolist()),
  directed_linear_program=dict(minimum_translation_m=float(ray.x[3]),primal_slack_m=float((b-Ar@ray.x).min()),solver_message=ray.message),
  solver_metadata=dict(active_set_method='SLSQP convex quadratic objective with analytic derivatives',iterations=int(result.nit),
   final_solution_method='Direct linear KKT least-squares solve, certified against every constraint',geometry_parameter_search=False))

def main():
 os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:2])
 for name in ('design58j2.json','translation-derivation58j2.json'):
  require(not (P/name).exists(),'Never overwrite derived candidate or proof')
 freeze=json.loads((J/'failed-candidate-freeze58j.json').read_text())
 root=P.parents[2]
 for key,row in {**freeze['files'],**freeze['protected_files']}.items():
  require(sha(root/key)==row['sha256'],'Frozen J or historical file changed: '+key)
 original=json.loads((J/'design58j.json').read_text());config=copy.deepcopy(original)
 diagnostics=json.loads((J/'failure-diagnostics58j.json').read_text())
 solutions=[]
 for fixed,moving in TASKS:
  diagnostic=next(x for x in diagnostics['empty_triples_with_all_pair_overlaps'] if set(x['regions'])==set([*fixed,moving]))
  solutions.append(solve_translation(original,fixed,moving,np.asarray(diagnostic['center_UVY'],float)))
 by_id={r['id']:r for r in config['controls']}
 for solution in solutions:by_id[solution['moving_region']]['center']=solution['new_center_UVY']
 config['candidate']='58J2';config['status']='One mathematically derived two-translation source-only candidate; native and visual acceptance unverified'
 config['local_repair_contract']=dict(parent_design_sha256=sha(J/'design58j.json'),common_ball_radius_m=RADIUS_M,
  only_changed_control_fields=['Back_Diagonal_Ledge.center','Left_Short_Accent.center'],candidate_count=1,
  all_planes_scales_yaws_unchanged=True,tolerances_unchanged=True,fixed_E_views_unchanged=True)
 report=dict(candidate='58J2',parent_design_sha256=sha(J/'design58j.json'),radius_selected_before_solution_m=RADIUS_M,
  maximum_local_translation_cap_m=MAX_TRANSLATION_M,solutions=solutions,candidate_count=1,
  parent_evidence_unchanged=True,native_started=False,visual_acceptance=False)
 for name,data in [('design58j2.json',config),('translation-derivation58j2.json',report)]:
  (P/name).write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps(dict(candidate='58J2',solutions=[{k:r[k] for k in ('moving_region','translation_UVY_m','translation_length_m','witness_UVY')} for r in solutions],design_sha256=sha(P/'design58j2.json'),native_started=False),indent=2))
if __name__=='__main__':main()
