from pathlib import Path
import json,hashlib,math
import numpy as np
R=Path(__file__).resolve().parents[1];ip=R/'captures/island-31i-control-intake.json';intake=json.loads(ip.read_text());e=json.loads((R/'captures/lantern_island_study_31h/geometry-evidence.json').read_text());ob=e['new']['island_c grass and exposed rock terrain'];v=np.array(ob['vertices']);f=ob['polygons'];mapped=[]
for a in intake['controls']:
 assert np.array_equal(v[a['actual31h_vertex']],a['xyz']);mapped.append({'name':a['name'],'actual31h_vertex':a['actual31h_vertex'],'xyz':a['xyz']})
tri=[]
for fi in [2142,2143]:
 t=v[f[fi]];n=np.cross(t[1]-t[0],t[2]-t[0]);area=np.linalg.norm(n)/2;n/=np.linalg.norm(n);tri.append({'actual31h_face':fi,'vertices':f[fi],'area_m2':float(area),'normal':n.tolist()})
angle=math.degrees(math.acos(np.clip(np.dot(tri[0]['normal'],tri[1]['normal']),-1,1)))
proposal='优先改实际面2142(1108,1104,1106)与2143(1104,1105,1106)合计约67.46m²的连续中坡：它们两法线仅约'+f'{angle:.3f}'+'°，说明当前面组织几乎延续同一坡向。让1104/1108侧的中肩前缘朝+Y海侧明确外展，肩后缘留在较内侧，用少量共边点建立有厚度的短肩；1105端向+X侧错开且维持比1104低的层次，由1109连接短上坡。低端1106单独朝-X/+Y钝转，与1107/1111不同向收束，避免全部点同向推出成巨板。这里给的是局部方向，不是未经自交/支承验证的位移量；不要只推1104单点形成尖峰。'
supp={'source':str(ip.relative_to(R)),'sha256':hashlib.sha256(ip.read_bytes()).hexdigest(),'actual31h_coordinates_rechecked':True,'control_mapping':mapped,'bounded_two_face_geometry':tri,'two_face_normal_angle_degrees':angle,'direction_proposal':proposal,'limits':'Only8sourcecoordinates and2adjacentfaces inspected; no full mesh/support scan. Current-source evidence plus bounded design suggestion, not31i candidate acceptance.'}
p=R/'reviews/round-31h-island-independent-review.json';r=json.loads(p.read_text(encoding='utf-8'));r['next_round_actual_control_mapping_supplement']=supp;p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');p=R/'reviews/round-31h-island-independent-review.md';s=p.read_text(encoding='utf-8');s+='\n## 实际31h点号与两面定位补充\n\n接续输入`captures/island-31i-control-intake.json`的8点坐标已与31h实际源逐点核对。点1104高肩、1105中回折、1106低西根、1107东海鼻、1108西宽面、1109高东折、1110水下、1111外肩；完整XYZ在JSON。\n\n'+proposal+'\n';p.write_text(s,encoding='utf-8');print(json.dumps({'normal_angle_degrees':angle,'face_area_sum_m2':sum(a['area_m2'] for a in tri),'mapping_confirmed':8},indent=2))

