from pathlib import Path
import json,struct,hashlib,math
import numpy as np
R=Path(r'E:\FeiTing');run=R/'captures/validation_runs/coast-environment-27b-20260908T145749Z-86704eae999c425590f3ff5cadced574'
s=json.loads((run/'images/night-reference.png.json').read_text());cam=s['camera'];rx,ry,rz=cam['rotation'];cx,sx=math.cos(rx),math.sin(rx);cy,sy=math.cos(ry),math.sin(ry)
rot=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
out=[]
for a in s['environment_study']['native_sky_assets']:
 if a['asset']=='moon':continue
 p=run/'study-inputs/new-environment27b/sky-assets'/(a['asset']+'.glb');blob=p.read_bytes();size=struct.unpack_from('<I',blob,12)[0];g=json.loads(blob[20:20+size]);raw=blob[28+size:]
 arr=[]
 for n in g['nodes']:
  if 'mesh' not in n:continue
  for pr in g['meshes'][n['mesh']]['primitives']:
   acc=g['accessors'][pr['attributes']['POSITION']];bv=g['bufferViews'][acc['bufferView']];off=bv.get('byteOffset',0)+acc.get('byteOffset',0);pts=np.frombuffer(raw,dtype='<f4',count=acc['count']*3,offset=off).reshape(-1,3).astype(float)
   assert 'matrix' not in n and 'rotation' not in n and 'translation' not in n and 'scale' not in n,n
   arr.append(pts)
 pts=np.concatenate(arr);c,t=math.cos(.35),math.sin(.35);r=np.array([[c,0,t],[0,1,0],[-t,0,c]])
 world=pts@r.T*a['scale']+a['position'];v=(world-cam['position'])@rot
 f=math.tan(math.radians(cam['fov']/2));px=836+v[:,0]/(-v[:,2]*f)*470.5;py=470.5-v[:,1]/(-v[:,2]*f)*470.5
 out.append({'asset':a['asset'],'position':a['position'],'projected_bounds':[float(px.min()),float(py.min()),float(px.max()),float(py.max())],'sha':hashlib.sha256(blob).hexdigest()})
print(json.dumps(out,indent=2));(R/'reviews/round-27b-cloud-screen-projection.json').write_text(json.dumps(out,indent=2))
