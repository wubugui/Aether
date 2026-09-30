"""Read-only ray diagnosis against exported geometry in the current study."""
import ast, json, math
from pathlib import Path
import numpy as np
root=Path('D:/test6')
syntax=ast.parse((root/'tools/verify_geology_assets.py').read_text())
reader={}
exec(compile(ast.Module(body=[n for n in syntax.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'GLB reader','exec'),reader)
camera=np.array([0.,145.,250.]);pitch=math.atan2(-4.,64.9);f=941/(2*math.tan(math.radians(25)))
geometry=[]
for item in json.loads((root/'assets/cliff_kit.json').read_text()):
    kind=item['name'];suffix={'cliff_front_columns':'prototype','cliff_shadow_buttress':'shadow_buttress'}.get(kind)
    path=root/'captures'/f'cliff_sections_10b_{suffix}.glb' if suffix else root/item['path']
    doc,t=reader['triangles'](path);t+=item['position'];geometry.append((kind,t))
for cx,cz in [(0,0),(0,-1)]:
    name=f'Ground_{cx}_{cz}';_,t=reader['triangles'](root/'assets/terrain'/(name+'.glb'))
    t+=np.array([cx*768,0,cz*768]);geometry.append((name,t))

def project(p):
    x,y,z=p-camera
    cy=math.cos(pitch)*y+math.sin(pitch)*z
    cz=-math.sin(pitch)*y+math.cos(pitch)*z
    return [round(836-f*x/cz,1),round(470.5+f*cy/cz,1)]

def hit(u,v):
    yy=(470.5-v)/f
    ray=np.array([(u-836)/f,math.cos(pitch)*yy+math.sin(pitch),math.sin(pitch)*yy-math.cos(pitch)])
    hits=[]
    for kind,t in geometry:
        e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];h=np.cross(ray,e2);a=np.einsum('ij,ij->i',e1,h)
        valid=abs(a)>1e-8;inv=np.zeros_like(a);inv[valid]=1/a[valid]
        s=camera-t[:,0];uu=inv*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1)
        vv=inv*(q@ray);depth=inv*np.einsum('ij,ij->i',e2,q)
        valid&=(uu>=0)&(vv>=0)&(uu+vv<=1)&(depth>0)
        if valid.any():
            ids=np.where(valid)[0];k=ids[np.argmin(depth[ids])]
            hits.append((float(depth[k]),kind,int(k),[project(p) for p in t[k]],(camera+ray*depth[k]).round(2).tolist()))
    return {'pixel':[u,v],'hits':sorted(hits)[:2]}

points=[(1000,900),(970,925),(1040,880),(1100,865),(1140,845),(1100,810),(1160,800),
        (1200,740),(1220,760),(1250,740),(1280,750),(1320,740),(1350,730),(1400,710)]
print(json.dumps([hit(*p) for p in points],indent=2))
