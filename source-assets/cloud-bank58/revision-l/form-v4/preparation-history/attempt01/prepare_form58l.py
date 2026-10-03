"""One continuous crown-waist / near-front form revision. Pure preparation only."""
import os,sys
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
sys.dont_write_bytecode=True
from pathlib import Path
import copy,json,hashlib,argparse,traceback
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry58l as g
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'form-v3'
REGIONS=[
 {'name':'A_complete_crown_waist','shape':'ellipse','center':[4140.,3910.],'radii':[230.,220.],'support_scale':1.6},
 {'name':'B_complete_crown_waist','shape':'ellipse','center':[4330.,4480.],'radii':[240.,230.],'support_scale':1.6},
 {'name':'near_actual_front','shape':'box','bounds':[3635.,4075.,3740.,4150.]},
]
CROWNS=[('A',4140.,3910.,230.,220.,945.),('B',4330.,4480.,240.,230.,975.)]
# Shoulders live roughly halfway between the local base and their main crown.
# They are connected relief in the same skin, not extra spheres or topology.
WAISTS=[('A_side_lower',4230.,3730.,135.,115.,850.),('A_near_oblique',4000.,3865.,140.,125.,850.),
        ('B_valley_lower',4230.,4320.,140.,125.,855.),('B_side_lower',4490.,4425.,145.,135.,865.)]
NEAR=[('large_lower_wider',3818.,3896.,150.,140.,860.),('medium_lower_wider',3730.,4000.,110.,105.,820.),('small_return',3903.,4000.,90.,75.,798.)]
def ss(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
def weights(xz):
 out=[]
 for region in REGIONS:
  if region['shape']=='ellipse':
   q=np.linalg.norm((xz-np.asarray(region['center']))/np.asarray(region['radii']),axis=1)
   out.append(ss((region['support_scale']-q)/.35))
  else:
   x0,x1,z0,z1=region['bounds'];out.append(ss(np.minimum.reduce([xz[:,0]-x0,x1-xz[:,0],xz[:,1]-z0,z1-xz[:,1]])/42.))
 return out

def valley_distance(xz,c):
 paths=[['V0','V1','V2','V3','V4'],['V2','VB1','VB2']];out=np.full(len(xz),np.inf)
 for names in paths:
  for ka,kb in zip(names,names[1:]):
   a=np.asarray(c['named_nodes'][ka]['world_xyz'])[[0,2]];b=np.asarray(c['named_nodes'][kb]['world_xyz'])[[0,2]];u=b-a;t=np.clip((xz-a)@u/(u@u),0,1);out=np.minimum(out,np.linalg.norm(xz-a-t[:,None]*u,axis=1))
 return out

def nearest_rim_y(xz,oldT,r):
 a=oldT[:r][:,[0,2]];b=np.roll(a,-1,axis=0);u=b-a;ay=oldT[:r,1];by=np.roll(ay,-1);out=[]
 for q in xz:
  t=np.clip(np.sum((q-a)*u,axis=1)/np.sum(u*u,axis=1),0,1);k=int(np.argmin(np.linalg.norm(q-a-t[:,None]*u,axis=1)));out.append(ay[k]+t[k]*(by[k]-ay[k]))
 return np.asarray(out)

def make():
 c=copy.deepcopy(g.read(OLD/'candidate.json'));b=copy.deepcopy(g.read(OLD/'bindings.json'));prior=copy.deepcopy(c)
 old=np.asarray(c['vertices_world']);v=old.copy();n=c['planar_vertex_count'];r=c['rim_count'];oldxz=old[:n][:,[0,2]];rim=np.asarray(c['external_rim_authority_float64_xz'])
 od=g.rim_distance(oldxz,rim);W=weights(oldxz);dv=valley_distance(oldxz,c);valley_keep=ss((dv-55)/45)
 # Author a smooth sample-row redistribution in the actual near front, including
 # the previously locked <90m INTERNAL rows. The shared true rim stays exact.
 radial=oldxz-np.asarray([3818.,3896.]);length=np.linalg.norm(radial,axis=1);direction=radial/np.maximum(length,1)[:,None]
 amount=np.where(od<90,10*np.sin(np.pi*np.minimum(od,90)/90),-6*np.sin(np.pi*np.clip((od-90)/70,0,1)))
 amount[od>=160]=0;shift=direction*(amount*W[2]*valley_keep)[:,None];shift[:r]=0
 for row in c['named_nodes'].values():shift[row['vertex_index']]=0
 v[:n,0]+=shift[:,0];v[:n,2]+=shift[:,1];v[n:,0]+=shift[r:,0];v[n:,2]+=shift[r:,1];v=g.native_world(v)
 xz=v[:n][:,[0,2]];d=g.rim_distance(xz,rim)
 # Variable shared baseline and zero-slope compact crown/waist sections avoid
 # both the old common 754m floor and the artificial Z=3790 cutting boundary.
 base=770+9*np.sin((xz[:,0]-4050)/310)+7*np.cos((xz[:,1]-4010)/290)
 target=base.copy()
 for name,x,z,rx,rz,crest in CROWNS+WAISTS+NEAR:
  q=np.sqrt(((xz[:,0]-x)/rx)**2+((xz[:,1]-z)/rz)**2)
  reach=1.6 if name in ('A','B') else 1.5
  kernel=.5+.5*np.cos(np.pi*np.minimum(q/reach,1))
  cap=base+(crest-base)*kernel
  h=np.maximum(8-abs(target-cap),0)/8
  target=np.maximum(target,cap)+2*h*h
 roll=np.sin(np.minimum(d/75,1)*np.pi/2)
 rim_y=nearest_rim_y(xz,old[:n],r);target=rim_y*(1-roll)+target*roll
 influence=(1-(1-W[0])*(1-W[1])*(1-W[2]))*valley_keep
 # B's named low exit and the retained C/D named centers have a continuous join.
 for name in ('C','D','B_exit'):
  center=np.asarray(c['named_nodes'][name]['world_xyz'])[[0,2]];influence*=ss(np.linalg.norm(oldxz-center,axis=1)/65)
 v[:n,1]=old[:n,1]*(1-influence)+target*influence
 _,_,oldB=g.solid_arrays(c,old)
 # A small belly return only accompanies the near shoulder's true exterior band.
 belly=-6*np.sin(np.minimum(d/45,1)*np.pi)**2*W[2]
 belly[(od>=80)|(d>=80)]=0
 v[n:,1]=oldB[r:,1]+belly[r:];v[:r]=old[:r]
 for name,row in c['named_nodes'].items():
  i=row['vertex_index'];v[i]=old[i]
  if i>=r:v[n+i-r]=old[n+i-r]
 for name,crest in [('A',945.),('B',975.)]:v[c['named_nodes'][name]['vertex_index'],1]=crest
 v=g.native_world(v);c['vertices_world']=v.tolist();c['version']=g.VERSION;b['version']=g.VERSION
 c.pop('form_v3',None);b.pop('form_v3',None)
 # Real absolute controls, handles, default/min/max/exercise and support fields.
 control_changes=[]
 for index,(name,x,z,rx,rz,crest) in enumerate(CROWNS):
  row=c['controls'][index];before=copy.deepcopy(row);delta=crest-row['default']
  for key in ('default','min','max','exercise_value'):row[key]+=delta
  row['position_world'][1]=crest
  q=np.sqrt(((xz[:,0]-x)/rx)**2+((xz[:,1]-z)/rz)**2)
  kernel=(.5+.5*np.cos(np.pi*np.minimum(q/1.6,1)))*valley_keep
  for key,node in c['named_nodes'].items():
   if key==name:continue
   center=np.asarray(node['world_xyz'])[[0,2]];kernel*=ss(np.linalg.norm(xz-center,axis=1)/55)
  kernel[:r]=0;kernel[c['named_nodes'][name]['vertex_index']]=1
  allw=np.zeros(len(v));allw[:n]=kernel;allw=g.f32(allw);field=np.zeros(v.shape);field[:,1]=allw
  row['weights']=allw.tolist();row['displacements_world']=field.tolist()
  row['semantic']='Absolute '+name+' crown height; continuous lowered/widened crown and offset half-height waist; genuine fixed-XZ top-height edit'
  c['named_nodes'][name]['world_xyz']=v[c['named_nodes'][name]['vertex_index']].tolist()
  b['baseline_nodes'][name]=copy.deepcopy(c['named_nodes'][name])
  control_changes.append({'id':row['id'],'old':{k:before[k] for k in ('default','min','max','exercise_value','position_world','semantic')},'new':{k:row[k] for k in ('default','min','max','exercise_value','position_world','semantic')},'absolute_parameter_shift_m':delta,'relative_range_preserved':[before['min']-before['default'],before['max']-before['default']],'old_support_sha256':hashlib.sha256(json.dumps([before['weights'],before['displacements_world']],separators=(',',':')).encode()).hexdigest(),'new_support_sha256':hashlib.sha256(json.dumps([row['weights'],row['displacements_world']],separators=(',',':')).encode()).hexdigest(),'old_supported_vertices':int(np.count_nonzero(before['weights'])),'new_supported_vertices':int(np.count_nonzero(allw))})
 _,T,B=g.solid_arrays(c)
 for row in c['authoritative_vertices']:
  row['top']=float(T[row['index'],1])
  if row.get('bottom') is not None:row['bottom']=float(B[row['index'],1])
 for row in b['baseline_authority']:
  row['historical_form_v3_top_world']=row['top_world'];row['historical_form_v3_bottom_world']=row['bottom_world'];i=row['vertex_index'];row['top_world']=T[i].tolist();row['bottom_world']=B[i].tolist()
 fixed_valley=np.flatnonzero(dv<=55).tolist()
 scope=dict(regions_world_xz=REGIONS,parent_candidate_sha256=g.sha(OLD/'candidate.json'),parent_bindings_sha256=g.sha(OLD/'bindings.json'),old_AB_crown_height_width_support_identity=False,old_two_rectangle_patch_identity=False,old_internal_XZ_identity=False,old_local_top_profile_identity=False,old_near_edge_belly_Y_identity=False,true_rim_XYZ_unchanged=True,core80m_rule_unchanged=True,core_belly_560_630_unchanged=True,core_minimum_thickness_120_unchanged=True,maximum_paired_XZ_displacement_m=35,maximum_edge_Y_displacement_m=35,maximum_top_Y_displacement_m=120,topology_unchanged=True,unchanged_control_ids=[x['id'] for x in c['controls'][2:]],AB_control_parameter_shifts={'A':-60,'B':-65},preserved_valley_vertices=fixed_valley)
 c['form_v4']=scope;b['form_v4']={**scope,'prior_vertices_world':old.tolist(),'prior_faces_sha256':hashlib.sha256(json.dumps(c['faces'],separators=(',',':')).encode()).hexdigest(),'prior_controls':prior['controls'],'prior_named_nodes':prior['named_nodes'],'prior_section_paths':prior['section_paths']}
 delta=v-old;changed=np.flatnonzero(np.any(delta!=0,axis=1));bd=B[:,1]-oldB[:,1]
 report=dict(candidate_version=g.VERSION,scope=scope,crowns=CROWNS,waist_shoulders=WAISTS,near_shoulders=NEAR,control_changes=control_changes,changed_vertices=len(changed),changed_plan_points=int(np.any(delta[:n][:,[0,2]]!=0,1).sum()),changed_top_y=int((delta[:n,1]!=0).sum()),changed_belly_y=int((bd!=0).sum()),changed_rim_y=int((delta[:r,1]!=0).sum()),max_XZ_m=float(np.linalg.norm(delta[:,[0,2]],axis=1).max()),top_Y_delta_range=[float(delta[:n,1].min()),float(delta[:n,1].max())],belly_Y_delta_range=[float(bd.min()),float(bd.max())],changed_world_bounds=[v[changed].min(0).tolist(),v[changed].max(0).tolist()],per_vertex_changes=[dict(index=int(i),before=old[i].tolist(),after=v[i].tolist(),delta=delta[i].tolist()) for i in changed],native_executed=False,visual_acceptance=False,full_native_acceptance=False)
 return c,b,report

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args()
 if not a.write:print('No-op. --write prepares this one authorized candidate only.');return
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
 g.write(HERE/'GEOMETRY_RESULT.json',result);print(json.dumps({**{k:v for k,v in r.items() if k not in ('per_vertex_changes','scope')},'geometry_passed':result['passed'],'error':result.get('error')},indent=2))
 if not result['passed']:raise SystemExit(1)
if __name__=='__main__':main()
