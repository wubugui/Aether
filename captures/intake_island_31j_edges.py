from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[1]
e=json.loads((R/'captures/lantern_island_study_31i/geometry-evidence.json').read_text());m=e['new']['island_c grass and exposed rock terrain'];v=np.array(m['vertices']);f=np.array(m['polygons']);ts=v[f]
splits=json.loads((R/'captures/lantern_island_study_31i/reform-plan.json').read_text())['actual_band_split_points']
new=[]
for a in splits:
 i=int(np.argmin(np.linalg.norm(v-a['after'],axis=1)));assert np.linalg.norm(v[i]-a['after'])<1e-6;new.append(i)
rows=[]
for name,edge in [('west shoulder back',[1108,1104]),('west shoulder front',new[:2]),('east shoulder back',[1109,1105]),('east shoulder front',new[2:])]:
 ids=np.flatnonzero(np.all(np.column_stack([np.any(f==i,axis=1) for i in edge]),axis=1));assert len(ids)==2
 normals=[];faces=[]
 for i in ids:
  t=ts[i];n=np.cross(t[1]-t[0],t[2]-t[0]);area=np.linalg.norm(n)/2;n/=np.linalg.norm(n);normals.append(n)
  faces.append(dict(face=int(i),vertices=f[i].tolist(),xyz=t.tolist(),normal=n.tolist(),area_m2=float(area),material=int(m['materials'][i])))
 rows.append(dict(name=name,edge=edge,xyz=v[edge].tolist(),length_m=float(np.linalg.norm(v[edge[0]]-v[edge[1]])),two_actual_faces=faces,normal_angle_deg=float(np.degrees(np.arccos(np.clip(np.dot(*normals),-1,1))))))
out=dict(scope='Actual31i rear shoulder front/back edges and adjacent final triangles.31j planning intake only; no31j source or proposed displacement. Angles are actual local normal changes, not visual acceptance.',new_split_point_indices=new,edges=rows)
p=R/'captures/island-31j-edge-intake.json';assert not p.exists();p.write_text(json.dumps(out,indent=2))
print(json.dumps([{k:x for k,x in a.items() if k!='two_actual_faces'} for a in rows],indent=2))
