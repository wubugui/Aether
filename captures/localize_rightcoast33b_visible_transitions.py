from pathlib import Path
import json,hashlib,math,numpy as np
R=Path(__file__).resolve().parents[1];read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=R/'reviews/round-33b-reopened-source.json';n=read(source);old=read(R/'captures/rightcoast33-native-intake.json');run=R/'captures/validation_runs/rightcoast-33b-20260908T230223Z-8cfad99a2e374240853a864447c92c75';rows=[]
assert n['source_sha256']==sha(R/'captures/rightcoast_study_33b/mainland_headland.blend')
for view,pixels in [('day-coast-front',[(843,528),(884,535),(890,378)]),('day-reference',[(1375,850),(1400,868)])]:
 scene=read(run/'images'/(view+'.png.json'));cam=scene['camera'];pitch,yaw,roll=cam['rotation'];assert abs(roll)<1e-6
 cy,sy,cx,sx=math.cos(yaw),math.sin(yaw),math.cos(pitch),math.sin(pitch);B=np.array([[cy,sy*sx,sy*cx],[0,cx,-sx],[-sy,cy*sx,cy*cx]]);wc=np.array(cam['position'])-np.array([-2180,0,-1830]);camera=wc[[0,2,1]]*[1,-1,1];f=941/(2*math.tan(math.radians(cam['fov']/2)))
 for px,py in pixels:
  g=B@np.array([(px-836)/f,-(py-470.5)/f,-1]);direction=g[[0,2,1]]*[1,-1,1];direction/=np.linalg.norm(direction);hits=[]
  for name,obj in n['objects'].items():
   vs=np.array(obj['vertices']);ids=np.array(obj['triangles']);ts=vs[ids];e1=ts[:,1]-ts[:,0];e2=ts[:,2]-ts[:,0];p=np.cross(direction,e2);det=np.einsum('ij,ij->i',e1,p);inv=np.divide(1.,det,out=np.zeros_like(det),where=abs(det)>1e-10);q0=camera-ts[:,0];u=np.einsum('ij,ij->i',q0,p)*inv;q=np.cross(q0,e1);v=q@direction*inv;d=np.einsum('ij,ij->i',e2,q)*inv;valid=np.where((abs(det)>1e-10)&(u>=0)&(v>=0)&(u+v<=1)&(d>0))[0]
   if not len(valid):continue
   i=int(valid[np.argmin(d[valid])]);tri=ts[i];oldtri=np.array(old['objects'][name]['vertices'])[ids[i]];normal=np.cross(e1[i],e2[i]);normal/=np.linalg.norm(normal)
   hits.append(dict(object=name,triangle=i,vertex_ids=ids[i].tolist(),xyz=tri.tolist(),old26b_xyz=oldtri.tolist(),vertex_displacements_m=np.linalg.norm(tri-oldtri,axis=1).tolist(),normal=normal.tolist(),slope_degrees=math.degrees(math.acos(min(1,max(-1,normal[2])))),distance_m=float(d[i]),location_blender=(camera+direction*d[i]).tolist()))
  hits.sort(key=lambda h:h['distance_m']);rows.append(dict(view=view,pixel=[px,py],nearest_source_hit=hits[0] if hits else None))
out=dict(scope='Five selected visible grey transition rays to actual independently reopened33b coast meshes. Buildings/paving/tree and originalWorld occluders excluded; no pixel attribution of covered objects. Source triangle old26b comparison identifies whether actual selected coast vertices changed; does not infer whole-zone cause.',source_sha256=n['source_sha256'],source_reopen_sha256=sha(source),rows=rows)
p=R/'captures/rightcoast33b-visible-transition-localization.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps([dict(view=r['view'],pixel=r['pixel'],hit=None if not r['nearest_source_hit'] else {k:r['nearest_source_hit'][k] for k in ['object','vertex_ids','vertex_displacements_m','location_blender','slope_degrees']}) for r in rows],indent=2))
