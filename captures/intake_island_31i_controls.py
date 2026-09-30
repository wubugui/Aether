from pathlib import Path
import json, numpy as np
R=Path(__file__).resolve().parents[1]
P=R/'captures/lantern_island_study_31h';e=json.loads((P/'geometry-evidence.json').read_text());plan=json.loads((P/'reform-plan.json').read_text())
m=e['new']['island_c grass and exposed rock terrain'];v=np.array(m['vertices']);f=np.array(m['polygons']);ts=v[f]
rows=[]
for a in plan['controls']:
 i=int(np.argmin(np.linalg.norm(v-a['xyz'],axis=1)));assert np.linalg.norm(v[i]-a['xyz'])<1e-5
 one=np.flatnonzero(np.any(f==i,axis=1));neighbors=sorted(set(f[one].ravel().tolist())-{i})
 faces=[]
 for j in one:
  t=ts[j];normal=np.cross(t[1]-t[0],t[2]-t[0]);area=np.linalg.norm(normal)/2;normal/=np.linalg.norm(normal)
  faces.append(dict(face=int(j),vertices=f[j].tolist(),area_m2=float(area),normal=normal.tolist(),material=int(m['materials'][j])))
 rows.append(dict(name=a['name'],actual31h_vertex=i,xyz=v[i].tolist(),original31g_control_uv=a['uv'],neighbors=[dict(index=j,xyz=v[j].tolist()) for j in neighbors],one_ring=faces))
out=dict(scope='Actual31h8 editable patch controls and complete one-rings for next local form edit. Intake only, no31i model or visual claim. Boundary remains fixed in31h; future displaced faces require new support/self-intersection checks.',source='captures/lantern_island_study_31h/island_c.blend',controls=rows,design_intent='Keep removed rear seam; develop an asymmetrical short high shoulder and lower opposite return with a broad blunt root, not a continuous planar apron. Material correction alone has not accepted the form.')
p=R/'captures/island-31i-control-intake.json';assert not p.exists();p.write_text(json.dumps(out,indent=2))
print(json.dumps([dict(name=a['name'],vertex=a['actual31h_vertex'],xyz=a['xyz'],faces=len(a['one_ring'])) for a in rows],indent=2))
