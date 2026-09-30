"""Read-only ray inspection of which independent study massif is actually seen."""
from pathlib import Path
import ast,json,math,numpy as np
root=Path('D:/test6');syntax=ast.parse((root/'tools/verify_geology_assets.py').read_text());reader={}
exec(compile(ast.Module(body=[n for n in syntax.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'reader','exec'),reader)
geometry=[]
for item in json.loads((root/'assets/mountain_kit.json').read_text()):
 path=root/'captures/mountain_study_11g'/(item['name']+'.glb');_,t=reader['triangles'](path);t+=item['position'];geometry.append((item['name'],t))
camera=np.array([0.,145.,250.]);pitch=math.atan2(-4,64.9);f=941/(2*math.tan(math.radians(25)));rows=[]
for u,v in [(1235,318),(1250,330),(1260,350),(1270,370),(1280,390),(1250,400),(1235,380),(1215,360),(1215,395),(1280,420),(1240,430),(1200,420)]:
 yy=(470.5-v)/f;ray=np.array([(u-836)/f,math.cos(pitch)*yy+math.sin(pitch),math.sin(pitch)*yy-math.cos(pitch)]);hits=[]
 for name,t in geometry:
  e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];h=np.cross(ray,e2);a=np.einsum('ij,ij->i',e1,h);valid=abs(a)>1e-8;inv=np.zeros_like(a);inv[valid]=1/a[valid]
  s=camera-t[:,0];uu=inv*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);vv=inv*(q@ray);depth=inv*np.einsum('ij,ij->i',e2,q);valid&=(uu>=0)&(vv>=0)&(uu+vv<=1)&(depth>0)
  if not valid.any():continue
  ids=np.flatnonzero(valid);i=ids[np.argmin(depth[ids])];normal=np.cross(e1[i],e2[i]);normal/=np.linalg.norm(normal)
  hits.append({'name':name,'depth':float(depth[i]),'triangle':int(i),'position':(camera+ray*depth[i]).tolist(),'normal':normal.tolist()})
 rows.append({'pixel':[u,v],'hits':sorted(hits,key=lambda h:h['depth'])[:2]})
path=root/'captures/round-11g-visible-surfaces.json';assert not path.exists();path.write_text(json.dumps(rows,indent=2))
for row in rows:print(row['pixel'],row['hits'][0] if row['hits'] else 'no massif')
