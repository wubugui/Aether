"""Root-side profile evidence from generated solid cap triangles; not native mesh acceptance."""
from pathlib import Path
import sys,json,hashlib
import shapely
from shapely.geometry import Polygon,Point,LineString
root=Path(__file__).resolve().parents[1];label=sys.argv[1]
path=root/'captures'/('village_paving_design_'+label)/'paving.json';data=json.loads(path.read_text())
rows=[];failures=[];counterexamples=[]
def geometries(g):
    if hasattr(g,'geoms'):
        for p in g.geoms:yield from geometries(p)
    else:yield g
for group in data['groups']:
    levels={}
    for solid in group['solids']:
        if solid['kind']!='foundation':continue
        level=round(solid['top_y']+.012,6)
        levels.setdefault(level,[]).extend(Polygon([solid['vertices_xz'][i] for i in tri]) for tri in solid['cap_triangles'])
    floors={h:shapely.union_all(polys) for h,polys in levels.items()}
    for p in ([(-2251.58,-1750.84)] if group['name']=='foreground' else [(-2247.4,-1870.672734)]):
        counterexamples.append({'group':group['name'],'point':p,'covered_heights':[h for h,poly in floors.items() if poly.covers(Point(p))]})
    for route_index,points in enumerate(group['routes']):
        line=LineString(points)
        for offset in [-.6,0.,.6]:
            shifted=line.offset_curve(offset) if offset else line
            for part in geometries(shifted):
                if part.geom_type!='LineString':continue
                breaks=[0.,part.length]
                for poly in floors.values():
                    for item in geometries(part.intersection(poly.boundary)):
                        if item.is_empty:continue
                        if item.geom_type=='Point':breaks.append(part.project(item))
                        elif item.geom_type=='LineString':breaks.extend(part.project(Point(p)) for p in item.coords)
                breaks=sorted(set(round(t,7) for t in breaks));runs=[]
                for a,b in zip(breaks,breaks[1:]):
                    if b-a<.0001:continue
                    point=part.interpolate((a+b)/2)
                    heights=[h for h,poly in floors.items() if poly.buffer(1e-7).covers(point)]
                    height=max(heights) if heights else None
                    if runs and runs[-1]['height']==height and abs(runs[-1]['end']-a)<.001:runs[-1]['end']=b
                    else:runs.append({'start':a,'end':b,'height':height,'midpoint':list(point.coords)[0]})
                issues=[]
                for i,run in enumerate(runs):
                    if run['height'] is None:continue
                    if i and runs[i-1]['height'] is not None:
                        rise=abs(run['height']-runs[i-1]['height'])
                        if rise>.181:issues.append({'kind':'large vertical step','rise':rise,'at':run['start']})
                    if 0<i<len(runs)-1 and runs[i-1]['height'] is not None and runs[i+1]['height'] is not None:
                        depth=min(runs[i-1]['height'],runs[i+1]['height'])-run['height']
                        if depth>.12 and run['end']-run['start']<.40:issues.append({'kind':'narrow deep groove','depth':depth,'length':run['end']-run['start'],'run':run})
                row={'group':group['name'],'route_index':route_index,'offset_m':offset,'runs':runs,'issues':issues};rows.append(row)
                if issues:failures.append(row)
report={'label':label,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'Root-only exact line/bedding-cap polygon profile intersections, center and +/-0.6m offsets. 12mm grout excluded from rise profile. No Blender, GPU, full-width feet or visual acceptance.','counterexamples':counterexamples,'profiles':rows,'failures':failures}
out=root/'reviews'/('round-'+label+'-root-paving-profiles.json');assert not out.exists();out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'counterexamples':counterexamples,'profiles':len(rows),'failed_profiles':len(failures),'issues':[{'group':r['group'],'route':r['route_index'],'offset':r['offset_m'],'issues':r['issues']} for r in failures]},indent=2),flush=True)
