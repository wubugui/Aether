"""Author an irregular 3D control cage; no renderer or Blender invocation."""
from pathlib import Path
import json,numpy as np
from scipy.spatial import Delaunay
P=Path(__file__).resolve().parent
rim=[(-350,-130,85),(-325,-230,65),(-235,-270,60),(-120,-260,52),(15,-245,45),(125,-245,35),(235,-220,25),(325,-125,35),(350,-30,40),(300,70,60),(235,170,65),(140,250,70),(15,250,55),(-100,220,85),(-260,150,125),(-335,40,110)]
regions={
 'main_wide_asymmetric_crown':[(-280,-100,235),(-240,-190,205),(-130,-205,225),(-65,-165,225),(-215,-80,300),(-145,-130,315),(-65,-65,305),(-100,35,330),(-210,40,310),(-265,100,220),(-130,135,230),(-30,105,205)],
 'medium_oblique_shoulder':[(95,155,185),(145,110,215),(200,65,195),(200,155,180),(90,55,180),(265,55,115)],
 'low_small_folded_shoulder':[(135,-150,110),(220,-145,140),(245,-75,105),(130,-55,95)],
 'open_saddle_line':[(15,-145,78),(35,-35,115),(30,55,145),(0,135,125)],
}
verts=list(rim);groups={}
for name,points in regions.items():
 groups[name]=list(range(len(verts),len(verts)+len(points)));verts+=points
v=np.array(verts,float);faces=[]
for face in Delaunay(v[:,:2]).simplices:
 a,b,c=v[face];cross=np.cross(b-a,c-a)
 faces.append(face.tolist() if cross[2]>0 else face[::-1].tolist())
# Lower shell contracts inward, with non-coplanar broad belly controls.
n=len(rim);lower_start=len(verts)
for i,(x,y,z) in enumerate(rim):verts.append((x*.80+8,y*.78-4,-5+9*np.sin(i*1.37)))
bottom=[(-170,-20,-30),(-15,-90,-36),(110,75,-25),(190,-85,-24),(-70,130,-26)]
verts+=bottom;low=np.array(verts[lower_start:])
for face in Delaunay(low[:,:2]).simplices:
 a,b,c=low[face];face=face if np.cross(b-a,c-a)[2]<0 else face[::-1];faces.append((face+lower_start).tolist())
for i in range(n):j=(i+1)%n;faces.append([i,lower_start+i,lower_start+j,j])
# Boundary contour is convex: every named rim edge must exist in the roof.
edges={tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in faces if all(k<lower_start for k in f) for i in range(len(f))}
assert all(tuple(sorted((i,(i+1)%n))) in edges for i in range(n))
layout={'vertices':verts,'faces':faces,'groups':groups,'rim_count':n,'lower_start':lower_start,
 'placement_center_xy':[-350,-360],'construction':'One closed irregular multi-face cage with unequal 3D shoulder directions; no ellipse primitives, cutter booleans, repeated axial cross-sections, or noise field',
 'open_saddle_route':'(15,-245,45) -> (15,-145,78) -> (35,-35,115) -> (30,55,145) -> (0,135,125) -> (15,250,55)',
 'design_visible_volume_ratio':[1,.40,.12],'visual_acceptance':False}
(P/'layout52h.json').write_text(json.dumps(layout,indent=2)+'\n')
print(len(verts),'control vertices',len(faces),'control faces')
