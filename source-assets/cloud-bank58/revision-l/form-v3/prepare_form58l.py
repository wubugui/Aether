"""One paired-point art revision, no engine. Original two patches only."""
import os,sys
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,copy,json,hashlib,traceback
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry58l as g
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'form-v2'
REGIONS=[dict(name='near_three_offset_shoulders',bounds=[3660,4090,3800,4080]),dict(name='side_three_shoulder_belly_turns',bounds=[3800,4630,3430,3790])]
# Unequal named masses, two groups; these are connected skin relief, not spheres.
NEAR=[('large_high',3818.,3896.,123.,101.,920.),('medium_low',3730.,4000.,88.,87.,850.),('small_return',3903.,4000.,69.,66.,821.)]
SIDE=[('near_high_turn',4500.,3595.,118.,115.,873.),('middle_low_turn',4170.,3575.,108.,112.,831.),('far_short_turn',3900.,3680.,80.,76.,806.)]
def ss(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
def box_weight(xz,box):
 x0,x1,z0,z1=box;return ss(np.minimum.reduce([xz[:,0]-x0,x1-xz[:,0],xz[:,1]-z0,z1-xz[:,1]])/42.)
def patch_height(xz,lobes):
 target=np.full(len(xz),754.)
 for name,x,z,rx,rz,crest in lobes:
  q=((xz[:,0]-x)/rx)**2+((xz[:,1]-z)/rz)**2
  cap=754+(crest-754)*np.sqrt(np.maximum(0,1-q))
  # A small join radius retains a visible saddle rather than a broad soft max.
  h=np.maximum(6-abs(target-cap),0)/6
  target=np.maximum(target,cap)+1.5*h*h
 return target

def make():
 c=g.read(OLD/'candidate.json');b=g.read(OLD/'bindings.json');c=copy.deepcopy(c);b=copy.deepcopy(b)
 old=np.asarray(c['vertices_world']);v=old.copy();n=c['planar_vertex_count'];r=c['rim_count'];oldxz=old[:n][:,[0,2]]
 rim=np.asarray(c['external_rim_authority_float64_xz']);od=g.rim_distance(oldxz,rim);weights=[box_weight(oldxz,s['bounds']) for s in REGIONS]
 # Smooth lateral edits of existing paired samples. Fade before the protected
 # outer return so the original 80m boundary cannot be moved into an exception.
 shift=np.zeros((n,2))
 for W,lobes in zip(weights,(NEAR,SIDE)):
  for name,x,z,rx,rz,crest in lobes:
   off=oldxz-np.array([x,z]);q=(off[:,0]/(rx*1.25))**2+(off[:,1]/(rz*1.25))**2
   shift+=-.20*off*np.exp(-q*1.5)[:,None]*W[:,None]
 shift*=ss((od-90)/45)[:,None]
 for row in c['named_nodes'].values():shift[row['vertex_index']]=0
 v[:n,0]+=shift[:,0];v[:n,2]+=shift[:,1];v[n:,0]+=shift[r:,0];v[n:,2]+=shift[r:,1]
 v=g.native_world(v);xz=v[:n][:,[0,2]];d=g.rim_distance(xz,rim)
 # Uneven true-rim Y follows the three low-frequency turning regions. Never
 # moves the real concave outline or creates a fake internal edge exception.
 rim_delta=np.zeros(n)
 for W,lobes in zip(weights,(NEAR,SIDE)):
  for j,(name,x,z,rx,rz,crest) in enumerate(lobes):
   q=((xz[:,0]-x)/(rx*1.25))**2+((xz[:,1]-z)/(rz*1.3))**2
   rim_delta+=(22 if j==0 else -16 if j==1 else 13)*np.exp(-q)*W
 rim_delta*=1-ss(d/70)
 for W,lobes in zip(weights,(NEAR,SIDE)):
  target=patch_height(xz,lobes)
  # Existing exterior Y serves only as this candidate's baseline, with this
  # explicit local edit. No attempt to infer a new arbitrary global rim.
  rim_base=685+15*np.sin((xz[:,0]-3958+8)/260)+12*np.cos((xz[:,1]-4100)/220)
  roll=np.sin(np.minimum(d/75,1)*np.pi/2)
  target=(rim_base+rim_delta)*(1-roll)+target*roll
  # Narrow the blend in the rising main-crown approach. This is authored
  # influence, not a displacement clamp or a changed safety threshold.
  crown_join=ss((970-old[:n,1])/110)
  influence=W*crown_join
  v[:n,1]=v[:n,1]*(1-influence)+target*influence
 # Belly turn has distinct curvature, only in the original true outer band.
 # It returns exactly to the old belly by d=45, before the 80m core threshold.
 _,_,oldB=g.solid_arrays(c,old)
 bd=-(12*np.sin(np.minimum(d/45,1)*np.pi)**2)*(weights[0]+weights[1])
 bd+=rim_delta*(1-ss(d/45))
 allowed=(od<80)&(d<80)
 bd[~allowed]=0
 v[n:,1]=oldB[r:,1]+bd[r:]
 # Shared rim closes both skin sheets; exact named top AND belly points survive.
 v[:r,1]=old[:r,1]+rim_delta[:r]
 for row in c['named_nodes'].values():
  i=row['vertex_index'];v[i]=old[i]
  if i>=r:v[n+i-r]=old[n+i-r]
 v=g.native_world(v)
 # Strict outside preservation, also protecting tiny boundary weight roundoff.
 inside=np.zeros(n,bool)
 for s in REGIONS:
  x0,x1,z0,z1=s['bounds'];inside|=(oldxz[:,0]>=x0)&(oldxz[:,0]<=x1)&(oldxz[:,1]>=z0)&(oldxz[:,1]<=z1)
 g.require(np.array_equal(v[~np.r_[inside,inside[r:]]],old[~np.r_[inside,inside[r:]]]),'OUTSIDE_CHANGED')
 c.pop('form_v2',None);b.pop('form_v2',None)
 c['version']=g.VERSION;b['version']=g.VERSION;c['vertices_world']=v.tolist()
 _,T,B=g.solid_arrays(c)
 for row in c['authoritative_vertices']:
  row['top']=float(T[row['index'],1])
  if row.get('bottom') is not None:row['bottom']=float(B[row['index'],1])
 for row in b['baseline_authority']:
  row['historical_form_v2_top_world']=row['top_world'];row['historical_form_v2_bottom_world']=row['bottom_world']
  i=row['vertex_index'];row['top_world']=T[i].tolist();row['bottom_world']=B[i].tolist()
 scope=dict(regions_world_xz=REGIONS,parent_candidate_sha256=g.sha(OLD/'candidate.json'),parent_bindings_sha256=g.sha(OLD/'bindings.json'),old_internal_XZ_identity=False,old_edge_belly_Y_identity=False,old_local_top_profile_identity=False,true_rim_XZ_unchanged=True,core80m_rule_unchanged=True,core_belly_560_630_unchanged=True,core_minimum_thickness_120_unchanged=True,maximum_paired_XZ_displacement_m=35,maximum_edge_Y_displacement_m=35,maximum_top_Y_displacement_m=120,topology_unchanged=True,all_control_fields_unchanged=True)
 c['form_v3']=scope;b['form_v3']={**scope,'prior_vertices_world':old.tolist(),'prior_faces_sha256':hashlib.sha256(json.dumps(c['faces'],separators=(',',':')).encode()).hexdigest(),'prior_controls_sha256':hashlib.sha256(json.dumps(c['controls'],separators=(',',':')).encode()).hexdigest()}
 delta=v-old;changed=np.flatnonzero(np.any(delta!=0,1));bd=B[:,1]-oldB[:,1]
 report=dict(candidate_version=g.VERSION,scope=scope,lobes={'near':NEAR,'side':SIDE},changed_vertices=len(changed),changed_plan_points=int(np.any(delta[:n][:,[0,2]]!=0,1).sum()),changed_top_y=int((delta[:n,1]!=0).sum()),changed_belly_y=int((bd!=0).sum()),changed_rim_y=int((delta[:r,1]!=0).sum()),max_XZ_m=float(np.linalg.norm(delta[:,[0,2]],axis=1).max()),top_Y_delta_range=[float(delta[:n,1].min()),float(delta[:n,1].max())],belly_Y_delta_range=[float(bd.min()),float(bd.max())],per_vertex_changes=[dict(index=int(i),before=old[i].tolist(),after=v[i].tolist(),delta=delta[i].tolist()) for i in changed],native_executed=False,visual_acceptance=False,full_native_acceptance=False)
 return c,b,report

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args()
 if not a.write:print('No-op. --write prepares the single approved art candidate only.');return
 for fn in ('candidate.json','bindings.json','FORM_CHANGE_REPORT.json','GEOMETRY_RESULT.json'):g.require(not(HERE/fn).exists(),'PRESERVE_PRIOR_PREPARATION:'+fn)
 c,b,r=make();g.write(HERE/'candidate.json',c);g.write(HERE/'bindings.json',b);g.write(HERE/'FORM_CHANGE_REPORT.json',r)
 result={'passed':False,'native_executed':False,'candidate_sha256':g.sha(HERE/'candidate.json')}
 try:
  result['geometry']=g.validate_candidate(c);result['controls']=[]
  for control in c['controls']:
   moved=g.evaluate(c,{control['id']:control['exercise_value']});result['controls'].append({'id':control['id'],'changed_vertices':int(np.any(moved!=np.asarray(c['vertices_world']),1).sum())})
   for extra in control.get('secondary_parameters',[]):
    key=control['id']+'.'+extra['id'];moved=g.evaluate(c,{key:extra['exercise_value']});result['controls'].append({'id':key,'changed_vertices':int(np.any(moved!=np.asarray(c['vertices_world']),1).sum())})
  result['passed']=True
 except BaseException:result['error']=traceback.format_exc()
 g.write(HERE/'GEOMETRY_RESULT.json',result);print(json.dumps({**{k:v for k,v in r.items() if k!='per_vertex_changes'},'geometry_passed':result['passed'],'error':result.get('error')},indent=2))
 if not result['passed']:raise SystemExit(1)
if __name__=='__main__':main()
