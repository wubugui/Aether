from pathlib import Path
import json,math,hashlib,numpy as np
from shapely.geometry import Polygon,shape
R=Path(__file__).resolve().parents[1];old=json.loads((R/'captures/foreground_island_study_32b/design-plan.json').read_text(encoding='utf-8'));actual=json.loads((R/'reviews/round-32b-foreground-independent-geometry.json').read_text(encoding='utf-8'))
boundary=[[-48,-12,24],[-35,-9,26.7],[-25,-5,28],[-6,-2,29.6],[5,2,29.1],[9,17,25.8],[17,30,21.5],[20,36,18.5],[12,43,15.5],[2,41,17],[-12,39,20.5],[-25,34,23],[-43,30,24.5],[-52,20,25.5],[-56,6,25],[-53,-4,24.5]]
poly=Polygon([p[:2] for p in boundary]);assert poly.is_valid and poly.exterior.is_ccw
pads=old['pads'];pads[-1]['half']=[5.1,5.1]
padchecks=[]
for pad,a in zip(pads,actual['sites']):
 c,s=math.cos(pad['yaw']),math.sin(pad['yaw']);hx,hy=pad['half'];x,y=pad['xy'];p=Polygon([(x+c*u-s*v,y+s*u+c*v) for u,v in [(-hx,-hy),(hx,-hy),(hx,hy),(-hx,hy)]]);foot=shape(a['actual_asset_bottom_footprint_geojson']);assert poly.covers(p) and poly.covers(foot),pad['id'];padchecks.append(dict(id=pad['id'],design_pad_min_boundary_distance_m=p.distance(poly.boundary),actual_footprint_min_boundary_distance_m=foot.distance(poly.boundary)))
routes=[dict(xyh=[[-23,-3.1,28],[-20,-3.5,28],[-16,-2.8,28.3],[-13,0,28.8],[-11,5,29.1],[-10,10,29.7],[-7,12,29.9],[-3,12,30.0621],[1,9,30.0621]],width=1.35),dict(xyh=[[-8.8,13.75,28.5],[-10.4,13,28.7],[-10,10,29.7]],width=1.35),dict(xyh=[[-23,-3.1,28],[-30,-3.5,27.7],[-35,-5,27],[-43,-6,25.8],[-48,-7,24.9]],width=1.35)]
trees=[[-42,-1,1.1],[-35,0,1.6],[-45,10,.85],[-36,12,1.05],[-49,-4,.65],[4,22,.65],[10,29,.45],[14,36,.35]]
for x,y,sc in trees:assert poly.contains(Polygon([(x+math.cos(i*math.pi/4),y+math.sin(i*math.pi/4)) for i in range(8)]))
# Authored staggered cross sections. Offsets are in metres, with unequal levels.
offsets=[[4,6,3,5,4,3,6,4,3,5,4,3,5,4,3,5],[10,12,9,11,10,9,12,10,9,11,10,9,11,10,9,11],[13,15,12,14,13,12,15,13,12,14,13,12,14,13,12,14]]
heights=[[16,15,21,20,17,18,13,12,10,12,15,16,15,18,17,15],[7,5,8,6,9,6,7,4,5,6,8,7,6,8,5,7],[.8,.4,1.1,.6,.9,.5,.8,.4,.7,.5,.9,.4,.7,.5,.9,.6]]
normals=[]
for i,p in enumerate(boundary):
 a=np.array(p[:2],dtype=float)-np.array(boundary[i-1][:2]);b=np.array(boundary[(i+1)%len(boundary)][:2],dtype=float)-np.array(p[:2]);a/=np.linalg.norm(a);b/=np.linalg.norm(b);n=np.array([a[1]+b[1],-a[0]-b[0]]);n/=np.linalg.norm(n);normals.append(n)
rings=[];last=poly;ringchecks=[]
for off,hs in zip(offsets,heights):
 ring=[[p[0]+n[0]*d,p[1]+n[1]*d,h] for p,n,d,h in zip(boundary,normals,off,hs)];p=Polygon([v[:2] for v in ring]);assert p.is_valid and p.covers(last),(p.is_valid,p.difference(last).area,last.difference(p).area);ringchecks.append(dict(area_m2=p.area,contains_previous=True));last=p;rings.append(ring)
out=dict(scope='32c local A terrain reconstruction with compact authored grass crest, joined inhabited upland, staggered outward rock sections and broad low rock shoulders. Fixed32b house/tower sites and same-world camera retained. All geometry is designed, not known original reference geography. No full world regeneration or visual acceptance.',source='captures/foreground_island_study_32b/island_a.blend',source_sha256=hashlib.sha256((R/'captures/foreground_island_study_32b/island_a.blend').read_bytes()).hexdigest(),boundary_xyh=boundary,rock_section_rings_xyh=rings,pads=pads,routes=routes,trees_blender_xy_scale=trees,cap_thickness_m=.18,tree_pad_radius_m=1.,preflight=dict(pads=padchecks,rock_contours=ringchecks),reference='ref/1342.png')
p=R/'captures/foreground32c-design-plan.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out['preflight'],indent=2))
