from pathlib import Path
import json,math,hashlib,collections
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];ep=R/'captures/lantern_island_study_31h/geometry-evidence.json';e=json.loads(ep.read_text(encoding='utf-8'));tn='island_c grass and exposed rock terrain';ob=e['new'][tn];v=np.array(ob['vertices']);f=ob['polygons'];path=e['new']['island_c terrain fitted keeper paths'];pv=np.array(path['vertices']);road=unary_union([Polygon(pv[q][:,:2]) for q in path['polygons'] if np.cross(pv[q][1]-pv[q][0],pv[q][2]-pv[q][0])[2]>1e-9]);pads=unary_union([Polygon(x['polygon']) for x in e['sites']]);base=json.loads((R/'reviews/round-31f-actual-tree-support.json').read_text());foot=np.array(base['native_bottom_polygon_xy']);sp=R/'captures/validation_runs/lantern-island-31h-20260908T212800Z-78b153beccc94a60ba27ba0e79a1cfaa/images/night-reference.png.json';side=json.loads(sp.read_text());treepol=[]
for p in side['placements']:
 if p.get('kind')!='existing_native_pine' or p.get('island') not in ['island_c','island_d']:continue
 a=0 if p['island']=='island_c' else 2.;origin=np.array([-3050,0,-2650]) if p['island']=='island_c' else np.array([-2372,0,-1812]);d=np.array(p['position'])-origin;c,s=math.cos(a),math.sin(a);xy=np.array([c*d[0]-s*d[2],-(s*d[0]+c*d[2])]);rot=np.array([[c,s],[-s,c]]);treepol.append(Polygon(foot@rot.T*p['scale']+xy))
assert len(treepol)==14;masks={'road':road,'pads':pads,'actual31h_trunks':unary_union(treepol)};adj=collections.defaultdict(list)
for fi,ids in enumerate(f):
 for a,b in zip(ids,ids[1:]+ids[:1]):adj[tuple(sorted([a,b]))].append({'face':fi,'directed_edge':[a,b]})
def face_info(fi):
 t=v[f[fi]];n=np.cross(t[1]-t[0],t[2]-t[0]);ar=np.linalg.norm(n)/2;n/=np.linalg.norm(n);p=Polygon(t[:,:2]);return {'face':fi,'vertices':f[fi],'xyz':t.tolist(),'material':ob['materials'][fi],'area3d_m2':float(ar),'normal':n.tolist(),'projection_mask_distance_m':{k:p.distance(m) for k,m in masks.items()},'upward_support_projection_intersection_m2':{k:p.intersection(m).area if n[2]>1e-9 else 0. for k,m in masks.items()}}
groups=[{'target_face':2142,'requested_edges':[[1108,1106],[1104,1106]],'status':'Parent explicitly selected both split edges.'},{'target_face':2158,'requested_edges':[[1109,1107],[1105,1107]],'status':'Inferred analogous east shoulder split towards low1107; report all target edges as well, pending exact31i plan.'}];rows=[]
for g in groups:
 fi=g['target_face'];all_edges=[]
 for a,b in zip(f[fi],f[fi][1:]+f[fi][:1]):
  aa=adj[tuple(sorted([a,b]))];assert len(aa)==2;all_edges.append({'edge':[a,b],'xyz':[v[a].tolist(),v[b].tolist()],'length_m':float(np.linalg.norm(v[a]-v[b])),'incident_faces':aa,'candidate_split_edge':tuple(sorted([a,b])) in [tuple(sorted(x)) for x in g['requested_edges']]})
 neighbors=sorted({a['face'] for ed in all_edges for a in ed['incident_faces']});rows.append({**g,'target':face_info(fi),'all_edges':all_edges,'complete_edge_neighbor_faces':[face_info(x) for x in neighbors]})
endpoints=sorted({i for g in groups for ed in g['requested_edges'] for i in ed});endpoint_rows=[]
for vi in endpoints:
 incident=[i for i,ids in enumerate(f) if vi in ids];occupied=[]
 for fi in incident:
  a=face_info(fi)
  if any(x>1e-8 for x in a['upward_support_projection_intersection_m2'].values()):occupied.append(a)
 endpoint_rows.append({'vertex':vi,'xyz':v[vi].tolist(),'complete_incident_faces':incident,'occupied_upward_one_ring_faces':occupied})
notes=['Use one BMesh edge_split on the shared edge so both incident faces use exactly the same inserted vertex; face_split only after both original edge splits exist.','2142 cut creates one quad and one triangle locally; its neighbors acquire the same boundary points. Their final tessellation may change even if the new point stays on the old edge. Record and check that entire changed set.','If the split point is displaced out of the old edge to create shoulder thickness, both incident faces change shape. Treat the opposite neighbor as part of the authored patch; do not preserve its old triangle while moving only target geometry.','Keep retained occupied upper support linear patches or explicitly repartition their boundary; exact31i candidate support remains necessary even though this bounded one-ring intake has no occupied intersections.','Quads with four authored noncoplanar vertices need explicit intended diagonal or actual exported tessellation review, not a claim that quad existence proves broad shoulder shape.','Shared edge checks use actual31h source indices; after BMesh split/reindex match coordinates or lineage, not stale numbers.','East split-edge choice in this intake is provisional; actual parent plan takes precedence.']
report={'round':'31i','scope':'Bounded actual31h shared-edge and endpoint-one-ring intake only. No31i candidate/native/GPU or full support check.','files':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ep,sp]},'current_actual_tree_count':14,'selected_groups':rows,'endpoint_one_rings':endpoint_rows,'construction_requirements':notes,'full_reference_accepted':False}
(R/'reviews/round-31i-shared-edge-intake.json').write_text(json.dumps(report,indent=2),encoding='utf-8');md='# 31i 真实共享边与支承预审\n\n只分析31h原生两肩目标面及完整边邻面/端点一环；使用31h实际运行14树轴变换原生六边形干底，旧2m盘未冻结。\n\n'
for g in rows:
 md+='## 目标面'+str(g['target_face'])+'\n\n'
 for a in g['all_edges']:md+='- 边'+str(a['edge'])+'，相邻面'+str([x['face'] for x in a['incident_faces']])+'，'+('拟split边' if a['candidate_split_edge'] else '其他共边')+'。\n'
 md+='\n完整边邻面：'+str([x['face'] for x in g['complete_edge_neighbor_faces']])+'；各实际坐标、面积、支承相交和净距在JSON。\n\n'
md+='## 正确切分边界\n\n'+'\n\n'.join('- '+x for x in notes)+'\n\n当前只作拓扑预审，不能把未碰支承的一环当作任意移动许可。31i实际GLB仍需闭合、支承、离散相交与视觉审查。\n';(R/'reviews/round-31i-shared-edge-intake.md').write_text(md,encoding='utf-8');print(json.dumps({'groups':[{'target':x['target_face'],'edges':[{'edge':a['edge'],'faces':[q['face'] for q in a['incident_faces']]} for a in x['all_edges']],'occupied_neighbors':[a['face'] for a in x['complete_edge_neighbor_faces'] if any(v>1e-8 for v in a['upward_support_projection_intersection_m2'].values())]} for x in rows],'occupied_endpoint_rings':[{k:x[k] for k in ['vertex','occupied_upward_one_ring_faces']} for x in endpoint_rows]},indent=2))
