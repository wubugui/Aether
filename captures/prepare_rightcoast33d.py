from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import Polygon,Point,box,shape,mapping
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=R/'captures/rightcoast_study_33b/mainland_headland.blend';native=read(R/'reviews/round-33b-reopened-source.json');assert sha(src)==native['source_sha256']
name='Mainland headland continuous bedrock and grass terraces';obj=native['objects'][name];vs=np.array(obj['vertices']);polys=obj['polygons'];occupied=shape(read(R/'reviews/round-33-occupied-regions.json')['hard_occupied_house_and_paving_union']);protected=occupied.buffer(1.2)
selected=[];shapes=[];all_top=set();incident={}
for i,ids in enumerate(polys):
 xyz=vs[ids]
 for j in ids:incident.setdefault(j,[]).append(i)
 if np.min(xyz[:,2])<=0:continue
 normal=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);poly=Polygon(xyz[:,:2])
 if normal[2]<=1e-7 or poly.area<1e-8:continue
 all_top.add(i)
 c=poly.centroid
 if -43<c.x<55 and -43<c.y<30 and not poly.intersects(protected):selected.append(i);shapes.append(poly)
patch=unary_union(shapes);assert patch.is_valid
components=list(patch.geoms) if patch.geom_type=='MultiPolygon' else [patch]
# Retain only the single coherent bay patch, not isolated triangles beyond protected lanes.
patch=max(components,key=lambda p:p.area);selected=[i for i in selected if patch.covers(Polygon(vs[polys[i],:2]).representative_point())]
edges={}
for i in selected:
 ids=polys[i]
 for a,b in zip(ids,ids[1:]+ids[:1]):edges[tuple(sorted((a,b)))]=edges.get(tuple(sorted((a,b))),0)+1
border=[e for e,c in edges.items() if c==1];boundary=sorted({i for e in border for i in e});lookup={vi:i for i,vi in enumerate(boundary)};selected_set=set(selected)
floor=box(-28,-7,-14,10);floor_inset=floor.intersection(patch.buffer(-.35));assert not floor_inset.is_empty
coords=[vs[i,:2].tolist() for i in boundary];constraints=[]
for i in boundary:
 adjacent=incident[i];fixed=any(j in all_top and j not in selected_set for j in adjacent)
 coast=any(np.min(vs[polys[j],2])<0 for j in adjacent)
 z=float(vs[i,2]);at=Point(*vs[i,:2])
 if coast and not fixed:
  d=floor.distance(at);t=max(0,min(1,d/24));w=1-t*t*(3-2*t);z=z+w*(min(z,1.6)-z)
 constraints.append(dict(point=lookup[i],height=z,source_vertex=i,coast=coast,fixed_to_outside_top=fixed))
newedges=[(lookup[a],lookup[b]) for a,b in border]
for region in (list(floor_inset.geoms) if floor_inset.geom_type=='MultiPolygon' else [floor_inset]):
 loop=list(region.exterior.coords)[:-1];start=len(coords);coords.extend([list(p) for p in loop]);newedges.extend((start+i,start+(i+1)%len(loop)) for i in range(len(loop)))
for x in np.arange(-43,55,6):
 for y in np.arange(-43,30,6):
  p=Point(float(x+.7),float(y+.4))
  if patch.contains(p) and patch.boundary.distance(p)>.8 and floor_inset.boundary.distance(p)>.6:coords.append([p.x,p.y])
plan=dict(label='33d',source=str(src.relative_to(R)),source_sha256=sha(src),source_reopen='reviews/round-33b-reopened-source.json',source_reopen_sha256=sha(R/'reviews/round-33b-reopened-source.json'),object=name,selected_polygons=selected,patch=mapping(patch),patch_area_m2=patch.area,actual_occupied_distance_m=patch.distance(occupied),points=coords,edges=newedges,boundary_constraints=constraints,floor=mapping(floor),floor_inset=mapping(floor_inset),floor_height_m=1.6,scope='Replace only coherent bay upper-surface patch with constrained native triangulation and broadly interpolated slope. Keep whole surrounding source, nine actual house and922paving domains; original underwater shell retained. Height solving uses explicit low shore and exact outside boundary, not a short vertical dip. Native, actual support, GPU and art review still required.')
p=R/'captures/rightcoast33d-design-plan.json';assert not p.exists();p.write_text(json.dumps(plan,indent=2),encoding='utf-8')
print(json.dumps(dict(selected_polygons=len(selected),patch_area=patch.area,points=len(coords),boundary_vertices=len(boundary),distance_actual_occupied=patch.distance(occupied),floor_area=floor_inset.area),indent=2))
