from pathlib import Path
import json,math,collections
import numpy as np
from shapely.geometry import Polygon,Point,MultiPoint,LineString
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
e=json.loads((R/'captures/lantern_island_study_29a/geometry-evidence.json').read_text())
t=e['new']['island_c grass and exposed rock terrain'];v=np.array(t['vertices']);n=len(v)//2
assert np.max(np.abs(v[:n,:2]-v[n:,:2]))<1e-6
assert np.max(np.abs(v[:n,2]-.65-v[n:,2]))<2e-6
top=[(i,p) for i,p in enumerate(t['polygons']) if max(p)<n]
road=unary_union([Polygon(p) for p in e['protection']['path_top_triangles']])
protection=unary_union([road.buffer(1.2)]+[Polygon(p) for p in e['protection']['pads']]+[Point(p).buffer(2) for p in e['protection']['trees']])
protected_faces=[i for i,p in top if Polygon(v[p,:2]).intersects(protection)]
protected_vertices=sorted({j for i in protected_faces for j in t['polygons'][i]})
protected_surface=unary_union([Polygon(v[t['polygons'][i],:2]) for i in protected_faces])
edges=collections.Counter(tuple(sorted((p[j],p[(j+1)%len(p)]))) for _,p in top for j in range(len(p)))
shore=unary_union([LineString(v[list(edge),:2]) for edge,count in edges.items() if count==1])
new=v.copy()
for i,(x,y,z) in enumerate(v[:n]):
    if i in protected_vertices:continue
    pt=Point(x,y);d=pt.distance(shore);p=pt.distance(protected_surface)
    rim=5.2+1.8*math.sin(x*.08+y*.055)+.6*math.cos(y*.16)
    # A connected broad shoulder climbs from an unequal low rim toward the
    # original supported summit; a smooth join leaves protected triangles exact.
    target=rim+(18.0-rim)*min(1.,d/22.)
    w=min(1.,p/5.0);w=w*w*(3-2*w)
    new[i,2]=z*(1-w)+target*w
    new[i+n,2]=new[i,2]-.65
assert np.array_equal(new[protected_vertices],v[protected_vertices])
out={'basis':'29a','terrain_vertices':new.tolist(),'top_vertex_count':n,'protected_face_indices':protected_faces,'protected_vertex_indices':protected_vertices,'changed_top_vertices':int(np.sum(np.abs(new[:n,2]-v[:n,2])>1e-5)),'maximum_height_change_m':float(np.max(np.abs(new[:,2]-v[:,2]))),'protection':e['protection'],'scope':'Preserve every actual top triangle intersecting road+1.2m, padded tower/house foundations, or conservative tree axes+2m. Remodel remaining connected terrain; no whole terrain preservation claim.'}
(R/'captures/island-29b-terrain-plan.json').write_text(json.dumps(out,indent=2))
print({k:out[k] for k in ['top_vertex_count','changed_top_vertices','maximum_height_change_m']},'protected faces',len(protected_faces))
