"""Author broad connecting rock ribs and measure exact protected surface clearance."""
from pathlib import Path
import json,math
import numpy as np
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];e=json.loads((R/'captures/lantern_island_study_29b/geometry-evidence.json').read_text())
protection=unary_union([Polygon(p) for p in e['protection']['path_top_triangles']]+[Polygon(p) for p in e['protection']['pads']]+[Point(p).buffer(2) for p in e['protection']['trees']])
t=e['new']['island_c grass and exposed rock terrain'];tv=np.array(t['vertices']);n=len(tv)//2
support=[]
for face in t['polygons']:
 if max(face)>=n:continue
 q=tv[face];part=Polygon(q[:,:2]).intersection(protection)
 if part.area>1e-10:support.append((part,q))
def plane(q):return np.linalg.solve(np.column_stack([q[:,:2],np.ones(3)]),q[:,2])
def points(poly):
 if poly.is_empty:return []
 if poly.geom_type=='Polygon':return list(poly.exterior.coords)
 if hasattr(poly,'geoms'):return [p for g in poly.geoms for p in points(g)]
 return list(poly.coords)
design=[('Southwest summit buttress',(-7,-19.5),(-16,-36),(4.5,6.,8.),(16.35,12.,4.5),1.5),('Southeast diagonal buttress',(2,-15),(20,-28),(3.,7.5,9.),(16.9,12.4,3.3),-1.5),('East tower shoulder',(9,3),(33,12),(3.2,7.,8.),(17.2,12.,3.8),1.0),('North descending spine',(-3,10),(-6,37),(3.,5.,9.),(16.,10.,2.8),-1.)]
meshes=[]
for name,start,end,widths,heights,lean in design:
 start=np.array(start);end=np.array(end);axis=end-start;side=np.array([-axis[1],axis[0]])/np.linalg.norm(axis)
 verts=[]
 for row,f in enumerate([0.,.46,1.]):
  c=start+axis*f+side*(lean if row==1 else 0)
  for col,sign in enumerate([-1,0,1]):
   xy=c+side*widths[row]*sign
   z=heights[row]-(0 if col==1 else ([2.0,4.0,2.3][row] if col==0 else [1.3,3.0,1.6][row]))
   verts.append([*xy,z])
 faces=[]
 for row in range(2):
  for col in range(2):
   a=row*3+col;b=a+1;c=a+4;d=a+3
   faces.extend([[a,b,d],[b,c,d]] if (row+col)%2 else [[a,b,c],[a,c,d]])
 v=np.array(verts);delta=0.;checks=0
 for f in faces:
  q=v[f];p=Polygon(q[:,:2]);rp=plane(q)
  for area,original in support:
   overlap=p.intersection(area)
   if overlap.is_empty:continue
   sp=plane(original)
   for x,y in points(overlap):delta=max(delta,float(np.dot(rp-sp,[x,y,1]))+.12);checks+=1
 # Lower this whole authored roof only if the exact clipped plane comparison
 # requires it; all protected surfaces retain at least12cm vertical separation.
 v[:,2]-=delta
 bottom=v.copy();bottom[:,2]=-5.;verts=np.concatenate([v,bottom]).tolist();roof=list(faces)
 faces += [[i+9 for i in reversed(f)] for f in roof]
 boundary=[0,1,2,5,8,7,6,3]
 for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.extend([[a,b,b+9],[a,b+9,a+9]])
 meshes.append({'name':name,'vertices':verts,'faces':faces,'roof_faces':roof,'exact_protection_check_vertices':checks,'vertical_adjustment_m':delta,'minimum_protection_vertical_gap_m':.12 if checks else None})
out={'meshes':meshes,'scope':'Four editable closed diagonal bearing ribs. Protected region is actual road footprint, padded building footprints and conservative tree-axis2m disks; exact clipped triangle plane check, not horizontal exclusion.12cm vertical gap below existing support surfaces. No full walking or tree-branch claim.'}
(R/'captures/island-29c-shoulder-plan.json').write_text(json.dumps(out,indent=2));print([(m['name'],m['vertical_adjustment_m'],m['exact_protection_check_vertices']) for m in meshes])
