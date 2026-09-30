"""Prepare native constrained Blender triangulation for resized land and full-size pads."""
from pathlib import Path
import json,math,collections
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];e=json.loads((R/'captures/lantern_island_study_29e/geometry-evidence.json').read_text())
scale=np.array([.72,.72,.65]);tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths'
t=e['new'][tn];v=np.array(t['vertices'])*scale;n=len(v)//2;top=[p for p in t['polygons'] if max(p)<n];poly=unary_union([Polygon(v[p,:2]) for p in top])
counts=collections.Counter(tuple(sorted((p[i],p[(i+1)%3]))) for p in top for i in range(3));edges=list(counts);adj={}
for (a,b),count in counts.items():
 if count==1:adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
outline=[min(adj)];last=-1
while True:
 p=outline[-1];q=next(j for j in adj[p] if j!=last)
 if q==outline[0]:break
 outline.append(q);last=p
assert len(outline)==18
xy=v[:n,:2].tolist()
def rect(cx,cy,wx,wy,turn):
 co,si=math.cos(turn),math.sin(turn);return [(cx+co*x-si*y,cy+si*x+co*y) for x,y in [(-wx,-wy),(wx,-wy),(wx,wy),(-wx,wy)]]
def add_ring(ring):
 start=len(xy);xy.extend([list(p) for p in ring]);edges.extend([(start+i,start+(i+1)%len(ring)) for i in range(len(ring))])
sites=[{'name':'tower','center':[1.5,-.8],'half_width':4.3,'half_depth':4.3,'turn':.1},{'name':'keeper_house','center':[-8.64,-10.08],'half_width':3.05,'half_depth':4.1,'turn':-.15}]
for s in sites:
 s['polygon']=rect(*s['center'],s['half_width'],s['half_depth'],s['turn']);outside=Polygon(s['polygon']).difference(poly).area
 assert outside<1e-7,(s['name'],'pad outside resized island',outside);add_ring(s['polygon'])
p=e['new'][pn];pv=np.array(p['vertices'])*scale;half=len(pv)//2;road=unary_union([Polygon(pv[face,:2]) for face in p['polygons'] if max(face)<half]);road_polygons=[]
for shape in (list(road.geoms) if hasattr(road,'geoms') else [road]):
 rings=[list(shape.exterior.coords)[:-1]]+[list(r.coords)[:-1] for r in shape.interiors]
 for ring in rings:add_ring(ring)
 road_polygons.append(rings)
out={'land_scale_blender_xyz':scale.tolist(),'source_scaled_terrain_vertices':v.tolist(),'source_top_triangles':top,'source_top_vertex_count':n,'cdt_points':xy,'cdt_edges':edges,'cdt_outline':outline,'sites':sites,'road_polygons':road_polygons,'d_world_position':[-2372,0,-1812],'d_yaw':2.0,'tower_offset_godot':[1.5,0,.8],'house_offset_godot':[-8.64,0,10.08],'tree_offset_scale':.72,'native_building_scale_unchanged':True,'scope':'Proportion candidate; not original geography or exact pixel-to3D reconstruction. Native Blender constrained triangulation clips real pad and road boundaries. Tower site shifted locally to retain full4.3m support inside smaller island; native building dimensions unchanged.'}
(R/'captures/island-30a-proportion-plan.json').write_text(json.dumps(out,indent=2));print('Native CDT input',len(xy),'points',len(edges),'edges; pads fully inside actual resized coastline')
