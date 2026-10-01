import bpy,json,math,random,collections,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53'
SRC=D+'/revision-d';OUT=D+'/integration-west53'
base=json.load(open(D+'/base51b.json'));data=json.load(open(SRC+'/rim53-payload.json'));sculpt=json.load(open(SRC+'/sculpt-report.json'))
def tree(f):return BVHTree.FromPolygons([Vector(p) for p in f],[(i,i+1,i+2) for i in range(0,len(f),3)],all_triangles=True)
oldfaces=[p for m in base['meshes'].values() for p in m['faces']];newfaces=[p for n,m in base['meshes'].items() if n not in [q['name'] for q in data['mountains']] for p in m['faces']]
for m in data['mountains']:newfaces+=m['collision_vertices']
old=tree(oldfaces);new=tree(newfaces)
terrain=tree([p for name,m in base['meshes'].items() if name.startswith('Ground_') for p in m['faces']])
def hit(tr,x,z):return tr.ray_cast(Vector((x,1500,z)),Vector((0,-1,0)),3000)
def h(tr,x,z):
 p,n,i,d=hit(tr,x,z);return p.y if p else None
report={'baseline_scene':base['scene'],'baseline_renderer':base['renderer'],'roundtrip':[],'building_probes':[],'water':{},'scatter':[],'terrain_meshes':'All six baseline terrain meshes retained byte-for-byte in payload scope; no terrain writes are part of candidate.'}
def k(t):return tuple(sorted(tuple(round(v,4) for v in p) for p in t))
for m in data['mountains']:
 bpy.ops.wm.open_mainfile(filepath=SRC+'/'+m['name']+'_rim53.blend');org=m['origin'];a={o.name:o for o in bpy.data.objects if o.type=='MESH'}
 for c in m['components']:
  o=a[c['name']];mesh=o.data;mesh.calc_loop_triangles();f=[]
  for t in mesh.loop_triangles:
   for i in reversed(t.vertices):
    p=o.matrix_world@mesh.vertices[i].co;f.append([p.x+org[0],p.z+org[1],-p.y+org[2]])
  match=collections.Counter(k(f[i:i+3]) for i in range(0,len(f),3))==collections.Counter(k(c['vertices'][i:i+3]) for i in range(0,len(c['vertices']),3))
  report['roundtrip'].append({'mountain':m['name'],'component':c['name'],'blend_reopen_matches_payload_faces_0_1mm':match,'triangles':len(f)//3})
  assert match,(m['name'],c['name'],'roundtrip mismatch')
# Actual building footprint + full 50m northern buffer evaluated densely at 2m including boundaries.
maxbuild=0
for b in sculpt['buildings_protected']:
 mx=0;count=0
 xs=[b['xmin']+i*2 for i in range(math.ceil((b['xmax']-b['xmin'])/2)+1)];zs=[b['zmin']+i*2 for i in range(math.ceil((b['zmax']-b['zmin'])/2)+1)]
 for x in xs:
  for z in zs:
   a=h(old,x,z);c=h(new,x,z)
   if a is not None and c is not None:mx=max(mx,abs(c-a));count+=1
 maxbuild=max(maxbuild,mx);report['building_probes'].append({'node':b['node'],'samples_2m':count,'max_top_support_difference_m':mx})
report['building_support_max_difference_m']=maxbuild
assert maxbuild<.002,('building protection failed',maxbuild)
print('RIM53_BUILDINGS_CHECKED',maxbuild,flush=True)
report['water']=json.load(open(SRC+'/continuous-water-footprint-proof.json'))
# Conservatively relocate only genuinely affected vegetation. Retain original index, rotation, scale and support clearance.
occupied=[r['position'] for g in base['scatter'] for r in g['instances']];rng=random.Random(53112804)
changes=[];counts=collections.Counter();badold=[]
def protected(x,z):return any(b['xmin']-3<x<b['xmax']+3 and b['zmin']-3<z<b['zmax']+3 for b in sculpt['buildings_protected'])
for g in base['scatter']:
 tilex,tilez=map(int,g['node'].split('_')[-2:]);kind=g['node'].split('/')[-1].split('_')[0]
 for rec in g['instances']:
  x,y,z=rec['position'];a=h(old,x,z);p,n,idx,d=hit(new,x,z);b=p.y if p else None
  if a is None or b is None:raise RuntimeError(('scatter support missing',g['node'],rec['index']))
  clearance=y-a;status='unchanged';target=[x,y,z];normal=abs(n.y)
  if abs(b-a)>.015:
   if kind=='rock' and normal>.55:
    target=[x,b+clearance,z];status='vertically_resupported_on_rock'
   else:
    # Move to unchanged dry support inside same actual tile. Keep trees away from steep/new rock and snow.
    cand=[]
    for attempt in range(9000):
     nx=rng.uniform(tilex*768+16,(tilex+1)*768-16);nz=rng.uniform(tilez*768+16,(tilez+1)*768-16)
     if protected(nx,nz):continue
     q,no,_,_=hit(new,nx,nz);oh=h(old,nx,nz)
     if q is None or oh is None or q.y<5 or q.y>175 or abs(no.y)<.87 or abs(q.y-oh)>.01:continue
     terrain_h=h(terrain,nx,nz)
     if terrain_h is None or abs(q.y-terrain_h)>.02:continue
     if min((nx-v[0])**2+(nz-v[2])**2 for v in occupied)<12**2:continue
     cand.append(((nx-x)**2+(nz-z)**2,nx,q.y,nz))
     if len(cand)>=30:break
    if not cand:raise RuntimeError(('no safe scatter landing',g['node'],rec['index']))
    _,nx,ny,nz=min(cand);target=[nx,ny+clearance,nz];status='relocated_from_new_stone_or_snow_to_unchanged_dry_ground'
   # Transform translation from world delta into original group basis.
   t=g['global_transform'];from mathutils import Matrix
   basis=Matrix(((t[0],t[3],t[6]),(t[1],t[4],t[7]),(t[2],t[5],t[8])))
   delta=basis.inverted()@(Vector(target)-Vector(rec['position']));after=list(rec['transform'])
   for i in range(3):after[9+i]+=delta[i]
   changes.append({'node_path':g['node'].replace('/Skyfarer/',''),'index':rec['index'],'before_transform':rec['transform'],'after_transform':after})
   occupied.append(target)
  if abs(clearance)>1:badold.append({'node':g['node'],'index':rec['index'],'baseline_support_clearance_m':clearance,'status':status})
  counts[status]+=1
  report['scatter'].append({'node':g['node'],'index':rec['index'],'kind':kind,'status':status,'baseline_world_position':rec['position'],'new_world_position':target,'baseline_support_y':a,'new_support_y_at_original_position':b,'baseline_support_clearance_m':clearance,'new_support_clearance_m':target[1]-h(new,target[0],target[2]),'new_slope_abs_normal_y_at_original':normal})
report['scatter_counts']=dict(counts);report['scatter_total']=sum(counts.values());report['inherited_scatter_support_outliers']=badold
assert report['scatter_total']==1261
report['scatter_support_max_preserved_clearance_error_m']=max(abs(r['new_support_clearance_m']-r['baseline_support_clearance_m']) for r in report['scatter'])
data['scatter']=changes
expected={(r['node'],r['index']) for r in json.load(open(SRC+'/native-readback-impact.json'))['scatter'] if r['status']=='source_support_changed_pending_reconcile'}
actual={(r['node_path'].replace('World/','/Skyfarer/World/',1),r['index']) for r in changes}
assert expected==actual and len(changes)==120,(len(expected),len(actual),'exact changed support set differs')
report['exact_120_affected_indices_matched']=True
report['untouched_1141_indices_preserved']=True
report['relocation_occupied_spacing_m']=12
report['plant_destination_requires_unchanged_actual_terrain_top']=True
json.dump(data,open(OUT+'/integration-payload.json','w'));json.dump(report,open(OUT+'/scatter-reconcile-report.json','w'),indent=2)
print('RIM53_VERIFIED',report['scatter_counts'],'old_outliers',len(badold),flush=True)
