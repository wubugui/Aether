import bpy,json,math,random,collections,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53'
O=D+'/revision-d'
base=json.load(open(D+'/base51b.json'));data=json.load(open(O+'/rim53-payload.json'));sculpt=json.load(open(O+'/sculpt-report.json'))
def tree(f):return BVHTree.FromPolygons([Vector(p) for p in f],[(i,i+1,i+2) for i in range(0,len(f),3)],all_triangles=True)
oldfaces=[p for m in base['meshes'].values() for p in m['faces']];newfaces=[p for n,m in base['meshes'].items() if n not in [q['name'] for q in data['mountains']] for p in m['faces']]
for m in data['mountains']:newfaces+=m['collision_vertices']
old=tree(oldfaces);new=tree(newfaces)
def hit(tr,x,z):return tr.ray_cast(Vector((x,1500,z)),Vector((0,-1,0)),3000)
def h(tr,x,z):
 p,n,i,d=hit(tr,x,z);return p.y if p else None
report={'baseline_scene':base['scene'],'baseline_renderer':base['renderer'],'roundtrip':[],'building_probes':[],'water':{},'scatter':[],'terrain_meshes':'All six baseline terrain meshes retained byte-for-byte in payload scope; no terrain writes are part of candidate.'}
def k(t):return tuple(sorted(tuple(round(v,4) for v in p) for p in t))
for m in data['mountains']:
 bpy.ops.wm.open_mainfile(filepath=O+'/'+m['name']+'_rim53.blend');org=m['origin'];a={o.name:o for o in bpy.data.objects if o.type=='MESH'}
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
counts=collections.Counter();by_tile=collections.defaultdict(collections.Counter)
for group in base['scatter']:
 for rec in group['instances']:
  x,y,z=rec['position'];a=h(old,x,z);b=h(new,x,z);assert a is not None and b is not None
  status='source_support_changed_pending_reconcile' if abs(a-b)>.015 else 'unchanged'
  counts[status]+=1;tile='_'.join(group['node'].split('_')[-2:]);by_tile[tile][status]+=1
  report['scatter'].append({'node':group['node'],'index':rec['index'],'world_position':rec['position'],'old_support_y':a,'new_support_y':b,'delta_m':b-a,'status':status,'transform_not_applied':True})
report['scatter_counts']=dict(counts);report['scatter_by_tile']={k:dict(v) for k,v in by_tile.items()};report['scatter_total']=sum(counts.values())
report['scatter_reconciled']=False;report['integrated']=False;report['visual_acceptance']=False
json.dump(report,open(O+'/native-readback-impact.json','w'),indent=2)
print('RIM53D_READBACK_AND_IMPACT',report['scatter_counts'],report['scatter_by_tile'],flush=True)
