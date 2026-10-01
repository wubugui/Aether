"""Realhorizontaltriangle slices and exactloop nesting,diagnosticonly."""
import json,os
from pathlib import Path
from collections import defaultdict
import numpy as np
from matplotlib.path import Path as PolyPath
P=Path(__file__).resolve().parent;n=np.load(P/'full57-actual-triangles58c.npz');tri=n['vertices'][n['indices']]

def contours(height):
 t=tri[(tri[:,:,1].min(1)<height)&(tri[:,:,1].max(1)>height)];segments=[]
 for q in t:
  pts=[]
  for i in range(3):
   a,b=q[i],q[(i+1)%3]
   if (a[1]-height)*(b[1]-height)<0:pts.append(a+(b-a)*((height-a[1])/(b[1]-a[1])))
  if len(pts)==2:segments.append(pts)
 points={};edges=[];links=defaultdict(list)
 for seg in segments:
  pair=[]
  for q in seg:
   key=tuple(np.round(q[[0,2]],5));points.setdefault(key,q[[0,2]]);pair.append(key)
  a,b=pair;links[a].append(b);links[b].append(a);edges.append((a,b))
 if any(len(v)!=2 for v in links.values()):return dict(height_y_m=height,invalid_node_degrees=True,loops=[])
 todo=set(links);loops=[]
 while todo:
  first=min(todo);current=first;previous=None;loop=[]
  while current in todo:
   todo.remove(current);loop.append(points[current]);nexts=links[current];nxt=nexts[0] if nexts[0]!=previous else nexts[1];previous,current=current,nxt
  if current!=first:raise RuntimeError('Slicechainnotclosed')
  q=np.array(loop);area=abs(float(np.sum(q[:,0]*np.roll(q[:,1],-1)-q[:,1]*np.roll(q[:,0],-1))*.5));loops.append(dict(points_xz=q.tolist(),absolute_area_m2=area))
 for i,r in enumerate(loops):
  q=np.array(r['points_xz']);probe=q[0];parents=[j for j,s in enumerate(loops) if j!=i and PolyPath(s['points_xz']).contains_point(probe)]
  r.update(nesting_depth=len(parents),air_hole=bool(len(parents)%2),xz_bounds=[q.min(0).tolist(),q.max(0).tolist()])
 return dict(height_y_m=height,invalid_node_degrees=False,loops=loops)
rows=[contours(float(y)+.123) for y in range(600,1001,5)];holes=[dict(height_y_m=r['height_y_m'],**s) for r in rows for s in r['loops'] if s['air_hole']]
(P/'horizontal-hole-sections58c.json').write_text(json.dumps(dict(rows=rows,hole_contours=holes,method='Actualtriangles intersect horizontalYplanes5mspacing+0.123 offset;loopnesting locates closedairholes inslices. Not acomplete topology classificationor fillplan.'),indent=2)+'\n')
print('Horizontalairholecontours',len(holes));print(json.dumps([{k:v for k,v in r.items() if k!='points_xz'} for r in holes],indent=2))
os.environ.setdefault('MPLCONFIGDIR','/tmp/feiting58c-matplotlib');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,axes=plt.subplots(2,3,figsize=(15,10))
for ax,y in zip(axes.ravel(),[700,750,800,825,850,900]):
 row=next(r for r in rows if abs(r['height_y_m']-(y+.123))<.01)
 for s in row['loops']:
  q=np.array(s['points_xz']);q=np.r_[q,q[:1]];ax.plot(q[:,0],q[:,1],c='#be4b37' if s['air_hole'] else'#476677',lw=1)
 ax.set_title('WorldY '+str(row['height_y_m'])+'m');ax.set_aspect('equal');ax.set_xlim(2550,5200);ax.set_ylim(2200,4750);ax.grid(alpha=.15)
fig.suptitle('ActualCgenus2union: horizontal contour nesting\nRed is an enclosedairloop inthissection, not arepairedmesh');fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(P/'horizontal-hole-sections58c.png',dpi=120);plt.close(fig)
