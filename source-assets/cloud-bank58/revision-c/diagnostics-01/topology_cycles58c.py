"""Exact triangulated tree-cotree H1 generators; diagnostic cycles, not repairs."""
import json,heapq,math
from pathlib import Path
from collections import defaultdict
import numpy as np
P=Path(__file__).resolve().parent;n=np.load(P/'full57-actual-triangles58c.npz');v=n['vertices'];f=n['indices'];edgefaces=defaultdict(list)
for i,t in enumerate(f):
 for a,b in [(t[0],t[1]),(t[1],t[2]),(t[2],t[0])]:edgefaces[tuple(sorted((int(a),int(b))))].append(i)
assert all(len(x)==2 for x in edgefaces.values());adj=defaultdict(list)
for a,b in edgefaces:
 length=float(np.linalg.norm(v[a]-v[b]));adj[a].append((b,length));adj[b].append((a,length))
outputs=[]
for point in [[4090,820,3990],[4370,780,2740],[3800,650,3500]]:
 root=int(np.linalg.norm(v-point,axis=1).argmin());dist=np.full(len(v),np.inf);dist[root]=0;parent=np.full(len(v),-1,dtype=int);heap=[(0,root)]
 while heap:
  d,a=heapq.heappop(heap)
  if d!=dist[a]:continue
  for b,w in adj[a]:
   nd=d+w
   if nd<dist[b]:dist[b]=nd;parent[b]=a;heapq.heappush(heap,(nd,b))
 primal={tuple(sorted((int(i),int(p)))) for i,p in enumerate(parent) if p>=0};dual=[]
 for edge,faces in edgefaces.items():
  if edge in primal:continue
  a,b=edge;weight=dist[a]+dist[b]+float(np.linalg.norm(v[a]-v[b]));dual.append((weight,edge,faces))
 dsu=list(range(len(f)))
 def find(a):
  while dsu[a]!=a:dsu[a]=dsu[dsu[a]];a=dsu[a]
  return a
 leftovers=[]
 for weight,edge,faces in sorted(dual,reverse=True):
  a,b=map(find,faces)
  if a!=b:dsu[a]=b
  else:leftovers.append(edge)
 assert len(leftovers)==4
 cycles=[]
 for a,b in leftovers:
  aa=[];x=a
  while x!=-1:aa.append(int(x));x=parent[x]
  amap={x:i for i,x in enumerate(aa)};bb=[];x=b
  while x not in amap:bb.append(int(x));x=parent[x]
  path=aa[:amap[x]+1]+bb[::-1];path.append(a);q=v[path]
  cycles.append(dict(vertex_ids=path,points_world=q.tolist(),length_m=float(np.linalg.norm(np.diff(q,axis=0),axis=1).sum()),world_bounds=[q.min(0).tolist(),q.max(0).tolist()]))
 outputs.append(dict(root_world=v[root].tolist(),cycles=cycles))
(P/'actual-topology-cycles58c.json').write_text(json.dumps(dict(basis_dimension=4,genus=2,root_trials=outputs,method='Actualstoredclosedorientabletriangles;shortestprimal spanningtree plus maximumweighteddual spanningtree. Four leftoveredges yieldH1fundamentalcyclebasis. Loops are surfacepaths around handles, not cavityfills or exact tunnelcentrelines.'),indent=2)+'\n')
for o in outputs:
 print('ROOT',o['root_world'])
 for c in o['cycles']:print('length',round(c['length_m'],2),'bounds',c['world_bounds'])
