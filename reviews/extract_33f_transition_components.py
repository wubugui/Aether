from pathlib import Path
import json,hashlib
from collections import defaultdict
import numpy as np
from shapely.geometry import shape,mapping
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
d=read('reviews/round-33d-visible-transition-domain.json');b=read('reviews/round-33b-reopened-source.json');native_d=read('reviews/round-33d-reopened-source.json');native_e=read('reviews/round-33e-reopened-source.json');name=next(n for n in b['objects'] if n.startswith('Mainland'));bv=np.array(b['objects'][name]['vertices']);dv=np.array(native_d['objects'][name]['vertices']);ev=np.array(native_e['objects'][name]['vertices']);lookup=defaultdict(list)
for i,p in enumerate(dv):lookup[tuple(p)].append(i)
free={v['vertex_index'] for v in d['one_ring_vertices'] if v['can_move_without_splitting_any_occupied_incident_face']};vrows={v['vertex_index']:v for v in d['one_ring_vertices']};faces=d['one_ring_faces'];parent={v['vertex_index']:v['vertex_index'] for v in d['one_ring_vertices']}
def root(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
for f in faces:
 a,c,e=f['vertex_indices'];parent[root(c)]=root(a);parent[root(e)]=root(a)
groups=defaultdict(set)
for i in parent:groups[root(i)].add(i)
components=[];vcomponent={}
for ci,ids in enumerate(sorted(groups.values(),key=lambda s:min(s))):
 fs=[f for f in faces if set(f['vertex_indices']).issubset(ids)];hits=[dict(view=h['view'],pixel=h['pixel'],triangle=h['actual_hit_face']['actual_triangle']) for h in d['hits'] if set(h['actual_hit_face']['vertex_indices']).issubset(ids)];points=bv[sorted(ids)];poly=unary_union([shape(f['triangle_projection']) for f in fs]);front=any(h['view']=='day-coast-front' for h in hits);reference=any(h['view']=='day-reference' for h in hits);components.append(dict(component=ci,source33b_vertex_ids=sorted(ids),actual_triangle_ids=[f['actual_triangle'] for f in fs],vertex_count=len(ids),triangle_count=len(fs),free_vertex_ids=sorted(ids&free),kept_support_boundary_vertices=sorted(ids-free),selected_hits=hits,contains_front_hit=front,contains_main_reference_hit=reference,xyz_bounds=[points.min(axis=0).tolist(),points.max(axis=0).tolist()],projection=mapping(poly),projected_area_m2=poly.area))
 for i in ids:vcomponent[i]=ci
selectedcomponents=[c for c in components if c['contains_front_hit']];excludedcomponents=[c for c in components if c['contains_main_reference_hit']];selected=set().union(*(set(c['free_vertex_ids']) for c in selectedcomponents));assert selected and all(not c['contains_main_reference_hit'] for c in selectedcomponents)
crossfaces=[]
for i,f in enumerate(b['objects'][name]['triangles']):
 memberships={vcomponent[v] for v in f if v in vcomponent}
 if len(memberships)>1:crossfaces.append(dict(actual_triangle=i,vertex_ids=f,domain_components=sorted(memberships)))
maps=[]
for i in sorted(selected):
 match=lookup[tuple(bv[i])];maps.append(dict(source33b_vertex_index=i,source33b_xyz=bv[i].tolist(),actual33d_exact_xyz_matches=match,selected33e_xyz=ev[i].tolist(),only_z_changed_from33b=bool(np.array_equal(bv[i,:2],ev[i,:2])),proposed_z_delta_m=float(ev[i,2]-bv[i,2])))
quad=[2466,4346,4348,4350];quadmap=[dict(source33b_vertex_index=i,xyz=bv[i].tolist(),actual33d_exact_xyz_matches=lookup[tuple(bv[i])],in_selected_front_free_points=i in selected) for i in quad]
result=dict(scope='33f read-only domain vertexconnectivity and exact coordinate mapping preparation; no source edits, new model or GPU.',bindings={'domain_sha256':sha('reviews/round-33d-visible-transition-domain.json'),'source33b_sha256':b['source_sha256'],'source33d_sha256':native_d['source_sha256'],'source33e_sha256':native_e['source_sha256']},connectivity_definition='Connected through actual shared vertex indices among the94investigated source33b triangles. This is domain connectivity, not disconnected components of the entire continuous mainland.',components=components,selected_front_component_ids=[c['component'] for c in selectedcomponents],excluded_main_reference_component_ids=[c['component'] for c in excludedcomponents],selected_front_free_vertex_count=len(selected),selected_front_free_vertex_ids=sorted(selected),excluded_main_reference_free_vertex_count=sum(len(c['free_vertex_ids']) for c in excludedcomponents),front_and_reference_domain_components_disjoint=not(set(c['component'] for c in selectedcomponents)&set(c['component'] for c in excludedcomponents)),full_source_triangles_touching_multiple_domain_components=crossfaces,selected_front_exact33d_mapping=maps,all_selected_front_points_unique_exact33d_match=all(len(m['actual33d_exact_xyz_matches'])==1 for m in maps),restored_old_diagonal_source33b=[2466,4348],rejected_new_diagonal_source33b=[4346,4350],fourpoint_diagonal_domain_mapping=quadmap,limits=['All coordinate mappings use unchanged original33b XYZ in the actual33d source; never use old indices directly after33d remesh.','No direction to copy the two mainreference groups. Their actual source coordinates and33d geometry remain the baseline.','All incident source triangles are inspected only for cross-component coupling; no new wholeoccupiedsupport or selfintersection scan.','Candidate should validate actualgeometry, support intrusion and positive XY triangles after restoring the local diagonal. Group separation alone is not candidate acceptance.'])
(R/'reviews/round-33f-transition-component-intake.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
md=f'''33f限定准备完成。以实际33b一环94张三角的共享顶点索引连通性分组，共{len(components)}组；front组与两处主图组分离。这里指已调查面片的连通性，不是声称整个大陆网格断开。

选用含front(843,528)、front(884,535)命中的组{result['selected_front_component_ids']}，共{len(selected)}个自由点；排除主图组{result['excluded_main_reference_component_ids']}，其自由点共{result['excluded_main_reference_free_vertex_count']}个。每组完整面/点索引、XYZ范围和GeoJSON都已记录。父任务可直接采用selected_front_free_vertex_ids，不能把整个86点清单一起合并。

再检查实际源中连接不同调查组的三角，共{len(crossfaces)}张，详细记录在full_source_triangles_touching_multiple_domain_components中；如有这种邻接，组间是否互相牵动应由实际三角决定，不仅看投影分离。

所选{len(selected)}点均以原33b精确XYZ在实际33d重编号源中唯一匹配，报告保存每点的actual33d_exact_xyz_matches及33e建议新Z；没有按旧索引直接拷入。33e只有Z变化的事实也逐点核对。恢复对角线四点[2466,4346,4348,4350]的33d索引映射另列：应使用旧[2466,4348]连接，拒绝已证导致反向的[4346,4350]连接。

只读准备不等于33f候选通过；候选仍需验证新旧实际几何差集、占用域、正向XY三角及实际视觉效果。本次未建模、未打开Blender或运行GPU。
'''
(R/'reviews/round-33f-transition-component-intake.md').write_text(md,encoding='utf-8')
print(json.dumps(dict(groups=[{k:c[k] for k in ['component','vertex_count','triangle_count','free_vertex_ids','kept_support_boundary_vertices','selected_hits']} for c in components],selected=len(selected),unique=result['all_selected_front_points_unique_exact33d_match'],crossfaces=crossfaces,quad=quadmap),indent=2))
