from pathlib import Path
import json, math
from shapely.geometry import Polygon, Point
R=Path(__file__).resolve().parents[1]
p=json.loads((R/'captures/island-30g-faceted-cut-plan.json').read_text())
p['scope']='30h authored cutter tessellation independent of source triangle edges; same protected cut domains; rim sampling and inset transition vertices.'
for c, spec in zip(p['components'],p['original_specs']):
    pts=[];edges=[];outline=[];region=Polygon(c['polygon'],c['holes'])
    for ri,ring in enumerate([c['polygon'],*c['holes']]):
        ids=[]
        for a,b in zip(ring,ring[1:]+ring[:1]):
            count=max(1,math.ceil(math.dist(a,b)/1.7))
            for k in range(count):
                ids.append(len(pts));pts.append([a[j]+(b[j]-a[j])*k/count for j in range(2)])
        edges.extend([[a,b] for a,b in zip(ids,ids[1:]+ids[:1])])
        if ri==0:outline=ids
    inner=region.buffer(-c['blend_width'],join_style=2)
    parts=[inner] if inner.geom_type=='Polygon' else list(inner.geoms)
    for part in parts:
        if part.is_empty:continue
        for ring in [part.exterior,*part.interiors]:
            pts.extend([list(v) for v in list(ring.coords)[:-1]])
    pts.extend([a for a in spec['anchors'] if region.contains(Point(a))])
    c.update(cdt_points=pts,cdt_edges=edges,cdt_outline=outline)
dst=R/'captures/island-30h-faceted-cut-plan.json';assert not dst.exists();dst.write_text(json.dumps(p,indent=2))
s=(R/'blender/model_lantern_island_30f.py').read_text().replace('30f','30h')
s=s.replace("scope='30h southern/eastern", "scope='30h independently tessellated southern/eastern")
dst=R/'blender/model_lantern_island_30h.py';assert not dst.exists();dst.write_text(s)
for a,b in [('captures/check_island_30f.py','captures/check_island_30h.py'),('tools/render_lantern_island_30f.py','tools/render_lantern_island_30h.py')]:
    dst=R/b;assert not dst.exists();dst.write_text((R/a).read_text().replace('30f','30h'))
print([(c['name'],len(c['cdt_points'])) for c in p['components']])
