#!/usr/bin/env python3
"""Read-only exact-BVH validation of frozen1m base plus newly baked0.25m patches."""
import ast,json,hashlib,math,time
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;BASE=P.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
meta=json.loads((BASE/'support49-export.json').read_text());manifest=json.loads((P/'patches.json').read_text());old=json.loads((BASE/'depth49-bake-report.json').read_text())
assert sha(BASE/'support49-world-f32.bin')==manifest['source_triangle_binary_sha256']
assert sha(BASE/'height49-1m-rf.f32')==manifest['frozen_base_height_rf_sha256']
raw=np.fromfile(BASE/'support49-world-f32.bin',dtype='<f4').reshape(-1,3,3).astype(float)
ids=np.empty(len(raw),np.int32)
for n,m in enumerate(meta['included_meshes']):ids[m['byte_offset']//36:(m['byte_offset']+m['byte_length'])//36]=n
lo=raw[:,:,[0,2]].min(1);hi=raw[:,:,[0,2]].max(1);aa,bb,cc=raw[:,0],raw[:,1],raw[:,2]
d0=(bb[:,2]-cc[:,2])*(aa[:,0]-cc[:,0])+(cc[:,0]-bb[:,0])*(aa[:,2]-cc[:,2])
valid=(np.abs(d0)>1e-12)&(hi[:,0]>=768)&(lo[:,0]<=1536)&(hi[:,1]>=-2304)&(lo[:,1]<=-768)
tri=raw[valid];mids=ids[valid];lo=lo[valid];hi=hi[valid];den=d0[valid];a,b,c=tri[:,0],tri[:,1],tri[:,2];centers=(lo+hi)*.5;nodes=[]
for f in ast.parse((BASE/'bake_support_depth49.py').read_text()).body:
 if isinstance(f,ast.FunctionDef) and f.name in ['build','top','summary']:exec(compile(ast.Module(body=[f],type_ignores=[]),'<frozen BVH functions>','exec'),globals())
build(np.arange(len(tri)))
base_data=np.fromfile(BASE/'height49-1m-rf.f32',dtype='<f4').reshape(1537,769)
patches=[]
for p in manifest['patches']:
 assert sha(P/p['raw_float32_file'])==p['raw_sha256']
 q=dict(p);q['data']=np.fromfile(P/p['raw_float32_file'],dtype='<f4').reshape(p['size'][1],p['size'][0]);patches.append(q)
for i,p in enumerate(patches):
 for q in patches[i+1:]:
  x0,z0,x1,z1=p['world_bounds'];u0,v0,u1,v1=q['world_bounds'];assert x1<=u0 or u1<=x0 or z1<=v0 or v1<=z0

def sample(data,x,z,bounds,spacing):
 h,w=data.shape;gx=min(w-1,max(0,(x-bounds[0])/spacing));gz=min(h-1,max(0,(z-bounds[1])/spacing))
 ix=min(w-2,int(gx));iz=min(h-2,int(gz));fx=gx-ix;fz=gz-iz
 return float(data[iz,ix]*(1-fx)*(1-fz)+data[iz,ix+1]*fx*(1-fz)+data[iz+1,ix]*(1-fx)*fz+data[iz+1,ix+1]*fx*fz)
def base_sample(x,z):return sample(base_data,x,z,[768,-2304,1536,-768],1.0)
def select_patch(x,z):
 for p in patches:
  x0,z0,x1,z1=p['world_bounds']
  if x0<=x<=x1 and z0<=z<=z1:return p
 return None
def weight(p,x,z):
 x0,z0,x1,z1=p['world_bounds'];d=min(x-x0,z-z0,x1-x,z1-z)
 if d<=0:return 0.0
 if d>=8:return 1.0
 t=d/8;return t*t*(3-2*t)
def patch_sample(p,x,z):return sample(p['data'],x,z,p['world_bounds'],.25)
def fused_sample(x,z):
 base=base_sample(x,z);p=select_patch(x,z)
 if p is None:return base
 w=weight(p,x,z)
 if w<=0:return base # Literal unchanged branch, avoids arithmetic/NaN surprises.
 return base+(patch_sample(p,x,z)-base)*w

def segment_has_true_jump(p0,h0,p1,h1):
 # Refine the largest-changing half until <0.1mm. A continuous linear cliff
 # halves its vertical difference; a genuine finite jump retains it.
 if abs(h1-h0)<.25:return False,None
 prev=abs(h1-h0);ratios=[]
 for _ in range(13):
  mid=(p0+p1)*.5;hm=top(float(mid[0]),float(mid[1]))
  if abs(hm-h0)>=abs(h1-hm):p1,h1=mid,hm
  else:p0,h0=mid,hm
  delta=abs(h1-h0);ratios.append(delta/max(prev,1e-30));prev=delta
 delta=abs(h1-h0);dist=float(np.linalg.norm(p1-p0))
 ok=delta>.25 and min(ratios[-3:])>.8
 return ok,{'remaining_height_jump_m':delta,'interval_length_m':dist,'last_three_refinement_ratios':ratios[-3:]}
class_cache={};classification_evidence=[]
def classify(x,z,p,exact):
 if p is None:return 'outside_patch_unchanged'
 x0,z0,_,_=p['world_bounds'];ix=math.floor((x-x0)*4);iz=math.floor((z-z0)*4);key=(p['name'],ix,iz)
 # Cells cached as continuous need sample-specific check if a tiny feature lies
 # wholly between lattice points. Include the exact sample as an endpoint.
 corners=np.array([[x0+ix*.25,z0+iz*.25],[x0+(ix+1)*.25,z0+iz*.25],[x0+ix*.25,z0+(iz+1)*.25],[x0+(ix+1)*.25,z0+(iz+1)*.25]])
 if key not in class_cache:
  vals=[top(float(xx),float(zz)) for xx,zz in corners];class_cache[key]=(corners,vals)
 else:corners,vals=class_cache[key]
 span=max(vals+[exact])-min(vals+[exact])
 if span<.25:return 'continuous_general'
 anchor=np.array([x,z]);candidates=[(anchor,exact,corners[j],vals[j]) for j in range(4) if abs(exact-vals[j])>.25]
 candidates +=[(corners[j],vals[j],corners[k],vals[k]) for j,k in [(0,1),(0,2),(1,3),(2,3)] if abs(vals[j]-vals[k])>.25]
 candidates.sort(key=lambda s:abs(s[1]-s[3]),reverse=True)
 for v0,h0,v1,h1 in candidates:
  ok,evidence=segment_has_true_jump(v0,h0,v1,h1)
  if ok:
   if len(classification_evidence)<40:classification_evidence.append({'world_xz':[x,z],'patch':p['name'],'evidence':evidence})
   return 'true_discontinuity_nearby'
 return 'continuous_steep_or_fold'

def row(x,z, classify_it=True):
 exact=top(float(x),float(z));base=base_sample(x,z);fused=fused_sample(x,z);p=select_patch(x,z);patch=patch_sample(p,x,z) if p else None
 r={'world_xz':[float(x),float(z)],'actual_highest_y':exact,'base_height_y':base,'fused_height_y':fused,'patch':p['name'] if p else None,'patch_only_height_y':patch,'blend_weight':weight(p,x,z) if p else 0.0,'classification':classify(x,z,p,exact) if classify_it else None}
 for tag,y in [('base',base),('fused',fused),('patch_only',patch)]:
  r[tag+'_height_error_m']=abs(y-exact) if y is not None else None
  r[tag+'_depth_error_m']=abs(max(0,-y)-max(0,-exact)) if y is not None else None
 return r

def metrics(rows):
 result={'sample_count':len(rows)}
 for tag in ['base','patch_only','fused']:
  for kind in ['height','depth']:
   result[tag+'_'+kind+'_error']=summary([r[tag+'_'+kind+'_error_m'] for r in rows if r[tag+'_'+kind+'_error_m'] is not None])
 return result
def split_metrics(rows):
 labels=sorted(set(r['classification'] for r in rows));return {k:metrics([r for r in rows if r['classification']==k]) for k in labels}
start=time.time()
# Same random stream and coordinates as frozen1m report; do not overwrite it.
rng=np.random.default_rng(490050);rng.integers(0,769,2500);rng.integers(0,1537,2500)
xs=rng.uniform(768,1536,4000);zs=rng.uniform(-2304,-768,4000)
global_rows=[row(float(x),float(z)) for x,z in zip(xs,zs)]
print('same global points done',time.time()-start,flush=True)
local_rows=[];grid_rows=[];edge_rows=[]
for n,p in enumerate(patches):
 rng=np.random.default_rng(490025+n);x0,z0,x1,z1=p['world_bounds']
 xs=rng.uniform(x0,x1,3000);zs=rng.uniform(z0,z1,3000)
 local_rows.extend(row(float(x),float(z)) for x,z in zip(xs,zs))
 for ix,iz in zip(rng.integers(0,p['size'][0],1200),rng.integers(0,p['size'][1],1200)):
  x=x0+int(ix)*.25;z=z0+int(iz)*.25;actual=top(x,z);stored=float(p['data'][iz,ix]);grid_rows.append({'patch':p['name'],'world_xz':[x,z],'height_error_m':abs(actual-stored)})
 # Exact boundary and several points just outside: fusion must return exact base.
 for t in np.linspace(0,1,129):
  for x,z in [(x0,z0+(z1-z0)*t),(x1,z0+(z1-z0)*t),(x0+(x1-x0)*t,z0),(x0+(x1-x0)*t,z1),(x0-.001,z0+(z1-z0)*t),(x1+.001,z0+(z1-z0)*t),(x0+(x1-x0)*t,z0-.001),(x0+(x1-x0)*t,z1+.001)]:
   edge_rows.append({'patch':p['name'],'world_xz':[float(x),float(z)],'fused_minus_base':fused_sample(x,z)-base_sample(x,z)})
 print('local',p['name'],'done',time.time()-start,flush=True)
# Recreate same actual source-triangle shoreline crossings and same +/-2m search.
shore=[]
for k,t in enumerate(tri):
 if t[:,1].min()>0 or t[:,1].max()<0:continue
 crossing=[]
 for j in range(3):
  u=t[j];v=t[(j+1)%3]
  if u[1]==0:crossing.append(u.copy())
  if u[1]*v[1]<0:crossing.append(u+(v-u)*(-u[1]/(v[1]-u[1])))
 if len(crossing)<2:continue
 u,v=crossing[:2];tangent=(v-u)[[0,2]];length=np.linalg.norm(tangent)
 if length<1e-6:continue
 normal=np.array([-tangent[1],tangent[0]])/length
 for fraction in [.2,.5,.8]:
  point=u*(1-fraction)+v*fraction;x,z=point[[0,2]]
  if x<768.1 or x>1535.9 or z< -2303.9 or z> -768.1:continue
  exact=top(x,z)
  if abs(exact)>.005:continue
  r=row(float(x),float(z));r['source_mesh']=meta['included_meshes'][int(mids[k])]['path'];r['normal_xz']=normal.tolist()
  p=select_patch(x,z)
  for tag,fn in [('base',base_sample),('fused',fused_sample),('patch_only',lambda xx,zz,p=p:patch_sample(p,xx,zz) if p else None)]:
   if tag=='patch_only' and p is None:r[tag+'_zero_offset_m']=None;continue
   shifts=np.linspace(-2,2,161);vals=[fn(float(x+normal[0]*s),float(z+normal[1]*s)) for s in shifts];zeros=[]
   for j in range(len(shifts)-1):
    if vals[j]==0:zeros.append(float(shifts[j]))
    elif vals[j]*vals[j+1]<0:zeros.append(float(shifts[j]-vals[j]*(shifts[j+1]-shifts[j])/(vals[j+1]-vals[j])))
   r[tag+'_zero_offset_m']=min(map(abs,zeros)) if zeros else None
  shore.append(r)
assert len(shore)==len(old['actual_shore_samples']),(len(shore),len(old['actual_shore_samples']))
for current,original in zip(shore,old['actual_shore_samples']):
 assert np.allclose(current['world_xz'],original['world_xz'],atol=1e-8,rtol=0)
 assert abs(current['base_height_y']-original['baked_signed_height_y'])<1e-10
print('same shore done',time.time()-start,flush=True)

def shore_metrics(rows):
 out=metrics(rows)
 for tag in ['base','patch_only','fused']:
  applicable=[r for r in rows if tag!='patch_only' or r['patch'] is not None]
  out[tag+'_zero_horizontal_offset']=summary([r[tag+'_zero_offset_m'] for r in applicable if r[tag+'_zero_offset_m'] is not None])
  out[tag+'_zero_not_found_within_2m']=sum(r[tag+'_zero_offset_m'] is None for r in applicable)
 return out
per_patch={}
for p in patches:
 name=p['name'];local=[r for r in local_rows if r['patch']==name];ss=[r for r in shore if r['patch']==name]
 per_patch[name]={'gridpoint_height_error':summary([r['height_error_m'] for r in grid_rows if r['patch']==name]),'continuous_random':metrics(local),'continuous_random_by_actual_geometry':split_metrics(local),'same_actual_shore':shore_metrics(ss),'shore_by_actual_geometry':{k:shore_metrics([r for r in ss if r['classification']==k]) for k in sorted(set(r['classification'] for r in ss))},'largest_continuous_errors':sorted(local,key=lambda r:r['fused_height_error_m'],reverse=True)[:12],'largest_shore_errors':sorted(ss,key=lambda r:r['fused_height_error_m'],reverse=True)[:12]}
unchanged=[r for r in global_rows if r['blend_weight']==0.0]
report={'purpose':'Existing49 water material diagnostic accuracy,0.25m additive patches over immutable1m base; no scene changes/candidate',
 'source_scene_sha256':manifest['source_scene_sha256'],'source_triangle_binary_sha256':manifest['source_triangle_binary_sha256'],'patch_manifest_sha256':sha(P/'patches.json'),'frozen1m_report_sha256':sha(BASE/'depth49-bake-report.json'),
 'classification_method':{'general':'Actual BVH heights at sample and containing0.25m cell corners vary <0.25m','true_discontinuity_nearby':'Across sample/corner or corner/corner segment, bisect largest height-change half13 times; remaining jump>0.25m and last3 change ratios each>0.8. Continuous steep linear faces halve their delta and are not called discontinuities. This is a numerical geometric diagnostic at <0.1mm, not a symbolic topology proof.','continuous_steep_or_fold':'Cell varies >=0.25m but refinement did not establish a persistent finite jump. Includes genuine steep continuous faces and creases; errors remain included in full metrics.','no_exclusions':'No discontinuity sample is dropped from aggregate statistics; missing zero crossings remain explicit failures.'},
 'same4000_global_random':metrics(global_rows),'same4000_affected_subset':metrics([r for r in global_rows if r['patch'] is not None]),'same4000_by_actual_geometry':split_metrics(global_rows),
 'same2180_actual_shore':shore_metrics(shore),'same_actual_island_shore_subset':shore_metrics([r for r in shore if '/LakeIslands49/' in r['source_mesh']]),
 'combined_patch_random_12000':metrics(local_rows),'combined_patch_random_by_actual_geometry':split_metrics(local_rows),
 'per_patch':per_patch,'outside_feather_proof':{'strict_function':'if no containing patch or edge distance<=0, return unchanged base sample directly. Four patch domains do not overlap.','random_zero_weight_samples':len(unchanged),'random_zero_weight_max_absolute_change':max(abs(r['fused_height_y']-r['base_height_y']) for r in unchanged),'boundary_and_just_outside_samples':len(edge_rows),'boundary_and_outside_max_absolute_change':max(abs(r['fused_minus_base']) for r in edge_rows),'base_rf_sha256_before':manifest['frozen_base_height_rf_sha256'],'base_rf_sha256_after':sha(BASE/'height49-1m-rf.f32'),'base_image_sha256_before':manifest['frozen_base_height_image_sha256'],'base_image_sha256_after':sha(BASE/'height49-1m-rf.res'),'minimum_actual_footprint_clearance_beyond8m_feather_m':min(p['minimum_margin_beyond_feather_m'] for p in patches)},
 'true_discontinuity_examples':classification_evidence,'all_same_global_samples':global_rows,'all_same_shore_samples':shore,'elapsed_seconds':time.time()-start,
 'limits':'0.25m bilinear heightfields cannot exactly represent vertical/overhanging upper-envelope jumps or arbitrarily thin wet rocks. Large maximum Y/depth errors are reported, not hidden by gridpoint accuracy. Visual A/B/A remains required.', 'visual_acceptance':False,'candidate_created':False}
assert not (P/'fusion-verification.json').exists();(P/'fusion-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:report[k] for k in ['same4000_global_random','same4000_affected_subset','same_actual_island_shore_subset','combined_patch_random_12000','combined_patch_random_by_actual_geometry','outside_feather_proof','elapsed_seconds']},indent=2),flush=True)
