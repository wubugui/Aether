from pathlib import Path
import json, collections, math
import numpy as np
from shapely.geometry import Polygon, shape
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
e=json.loads((R/'captures/lantern_island_study_31f/geometry-evidence.json').read_text())
s=json.loads((R/'reviews/round-31g-support-intake.json').read_text())
m=e['new']['island_c grass and exposed rock terrain'];v=np.array(m['vertices']);f=np.array(m['polygons']);t=v[f];c=t.mean(axis=1)
support=unary_union([shape(s['road_geometry_geojson'])]+[Polygon(a['polygon']) for a in s['pads']]+[Polygon(a) for a in s['all14_actual_tree_footprints_xy']])
protected=set(i for i,x in enumerate(t) if np.cross(x[1]-x[0],x[2]-x[0])[2]>1e-8 and Polygon(x[:,:2]).intersection(support).area>1e-8)
def boundary(ids):
 edges=collections.Counter(tuple(sorted((int(a),int(b)))) for i in ids for a,b in zip(f[i],np.roll(f[i],-1)))
 adj=collections.defaultdict(list)
 for (a,b),n in edges.items():
  if n==1:adj[a].append(b);adj[b].append(a)
 if any(len(x)!=2 for x in adj.values()):return None,dict(collections.Counter(len(x) for x in adj.values()))
 unseen=set(adj);loops=[]
 while unseen:
  start=min(unseen);loop=[start];prev=-1;cur=start
  while True:
   nxt=next(x for x in adj[cur] if x!=prev)
   if nxt==start:break
   loop.append(nxt);prev,cur=cur,nxt
   if len(loop)>len(adj):raise RuntimeError('loop')
  unseen-=set(loop);loops.append(loop)
 return loops,None
out=[]
for mode,center,radii in [('main',[-5,9,5],[12,10,10]),('narrow',[-4,9,5],[9,8,8]),('broad',[-5,9,5],[15,12,11])]:
 ids=set(int(i) for i in np.flatnonzero(np.sum(((c-center)/radii)**2,axis=1)<1))-protected
 loops,bad=boundary(ids)
 row=dict(mode=mode,center=center,radii=radii,faces=sorted(ids),protected_count=len(protected),boundary=loops,bad=bad)
 if loops:
  row['projections']=[]
  for loop in loops:
   xyz=v[loop];projs={}
   for label,q in [('xy',xyz[:,:2]),('uz',np.column_stack(((xyz[:,0]+xyz[:,1])/math.sqrt(2),xyz[:,2])))]:
    p=Polygon(q);projs[label]=dict(valid=p.is_valid,area=p.area)
   row['projections'].append(dict(vertices=len(loop),bounds=[xyz.min(axis=0).tolist(),xyz.max(axis=0).tolist()],tests=projs))
 out.append(row)
p=R/'captures/island-31g-patch-intake.json';p.write_text(json.dumps(out,indent=2))
print(json.dumps([{k:x for k,x in a.items() if k not in ['faces','boundary']} for a in out],indent=2))
