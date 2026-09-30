import bpy,json,random,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake48'
base=json.load(open(D+'/base47.json'));support=json.load(open(D+'/support47.json'))
payload=json.load(open(D+'/lake48-payload.json'));payload['scatter']=[]
report=json.load(open(D+'/sculpt-report.json'));report['scatter']=[]
def makebvh(f):return BVHTree.FromPolygons([Vector(v) for v in f],[(i,i+1,i+2) for i in range(0,len(f),3)],all_triangles=True)
def height(trees,x,z):
 hits=[t.ray_cast(Vector((x,1200,z)),Vector((0,-1,0)),2000)[0] for t in trees]
 return max((p.y for p in hits if p is not None),default=None)
oldbvhs={k:makebvh(v['faces']) for k,v in {**support['meshes'],**base['meshes']}.items()}
bvhs=dict(oldbvhs)
for m in payload['meshes']:bvhs[m['name']]=makebvh(m['vertices'])
# Move only affected tree/rock placements; dry untouched anchors retain exact bytes. Original index/rotation/scale retained.
occupied=[p['position'] for g in base['scatter'] for p in g['instances']];rng=random.Random(481128)
for group in base['scatter']:
 node=group['node'];tile='Ground_1_-3' if node.endswith('_1_-3') else 'Ground_1_-2';zmin=-2304 if tile.endswith('-3') else -1536
 for rec in group['instances']:
  x,y,z=rec['position'];old=height(list(oldbvhs.values()),x,z);new=height(list(bvhs.values()),x,z)
  if old is None or new is None:raise RuntimeError('support absent')
  if abs(new-old)<.015:continue
  target=(x,new,z);reason='resupported';clearance=y-old
  if abs(clearance)>1:raise RuntimeError(("unexpected original support offset",node,rec["index"],clearance))
  if new<3:
   candidates=[]
   for attempt in range(2200):
    nx=rng.uniform(796,1506);nz=rng.uniform(zmin+24,zmin+744);h=height(list(bvhs.values()),nx,nz)
    if h is None or h<5 or h>135:continue
    if min((nx-p[0])**2+(nz-p[2])**2 for p in occupied)<12**2:continue
    # Keep scatter spread over dry upland patches, not snapped to a shoreline contour.
    cost=(nx-x)**2+(nz-z)**2
    candidates.append((cost,nx,h,nz))
    if len(candidates)>=45:break
   if not candidates:raise RuntimeError(('no scatter landing',node,rec['index']))
   _,nx,h,nz=min(candidates);target=(nx,h,nz);reason='relocated_from_submerged_basin'
  before=rec['transform'];after=list(before);after[9:12]=[before[9]+target[0]-x,before[10]+target[1]+clearance-y,before[11]+target[2]-z];occupied.append(list(target))
  payload['scatter'].append({'node_path':node.replace('/Skyfarer/',''),'index':rec['index'],'before_transform':before,'after_transform':after})
  report['scatter'].append({'node':node,'index':rec['index'],'reason':reason,'old':rec['position'],'new':[target[0],target[1]+clearance,target[2]],'preserved_support_offset':clearance})
json.dump(payload,open(D+'/lake48-payload.json','w'));json.dump(report,open(D+'/sculpt-report.json','w'),indent=2)
print('LAKE48_SCULPT_DONE',len(payload['scatter']))
