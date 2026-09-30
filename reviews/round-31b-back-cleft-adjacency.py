from pathlib import Path
import json,numpy as np
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];p=R/'reviews/round-31b-back-cleft-independent.json';r=json.loads(p.read_text());e=json.loads((R/'captures/lantern_island_study_31b/geometry-evidence.json').read_text());native=e['new']['island_c grass and exposed rock terrain'];v=np.array(native['vertices']);faces=native['polygons'];path=e['new']['island_c terrain fitted keeper paths'];pv=np.array(path['vertices'])
road=unary_union([Polygon(pv[f][:,:2]) for f in path['polygons'] if np.cross(pv[f][1]-pv[f][0],pv[f][2]-pv[f][0])[2]>1e-9]);pads=unary_union([Polygon(s['polygon']) for s in e['sites']]);trees=unary_union([Point(x).buffer(2) for x in r['actual_C_D_tree_local_axes']]);masks={'road':road,'pads':pads,'current14tree_disks':trees}
indices=sorted({i for s in r['samples'] for i in s['source_vertex_indices']});out=[]
for vi in indices:
 adj=[]
 for fi,f in enumerate(faces):
  if vi not in f:continue
  t=v[f];normal=np.cross(t[1]-t[0],t[2]-t[0]);poly=Polygon(t[:,:2]);inter={n:poly.intersection(m).area for n,m in masks.items()}
  if normal[2]>1e-9 and any(a>1e-8 for a in inter.values()):adj.append({'face':fi,'projection_intersection_area_m2':inter})
 out.append({'source_vertex':vi,'upward_adjacent_faces_intersecting_protection':adj})
r['bounded_sample_vertex_adjacency']=out
r['adjacency_area_limit']='Only vertex939 has incident upward faces touching the expanded-pad domain by computed slivers: face308 8.6547e-8m2 and face1032 5.8139e-8m2. These tiny projection-area slivers are consistent with float boundary drift; no sliver width was measured; they do not establish substantive occupied support or justify freezing a whole triangle. Keep the true pad boundary in an authored edit and recheck actual support after candidate construction.'
r['near_tower_edit_boundary']='Four points lie outside occupied projections. Closest sampled entire face1467 is1.37483158m from expanded tower pad; common upper vertex939 at(-1.387008,5.015520,11.690657) is1.774687m away. Its upward incident faces must be considered before editing shared vertices; retain occupied linear support planes and clip the local edit domain at the actual rotated pad boundary. This distance is not a blanket allowed displacement or excavation radius.'
r['provenance_limit']='309 y5.0155..9.4276 and1467 y4.1582..5.8320 are inward of North y15+;1454 extends y9.3623..17.9081 despite hit y12.2823. No causal attribution of entire cleft to a historic cutter or31a/b from four rays.'
p.write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))

