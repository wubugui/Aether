"""Concrete 3D cage coordinates and engineering projections; no engine/render/world."""
from pathlib import Path
from collections import Counter
import json,os,numpy as np
os.environ.setdefault("MPLCONFIGDIR","/tmp/mpl-cloud52h")
os.environ.setdefault("XDG_CACHE_HOME","/tmp/cache-cloud52h")
from scipy.spatial import ConvexHull
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
P=Path(__file__).resolve().parent
regions={
'M_main':[
(-230,-110,160),(-215,-180,90),(-100,-210,145),(40,-175,125),(125,-80,175),(85,80,195),(-10,165,170),(-155,195,95),(-280,80,135),(-300,-15,55),
(-165,-70,290),(-60,-100,305),(10,-10,285),(-55,85,320),(-185,70,260),
(-170,-55,-65),(-65,-140,-20),(55,-55,-5),(25,90,-25),(-140,125,-40),(-245,25,-5)],
'S_medium_rear_oblique':[
(-80,65,65),(-20,0,85),(115,15,130),(205,30,105),(280,120,90),(235,205,65),(110,245,85),(-45,160,110),
(55,80,240),(195,105,215),(205,165,200),(105,185,210),(90,110,-15),(170,175,15),(210,90,20)],
'T_small_front_fold':[
(-30,-75,100),(5,-165,50),(165,-190,35),(210,-135,75),(180,-40,60),(50,10,90),
(65,-95,165),(150,-110,145),(155,-55,125),(45,-90,-20),(145,-105,-10),(135,-20,20)]}
transform={'scale_xyz':[1.2,1.12,1.0],'translate_xyz':[-350,-360,35]}
parts={};hulls={}
for name,raw in regions.items():
 points=np.array(raw)*transform['scale_xyz']+transform['translate_xyz'];h=ConvexHull(points);hulls[name]=h;faces=[]
 for simplex,eq in zip(h.simplices,h.equations):
  face=simplex.tolist();a,b,c=points[face]
  if np.dot(np.cross(b-a,c-a),eq[:3])<0:face.reverse()
  faces.append(face)
 edges=Counter(tuple(sorted((f[i],f[(i+1)%3]))) for f in faces for i in range(3));assert all(n==2 for n in edges.values())
 used=sorted(set(i for f in faces for i in f))
 parts[name]={'vertices_blender_m':points.tolist(),'oriented_triangles':faces,'used_hull_indices':used,'interior_reference_indices':sorted(set(range(len(points)))-set(used)),'closed_edge_incidence_two':True,'volume_m3':h.volume,'bounds':[points.min(axis=0).tolist(),points.max(axis=0).tolist()]}
# Estimate intersection of the planned convex control volumes, not a cloud coverage claim.
allp=np.concatenate([np.array(p['vertices_blender_m']) for p in parts.values()]);lo=allp.min(axis=0);hi=allp.max(axis=0)
xyz=np.stack(np.meshgrid(*[np.arange(a+5,b,10) for a,b in zip(lo,hi)],indexing='ij'),axis=-1).reshape(-1,3)
inside={name:np.all(xyz@h.equations[:,:3].T+h.equations[:,3]<=1e-8,axis=1) for name,h in hulls.items()}
pairs={f'{a} + {b}':int(np.count_nonzero(inside[a]&inside[b]))*1000 for i,a in enumerate(parts) for b in list(parts)[i+1:]}
assert pairs['M_main + S_medium_rear_oblique']>100000 and pairs['M_main + T_small_front_fold']>100000
union=np.logical_or.reduce(list(inside.values()))
plan={'status':'Control-cage design data only, not a modeled or visually accepted cloud','failed_source_review':'cloud-evidence/cloudsea52h-main-source-v0-20261001T090045Z-khsjhj60/images','source_reference':'ref/1216.png','reference_actually_viewed':True,'coordinate_system':'Blender x/y horizontal, z up; placement and scale already baked into listed points','authored_transform_from_design_points':transform,'parts':parts,'bounds':[lo.tolist(),hi.tolist()],'dimensions_m':(hi-lo).tolist(),'volume_ratios_unmerged':[h.volume/hulls['M_main'].volume for h in hulls.values()],'planned_positive_volume_overlap_sample_m3':pairs,'planned_union_volume_10m_sample_m3':int(union.sum())*1000,'assembly':'Positive volumes overlap broadly and will form one closed native volume after reviewed cage construction; no negative cutter, global base disk or through-going trench','visual_acceptance':False,'final_blend_built':False,'world_integration':False}
(P/'cage52h_b.json').write_text(json.dumps(plan,indent=2)+'\n')
fig,axes=plt.subplots(1,3,figsize=(17,5.6));colors=['#477cb2','#64a98b','#d49a49']
for ax,(dims,title) in zip(axes,[((0,2),'FRONT: x / z'),((1,2),'SIDE: y / z'),((0,1),'TOP: x / y')]):
 for (name,part),color in zip(parts.items(),colors):
  pts=np.array(part['vertices_blender_m'])[:,dims];h=ConvexHull(pts);poly=pts[h.vertices]
  ax.add_patch(Polygon(poly,closed=True,facecolor=color,edgecolor=color,alpha=.25,lw=2))
  ax.plot(*np.vstack([poly,poly[:1]]).T,color=color,lw=1.4)
  ax.scatter(*pts.T,s=10,c=color)
  for i,xy in enumerate(pts):ax.annotate(name[0]+str(i),xy,fontsize=6,xytext=(2,2),textcoords='offset points',color=color)
 ax.set_title(title);ax.set_aspect('equal');ax.autoscale_view();ax.grid(alpha=.2);ax.set_xlabel('meters');ax.set_ylabel('meters')
fig.suptitle('52h B CAGE PLAN: three unequal 3D positive volumes; no shared base / no cut trench\nEngineering projections only. Overlap is shown, not an evaluated cloud surface.',fontsize=13)
fig.tight_layout();fig.savefig(P/'cage52h_b_projections.svg');fig.savefig(P/'cage52h_b_projections.png',dpi=150);plt.close(fig)
print(json.dumps({k:plan[k] for k in ['dimensions_m','volume_ratios_unmerged','planned_positive_volume_overlap_sample_m3','planned_union_volume_10m_sample_m3']},indent=2))
