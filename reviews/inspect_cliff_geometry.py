from pathlib import Path
import json,struct,collections,numpy as np
ROOT=Path('D:/test6')
def glb(path):
 d=Path(path).read_bytes();n=struct.unpack_from('<I',d,12)[0];j=json.loads(d[20:20+n]);o=20+n;l=struct.unpack_from('<I',d,o)[0];b=d[o+8:o+8+l]
 def acc(i):
  a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];typ={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];dim={'SCALAR':1,'VEC3':3,'VEC4':4,'VEC2':2}[a['type']];dt=np.dtype(typ);off=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',dt.itemsize*dim)
  return np.ndarray((a['count'],dim),dt,buffer=b,offset=off,strides=(stride,dt.itemsize)).copy()
 verts=[];tris=[]
 for m in j['meshes']:
  for p in m['primitives']:
   x=acc(p['attributes']['POSITION']).astype(float);i=acc(p['indices']).reshape(-1,3) if 'indices' in p else np.arange(len(x)).reshape(-1,3);tris.extend(x[i]);verts.extend(x)
 return j,np.asarray(verts),np.asarray(tris)
def crossings(t,x,z):
 a,b,c=t[:,0],t[:,1],t[:,2];den=(b[:,2]-c[:,2])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,2]-c[:,2]);good=np.abs(den)>1e-8
 den=np.where(good,den,1);u=((b[:,2]-c[:,2])*(x-c[:,0])+(c[:,0]-b[:,0])*(z-c[:,2]))/den;v=((c[:,2]-a[:,2])*(x-c[:,0])+(a[:,0]-c[:,0])*(z-c[:,2]))/den;w=1-u-v;inside=good&(u>=-1e-7)&(v>=-1e-7)&(w>=-1e-7)
 return (a[:,1]*u+b[:,1]*v+c[:,1]*w)[inside]
kit=json.loads((ROOT/'assets/cliff_kit.json').read_text());reports=[];world=[]
for item in kit:
 j,v,t=glb(ROOT/item['path']);key={};ids=[]
 for tri in t:
  it=[]
  for p in tri:
   k=tuple(np.round(p,5));it.append(key.setdefault(k,len(key)))
  ids.append(it)
 edges=collections.Counter(tuple(sorted((a,b))) for tr in ids for a,b in zip(tr,tr[1:]+tr[:1]));areas=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)*.5;volume=np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6
 reports.append({'name':item['name'],'mesh_triangles':len(t),'welded_vertices':len(key),'open_or_nonmanifold_edges':sum(n!=2 for n in edges.values()),'degenerate_faces':int((areas<1e-8).sum()),'signed_volume':float(volume),'volume_relative_error':abs(abs(volume)-item['volume_m3'])/item['volume_m3'],'images':len(j.get('images',[])),'nodes':j['nodes']})
 world.append(t+np.asarray(item['position']))
terrain=[]
for name in ['Ground_0_-1','Ground_0_0']:
 _,_,t=glb(ROOT/'assets/terrain'/f'{name}.glb');t+=np.array([0,0,-768 if name.endswith('_-1') else 0]);terrain.append(t)
terrain=np.concatenate(terrain);gaps=[]
for item,t in zip(kit,world):
 lo=t.min((0,1));hi=t.max((0,1))
 for x in np.linspace(lo[0],hi[0],14)[1:-1]:
  for z in np.linspace(lo[2],hi[2],14)[1:-1]:
   hits=crossings(t,x,z)
   if len(hits)<2:continue
   ground_hits=crossings(terrain,x,z);ground=max(0,float(ground_hits.max())) if len(ground_hits) else 0
   # Space below the lowest of all covering solid cliff modules.
   intervals=[crossings(other,x,z) for other in world];intervals=[ys for ys in intervals if len(ys)>1]
   bottom=min(float(ys.min()) for ys in intervals);top=max(float(ys.max()) for ys in intervals)
   if bottom-ground>9:
    gaps.append({'cliff':item['name'],'x':float(x),'z':float(z),'terrain_y':ground,'lowest_cliff_bottom':bottom,'highest_cliff_top':top,'gap':bottom-ground,'free_point_y':(ground+bottom)*.5})
gaps.sort(key=lambda p:-p['gap'])
result={'asset_checks':reports,'under_cliff_gap_candidates':gaps[:12],'candidate_count':len(gaps),'note':'Read-only numerical geometry review. Native node transforms listed for verification. Runtime ray validation still required.'}
(ROOT/'reviews/cliff-geometry-review.json').write_text(json.dumps(result,indent=2))
for r in reports:print(r['name'],'triangles',r['mesh_triangles'],'bad_edges',r['open_or_nonmanifold_edges'],'volume_rel_error',r['volume_relative_error'],'images',r['images'])
print('UNDER-CLIFF GAP CANDIDATES',len(gaps));print(json.dumps(gaps[:3],indent=2))
