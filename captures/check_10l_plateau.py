"""Independent exported shell and contact-rim check against both real tiles."""
from pathlib import Path
import ast,json,hashlib,collections,numpy as np
from shapely.geometry import Polygon
from shapely import union_all
root=Path('D:/test6');source=root/'captures/cliff_sections_10l_eastern_plateau.glb'
syntax=ast.parse((root/'tools/verify_geology_assets.py').read_text());reader={}
exec(compile(ast.Module(body=[n for n in syntax.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'actual exported GLB','exec'),reader)
doc,t=reader['triangles'](source)
keymap={};ids=[]
for face in t:ids.append([keymap.setdefault(tuple(np.round(v,5)),len(keymap)) for v in face])
points=np.array(list(keymap));edges=collections.Counter(tuple(sorted((a,b))) for f in ids for a,b in zip(f,f[1:]+f[:1]))
n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(n,axis=1)*.5
volume=abs(float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6))
polys=[Polygon(tri[:,[0,2]]) for tri in t[n[:,1]>1e-6]]
overlap=sum(p.area for p in polys)-union_all(polys).area
contact_edges=set()
for f in ids:
    if not any(points[k,1]< -14 for k in f):continue
    above=[k for k in f if points[k,1]> -14]
    if len(above)==2:contact_edges.add(tuple(sorted(above)))
origin=next(i['position'] for i in json.loads((root/'assets/cliff_kit.json').read_text()) if i['name']=='cliff_eastern_plateau')
samples=[]
for a,b in contact_edges:
    aa,bb=points[a],points[b];count=max(2,int(np.ceil(np.linalg.norm((bb-aa)[[0,2]])/.5))+1)
    samples.extend(aa*(1-k)+bb*k+origin for k in np.linspace(0,1,count))
samples=np.array(samples);ground=[];tile_hashes={}
for cx,cz in [(0,0),(0,-1)]:
    path=root/'captures'/f'round-10d-Ground_{cx}_{cz}.glb';_,faces=reader['triangles'](path)
    faces+=np.array([cx*768,0,cz*768]);ground.append(faces);tile_hashes[path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
ground=np.concatenate(ground)
lo=samples[:,[0,2]].min(0)-1;hi=samples[:,[0,2]].max(0)+1
keep=(ground[:,:,[0,2]].min(1)<=hi).all(1)&(ground[:,:,[0,2]].max(1)>=lo).all(1)
a,b,c=ground[keep,0],ground[keep,1],ground[keep,2]
den=(b[:,2]-c[:,2])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,2]-c[:,2])
errors=[];misses=0
for p in samples:
    u=((b[:,2]-c[:,2])*(p[0]-c[:,0])+(c[:,0]-b[:,0])*(p[2]-c[:,2]))/den
    v=((c[:,2]-a[:,2])*(p[0]-c[:,0])+(a[:,0]-c[:,0])*(p[2]-c[:,2]))/den
    inside=(u>=-1e-5)&(v>=-1e-5)&(u+v<=1+1e-5)
    if not inside.any():misses+=1;continue
    height=(u*a[:,1]+v*b[:,1]+(1-u-v)*c[:,1])[inside].max()
    errors.append(float(p[1]-height))
bad_edges=sum(v!=2 for v in edges.values());deg=int((area<1e-8).sum())
report={'passed':bad_edges==0 and deg==0 and abs(overlap)<.001 and misses==0 and max(errors)<0,
        'glb_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'terrain_sha256':tile_hashes,
        'triangles':len(t),'bad_edges':bad_edges,'degenerate_faces':deg,'volume_m3':volume,'upper_projection_overlap_m2':overlap,
        'contact_edges':len(contact_edges),'contact_samples':len(samples),'misses':misses,
        'maximum_contact_above_ground_m':max(errors),'minimum_contact_above_ground_m':min(errors),
        'scope':'Exported mesh manifold, area, projected upper-surface overlap; every actual rim edge sampled at at most 0.5 m against the two study terrain GLBs. Not a full world/flight test.'}
(root/'captures/round-10l-plateau-geometry.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
raise SystemExit(0 if report['passed'] else 1)
