from pathlib import Path
import json,math
from shapely.geometry import Polygon,shape
from shapely.affinity import affine_transform
R=Path(__file__).resolve().parents[1];plan=json.loads((R/'captures/foreground32d-design-plan.json').read_text(encoding='utf-8'));actual=json.loads((R/'reviews/round-32b-foreground-independent-geometry.json').read_text(encoding='utf-8'));poly=Polygon([p[:2] for p in plan['boundary_xyh']])
plan['scope']=plan['scope'].replace('32d','32e')+'32e turns the left keeper house gable toward the unchanged camera and rebuilds its real pad/entrance routes, lowers the right house site1.5m, and reduces the tallest left pine. Tower pad extent is derived from the complete actual lowest asset triangle union after32d left a real small stair-footprint strip below the flat plateau.'
plan['pads'][0]['yaw']=math.pi/2;plan['pads'][1]['height']=27.
mask=shape(actual['building_assets']['tower']['actual_bottom_triangle_union_geojson']);bounds=mask.bounds
plan['pads'][2]['half']=[max(5.1,math.ceil((max(abs(bounds[i]),abs(bounds[i+2]))+.12)*20)/20) for i in [0,1]]
plan['trees_blender_xy_scale'][1][2]=1.2
plan['routes']=[dict(xyh=[[-16.9,3,28],[-15,3,28],[-15,5,28],[-11,5,29.1],[-10,10,29.7],[-7,12,29.9],[-3,12,30.0621],[1,9,30.0621]],width=1.35),dict(xyh=[[-8.8,13.75,27],[-12.5,12.5,27.2],[-15,9,27.6],[-15,5,28]],width=1.35),dict(xyh=[[-16.9,3,28],[-15,3,28],[-14.8,0,28],[-15,-2.6,28],[-24,-3.5,28],[-30,-3.5,27.7],[-35,-5,27],[-43,-6,25.8],[-48,-7,24.9]],width=1.35)]
checks=[]
for pad in plan['pads']:
 c,s=math.cos(pad['yaw']),math.sin(pad['yaw']);x,y=pad['xy'];hx,hy=pad['half'];p=Polygon([(x+c*u-s*v,y+s*u+c*v) for u,v in [(-hx,-hy),(hx,-hy),(hx,hy),(-hx,hy)]]);sc=pad['scale'];foot=shape(actual['building_assets']['tower' if pad['id']=='tower' else 'house']['actual_bottom_triangle_union_geojson']);foot=affine_transform(foot,[c*sc,-s*sc,s*sc,c*sc,x,y]);assert poly.covers(p) and poly.covers(foot) and p.covers(foot),pad['id'];checks.append(dict(id=pad['id'],half=pad['half'],actual_base_in_design_pad=True,actual_base_coast_margin_m=foot.distance(poly.boundary),pad_coast_margin_m=p.distance(poly.boundary)))
plan['preflight']['pads']=checks
p=R/'captures/foreground32e-design-plan.json';assert not p.exists();p.write_text(json.dumps(plan,indent=2),encoding='utf-8')
s=(R/'blender/model_foreground_island_32d.py').read_text(encoding='utf-8').replace('32d','32e');p=R/'blender/model_foreground_island_32e.py';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(R/'tools/render_foreground_island_32d.py').read_text(encoding='utf-8').replace('32d','32e');needle="s=s.replace('Vector3(-22,0,2)','Vector3(-23,0,-3)').replace('Vector3(19,0,6)','Vector3(-8,0,-19)')";assert needle in s;s=s.replace(needle,needle+"\n   s=s.replace('Vector3(-23,0,-3))','Vector3(-23,0,-3),PI/2)')")
p=R/'tools/render_foreground_island_32e.py';assert not p.exists();p.write_text(s,encoding='utf-8');print(json.dumps(checks,indent=2))
