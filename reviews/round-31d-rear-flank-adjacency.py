from pathlib import Path
import json,numpy as np
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];p=R/'reviews/round-31d-rear-flank-independent.json';r=json.loads(p.read_text());e=json.loads((R/'captures/lantern_island_study_31d/geometry-evidence.json').read_text());native=e['new']['island_c grass and exposed rock terrain'];v=np.array(native['vertices']);faces=native['polygons'];path=e['new']['island_c terrain fitted keeper paths'];pv=np.array(path['vertices'])
road=unary_union([Polygon(pv[f][:,:2]) for f in path['polygons'] if np.cross(pv[f][1]-pv[f][0],pv[f][2]-pv[f][0])[2]>1e-9]);sites={s['name']:Polygon(s['polygon']) for s in e['sites']};pads=unary_union(list(sites.values()));trees=unary_union([Point(x).buffer(2) for x in r['actual_C_D_tree_local_axes']]);masks={'road':road,'pads':pads,'current14tree_disks':trees};hulls=[(a['name'],ConvexHull(np.array(a['actual_operand_geometry']['vertices']))) for a in e['additions']]
indices=sorted({i for s in r['samples'] for i in s['source_vertex_indices']});out=[]
for vi in indices:
 adj=[]
 for fi,f in enumerate(faces):
  if vi not in f:continue
  t=v[f];normal=np.cross(t[1]-t[0],t[2]-t[0]);poly=Polygon(t[:,:2]);inter={n:poly.intersection(m).area for n,m in masks.items()}
  if normal[2]>1e-9 and any(a>1e-8 for a in inter.values()):adj.append({'face':fi,'projection_intersection_area_m2':inter})
 out.append({'source_vertex':vi,'upward_adjacent_faces_intersecting_protection':adj})
for s in r['samples']:
 t=v[s['source_vertex_indices']];poly=Polygon(t[:,:2]);s['individual_site_face_distance_m']={n:poly.distance(m) for n,m in sites.items()};s['face_3d_area_m2']=float(np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))/2);matches=[]
 for name,h in hulls:
  eq=h.equations;dist=t@eq[:,:3].T+eq[:,3];on=np.max(abs(dist),axis=0);inside=float(np.max(dist));matches.append({'name':name,'minimum_max_vertex_distance_to_one_operand_plane_m':float(min(on)),'maximum_outside_operand_halfspace_distance_m':max(0,inside),'actual_face_on_operand_exterior_supporting_plane_and_inside':bool(min(on)<1e-4 and inside<1e-4)})
 s['actual_operand_supporting_plane_tests']=matches
r['bounded_sample_vertex_adjacency']=out;r['operand_provenance_method']='Actual sampled GLB face was already matched to native exported source. All3vertices tested on each convex operand supporting plane within0.1mm and inside all its halfspaces. This is bounded geometric provenance evidence, not pixel naming or approximate point proximity.'
r['limits']=[x for x in r['limits'] if not x.startswith('A point at y5-12')];r['limits'].append('All face indices apply only to31d actual geometry. Near-zero XY projection can be a large visible3D wall; it is not evidence of no material face. One-ring occupied intersections can constrain moving shared vertices even if sampled face itself is outside.')
p.write_text(json.dumps(r,indent=2),encoding='utf-8')
print(json.dumps({'sample_summary':[{'pixel':s['pixel'],'face':s['source_face'],'pad_distances':s['individual_site_face_distance_m'],'tree_gap_m':s['protection_relations']['actual_CD_tree_axis_2m_disks']['face_horizontal_distance_m'],'area3d_m2':s['face_3d_area_m2'],'operand_matches':[x['name'] for x in s['actual_operand_supporting_plane_tests'] if x['actual_face_on_operand_exterior_supporting_plane_and_inside']]} for s in r['samples']],'occupied_adjacency':[x for x in out if x['upward_adjacent_faces_intersecting_protection']]},indent=2))
