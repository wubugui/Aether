from pathlib import Path
import json,math,hashlib,collections
import numpy as np
from shapely.geometry import Polygon,Point,shape,LineString
from shapely.ops import unary_union
from shapely.strtree import STRtree
from shapely.validation import explain_validity
R=Path(__file__).resolve().parents[1];p=R/'captures/island-31g-cut-patch.json';raw=json.loads(p.read_text());v=np.array(raw['vertices']);f=raw['polygons'];selected=set(raw['selected_faces']);assert all(len(x)==3 for x in f)
intake=json.loads((R/'reviews/round-31g-support-intake.json').read_text());tree=json.loads((R/'reviews/round-31f-actual-tree-support.json').read_text());masks={'road':shape(intake['road_geometry_geojson']),'pads':unary_union([Polygon(s['polygon']) for s in intake['pads']]),'actual_trunks':unary_union([Polygon(x) for x in intake['all14_actual_tree_footprints_xy']])}
edges=collections.defaultdict(list)
for fi,ids in enumerate(f):
 for a,b in zip(ids,ids[1:]+ids[:1]):edges[tuple(sorted([a,b]))].append((fi,a,b))
adj=collections.defaultdict(set);bound=[]
for key,items in edges.items():
 chosen=[x for x in items if x[0] in selected]
 if len(chosen)==2:adj[chosen[0][0]].add(chosen[1][0]);adj[chosen[1][0]].add(chosen[0][0])
 elif len(chosen)==1:bound.append(chosen[0])
remaining=set(selected);components=[]
while remaining:
 stack=[remaining.pop()];part=[]
 while stack:
  a=stack.pop();part.append(a)
  for b in adj[a]:
   if b in remaining:remaining.remove(b);stack.append(b)
 components.append(part)
out=collections.defaultdict(list);incoming=collections.Counter()
for fi,a,b in bound:out[a].append(b);incoming[b]+=1
degree_bad={a:{'out':len(out[a]),'in':incoming[a]} for a in set(out)|set(incoming) if len(out[a])!=1 or incoming[a]!=1}
loops=[]
if not degree_bad:
 remain=set(out)
 while remain:
  a=next(iter(remain));start=a;loop=[]
  while a in remain:remain.remove(a);loop.append(a);a=out[a][0]
  assert a==start;loops.append(loop)
def az(x):return np.column_stack([np.arctan2(x[:,1],x[:,0]),x[:,2]])
looprows=[]
for l in loops:
 q=az(v[l]);po=Polygon(q);looprows.append({'vertices':l,'xyz':v[l].tolist(),'angle_radian_z':q.tolist(),'simple_boundary':LineString(np.vstack([q,q[0]])).is_simple,'valid_polygon':po.is_valid,'validity':explain_validity(po),'area_radian_m':po.area,'angle_degrees_min_max':[float(np.degrees(q[:,0].min())),float(np.degrees(q[:,0].max()))],'z_min_max':[float(q[:,1].min()),float(q[:,1].max())]})
occupancy=[]
for name,mask in masks.items():
 rows=[];upp=[];anypol=[]
 for fi in selected:
  t=v[f[fi]];inter=Polygon(t[:,:2]).intersection(mask)
  if inter.area<1e-10:continue
  nz=float(np.cross(t[1]-t[0],t[2]-t[0])[2]);anypol.append(inter)
  if nz>1e-9:upp.append(inter)
  rows.append({'face':fi,'projection_intersection_m2':inter.area,'normal_z_unnormalized':nz,'z_range':[float(t[:,2].min()),float(t[:,2].max())]})
 occupancy.append({'mask':name,'all_face_projection_intersection_union_m2':unary_union(anypol).area,'upward_face_projection_intersection_union_m2':unary_union(upp).area,'faces':rows})
# Inspect kept one-ring upward support at boundary vertices; a fixed boundary itself cannot move these triangles.
boundv=set(out);touch=[]
for fi,ids in enumerate(f):
 if fi in selected or not boundv.intersection(ids):continue
 t=v[ids]
 if np.cross(t[1]-t[0],t[2]-t[0])[2]<=1e-9:continue
 areas={n:Polygon(t[:,:2]).intersection(m).area for n,m in masks.items()};areas={n:a for n,a in areas.items() if a>1e-10}
 if areas:touch.append({'kept_face':fi,'boundary_vertices':sorted(boundv.intersection(ids)),'support_intersection_m2':areas})
sf=sorted(selected);ts=np.array([v[f[i]] for i in sf]);q=np.array([az(t) for t in ts]);pp=[Polygon(t) for t in q];ix=STRtree(pp);sig=(q[:,1,0]-q[:,0,0])*(q[:,2,1]-q[:,0,1])-(q[:,1,1]-q[:,0,1])*(q[:,2,0]-q[:,0,0]);overlaps=[]
for i,poly in enumerate(pp):
 if poly.area<1e-12:continue
 for j in ix.query(poly):
  j=int(j)
  if j<=i or pp[j].area<1e-12:continue
  inter=poly.intersection(pp[j])
  if inter.area<1e-8:continue
  a=inter.representative_point();uv=[a.x,a.y,1];r1=np.linalg.solve(np.column_stack([q[i],np.ones(3)]),np.linalg.norm(ts[i,:,:2],axis=1));r2=np.linalg.solve(np.column_stack([q[j],np.ones(3)]),np.linalg.norm(ts[j,:,:2],axis=1));overlaps.append({'face_pair':[sf[i],sf[j]],'angle_z_overlap_area_radian_m':inter.area,'sample_angle_z':[a.x,a.y],'linear_parameterized_radius_difference_m':float(abs(np.dot(uv,r1-r2)))})
overlaps.sort(key=lambda a:a['angle_z_overlap_area_radian_m'],reverse=True)
report={'round':'31g','scope':'Actual bisected31f cut-patch plan only, no31g generated mesh acceptance. Angle/z vertex-linear triangle parameterization is diagnostic; not exact cylindrical projection of triangle interiors.','source_plan_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'counts':{'vertices':len(v),'all_faces':len(f),'selected_faces':len(selected),'boundary_edges':len(bound),'boundary_loops':len(loops),'components':[len(x) for x in components]},'all_mesh_edges_two_faces':all(len(x)==2 for x in edges.values()),'boundary_kept_counterparts':all(len(edges[tuple(sorted([a,b]))])==2 and sum(x[0] not in selected for x in edges[tuple(sorted([a,b]))])==1 for _,a,b in bound),'boundary_degree_errors':degree_bad,'loops':looprows,'selected_support_intersections':occupancy,'kept_upward_support_faces_using_fixed_boundary':touch,'angle_z_selected_triangle_parameterization':{'positive_winding':int(sum(sig>1e-10)),'negative_winding':int(sum(sig<-1e-10)),'near_zero_abs_double_area_below1e_10':int(sum(abs(sig)<=1e-10)),'overlap_pair_count':len(overlaps),'largest20_overlap_examples':overlaps[:20],'boundary_simple_does_not_prove_interior_single_valued':True},'full_reference_accepted':False,'limits':['Intersections are geometric XY projection; downward/buried selected faces do not automatically imply actual support removal. Upward intersections are separately listed for closer height/upper-envelope checking.','Fixed boundary sharing kept support is permissible only if all boundary coordinates/edges and kept faces are retained.','No existing31f full support/self-intersection/GPU/Blender rerun.','New replacement faces need their own support, boundary, closure and local self-intersection validation.']}
(R/'reviews/round-31g-cut-patch-independent.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
md='# 31g 切分后实际面片独立核验\n\n当前选区'+str(len(selected))+'面，边邻接连通分量'+str([len(x) for x in components])+'，'+str(len(bound))+'条边界边、'+str(len(loops))+'个边界环；每条边都有一个保留壳对应面。边界度异常：'+str(degree_bad)+'。\n\n'
for x in occupancy:md+=f"- {x['mask']}：选中向上面投影相交并集{x['upward_face_projection_intersection_union_m2']:.12g}m²；所有面投影{x['all_face_projection_intersection_union_m2']:.12g}m²。\n"
md+='\n边界参数域检查：'+str([{k:x[k] for k in ['simple_boundary','valid_polygon','validity','angle_degrees_min_max','z_min_max']} for x in looprows])+'。保留壳共享边界的支承邻面'+str(len(touch))+'个，列在JSON中，不能在重接时随意挪动边界。\n\n(angle,z)顶点线性参数三角中存在'+str(len(overlaps))+'对正面积重合，正/反绕向'+str(int(sum(sig>1e-10)))+'/'+str(int(sum(sig<-1e-10)))+'。简单边界只说明可定义参数域，不意味着旧内部是单值径向图；旧内部重合不等于3D自交，也不直接否决删除旧片后新设计单值曲面。新径向设计仍须保持真实边界，并验证其与保留壳的关系。该诊断不是非线性圆柱投影的精确三角内映射。\n\n本次没有生成新壳或重跑31f整套支承；31g最终模型待验证。\n'
(R/'reviews/round-31g-cut-patch-independent.md').write_text(md,encoding='utf-8');print(json.dumps({k:report[k] for k in ['counts','all_mesh_edges_two_faces','boundary_kept_counterparts','boundary_degree_errors']},indent=2));print(json.dumps({'occupancy':[{k:a[k] for k in a if k!='faces'} for a in occupancy],'loop_summary':[{k:a[k] for k in a if k not in ['vertices','xyz','angle_radian_z']} for a in looprows],'kept_support_faces':touch,'overlaps':len(overlaps),'positive':int(sum(sig>1e-10)),'negative':int(sum(sig<-1e-10))},indent=2))
