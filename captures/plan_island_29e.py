"""Authored coarse rock planes with rebuilt terrain-fitted path, retain occupied sites."""
from pathlib import Path
import json,collections,math
import numpy as np
from scipy.spatial import Delaunay
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union,nearest_points
R=Path(__file__).resolve().parents[1];e=json.loads((R/'captures/lantern_island_study_29d/geometry-evidence.json').read_text());prior=json.loads((R/'captures/lantern_island_study_29d/terrain-plan.json').read_text())
t=e['new']['island_c grass and exposed rock terrain'];v=np.array(t['vertices']);n=len(v)//2;top=[(i,p) for i,p in enumerate(t['polygons']) if max(p)<n]
sites=unary_union([Polygon(p) for p in e['protection']['pads']]+[Point(p).buffer(2) for p in e['protection']['trees']])
protected_faces=[i for i,p in top if Polygon(v[p,:2]).intersects(sites)];protected_vertices=sorted({j for i in protected_faces for j in t['polygons'][i]})
protected_surface=unary_union([Polygon(v[t['polygons'][i],:2]) for i in protected_faces])
edges=collections.Counter(tuple(sorted((p[j],p[(j+1)%3]))) for _,p in top for j in range(3));boundary=sorted({i for edge,c in edges.items() if c==1 for i in edge})
controls=[[-12,-14,16.45],[1,1,17.99],[-19,-8,14.1],[-8,-24,12.0],[7,-15,14.5],[18,-8,9.4],[16,7,13.0],[7,19,11.5],[-4,19,12.8],[-26,1,9.8],[-19,22,7.5],[23,20,7.8],[0,-8,17.0]]
control=np.concatenate([v[boundary],np.array(controls)]);tri=Delaunay(control[:,:2])
def authored(xy):
 j=int(tri.find_simplex(xy));assert j>=0,(xy,j)
 uv=tri.transform[j,:2]@(xy-tri.transform[j,2]);w=np.r_[uv,1-sum(uv)];return float(w@control[tri.simplices[j],2])
road=unary_union([Polygon(p) for p in e['protection']['path_top_triangles']])
old_tri=np.array([v[p] for _,p in top]);old_inverse=np.array([np.linalg.inv(np.column_stack([q[:,:2],np.ones(3)])) for q in old_tri])
def old_height(xy):
 weights=np.einsum('i,nij->nj',np.r_[xy,1.],old_inverse);ids=np.flatnonzero(np.min(weights,axis=1)>=-2e-5);assert len(ids),(xy,'old ground')
 k=int(ids[0]);return float(weights[k]@old_tri[k,:,2])
new=v.copy()
for i in range(n):
 if i in protected_vertices or i in boundary:continue
 pt=Point(v[i,:2]);target=authored(v[i,:2]);distance=pt.distance(protected_surface)
 # A broad graded shoulder supports the path, replacing its old abrupt narrow
 # raised berm. It is a terrain edit; the path is still re-draped below.
 rd=pt.distance(road)
 if rd<10:
  q=nearest_points(pt,road)[1];grade=old_height(np.array(q.coords[0]));a=rd/10.;rw=1-a*a*(3-2*a)
  target=max(target,target*(1-rw)+grade*rw)
 # The prior road ring is free to settle onto new rock planes. Blend only at
 # actual occupied-site support, not along the previous entire road shoulder.
 f=min(1.,distance/2.5);w=f*f*(3-2*f);new[i,2]=v[i,2]*(1-w)+target*w;new[i+n,2]=new[i,2]-.65
original_path=e['new']['island_c terrain fitted keeper paths'];pv=np.array(original_path['vertices']);pn=len(pv)//2
terrain_tri=np.array([new[p] for _,p in top]);matrices=np.array([np.linalg.inv(np.column_stack([q[:,:2],np.ones(3)])) for q in terrain_tri])
def surface(xy):
 weights=np.einsum('i,nij->nj',np.r_[xy,1.],matrices);ids=np.flatnonzero(np.min(weights,axis=1)>=-2e-5);assert len(ids),(xy,'no ground')
 k=int(ids[0]);return float(weights[k]@terrain_tri[k,:,2])
for i in range(pn):pv[i,2]=surface(pv[i,:2])+.045;pv[pn+i,2]=pv[i,2]-.35
path_slopes=[]
for face in original_path['polygons']:
 if max(face)>=pn:continue
 q=pv[face];normal=np.cross(q[1]-q[0],q[2]-q[0]);normal/=np.linalg.norm(normal);path_slopes.append(math.degrees(math.acos(min(1.,max(-1.,normal[2])))))
core=np.array(e['new']['island_c faulted bedrock']['vertices']);offset=54;assert len(core)==offset+n;core[offset:]=new[n:]
mapping=prior['core_boundary_map']
for i,j in enumerate(mapping):
 # Keep the existing uneven geological row, remove lateral offsets that caused
 # local projected folded quads. This remains an overhanging concave coast.
 core[36+i,:2]=core[18+i,:2]*.48+new[j,:2]*.52
 core[36+i,2]=max(1.7,new[n+j,2]*[.70,.38,.64,.28,.75,.44,.30,.67,.39,.76,.48,.29,.71,.36,.62,.43,.78,.32][i])
out={'terrain_vertices':new.tolist(),'path_vertices':pv.tolist(),'core_vertices':core.tolist(),'core_faces':e['new']['island_c faulted bedrock']['polygons'],'core_cap_offset':54,'core_boundary_map':mapping,'protected_face_indices':protected_faces,'protected_vertex_indices':protected_vertices,'top_vertex_count':n,'changed_top_vertices':int(np.sum(np.abs(new[:n,2]-v[:n,2])>1e-5)),'path_max_slope_degrees':max(path_slopes),'authored_controls':controls,'scope':'Road shape is intentionally rebuilt onto13 authored offset rock plane controls plus true shoreline. Protected occupied tower/house padded footprint and tree2m disks retain original support triangles; no old road-height preservation claim. Validate actual exported path top gap and slope, source/world fixtures, and visual fidelity.'}
(R/'captures/island-29e-terrain-plan.json').write_text(json.dumps(out,indent=2));print('protected faces',len(protected_faces),'changed',out['changed_top_vertices'],'path max slope',out['path_max_slope_degrees'])
