"""Repair only two confirmed pinched 24i contours; preserve the authored street grading."""
from pathlib import Path
import json,hashlib
from collections import Counter
import shapely
from shapely.geometry import Polygon,Point
root=Path(__file__).resolve().parents[1];source=root/'captures/village_paving_design_24i/paving.json'
out=root/'captures/village_paving_design_24j';assert not out.exists();out.mkdir()
data=json.loads(source.read_text());repairs=[]
def polygon(s):return shapely.union_all([Polygon([s['vertices_xz'][i] for i in t]) for t in s['cap_triangles']])
def encode(s,p):
    vertices=[];lookup={};edges=[];caps=[]
    def vertex(point):
        key=tuple(round(c,5) for c in point)
        if key not in lookup:lookup[key]=len(vertices);vertices.append(key)
        return lookup[key]
    for ring in [p.exterior]+list(p.interiors):
        ids=[vertex(v) for v in list(ring.coords)[:-1]]
        edges.extend((a,b) for a,b in zip(ids,ids[1:]+ids[:1]))
    for tri in shapely.constrained_delaunay_triangles(p).geoms:caps.append([vertex(v) for v in list(tri.exterior.coords)[:-1]])
    degrees=Counter(i for edge in edges for i in edge);assert all(n==2 for n in degrees.values()),'Pinch remains'
    s.update(vertices_xz=vertices,boundary_edges=edges,cap_triangles=caps,area_m2=p.area)
for group in data['groups']:
    for s in group['solids']:
        degrees=Counter(i for edge in s['boundary_edges'] for i in edge)
        bad=[i for i,n in degrees.items() if n!=2]
        if not bad:continue
        original=polygon(s)
        patches=[Point(s['vertices_xz'][i]).buffer(.004,quad_segs=1) for i in bad]
        corrected=shapely.set_precision(shapely.union_all([original]+patches),.001)
        assert corrected.is_valid and corrected.geom_type=='Polygon'
        assert corrected.difference(original).area<.0001 and original.difference(corrected).area<.0001
        repairs.append({'group':group['name'],'solid':s['name'],'contact_points':[s['vertices_xz'][i] for i in bad],'added_area_m2':corrected.difference(original).area,'removed_area_m2':original.difference(corrected).area})
        encode(s,corrected)
    # Grade against the actual cleaned bedding caps, including the millimetre
    # contact repair, instead of against a pre-cleanup contour approximation.
    levels={}
    for s in group['solids']:
        if s['kind']=='foundation':levels.setdefault(round(s['top_y']+.012,7),[]).append(polygon(s))
    group['grading_bands']=[{'height':h,'geojson':shapely.to_geojson(shapely.union_all(polys))} for h,polys in levels.items()]
assert len(repairs)==2,repairs
data.update(label='24j',source_24i_design_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),contour_contact_repairs=repairs)
(out/'paving.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(repairs,indent=2),flush=True)
