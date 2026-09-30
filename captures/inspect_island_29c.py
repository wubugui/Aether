from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[1];e=json.loads((R/'captures/lantern_island_study_29b/geometry-evidence.json').read_text())
t=e['new']['island_c grass and exposed rock terrain'];v=np.array(t['vertices']);n=len(v)//2;ts=[v[p] for p in t['polygons'] if max(p)<n]
def height(x,y):
 for q in ts:
  a,b,c=q;mat=np.array([b[:2]-a[:2],c[:2]-a[:2]]).T
  uv=np.linalg.solve(mat,np.array([x,y])-a[:2])
  if min(*uv,1-sum(uv))>=-1e-5:return float(a[2]+uv[0]*(b[2]-a[2])+uv[1]*(c[2]-a[2]))
for y in [-30,-25,-20,-17,-14,-10,-5,0,5,10]:
 print(y,[(x,round(height(x,y) or 0,2)) for x in [-20,-15,-10,-5,0,5,10,15,20,25]])
