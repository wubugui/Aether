from pathlib import Path
import json,math
import numpy as np
from shapely.geometry import Polygon,LineString
from shapely.validation import explain_validity
R=Path(__file__).resolve().parents[1];rows=[]
for variant in ['cut-patch','full-depth']:
 p=R/f'reviews/round-31g-{variant}-independent.json';r=json.loads(p.read_text());loop=r['loops'][0];v=np.array(loop['xyz']);q=np.array(loop['angle_radian_z']);snap=q.copy()
 for angle in [58,156]:snap[abs(np.degrees(snap[:,0])-angle)<.0001,0]=math.radians(angle)
 for z in [-1,-5.849999904632568,10.7]:snap[abs(snap[:,1]-z)<1e-5,1]=z
 sides=[]
 for angle in [58,156]:
  ix=np.flatnonzero(abs(np.degrees(q[:,0])-angle)<.0001);s=[]
  for j in ix:
   k=(j+1)%len(q)
   if k in ix:
    s.append({'indices':[loop['vertices'][j],loop['vertices'][k]],'z_pair':[q[j,1],q[k,1]],'radius_pair':np.linalg.norm(v[[j,k],:2],axis=1).tolist(),'signed_z_step':q[k,1]-q[j,1]})
  pos=[a for a in s if a['signed_z_step']>1e-5];neg=[a for a in s if a['signed_z_step']<-1e-5];backtrack=min(sum(x['signed_z_step'] for x in pos),-sum(x['signed_z_step'] for x in neg));sides.append({'angle_degrees':angle,'positive_height_steps':len(pos),'negative_height_steps':len(neg),'minority_direction_total_height_m':backtrack,'edges':s})
 po=Polygon(snap);row={'variant':variant,'original_boundary_valid':loop['valid_polygon'],'normalized_parameter_boundary_valid':po.is_valid,'normalized_parameter_validity':explain_validity(po),'normalization':'Only parameter diagnostic: angle within.0001deg snaps to58/156, z within1e-5m snaps tocutplane. No3D coordinates changed.','angular_sides':sides};rows.append(row);r['boundary_parameter_normalization_diagnostic']=row;p.write_text(json.dumps(r,indent=2),encoding='utf-8')
 md=R/f'reviews/round-31g-{variant}-independent.md';s=md.read_text(encoding='utf-8');s+='\n## 切面浮点与真实折返区分\n\n仅将参数值贴到原切平面（角差<0.0001°、高度差<10µm），不改3D点；参数多边形有效性为'+str(po.is_valid)+'（'+explain_validity(po)+'）。两角边的少数方向高程累积量分别为'+str([x['minority_direction_total_height_m'] for x in sides])+'m；这些记录可区分浮点抖动和沿角边真实高程折返。各实际边点号、高度与半径在JSON内。\n';md.write_text(s,encoding='utf-8')
(R/'reviews/round-31g-boundary-parameter-check.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps([{k:v for k,v in r.items() if k!='angular_sides'}|{'sides':[{k:v for k,v in a.items() if k!='edges'} for a in r['angular_sides']]} for r in rows],indent=2))
