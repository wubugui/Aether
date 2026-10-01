import json, re, hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
raw=json.loads((D/'native-coast.json').read_text())
terr={v['node'].split('/')[-1]:v for v in raw['terrain']}
tris={k:np.array(v['faces']).reshape(-1,3,3) for k,v in terr.items()}
cols={v['node'].split('/')[-3]:np.array(v['faces']).reshape(-1,3,3) for v in raw['collision']}
alltri=np.concatenate(list(tris.values()))
labels=np.concatenate([np.full(len(t),k) for k,t in tris.items()])
def ray(pos,direction,tri=alltri):
    e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0]
    h=np.cross(direction,e2);a=np.einsum('ij,ij->i',e1,h)
    f=np.divide(1,a,out=np.zeros_like(a),where=np.abs(a)>1e-9)
    s=pos-tri[:,0];u=f*np.einsum('ij,ij->i',s,h)
    q=np.cross(s,e1);v=f*np.einsum('j,ij->i',direction,q);t=f*np.einsum('ij,ij->i',e2,q)
    mask=(np.abs(a)>1e-9)&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(t>1e-5)
    idx=np.flatnonzero(mask)
    if not len(idx):return None
    i=idx[np.argmin(t[idx])];return i,(pos+direction*t[i])
def height(k,x,z):
    hit=ray(np.array([x,1500,z]),np.array([0,-1,0]),tris[k])
    return float(hit[1][1]) if hit else None
out={'mode':'Offline numerical analysis of raw saved surface arrays and collision arrays; no render or runtime claimed','source_sha256':raw['source_sha256'],'pixel_rays':[],'edge_profiles':{},'mesh_collision':{}}
c=np.array([-2600,330,-2350]);target=np.array([-2969,156,-3263]);f=(target-c);f=f/np.linalg.norm(f);r=np.cross(f,[0,1,0]);r=r/np.linalg.norm(r);u=np.cross(r,f)
for px,py in [(500,285),(520,360),(545,405),(564,452),(605,540),(630,620),(700,590),(850,580),(700,435),(650,390),(700,340)]:
    direction=f+(px/1180*2-1)*np.tan(np.radians(55)/2)*1180/664*r+(1-py/664*2)*np.tan(np.radians(55)/2)*u
    hit=ray(c,direction)
    out['pixel_rays'].append({'px':px,'py':py,'node':str(labels[hit[0]]) if hit else None,'point':hit[1].tolist() if hit else None})
for k in ['Ground_-4_-4','Ground_-4_-5','Ground_-5_-4','Ground_-5_-5','Ground_-5_-6','Ground_-4_-6']:
    a=tris[k];col=cols[k]
    out['mesh_collision'][k]={'surface_triangles':len(a),'collider_triangles':len(col),'ordered_max_abs_error':float(np.max(np.abs(a-col))) if a.shape==col.shape else None,'bounds':[a.min(axis=(0,1)).tolist(),a.max(axis=(0,1)).tolist()]}
for z in np.arange(-4200,-2200+1,100):
    row={}
    for x in [-3072.1,-3072,-3071.9,-3050,-3000,-2950,-2900,-2800,-2700,-2600]:
        k=f'Ground_{int(np.floor(x/768))}_{int(np.floor(z/768))}'
        if k in tris:row[str(x)]={"ground":k,"y":height(k,x,z)}
    out['edge_profiles'][str(z)]=row
(D/'analysis.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:out[k] for k in ['pixel_rays','mesh_collision']},indent=2))
print('edge profile x=-3072.1,-3071.9,-3000,-2900')
for z,row in out['edge_profiles'].items():print(z,[(x,round(row[x]['y'],3) if row[x]['y'] is not None else None) for x in ['-3072.1','-3071.9','-3000','-2900'] if x in row])
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection,LineCollection
fig,ax=plt.subplots(figsize=(12,11),dpi=150)
xy=alltri[:,:,[0,2]];h=alltri[:,:,1].mean(axis=1)
p=PolyCollection(xy,array=h,cmap='terrain',clim=(-10,180),edgecolors='none');ax.add_collection(p)
coast=[]
for tri in alltri:
 points=[]
 for a,b in zip(tri,np.roll(tri,-1,axis=0)):
  if (a[1]<=0<b[1]) or (b[1]<=0<a[1]):points.append((a+(b-a)*(-a[1]/(b[1]-a[1])))[[0,2]])
 if len(points)==2:coast.append(points)
ax.add_collection(LineCollection(coast,colors='cyan',linewidths=.7))
for x in range(-4608,-768+1,768):ax.axvline(x,color='black',linewidth=.5,alpha=.5)
for z in range(-5376,-1536+1,768):ax.axhline(z,color='black',linewidth=.5,alpha=.5)
for k,t in tris.items():
 center=t.mean(axis=(0,1))
 ax.text(center[0],center[2],k,ha='center',fontsize=6,color='black')
ax.plot(c[0],c[2],'r*',markersize=15,label='1131/1347 camera')
for hit in out['pixel_rays']:
 if hit['point']:
  pt=hit['point'];ax.plot([c[0],pt[0]],[c[2],pt[2]],color='red',alpha=.4,linewidth=.5);ax.text(pt[0],pt[2],str((hit['px'],hit['py'])),fontsize=6)
ax.set(xlim=(-3900,-1800),ylim=(-4650,-2000),xlabel='World X (m)',ylabel='World Z (m)',title='Saved53 coast geometry: sea level contour and tile grid')
ax.invert_yaxis();ax.set_aspect('equal');fig.colorbar(p,ax=ax,label='Height (m)');fig.tight_layout();fig.savefig(D/'native-coast-map.png')
