from pathlib import Path
import json,numpy as np
from shapely.geometry import Polygon,mapping
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf-8'))
p=R/'reviews/round-33e-rightcoast-independent-geometry.json';d=read(str(p.relative_to(R)));old=read('reviews/round-33b-reopened-source.json');new=read('reviews/round-33e-reopened-source.json');rows=[]
def coords(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return list(g.exterior.coords)
 return [p for child in getattr(g,'geoms',[]) for p in coords(child)]
for neg in d['new_changed_nonupward_triangles']:
 name=neg['object'];a,b=old['objects'][name],new['objects'][name];ov,nv=np.array(a['vertices']),np.array(b['vertices']);i=neg['actual_triangle'];f=b['triangles'][i];t=nv[f];pol=Polygon(t[:,:2]);co=np.linalg.solve(np.column_stack([t[:,:2],np.ones(3)]),t[:,2]);neigh=[];quadpairs=[]
 for j,g in enumerate(b['triangles']):
  shared=set(f)&set(g)
  if j==i or len(shared)!=2:continue
  tt=nv[g];pp=Polygon(tt[:,:2]);cut=pol.intersection(pp);normal=np.cross(tt[1]-tt[0],tt[2]-tt[0]);cc=np.linalg.solve(np.column_stack([tt[:,:2],np.ones(3)]),tt[:,2]);diff=[float(np.dot(co-cc,[*xy,1])) for xy in coords(cut)];vset=set(f)|set(g);oldpair=[(ii,ff) for ii,ff in enumerate(a['triangles']) if set(ff).issubset(vset)]
  neigh.append(dict(actual_triangle=j,vertex_indices=g,shared_edge=sorted(shared),vertices=tt.tolist(),normal_z=float(normal[2]/np.linalg.norm(normal)),xy_overlap_area_m2=cut.area,xy_overlap=mapping(cut),negative_minus_neighbor_surface_height_min_max_m=[min(diff),max(diff)] if diff else None))
  if len(oldpair)==2 and set(oldpair[0][1])|set(oldpair[1][1])==vset:
   quadpairs.append(dict(four_vertices=sorted(vset),old_triangles=[dict(actual_triangle=ii,indices=ff,old_xyz=ov[ff].tolist(),old_signed_twice_xy_area=float(np.cross(ov[ff][1]-ov[ff][0],ov[ff][2]-ov[ff][0])[2])) for ii,ff in oldpair],old_diagonal=sorted(set(oldpair[0][1])&set(oldpair[1][1])),new_diagonal=sorted(shared),new_pair_actual_triangles=[i,j]))
 rows.append(dict(negative_actual_triangle=i,indices=f,new_xyz=t.tolist(),signed_twice_xy_area=float(np.cross(t[1]-t[0],t[2]-t[0])[2]),absolute_projected_area_m2=pol.area,minimum_projected_altitude_m=2*pol.area/max(np.linalg.norm(t[(k+1)%3,:2]-t[k,:2]) for k in range(3)),shared_edge_neighbors=neigh,recovered_old_new_quad_pairs=quadpairs))
d['local_new_xy_foldback_evidence']=rows;d['failure_classification']='New3Dbeautifydiagonal creates an actual negativeXYorientation triangle and localprojectedoverlap. Nohouse/pavingintrusion; this is a terrainprojectionfoldback, not a claim of positive-area3Dselfintersection.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows,indent=2))
