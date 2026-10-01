import json,numpy as np,os
D=os.path.dirname(__file__);p=json.load(open(D+'/lake49-payload.json'));q=json.load(open(D+'/../lake48/lake48-payload.json'));old={x['name']:x['vertices'] for x in q['meshes']}
for n,m in json.load(open(D+'/../lake48/support47.json'))['meshes'].items():
 if n not in old:old[n]=m['faces']
def shoreline(tris):
 out=[]
 for t in tris:
  pp=[]
  for a,b in zip(t,np.roll(t,-1,axis=0)):
   if (a[1]>0)!=(b[1]>0):pp.append((a+(b-a)*(-a[1]/(b[1]-a[1])))[[0,2]])
  if len(pp)==2:out.append(pp)
 return np.array(out)
shore=shoreline(np.concatenate([np.array(v).reshape(-1,3,3) for v in old.values()]))
def pseg(p,a,b):
 d=b-a;t=np.clip(((p-a)*d).sum(1)/(d*d).sum(1),0,1);return np.sqrt(((p-a-d*t[:,None])**2).sum(1))
out=[]
for s in p['islands']:
 land=shoreline(np.concatenate([np.array(m['vertices']).reshape(-1,3,3) for m in s['meshes'] if m['role'] in ['shoulder','wetshore','rockroot']]))
 best=1e9;record=None
 for a,b in land:
  for p in [a,b]:
   ds=pseg(p,shore[:,0],shore[:,1]);i=int(ds.argmin())
   if ds[i]<best:best=float(ds[i]);record={'island_waterline_xz':p.tolist(),'old_shore_segment':shore[i].tolist()}
  for p in shore.reshape(-1,2):
   ds=pseg(p,a[None,:],b[None,:]);d=float(ds[0])
   if d<best:best=d;record={'old_shore_xz':p.tolist(),'island_waterline_segment':[a.tolist(),b.tolist()]}
 out.append({'name':s['name'],'min_water_gap_to_existing48_shoreline_m':best,'closest':record})
json.dump({'method':'Exact triangle Y0 intersections, shortest endpoint-segment XZ distance; shores are disjoint','islands':out},open(D+'/shore-water-gaps.json','w'),indent=2);print(out)
