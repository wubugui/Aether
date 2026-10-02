"""A few original-camera mesh samples; no renderer or visual-acceptance score."""
import os,sys
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np,json
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import geometry58l as g,native_support58l as s,prepare_form58l as prep

def top_at(c,xz):
 v=np.asarray(c['vertices_world']);tris=np.asarray(c['planar_triangles']);points=v[:c['planar_vertex_count']];q=points[tris][:,:,[0,2]];out=[]
 for i,t in enumerate(q):
  z=np.linalg.solve(np.column_stack((t[1]-t[0],t[2]-t[0])),np.asarray(xz)-t[0]);w=np.r_[1-z.sum(),z]
  if w.min()>=-1e-8:out.append((float(w@points[tris[i],1]),i))
 g.require(bool(out),'TARGET_OUTSIDE_TRUE_DOMAIN:'+str(xz));return np.array([xz[0],out[0][0],xz[1]]),out[0][1]
def project(c,b,point,view):
 cam=next(x for x in b['world_cameras'] if x['name']==view);M=np.asarray(s.camera_matrix(cam));P=np.asarray(s.projection(cam));local=g.local(point);q=np.linalg.inv(M)@np.r_[local,1.];ndc=P@q;ndc/=ndc[3];pixel=[float((ndc[0]+1)*1179/2),float((1-ndc[1])*664/2)]
 v=g.local(np.asarray(c['vertices_world']));tri=v[np.asarray(c['faces'])];e1=tri[:,1]-tri[:,0];e2=tri[:,2]-tri[:,0];origin=M[:3,3];direction=local-origin;distance=float(np.linalg.norm(direction));direction/=distance
 h=np.cross(direction,e2);det=(e1*h).sum(1);good=abs(det)>1e-9;inv=np.zeros(len(det));inv[good]=1/det[good];ss=origin-tri[:,0];u=inv*(ss*h).sum(1);cross=np.cross(ss,e1);w=inv*(cross@direction);t=inv*(e2*cross).sum(1);ids=np.flatnonzero(good&(u>=-1e-8)&(w>=-1e-8)&(u+w<=1+1e-8)&(t>0));nearest=float(t[ids].min()) if len(ids) else None
 return {'pixel_xy':pixel,'within_original_frame':bool(q[2]<0 and 0<=pixel[0]<1179 and 0<=pixel[1]<664),'target_depth_m':distance,'nearest_depth_m':nearest,'visible_at_sample':bool(nearest is not None and abs(nearest-distance)<1e-5),'occlusion_depth_m':None if nearest is None else distance-nearest}
def check():
 c=g.read(HERE/'candidate.json');old=g.read(HERE.parent/'form-v2/candidate.json');b=g.read(HERE/'bindings.json');rows=[]
 for view,lobes,extra in [('04-k-fixed-near',prep.NEAR,[('large_medium_saddle',3772,3955),('large_small_saddle',3880,3950)]),('03-k-fixed-side-back',prep.SIDE,[('near_middle_saddle',4335,3680),('middle_far_saddle',4020,3660)])]:
  for name,x,z,*_ in lobes+extra:
   p,ti=top_at(c,[x,z]);op,oi=top_at(old,[x,z]);rows.append({'view':view,'name':name,'world_xz':[x,z],'old_world_point':op.tolist(),'new_world_point':p.tolist(),'new_minus_old_y_m':float(p[1]-op[1]),'actual_top_triangle':ti,'old_projection':project(old,b,op,view),'new_projection':project(c,b,p,view)})
 return {'scope':'Finite actual mesh height/projection and nearest triangle samples at authored shoulders/saddles. Original camera matrices unchanged. Not a render, full-visibility proof, art score or visual acceptance. Some target samples can be hidden; report that unchanged.', 'source':g.sha(HERE/'candidate.json'),'samples':rows,'visual_acceptance':False,'native_executed':False}
if __name__=='__main__':r=check();g.write(HERE/'PROJECTION_SAMPLES.json',r);print(json.dumps(r,indent=2))
