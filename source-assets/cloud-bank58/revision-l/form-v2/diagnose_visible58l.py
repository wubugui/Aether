"""Read-only ray/triangle lookup of manually identified pixels in old true PNGs.
Not an image render, visibility acceptance or new camera. No image is altered.
"""
import os,sys
os.environ['OPENBLAS_NUM_THREADS']='1';sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry58l as g,native_support58l as s
import numpy as np,json
HERE=Path(__file__).resolve().parent

def diagnose():
 old=g.read(HERE.parent/'source-v1/candidate.json');new=g.read(HERE/'candidate.json');b=g.read(HERE/'bindings.json');v=np.array(old['vertices_world']);f=np.array(old['faces']);local=g.local(v);tri=local[f];e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];n=old['planar_vertex_count'];r=old['rim_count'];xz=v[:n][:,[0,2]];dist=g.rim_distance(xz,np.array(old['external_rim_authority_float64_xz']));newv=np.array(new['vertices_world'])
 selections={'03-k-fixed-side-back':[(360,440),(550,390),(260,505),(410,310),(625,310)],'04-k-fixed-near':[(770,410),(720,335),(980,220)],'01-original61-front':[(795,425)]}
 rows=[]
 for name,pixels in selections.items():
  cam=next(x for x in b['world_cameras'] if x['name']==name);M=np.array(s.camera_matrix(cam));P=np.array(s.projection(cam));origin=M[:3,3]
  for x,y in pixels:
   direction=M[:3,:3]@np.array([(2*(x+.5)/1179-1)/P[0,0],(1-2*(y+.5)/664)/P[1,1],-1.]);direction/=np.linalg.norm(direction)
   h=np.cross(direction,e2);det=np.sum(e1*h,1);good=np.abs(det)>1e-9;inv=np.zeros(len(f));inv[good]=1/det[good];ss=origin-tri[:,0];u=inv*np.sum(ss*h,1);q=np.cross(ss,e1);w=inv*(q@direction);t=inv*np.sum(e2*q,1);hit=good&(u>=0)&(w>=0)&(u+w<=1)&(t>0);ids=np.flatnonzero(hit)
   if not len(ids):rows.append(dict(view=name,pixel_xy=[x,y],hit=False));continue
   i=int(ids[np.argmin(t[ids])]);worldhit=g.world(origin+direction*t[i]);planids=np.where(f[i]<n,f[i],f[i]-n+r);dd=dist[planids];delta=newv[f[i],1]-v[f[i],1]
   rows.append(dict(view=name,pixel_xy=[x,y],hit=True,old_face_index=i,old_face_vertex_ids=f[i].tolist(),sheet='top' if i<len(old['planar_triangles']) else 'belly',world_hit=worldhit.tolist(),true_rim_distance_hit_m=float(g.rim_distance(worldhit[[0,2]][None],np.array(old['external_rim_authority_float64_xz']))[0]),true_rim_distance_vertices_m=dd.tolist(),new_top_y_deltas_m=delta.tolist()))
 return dict(method=__doc__,scope='Manual pixels chosen after viewing actual old PNGs. Their nearest triangle is calculated using original camera bytes and original float32 mesh. No new visual pass implied.',samples=rows)
if __name__=='__main__':g.write(HERE/'VISIBLE_WALL_DIAGNOSIS.json',diagnose());print(json.dumps(diagnose(),indent=2))
