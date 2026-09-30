"""Conforming subdivision preserves original terrain triangle edges outside local road grading."""
from pathlib import Path
import json,math,hashlib,sys
import shapely
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import polygonize
root=Path(__file__).resolve().parents[1]
label='25a';out=root/'captures'/('village_grading_design_'+label);assert not out.exists();out.mkdir()
layout=json.loads((root/'captures/headland_layout_23c/layout.json').read_text())
paving=json.loads((root/'captures/village_paving_design_24m/paving.json').read_text())
origin=layout['origin'];xy=[(p[0]-origin[0],p[2]-origin[2]) for p in layout['vertices']]
def local(poly):
    return shapely.transform(poly,lambda a:a-[origin[0],origin[2]])
faces=[Polygon([xy[i] for i in t]) for t in layout['triangles']]
domain=shapely.union_all(faces,grid_size=1e-5)
edges=set()
for face in layout['triangles']:
    for a,b in zip(face,face[1:]+face[:1]):edges.add(tuple(sorted((a,b))))
lines=[LineString([xy[a],xy[b]]) for a,b in edges]
groups=[]
for g in paving['groups']:
    foot=local(shapely.from_geojson(g['footprint_geojson']))
    # Keep the house-foundation exclusions of the reviewed grading design.
    original_collar=local(shapely.from_geojson(g['grading_footprint_geojson']))
    houses=[h for h in layout['houses'] if h['name'].startswith('fore_' if g['name']=='foreground' else 'bay_')]
    protected=[]
    for house in houses:
        wx,wz=(3.9,5.4) if house['asset']=='keeper_house' else ((3.26,4.1) if house['asset']=='fisher_cottage' else (4.4,3.4))
        c,s=math.cos(house['yaw']),math.sin(house['yaw']);hx,_,hz=house['position']
        protected.append(Polygon([(hx-origin[0]+c*u+s*v,hz-origin[2]-s*u+c*v) for u,v in [(-wx,-wz),(wx,-wz),(wx,wz),(-wx,wz)]]).buffer(.025,join_style=2))
    collar=foot.buffer(4.,quad_segs=6).difference(shapely.union_all(protected)).intersection(domain)
    assert collar.intersection(shapely.union_all(protected)).area<1e-6

    bands=[(row['height'],local(shapely.from_geojson(row['geojson']))) for row in g['grading_bands']]
    groups.append((foot,collar,bands))
    lines.extend([foot.boundary,collar.boundary]+[poly.boundary for h,poly in bands])
network=shapely.union_all(lines,grid_size=1e-5)
cells=list(polygonize(network));print('Conforming grading cells',len(cells),flush=True)
vertices=[];triangles=[];lookup={};constraints=[];areas=[]
def index(p):
    key=tuple(round(v,5) for v in p)
    if key not in lookup:
        lookup[key]=len(vertices);vertices.append(key)
        point=Point(key);candidates=[]
        for foot,collar,bands in groups:
            if not collar.buffer(1e-5).covers(point):continue
            # The outside collar returns continuously to the old ground; inside
            # every band, all vertices stay at least 6 cm below its tread top.
            edge=collar.boundary.distance(point)
            distance=foot.distance(point)
            weight=1. if distance<1e-5 else edge/max(1e-9,edge+distance)
            weight=weight*weight*(3-2*weight)
            ceiling=min(h-.06+.5*poly.distance(point) for h,poly in bands)-.5*distance
            candidates.append([ceiling,weight])
        constraints.append(candidates)
    return lookup[key]
for cell in cells:
    if not domain.covers(cell.representative_point()):continue
    for tri in shapely.constrained_delaunay_triangles(cell).geoms:
        if tri.area<1e-12:continue
        ids=[index(p) for p in list(tri.exterior.coords)[:-1]]
        assert len(ids)==3 and len(set(ids))==3
        triangles.append(ids);areas.append(tri.area)
counts={}
for tri in triangles:
    for a,b in zip(tri,tri[1:]+tri[:1]):
        e=tuple(sorted((a,b)));counts[e]=counts.get(e,0)+1
assert all(c<=2 for c in counts.values()),'Nonmanifold planar subdivision'
border=[e for e,c in counts.items() if c==1]
for a,b in border:
    assert domain.boundary.distance(LineString([vertices[a],vertices[b]]).interpolate(.5,normalized=True))<.0001,'Interior crack in noded subdivision'
report={'origin':origin,'vertices_xz_local':vertices,'triangles':triangles,'border_edges':border,'grading_constraints':constraints,'source_headland_glb_sha256':paving['headland_glb_sha256'],'paving_design_sha256':hashlib.sha256((root/'captures/village_paving_design_24m/paving.json').read_bytes()).hexdigest(),'minimum_triangle_area_m2':min(areas),'earth_fill_enabled':True,'earth_fill_outer_width_m':4.,'paving_candidate':'24m','prior_graded_headland':'24l','scope':'Conforming original-edge and actual street-band subdivision for cut-and-fill earthworks around reviewed24m paving. Original house foundations excluded; old shore/bottom/side mesh retained in Blender. Four metre outer blending is an art proposal, not yet visually accepted.'}
(out/'grading.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('Grading subdivision',len(vertices),'vertices',len(triangles),'triangles; border',len(border),flush=True)

