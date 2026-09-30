from pathlib import Path
import json,numpy as np
from shapely.geometry import shape,Point,Polygon
R=Path(__file__).resolve().parents[1];read=lambda p:json.loads(p.read_text(encoding='utf-8'))
n=read(R/'captures/rightcoast33-native-intake.json');b=read(R/'captures/rightcoast33b-design-plan.json');occ=shape(read(R/'reviews/round-33-occupied-regions.json')['hard_occupied_house_and_paving_union'])
name='Mainland headland continuous bedrock and grass terraces';v=np.array(b['objects'][name]['vertices'],dtype=np.float32).astype(float);ts=np.array(n['objects'][name]['triangles']);tri=v[ts];normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);rows=[]
for x,y in [(-25,-5),(-20,0),(-17,7),(-22,-12),(-12,-5),(-7,7),(-30,8),(-33,13)]:
 p=Point(x,y);hits=[]
 for i,t in enumerate(tri):
  if normals[i,2]<=1e-7:continue
  poly=Polygon(t[:,:2])
  if not poly.covers(p):continue
  co=np.linalg.solve(np.column_stack((t[1,:2]-t[0,:2],t[2,:2]-t[0,:2])),np.array([x,y])-t[0,:2]);z=t[0,2]+co[0]*(t[1,2]-t[0,2])+co[1]*(t[2,2]-t[0,2]);hits.append(dict(triangle=i,z=float(z),xyz=t.tolist(),projected_area=poly.area,actual_occupied_intersection=poly.intersection(occ).area))
 hits.sort(key=lambda h:h['z'],reverse=True);rows.append(dict(x=x,y=y,distance_to_actual_occupied_m=occ.distance(p),highest=hits[0] if hits else None))
out=dict(scope='Read-only33b float32 planned main shell vertices and original source triangle indices: candidate low working shore localization. Not a saved-source verification, not whole-world visibility or proof that an entire face/neighborhood is editable.',rows=rows)
p=R/'captures/rightcoast33-low-cove-localization.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(rows,indent=2))
