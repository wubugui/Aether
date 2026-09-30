from pathlib import Path
import json,math,hashlib,numpy as np
R=Path(__file__).resolve().parents[1];src=R/'reviews/round-32b-reopened-source.json';native=json.loads(src.read_text(encoding='utf-8'))
run=R/'captures/validation_runs/foreground-island-32b-20260908T221322Z-f2197374e6824751bce30284dabdfb95';scene=json.loads((run/'images/day-reference.png.json').read_text(encoding='utf-8'));cam=scene['camera'];pitch,yaw,roll=cam['rotation'];assert abs(roll)<1e-7
cy,sy=math.cos(yaw),math.sin(yaw);cx,sx=math.cos(pitch),math.sin(pitch);B=np.array([[cy,sy*sx,sy*cx],[0,cx,-sx],[-sy,cy*sx,cy*cx]])
camera=np.array([cam['position'][0]+2350,-cam['position'][2]-1650,cam['position'][1]]);f=941/(2*math.tan(math.radians(cam['fov']/2)))
meshes={name:np.array(o['vertices'])[np.array(o['triangles'])] for name,o in native['objects'].items()}
results=[]
for pixel in [(100,905),(260,901),(375,875),(490,904),(580,841),(660,833),(742,833)]:
 px,py=pixel;g=B@np.array([(px-836)/f,-(py-470.5)/f,-1]);direction=np.array([g[0],-g[2],g[1]]);direction/=np.linalg.norm(direction);hits=[]
 for name,ts in meshes.items():
  e1=ts[:,1]-ts[:,0];e2=ts[:,2]-ts[:,0];p=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,p);inv=np.divide(1.,det,out=np.zeros_like(det),where=np.abs(det)>1e-10);t=camera-ts[:,0];u=np.einsum('ij,ij->i',t,p)*inv;q=np.cross(t,e1);v=q@direction*inv;dist=np.einsum('ij,ij->i',e2,q)*inv
  ids=np.where((abs(det)>1e-10)&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(dist>0))[0]
  if not len(ids):continue
  i=int(ids[np.argmin(dist[ids])]);normal=np.cross(e1[i],e2[i]);normal/=np.linalg.norm(normal)
  hits.append(dict(object=name,triangle=i,triangle_xyz=ts[i].tolist(),location=(camera+direction*dist[i]).tolist(),normal=normal.tolist(),distance_m=float(dist[i])))
 hits.sort(key=lambda p:p['distance_m']);results.append(dict(pixel=list(pixel),first_native_island_hit=hits[0] if hits else None))
trees=[]
for item in native['planned_trees_actual_rays']:
 x,y=item['xy'];h=item['highest']['z'];world=np.array([x,h,-y])+np.array([-2350,0,-1650]);q=B.T@(world-np.array(cam['position']));base=[836+f*q[0]/-q[2],470.5-f*q[1]/-q[2]]
 trees.append(dict(xy=[x,y],ground_height_m=h,scale=item['scale'],projected_base_px=base,normal_z=item['highest']['normal'][2]))
out=dict(scope='Exact current32b fixed camera rays to saved source island meshes only. Selected pixels were directly viewed on actual day-reference. No building/tree ray occluders included; selected exposed ground/rock pixels only. Guides next genuine front-cliff boundary reconstruction, not material recolor or known original geography.',source_sha256=native['source_sha256'],source_evidence_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),image_sha256=hashlib.sha256((run/'images/day-reference.png').read_bytes()).hexdigest(),camera=cam,hits=results,tree_ground_projections=trees)
p=R/'captures/foreground32b-visible-grass-localization.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(dict(hits=[{'pixel':a['pixel'],'hit':None if not a['first_native_island_hit'] else {k:a['first_native_island_hit'][k] for k in ['object','location','normal']}} for a in results],tree_ground_projections=trees),indent=2))
