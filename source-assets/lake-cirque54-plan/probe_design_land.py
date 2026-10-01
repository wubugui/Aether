import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/scratch/a29d03198654/Aether';D=R+'/source-assets/lake-cirque54-plan';base=json.load(open(R+'/source-assets/lake-rim53/base51b.json'));west=json.load(open(R+'/source-assets/lake-rim53/integration-west53/integration-payload.json'))
items={name:m['faces'] for name,m in base['meshes'].items() if name!='massif_west_spur'}
for c in west['mountains'][0]['components']:items['west53/'+c['name']]=c['vertices']
trees={n:BVHTree.FromPolygons(list(map(Vector,f)),[(i,i+1,i+2) for i in range(0,len(f),3)],all_triangles=True) for n,f in items.items()}
rows=[]
for z in [-2220,-2140,-2070,-2020,-1960,-1880,-1800,-1720,-1640,-1560,-1480]:
 for x in [540,620,700,740,780,820,860,900,940,980]:
  hits=[]
  for n,t in trees.items():
   p,_,_,_=t.ray_cast(Vector((x,1500,z)),Vector((0,-1,0)),3000)
   if p:hits.append((p.y,n))
  h,n=max(hits) if hits else (None,None);rows.append({'x':x,'z':z,'actual_highest_y':h,'owner':n})
json.dump({'source_authority':'Saved53west changes are applied to real51b intake; unchanged cirque/neighbor geometry proven by full native audit. Planning support samples only; complete current-scene intake and full-world building rays remain required before sculpt/integration.','rows':rows},open(D+'/design-ground-samples.json','w'),indent=2)
for row in rows:
 if row['x'] in [700,740,780,820,900,940] and row['z'] in [-2140,-2070,-2020,-1960,-1880,-1800,-1720,-1640]:print(row)

plan=json.load(open(D+'/projection-options.json'));anchors=[]
for label,entry in plan['landmark_projections'].items():
 if label.startswith(('gully_','recommended_','low_saddle','lower_lake')):
  x,y,z=entry['world'];hits=[]
  for name,t in trees.items():
   hit,_,_,_=t.ray_cast(Vector((x,1500,z)),Vector((0,-1,0)),3000)
   if hit:hits.append((hit.y,name))
  height,owner=max(hits);anchors.append({'name':label,'world':entry['world'],'actual_baseline_highest':height,'owner':owner,'minimum_additive_visible_surface_y':height+2,'initial_target_below_current_surface':y<height})
json.dump(anchors,open(D+'/control-point-support.json','w'),indent=2)
print('CONTROL_POINTS',anchors)
