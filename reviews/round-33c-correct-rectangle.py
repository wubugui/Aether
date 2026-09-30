from pathlib import Path
import json,ast,math,numpy as np
from shapely.geometry import Polygon,box,mapping
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
plan=json.loads((R/'captures/rightcoast33c-design-plan.json').read_text(encoding='utf-8'));rect=box(*plan['working_shore']['bounds_blender_xy'])
assert rect.area==238
h=(R/'reviews/round-30d-cutback-intake.py').read_text(encoding='utf-8');exec(h[h.index('def plane'):h.index('road=unary_union')])
h=(R/'reviews/round-30j-plan-independent.py').read_text(encoding='utf-8');exec(h[h.index('def overlay'):h.index('rock_roofs=')])
s=(R/'reviews/round-33c-rightcoast-independent-geometry.py').read_text(encoding='utf-8')
# The prior function has an explicit XY bbox fastfilter as well as rectclip;
# remove that former fastfilter and let the correct rect perform clipping.
node=next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name=='shore')
fsource=ast.get_source_segment(s,node).replace("np.max(t[:,0])<-28 or np.min(t[:,0])>-7 or np.max(t[:,1])<-14 or np.min(t[:,1])>10 or ","")
exec(fsource)
results=[]
for label in ['33b','33c']:
 d=json.loads((R/f'reviews/round-{label}-reopened-source.json').read_text(encoding='utf-8'));ts=[]
 for name,o in d['objects'].items():
  vertices=np.array(o['vertices']);ts.extend((name,i,vertices[f]) for i,f in enumerate(o['triangles']))
 results.append(shore(ts))
p=R/'reviews/round-33c-rightcoast-independent-geometry.json';d=json.loads(p.read_text(encoding='utf-8'))
d['superseded_rectangle_measurement']={'reason':'Independent reviewer misread the4bounds as[xmin,xmax,ymin,ymax]. This was an error, not an intentionally expanded design region. It does not describe the actual working_shore rectangle.','incorrectly_used_bounds_xy':[-28,-14,-7,10],'incorrect_area_m2':504.,'before':d['low_shore_before'],'after':d['low_shore_after']}
d['scope']=d['scope'].replace('prescribed504m²','prescribed238m²');d['low_shore_rectangle_projection']=mapping(rect);d['working_shore_bounds_order']='xmin,ymin,xmax,ymax';d['low_shore_before'],d['low_shore_after']=results
d['visual_status_from_parent']='33c visually rejected;33b retained as basis. Structural low-surface metrics do not constitute an upgrade.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{k:v for k,v in r.items() if k!='highest_surface_cells'} for r in results],indent=2))
