#!/usr/bin/env python3
"""Bounded, source-only 167-row continuous support pre-solve. No engine or writes
outside this directory. --write creates separate reports, never placement buffers.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, sys
import numpy as np
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent; R=D.parents[2]; P=R/'candidates/round40-exclusive-20260930/project'; PREP=D.parent/'preparation-v1'
sys.path.insert(0,str(R/'source-assets/north-ridge62-intake/scatter-readonly-v1'))
import decoder62
sys.path.insert(0,str(R/'source-assets/coast57/revision-b'))
import foot_geometry57b as fg
import visible_geometry_core57b as vg
E=R/'cloud-evidence/north-ridge62-shadow-script-v4-20261002T094319Z-o5sjgbgh'
SURVEY=R/'cloud-evidence/coast-boundary-readonly-20261001/native-coast.json'
TREE={'pine','oak','poplar'}; TARGETS=['Ground_-4_-7','Ground_-3_-7','Ground_-4_-6','Ground_-3_-6','Ground_-4_-5','Ground_-3_-5']
FREEZE='12d9f492d3ae1251d37f6b8b94e9e5877eb85dd96f723f97542a5c4885818702'

def require(v,m):
 if not v:raise ValueError(m)
def read(p):return json.loads(p.read_text())
def check_pin(path,pin):
 require(path.stat().st_size==pin['bytes']and sha(path)==pin['sha256'],'consumed frozen source pin '+str(path))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(a):return hashlib.sha256(np.asarray(a,'<f4').tobytes()).hexdigest()
def affine(row,vertices):
 t=np.asarray(row['original_world_transform_columns'],float);return np.asarray(vertices,float)@t[:9].reshape(3,3)+t[9:]
def cross2(a,b):return a[0]*b[1]-a[1]*b[0]
def area2(p):return abs(float(np.sum(p[:,0]*np.roll(p[:,1],-1)-p[:,1]*np.roll(p[:,0],-1))))/2

def models(native):
 out={};pins={}
 for kind in ['pine','rock','bush','oak','poplar']:
  path=P/('assets/coast61/oak_-5_-5_CoastalPines36b.res'if kind=='pine'else f'assets/meshes/{kind}.res')
  raw=path.read_bytes();doc=decoder62._Reader(raw).parse();meshes=[r for r in doc['resources']if r['type']=='ArrayMesh'];m=meshes[-1]
  witness=next(x for x in native['visual_meshes']if ('/coast61/'in x['mesh_resource']if kind=='pine'else x['mesh_resource']==f'res://assets/meshes/{kind}.res'))
  require(len(m['properties']['_surfaces'])==1,'one known primary surface')
  s=m['properties']['_surfaces'][0];require(s['format']==34896613407 and s['primitive']==3,'fixed compressed source layout')
  n=s['vertex_count'];a=np.array(s['aabb']['values'],np.float32);off=s['vertex_data']['payload_offset'];require(s['vertex_data']['payload_bytes']==n*12,'vertex layout')
  q=np.frombuffer(raw[off:off+n*8],'<u2').reshape(n,4)[:,:3]
  v=(q.astype('f4')/np.float32(65535)*a[3:]+a[:3]).astype('f4');off=s['index_data']['payload_offset'];ix=np.frombuffer(raw[off:off+s['index_count']*2],'<u2');tri=v[ix].reshape(-1,3,3)
  require(digest(v)==witness['surfaces'][0]['vertex_bytes_sha256'] and digest(tri)==witness['face_bytes_sha256'],'actual native vertex/ordered face bytes '+kind)
  require(np.isfinite(v).all() and max(ix)<n,'finite indexed geometry')
  if kind in TREE:
   ring=np.unique(v[v[:,1]==v[:,1].min()],axis=0).astype(float);require(np.all(ring[:,1]==0) and len(ring)in [6,7],'actual flat root ring')
   ring=ring[np.argsort(np.arctan2(ring[:,2],ring[:,0]))];polys=[ring];first=float(np.min(v[v[:,1]>0,1]));baseadj=tri[np.any(tri[:,:,1]==0,axis=1)];trunk_layers=np.unique(baseadj[baseadj[:,:,1]>0,1]);require(len(trunk_layers)==1,'one trunk ring connected to base');trunk_first=float(trunk_layers[0])
  else:
   first=None;trunk_first=None;polys=[p for t in tri for p in [fg.clip_root(t.astype(float))]if len(p)>=3 and fg.plane(p)is not None]
  proxy=None
  if kind=='rock':
   step=np.float32(.0001);proxy=(np.floor(np.float32(tri/step)+np.float32(.5))*step).astype('f4')
   require(digest(tri)==native['rock']['face_bytes_sha256'] and digest(proxy)==native['rock']['get_faces_bytes_sha256'],'actual imported rock get_faces byte equality')
  out[kind]={'tri':tri.astype(float),'polys':polys,'proxy_polys':None if proxy is None else [p for t in proxy for p in [fg.clip_root(t.astype(float))]if len(p)>=3 and fg.plane(p)is not None], 'first_layer':first,'first_base_connected_trunk_ring':trunk_first,'tree_family_candidate_definition':'half the smaller of actual first positive mesh layer and first base-connected trunk ring; intentionally no looser than existing pine method','height':float(np.ptp(v[:,1])),'max_y':float(v[:,1].max()),'raw_vertex_sha256':digest(v),'indexed_faces_sha256':digest(tri),'proxy_get_faces_sha256':digest(proxy)if proxy is not None else None,'foot_polygon_count':len(polys),'path':str(path.relative_to(R))}
  pins[str(path.relative_to(R))]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
 return out,pins

class Terrain:
 def __init__(self,tri,labels):
  self.tri=np.asarray(tri,float);self.labels=labels;self.xz=self.tri[:,:,[0,2]];self.lo=self.xz.min(1);self.hi=self.xz.max(1);self.planes=np.array([fg.plane(t)for t in self.tri]);require(self.planes.shape==(len(tri),3),'heightfield planes');self.grid=collections.defaultdict(set)
  for i in range(len(tri)):
   for x in range(math.floor(self.lo[i,0]/32),math.floor(self.hi[i,0]/32)+1):
    for z in range(math.floor(self.lo[i,1]/32),math.floor(self.hi[i,1]/32)+1):self.grid[x,z].add(i)
 def possible(self,lo,hi):
  ids=set()
  for x in range(math.floor(lo[0]/32),math.floor(hi[0]/32)+1):
   for z in range(math.floor(lo[1]/32),math.floor(hi[1]/32)+1):ids.update(self.grid[x,z])
  return [i for i in sorted(ids)if np.all(self.lo[i]<=hi+1e-7) and np.all(self.hi[i]>=lo-1e-7)]
 def height(self,x,z):
  for i in self.possible(np.array([x,z]),np.array([x,z])):
   t=self.xz[i];a,b,c=t;den=cross2(b-a,c-a);u=cross2(np.array([x,z])-a,c-a)/den;v=cross2(b-a,np.array([x,z])-a)/den
   if min(u,v,1-u-v)>=-1e-8:return float(self.planes[i]@[x,z,1])
  raise ValueError('terrain root not covered')

def terrains():
 source=read(SURVEY);patch=read(PREP/'candidate-vertex-y.json');over={r['tile']:{tuple(p['before_xyz']):p['candidate_y']for p in r['vertex_y_overrides']}for r in patch['tiles']};old=[];new=[];collision=[];labels=[];records=[]
 for name in TARGETS:
  tile=next(t for t in source['terrain']if t['node'].endswith('/'+name));a=np.array(tile['faces'],float).reshape(-1,3,3);b=a.copy();c=np.array(next(t for t in source['collision']if '/'+name+'/'in t['node'])['faces'],float).reshape(-1,3,3)
  require(c.shape==a.shape,'same collision corner count')
  for tr in b:
   for v in tr:
    if tuple(v)in over.get(name,{}):v[1]=over[name][tuple(v)]
  old.extend(a);new.extend(b);collision.extend(c);labels.extend([[name,i]for i in range(len(a))]);records.append({'tile':name,'source_visual_collision_max_component_difference_m':float(np.max(abs(a-c))),'source_visual_collision_bit_identical':digest(a)==digest(c),'candidate_collision_status':'not authored; nominal common-surface target only, not native collision proof'})
 oldterrain=Terrain(old,labels);newterrain=Terrain(new,labels);newterrain.changed=np.any(oldterrain.tri!=newterrain.tri,axis=(1,2));return oldterrain,newterrain,Terrain(collision,labels),records

def feet(row,polys,terrain,keep_samples=False):
 lo=math.inf;hi=-math.inf;lower=None;upper=None;pieces=0;vertices=0;all_samples=[];coverage=[];changed_pieces=0;unchanged_pieces=0
 for pi,poly in enumerate(polys):
  world=affine(row,poly);pp=fg.plane(world);require(pp is not None,'vertical foot not supported');xz=world[:,[0,2]];covered=0.
  for i in terrain.possible(xz.min(0),xz.max(0)):
   overlap=fg.clip2(xz,terrain.xz[i])
   if len(overlap)<3:continue
   ar=area2(overlap)
   if ar<1e-9:continue
   covered+=ar;pieces+=1;vertices+=len(overlap)
   if hasattr(terrain,'changed'):
    if terrain.changed[i]:changed_pieces+=1
    else:unchanged_pieces+=1
   coords=np.column_stack([overlap,np.ones(len(overlap))]);fy=coords@pp;gy=coords@terrain.planes[i];delta=gy-fy
   for k,val in enumerate(delta):
    witness={'foot_polygon':pi,'terrain_triangle':terrain.labels[i],'xz':overlap[k].tolist(),'old_foot_y':float(fy[k]),'terrain_y':float(gy[k]),'terrain_minus_old_foot_y':float(val)}
    if val<lo:lo=float(val);lower=witness
    if val>hi:hi=float(val);upper=witness
    if keep_samples:all_samples.append(witness)
  full=area2(xz);require(abs(covered-full)<max(.00001,full*.00001),'continuous foot coverage');coverage.append({'polygon':pi,'area_m2':full,'covered_area_m2':covered})
 require(math.isfinite(lo)and math.isfinite(hi),'empty foot')
 result={'min_d':lo,'max_d':hi,'range_m':hi-lo,'min_witness':lower,'max_witness':upper,'intersection_pieces':pieces,'intersection_vertices':vertices,'coverage':coverage,'changed_terrain_pieces':changed_pieces,'unchanged_terrain_pieces':unchanged_pieces}
 if keep_samples:result['samples']=all_samples
 return result

def exposure_pieces(row,model,terrain):
 triangles=affine(row,model['tri'].reshape(-1,3)).reshape(-1,3,3);total=0.;covered=0.;out=[]
 for tri in triangles:
  total+=vg.area3(tri);xz=tri[:,[0,2]]
  for i in terrain.possible(xz.min(0),xz.max(0)):
   t=terrain.xz[i];sign=np.sign(sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(t,np.roll(t,-1,axis=0))));poly=tri.copy()
   for a,b in zip(t,np.roll(t,-1,axis=0)):
    edge=b-a;poly=vg.clip3(poly,np.array([-edge[1],0,edge[0]])*sign,(edge[1]*a[0]-edge[0]*a[1])*sign)
    if len(poly)<3:break
   if len(poly)<3:continue
   ar=vg.area3(poly)
   if ar<1e-10:continue
   covered+=ar;out.append((poly,terrain.planes[i]))
 require(abs(covered-total)<max(.001,total*.00001),'entire visual mesh coverage')
 return out,total

def exposure(pieces,total,dy,root_terrain):
 above=0.;max_y=-math.inf
 for poly,ground in pieces:
  p=poly.copy();p[:,1]+=dy;p=vg.clip3(p,np.array([-ground[0],1,-ground[1]]),-ground[2]);ar=vg.area3(p)
  if ar>1e-10:above+=ar;max_y=max(max_y,float(p[:,1].max()))
 return {'surface_area_total_m2':total,'surface_area_above_m2':above,'surface_fraction_above':above/total,'top_clearance_at_root_m':max_y-root_terrain if math.isfinite(max_y) else 0.}

def in_triangle(p,t):
 a,b,c=t;den=cross2(b-a,c-a);u=cross2(p-a,c-a)/den;v=cross2(b-a,p-a)/den;return min(u,v,1-u-v)>=-1e-10

def cap_triangle_max(tri,q,c,sy,r):
 """Analytic maximum q.u+c-sy*r+sy*sqrt(r*r-u.u) on triangle∩disk.
 Natural curved-cap air gaps are not constrained away. No sampling rays.
 """
 pts=[];un=r*q/math.sqrt(sy*sy+float(q@q))
 if in_triangle(un,tri):pts.append(un)
 for p in tri:
  if p@p<=r*r:pts.append(p)
 for p,end in zip(tri,np.roll(tri,-1,axis=0)):
  v=end-p;vv=float(v@v);t0=-float(p@v)/vv;near=p+t0*v;rr=r*r-float(near@near)
  if rr<0:continue
  radius=math.sqrt(rr/vv);left=max(0.,t0-radius);right=min(1.,t0+radius)
  if left>right:continue
  qv=float(q@v);stationary=t0+qv*math.sqrt(rr)/(math.sqrt(vv)*math.sqrt(qv*qv+sy*sy*vv));stationary=max(left,min(right,stationary));pts.extend([p+left*v,p+right*v,p+stationary*v])
 # Circle-boundary critical point handles a disk contained in the triangle.
 if np.linalg.norm(q)>0:
  cp=r*q/np.linalg.norm(q)
  if in_triangle(cp,tri):pts.append(cp)
 if not pts:return None
 vals=[float(q@u+c-sy*r+sy*math.sqrt(max(0.,r*r-float(u@u))))for u in pts];i=int(np.argmax(vals));return vals[i],pts[i]

def capsule(row,terrain):
 a=np.array(row['original_world_transform_columns'],float);B=a[:9].reshape(3,3).T;root=a[9:];require(np.array_equal(B[[0,2],1],[0.,0.])and np.array_equal(B[1,[0,2]],[0.,0.])and B[1,1]>0,'capsule profile only upright full affine');H=B[np.ix_([0,2],[0,2])];require(np.linalg.det(H)!=0,'capsule invertible XZ');inv=np.linalg.inv(H);sy=B[1,1];radius=float(np.float32(2.4));ext=radius*np.linalg.norm(H,axis=1);best=None
 # Coverage of the enclosing rectangle implies coverage of the curved disk.
 lo=root[[0,2]]-ext;hi=root[[0,2]]+ext;box=np.array([[lo[0],lo[1]],[hi[0],lo[1]],[hi[0],hi[1]],[lo[0],hi[1]]]);covered=0.
 for i in terrain.possible(lo,hi):
  clip=fg.clip2(box,terrain.xz[i])
  if len(clip)>=3:covered+=area2(clip)
 require(abs(covered-area2(box))<max(.00001,area2(box)*.00001),'capsule enclosing XZ coverage')
 for i in terrain.possible(root[[0,2]]-ext,root[[0,2]]+ext):
  local=(terrain.xz[i]-root[[0,2]])@inv.T;ground=terrain.planes[i];q=H.T@ground[:2];c=float(ground@[root[0],root[2],1])-root[1];hit=cap_triangle_max(local,q,c,sy,radius)
  if hit is not None and(best is None or hit[0]>best['max_d']):
   xz=H@hit[1]+root[[0,2]];best={'max_d':hit[0],'terrain_triangle':terrain.labels[i],'world_xz':xz.tolist(),'capsule_local_xz':hit[1].tolist()}
 require(best is not None,'capsule terrain missing')
 best.update({'radius_local_float32':radius,'height_local':11.,'center_y_local':5.5,'method':'analytic continuous lower ellipsoidal hemisphere from full source affine; natural curvature retained','runtime_physics_scaling_proved':False,'whole_capsule_projection_seated':False,'enclosing_rectangle_area_m2':area2(box),'enclosing_rectangle_terrain_covered_area_m2':covered})
 return best

def interval(row,model,foot,estimate,proxy=None):
 sy=float(row['original_world_transform_columns'][4]);require(sy>0,'positive vertical source scale');tree=row['class']in TREE
 layer=(model['first_layer']if row['class']=='pine'else min(model['first_layer'],model['first_base_connected_trunk_ring']))if tree else None
 bury=(layer*.5 if tree else model['height']*.5)*sy;extra=(layer*.5 if tree else model['max_y']/3)*sy
 lower=max(foot['max_d']-bury,estimate-extra);upper=foot['min_d']+fg.EPS
 if proxy is not None:lower=max(lower,proxy['max_d']-bury);upper=min(upper,proxy['min_d']+fg.EPS)
 return {'lower_y_translation_m':lower,'upper_y_translation_m':upper,'empty':lower>upper,'max_burial_m':bury,'max_extra_seat_m':extra,'air_gap_gate_m':fg.EPS,'inherited_rounding_seat_pad_m':fg.SEAT_PAD,'scope':'continuous visual and rock proxy lower polygons on nominal candidate surface; tree capsule handled separately','policy_status':'original57B/61 numeric limits'if row['class']in ['pine','rock','bush']else 'new conservative tree-family candidate tied to actual oak/poplar geometry; not a historical species-specific acceptance'}

def neighbor_list(row,rows,box):
 out=[]
 for r in rows:
  if(r['path'],r['index'])==(row['path'],row['index']):continue
  b=r['original_combined_bounds']
  if b['min'][0]<=box[1]and b['max'][0]>=box[0]and b['min'][2]<=box[3]and b['max'][2]>=box[2]:out.append({'path':r['path'],'index':r['index'],'protected_neighbor':r['protected_neighbor'],'original_action':r['action']})
 return out

def alternative(row,rows,foot,iv,plan):
 b=row['original_combined_bounds'];box=[b['min'][0]-8,b['max'][0]+8,b['min'][2]-8,b['max'][2]+8];need=max(0.,iv['lower_y_translation_m']-iv['upper_y_translation_m']);poly=np.array(plan['polygon_xz']);corners=np.array([[box[0],box[2]],[box[1],box[2]],[box[1],box[3]],[box[0],box[3]]]);inside=all(all(cross2(q-p,x-p)>=0 for p,q in zip(poly,np.roll(poly,-1,axis=0)))for x in corners)
 dy=(iv['lower_y_translation_m']+iv['upper_y_translation_m'])/2
 witness_edits=[]
 for label,w,target in [('low',foot['min_witness'],foot['min_witness']['old_foot_y']+dy-fg.EPS),('high',foot['max_witness'],foot['max_witness']['old_foot_y']+dy+iv['max_burial_m'])]:
  witness_edits.append({'constraint':label,'triangle':w['terrain_triangle'],'world_xz':w['xz'],'candidate_y':w['terrain_y'],'proposed_required_bound_y':target,'required_delta_at_witness_m':max(0.,target-w['terrain_y'])if label=='low'else min(0.,target-w['terrain_y'])})
 return {'type':'per-index bounded bench witness proposal; not a feasible surface or executed edit','proposed_dy_for_witnesses_m':dy,'exact_witness_constraints':witness_edits,'witness_changes_within_2m':all(abs(w['required_delta_at_witness_m'])<=2 for w in witness_edits),'exact_path':row['path'],'index':row['index'],'maximum_allowed_abs_height_change_m':2.,'maximum_collar_m':8.,'proposed_max_domain_box_xz':box,'domain_inside_ridge_polygon':inside,'necessary_half_interval_deficit_m':need/2,'height_limit_necessary_condition':need<=4.,'not_sufficient_because':['Vertex-level collar/protection/seam continuity not designed','Capsule lower-shell and visible-area limits must also pass','Full changed-neighbor continuous support must be recomputed','Exact candidate collision surface/readback unavailable'],'must_recheck_neighbors':neighbor_list(row,rows,box),'must_preserve':['all source coast56/coast61 instances and resources','all frozen low-floor and 80m wet guards','all original XZ/topology and unmodified source values','cloud 40m margin and original seam preservation'],'executed':False,'approved':False}

def solve():
 require(sha(PREP/'FINAL_SHA256.json')==FREEZE,'frozen preparation identity');freeze=read(PREP/'FINAL_SHA256.json')['files']
 for fn,pin in freeze.items():require((PREP/fn).stat().st_size==pin['bytes']and sha(PREP/fn)==pin['sha256'],'frozen preparation '+fn)
 plan=read(PREP/'candidate-plan.json')
 for p in [SURVEY,E/'native-proxy-meshes.json',E/'wrapper-report.json']:check_pin(p,plan['source_pins'][str(p.relative_to(R))])
 require(fg.EPS==.001 and fg.SEAT_PAD==.002,'unchanged inherited EPS/pad')
 allrows=read(PREP/'instance-support-plan.json')['rows'];rows=[r for r in allrows if r['intersected_changed_triangles']]
 require(len(allrows)==676 and len(rows)==167 and collections.Counter(r['class']for r in rows)=={'rock':66,'pine':60,'oak':19,'bush':18,'poplar':4},'exact 167 scope')
 native=read(E/'native-proxy-meshes.json');wrapper=read(E/'wrapper-report.json');require(wrapper['passed']and wrapper['native_report_sha256']==sha(E/'native-proxy-meshes.json'),'v4 native identity')
 mapping=read(D.parent/'build-v1/offline-mapping/mapping-summary.json');require(sha(D.parent/'build-v1/offline-mapping/mapping-summary.json')=='72b6d2d6ad1c7623d3a4e81a30c2daf20641d145f97a12605936998c1a36a371','actual four mesh mapping identity');require(all(x['survey_ordered_float32_match'] and x['float32_max_component_error_m']==0 for x in mapping['meshes']),'actual source corners match survey')
 model,pins=models(native)
 guardfile=R/'source-assets/north-ridge62-intake/proxy-bounds-v1/immutable-source-inputs.json';require(sha(guardfile)=='c30155bd55abaf153a3357b089988a45a65217545ffd4281dd337a61b9f1ef5a','original bounded source manifest');guard=read(guardfile)
 for p in sorted({P/r['resource'][6:].split('::')[0]for r in allrows}|{P/'scripts/open_world.gd'}):
  require(sha(p)==guard[str(p)],'original queried source resource identity '+str(p));pins[str(p.relative_to(R))]={'bytes':p.stat().st_size,'sha256':guard[str(p)]}
 before,after,oldcollision,terrainrecord=terrains();pins[str(SURVEY.relative_to(R))]={'bytes':SURVEY.stat().st_size,'sha256':sha(SURVEY)}
 inputs=[Path(__file__),guardfile,D.parent/'build-v1/offline-mapping/mapping-summary.json',D.parent/'build-v1/offline-mapping/FINAL_SHA256.json',PREP/'FINAL_SHA256.json',PREP/'candidate-plan.json',PREP/'candidate-vertex-y.json',PREP/'instance-support-plan.json',E/'native-proxy-meshes.json',E/'wrapper-report.json',Path(fg.__file__),Path(vg.__file__),Path(decoder62.__file__),R/'source-assets/coast61-integration/verify_runtime_feet61.py',R/'source-assets/coast57/revision-b/fit_scatter57b.py',P/'scripts/open_world.gd']
 for p in inputs:pins[str(p.relative_to(R))]={'bytes':p.stat().st_size,'sha256':sha(p)}
 output=[]
 for number,row in enumerate(rows):
  m=model[row['class']];root=row['original_world_transform_columns'][9:];oldroot=before.height(root[0],root[2]);newroot=after.height(root[0],root[2]);estimate=newroot-oldroot;f=feet(row,m['polys'],after);old=feet(row,m['polys'],before);oldc=feet(row,m['polys'],oldcollision);p=feet(row,m['proxy_polys'],after)if m['proxy_polys']is not None else None;iv=interval(row,m,f,estimate,p)
  cap=capsule(row,after)if row['class']in TREE else None;capold=capsule(row,before)if cap else None
  if cap:
   iv['lower_without_capsule_m']=iv['lower_y_translation_m'];iv['upper_without_capsule_m']=iv['upper_y_translation_m'];iv['lower_y_translation_m']=max(iv['lower_y_translation_m'],cap['max_d']-iv['max_burial_m']);iv['upper_y_translation_m']=min(iv['upper_y_translation_m'],cap['max_d']+fg.EPS);iv['empty']=iv['lower_y_translation_m']>iv['upper_y_translation_m'];iv['capsule_limit_status']='source-recipe diagnostic; same geometry-derived burial bound, natural gaps allowed; engine scaling/contact unobserved'
  blockers=[];selected=None;visibility=None
  if f['unchanged_terrain_pieces']>0:
   iv['before_unaffected_piece_preservation']=[iv['lower_y_translation_m'],iv['upper_y_translation_m']]
   iv['preserve_unchanged_foot_piece_gaps_requires_dy_zero']=True
   iv['lower_y_translation_m']=max(iv['lower_y_translation_m'],0.);iv['upper_y_translation_m']=min(iv['upper_y_translation_m'],0.);iv['empty']=iv['lower_y_translation_m']>iv['upper_y_translation_m']
  # Unchanged geometry under the actual foot need not inherit invented fresh support.
  exact_unchanged=f['changed_terrain_pieces']==0 and estimate==0. and (p is None or p['changed_terrain_pieces']==0) and (cap is None or abs(cap['max_d']-capold['max_d'])<=1e-10)
  if exact_unchanged:
   op,ot=exposure_pieces(row,m,before);npieces,nt=exposure_pieces(row,m,after);base=exposure(op,ot,0.,oldroot);current=exposure(npieces,nt,0.,newroot);ar=current['surface_area_above_m2']/base['surface_area_above_m2'];tr=current['top_clearance_at_root_m']/base['top_clearance_at_root_m'];area_limit=.95 if row['class']in TREE else .75;top_limit=.95 if row['class']in TREE else 2/3
   visibility={'before':base,'selected':current,'area_retention_ratio':ar,'top_clearance_retention_ratio':tr,'area_limit':area_limit,'top_limit':top_limit,'passed':ar>=area_limit and tr>=top_limit,'claim':'original foot/proxy conditions retained, not retrospectively repaired'}
   if visibility['passed']:selected=0.;status='preserve_exact_actual_foot_unchanged'
   else:status='blocked_visible_geometry_retention';blockers.append('Canopy/body exposure affected although the actual foot and source proxy support remain unchanged')
  elif iv['empty']:status='blocked_empty_y_interval';blockers.append('No pure-Y solution under stated continuous foot/extra-seat/source-capsule constraints')
  else:
   low=iv['lower_y_translation_m'];high=iv['upper_y_translation_m'];wanted=min(high,max(low,estimate-fg.SEAT_PAD));world_y=float(np.float32(root[1]+wanted));dy=world_y-root[1]
   if dy<low:world_y=float(np.nextafter(np.float32(root[1]+low),np.float32(math.inf)));dy=world_y-root[1]
   if dy>high:world_y=float(np.nextafter(np.float32(root[1]+high),np.float32(-math.inf)));dy=world_y-root[1]
   if not low<=dy<=high:status='blocked_no_float32_y_in_interval';blockers.append('No float32 world-Y value in analytical interval')
   else:
    op,ot=exposure_pieces(row,m,before);npieces,nt=exposure_pieces(row,m,after);base=exposure(op,ot,0.,oldroot);current=exposure(npieces,nt,dy,newroot);ar=current['surface_area_above_m2']/base['surface_area_above_m2'];tr=current['top_clearance_at_root_m']/base['top_clearance_at_root_m'];area_limit=.95 if row['class']in TREE else .75;top_limit=.95 if row['class']in TREE else 2/3
    if ar<area_limit or tr<top_limit:
     hiy=float(np.float32(root[1]+high));hiy=float(np.nextafter(np.float32(hiy),np.float32(-math.inf)))if hiy-root[1]>high else hiy;test=exposure(npieces,nt,hiy-root[1],newroot);ta=test['surface_area_above_m2']/base['surface_area_above_m2'];tt=test['top_clearance_at_root_m']/base['top_clearance_at_root_m']
     if ta>=area_limit and tt>=top_limit:dy=hiy-root[1];world_y=hiy;current=test;ar=ta;tr=tt
     else:blockers.append('Even highest permitted Y loses too much above-terrain surface area/top clearance')
    visibility={'before':base,'selected':current,'area_retention_ratio':ar,'top_clearance_retention_ratio':tr,'area_limit':area_limit,'top_limit':top_limit,'passed':ar>=area_limit and tr>=top_limit,'claim':'triangle surface area and top clearance, not occlusion or solid-volume visibility'}
    if visibility['passed']:selected=dy;status='conditional_source_y_candidate'
    else:status='blocked_visible_geometry_retention'
  if row['class']in ['oak','poplar']:iv['tree_family_extension']='new conservative candidate, requiring source/live views and continuous contact; not historical acceptance'
  result={'path':row['path'],'index':row['index'],'class':row['class'],'status':status,'original_world_transform_columns':row['original_world_transform_columns'],'source_buffer_sha256':row['source_buffer_sha256'],'source_resource':row['resource'],'root_support_delta_from_actual_triangles_m':estimate,'old_root_terrain_y':oldroot,'candidate_root_terrain_y':newroot,'visual_foot':f,'baseline_visual_foot':old,'baseline_collision_foot':oldc,'rock_proxy_foot_on_nominal_candidate':p,'capsule_candidate':cap,'capsule_baseline':capold,'interval':iv,'capsule_preservation_scope':'only the continuous worst lower-shell terrain-minus-cap metric is unchanged; not every natural cap gap'if status=='preserve_exact_actual_foot_unchanged'and cap is not None else None,'selected_dy_m':selected,'selected_world_y':root[1]+selected if selected is not None else None,'visible_geometry':visibility,'blockers':blockers,'basis_and_xz_preserved_in_proposal':True,'placement_written':False,'support_proved':False,'native_collision_surface_proved':False,'runtime_or_visual_acceptance':False}
  if selected is None:result['bounded_alternative']=alternative(row,allrows,f,iv,plan)
  else:
   b=row['original_combined_bounds'];result['overlapping_neighbors_requiring_native_recheck']=neighbor_list(row,allrows,[b['min'][0],b['max'][0],b['min'][2],b['max'][2]])
  output.append(result)
  if(number+1)%20==0:print('solved',number+1,'of 167',file=sys.stderr,flush=True)
 require(all(sha(R/path)==v['sha256']for path,v in pins.items()),'inputs unchanged')
 keep=[{'path':r['path'],'index':r['index'],'original_row_sha256':hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'action':r['action'],'protected_neighbor':r['protected_neighbor']}for r in allrows if not r['intersected_changed_triangles']]
 require(len(keep)==509 and sum(bool(r['protected_neighbor'])for r in keep)==2,'keep exact')
 result={'status':'source_only_finite_continuous_support_presolve','engine_invoked':False,'world_or_assets_changed':False,'placement_buffer_written':False,'all_167_support_proved':False,'input_pins':pins,'source_models':{k:{x:v for x,v in m.items()if x not in ['tri','polys','proxy_polys']}for k,m in model.items()},'source_terrain_collision_records':terrainrecord,'counts':dict(collections.Counter(r['status']for r in output)),'per_class':{k:dict(collections.Counter(r['status']for r in output if r['class']==k))for k in model},'rows':output,'exact_keep_509':keep,'other_saved_instances_minimum_kept':57630,'protected_full_instance_counts':{'coast56':243,'coast61':81},'zero_deletions':True,'limits':['Candidate collision transfer/native readback not yet authored or executed; all proposed collider checks use nominal visual candidate as explicit target','Capsule analysis is analytic source geometry, not Godot physics-server behavior under scaling','Geometry predicates use float64 evaluation of the original saved float32 affine; actual per-vertex engine rounding/contact requires native readback','Oak/poplar geometry measured but inherited accepted species policy absent','No bench or relocation applied; no world mutation, new engine, image, GLB, Git or Slack','All 509 query keeps and all original unhit slots are immutable; no source buffer rewritten','Full renderer visual, runtime support/clearance and protected-neighbor readback remain required']}
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r=solve()
 if a.write:(D/'support-results.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
 print(json.dumps({k:r[k]for k in ['status','counts','per_class','all_167_support_proved','zero_deletions']}))
if __name__=='__main__':main()
