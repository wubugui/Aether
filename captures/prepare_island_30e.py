from pathlib import Path
import json,math
import numpy as np
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];P=R/'captures/lantern_island_study_30d'
e=json.loads((P/'geometry-evidence.json').read_text());tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths'
def upper(o):
    v=np.array(o['vertices']);return [v[f] for f in o['polygons'] if len(f)==3 and np.cross(v[f[1]]-v[f[0]],v[f[2]]-v[f[0]])[2]>1e-10]
road=unary_union([Polygon(t[:,:2]) for t in upper(e['new'][pn])]);pads=unary_union([Polygon(s['polygon']) for s in e['sites']])
axes=json.loads((R/'reviews/round-30d-visible-slope-independent.json').read_text())['actual_C_D_tree_local_axes']
trees=unary_union([Point(p).buffer(2) for p in axes]);protected=unary_union([road,pads,trees]);mask=protected.buffer(.4).simplify(.005,preserve_topology=True)
surface=upper(e['new'][tn]);lines=[];seen=set()
for t in surface:
    for a,b in zip(t,np.roll(t,-1,axis=0)):
        key=tuple(sorted((tuple(np.round(a[:2],8)),tuple(np.round(b[:2],8)))))
        if key not in seen:seen.add(key);lines.append(LineString([a[:2],b[:2]]))
specs=[
 dict(name='Southern broken lip',polygon=[[-12,-29],[-1,-28],[3,-22],[1,-17],[-2,-15],[-6,-16],[-10,-21]],floor_plane=[.10,.13,4.8],anchors=[[-7,-24],[-5,-21],[-2,-19],[0,-22]],blend_width=1.8),
 dict(name='Southeast staggered recess',polygon=[[0,-24],[12,-23],[18,-17],[14,-10],[10,-8],[7,-9],[5,-12],[1,-15]],floor_plane=[.06,.10,4.12],anchors=[[4,-18],[7,-15],[11,-14],[13,-17],[8,-20]],blend_width=2.1),
 dict(name='Eastern split shoulder',polygon=[[11,-10],[25,-12],[29,-4],[24,3],[18,4],[13,1],[10,-3]],floor_plane=[.08,-.02,1.4],anchors=[[17,-8],[20,-5],[23,-3],[20,1],[16,1]],blend_width=1.6)]
components=[]
def each_line(g):
    if g.is_empty:return
    if g.geom_type in ['LineString','LinearRing']:yield g
    elif hasattr(g,'geoms'):
        for a in g.geoms:yield from each_line(a)
for spec in specs:
    region=Polygon(spec['polygon']).difference(mask)
    assert region.is_valid
    parts=[region] if region.geom_type=='Polygon' else list(region.geoms)
    for part_index,part in enumerate(parts):
        if part.area<.1:continue
        assert part.intersection(protected).area<1e-8
        pts=[];lookup={};edges=set()
        def point(p):
            key=tuple(round(float(x),8) for x in p)
            if key not in lookup:lookup[key]=len(pts);pts.append(list(key))
            return lookup[key]
        rings=[]
        for ring in [part.exterior,*part.interiors]:
            ids=[point(p) for p in list(ring.coords)[:-1]];rings.append(ids)
            for a,b in zip(ids,ids[1:]+ids[:1]):
                if a!=b:edges.add(tuple(sorted((a,b))))
        for line in lines:
            for segment in each_line(line.intersection(part)):
                coords=list(segment.coords)
                for a,b in zip(coords,coords[1:]):
                    ia,ib=point(a),point(b)
                    if ia!=ib:edges.add(tuple(sorted((ia,ib))))
        for p in spec['anchors']:
            if part.contains(Point(p)):point(p)
        components.append(dict(name=spec['name']+' '+str(part_index),polygon=[pts[i] for i in rings[0]],holes=[[pts[i] for i in ring] for ring in rings[1:]],cdt_points=pts,cdt_edges=[list(x) for x in sorted(edges)],cdt_outline=rings[0],floor_plane=spec['floor_plane'],blend_width=spec['blend_width'],area_m2=part.area,minimum_protected_distance_m=part.distance(protected)))
out=dict(scope='30e southern/eastern directly localized slope; three authored recessed facets with original-ground transition rims, protected polygons removed before native bottom-mesh construction.',source='captures/lantern_island_study_30d/island_c.blend',terrain_up_triangles=[t.tolist() for t in surface],components=components,nominal_protection_margin_m=.4,mask_simplification_m=.005,original_specs=specs)
p=R/'captures/island-30e-faceted-cut-plan.json';assert not p.exists();p.write_text(json.dumps(out,indent=2));print([(s['name'],len(s['cdt_points']),round(s['area_m2'],3),round(s['minimum_protected_distance_m'],4)) for s in components])
