from pathlib import Path
import json,math
import shapely
from shapely.geometry import Point,Polygon
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'captures/village_grading_design_25c/grading.json').read_text());p=json.loads((R/'captures/village_paving_design_24m/paving.json').read_text());l=json.loads((R/'captures/headland_layout_23c/layout.json').read_text())
o=d['origin'];groups=[]
for g in p['groups']:
 f=shapely.transform(shapely.from_geojson(g['footprint_geojson']),lambda a:a-[o[0],o[2]])
 protected=[]
 for h in l['houses']:
  if not h['name'].startswith('fore_' if g['name']=='foreground' else 'bay_'):continue
  wx,wz=(3.9,5.4) if h['asset']=='keeper_house' else ((3.26,4.1) if h['asset']=='fisher_cottage' else (4.4,3.4));c,s=math.cos(h['yaw']),math.sin(h['yaw']);hx,_,hz=h['position']
  protected.append(Polygon([(hx-o[0]+c*u+s*v,hz-o[2]-s*u+c*v) for u,v in [(-wx,-wz),(wx,-wz),(wx,wz),(-wx,wz)]]).buffer(.025,join_style=2))
 groups.append((g['name'],f,shapely.union_all(protected)))
for x,z in [(-2256.,-1746.),(-2253.60102081,-1748.39897919),(-2253.21147919,-1748.80680847),(-2236.15621948,-1875.882061),(-2236.15621948,-1875.95417786)]:
 i=min(range(len(d['vertices_xz_local'])),key=lambda i:math.dist(d['vertices_xz_local'][i],[x-o[0],z-o[2]]));pt=Point(d['vertices_xz_local'][i]);name,foot,prot=min(groups,key=lambda g:g[1].distance(pt))
 print(json.dumps({'world_xz':[x,z],'plan_index':i,'plan_local':d['vertices_xz_local'][i],'constraints':d['grading_constraints'][i],'group':name,'foot_distance':foot.distance(pt),'protected_distance':prot.distance(pt),'protected_contains':prot.contains(pt),'protected_boundary_distance':prot.boundary.distance(pt)}))
