from pathlib import Path
import json,hashlib,math
import numpy as np
from shapely.geometry import Polygon,Point,LineString
R=Path(__file__).resolve().parents[1]
src=(R/'reviews/round-30e-plan-independent.py').read_text(encoding='utf-8').replace('island-30e-faceted-cut-plan.json','island-30h-faceted-cut-plan.json').replace('round-30e-plan-independent.json','round-30h-plan-independent.json').replace("'round':'30e_plan'","'round':'30h_plan'")
exec(compile(src,'30h_projection_protection','exec'))
original=json.loads((R/'captures/island-30e-faceted-cut-plan.json').read_text());checks=[]
for c,o in zip(plan['components'],original['components']):
 assert c['polygon']==o['polygon'] and c['holes']==o['holes'];poly=Polygon(c['polygon'],c['holes']);pts=np.array(c['cdt_points']);lengths=[];boundaryerrors=[]
 for a,b in c['cdt_edges']:
  lengths.append(float(np.linalg.norm(pts[a]-pts[b])));line=LineString([pts[a],pts[b]]);boundaryerrors.append(line.difference(poly.boundary.buffer(1e-7)).length)
 assert max(lengths)<=1.700001 and max(boundaryerrors)<1e-7
 outside=[i for i,p in enumerate(pts) if not poly.buffer(1e-7).covers(Point(p))];assert not outside
 checks.append({'component':c['name'],'polygon_holes_exactly_same_as_validated30e':True,'point_count':len(pts),'constraint_edge_count':len(c['cdt_edges']),'max_constraint_edge_length_m':max(lengths),'all_constraint_edges_on_cutter_boundary':True,'constraint_edge_length_outside_boundary_tolerance_m':max(boundaryerrors),'all_input_points_inside_or_on_domain':True,'interior_point_count':sum(poly.boundary.distance(Point(p))>1e-7 for p in pts),'original30e_constraint_edge_count':len(o['cdt_edges'])})
out=R/'reviews/round-30h-plan-independent.json';report=json.loads(out.read_text());report['input_tessellation_checks']=checks;report['tessellation_scope']='All constrained edges now lie on cutter domain boundary; original terrain interior triangle edges are absent as constraints. Additional inset/anchor points remain inside the protected domain. This does not itself prove final Boolean validity.';out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(checks,indent=2))
