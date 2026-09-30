"""Resize actual land geometry, restore full-size native building support and fitted paths."""
from pathlib import Path
import json,math
import numpy as np
from shapely.geometry import Polygon,Point
R=Path(__file__).resolve().parents[1];e=json.loads((R/'captures/lantern_island_study_29e/geometry-evidence.json').read_text())
scale=np.array([.72,.72,.65]);tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths';cn='island_c faulted bedrock'
t=e['new'][tn];original=np.array(t['vertices']);v=original*scale;n=len(v)//2;top=[(i,p) for i,p in enumerate(t['polygons']) if max(p)<n]
def rect(cx,cy,wx,wy,turn):
 co,si=math.cos(turn),math.sin(turn);return Polygon([(cx+co*x-si*y,cy+si*x+co*y) for x,y in [(-wx,-wy),(wx,-wy),(wx,wy),(-wx,wy)]])
def get_height(vertices,xy):
 ts=np.array([vertices[p] for _,p in top]);inv=np.array([np.linalg.inv(np.column_stack([q[:,:2],np.ones(3)])) for q in ts]);weights=np.einsum('i,nij->nj',np.r_[xy,1.],inv);ids=np.flatnonzero(np.min(weights,axis=1)>=-2e-5);assert len(ids),(xy,'no terrain')
 k=int(ids[0]);return float(weights[k]@ts[k,:,2])
sites=[{'name':'tower','center':[.72,.72],'half_width':4.3,'half_depth':4.3,'turn':.1},{'name':'keeper_house','center':[-8.64,-10.08],'half_width':3.05,'half_depth':4.1,'turn':-.15}]
forced={};pad_rows=[]
for site in sites:
 cx,cy=site['center'];poly=rect(cx,cy,site['half_width'],site['half_depth'],site['turn']);h=get_height(v,np.array([cx,cy]));faces=[i for i,p in top if Polygon(v[p,:2]).intersects(poly)];ids=sorted({j for i in faces for j in t['polygons'][i]})
 for j in ids:
  if j in forced:assert abs(forced[j]-h)<.001,(j,'overlapping pad triangulation')
  forced[j]=h
 site.update(height=h,polygon=list(poly.exterior.coords)[:-1],protected_faces=faces,protected_vertices=ids);pad_rows.append((poly,h))
new=v.copy()
for i,p in enumerate(v[:n]):
 if i in forced:new[i,2]=forced[i]
 else:
  weights=[]
  for poly,h in pad_rows:
   d=Point(p[:2]).distance(poly)
   if d<3.5:
    a=d/3.5;w=1-a*a*(3-2*a);weights.append((w,h))
  if weights:
   w,h=max(weights);new[i,2]=p[2]*(1-w)+h*w
 new[n+i,2]=new[i,2]-.65
path=np.array(e['new'][pn]['vertices'])*scale;half=len(path)//2
ts=np.array([new[p] for _,p in top]);inv=np.array([np.linalg.inv(np.column_stack([q[:,:2],np.ones(3)])) for q in ts])
for i,p in enumerate(path[:half]):
 weights=np.einsum('i,nij->nj',np.r_[p[:2],1.],inv);ids=np.flatnonzero(np.min(weights,axis=1)>=-2e-5);assert len(ids);k=int(ids[0]);path[i,2]=weights[k]@ts[k,:,2]+.045;path[i+half,2]=path[i,2]-.35
slopes=[]
for face in e['new'][pn]['polygons']:
 if max(face)>=half:continue
 q=path[face];norm=np.cross(q[1]-q[0],q[2]-q[0]);norm/=np.linalg.norm(norm);slopes.append(math.degrees(math.acos(np.clip(norm[2],-1,1))))
core=np.array(e['new'][cn]['vertices'])*scale;core[54:]=new[n:]
out={'land_scale_blender_xyz':scale.tolist(),'terrain_vertices':new.tolist(),'path_vertices':path.tolist(),'core_vertices':core.tolist(),'top_vertex_count':n,'sites':sites,'path_max_slope_degrees':max(slopes),'d_world_position':[-2372,0,-1812],'d_yaw':2.0,'native_building_scale_unchanged':True,'scope':'Authored proportion candidate, not recovered original geography or pixel-derived exact dimensions. Apply scale to editable land meshes in Blender; full-size tower/house pads rebuilt and all affected sites/path/collision re-evaluated. Native tower scale1 and keeper-house scale0.7 retained in scene.'}
(R/'captures/island-30a-proportion-plan.json').write_text(json.dumps(out,indent=2));print('30a pad faces',[len(s['protected_faces']) for s in sites],'path maximum slope',max(slopes))
