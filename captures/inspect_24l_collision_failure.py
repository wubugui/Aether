from pathlib import Path
import json,collections
import shapely
from shapely.geometry import Polygon,Point
root=Path(__file__).resolve().parents[1]
run=root/'captures/validation_runs/village-paving-24l-20260908T133935Z-a85da8d179904470851864e01545b1c3'
report=json.loads((run/'images/day-foreground.png.json').read_text())['village_paving_study']
rows=report['failures'];print('Failures',len(rows),'ground penetrations',sum(r.get('ground_clearance_m',1)<-.015 for r in rows),'top errors',collections.Counter(round(r.get('top_error_m',0),2) for r in rows))
print('Minimum ground clearance',min(r['ground_clearance_m'] for r in report['paver_collision_samples']))
design=json.loads((run/'study-inputs/village-paving/paving-design.json').read_text())
points=[(-2257.72192382813,-1750.06359863281),(-2257.98291015625,-1749.37438964844)]
for q in points:
    point=Point(q);hits=[]
    for group in design['groups']:
        for s in group['solids']:
            caps=[Polygon([s['vertices_xz'][i] for i in tri]) for tri in s['cap_triangles']]
            poly=shapely.union_all(caps)
            if poly.covers(point):hits.append({'name':s['name'],'kind':s['kind'],'top_y':s['top_y'],'boundary_distance':poly.boundary.distance(point)})
    print(json.dumps({'point':q,'design_hits':hits},indent=2))
