"""Actualunion verticalairgaps,13mgrid. Samples localize;not completeholeproof."""
import json,sys,math,os
from pathlib import Path
from collections import defaultdict,deque
import numpy as np
P=Path(__file__).resolve().parent;R=P.parent/'recovery-01';sys.path.insert(0,str(R));from triangle_checks58c import vertical_hits
n=np.load(P/'full57-actual-triangles58c.npz');v=n['vertices'];f=n['indices'];tri=v[f];bin_size=52.;bins=defaultdict(list)
lo=tri[:,:,[0,2]].min(1);hi=tri[:,:,[0,2]].max(1)
for i,(a,b) in enumerate(zip(lo,hi)):
 for x in range(math.floor(a[0]/bin_size),math.floor(b[0]/bin_size)+1):
  for z in range(math.floor(a[1]/bin_size),math.floor(b[1]/bin_size)+1):bins[(x,z)].append(i)
xs=np.arange(math.floor(v[:,0].min()/13)*13,math.ceil(v[:,0].max()/13)*13+1,13.);zs=np.arange(math.floor(v[:,2].min()/13)*13,math.ceil(v[:,2].max()/13)*13+1,13.);gaps={};tested=0;errors=[]
for ix,x in enumerate(xs):
 for iz,z in enumerate(zs):
  ids=bins.get((math.floor(x/bin_size),math.floor(z/bin_size)),[])
  if not ids:continue
  hit=vertical_hits(tri[ids],[x,z]);tested+=1
  if hit['errors']:errors.append(dict(xz=[x,z],errors=hit['errors']))
  if len(hit['solid_intervals'])>1:
   intervals=hit['solid_intervals'];airs=[]
   for a,b in zip(intervals,intervals[1:]):airs.append(dict(top_y_m=a['bottom_y_m'],bottom_y_m=b['top_y_m'],height_m=a['bottom_y_m']-b['top_y_m']))
   for h in hit['hits']:h['triangle_ids']=[int(ids[j]) for j in h['triangle_ids']]
   gaps[(ix,iz)]=dict(world_xz=[float(x),float(z)],air_intervals=airs,actual_hits=hit['hits'])
todo=set(gaps);components=[]
while todo:
 first=todo.pop();q=[first];cells=[]
 while q:
  cell=q.pop();cells.append(cell)
  for d in [(1,0),(-1,0),(0,1),(0,-1)]:
   other=(cell[0]+d[0],cell[1]+d[1])
   if other in todo:todo.remove(other);q.append(other)
 rows=[gaps[c] for c in cells];points=np.array([r['world_xz'] for r in rows]);ys=[a[k] for r in rows for a in r['air_intervals'] for k in ['top_y_m','bottom_y_m']]
 components.append(dict(sample_count=len(rows),xz_bounds=[points.min(0).tolist(),points.max(0).tolist()],air_y_bounds=[min(ys),max(ys)],maximum_sampled_air_height_m=max(a['height_m'] for r in rows for a in r['air_intervals']),samples=rows))
components.sort(key=lambda r:-r['sample_count']);result=dict(actual_grid_spacing_m=13,tested_columns=tested,columns_with_more_than_one_solid_interval=len(gaps),sample_groups=components,ray_errors=errors,method='Actualfull57uniontriangles. Groupings use4neighborXZ13msamples;thislocatesoverhangair,not acontinuousglobaltunnelcount. Boundariesbetweenairgroupscanjoinbetweensamples.',geometry_repaired=False)
(P/'actual-airgap-locations58c.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['sample_groups','ray_errors']},indent=2));print(json.dumps([{k:v for k,v in c.items() if k!='samples'} for c in components],indent=2))
os.environ.setdefault('MPLCONFIGDIR','/tmp/feiting58c-matplotlib');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(11,9));ax.scatter(v[::10,0],v[::10,2],s=1,c='#bcc8cc',alpha=.5)
for i,c in enumerate(components):
 pts=np.array([r['world_xz'] for r in c['samples']]);ax.scatter(pts[:,0],pts[:,1],s=9);ax.text(pts[:,0].mean(),pts[:,1].mean(),str(i+1),fontsize=9,color='black')
ax.set_aspect('equal');ax.set_xlabel('WorldX m');ax.set_ylabel('WorldZ m');ax.set_title('ActualCunion: verticalairgap samplegroups13mgrid\nPotentialoverhangs/tunnels;groupcountisnotgenus');fig.tight_layout();fig.savefig(P/'actual-airgap-locations58c.png',dpi=120);plt.close(fig)
