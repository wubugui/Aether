from pathlib import Path
import json,numpy as np
R=Path(__file__).resolve().parents[1];report={}
for label in ['29b','29d']:
    e=json.loads((R/('captures/lantern_island_study_'+label+'/geometry-evidence.json')).read_text());t=e['new']['island_c grass and exposed rock terrain'];v=np.array(t['vertices']);nv=len(v)//2;pf=set(e['protected_face_indices']);pv=set(e['protected_vertex_indices']);rows=[]
    for i,p in enumerate(t['polygons']):
        if max(p)>=nv:continue
        q=v[p];normal=np.cross(q[1]-q[0],q[2]-q[0]);normal/=np.linalg.norm(normal)
        if q[:,2].mean()<=10 or normal[2]>=.5:continue
        rows.append({'face':i,'vertices':p,'protected_face':i in pf,'protected_vertices_count':sum(j in pv for j in p),'all_vertices_protected':all(j in pv for j in p),'xy_area_m2':float(abs(np.cross(q[1]-q[0],q[2]-q[0])[2])/2)})
    report[label]={'selected_faces':len(rows),'protected_faces':sum(r['protected_face'] for r in rows),'unprotected_faces':sum(not r['protected_face'] for r in rows),'unprotected_faces_all_vertices_protected':sum(not r['protected_face'] and r['all_vertices_protected'] for r in rows),'unprotected_faces_at_least_one_free_vertex':sum(not r['protected_face'] and not r['all_vertices_protected'] for r in rows),'all_vertices_protected_faces_total':sum(r['all_vertices_protected'] for r in rows),'unprotected_all_vertices_protected_indices':[r['face'] for r in rows if not r['protected_face'] and r['all_vertices_protected']],'rows':rows}
(R/'reviews/round-29d-independent-fixed-vertices.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:{a:b for a,b in v.items() if a!='rows'} for k,v in report.items()},indent=2))
